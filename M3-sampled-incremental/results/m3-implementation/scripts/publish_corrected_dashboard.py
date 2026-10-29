"""Export a completed corrected study and install its derived dashboard evidence.

This one-time handoff can wait for the active study. It never generates a paper.
The previous dashboard data is retained as a named backup inside the study folder.
"""

import argparse
import json
import shutil
import time
import zipfile
from pathlib import Path

from m3.provenance import sha256
from m3.store import atomic_json, utc_now

ROOT = Path(__file__).resolve().parents[1]
DISPLAY_FILES = ("run_summary.json", "predictions.csv", "resources.csv", "drift.csv")
DERIVED_FILES = (*DISPLAY_FILES, "features.jsonl", "sensitivity.json")


def canonicalize_results(directory):
    """Keep exported text hashes identical to Git's LF-normalized content."""
    for path in directory.iterdir():
        if path.is_file() and path.suffix in {".json", ".csv"}:
            raw = path.read_bytes()
            if b"\r\n" in raw:
                path.write_bytes(raw.replace(b"\r\n", b"\n"))


def replay_timing_audit(study, run_ids):
    rows = []
    for path in sorted((study / "matrix").glob("official_pilot_*/execution.json")):
        report = json.loads(path.read_text())
        if report.get("status") != "validated_realtime" or report.get("collector_run_id") not in run_ids:
            continue
        ratios = [(stage["actual_end_epoch"] - stage["actual_start_epoch"])
                  / (stage["packet_count"] / stage["pps"]) for stage in report["stages"]]
        rows.append({"run_id": report["collector_run_id"],
                     "scenario": report["research"]["scenario"],
                     "sampling_rate": report["sampling_rate"], "seed": report["research"]["seed"],
                     "execution_sha256": sha256(path),
                     "stage_duration_ratios": ratios, "max_stage_duration_ratio": max(ratios)})
    return {"trials": rows, "accepted_trials_audited": len(rows),
            "interpretation": "Stage wall duration divided by packet_count/requested_pps. "
            "Includes process overhead and scheduling delays; descriptive only, no post-hoc exclusions."}


def publish(study, dashboard, results=None):
    study, dashboard = Path(study).resolve(), Path(dashboard).resolve()
    output = (ROOT / "output").resolve()
    if not study.is_relative_to(output) or not dashboard.is_relative_to(output):
        raise ValueError("Study and dashboard must be inside the project output directory")
    status = json.loads((study / "study_status.json").read_text())
    readiness = json.loads((study / "analysis/research_readiness.json").read_text())
    if status.get("phase") != "complete" or not readiness.get("ready"):
        raise ValueError("A completed study with passing analysis gates is required")
    matrix = json.loads((study / "matrix/matrix.json").read_text())
    if matrix.get("protocol", {}).get("telemetry_clock") == "kernel_receive" and results is None:
        raise ValueError("Kernel-clock results require a separate explicit results directory")
    run_ids = {cell["run_id"] for cell in matrix["cells"] if cell["status"] == "completed"}
    if len(run_ids) != 54 or len(matrix["cells"]) != 54:
        raise ValueError("Dashboard handoff requires all 54 distinct primary runs")
    for name, checksum in json.loads((study / "paper_snapshot.json").read_text()).items():
        if sha256(ROOT / name) != checksum:
            raise ValueError(f"Protected document changed: {name}")
    publication = study / "publication_status.json"
    if publication.exists() and json.loads(publication.read_text()).get("phase") == "complete":
        actual = {p.parent.name for p in dashboard.glob("*/run_summary.json")}
        if actual == run_ids and all(
                sha256(dashboard / run / name) == sha256(study / "runs" / run / name)
                for run in run_ids for name in DISPLAY_FILES):
            return
        raise ValueError("Previously installed dashboard evidence has changed")

    stage, backup = study / "dashboard_stage", study / "previous_dashboard"
    for path in (stage, backup):
        if not path.resolve().is_relative_to(output) or path.is_symlink():
            raise ValueError("Unsafe dashboard staging or backup path")
    stage.mkdir(exist_ok=True)
    for run_id in sorted(run_ids):
        source = study / "runs" / run_id
        summary = json.loads((source / "run_summary.json").read_text())
        if (summary.get("run_id") != run_id or summary.get("status") != "completed"
                or summary.get("source") != "official_realtime_verified"
                or summary.get("config", {}).get("naive_bayes") != "log_space"
                or summary.get("validation", {}).get("accepted") is not True):
            raise ValueError(f"Invalid corrected primary evidence: {run_id}")
        destination = stage / run_id
        destination.mkdir(exist_ok=True)
        for name in DISPLAY_FILES:
            shutil.copyfile(source / name, destination / name)

    results = (Path(results).resolve() if results is not None
               else ROOT / "research/results/corrected_log_space_20261028")
    if not results.resolve().is_relative_to((ROOT / "research/results").resolve()):
        raise ValueError("Results must remain inside the project's research results directory")
    results.mkdir(exist_ok=True)
    audit = replay_timing_audit(study, run_ids)
    if audit["trials"]:
        atomic_json(study / "analysis/replay_timing_audit.json", audit)
    for source in sorted((study / "analysis").iterdir()):
        if source.is_file() and source.suffix in {".json", ".csv", ".png"}:
            shutil.copyfile(source, results / source.name)
    for name in ("trial_index.json", "source_sha256.json", "study_status.json"):
        shutil.copyfile(study / name, results / name)
    failures = study / "technical_failure_retries.json"
    if not failures.is_file():
        failures = study / "checkpoint_failure_retry.json"
    if failures.is_file():
        shutil.copyfile(failures, results / "failed_attempts.json")
    atomic_json(results / "protocol.json", matrix["protocol"])
    atomic_json(results / "matrix.json", matrix)
    archive = results / "derived_trial_evidence.zip"
    with zipfile.ZipFile(archive.with_suffix(".zip.tmp"), "w",
                         compression=zipfile.ZIP_DEFLATED) as bundle:
        for run_id in sorted(run_ids):
            names = DERIVED_FILES
            summary = json.loads((study / "runs" / run_id / "run_summary.json").read_text())
            if summary.get("config", {}).get("telemetry_clock") == "kernel_receive":
                names = (*names, "ingestion.jsonl")
            for name in names:
                source = study / "runs" / run_id / name
                if not source.is_file():
                    raise ValueError(f"Missing derived evidence: {source}")
                entry = zipfile.ZipInfo(f"{run_id}/{name}", date_time=(2026, 10, 28, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(entry, source.read_bytes())
    archive.with_suffix(".zip.tmp").replace(archive)
    canonicalize_results(results)
    manifest = {"study_id": status["study_id"], "source_revision": status["source_revision"],
                "accepted_trials": 54, "pilot_excluded": True,
                "naive_bayes": "log_space", "original_packet_payloads_included": False,
                "files": {p.name: sha256(p) for p in sorted(results.iterdir())
                          if p.is_file() and p.name != "artifact_manifest.json"}}
    atomic_json(results / "artifact_manifest.json", manifest)
    canonicalize_results(results)
    if dashboard.is_symlink():
        raise ValueError("Dashboard destination must be a regular output directory")
    if dashboard.exists():
        if backup.exists():
            raise ValueError("A previous dashboard backup already exists; inspect before replacing")
        dashboard.rename(backup)
    try:
        stage.rename(dashboard)
    except OSError:
        if backup.exists() and not dashboard.exists():
            backup.rename(dashboard)
        raise
    atomic_json(publication, {"phase": "complete", "updated_at": utc_now(),
                             "dashboard": str(dashboard), "accepted_trials": 54,
                             "results": str(results), "previous_dashboard": str(backup)})
    print(json.dumps({"phase": "complete", "dashboard_trials": 54,
                      "results": str(results)}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", default="output/research/log_space_20261028")
    parser.add_argument("--dashboard", default="output/published-study")
    parser.add_argument("--results", help="Separate research result directory for a new protocol")
    parser.add_argument("--wait", action="store_true",
                        help="Wait for this active study to finish before the one-time handoff")
    args = parser.parse_args()
    if args.wait:
        deadline = time.monotonic() + 6 * 3600
        while True:
            state_path = Path(args.study) / "study_status.json"
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            if state.get("phase") == "complete":
                break
            if state.get("phase") == "failed" or time.monotonic() >= deadline:
                raise RuntimeError(f"Study did not complete; dashboard handoff stopped: {state}")
            time.sleep(10)
    publish(args.study, args.dashboard, args.results)
