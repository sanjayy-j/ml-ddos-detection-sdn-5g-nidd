"""Run the corrected matrix and derived analysis after an accepted separate pilot.

Writes only the selected study directory. No manuscript or published results are edited.
Resume uses the matrix's recorded trial status and retained sensitivity artifacts.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdn"))

from analyse_research import analyse
from compute_sensitivity import compute
from run_research_matrix import execute

from m3.provenance import sha256
from m3.research_metrics import eligible
from m3.store import atomic_json, utc_now


def require_corrected_run(summary, *, pilot=False, telemetry_clock=None):
    if (summary.get("status") != "completed"
            or summary.get("source") != "official_realtime_verified"
            or summary.get("validation", {}).get("accepted") is not True
            or summary.get("config", {}).get("naive_bayes") != "log_space"):
        raise ValueError("An independently accepted corrected-model run is required")
    if telemetry_clock == "kernel_receive":
        required = ("telemetry_kernel_clock", "telemetry_ingestion_timing",
                    "telemetry_tail_complete", "independent_sflow_capture")
        if (summary.get("config", {}).get("telemetry_clock") != "kernel_receive"
                or any(summary.get("validation", {}).get(key) is not True for key in required)):
            raise ValueError("Kernel-clock study requires independently validated ingestion evidence")
    if pilot and (summary.get("sampling_rate") != 1
                  or summary.get("research", {}).get("study_role") != "validation_pilot"):
        raise ValueError("The pre-matrix pilot must be a separate N=1 validation pilot")
    if not pilot and not eligible(summary):
        raise ValueError("Primary matrix contains an ineligible run")


def paper_snapshot(study):
    path = study / "paper_snapshot.json"
    if path.exists():
        snapshot = json.loads(path.read_text())
    else:
        files = [p for p in (ROOT / "research").iterdir()
                 if p.is_file() and p.suffix.lower() in {".md", ".pdf", ".tex", ".docx"}]
        files.extend(p for p in (ROOT / "output/pdf").glob("*") if p.is_file())
        snapshot = {p.relative_to(ROOT).as_posix(): sha256(p) for p in files}
        atomic_json(path, snapshot)
    changed = [name for name, checksum in snapshot.items()
               if not (ROOT / name).is_file() or sha256(ROOT / name) != checksum]
    if changed:
        raise ValueError(f"Protected document changed: {changed}")
    return len(snapshot)


def finish(protocol, prepared, study):
    protocol, prepared, study = (Path(p).resolve() for p in (protocol, prepared, study))
    study.mkdir(parents=True, exist_ok=True)
    frozen = json.loads(protocol.read_text())
    if frozen.get("model", {}).get("naive_bayes") != "log_space":
        raise ValueError("Corrected study protocol must explicitly select log_space")
    protected_count = paper_snapshot(study)
    sources = sorted([*ROOT.glob("src/m3/*.py"), *ROOT.glob("sdn/*.py"),
                      ROOT / "scripts/analyse_research.py", ROOT / "scripts/compute_sensitivity.py"])
    fingerprint = {p.relative_to(ROOT).as_posix(): sha256(p) for p in sources}
    fingerprint[protocol.relative_to(ROOT).as_posix()] = sha256(protocol)
    fingerprint_path = study / "source_sha256.json"
    if fingerprint_path.exists() and json.loads(fingerprint_path.read_text()) != fingerprint:
        raise ValueError("Study code/protocol changed; inspect before resuming")
    atomic_json(fingerprint_path, fingerprint)
    status = {"study_id": frozen.get("study_id"), "updated_at": utc_now()}

    def phase(name, **details):
        status.update(phase=name, updated_at=utc_now(), **details)
        atomic_json(study / "study_status.json", status)
        print(json.dumps(status), flush=True)

    try:
        pilots = []
        for path in (study / "pilot/runs").glob("*/run_summary.json"):
            value = json.loads(path.read_text())
            if value.get("status") == "completed" and value.get("validation", {}).get("accepted"):
                require_corrected_run(value, pilot=True,
                                      telemetry_clock=frozen.get("telemetry_clock"))
                pilots.append(value)
        if len(pilots) != 1:
            raise ValueError("Exactly one accepted separate corrected N=1 pilot is required")
        phase("matrix", pilot_run_id=pilots[0]["run_id"],
              source_revision=subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                      cwd=ROOT, text=True).strip())
        execute(protocol, prepared, study / "matrix", runs_output=study / "runs")
        matrix = json.loads((study / "matrix/matrix.json").read_text())
        expected = {cell["run_id"] for cell in matrix["cells"] if cell["status"] == "completed"}
        paths = sorted((study / "runs").glob("*/run_summary.json"))
        if len(expected) != 54 or {p.parent.name for p in paths} != expected:
            raise ValueError("Corrected primary study must contain exactly 54 completed matrix runs")
        for path in paths:
            summary = json.loads(path.read_text())
            require_corrected_run(summary, telemetry_clock=frozen.get("telemetry_clock"))
            for name, checksum in summary["raw_hashes"].items():
                if sha256(summary["artifacts"][name]) != checksum:
                    raise ValueError(f"Raw evidence hash mismatch: {summary['run_id']}/{name}")
        phase("sensitivity", accepted_trials=len(paths))
        for index, path in enumerate(paths, 1):
            sensitivity = path.parent / "sensitivity.json"
            summary = json.loads(path.read_text())
            existing = json.loads(sensitivity.read_text()) if sensitivity.exists() else {}
            if not (existing.get("primary_run_id") == summary["run_id"]
                    and existing.get("raw_hashes") == summary["raw_hashes"]
                    and existing.get("window_seconds") == 1.0
                    and existing.get("models", {}).get("hat_adwin", {}).get("naive_bayes") == "log_space"):
                compute(path.parent)
            phase("sensitivity", sensitivity_completed=index)
        phase("analysis")
        readiness = analyse(study / "runs", study / "analysis")
        if not readiness["ready"]:
            raise ValueError(f"Corrected study evidence incomplete: {readiness}")
        if {p.relative_to(ROOT).as_posix(): sha256(p) for p in sources} != {
                key: value for key, value in fingerprint.items()
                if key != protocol.relative_to(ROOT).as_posix()}:
            raise ValueError("Study source changed during the experiment")
        paper_snapshot(study)
        index = [{"run_id": json.loads(p.read_text())["run_id"],
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                  "summary": p.relative_to(ROOT).as_posix()} for p in paths]
        atomic_json(study / "trial_index.json", index)
        phase("complete", ready=True, protected_documents_verified=protected_count,
              dashboard_runs=str(study / "runs"))
        return readiness
    except BaseException as error:
        phase("failed", error=str(error))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default="configs/research_protocol_log_space.json")
    parser.add_argument("--prepared", default="data/prepared/research_20261019_equalrate_v1")
    parser.add_argument("--output", default="output/research/log_space_20261028")
    args = parser.parse_args()
    finish(args.protocol, args.prepared, args.output)
