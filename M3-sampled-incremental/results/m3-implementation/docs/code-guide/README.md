# Understand your M3 project

This is a study guide to the actual code in this checkout, inspected on 15 October 2026. It includes the project structure, how data moves, each file's job, and source lines paired with explanations. Start here, then use the four source chapters in the order below. The browser edition has navigation and search.

The current implementation is **M3 only, using the official 5G-NIDD release**. The earlier conversation proposed a shared M1/M2/M3 interface, but the present app is an M3 results dashboard. The current code and its evidence boundaries take precedence over that older plan.

## Read in this order

1. Read this overview and the concrete observation example below.
2. In [backend.md](backend.md), begin with `config.py`, `data.py`, `model.py`, and `engine.py`. These explain what a model receives, learns, and predicts.
3. Read `metrics.py`, `store.py`, `provenance.py`, and `analysis.py` in the same chapter. These explain where numbers come from and how evidence is saved.
4. Read `packets.py`, `ground_truth.py`, `labels.py`, `sflow.py`, and `live.py`. These explain how real network packets become model observations.
5. Read [sdn-and-data-tools.md](sdn-and-data-tools.md) for the downloader, label preparation, controller, topology and diagnostics.
6. Read [frontend.md](frontend.md) for React, API requests, plots, filtering and frontend tests. Read backend `api.py` and `cli.py` alongside it.
7. Read [tests-and-configuration.md](tests-and-configuration.md) to understand exactly what the tests assert and what the two supplied configurations mean.
8. Use [reference-data.md](reference-data.md) for line explanations of the dataset manifest and generated npm dependency lock. These record data/dependency identity rather than model decisions.

Every table pairs a physical line number with its original source and explanation. A statement may span several lines: the opening line explains the operation; following lines explain arguments, values, conditions and delimiters. Comments and blank lines are identified too. A frozen dataclass is not recursively immutable, and type hints alone are not runtime validation.

## The structure you maintain

```text
Project/
  README.md                         Setup, scope, evidence rules and commands
  pyproject.toml                    Python packaging, dependencies, CLI and test/lint settings
  .gitignore                       Files excluded from new Git tracking
  .gitattributes                   Text line endings and binary file handling
  configs/
    official_csv_pilot.json        Small official CSV run settings
    live_telemetry_validation.json Live telemetry diagnostic settings
  src/m3/
    __init__.py                    Package identity/version
    cli.py                         m3 audit/run/live/sweep/analyse/serve dispatch
    config.py                      Immutable run settings and validation
    data.py                        CSV reader, target mapping, feature allowlist and audit
    model.py                       River HAT plus separate error ADWIN wrapper
    engine.py                      Shared evaluation and offline CSV/PCAP replay
    metrics.py                     Confusion counts, precision/recall/F1/AUC, latency
    packets.py                     Packet parsing and sampled window features
    ground_truth.py                Independent packet-to-official-flow label matching
    labels.py                      Verified-source timeline annotations
    sflow.py                       Bounds-checked binary sFlow v5 decoder
    live.py                        Live UDP collector and window evaluation
    resources.py                   Background process CPU/memory/resource monitor
    lab.py                         Independent OVS entries and OpenFlow traffic capture
    provenance.py                  Official manifest and SHA256 input validation
    store.py                       Raw CSV writers, atomic summary, run reader
    analysis.py                    Comparable trial aggregation and Pareto plots
  scripts/
    fetch_dataset.py               Official release download, verification and extraction
    setup_sdn.sh                   Linux/WSL dependencies and runtime setup
  sdn/
    README.md                      Lab setup, diagnostics and replay instructions
    controller.py                  OS-Ken learning-switch OpenFlow controller
    topology.py                    Isolated Mininet/OVS network and bounded optional replay
    preflight.py                   Linux/tooling readiness checks
    inspect_session_labels.py      Audit conflicts in official session labels/tuples
    prepare_flow_labels.py         Checked CSV-to-Argus Offset joins
    validate_sflow.py              Actual exporter diagnostics at N=1/N=10
    run_live_validation.py         Actual collector diagnostic using benign probe traffic
  tests/
    test_core.py                   Config/model/metrics/pipeline/provenance/API tests
    test_ground_truth.py           Flow matching and unsampled label/count tests
    test_lab.py                    Mocked OVS snapshot/argument handling tests
    test_live.py                   Short local UDP collector test
  frontend/
    README.md                      Frontend commands and scope
    package.json                   npm scripts and declared dependency ranges
    package-lock.json              Generated exact dependency resolution/integrity metadata
    index.html                     Browser HTML shell
    vite.config.ts                 React tooling, test environment, API proxy
    tsconfig.json                  TypeScript checking/compiler configuration
    .gitignore                     Frontend-local exclusions
    src/
      main.tsx                     Mount React into the HTML shell
      App.tsx                      M3 dashboard, polling, selections and SVG charts
      api.ts                       HTTP fetching and runtime response validation
      evidence.ts                  Metric labels, comparability and Pareto filtering
      types.ts                     TypeScript evidence/result shapes
      style.css                    Layout, colors, responsiveness and component styles
      test-setup.ts                Test cleanup and DOM assertion setup
      test-fixtures.ts             Clearly artificial reusable test evidence
      App.test.tsx                 Dashboard behavior tests
      api.test.ts                  API evidence-validation tests
      evidence.test.ts             Formatting/comparison/Pareto tests
      integration.test.tsx         Render checks against separately running actual API
  data/
    manifest.json                  Official file identities, hashes and transformations
    raw/                           Downloaded originals; large, ignored
    prepared/                      Derived label/trace artifacts; ignored
  docs/
    implementation.md             Current design and measurement contract
    data-source.md                Publisher/source/label rules
    verification-status.md        Dated checkpoint, including remaining work
    code-guide/                   This educational guide
  output/
    runs/<run-id>/                 Predictions/resources/drift CSVs and JSON summaries
    analysis/                      Generated aggregates, charts and Pareto fronts
    sdn/                           Raw lab diagnostic evidence
    pdf/                           Generated handoff PDFs
```

Local housekeeping directories also exist: `.venv` and `.venv-sdn` are installed Python environments; `.tools` holds local executables; `.pytest_cache`, `.ruff_cache` and `__pycache__` are caches; `tmp` is scratch space; `Partner Work` contains local partner material; `.git` stores version history. Those are not source modules to memorize. Generated `node_modules`/`dist`, downloaded datasets and raw captures can contain many files. Their schema and role are documented without attempting to explain installed third-party library internals or millions of dataset records.

`inventory.json` records the exact tracked-file snapshot, each file's role, SHA256 and coverage chapter. `coverage-report.json` verifies that every maintained executable/configuration line and the two reference JSON files have matching numbered explanations. New guide and graph files are documentation/tool outputs created by this task.

## Three workflows, with different evidence

```text
CSV replay:
CLI -> RunConfig -> provenance -> iter_csv -> allowed flow features
    -> seeded selection with probability 1/N -> Evaluation -> OnlineDetector

Offline packet replay:
CLI -> RunConfig -> provenance -> original PCAP packets
    -> ALL original packets -> FlowLabels/WindowTruth -> window answer
    -> SELECTED packets -> WindowAccumulator -> packet-window features
    -> Evaluation -> OnlineDetector

Live collection:
Mininet hosts -> OVS (sampling happens here) -> sFlow UDP exports
    -> run_live -> decode_datagram -> WindowAccumulator
    + independently supplied timeline labels -> Evaluation -> OnlineDetector

All three:
Evaluation -> raw predictions + quality + ADWIN event records
ResourceMonitor -> process metrics + optional LabMeasurements
RunWriter -> output/runs/<run-id>/ CSVs + run_summary.json

Display:
React App -> frontend/api.ts -> FastAPI -> RunRepository -> saved evidence

Analysis:
CLI analyse -> RunRepository -> compatible groups -> repeated-trial statistics
            -> quality/cost charts + measured-bandwidth Pareto front
```

The CLI, model experiment, SDN controller, telemetry collector and HTTP server are separate roles. Opening the dashboard does not start learning. The controller forwards network traffic; HAT predicts alarms; there is no automatic attack-blocking/mitigation in the M3 application.

## Follow one observation yourself

Consider a CSV record whose true family is UDPFlood. `iter_csv` keeps its allowed numeric features and Proto, and maps its target to 1. Labels, IP addresses, tools, Offset and Seq do not enter `features`. Suppose the seeded sampler selects it and it occurs after warm-up.

1. `Evaluation.observe` reads the true label as evaluation metadata and tracks the first attack, if needed.
2. `OnlineDetector.predict(features)` asks HAT for the attack probability. Suppose it returns 0.7. With threshold 0.5, `predicted` becomes 1. This example value illustrates the code; it is not an experimental result.
3. `RunWriter.append` writes the prediction, score, true label, latency and phase to predictions.csv.
4. `QualityMetrics.update` increments `(1, 1)`, a true positive, and stores score/latency.
5. `OnlineDetector.learn` gives the external ADWIN error 0 because the answer was correct. It then calls HAT's `learn_one(features, 1)`.
6. If external ADWIN signals a change, the evaluator appends a drift event. That signal does not itself reset HAT; HAT's internal adaptation is a separate mechanism.
7. Periodic summary saves and the resource thread produce readable evidence for the dashboard.

For warm-up, steps involving scored metrics and the external error monitor are skipped, but predictions are logged and HAT still learns. For an unknown label (`None`), the prediction is logged and neither quality scoring nor supervised learning occurs. For held-out SYNFlood during unseen-scenario warm-up, the record is excluded before prediction.

When running live, the model does not know whether traffic is malicious by magic. The code learns only when separate ground-truth annotations supply a label. Immediate labels after prediction are an experiment assumption. A real deployment needs a trustworthy label-feedback policy.

## Why each measurement exists

| Concept | What it answers | Code location |
|---|---|---|
| Precision | Of alarms raised, how many were correct? | metrics.py |
| Recall | Of actual attack observations, how many were caught? | metrics.py |
| F1 | How well are precision and recall balanced? | metrics.py |
| ROC-AUC | Do attack observations rank above benign ones by probability? | metrics.py |
| False-positive rate | How often does benign traffic trigger an alarm? | metrics.py |
| Inference latency | How long did the prediction call take? | model.py, metrics.py |
| Detection delay | Time from first known attack to first correct alarm window | engine.py |
| Packets-to-detect | Original packets from attack onset through alarm window, when counts known | engine.py, ground_truth.py |
| Detector CPU/RSS | Cost of the collector/detector process | resources.py |
| Controller CPU | Separate controller process cost, when a PID is available | resources.py |
| sFlow payload bandwidth | Export bytes received by the collector per second | live.py, resources.py |
| OpenFlow bandwidth | Independently captured controller-channel frame bytes per second | lab.py |
| Flow-table entries | Snapshot mean of actual OVS flow entries | lab.py |
| Post-drift recovery | Time to regain an agreed performance level after annotated shift | Currently unavailable in engine.py |

The same number has different meaning under different modes: CSV quality is conditional on selected flow rows; packet replay quality applies to fully labeled windows formed from unsampled original truth. An estimated offline payload proxy is not measured live network bandwidth. The software records that distinction explicitly.

## Python and frontend syntax you will meet

| Syntax | Meaning in this code |
|---|---|
| `class X:` | Defines a type that groups state and methods. A new instance is made by `X(...)`. |
| `self` | The current object instance, supplied by Python when you call its method. |
| `def` / `return` | Define a function / send its result back to the caller. Defining is not executing the body. |
| `@dataclass(frozen=True)` | Generates field initialization/helpers and prevents normal field reassignment. |
| `str \| None` | Type hint allowing a string or absence; it does not validate runtime input by itself. |
| `dict`, `list`, `tuple`, `set` | Named-key mapping, ordered mutable sequence, fixed sequence, unique-value collection. |
| `yield` / `yield from` | Produce items lazily; code runs as the caller iterates, rather than building all records at once. |
| `[x for x in values if condition]` | Build a collection by looping and filtering. |
| `**dictionary` | Expand named arguments or merge dictionary entries in the surrounding expression. |
| `with` | Enter a context that manages release/closing, including on errors. |
| `try` / `except` / `finally` | Attempt work, handle specified exceptions, always perform final cleanup. |
| `lambda` | Small unnamed function, commonly a sort key or safe division helper. |
| `Path(__file__)` | Filesystem path to this source module, unlike paths relative to the working directory. |
| `async` / `await` in frontend | Start an asynchronous operation and wait without blocking the browser's whole event loop. |
| TypeScript `interface` / `type` | Describe data shapes to the compiler; runtime API validation is still needed. |
| React `useState` | Store UI state whose updates schedule a render. |
| React `useEffect` | Run side effects such as fetching/polling, with cleanup. |
| React `useMemo` / `useCallback` | Reuse derived values/function identities while their dependencies are unchanged. |
| JSX `{expression}` | Insert a JavaScript expression into the rendered element tree. |
| `AbortController` | Cancel outstanding fetches when a selection changes or a component is cleaned up. |

## What is implemented and what still needs evidence

The code implements the pipeline, conservative label matching, provenance checks, raw persistence, resource collection, API, M3 frontend and analysis. That does not mean the complete scientific study has been performed. The dated `docs/verification-status.md` distinguishes earlier checks from pending official capture coverage, scored live attack replay, full rates/trials/scenarios, recovery analysis and final reporting. This guide did not rerun those experiments.

The optional static-build path in `api.py` uses `parents[2]`: for Project/src/m3/api.py, parents[0] is m3, parents[1] is src and parents[2] is Project. It correctly points to root `frontend/dist` and mounts only if that build exists. The overview API's maximum-F1 selection does not establish comparability across sources/scenarios; inspect the evidence grouping before making that claim. Application behavior was not changed by this documentation request.

## Learn by predicting behavior

Before executing a command, write what files it reads, what objects it creates and what files it writes. Then compare that prediction with its implementation.

- In `model.py`, explain why `predict` has no label parameter but `learn` does.
- In `data.py`, count the 29 features and identify which source columns are intentionally excluded.
- In `engine.py`, point to the exact line where scoring precedes learning. Explain how an unknown label changes the path.
- Explain why selecting scenario="drift" is insufficient to create a drift experiment.
- Draw the two parallel paths for original packet truth versus sampled packet features.
- In `store.py`, explain why readers see either the old or new JSON summary rather than a half-written file.
- In `analysis.py`, explain why an efficient Pareto point is not automatically the selected knee.
- In `App.tsx`, trace one selected run from state change to request, validation and rendered metric.
- Read a test assertion, intentionally predict its expected result on paper, then explain the implementation that makes it pass.

The goal is to be able to explain an input's path, defend the experiment assumptions, and identify what would change if you edited a line. You do not need to memorize library source or generated dependency hashes.
