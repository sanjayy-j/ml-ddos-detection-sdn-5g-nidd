"""Local-only commands. Production runs always enforce official data provenance."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

from m3.config import SAMPLING_RATES, RunConfig
from m3.store import atomic_json


def main():
    parser = argparse.ArgumentParser(
        description="M3 official-data evaluation and live sFlow collector"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Verify and inspect an official CSV")
    audit.add_argument("input")
    audit.add_argument("--manifest", default="data/manifest.json")
    audit.add_argument("--output", default="output/analysis/dataset_audit.json")
    for name in ("run", "live", "sweep"):
        command = sub.add_parser(name)
        command.add_argument("--config", required=True)
    analysis = sub.add_parser("analyse")
    analysis.add_argument("--runs", default="output/runs")
    analysis.add_argument("--output", default="output/analysis")
    serve = sub.add_parser("serve")
    serve.add_argument("--runs", default="output/runs")
    serve.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        if args.command == "audit":
            from m3.data import audit_csv
            from m3.provenance import verify_input

            value = {"provenance": verify_input(args.input, args.manifest), **audit_csv(args.input)}
            target = Path(args.output)
            target.parent.mkdir(parents=True, exist_ok=True)
            atomic_json(target, value)
            print(
                json.dumps(
                    {
                        "output": str(target),
                        "rows": value["rows"],
                        "attack_counts": value["attack_counts"],
                    },
                    indent=2,
                )
            )
        elif args.command in ("run", "live", "sweep"):
            from m3.engine import run_replay
            from m3.live import run_live

            config = RunConfig.load(args.config)
            if args.command == "live":
                result = run_live(config)
            elif args.command == "sweep":
                if config.mode == "live_sflow":
                    raise ValueError(
                        "Live sweeps require the SDN orchestrator to reconfigure the switch each time"
                    )
                result = []
                for rate in SAMPLING_RATES:
                    for trial in range(3):
                        run = run_replay(
                            replace(config, sampling_rate=rate, seed=config.seed + trial)
                        )
                        result.append({"run_id": run["run_id"], "N": rate, "seed": run["seed"]})
                        print(json.dumps(result[-1]), flush=True)
            else:
                result = run_replay(config)
            print(json.dumps(result, indent=2, allow_nan=False))
        elif args.command == "analyse":
            from m3.analysis import analyse

            print(json.dumps(analyse(args.runs, args.output), indent=2))
        else:
            import uvicorn

            from m3.api import create_app

            uvicorn.run(create_app(args.runs), host="127.0.0.1", port=args.port)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"M3: {exc}\n")


if __name__ == "__main__":
    main()
