# Backend: every source line explained

This chapter pairs every physical source line (including comments and blank lines) with its purpose or syntax. Source was read from the current working tree when this guide was generated. Line numbers refer to that snapshot; SHA256 values let you detect later changes. External package internals are outside this repository; their call boundaries are explained here.

Read each file summary and symbol notes first, then its line table. A definition does not run its body until called. Indentation controls blocks; brackets let one statement span several physical lines.

## src/m3/__init__.py

**Package identity.** Marks src/m3 as the Python package m3. It contains package documentation and the package version; importing m3 alone does not start a server or an experiment.

Snapshot: 3 lines; SHA256 `3c16faf3df0efd9e0210c1ae9cad4245f8824e294442fcec9f93902721a31afe`.

### Named operations


### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;M3 experiment pipeline. Ground truth is never a model feature.&quot;&quot;&quot;</code> | Documentation string: M3 experiment pipeline. Ground truth is never a model feature. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>__version__ = &quot;0.1.0&quot;</code> | Set __version__. Use the literal '0.1.0'. |

## src/m3/config.py

**Experiment configuration and validation.** RunConfig is an immutable description of one run. Defaults supply omitted JSON values. Construction validates values immediately, before collectors or replay readers start. A scenario name records intent; it does not construct a drift scenario or rearrange a trace.

Snapshot: 93 lines; SHA256 `330794a520a634829a4a0f1e9c19564f59c513e052324a59c6a974a1e1fa92dc`.

### Named operations

- `RunConfig` (L11): Frozen dataclass: fields are configuration values with defaults; type hints describe intended types, while __post_init__ performs the actual checks.
- `RunConfig.__post_init__` (L36): Runs automatically after dataclass initialization; invalid configuration raises ValueError before an experiment starts.
- `RunConfig.to_dict` (L84): Serializes the dataclass for saved configuration/provenance; this returns a dictionary, not a JSON string.
- `RunConfig.load` (L88): Reads UTF-8 JSON, rejects unknown keys, then constructs RunConfig and triggers all validation.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 2 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 3 | <code>import re</code> | Import re to validate bridge names and run IDs with regular expressions. |
| 4 | <code>from dataclasses import asdict, dataclass, fields</code> | Import asdict, dataclass, fields from dataclasses. This makes the named library helpers available without the module prefix. |
| 5 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <code>SAMPLING_RATES = (1, 2, 5, 10, 20, 50)</code> | Set SAMPLING_RATES. Bundle these values in a tuple: (1, 2, 5, 10, 20, 50). |
| 8 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 9 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 10 | <code>@dataclass(frozen=True)</code> | Apply the dataclass decorator: generate initialization and field helpers; frozen=True prevents normal field reassignment. |
| 11 | <code>class RunConfig:</code> | Define class RunConfig. Frozen dataclass: fields are configuration values with defaults; type hints describe intended types, while __post_init__ performs the actual checks. |
| 12 | <code>    mode: str = &quot;csv_replay&quot;</code> | Declare configuration field mode with the shown type/default. Selects csv_replay, pcap_replay, or live_sflow, which have different units, features and evidence strength. |
| 13 | <code>    input_path: str &#124; None = None</code> | Declare configuration field input_path with the shown type/default. CSV/PCAP input path for replay; in live mode optional input provenance alone does not send or replay traffic. |
| 14 | <code>    manifest_path: str = &quot;data/manifest.json&quot;</code> | Declare configuration field manifest_path with the shown type/default. JSON registry used to verify official dataset identity and SHA256 of selected inputs. |
| 15 | <code>    labels_path: str &#124; None = None</code> | Declare configuration field labels_path with the shown type/default. Optional independently documented full-window timeline annotations; absent annotations leave packet windows unknown. |
| 16 | <code>    flow_labels_path: str &#124; None = None</code> | Declare configuration field flow_labels_path with the shown type/default. Prepared official flow interval table used only for offline packet matching; mutually exclusive with timeline labels. |
| 17 | <code>    output_root: str = &quot;output/runs&quot;</code> | Declare configuration field output_root with the shown type/default. Parent directory for unique per-run raw evidence and summaries. |
| 18 | <code>    sampling_rate: int = 1</code> | Declare configuration field sampling_rate with the shown type/default. Inverse sampling probability N; allowed values are 1, 2, 5, 10, 20, 50. Offline uses Bernoulli draws with probability 1/N; it does not deterministically retain every Nth row. |
| 19 | <code>    seed: int = 42</code> | Declare configuration field seed with the shown type/default. Seed for reproducible offline random selection and HAT randomness; live OVS sampling is not made deterministic by this Python seed. |
| 20 | <code>    scenario: str = &quot;baseline&quot;</code> | Declare configuration field scenario with the shown type/default. Experiment category baseline/drift/unseen. Choosing drift alone does not change the data. unseen excludes SYNFlood warm-up observations. |
| 21 | <code>    threshold: float = 0.5</code> | Declare configuration field threshold with the shown type/default. Attack probability cutoff used to create y_pred; kept fixed for controlled comparisons. |
| 22 | <code>    warmup_records: int = 1000</code> | Declare configuration field warmup_records with the shown type/default. First eligible CSV records before evaluation; determined before sampling, so actual learned warm-up count decreases with N. |
| 23 | <code>    max_records: int &#124; None = None</code> | Declare configuration field max_records with the shown type/default. Optional upper bound on raw input records read, including records later excluded or not selected. |
| 24 | <code>    warmup_seconds: float = 20.0</code> | Declare configuration field warmup_seconds with the shown type/default. Packet-window relative start times before this boundary are warm-up and excluded from scoring. |
| 25 | <code>    window_seconds: float = 1.0</code> | Declare configuration field window_seconds with the shown type/default. Width of packet feature/label windows; CSV ignores packet windowing. |
| 26 | <code>    duration_seconds: float = 80.0</code> | Declare configuration field duration_seconds with the shown type/default. Configured live collection duration; it does not limit offline replay in this implementation. |
| 27 | <code>    bind: str = &quot;127.0.0.1&quot;</code> | Declare configuration field bind with the shown type/default. IPv4 local address of the UDP sFlow receiver; default loopback means same host/network namespace. |
| 28 | <code>    port: int = 6343</code> | Declare configuration field port with the shown type/default. UDP listening port for sFlow payloads; distinct from the API port and OpenFlow port. |
| 29 | <code>    start_epoch: float &#124; None = None</code> | Declare configuration field start_epoch with the shown type/default. Optional scheduled collector origin in Unix seconds; absent value uses current wall clock. |
| 30 | <code>    controller_pid: int &#124; None = None</code> | Declare configuration field controller_pid with the shown type/default. Optional separate OS-Ken controller process ID for CPU measurement, not the detector process ID. |
| 31 | <code>    ovs_bridge: str &#124; None = None</code> | Declare configuration field ovs_bridge with the shown type/default. Configured OVS bridge used only for read-only live flow-count snapshots. |
| 32 | <code>    openflow_port: int &#124; None = None</code> | Declare configuration field openflow_port with the shown type/default. OpenFlow TCP port captured independently on Linux loopback for controller-channel byte counts. |
| 33 | <code>    grace_period: int = 200</code> | Declare configuration field grace_period with the shown type/default. HAT split-evaluation interval in observations at a leaf; not a warm-up count or ADWIN window size. |
| 34 | <code>    drift_delta: float = 0.002</code> | Declare configuration field drift_delta with the shown type/default. ADWIN sensitivity parameter passed to HAT internal detectors and the external error monitor. |
| 35 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 36 | <code>    def __post_init__(self):</code> | Define function/method __post_init__. Runs automatically after dataclass initialization; invalid configuration raises ValueError before an experiment starts. |
| 37 | <code>        if self.mode not in {&quot;csv_replay&quot;, &quot;pcap_replay&quot;, &quot;live_sflow&quot;}:</code> | Branch only if self.mode not in {'csv_replay', 'pcap_replay', 'live_sflow'} is true; otherwise skip this indented block or take its following elif/else. |
| 38 | <code>            raise ValueError(&quot;Unknown input mode&quot;)</code> | Raise ValueError('Unknown input mode') and stop this operation; the caller can record/report this invalid condition. |
| 39 | <code>        if self.flow_labels_path and (self.mode != &quot;pcap_replay&quot; or self.labels_path):</code> | Branch only if self.flow_labels_path and (self.mode != 'pcap_replay' or self.labels_path) is true; otherwise skip this indented block or take its following elif/else. |
| 40 | <code>            raise ValueError(</code> | Raise ValueError('flow_labels_path is for offline packet replay only; use either flow labels or timeline labels') and stop this operation; the caller can record/report this invalid condition. |
| 41 | <code>                &quot;flow_labels_path is for offline packet replay only; use either flow labels or timeline labels&quot;</code> | Literal component of the surrounding statement: 'flow_labels_path is for offline packet replay only; use either flow labels or timeline labels'. Its role is determined by the field/call immediately above. |
| 42 | <code>            )</code> | Close the call to ValueError begun above; this is punctuation, not a separate operation. |
| 43 | <code>        if type(self.sampling_rate) is not int or self.sampling_rate not in SAMPLING_RATES:</code> | Branch only if type(self.sampling_rate) is not int or self.sampling_rate not in SAMPLING_RATES is true; otherwise skip this indented block or take its following elif/else. |
| 44 | <code>            raise ValueError(f&quot;sampling_rate must be one of {SAMPLING_RATES}&quot;)</code> | Raise ValueError(f'sampling_rate must be one of {SAMPLING_RATES}') and stop this operation; the caller can record/report this invalid condition. |
| 45 | <code>        if type(self.seed) is not int:</code> | Branch only if type(self.seed) is not int is true; otherwise skip this indented block or take its following elif/else. |
| 46 | <code>            raise ValueError(&quot;seed must be an integer&quot;)</code> | Raise ValueError('seed must be an integer') and stop this operation; the caller can record/report this invalid condition. |
| 47 | <code>        for name in (&quot;warmup_records&quot;, &quot;grace_period&quot;, &quot;port&quot;):</code> | Loop: assign each item from ('warmup_records', 'grace_period', 'port') into name, then execute the indented body. |
| 48 | <code>            if type(getattr(self, name)) is not int:</code> | Branch only if type(getattr(self, name)) is not int is true; otherwise skip this indented block or take its following elif/else. |
| 49 | <code>                raise ValueError(f&quot;{name} must be an integer&quot;)</code> | Raise ValueError(f'{name} must be an integer') and stop this operation; the caller can record/report this invalid condition. |
| 50 | <code>        if self.max_records is not None and type(self.max_records) is not int:</code> | Branch only if self.max_records is not None and type(self.max_records) is not int is true; otherwise skip this indented block or take its following elif/else. |
| 51 | <code>            raise ValueError(&quot;max_records must be an integer or null&quot;)</code> | Raise ValueError('max_records must be an integer or null') and stop this operation; the caller can record/report this invalid condition. |
| 52 | <code>        if self.scenario not in {&quot;baseline&quot;, &quot;drift&quot;, &quot;unseen&quot;}:</code> | Branch only if self.scenario not in {'baseline', 'drift', 'unseen'} is true; otherwise skip this indented block or take its following elif/else. |
| 53 | <code>            raise ValueError(&quot;scenario must be baseline, drift or unseen&quot;)</code> | Raise ValueError('scenario must be baseline, drift or unseen') and stop this operation; the caller can record/report this invalid condition. |
| 54 | <code>        if self.start_epoch is not None and not math.isfinite(self.start_epoch):</code> | Branch only if self.start_epoch is not None and (not math.isfinite(self.start_epoch)) is true; otherwise skip this indented block or take its following elif/else. |
| 55 | <code>            raise ValueError(&quot;start_epoch must be finite&quot;)</code> | Raise ValueError('start_epoch must be finite') and stop this operation; the caller can record/report this invalid condition. |
| 56 | <code>        if self.ovs_bridge is not None and not re.fullmatch(</code> | Branch only if self.ovs_bridge is not None and (not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,31}', self.ovs_bridge)) is true; otherwise skip this indented block or take its following elif/else. |
| 57 | <code>            r&quot;[A-Za-z0-9][A-Za-z0-9_.-]{0,31}&quot;, self.ovs_bridge</code> | Literal component of the surrounding statement: '[A-Za-z0-9][A-Za-z0-9_.-]{0,31}'. Its role is determined by the field/call immediately above. |
| 58 | <code>        ):</code> | Continue the surrounding RunConfig.__post_init__ statement: ):. The indentation and open brackets connect it to the operation above. |
| 59 | <code>            raise ValueError(&quot;Invalid OVS bridge name&quot;)</code> | Raise ValueError('Invalid OVS bridge name') and stop this operation; the caller can record/report this invalid condition. |
| 60 | <code>        if self.openflow_port is not None and (</code> | Branch only if self.openflow_port is not None and (type(self.openflow_port) is not int or not 1 <= self.openflow_port <= 65535) is true; otherwise skip this indented block or take its following elif/else. |
| 61 | <code>            type(self.openflow_port) is not int or not 1 &lt;= self.openflow_port &lt;= 65535</code> | Continuation of the statement above. Evaluate type(self.openflow_port) is not int or not 1 <= self.openflow_port <= 65535 left to right with short-circuit or. |
| 62 | <code>        ):</code> | Continue the surrounding RunConfig.__post_init__ statement: ):. The indentation and open brackets connect it to the operation above. |
| 63 | <code>            raise ValueError(&quot;Invalid OpenFlow port&quot;)</code> | Raise ValueError('Invalid OpenFlow port') and stop this operation; the caller can record/report this invalid condition. |
| 64 | <code>        if not math.isfinite(self.threshold) or not 0 &lt; self.threshold &lt; 1:</code> | Branch only if not math.isfinite(self.threshold) or not 0 < self.threshold < 1 is true; otherwise skip this indented block or take its following elif/else. |
| 65 | <code>            raise ValueError(&quot;threshold must be strictly between 0 and 1&quot;)</code> | Raise ValueError('threshold must be strictly between 0 and 1') and stop this operation; the caller can record/report this invalid condition. |
| 66 | <code>        if self.warmup_records &lt; 0 or (self.max_records is not None and self.max_records &lt; 1):</code> | Branch only if self.warmup_records < 0 or (self.max_records is not None and self.max_records < 1) is true; otherwise skip this indented block or take its following elif/else. |
| 67 | <code>            raise ValueError(&quot;Invalid record limit&quot;)</code> | Raise ValueError('Invalid record limit') and stop this operation; the caller can record/report this invalid condition. |
| 68 | <code>        for value in (self.window_seconds, self.duration_seconds):</code> | Loop: assign each item from (self.window_seconds, self.duration_seconds) into value, then execute the indented body. |
| 69 | <code>            if not math.isfinite(value) or value &lt;= 0:</code> | Branch only if not math.isfinite(value) or value <= 0 is true; otherwise skip this indented block or take its following elif/else. |
| 70 | <code>                raise ValueError(&quot;Window and duration must be positive and finite&quot;)</code> | Raise ValueError('Window and duration must be positive and finite') and stop this operation; the caller can record/report this invalid condition. |
| 71 | <code>        if not math.isfinite(self.warmup_seconds) or self.warmup_seconds &lt; 0:</code> | Branch only if not math.isfinite(self.warmup_seconds) or self.warmup_seconds < 0 is true; otherwise skip this indented block or take its following elif/else. |
| 72 | <code>            raise ValueError(&quot;Warm-up duration must be nonnegative&quot;)</code> | Raise ValueError('Warm-up duration must be nonnegative') and stop this operation; the caller can record/report this invalid condition. |
| 73 | <code>        if not 1 &lt;= self.port &lt;= 65535:</code> | Branch only if not 1 <= self.port <= 65535 is true; otherwise skip this indented block or take its following elif/else. |
| 74 | <code>            raise ValueError(&quot;Invalid UDP port&quot;)</code> | Raise ValueError('Invalid UDP port') and stop this operation; the caller can record/report this invalid condition. |
| 75 | <code>        if (</code> | Branch only if not math.isfinite(self.drift_delta) or not 0 < self.drift_delta < 1 or self.grace_period < 1 is true; otherwise skip this indented block or take its following elif/else. |
| 76 | <code>            not math.isfinite(self.drift_delta)</code> | Continuation of the statement above. Evaluate not math.isfinite(self.drift_delta) or not 0 < self.drift_delta < 1 or self.grace_period < 1 left to right with short-circuit or. |
| 77 | <code>            or not 0 &lt; self.drift_delta &lt; 1</code> | Continuation of the statement above. Read not 0 < self.drift_delta < 1 from the current function/object state. |
| 78 | <code>            or self.grace_period &lt; 1</code> | Continuation of the statement above. Evaluate the comparison self.grace_period < 1 to True/False; comparisons may short-circuit. |
| 79 | <code>        ):</code> | Continue the surrounding RunConfig.__post_init__ statement: ):. The indentation and open brackets connect it to the operation above. |
| 80 | <code>            raise ValueError(&quot;Invalid model configuration&quot;)</code> | Raise ValueError('Invalid model configuration') and stop this operation; the caller can record/report this invalid condition. |
| 81 | <code>        if self.mode != &quot;live_sflow&quot; and not self.input_path:</code> | Branch only if self.mode != 'live_sflow' and (not self.input_path) is true; otherwise skip this indented block or take its following elif/else. |
| 82 | <code>            raise ValueError(&quot;Replay modes require input_path&quot;)</code> | Raise ValueError('Replay modes require input_path') and stop this operation; the caller can record/report this invalid condition. |
| 83 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 84 | <code>    def to_dict(self):</code> | Define function/method to_dict. Serializes the dataclass for saved configuration/provenance; this returns a dictionary, not a JSON string. |
| 85 | <code>        return asdict(self)</code> | Return to the caller: Call asdict with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 86 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 87 | <code>    @classmethod</code> | Apply classmethod: Python supplies the class as cls, so RunConfig.load can construct an instance. |
| 88 | <code>    def load(cls, path: str &#124; Path):</code> | Define function/method load. Reads UTF-8 JSON, rejects unknown keys, then constructs RunConfig and triggers all validation. |
| 89 | <code>        data = json.loads(Path(path).read_text(encoding=&quot;utf-8&quot;))</code> | Set data. Call json.loads with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 90 | <code>        unknown = set(data) - {f.name for f in fields(cls)}</code> | Set unknown. Calculate set(data) - {f.name for f in fields(cls)} using subtract; / returns a floating-point ratio and // floors division where used. |
| 91 | <code>        if unknown:</code> | Branch only if unknown is true; otherwise skip this indented block or take its following elif/else. |
| 92 | <code>            raise ValueError(f&quot;Unknown configuration keys: {sorted(unknown)}&quot;)</code> | Raise ValueError(f'Unknown configuration keys: {sorted(unknown)}') and stop this operation; the caller can record/report this invalid condition. |
| 93 | <code>        return cls(**data)</code> | Return to the caller: Call cls with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |

## src/m3/data.py

**CSV records, feature extraction, and audit.** Converts official CSV rows into Record objects. The allowlist is the boundary between model features and evaluation-only labels. A CSV row index is stored as time for bookkeeping only; it does not establish physical time or natural chronology.

Snapshot: 119 lines; SHA256 `9e8ac45f7820a09082877768e7e0b85cbeaf13a1b7d8a5ff0c4d1a9421458e9f`.

### Named operations

- `Record` (L29): Immutable transport object shared by data readers, windowing, and Evaluation; label and family are metadata, not features.
- `binary_label` (L37): Returns 1 for the three in-scope floods, 0 for compatible benign labels, and None for excluded families; contradictions raise errors.
- `extract_flow_features` (L52): Uses only the feature allowlist; each numeric feature gets a missing-value flag, non-finite values become zero, and Proto becomes lowercase.
- `iter_csv` (L69): Lazily yields one Record at a time from a CSV; validates essential columns and malformed rows before handing records to the engine.
- `audit_csv` (L90): Counts rows, attack families, missing fields and exact duplicate row signatures without training. The duplicate-signature set grows with dataset size.

The 14 numeric CSV columns describe duration, packet/byte totals, direction-specific totals/means/TTL/rates. Their exact publisher semantics and units must be checked against the data dictionary. The extractor produces 14 values plus 14 missing flags and Proto: 29 features. Missing flags prevent a substituted zero from pretending the source really measured zero.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import csv</code> | Import csv to stream CSV records and write raw tabular evidence. |
| 2 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 3 | <code>from collections import Counter</code> | Import Counter from collections. This makes the named library helpers available without the module prefix. |
| 4 | <code>from dataclasses import dataclass</code> | Import dataclass from dataclasses. This makes the named library helpers available without the module prefix. |
| 5 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <code>POSITIVE_FAMILIES = {&quot;UDPFlood&quot;, &quot;SYNFlood&quot;, &quot;ICMPFlood&quot;}</code> | Set POSITIVE_FAMILIES. Read {'UDPFlood', 'SYNFlood', 'ICMPFlood'} from the current function/object state. |
| 8 | <code># Deliberate allowlist: labels, tools, addresses, row IDs, Seq and Offset never reach the model.</code> | Source comment: Deliberate allowlist: labels, tools, addresses, row IDs, Seq and Offset never reach the model. This documents intent and does not execute. |
| 9 | <code>NUMERIC_COLUMNS = (</code> | Set NUMERIC_COLUMNS. Bundle these values in a tuple: ('Dur', 'TotPkts', 'TotBytes', 'SrcBytes', 'DstBytes', 'sMeanPktSz', 'dMeanPktSz', 'sTtl', 'dTtl', 'SrcPkts', 'DstPkts', 'Rate', 'SrcRate', 'DstRate'). |
| 10 | <code>    &quot;Dur&quot;,</code> | Literal component of the surrounding statement: 'Dur'. Its role is determined by the field/call immediately above. |
| 11 | <code>    &quot;TotPkts&quot;,</code> | Literal component of the surrounding statement: 'TotPkts'. Its role is determined by the field/call immediately above. |
| 12 | <code>    &quot;TotBytes&quot;,</code> | Literal component of the surrounding statement: 'TotBytes'. Its role is determined by the field/call immediately above. |
| 13 | <code>    &quot;SrcBytes&quot;,</code> | Literal component of the surrounding statement: 'SrcBytes'. Its role is determined by the field/call immediately above. |
| 14 | <code>    &quot;DstBytes&quot;,</code> | Literal component of the surrounding statement: 'DstBytes'. Its role is determined by the field/call immediately above. |
| 15 | <code>    &quot;sMeanPktSz&quot;,</code> | Literal component of the surrounding statement: 'sMeanPktSz'. Its role is determined by the field/call immediately above. |
| 16 | <code>    &quot;dMeanPktSz&quot;,</code> | Literal component of the surrounding statement: 'dMeanPktSz'. Its role is determined by the field/call immediately above. |
| 17 | <code>    &quot;sTtl&quot;,</code> | Literal component of the surrounding statement: 'sTtl'. Its role is determined by the field/call immediately above. |
| 18 | <code>    &quot;dTtl&quot;,</code> | Literal component of the surrounding statement: 'dTtl'. Its role is determined by the field/call immediately above. |
| 19 | <code>    &quot;SrcPkts&quot;,</code> | Literal component of the surrounding statement: 'SrcPkts'. Its role is determined by the field/call immediately above. |
| 20 | <code>    &quot;DstPkts&quot;,</code> | Literal component of the surrounding statement: 'DstPkts'. Its role is determined by the field/call immediately above. |
| 21 | <code>    &quot;Rate&quot;,</code> | Literal component of the surrounding statement: 'Rate'. Its role is determined by the field/call immediately above. |
| 22 | <code>    &quot;SrcRate&quot;,</code> | Literal component of the surrounding statement: 'SrcRate'. Its role is determined by the field/call immediately above. |
| 23 | <code>    &quot;DstRate&quot;,</code> | Literal component of the surrounding statement: 'DstRate'. Its role is determined by the field/call immediately above. |
| 24 | <code>)</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 25 | <code>CATEGORICAL_COLUMNS = (&quot;Proto&quot;,)</code> | Set CATEGORICAL_COLUMNS. Bundle these values in a tuple: ('Proto',). |
| 26 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 27 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 28 | <code>@dataclass(frozen=True)</code> | Apply the dataclass decorator: generate initialization and field helpers; frozen=True prevents normal field reassignment. |
| 29 | <code>class Record:</code> | Define class Record. Immutable transport object shared by data readers, windowing, and Evaluation; label and family are metadata, not features. |
| 30 | <code>    index: int</code> | Set index. Type annotation only; no value is assigned on this line. |
| 31 | <code>    time: float</code> | Set time. Type annotation only; no value is assigned on this line. |
| 32 | <code>    features: dict[str, float &#124; str]</code> | Set features. Type annotation only; no value is assigned on this line. |
| 33 | <code>    label: int &#124; None</code> | Set label. Type annotation only; no value is assigned on this line. |
| 34 | <code>    attack_family: str</code> | Set attack_family. Type annotation only; no value is assigned on this line. |
| 35 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 36 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 37 | <code>def binary_label(family: str, label: str) -&gt; int &#124; None:</code> | Define function/method binary_label. Returns 1 for the three in-scope floods, 0 for compatible benign labels, and None for excluded families; contradictions raise errors. |
| 38 | <code>    family, label = family.strip(), label.strip()</code> | Set (family, label). Bundle these values in a tuple: (family.strip(), label.strip()). |
| 39 | <code>    if family.startswith(&quot;SYNTH_&quot;) or label.startswith(&quot;SYNTH_&quot;):</code> | Branch only if family.startswith('SYNTH_') or label.startswith('SYNTH_') is true; otherwise skip this indented block or take its following elif/else. |
| 40 | <code>        raise ValueError(&quot;Synthetic placeholder labels are not valid official experiment data&quot;)</code> | Raise ValueError('Synthetic placeholder labels are not valid official experiment data') and stop this operation; the caller can record/report this invalid condition. |
| 41 | <code>    if family in POSITIVE_FAMILIES:</code> | Branch only if family in POSITIVE_FAMILIES is true; otherwise skip this indented block or take its following elif/else. |
| 42 | <code>        if label.lower() not in {&quot;malicious&quot;, &quot;1&quot;, &quot;attack&quot;, family.lower()}:</code> | Branch only if label.lower() not in {'malicious', '1', 'attack', family.lower()} is true; otherwise skip this indented block or take its following elif/else. |
| 43 | <code>            raise ValueError(f&quot;Conflicting label for {family}: {label}&quot;)</code> | Raise ValueError(f'Conflicting label for {family}: {label}') and stop this operation; the caller can record/report this invalid condition. |
| 44 | <code>        return 1</code> | Return to the caller: Use the literal 1. |
| 45 | <code>    if family.lower() == &quot;benign&quot; and label.lower() in {&quot;benign&quot;, &quot;0&quot;, &quot;normal&quot;}:</code> | Branch only if family.lower() == 'benign' and label.lower() in {'benign', '0', 'normal'} is true; otherwise skip this indented block or take its following elif/else. |
| 46 | <code>        return 0</code> | Return to the caller: Use the literal 0. |
| 47 | <code>    if family.lower() == &quot;benign&quot;:</code> | Branch only if family.lower() == 'benign' is true; otherwise skip this indented block or take its following elif/else. |
| 48 | <code>        raise ValueError(f&quot;Conflicting benign label: {label}&quot;)</code> | Raise ValueError(f'Conflicting benign label: {label}') and stop this operation; the caller can record/report this invalid condition. |
| 49 | <code>    return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 50 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 51 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 52 | <code>def extract_flow_features(row: dict[str, str]) -&gt; dict[str, float &#124; str]:</code> | Define function/method extract_flow_features. Uses only the feature allowlist; each numeric feature gets a missing-value flag, non-finite values become zero, and Proto becomes lowercase. |
| 53 | <code>    features: dict[str, float &#124; str] = {}</code> | Set features. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 54 | <code>    for name in NUMERIC_COLUMNS:</code> | Loop: assign each item from NUMERIC_COLUMNS into name, then execute the indented body. |
| 55 | <code>        raw = (row.get(name) or &quot;&quot;).strip()</code> | Set raw. Call (row.get(name) or '').strip with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 56 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 57 | <code>            value = float(raw)</code> | Set value. Convert raw to float. |
| 58 | <code>        except ValueError:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 59 | <code>            if raw and raw.lower() not in {&quot;nan&quot;, &quot;null&quot;, &quot;none&quot;}:</code> | Branch only if raw and raw.lower() not in {'nan', 'null', 'none'} is true; otherwise skip this indented block or take its following elif/else. |
| 60 | <code>                raise ValueError(f&quot;Invalid numeric value in {name}: {raw!r}&quot;) from None</code> | Raise ValueError(f'Invalid numeric value in {name}: {raw!r}') and stop this operation; chain the original cause for diagnostics. |
| 61 | <code>            value = math.nan</code> | Set value. Read math.nan from the current function/object state. |
| 62 | <code>        features[f&quot;missing_{name}&quot;] = int(not math.isfinite(value))</code> | Set features[f'missing_{name}']. Convert not math.isfinite(value) to int. |
| 63 | <code>        features[name] = value if math.isfinite(value) else 0.0</code> | Set features[name]. Choose value when math.isfinite(value) is true; otherwise choose 0.0. |
| 64 | <code>    for name in CATEGORICAL_COLUMNS:</code> | Loop: assign each item from CATEGORICAL_COLUMNS into name, then execute the indented body. |
| 65 | <code>        features[name] = (row.get(name) or &quot;unknown&quot;).strip().lower()</code> | Set features[name]. Call (row.get(name) or 'unknown').strip().lower with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 66 | <code>    return features</code> | Return to the caller: Read features from the current function/object state. |
| 67 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 68 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 69 | <code>def iter_csv(path: str &#124; Path):</code> | Define function/method iter_csv. Lazily yields one Record at a time from a CSV; validates essential columns and malformed rows before handing records to the engine. |
| 70 | <code>    with Path(path).open(&quot;r&quot;, newline=&quot;&quot;, encoding=&quot;utf-8-sig&quot;) as stream:</code> | Enter managed resource/lock context Path(path).open('r', newline='', encoding='utf-8-sig') as stream. Exiting the block releases/closes it, including on exceptions. |
| 71 | <code>        reader = csv.DictReader(line for line in stream if not line.startswith(&quot;#&quot;))</code> | Set reader. Call csv.DictReader with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 72 | <code>        required = {&quot;Label&quot;, &quot;Attack Type&quot;, &quot;Proto&quot;, &quot;Dur&quot;, &quot;TotPkts&quot;, &quot;TotBytes&quot;}</code> | Set required. Read {'Label', 'Attack Type', 'Proto', 'Dur', 'TotPkts', 'TotBytes'} from the current function/object state. |
| 73 | <code>        if not reader.fieldnames or not required.issubset(reader.fieldnames):</code> | Branch only if not reader.fieldnames or not required.issubset(reader.fieldnames) is true; otherwise skip this indented block or take its following elif/else. |
| 74 | <code>            raise ValueError(</code> | Raise ValueError(f'Missing CSV columns: {sorted(required - set(reader.fieldnames or []))}') and stop this operation; the caller can record/report this invalid condition. |
| 75 | <code>                f&quot;Missing CSV columns: {sorted(required - set(reader.fieldnames or []))}&quot;</code> | Continuation of the statement above. Read f'Missing CSV columns: {sorted(required - set(reader.fieldnames or []))}' from the current function/object state. |
| 76 | <code>            )</code> | Close the call to ValueError begun above; this is punctuation, not a separate operation. |
| 77 | <code>        for index, row in enumerate(reader):</code> | Loop: assign each item from enumerate(reader) into (index, row), then execute the indented body. |
| 78 | <code>            if None in row:</code> | Branch only if None in row is true; otherwise skip this indented block or take its following elif/else. |
| 79 | <code>                raise ValueError(f&quot;Malformed CSV row {index + 2}&quot;)</code> | Raise ValueError(f'Malformed CSV row {index + 2}') and stop this operation; the caller can record/report this invalid condition. |
| 80 | <code>            family = row[&quot;Attack Type&quot;].strip()</code> | Set family. Call row['Attack Type'].strip with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 81 | <code>            yield Record(</code> | Yield one item to the caller and pause this generator: Construct a new Record using index, float(index), extract_flow_features(row), binary_label(family, row['Label']), family. |
| 82 | <code>                index,</code> | Continuation of the statement above. Read index from the current function/object state. |
| 83 | <code>                float(index),</code> | Continuation of the statement above. Convert index to float. |
| 84 | <code>                extract_flow_features(row),</code> | Continuation of the statement above. Call extract_flow_features with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 85 | <code>                binary_label(family, row[&quot;Label&quot;]),</code> | Continuation of the statement above. Call binary_label with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 86 | <code>                family,</code> | Continuation of the statement above. Read family from the current function/object state. |
| 87 | <code>            )</code> | Close the call to Record begun above; this is punctuation, not a separate operation. |
| 88 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 89 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 90 | <code>def audit_csv(path: str &#124; Path) -&gt; dict:</code> | Define function/method audit_csv. Counts rows, attack families, missing fields and exact duplicate row signatures without training. The duplicate-signature set grows with dataset size. |
| 91 | <code>    counts: Counter = Counter()</code> | Set counts. Call Counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 92 | <code>    missing: Counter = Counter()</code> | Set missing. Call Counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 93 | <code>    seen: set[str] = set()</code> | Set seen. Call set with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 94 | <code>    duplicate_rows = 0</code> | Set duplicate_rows. Use the literal 0. |
| 95 | <code>    rows = 0</code> | Set rows. Use the literal 0. |
| 96 | <code>    import hashlib</code> | Import hashlib to calculate SHA256 fingerprints of exact source bytes. |
| 97 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 98 | <code>    with Path(path).open(&quot;r&quot;, newline=&quot;&quot;, encoding=&quot;utf-8-sig&quot;) as stream:</code> | Enter managed resource/lock context Path(path).open('r', newline='', encoding='utf-8-sig') as stream. Exiting the block releases/closes it, including on exceptions. |
| 99 | <code>        reader = csv.DictReader(line for line in stream if not line.startswith(&quot;#&quot;))</code> | Set reader. Call csv.DictReader with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 100 | <code>        columns = reader.fieldnames or []</code> | Set columns. Evaluate reader.fieldnames or [] left to right with short-circuit or. |
| 101 | <code>        for row in reader:</code> | Loop: assign each item from reader into row, then execute the indented body. |
| 102 | <code>            if None in row:</code> | Branch only if None in row is true; otherwise skip this indented block or take its following elif/else. |
| 103 | <code>                raise ValueError(f&quot;Malformed row {rows + 2}&quot;)</code> | Raise ValueError(f'Malformed row {rows + 2}') and stop this operation; the caller can record/report this invalid condition. |
| 104 | <code>            rows += 1</code> | Increase rows by 1 and retain the updated state. |
| 105 | <code>            counts[row.get(&quot;Attack Type&quot;, &quot;unknown&quot;)] += 1</code> | Increase counts[row.get('Attack Type', 'unknown')] by 1 and retain the updated state. |
| 106 | <code>            for key, value in row.items():</code> | Loop: assign each item from row.items() into (key, value), then execute the indented body. |
| 107 | <code>                if not value or value.strip().lower() in {&quot;nan&quot;, &quot;null&quot;, &quot;none&quot;}:</code> | Branch only if not value or value.strip().lower() in {'nan', 'null', 'none'} is true; otherwise skip this indented block or take its following elif/else. |
| 108 | <code>                    missing[key] += 1</code> | Increase missing[key] by 1 and retain the updated state. |
| 109 | <code>            signature = hashlib.sha256(repr(tuple(row.values())).encode()).hexdigest()</code> | Set signature. Call hashlib.sha256(repr(tuple(row.values())).encode()).hexdigest with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 110 | <code>            duplicate_rows += signature in seen</code> | Increase duplicate_rows by signature in seen and retain the updated state. |
| 111 | <code>            seen.add(signature)</code> | Insert signature into seen; set insertion keeps unique values. |
| 112 | <code>    return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 113 | <code>        &quot;rows&quot;: rows,</code> | Field rows: Named entry in the surrounding dictionary. Its value is rows; consumers access it by this key. |
| 114 | <code>        &quot;columns&quot;: columns,</code> | Field columns: Named entry in the surrounding dictionary. Its value is columns; consumers access it by this key. |
| 115 | <code>        &quot;attack_counts&quot;: dict(counts),</code> | Field attack_counts: Named entry in the surrounding dictionary. Its value is dict(counts); consumers access it by this key. |
| 116 | <code>        &quot;missing_counts&quot;: dict(missing),</code> | Field missing_counts: Named entry in the surrounding dictionary. Its value is dict(missing); consumers access it by this key. |
| 117 | <code>        &quot;duplicate_rows&quot;: duplicate_rows,</code> | Field duplicate_rows: Named entry in the surrounding dictionary. Its value is duplicate_rows; consumers access it by this key. |
| 118 | <code>        &quot;ordering&quot;: &quot;CSV row order only; chronological order is not established&quot;,</code> | Field ordering: Named entry in the surrounding dictionary. Its value is "CSV row order only; chronological order is not established"; consumers access it by this key. |
| 119 | <code>    }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |

## src/m3/model.py

**The actual online learner.** Wraps the installed River Hoeffding Adaptive Tree. It is one incremental model, not a neural network trained in epochs. Predict obtains the attack probability before learn updates the model. HAT has internal ADWIN detectors for branch adaptation; the separate monitor records changes in observed prediction errors.

Snapshot: 30 lines; SHA256 `6110282de738ea0aa149e0181187053dac8c70262b82806d8ddce47011a96b03`.

### Named operations

- `OnlineDetector.__init__` (L7): Constructs the HAT and a separate error ADWIN. Neither object has learned examples yet.
- `OnlineDetector.predict` (L18): Obtains class probabilities; missing class 1 defaults to zero. Thresholding creates a binary prediction and elapsed time measures prediction only.
- `OnlineDetector.learn` (L24): Optionally feeds 0/1 prediction error to the external monitor, updates HAT with the ground-truth label, and returns whether the external monitor alarmed.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>from time import perf_counter</code> | Import perf_counter from time. This makes the named library helpers available without the module prefix. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>from river import drift, tree</code> | Import drift, tree from river. This makes the named library helpers available without the module prefix. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 6 | <code>class OnlineDetector:</code> | Define class OnlineDetector. Groups the following statements into a named reusable operation. |
| 7 | <code>    def __init__(self, config):</code> | Define function/method __init__. Constructs the HAT and a separate error ADWIN. Neither object has learned examples yet. |
| 8 | <code>        self.model = tree.HoeffdingAdaptiveTreeClassifier(</code> | Set self.model. Call tree.HoeffdingAdaptiveTreeClassifier with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 9 | <code>            grace_period=config.grace_period,</code> | Keyword argument grace_period for the call above. HAT split-evaluation interval in observations at a leaf; not a warm-up count or ADWIN window size. |
| 10 | <code>            seed=config.seed,</code> | Keyword argument seed for the call above. Seed for reproducible offline random selection and HAT randomness; live OVS sampling is not made deterministic by this Python seed. |
| 11 | <code>            drift_detector=drift.ADWIN(delta=config.drift_delta),</code> | Keyword argument drift_detector for the call above. ADWIN instance used inside HAT for branch adaptation. |
| 12 | <code>            nominal_attributes=[&quot;Proto&quot;],</code> | Keyword argument nominal_attributes for the call above. Treat Proto as categorical rather than a numeric ordered measurement. |
| 13 | <code>            max_size=100,</code> | Keyword argument max_size for the call above. River HAT maximum model size setting (MiB); this is not a maximum tree depth. |
| 14 | <code>        )</code> | Close the call to tree.HoeffdingAdaptiveTreeClassifier begun above; this is punctuation, not a separate operation. |
| 15 | <code>        self.monitor = drift.ADWIN(delta=config.drift_delta)</code> | Construct a SECOND ADWIN dedicated to logged prediction error. It does not replace the ADWIN instances HAT uses internally and is not a command to reset the tree. |
| 16 | <code>        self.threshold = config.threshold</code> | Keep the probability cutoff on the wrapper so prediction can turn an attack probability into 0/1 consistently across runs. |
| 17 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 18 | <code>    def predict(self, features):</code> | Define function/method predict. Obtains class probabilities; missing class 1 defaults to zero. Thresholding creates a binary prediction and elapsed time measures prediction only. |
| 19 | <code>        started = perf_counter()</code> | Read a high-resolution monotonic timer immediately before prediction; only prediction work is timed, not model training. |
| 20 | <code>        probabilities = self.model.predict_proba_one(features)</code> | Give HAT the feature dictionary, obtain probabilities keyed by class label, and leave the model untrained on this observation. |
| 21 | <code>        score = float(probabilities.get(1, 0.0))</code> | Extract the attack-class (integer 1) probability. An empty/new model may have no class 1 entry, so use probability 0.0. |
| 22 | <code>        return int(score &gt;= self.threshold), score, (perf_counter() - started) * 1000</code> | Return three values: the thresholded 0/1 alarm, unthresholded probability for ROC-AUC, and elapsed prediction time converted from seconds to milliseconds. |
| 23 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 24 | <code>    def learn(self, features, label, predicted, monitor=True):</code> | Define function/method learn. Optionally feeds 0/1 prediction error to the external monitor, updates HAT with the ground-truth label, and returns whether the external monitor alarmed. |
| 25 | <code>        detected = False</code> | Default the external drift alarm to false, including warm-up calls with monitor=False. |
| 26 | <code>        if monitor:</code> | Only feed prediction errors to the external ADWIN for scored evaluation observations; warm-up still trains HAT but bypasses this monitor. |
| 27 | <code>            self.monitor.update(int(label != predicted))</code> | Convert correctness into supervised error: correct => 0, wrong => 1. ADWIN observes whether this error stream changes. |
| 28 | <code>            detected = self.monitor.drift_detected</code> | Read whether the preceding error update triggered an external ADWIN alarm. Reading this flag does not change HAT. |
| 29 | <code>        self.model.learn_one(features, label)</code> | Train HAT incrementally using this observation and the revealed true label; its own internal ADWIN can adapt tree branches. |
| 30 | <code>        return detected</code> | Give Evaluation the external alarm flag so it can append a drift-event row without resetting the model. |

## src/m3/metrics.py

**Measurement envelopes and detection metrics.** Keeps missing measurements distinct from real zeroes. All quality scores are calculated from scored observations, excluding warm-up and unknown labels. ROC-AUC uses average ranks for equal scores. Exact AUC retains labels and scores in memory, so the entire pipeline is not constant-memory despite incremental model learning.

Snapshot: 92 lines; SHA256 `bceece8e984d031c70bfa66a952a7dd661ca08cd830d720dd170006614ee89ec`.

### Named operations

- `measurement` (L7): Wraps a value with its unit, evidence status and reason; None or non-finite Python floats become explicitly unavailable.
- `roc_auc` (L23): Computes rank-based AUC: probability that an attack scores above a benign example, with tied scores receiving half credit. Needs both classes.
- `QualityMetrics.__init__` (L41): Initializes confusion counts and raw score/latency lists for one run, plus counters for held-out SYNFlood recall.
- `QualityMetrics.update` (L49): Adds exactly one scored labeled prediction. Prediction must have happened before this method and before learning.
- `QualityMetrics.summary` (L58): Calculates attack metrics, per-class metrics, mean/p95 latency, and optional unseen-family recall; division by zero produces unavailable.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 2 | <code>from collections import Counter</code> | Import Counter from collections. This makes the named library helpers available without the module prefix. |
| 3 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 4 | <code>import numpy as np</code> | Import numpy as np to calculate numeric means and percentiles. |
| 5 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <code>def measurement(value, unit=&quot;ratio&quot;, reason=None, status=&quot;measured&quot;):</code> | Define function/method measurement. Wraps a value with its unit, evidence status and reason; None or non-finite Python floats become explicitly unavailable. |
| 8 | <code>    if value is None or (isinstance(value, float) and not math.isfinite(value)):</code> | Branch only if value is None or (isinstance(value, float) and (not math.isfinite(value))) is true; otherwise skip this indented block or take its following elif/else. |
| 9 | <code>        return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 10 | <code>            &quot;value&quot;: None,</code> | Field value: Named entry in the surrounding dictionary. Its value is None; consumers access it by this key. |
| 11 | <code>            &quot;unit&quot;: unit,</code> | Field unit: Measurement units or observation unit; flow for CSV and window for packet/live replay. |
| 12 | <code>            &quot;status&quot;: &quot;unavailable&quot;,</code> | Field status: Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 13 | <code>            &quot;reason&quot;: reason or &quot;Insufficient observations&quot;,</code> | Field reason: Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 14 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 15 | <code>    return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 16 | <code>        &quot;value&quot;: float(value),</code> | Field value: Named entry in the surrounding dictionary. Its value is float(value); consumers access it by this key. |
| 17 | <code>        &quot;unit&quot;: unit,</code> | Field unit: Measurement units or observation unit; flow for CSV and window for packet/live replay. |
| 18 | <code>        &quot;status&quot;: status,</code> | Field status: Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 19 | <code>        &quot;reason&quot;: reason if status == &quot;estimated&quot; else None,</code> | Field reason: Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 20 | <code>    }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 21 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 22 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 23 | <code>def roc_auc(labels: list[int], scores: list[float]) -&gt; float &#124; None:</code> | Define function/method roc_auc. Computes rank-based AUC: probability that an attack scores above a benign example, with tied scores receiving half credit. Needs both classes. |
| 24 | <code>    positive, negative = sum(labels), len(labels) - sum(labels)</code> | Because labels are 0/1, summing counts attacks; total minus attacks counts benign observations. |
| 25 | <code>    if not positive or not negative:</code> | AUC requires both classes. A one-class stream cannot show how well attacks rank above benign records. |
| 26 | <code>        return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 27 | <code>    ordered = sorted(zip(scores, labels))</code> | Pair score/label and sort ascending by score. Ties are subsequently grouped, preventing label-based tie ordering from biasing AUC. |
| 28 | <code>    rank_sum = 0.0</code> | Accumulate the ranks assigned to positive examples; ranks start at 1 rather than zero. |
| 29 | <code>    i = 0</code> | Start at the first unprocessed sorted score group. |
| 30 | <code>    while i &lt; len(ordered):</code> | Repeat the indented body while i < len(ordered) remains true; the body must advance state or terminate. |
| 31 | <code>        j = i + 1</code> | Begin searching just past i for the end of its equal-score group. |
| 32 | <code>        while j &lt; len(ordered) and ordered[j][0] == ordered[i][0]:</code> | Advance through all entries having exactly the same probability so they receive one shared average rank. |
| 33 | <code>            j += 1</code> | Increase j by 1 and retain the updated state. |
| 34 | <code>        average_rank = ((i + 1) + j) / 2</code> | A tie block spans zero-based i through j-1, hence one-based ranks i+1 through j. Their midpoint is the tie rank. |
| 35 | <code>        rank_sum += average_rank * sum(label for _, label in ordered[i:j])</code> | Count positives in the tie group and add their shared ranks; tied positive/negative comparisons therefore receive half credit. |
| 36 | <code>        i = j</code> | Skip the score group just handled and process the next score value. |
| 37 | <code>    return (rank_sum - positive * (positive + 1) / 2) / (positive * negative)</code> | Subtract positive-only rank contributions and divide by all positive-negative pairs. This yields AUC, including half credit for ties. |
| 38 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 39 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 40 | <code>class QualityMetrics:</code> | Define class QualityMetrics. Groups the following statements into a named reusable operation. |
| 41 | <code>    def __init__(self):</code> | Define function/method __init__. Initializes confusion counts and raw score/latency lists for one run, plus counters for held-out SYNFlood recall. |
| 42 | <code>        self.confusion = Counter()</code> | Set self.confusion. Call Counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 43 | <code>        self.labels: list[int] = []</code> | Set self.labels. Build the ordered list below; order is retained. |
| 44 | <code>        self.scores: list[float] = []</code> | Set self.scores. Build the ordered list below; order is retained. |
| 45 | <code>        self.latencies: list[float] = []</code> | Set self.latencies. Build the ordered list below; order is retained. |
| 46 | <code>        self.unseen_true = 0</code> | Set self.unseen_true. Use the literal 0. |
| 47 | <code>        self.unseen_detected = 0</code> | Set self.unseen_detected. Use the literal 0. |
| 48 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 49 | <code>    def update(self, label, predicted, score, latency_ms, family, unseen_family=&quot;SYNFlood&quot;):</code> | Define function/method update. Adds exactly one scored labeled prediction. Prediction must have happened before this method and before learning. |
| 50 | <code>        self.confusion[(label, predicted)] += 1</code> | Increment the confusion cell addressed by (truth, prediction): (1,1)=TP; (0,1)=FP; (0,0)=TN; (1,0)=FN. |
| 51 | <code>        self.labels.append(label)</code> | Retain this scored observation's true label for exact AUC computation. |
| 52 | <code>        self.scores.append(score)</code> | Retain its original probability score, rather than the thresholded 0/1 prediction, for AUC. |
| 53 | <code>        self.latencies.append(latency_ms)</code> | Retain prediction-only latency in milliseconds for mean and 95th percentile. |
| 54 | <code>        if label == 1 and family == unseen_family:</code> | Branch only if label == 1 and family == unseen_family is true; otherwise skip this indented block or take its following elif/else. |
| 55 | <code>            self.unseen_true += 1</code> | Count an actual attack from the designated held-out family (default SYNFlood). |
| 56 | <code>            self.unseen_detected += int(predicted == 1)</code> | Increase detected held-out attacks by 1 only if this attack was alarmed. |
| 57 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 58 | <code>    def summary(self, unseen_enabled=False):</code> | Define function/method summary. Calculates attack metrics, per-class metrics, mean/p95 latency, and optional unseen-family recall; division by zero produces unavailable. |
| 59 | <code>        tp, fp = self.confusion[(1, 1)], self.confusion[(0, 1)]</code> | Read true positives and false positives; Counter returns zero for unseen confusion cells. |
| 60 | <code>        tn, fn = self.confusion[(0, 0)], self.confusion[(1, 0)]</code> | Read true negatives and false negatives. |
| 61 | <code>        divide = lambda a, b: a / b if b else None</code> | Define safe division so an absent denominator produces unavailable (None), not a fabricated zero or exception. |
| 62 | <code>        result = {</code> | Set result. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 63 | <code>            &quot;precision&quot;: measurement(divide(tp, tp + fp), reason=&quot;No positive predictions&quot;),</code> | Field precision: TP/(TP+FP): proportion of alarms that are correct. |
| 64 | <code>            &quot;recall&quot;: measurement(divide(tp, tp + fn), reason=&quot;No positive labels&quot;),</code> | Field recall: TP/(TP+FN): proportion of actual attack observations detected. |
| 65 | <code>            &quot;f1&quot;: measurement(</code> | Field f1: 2TP/(2TP+FP+FN): balances precision and recall. |
| 66 | <code>                divide(2 * tp, 2 * tp + fp + fn), reason=&quot;No positive labels or predictions&quot;</code> | Literal component of the surrounding statement: 'No positive labels or predictions'. Its role is determined by the field/call immediately above. |
| 67 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 68 | <code>            &quot;roc_auc&quot;: measurement(</code> | Field roc_auc: Rank-based separability of attack scores; needs both classes. |
| 69 | <code>                roc_auc(self.labels, self.scores), reason=&quot;ROC-AUC requires both classes&quot;</code> | Continuation of the statement above. Call roc_auc with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 70 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 71 | <code>            &quot;false_positive_rate&quot;: measurement(divide(fp, fp + tn), reason=&quot;No negative labels&quot;),</code> | Field false_positive_rate: FP/(FP+TN): fraction of benign observations incorrectly alarmed. |
| 72 | <code>            &quot;inference_latency_ms&quot;: measurement(</code> | Field inference_latency_ms: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 73 | <code>                np.mean(self.latencies) if self.latencies else None, &quot;ms&quot;</code> | Continuation of the statement above. Choose np.mean(self.latencies) when self.latencies is true; otherwise choose None. |
| 74 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 75 | <code>            &quot;inference_latency_p95_ms&quot;: measurement(</code> | Field inference_latency_p95_ms: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 76 | <code>                np.percentile(self.latencies, 95) if self.latencies else None, &quot;ms&quot;</code> | Continuation of the statement above. Choose np.percentile(self.latencies, 95) when self.latencies is true; otherwise choose None. |
| 77 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 78 | <code>            &quot;unseen_attack_recall&quot;: measurement(</code> | Field unseen_attack_recall: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 79 | <code>                divide(self.unseen_detected, self.unseen_true) if unseen_enabled else None,</code> | Continuation of the statement above. Choose divide(self.unseen_detected, self.unseen_true) when unseen_enabled is true; otherwise choose None. |
| 80 | <code>                reason=&quot;No held-out SYN attack observations&quot;</code> | Keyword argument reason for the call above. Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 81 | <code>                if unseen_enabled</code> | Continuation of the statement above. Read unseen_enabled from the current function/object state. |
| 82 | <code>                else &quot;Not an unseen-attack scenario&quot;,</code> | Literal component of the surrounding statement: 'Not an unseen-attack scenario'. Its role is determined by the field/call immediately above. |
| 83 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 84 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 85 | <code>        for label, prefix in [(1, &quot;attack&quot;), (0, &quot;benign&quot;)]:</code> | Calculate one-vs-rest metrics twice, treating attack and benign in turn as the target class. |
| 86 | <code>            true = self.confusion[(label, label)]</code> | Set true. Read self.confusion[label, label] from the current function/object state. |
| 87 | <code>            false = self.confusion[(1 - label, label)]</code> | Set false. Read self.confusion[1 - label, label] from the current function/object state. |
| 88 | <code>            missed = self.confusion[(label, 1 - label)]</code> | Set missed. Read self.confusion[label, 1 - label] from the current function/object state. |
| 89 | <code>            result[f&quot;{prefix}_precision&quot;] = measurement(divide(true, true + false))</code> | Set result[f'{prefix}_precision']. Create a value/unit/status/reason envelope and preserve unavailable versus true zero. |
| 90 | <code>            result[f&quot;{prefix}_recall&quot;] = measurement(divide(true, true + missed))</code> | Set result[f'{prefix}_recall']. Create a value/unit/status/reason envelope and preserve unavailable versus true zero. |
| 91 | <code>            result[f&quot;{prefix}_f1&quot;] = measurement(divide(2 * true, 2 * true + false + missed))</code> | Set result[f'{prefix}_f1']. Create a value/unit/status/reason envelope and preserve unavailable versus true zero. |
| 92 | <code>        return result</code> | Return to the caller: Read result from the current function/object state. |

## src/m3/engine.py

**Replay execution and predict-before-learn evaluation.** Evaluation is shared by offline replay and live collection. run_replay chooses CSV or PCAP input, maintains counts, obtains independent labels, samples features, and writes evidence. The source field official_5g_nidd records provenance; it does not imply live deployment or a completed study.

Snapshot: 236 lines; SHA256 `9e99cd0676d80f647099d2de20f780eaef724480f2af393907a2d21fbc6b21f7`.

### Named operations

- `Evaluation.__init__` (L19): Creates one detector and evaluator state for this run: quality, first attack/alarm, unsampled-packet tracking, processed count, and summary-save timer.
- `Evaluation.observe` (L31): One observation enters here. Exclude held-out warm-up examples, predict and log first, score labeled evaluation observations, then learn. Unknown labels never train.
- `Evaluation.summary` (L106): Produces metric envelopes plus detection delay and packet count. CSV row positions cannot supply physical delay. Post-drift recovery remains unavailable pending annotated analysis.
- `run_replay` (L137): Verifies official input (unless explicitly a fixture), creates a writer/new model, starts resource monitoring, replays CSV or PCAP, then finalizes evidence even for captured processing failures.
- `run_replay.observe_window` (L185): Assigns truth to a completed packet window, keeps warm-up separate, and calls the shared evaluator with independent original-packet counts when available.

CSV warm-up is determined from eligible records before the selection draw. At N=10, roughly one tenth of that prefix is actually learned. Every selected held-out observation is predicted, scored, then learned; this is online test-then-train with immediate oracle labels, not a frozen held-out model test. The scenario="drift" name alone does not inject a shift. Packet windows derive ground truth from unsampled original packets. The final partial capture window is intentionally dropped.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 2 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 3 | <code>import random</code> | Import random to draw seeded pseudo-random samples for offline selection. |
| 4 | <code>import time</code> | Import time to measure elapsed work with monotonic timers and live collection with epoch wall-clock time. |
| 5 | <code>from dataclasses import replace</code> | Import replace from dataclasses. This makes the named library helpers available without the module prefix. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <code>from m3.data import iter_csv</code> | Import iter_csv from m3.data. These are project definitions; follow the named module in this guide to see their implementation. |
| 8 | <code>from m3.ground_truth import FlowLabels, WindowTruth</code> | Import FlowLabels, WindowTruth from m3.ground_truth. These are project definitions; follow the named module in this guide to see their implementation. |
| 9 | <code>from m3.labels import LabelTimeline</code> | Import LabelTimeline from m3.labels. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <code>from m3.metrics import QualityMetrics, measurement</code> | Import QualityMetrics, measurement from m3.metrics. These are project definitions; follow the named module in this guide to see their implementation. |
| 11 | <code>from m3.model import OnlineDetector</code> | Import OnlineDetector from m3.model. These are project definitions; follow the named module in this guide to see their implementation. |
| 12 | <code>from m3.packets import WindowAccumulator, iter_pcap, parse_header</code> | Import WindowAccumulator, iter_pcap, parse_header from m3.packets. These are project definitions; follow the named module in this guide to see their implementation. |
| 13 | <code>from m3.provenance import verify_input</code> | Import verify_input from m3.provenance. These are project definitions; follow the named module in this guide to see their implementation. |
| 14 | <code>from m3.resources import ResourceMonitor</code> | Import ResourceMonitor from m3.resources. These are project definitions; follow the named module in this guide to see their implementation. |
| 15 | <code>from m3.store import RunWriter</code> | Import RunWriter from m3.store. These are project definitions; follow the named module in this guide to see their implementation. |
| 16 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 17 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 18 | <code>class Evaluation:</code> | Define class Evaluation. Groups the following statements into a named reusable operation. |
| 19 | <code>    def __init__(self, config, writer, model=None):</code> | Define function/method __init__. Creates one detector and evaluator state for this run: quality, first attack/alarm, unsampled-packet tracking, processed count, and summary-save timer. |
| 20 | <code>        self.config, self.writer = config, writer</code> | Set (self.config, self.writer). Bundle these values in a tuple: (config, writer). |
| 21 | <code>        self.detector = model or OnlineDetector(config)</code> | Set self.detector. Evaluate model or OnlineDetector(config) left to right with short-circuit or. |
| 22 | <code>        self.quality = QualityMetrics()</code> | Set self.quality. Construct a new QualityMetrics using the shown keyword/default values. |
| 23 | <code>        self.first_attack = None</code> | Set self.first_attack. Use the literal None (None means unavailable/not set). |
| 24 | <code>        self.first_alarm = None</code> | Set self.first_alarm. Use the literal None (None means unavailable/not set). |
| 25 | <code>        self.attack_packets = 0</code> | Set self.attack_packets. Use the literal 0. |
| 26 | <code>        self.packet_counts_known = True</code> | Set self.packet_counts_known. Use the literal True. |
| 27 | <code>        self.packets_at_alarm = None</code> | Set self.packets_at_alarm. Use the literal None (None means unavailable/not set). |
| 28 | <code>        self.processed = 0</code> | Set self.processed. Use the literal 0. |
| 29 | <code>        self.last_save = time.perf_counter()</code> | Set self.last_save. Call time.perf_counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 31 | <code>    def observe(</code> | Define function/method observe. One observation enters here. Exclude held-out warm-up examples, predict and log first, score labeled evaluation observations, then learn. Unknown labels never train. |
| 32 | <code>        self,</code> | Continue the surrounding Evaluation.observe statement: self,. The indentation and open brackets connect it to the operation above. |
| 33 | <code>        record,</code> | Continue the surrounding Evaluation.observe statement: record,. The indentation and open brackets connect it to the operation above. |
| 34 | <code>        warmup=False,</code> | Keyword argument warmup for the call above. Pass the shown value False into that parameter. |
| 35 | <code>        sampled_packets=None,</code> | Keyword argument sampled_packets for the call above. Pass the shown value None into that parameter. |
| 36 | <code>        observed_time=None,</code> | Keyword argument observed_time for the call above. Pass the shown value None into that parameter. |
| 37 | <code>        ground_truth_packets=None,</code> | Keyword argument ground_truth_packets for the call above. Pass the shown value None into that parameter. |
| 38 | <code>    ):</code> | Continue the surrounding Evaluation.observe statement: ):. The indentation and open brackets connect it to the operation above. |
| 39 | <code>        counts = self.writer.summary[&quot;counts&quot;]</code> | Set counts. Read self.writer.summary['counts'] from the current function/object state. |
| 40 | <code>        label = record.label</code> | Set label. Read record.label from the current function/object state. |
| 41 | <code>        if warmup and self.config.scenario == &quot;unseen&quot; and record.attack_family == &quot;SYNFlood&quot;:</code> | Branch only if warmup and self.config.scenario == 'unseen' and (record.attack_family == 'SYNFlood') is true; otherwise skip this indented block or take its following elif/else. |
| 42 | <code>            counts[&quot;excluded&quot;] += 1</code> | Increase counts['excluded'] by 1 and retain the updated state. |
| 43 | <code>            return</code> | Return to the caller with None. |
| 44 | <code>        if not warmup and self.first_alarm is None:</code> | Branch only if not warmup and self.first_alarm is None is true; otherwise skip this indented block or take its following elif/else. |
| 45 | <code>            if label == 1 and self.first_attack is None:</code> | Branch only if label == 1 and self.first_attack is None is true; otherwise skip this indented block or take its following elif/else. |
| 46 | <code>                self.first_attack = record.time</code> | Set self.first_attack. Read record.time from the current function/object state. |
| 47 | <code>            if self.first_attack is not None:</code> | Branch only if self.first_attack is not None is true; otherwise skip this indented block or take its following elif/else. |
| 48 | <code>                if ground_truth_packets is None:</code> | Branch only if ground_truth_packets is None is true; otherwise skip this indented block or take its following elif/else. |
| 49 | <code>                    self.packet_counts_known = False</code> | Set self.packet_counts_known. Use the literal False. |
| 50 | <code>                else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 51 | <code>                    self.attack_packets += ground_truth_packets</code> | Increase self.attack_packets by ground_truth_packets and retain the updated state. |
| 52 | <code>        predicted, score, latency = self.detector.predict(record.features)</code> | Predict from features only. This happens before the true label is given to the learner and before the scored update. |
| 53 | <code>        observed_time = (</code> | Set observed_time. Choose observed_time when observed_time is not None is true; otherwise choose record.time + (0 if self.config.mode == 'csv_replay' else self.config.window_seconds). |
| 54 | <code>            observed_time</code> | Continuation of the statement above. Choose observed_time when observed_time is not None is true; otherwise choose record.time + (0 if self.config.mode == 'csv_replay' else self.config.window_seconds). |
| 55 | <code>            if observed_time is not None</code> | Continuation of the statement above. Evaluate the comparison observed_time is not None to True/False; comparisons may short-circuit. |
| 56 | <code>            else record.time</code> | Continuation of the statement above. Calculate record.time + (0 if self.config.mode == 'csv_replay' else self.config.window_seconds) using add; / returns a floating-point ratio and // floors division where used. |
| 57 | <code>            + (0 if self.config.mode == &quot;csv_replay&quot; else self.config.window_seconds)</code> | Continuation of the statement above. Choose 0 when self.config.mode == 'csv_replay' is true; otherwise choose self.config.window_seconds. |
| 58 | <code>        )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 59 | <code>        phase = &quot;unlabeled&quot; if label is None else &quot;warmup&quot; if warmup else &quot;evaluation&quot;</code> | Set phase. Choose 'unlabeled' when label is None is true; otherwise choose 'warmup' if warmup else 'evaluation'. |
| 60 | <code>        self.writer.append(</code> | Append one raw evidence row to the named CSV and flush it immediately. |
| 61 | <code>            &quot;predictions&quot;,</code> | Literal component of the surrounding statement: 'predictions'. Its role is determined by the field/call immediately above. |
| 62 | <code>            {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 63 | <code>                &quot;index&quot;: record.index,</code> | Field index: Named entry in the surrounding dictionary. Its value is record.index; consumers access it by this key. |
| 64 | <code>                &quot;time&quot;: record.time,</code> | Field time: Named entry in the surrounding dictionary. Its value is record.time; consumers access it by this key. |
| 65 | <code>                &quot;y_true&quot;: label,</code> | Field y_true: Named entry in the surrounding dictionary. Its value is label; consumers access it by this key. |
| 66 | <code>                &quot;y_pred&quot;: predicted,</code> | Field y_pred: Named entry in the surrounding dictionary. Its value is predicted; consumers access it by this key. |
| 67 | <code>                &quot;score&quot;: score,</code> | Field score: Named entry in the surrounding dictionary. Its value is score; consumers access it by this key. |
| 68 | <code>                &quot;latency_ms&quot;: latency,</code> | Field latency_ms: Named entry in the surrounding dictionary. Its value is latency; consumers access it by this key. |
| 69 | <code>                &quot;phase&quot;: phase,</code> | Field phase: Named entry in the surrounding dictionary. Its value is phase; consumers access it by this key. |
| 70 | <code>                &quot;attack_family&quot;: record.attack_family,</code> | Field attack_family: Named entry in the surrounding dictionary. Its value is record.attack_family; consumers access it by this key. |
| 71 | <code>                &quot;sampled_packets&quot;: sampled_packets,</code> | Field sampled_packets: Named entry in the surrounding dictionary. Its value is sampled_packets; consumers access it by this key. |
| 72 | <code>                &quot;observed_time&quot;: observed_time,</code> | Field observed_time: Named entry in the surrounding dictionary. Its value is observed_time; consumers access it by this key. |
| 73 | <code>                &quot;ground_truth_packets&quot;: ground_truth_packets,</code> | Field ground_truth_packets: Named entry in the surrounding dictionary. Its value is ground_truth_packets; consumers access it by this key. |
| 74 | <code>            },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 75 | <code>        )</code> | Close the call to self.writer.append begun above; this is punctuation, not a separate operation. |
| 76 | <code>        if label is None:</code> | Unknown truth: log the prediction but do not score or train with an invented answer. |
| 77 | <code>            counts[&quot;unlabeled&quot;] += 1</code> | Increase counts['unlabeled'] by 1 and retain the updated state. |
| 78 | <code>        elif warmup:</code> | Known truth in warm-up: train HAT without including this example in reported evaluation quality. |
| 79 | <code>            counts[&quot;warmup&quot;] += 1</code> | Increase counts['warmup'] by 1 and retain the updated state. |
| 80 | <code>            self.detector.learn(record.features, label, predicted, monitor=False)</code> | Warm up HAT using the revealed label, while deliberately keeping the external error-monitor history clean. |
| 81 | <code>        else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 82 | <code>            # Evaluation order is deliberately visible: log/score before learning.</code> | Source comment: Evaluation order is deliberately visible: log/score before learning. This documents intent and does not execute. |
| 83 | <code>            self.quality.update(label, predicted, score, latency, record.attack_family)</code> | Score the already logged prediction BEFORE calling learn; this is the central protection against training on an answer before testing it. |
| 84 | <code>            counts[&quot;evaluated&quot;] += 1</code> | Increase counts['evaluated'] by 1 and retain the updated state. |
| 85 | <code>            if label == 1 and predicted == 1 and self.first_alarm is None:</code> | Branch only if label == 1 and predicted == 1 and (self.first_alarm is None) is true; otherwise skip this indented block or take its following elif/else. |
| 86 | <code>                self.first_alarm = observed_time</code> | Set self.first_alarm. Read observed_time from the current function/object state. |
| 87 | <code>                if self.packet_counts_known:</code> | Branch only if self.packet_counts_known is true; otherwise skip this indented block or take its following elif/else. |
| 88 | <code>                    self.packets_at_alarm = self.attack_packets</code> | Set self.packets_at_alarm. Read self.attack_packets from the current function/object state. |
| 89 | <code>            if self.detector.learn(record.features, label, predicted):</code> | After scoring, reveal the label to the model and log an event if its separate error ADWIN alarmed. |
| 90 | <code>                self.writer.append(</code> | Append one raw evidence row to the named CSV and flush it immediately. |
| 91 | <code>                    &quot;drift&quot;,</code> | Literal component of the surrounding statement: 'drift'. Its role is determined by the field/call immediately above. |
| 92 | <code>                    {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 93 | <code>                        &quot;time&quot;: record.time,</code> | Field time: Named entry in the surrounding dictionary. Its value is record.time; consumers access it by this key. |
| 94 | <code>                        &quot;index&quot;: record.index,</code> | Field index: Named entry in the surrounding dictionary. Its value is record.index; consumers access it by this key. |
| 95 | <code>                        &quot;event&quot;: &quot;error_distribution_change&quot;,</code> | Field event: Named entry in the surrounding dictionary. Its value is "error_distribution_change"; consumers access it by this key. |
| 96 | <code>                        &quot;detector&quot;: &quot;external_ADWIN&quot;,</code> | Field detector: Named entry in the surrounding dictionary. Its value is "external_ADWIN"; consumers access it by this key. |
| 97 | <code>                    },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 98 | <code>                )</code> | Close the call to self.writer.append begun above; this is punctuation, not a separate operation. |
| 99 | <code>                self.writer.summary[&quot;drift_count&quot;] += 1</code> | Increase self.writer.summary['drift_count'] by 1 and retain the updated state. |
| 100 | <code>        self.processed += 1</code> | Increase self.processed by 1 and retain the updated state. |
| 101 | <code>        if time.perf_counter() - self.last_save &gt; 1:</code> | Branch only if time.perf_counter() - self.last_save > 1 is true; otherwise skip this indented block or take its following elif/else. |
| 102 | <code>            self.writer.summary[&quot;metrics&quot;] = self.summary()</code> | Set self.writer.summary['metrics']. Call self.summary with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 103 | <code>            self.writer.save()</code> | Publish the current summary atomically so the dashboard can poll it safely. |
| 104 | <code>            self.last_save = time.perf_counter()</code> | Set self.last_save. Call time.perf_counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 105 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 106 | <code>    def summary(self):</code> | Define function/method summary. Produces metric envelopes plus detection delay and packet count. CSV row positions cannot supply physical delay. Post-drift recovery remains unavailable pending annotated analysis. |
| 107 | <code>        result = self.quality.summary(self.config.scenario == &quot;unseen&quot;)</code> | Set result. Call self.quality.summary with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 108 | <code>        physical = self.config.mode != &quot;csv_replay&quot;</code> | Set physical. Evaluate the comparison self.config.mode != 'csv_replay' to True/False; comparisons may short-circuit. |
| 109 | <code>        delay = (</code> | Set delay. Choose self.first_alarm - self.first_attack when physical and self.first_alarm is not None is true; otherwise choose None. |
| 110 | <code>            self.first_alarm - self.first_attack</code> | Continuation of the statement above. Choose self.first_alarm - self.first_attack when physical and self.first_alarm is not None is true; otherwise choose None. |
| 111 | <code>            if physical and self.first_alarm is not None</code> | Continuation of the statement above. Evaluate physical and self.first_alarm is not None left to right with short-circuit and. |
| 112 | <code>            else None</code> | Literal component of the surrounding statement: None. Its role is determined by the field/call immediately above. |
| 113 | <code>        )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 114 | <code>        result.update(</code> | Call result.update with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 115 | <code>            {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 116 | <code>                &quot;detection_time_seconds&quot;: measurement(</code> | Field detection_time_seconds: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 117 | <code>                    delay,</code> | Continuation of the statement above. Read delay from the current function/object state. |
| 118 | <code>                    &quot;seconds&quot;,</code> | Literal component of the surrounding statement: 'seconds'. Its role is determined by the field/call immediately above. |
| 119 | <code>                    &quot;No detected, labeled attack&quot;</code> | Continuation of the statement above. Choose 'No detected, labeled attack' when physical is true; otherwise choose 'CSV row indices are not physical timestamps'. |
| 120 | <code>                    if physical</code> | Continuation of the statement above. Read physical from the current function/object state. |
| 121 | <code>                    else &quot;CSV row indices are not physical timestamps&quot;,</code> | Literal component of the surrounding statement: 'CSV row indices are not physical timestamps'. Its role is determined by the field/call immediately above. |
| 122 | <code>                    status=&quot;measured&quot; if self.config.mode == &quot;live_sflow&quot; else &quot;estimated&quot;,</code> | Keyword argument status for the call above. Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 123 | <code>                ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 124 | <code>                &quot;packets_to_detect&quot;: measurement(</code> | Field packets_to_detect: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 125 | <code>                    self.packets_at_alarm if physical else None,</code> | Continuation of the statement above. Choose self.packets_at_alarm when physical is true; otherwise choose None. |
| 126 | <code>                    &quot;packets through alarm window&quot;,</code> | Literal component of the surrounding statement: 'packets through alarm window'. Its role is determined by the field/call immediately above. |
| 127 | <code>                    &quot;No detected attack with complete unsampled packet counts&quot;,</code> | Literal component of the surrounding statement: 'No detected attack with complete unsampled packet counts'. Its role is determined by the field/call immediately above. |
| 128 | <code>                ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 129 | <code>                &quot;post_drift_recovery_seconds&quot;: measurement(</code> | Field post_drift_recovery_seconds: Deliberately unavailable: no annotated recovery calculation is implemented. |
| 130 | <code>                    None, &quot;seconds&quot;, &quot;Requires an annotated drift boundary and recovery analysis&quot;</code> | Literal component of the surrounding statement: 'Requires an annotated drift boundary and recovery analysis'. Its role is determined by the field/call immediately above. |
| 131 | <code>                ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 132 | <code>            }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 133 | <code>        )</code> | Close the call to result.update begun above; this is punctuation, not a separate operation. |
| 134 | <code>        return result</code> | Return to the caller: Read result from the current function/object state. |
| 135 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 136 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 137 | <code>def run_replay(config, *, fixture=False, model=None):</code> | Define function/method run_replay. Verifies official input (unless explicitly a fixture), creates a writer/new model, starts resource monitoring, replays CSV or PCAP, then finalizes evidence even for captured processing failures. |
| 138 | <code>    provenance = None if fixture else verify_input(config.input_path, config.manifest_path)</code> | Set provenance. Choose None when fixture is true; otherwise choose verify_input(config.input_path, config.manifest_path). |
| 139 | <code>    writer = RunWriter(config, &quot;fixture&quot; if fixture else &quot;official_5g_nidd&quot;, provenance)</code> | Set writer. Construct a new RunWriter using config, 'fixture' if fixture else 'official_5g_nidd', provenance. |
| 140 | <code>    evaluator = Evaluation(config, writer, model)</code> | Set evaluator. Call Evaluation with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 141 | <code>    resources = ResourceMonitor(writer)</code> | Set resources. Construct a new ResourceMonitor using writer. |
| 142 | <code>    resources.start()</code> | Call resources.start with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 143 | <code>    rng = random.Random(config.seed)</code> | Set rng. Call random.Random with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 144 | <code>    error = None</code> | Set error. Use the literal None (None means unavailable/not set). |
| 145 | <code>    try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 146 | <code>        if config.mode == &quot;csv_replay&quot;:</code> | Branch only if config.mode == 'csv_replay' is true; otherwise skip this indented block or take its following elif/else. |
| 147 | <code>            eligible = 0</code> | Set eligible. Use the literal 0. |
| 148 | <code>            for record in iter_csv(config.input_path):</code> | Loop: assign each item from iter_csv(config.input_path) into record, then execute the indented body. |
| 149 | <code>                counts = writer.summary[&quot;counts&quot;]</code> | Set counts. Read writer.summary['counts'] from the current function/object state. |
| 150 | <code>                counts[&quot;input&quot;] += 1</code> | Increase counts['input'] by 1 and retain the updated state. |
| 151 | <code>                if config.max_records is not None and counts[&quot;input&quot;] &gt; config.max_records:</code> | Branch only if config.max_records is not None and counts['input'] > config.max_records is true; otherwise skip this indented block or take its following elif/else. |
| 152 | <code>                    counts[&quot;input&quot;] -= 1</code> | Decrease counts['input'] by 1 and retain the updated state. |
| 153 | <code>                    break</code> | Exit the nearest loop immediately; execution resumes after that loop. |
| 154 | <code>                if record.label is None:</code> | Branch only if record.label is None is true; otherwise skip this indented block or take its following elif/else. |
| 155 | <code>                    counts[&quot;excluded&quot;] += 1</code> | Increase counts['excluded'] by 1 and retain the updated state. |
| 156 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 157 | <code>                warmup = eligible &lt; config.warmup_records</code> | Decide warm-up from the eligible input prefix BEFORE sampling; it is not a promise that warmup_records observations are learned at every N. |
| 158 | <code>                eligible += 1</code> | Advance the eligible prefix counter for every in-scope labeled record, even when the sampler later skips it. |
| 159 | <code>                if rng.random() &gt;= 1 / config.sampling_rate:</code> | Discard this flow with probability 1-1/N. At N=1 every random draw is less than 1, so every eligible record is retained. |
| 160 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 161 | <code>                counts[&quot;sampled&quot;] += 1</code> | Increase counts['sampled'] by 1 and retain the updated state. |
| 162 | <code>                resources.telemetry_bytes += len(json.dumps(record.features).encode())</code> | Count serialized feature bytes as an offline cost proxy; these bytes were not actually exported by a network switch. |
| 163 | <code>                evaluator.observe(record, warmup)</code> | Send an observation into predict-log-score-learn, with warm-up and label availability kept explicit. |
| 164 | <code>            writer.summary[&quot;notes&quot;] = [</code> | Set writer.summary['notes']. Build the ordered list below; order is retained. |
| 165 | <code>                &quot;Flow-record subsampling; scored quality is conditional on selection&quot;,</code> | Literal component of the surrounding statement: 'Flow-record subsampling; scored quality is conditional on selection'. Its role is determined by the field/call immediately above. |
| 166 | <code>                &quot;CSV row order does not establish natural chronology&quot;,</code> | Literal component of the surrounding statement: 'CSV row order does not establish natural chronology'. Its role is determined by the field/call immediately above. |
| 167 | <code>            ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 168 | <code>        elif config.mode == &quot;pcap_replay&quot;:</code> | Branch only if config.mode == 'pcap_replay' is true; otherwise skip this indented block or take its following elif/else. |
| 169 | <code>            labels = LabelTimeline(config.labels_path)</code> | Set labels. Construct a new LabelTimeline using config.labels_path. |
| 170 | <code>            flow_labels = None</code> | Set flow_labels. Use the literal None (None means unavailable/not set). |
| 171 | <code>            truth = {}</code> | Set truth. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 172 | <code>            if config.flow_labels_path:</code> | Branch only if config.flow_labels_path is true; otherwise skip this indented block or take its following elif/else. |
| 173 | <code>                writer.summary[&quot;label_provenance&quot;] = (</code> | Set writer.summary['label_provenance']. Choose None when fixture is true; otherwise choose verify_input(config.flow_labels_path, config.manifest_path). |
| 174 | <code>                    None if fixture else verify_input(config.flow_labels_path, config.manifest_path)</code> | Continuation of the statement above. Choose None when fixture is true; otherwise choose verify_input(config.flow_labels_path, config.manifest_path). |
| 175 | <code>                )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 176 | <code>                flow_labels = FlowLabels(config.flow_labels_path)</code> | Set flow_labels. Construct a new FlowLabels using config.flow_labels_path. |
| 177 | <code>                writer.summary[&quot;packet_label_coverage&quot;] = {</code> | Set writer.summary['packet_label_coverage']. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 178 | <code>                    &quot;matched&quot;: 0,</code> | Field matched: Named entry in the surrounding dictionary. Its value is 0; consumers access it by this key. |
| 179 | <code>                    &quot;unknown&quot;: 0,</code> | Field unknown: Named entry in the surrounding dictionary. Its value is 0; consumers access it by this key. |
| 180 | <code>                    &quot;unjoinable_flow_rows&quot;: flow_labels.unjoinable_rows,</code> | Field unjoinable_flow_rows: Named entry in the surrounding dictionary. Its value is flow_labels.unjoinable_rows; consumers access it by this key. |
| 181 | <code>                }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 182 | <code>            accumulator = WindowAccumulator(config.window_seconds)</code> | Set accumulator. Construct a new WindowAccumulator using config.window_seconds. |
| 183 | <code>            origin = None</code> | Set origin. Use the literal None (None means unavailable/not set). |
| 184 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 185 | <code>            def observe_window(item):</code> | Define function/method observe_window. Assigns truth to a completed packet window, keeps warm-up separate, and calls the shared evaluator with independent original-packet counts when available. |
| 186 | <code>                record, count = item</code> | Set (record, count). Read item from the current function/object state. |
| 187 | <code>                window_truth = truth.pop(record.index, WindowTruth()) if flow_labels else None</code> | Set window_truth. Choose truth.pop(record.index, WindowTruth()) when flow_labels is true; otherwise choose None. |
| 188 | <code>                label, family = (</code> | Set (label, family). Choose window_truth.label() when window_truth is true; otherwise choose labels.label(record.time, record.time + config.window_seconds, origin). |
| 189 | <code>                    window_truth.label()</code> | Continuation of the statement above. Choose window_truth.label() when window_truth is true; otherwise choose labels.label(record.time, record.time + config.window_seconds, origin). |
| 190 | <code>                    if window_truth</code> | Continuation of the statement above. Read window_truth from the current function/object state. |
| 191 | <code>                    else labels.label(record.time, record.time + config.window_seconds, origin)</code> | Continuation of the statement above. Use full-window annotation coverage; uncovered or boundary-crossing windows stay unknown. |
| 192 | <code>                )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 193 | <code>                evaluator.observe(</code> | Send an observation into predict-log-score-learn, with warm-up and label availability kept explicit. |
| 194 | <code>                    replace(record, label=label, attack_family=family),</code> | Continuation of the statement above. Create a new dataclass instance with selected fields changed; the original remains unchanged: replace(record, label=label, attack_family=family). |
| 195 | <code>                    record.time &lt; config.warmup_seconds,</code> | Continuation of the statement above. Evaluate the comparison record.time < config.warmup_seconds to True/False; comparisons may short-circuit. |
| 196 | <code>                    count,</code> | Continuation of the statement above. Read count from the current function/object state. |
| 197 | <code>                    ground_truth_packets=window_truth.packets if window_truth else None,</code> | Keyword argument ground_truth_packets for the call above. Pass the shown value window_truth.packets if window_truth else None into that parameter. |
| 198 | <code>                )</code> | Close the call to evaluator.observe begun above; this is punctuation, not a separate operation. |
| 199 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 200 | <code>            for timestamp, header in iter_pcap(config.input_path):</code> | Loop: assign each item from iter_pcap(config.input_path) into (timestamp, header), then execute the indented body. |
| 201 | <code>                if origin is None:</code> | Branch only if origin is None is true; otherwise skip this indented block or take its following elif/else. |
| 202 | <code>                    origin = timestamp</code> | Anchor relative replay windows to the first observed capture timestamp, while retaining original epoch time for official interval matches. |
| 203 | <code>                writer.summary[&quot;counts&quot;][&quot;input&quot;] += 1</code> | Increase writer.summary['counts']['input'] by 1 and retain the updated state. |
| 204 | <code>                if config.max_records and writer.summary[&quot;counts&quot;][&quot;input&quot;] &gt; config.max_records:</code> | Branch only if config.max_records and writer.summary['counts']['input'] > config.max_records is true; otherwise skip this indented block or take its following elif/else. |
| 205 | <code>                    writer.summary[&quot;counts&quot;][&quot;input&quot;] -= 1</code> | Decrease writer.summary['counts']['input'] by 1 and retain the updated state. |
| 206 | <code>                    break</code> | Exit the nearest loop immediately; execution resumes after that loop. |
| 207 | <code>                for item in accumulator.advance(timestamp - origin):</code> | Loop: assign each item from accumulator.advance(timestamp - origin) into item, then execute the indented body. |
| 208 | <code>                    observe_window(item)</code> | Call observe_window with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 209 | <code>                if flow_labels:</code> | Branch only if flow_labels is true; otherwise skip this indented block or take its following elif/else. |
| 210 | <code>                    label, family = flow_labels.match(header, timestamp)</code> | Derive this original packet's answer using verified flow metadata BEFORE random feature sampling. |
| 211 | <code>                    index = math.floor((timestamp - origin) / config.window_seconds)</code> | Set index. Call math.floor with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 212 | <code>                    truth.setdefault(index, WindowTruth()).add(label, family)</code> | Add every original packet's label to its independent truth window, including packets the feature sampler will discard. |
| 213 | <code>                    writer.summary[&quot;packet_label_coverage&quot;][</code> | Increase writer.summary['packet_label_coverage']['matched' if label is not None else 'unknown'] by 1 and retain the updated state. |
| 214 | <code>                        &quot;matched&quot; if label is not None else &quot;unknown&quot;</code> | Continuation of the statement above. Choose 'matched' when label is not None is true; otherwise choose 'unknown'. |
| 215 | <code>                    ] += 1</code> | Literal component of the surrounding statement: 1. Its role is determined by the field/call immediately above. |
| 216 | <code>                packet = parse_header(header, timestamp, len(header), config.sampling_rate)</code> | Set packet. Parse supported packet-header bytes defensively; unsupported/truncated input produces None. |
| 217 | <code>                if packet and rng.random() &lt; 1 / config.sampling_rate:</code> | Only supported parsed packets selected with probability 1/N enter feature accumulation; window truth has already considered the original packet. |
| 218 | <code>                    writer.summary[&quot;counts&quot;][&quot;sampled&quot;] += 1</code> | Increase writer.summary['counts']['sampled'] by 1 and retain the updated state. |
| 219 | <code>                    resources.telemetry_bytes += min(len(header), 128)</code> | Increase resources.telemetry_bytes by min(len(header), 128) and retain the updated state. |
| 220 | <code>                    for item in accumulator.add(packet, origin):</code> | Loop: assign each item from accumulator.add(packet, origin) into item, then execute the indented body. |
| 221 | <code>                        observe_window(item)</code> | Call observe_window with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 222 | <code>            # The final incomplete capture window is intentionally not scored.</code> | Source comment: The final incomplete capture window is intentionally not scored. This documents intent and does not execute. |
| 223 | <code>            writer.summary[&quot;notes&quot;] = [</code> | Set writer.summary['notes']. Build the ordered list below; order is retained. |
| 224 | <code>                &quot;Seeded offline packet selection, not measured switch export&quot;,</code> | Literal component of the surrounding statement: 'Seeded offline packet selection, not measured switch export'. Its role is determined by the field/call immediately above. |
| 225 | <code>                &quot;Final partial capture window excluded&quot;,</code> | Literal component of the surrounding statement: 'Final partial capture window excluded'. Its role is determined by the field/call immediately above. |
| 226 | <code>                &quot;Window positive if any authoritative matched flood packet; negative only when all packets known benign or window empty; other windows unscored&quot;,</code> | Literal component of the surrounding statement: 'Window positive if any authoritative matched flood packet; negative only when all packets known benign or window empty; other windows unscored'. Its role is determined by the field/call immediately above. |
| 227 | <code>            ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 228 | <code>        else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 229 | <code>            raise ValueError(&quot;Use the live collector for live_sflow mode&quot;)</code> | Reject live mode in the offline runner. Actual exported UDP samples must go through run_live. |
| 230 | <code>    except Exception as exc:  # noqa: BLE001 - preserve failures from third-party models in the run log</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 231 | <code>        error = exc</code> | Retain the processing failure so final run evidence can be saved with failed status and the original error. |
| 232 | <code>    metrics = {**evaluator.summary(), **resources.finish()}</code> | Set metrics. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 233 | <code>    writer.finish(metrics, error)</code> | Persist final run status, metrics and any failure, then close raw CSV files. |
| 234 | <code>    if error:</code> | Branch only if error is true; otherwise skip this indented block or take its following elif/else. |
| 235 | <code>        raise RuntimeError(f&quot;Run {writer.run_id} failed; raw logs preserved: {error}&quot;) from error</code> | Raise RuntimeError(f'Run {writer.run_id} failed; raw logs preserved: {error}') and stop this operation; chain the original cause for diagnostics. |
| 236 | <code>    return writer.summary</code> | Return to the caller: Read writer.summary from the current function/object state. |

## src/m3/packets.py

**Packet decoding and fixed-width window features.** Packet stores a small parsed header summary. WindowAccumulator turns sampled packets into packet-window-v1 features. Multiplying a sampled packet by its reported sampling rate estimates traffic volume; it does not recover original packet identities. CSV flow-v1 features are a different schema.

Snapshot: 132 lines; SHA256 `b7eef6e17c986b923014416da92e7f07dd381b51cfba5db03705143c8ebbd692`.

### Named operations

- `Packet` (L12): Stores arrival/capture time, original frame length, IP protocol, TCP SYN flag, and inverse sampling probability N.
- `parse_header` (L20): Parses supported Ethernet/VLAN/IPv4/IPv6 headers defensively and derives a SYN flag. Unsupported or too-short input returns None, not guessed fields.
- `iter_pcap` (L64): Streams pcap/pcapng records, requires Ethernet link type, and rejects timestamps that go backwards.
- `WindowAccumulator.__init__` (L85): Validates a positive window width and initializes an unstarted accumulator.
- `WindowAccumulator._record` (L92): Creates packet-window features from currently stored sampled packets; empty windows get zero numeric features and empty_window=1.
- `WindowAccumulator.advance` (L111): Emits completed windows up to the new relative-time bin, including empty windows, and rejects backwards or unreasonable gaps.
- `WindowAccumulator.add` (L126): Closes previous windows before appending the new packet to its time bin. It is a generator; work occurs when iterated.
- `WindowAccumulator.finish` (L130): Can emit the currently open window. Offline engine intentionally does not call it, avoiding a partially captured final window.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 2 | <code>import struct</code> | Import struct to decode/encode network byte-order integers and binary framing. |
| 3 | <code>from dataclasses import dataclass</code> | Import dataclass from dataclasses. This makes the named library helpers available without the module prefix. |
| 4 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 5 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 6 | <code>import dpkt</code> | Import dpkt to read packet-capture files and parse packet structures. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <code>from m3.data import Record</code> | Import Record from m3.data. These are project definitions; follow the named module in this guide to see their implementation. |
| 9 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <code>@dataclass(frozen=True)</code> | Apply the dataclass decorator: generate initialization and field helpers; frozen=True prevents normal field reassignment. |
| 12 | <code>class Packet:</code> | Define class Packet. Stores arrival/capture time, original frame length, IP protocol, TCP SYN flag, and inverse sampling probability N. |
| 13 | <code>    time: float</code> | Set time. Type annotation only; no value is assigned on this line. |
| 14 | <code>    length: int</code> | Set length. Type annotation only; no value is assigned on this line. |
| 15 | <code>    protocol: int</code> | Set protocol. Type annotation only; no value is assigned on this line. |
| 16 | <code>    syn: bool</code> | Set syn. Type annotation only; no value is assigned on this line. |
| 17 | <code>    sample_rate: int = 1</code> | Set sample_rate. Use the literal 1. |
| 18 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 19 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 20 | <code>def parse_header(header: bytes, time: float, length: int, sample_rate=1, protocol=1):</code> | Define function/method parse_header. Parses supported Ethernet/VLAN/IPv4/IPv6 headers defensively and derives a SYN flag. Unsupported or too-short input returns None, not guessed fields. |
| 21 | <code>    offset = 0</code> | Start at byte zero; Ethernet parsing will move this cursor to the IP header, while raw IP protocol modes leave it at zero. |
| 22 | <code>    if protocol == 1:  # sFlow raw header protocol: Ethernet ISO88023</code> | Branch only if protocol == 1 is true; otherwise skip this indented block or take its following elif/else. |
| 23 | <code>        if len(header) &lt; 14:</code> | Branch only if len(header) < 14 is true; otherwise skip this indented block or take its following elif/else. |
| 24 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 25 | <code>        ethertype = struct.unpack_from(&quot;!H&quot;, header, 12)[0]</code> | Read the Ethernet type from bytes 12-13 as an unsigned 16-bit big-endian integer; tuple index [0] extracts the decoded number. |
| 26 | <code>        offset = 14</code> | Skip the standard 14-byte Ethernet header to find its payload. |
| 27 | <code>        while ethertype in (0x8100, 0x88A8):</code> | Unwrap one or more 802.1Q/provider VLAN tags before interpreting the IP payload. |
| 28 | <code>            if len(header) &lt; offset + 4:</code> | Branch only if len(header) < offset + 4 is true; otherwise skip this indented block or take its following elif/else. |
| 29 | <code>                return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 30 | <code>            ethertype = struct.unpack_from(&quot;!H&quot;, header, offset + 2)[0]</code> | Set ethertype. Read struct.unpack_from('!H', header, offset + 2)[0] from the current function/object state. |
| 31 | <code>            offset += 4</code> | Increase offset by 4 and retain the updated state. |
| 32 | <code>    elif protocol == 11:</code> | Branch only if protocol == 11 is true; otherwise skip this indented block or take its following elif/else. |
| 33 | <code>        ethertype = 0x0800</code> | Set ethertype. Use the literal 2048. |
| 34 | <code>    elif protocol == 12:</code> | Branch only if protocol == 12 is true; otherwise skip this indented block or take its following elif/else. |
| 35 | <code>        ethertype = 0x86DD</code> | Set ethertype. Use the literal 34525. |
| 36 | <code>    else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 37 | <code>        return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 38 | <code>    if ethertype == 0x0800:</code> | Branch only if ethertype == 2048 is true; otherwise skip this indented block or take its following elif/else. |
| 39 | <code>        if len(header) &lt; offset + 20 or header[offset] &gt;&gt; 4 != 4:</code> | Branch only if len(header) < offset + 20 or header[offset] >> 4 != 4 is true; otherwise skip this indented block or take its following elif/else. |
| 40 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 41 | <code>        ihl = (header[offset] &amp; 15) * 4</code> | Mask the IPv4 first byte's low 4 bits to obtain header length in 32-bit words, then multiply by 4 for bytes. |
| 42 | <code>        if ihl &lt; 20 or len(header) &lt; offset + ihl:</code> | Branch only if ihl < 20 or len(header) < offset + ihl is true; otherwise skip this indented block or take its following elif/else. |
| 43 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 44 | <code>        ipproto = header[offset + 9]</code> | Set ipproto. Read header[offset + 9] from the current function/object state. |
| 45 | <code>        fragmented = struct.unpack_from(&quot;!H&quot;, header, offset + 6)[0] &amp; 0x1FFF</code> | Extract the 13-bit IPv4 fragment offset. Nonzero means a later fragment lacking the start of the transport header. |
| 46 | <code>        transport = offset + ihl</code> | Set transport. Calculate offset + ihl using add; / returns a floating-point ratio and // floors division where used. |
| 47 | <code>    elif ethertype == 0x86DD:</code> | Branch only if ethertype == 34525 is true; otherwise skip this indented block or take its following elif/else. |
| 48 | <code>        if len(header) &lt; offset + 40:</code> | Branch only if len(header) < offset + 40 is true; otherwise skip this indented block or take its following elif/else. |
| 49 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 50 | <code>        ipproto, fragmented, transport = header[offset + 6], False, offset + 40</code> | Set (ipproto, fragmented, transport). Bundle these values in a tuple: (header[offset + 6], False, offset + 40). |
| 51 | <code>        if ipproto not in (6, 17, 58):</code> | Branch only if ipproto not in (6, 17, 58) is true; otherwise skip this indented block or take its following elif/else. |
| 52 | <code>            return None  # IPv6 extension headers require additional decoding; do not guess.</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 53 | <code>    else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 54 | <code>        return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 55 | <code>    syn = (</code> | Set syn. Evaluate ipproto == 6 and (not fragmented) and (len(header) >= transport + 14) and bool(header[transport + 13] & 2) left to right with short-circuit and. |
| 56 | <code>        ipproto == 6</code> | Keyword argument ipproto for the call above. Pass the shown value = 6 into that parameter. |
| 57 | <code>        and not fragmented</code> | Continuation of the statement above. Read not fragmented from the current function/object state. |
| 58 | <code>        and len(header) &gt;= transport + 14</code> | Continuation of the statement above. Evaluate the comparison len(header) >= transport + 14 to True/False; comparisons may short-circuit. |
| 59 | <code>        and bool(header[transport + 13] &amp; 2)</code> | Continuation of the statement above. Convert header[transport + 13] & 2 to bool. |
| 60 | <code>    )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 61 | <code>    return Packet(time, length, ipproto, syn, sample_rate)</code> | Return to the caller: Construct a new Packet using time, length, ipproto, syn, sample_rate. |
| 62 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 63 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 64 | <code>def iter_pcap(path: str &#124; Path):</code> | Define function/method iter_pcap. Streams pcap/pcapng records, requires Ethernet link type, and rejects timestamps that go backwards. |
| 65 | <code>    with Path(path).open(&quot;rb&quot;) as stream:</code> | Enter managed resource/lock context Path(path).open('rb') as stream. Exiting the block releases/closes it, including on exceptions. |
| 66 | <code>        magic = stream.read(4)</code> | Set magic. Call stream.read with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 67 | <code>        stream.seek(0)</code> | Call stream.seek with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 68 | <code>        reader = (</code> | Set reader. Choose dpkt.pcapng.Reader(stream) when magic == b'\n\r\r\n' is true; otherwise choose dpkt.pcap.Reader(stream). |
| 69 | <code>            dpkt.pcapng.Reader(stream) if magic == b&quot;\x0a\x0d\x0d\x0a&quot; else dpkt.pcap.Reader(stream)</code> | Continuation of the statement above. Choose dpkt.pcapng.Reader(stream) when magic == b'\n\r\r\n' is true; otherwise choose dpkt.pcap.Reader(stream). |
| 70 | <code>        )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 71 | <code>        if reader.datalink() != dpkt.pcap.DLT_EN10MB:</code> | Branch only if reader.datalink() != dpkt.pcap.DLT_EN10MB is true; otherwise skip this indented block or take its following elif/else. |
| 72 | <code>            raise ValueError(</code> | Raise ValueError('Packet input requires Ethernet captures; use the official GTP-removed trace') and stop this operation; the caller can record/report this invalid condition. |
| 73 | <code>                &quot;Packet input requires Ethernet captures; use the official GTP-removed trace&quot;</code> | Literal component of the surrounding statement: 'Packet input requires Ethernet captures; use the official GTP-removed trace'. Its role is determined by the field/call immediately above. |
| 74 | <code>            )</code> | Close the call to ValueError begun above; this is punctuation, not a separate operation. |
| 75 | <code>        previous = float(&quot;-inf&quot;)</code> | Set previous. Convert '-inf' to float. |
| 76 | <code>        for timestamp, header in reader:</code> | Loop: assign each item from reader into (timestamp, header), then execute the indented body. |
| 77 | <code>            timestamp = float(timestamp)</code> | Set timestamp. Convert timestamp to float. |
| 78 | <code>            if timestamp &lt; previous:</code> | Branch only if timestamp < previous is true; otherwise skip this indented block or take its following elif/else. |
| 79 | <code>                raise ValueError(&quot;Capture timestamps are not ordered&quot;)</code> | Raise ValueError('Capture timestamps are not ordered') and stop this operation; the caller can record/report this invalid condition. |
| 80 | <code>            previous = timestamp</code> | Set previous. Read timestamp from the current function/object state. |
| 81 | <code>            yield timestamp, header</code> | Yield one item to the caller and pause this generator: Bundle these values in a tuple: (timestamp, header). |
| 82 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 83 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 84 | <code>class WindowAccumulator:</code> | Define class WindowAccumulator. Groups the following statements into a named reusable operation. |
| 85 | <code>    def __init__(self, seconds=1):</code> | Define function/method __init__. Validates a positive window width and initializes an unstarted accumulator. |
| 86 | <code>        if not math.isfinite(seconds) or seconds &lt;= 0:</code> | Branch only if not math.isfinite(seconds) or seconds <= 0 is true; otherwise skip this indented block or take its following elif/else. |
| 87 | <code>            raise ValueError(&quot;Window duration must be positive and finite&quot;)</code> | Raise ValueError('Window duration must be positive and finite') and stop this operation; the caller can record/report this invalid condition. |
| 88 | <code>        self.seconds = seconds</code> | Set self.seconds. Read seconds from the current function/object state. |
| 89 | <code>        self.index = None</code> | Set self.index. Use the literal None (None means unavailable/not set). |
| 90 | <code>        self.packets = []</code> | Begin a fresh packet list after initialization or advancing a completed window. |
| 91 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 92 | <code>    def _record(self):</code> | Define function/method _record. Creates packet-window features from currently stored sampled packets; empty windows get zero numeric features and empty_window=1. |
| 93 | <code>        count = len(self.packets)</code> | Count observed sampled packets in the current window; this is not the unsampled original packet count. |
| 94 | <code>        weighted_packets = sum(p.sample_rate for p in self.packets)</code> | Estimate original packet count by adding inverse sampling probability N for each observed packet. |
| 95 | <code>        weighted_bytes = sum(p.length * p.sample_rate for p in self.packets)</code> | Estimate original byte count by multiplying each observed frame length by its inverse sampling probability. |
| 96 | <code>        total_bytes = sum(p.length for p in self.packets)</code> | Set total_bytes. Add the values yielded by (p.length for p in self.packets); booleans count as 1 for True and 0 for False. |
| 97 | <code>        features = {</code> | Set features. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 98 | <code>            &quot;packets_per_second&quot;: weighted_packets / self.seconds,</code> | Field packets_per_second: Estimated original volume: sum of inverse sampling probabilities divided by window width. |
| 99 | <code>            &quot;bytes_per_second&quot;: weighted_bytes / self.seconds,</code> | Field bytes_per_second: Estimated byte volume: sum of frame length times sampling rate divided by window width. |
| 100 | <code>            &quot;mean_packet_size&quot;: total_bytes / count if count else 0.0,</code> | Field mean_packet_size: Mean length among observed sampled packets; sampling weights are not applied here. |
| 101 | <code>            &quot;udp_fraction&quot;: sum(p.protocol == 17 for p in self.packets) / count if count else 0.0,</code> | Field udp_fraction: Fraction of observed sampled packets whose IP protocol is UDP (17). |
| 102 | <code>            &quot;tcp_fraction&quot;: sum(p.protocol == 6 for p in self.packets) / count if count else 0.0,</code> | Field tcp_fraction: Fraction of observed sampled packets whose IP protocol is TCP (6). |
| 103 | <code>            &quot;icmp_fraction&quot;: sum(p.protocol in (1, 58) for p in self.packets) / count</code> | Field icmp_fraction: Fraction of observed sampled packets marked ICMP/ICMPv6 (1/58). |
| 104 | <code>            if count</code> | Continuation of the statement above. Read count from the current function/object state. |
| 105 | <code>            else 0.0,</code> | Literal component of the surrounding statement: 0.0. Its role is determined by the field/call immediately above. |
| 106 | <code>            &quot;syn_fraction&quot;: sum(p.syn for p in self.packets) / count if count else 0.0,</code> | Field syn_fraction: Fraction of observed sampled packets with TCP SYN flag set; includes SYN+ACK because only the SYN bit is tested. |
| 107 | <code>            &quot;empty_window&quot;: int(not count),</code> | Field empty_window: Flag equal to 1 when no sampled packets were stored for this window. |
| 108 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 109 | <code>        return Record(self.index, self.index * self.seconds, features, None, &quot;unknown&quot;), count</code> | Return to the caller: Bundle these values in a tuple: (Record(self.index, self.index * self.seconds, features, None, 'unknown'), count). |
| 110 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 111 | <code>    def advance(self, relative_time):</code> | Define function/method advance. Emits completed windows up to the new relative-time bin, including empty windows, and rejects backwards or unreasonable gaps. |
| 112 | <code>        index = math.floor(relative_time / self.seconds)</code> | Put time into a half-open window: at width 1, times [0,1) map to bin 0 and [1,2) to bin 1. |
| 113 | <code>        if index &lt; 0:</code> | Branch only if index < 0 is true; otherwise skip this indented block or take its following elif/else. |
| 114 | <code>            return</code> | Return to the caller with None. |
| 115 | <code>        if self.index is None:</code> | Branch only if self.index is None is true; otherwise skip this indented block or take its following elif/else. |
| 116 | <code>            self.index = 0</code> | Set self.index. Use the literal 0. |
| 117 | <code>        if index &lt; self.index:</code> | Branch only if index < self.index is true; otherwise skip this indented block or take its following elif/else. |
| 118 | <code>            raise ValueError(&quot;Window observations moved backwards&quot;)</code> | Raise ValueError('Window observations moved backwards') and stop this operation; the caller can record/report this invalid condition. |
| 119 | <code>        if index - self.index &gt; 100000:</code> | Branch only if index - self.index > 100000 is true; otherwise skip this indented block or take its following elif/else. |
| 120 | <code>            raise ValueError(&quot;Capture gap is too large; prepare a documented trace segment&quot;)</code> | Raise ValueError('Capture gap is too large; prepare a documented trace segment') and stop this operation; the caller can record/report this invalid condition. |
| 121 | <code>        while self.index &lt; index:</code> | Repeat the indented body while self.index < index remains true; the body must advance state or terminate. |
| 122 | <code>            yield self._record()</code> | Emit the current window's Record and observed count to the caller before advancing/clearing state. |
| 123 | <code>            self.index += 1</code> | Increase self.index by 1 and retain the updated state. |
| 124 | <code>            self.packets = []</code> | Begin a fresh packet list after initialization or advancing a completed window. |
| 125 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 126 | <code>    def add(self, packet, origin):</code> | Define function/method add. Closes previous windows before appending the new packet to its time bin. It is a generator; work occurs when iterated. |
| 127 | <code>        yield from self.advance(packet.time - origin)</code> | Forward each item yielded by self.advance(packet.time - origin) to this generator's caller. |
| 128 | <code>        self.packets.append(packet)</code> | Append packet to the end of self.packets. |
| 129 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 130 | <code>    def finish(self):</code> | Define function/method finish. Can emit the currently open window. Offline engine intentionally does not call it, avoiding a partially captured final window. |
| 131 | <code>        if self.index is not None:</code> | Branch only if self.index is not None is true; otherwise skip this indented block or take its following elif/else. |
| 132 | <code>            yield self._record()</code> | Emit the current window's Record and observed count to the caller before advancing/clearing state. |

## src/m3/ground_truth.py

**Conservative packet-to-flow ground truth.** Matches original packet headers against verified numeric official flow intervals. Matching uses bidirectional endpoints, ports for TCP/UDP, protocol, and epoch time. Unknown/conflicting cases stay unknown. Ground truth is calculated independently of feature sampling; this prevents discarded attack packets from disappearing from the test answer.

Snapshot: 172 lines; SHA256 `0f71ce43cfc297b8a7021adebfeeeb53c0d9b5a797ee87dda55420c1f410327d`.

### Named operations

- `flow_key` (L15): Normalizes IP addresses and sorts endpoint pairs, so forward and reverse packets share one lookup key; TCP/UDP need numeric ports.
- `packet_key` (L27): Builds a flow key from an Ethernet frame using dpkt. Unsupported protocols, noninitial IPv4 fragments, and parse errors return None.
- `IntervalIndex.__init__` (L53): Builds sorted interval starts plus a balanced max-end tree to avoid scanning all historical flows for every packet.
- `IntervalIndex.at` (L65): Uses binary search on starts and max-end pruning to return intervals overlapping the timestamp, allowing one microsecond tolerance.
- `FlowLabels.__init__` (L82): Loads/validates the prepared numeric interval table, groups matching endpoints/protocols, and builds an interval index for each group.
- `FlowLabels.match` (L136): Finds candidate official intervals for one original packet. Zero matches or mixed binary labels return unknown; same binary label with several families becomes mixed_flood.
- `WindowTruth.__init__` (L151): Tracks all original packets and authoritative positive families for one window, independently of sampled features.
- `WindowTruth.add` (L156): Counts each original packet, counts unknown labels, and records positive attack families.
- `WindowTruth.label` (L162): Any known flood packet makes a positive window; otherwise unknown packets make it unscored; no unknown/positive packets means benign, including empty windows.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;Conservative packet-to-official-flow joins; unknown/conflicting matches stay unknown.&quot;&quot;&quot;</code> | Documentation string: Conservative packet-to-official-flow joins; unknown/conflicting matches stay unknown. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>import csv</code> | Import csv to stream CSV records and write raw tabular evidence. |
| 4 | <code>import ipaddress</code> | Import ipaddress to validate and normalize IP addresses. |
| 5 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 6 | <code>from bisect import bisect_right</code> | Import bisect_right from bisect. This makes the named library helpers available without the module prefix. |
| 7 | <code>from collections import defaultdict</code> | Import defaultdict from collections. This makes the named library helpers available without the module prefix. |
| 8 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 9 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 10 | <code>import dpkt</code> | Import dpkt to read packet-capture files and parse packet structures. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <code>from m3.data import POSITIVE_FAMILIES</code> | Import POSITIVE_FAMILIES from m3.data. These are project definitions; follow the named module in this guide to see their implementation. |
| 13 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 14 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 15 | <code>def flow_key(source, destination, protocol, sport=None, dport=None):</code> | Define function/method flow_key. Normalizes IP addresses and sorts endpoint pairs, so forward and reverse packets share one lookup key; TCP/UDP need numeric ports. |
| 16 | <code>    source, destination = str(ipaddress.ip_address(source)), str(ipaddress.ip_address(destination))</code> | Set (source, destination). Bundle these values in a tuple: (str(ipaddress.ip_address(source)), str(ipaddress.ip_address(destination))). |
| 17 | <code>    if protocol in (6, 17):</code> | Branch only if protocol in (6, 17) is true; otherwise skip this indented block or take its following elif/else. |
| 18 | <code>        if sport is None or dport is None:</code> | Branch only if sport is None or dport is None is true; otherwise skip this indented block or take its following elif/else. |
| 19 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 20 | <code>        endpoints = sorted(((source, int(sport)), (destination, int(dport))))</code> | Sort endpoint/port pairs so either direction of the same TCP/UDP flow receives the same canonical key. |
| 21 | <code>    else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 22 | <code>        # ICMP direction/type identifiers are not Argus TCP/UDP ports. Time+endpoints only.</code> | Source comment: ICMP direction/type identifiers are not Argus TCP/UDP ports. Time+endpoints only. This documents intent and does not execute. |
| 23 | <code>        endpoints = sorted(((source, None), (destination, None)))</code> | Set endpoints. Create a sorted copy using the supplied ordering/key: sorted(((source, None), (destination, None))). |
| 24 | <code>    return protocol, tuple(endpoints)</code> | Return to the caller: Bundle these values in a tuple: (protocol, tuple(endpoints)). |
| 25 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 26 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 27 | <code>def packet_key(header):</code> | Define function/method packet_key. Builds a flow key from an Ethernet frame using dpkt. Unsupported protocols, noninitial IPv4 fragments, and parse errors return None. |
| 28 | <code>    try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 29 | <code>        ip = dpkt.ethernet.Ethernet(header).data</code> | Set ip. Read dpkt.ethernet.Ethernet(header).data from the current function/object state. |
| 30 | <code>        if isinstance(ip, dpkt.ip.IP):</code> | Branch only if isinstance(ip, dpkt.ip.IP) is true; otherwise skip this indented block or take its following elif/else. |
| 31 | <code>            if ip.offset:</code> | Branch only if ip.offset is true; otherwise skip this indented block or take its following elif/else. |
| 32 | <code>                return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 33 | <code>            protocol = ip.p</code> | Set protocol. Read ip.p from the current function/object state. |
| 34 | <code>        elif isinstance(ip, dpkt.ip6.IP6):</code> | Branch only if isinstance(ip, dpkt.ip6.IP6) is true; otherwise skip this indented block or take its following elif/else. |
| 35 | <code>            protocol = ip.nxt</code> | Set protocol. Read ip.nxt from the current function/object state. |
| 36 | <code>        else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 37 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 38 | <code>        source, destination = ipaddress.ip_address(ip.src), ipaddress.ip_address(ip.dst)</code> | Set (source, destination). Bundle these values in a tuple: (ipaddress.ip_address(ip.src), ipaddress.ip_address(ip.dst)). |
| 39 | <code>        if protocol in (6, 17):</code> | Branch only if protocol in (6, 17) is true; otherwise skip this indented block or take its following elif/else. |
| 40 | <code>            if not isinstance(ip.data, (dpkt.tcp.TCP, dpkt.udp.UDP)):</code> | Branch only if not isinstance(ip.data, (dpkt.tcp.TCP, dpkt.udp.UDP)) is true; otherwise skip this indented block or take its following elif/else. |
| 41 | <code>                return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 42 | <code>            return flow_key(source, destination, protocol, ip.data.sport, ip.data.dport)</code> | Return to the caller: Construct a canonical bidirectional protocol/endpoint key. |
| 43 | <code>        if protocol in (1, 58):</code> | Branch only if protocol in (1, 58) is true; otherwise skip this indented block or take its following elif/else. |
| 44 | <code>            return flow_key(source, destination, protocol)</code> | Return to the caller: Construct a canonical bidirectional protocol/endpoint key. |
| 45 | <code>        return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 46 | <code>    except (ValueError, dpkt.UnpackError, AttributeError):</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 47 | <code>        return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 48 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 49 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 50 | <code>class IntervalIndex:</code> | Define class IntervalIndex. Groups the following statements into a named reusable operation. |
| 51 | <code>    &quot;&quot;&quot;Balanced max-end index: avoid scanning all historical flows on each packet.&quot;&quot;&quot;</code> | Documentation string: Balanced max-end index: avoid scanning all historical flows on each packet. It explains the module/class/function; it is not an extra experiment step. |
| 52 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 53 | <code>    def __init__(self, intervals):</code> | Define function/method __init__. Builds sorted interval starts plus a balanced max-end tree to avoid scanning all historical flows for every packet. |
| 54 | <code>        self.intervals = sorted(intervals)</code> | Set self.intervals. Create a sorted copy using the supplied ordering/key: sorted(intervals). |
| 55 | <code>        self.starts = [row[0] for row in self.intervals]</code> | Set self.starts. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [row[0] for row in self.intervals]. |
| 56 | <code>        self.size = 1</code> | Set self.size. Use the literal 1. |
| 57 | <code>        while self.size &lt; len(intervals):</code> | Repeat the indented body while self.size < len(intervals) remains true; the body must advance state or terminate. |
| 58 | <code>            self.size *= 2</code> | Multiply self.size by 2 and retain the updated state. |
| 59 | <code>        self.ends = [float(&quot;-inf&quot;)] * (self.size * 2)</code> | Set self.ends. Calculate [float('-inf')] * (self.size * 2) using multiply; / returns a floating-point ratio and // floors division where used. |
| 60 | <code>        for index, row in enumerate(self.intervals):</code> | Loop: assign each item from enumerate(self.intervals) into (index, row), then execute the indented body. |
| 61 | <code>            self.ends[self.size + index] = row[1]</code> | Set self.ends[self.size + index]. Read row[1] from the current function/object state. |
| 62 | <code>        for node in range(self.size - 1, 0, -1):</code> | Loop: assign each item from range(self.size - 1, 0, -1) into node, then execute the indented body. |
| 63 | <code>            self.ends[node] = max(self.ends[node * 2], self.ends[node * 2 + 1])</code> | Set self.ends[node]. Select the largest supplied value from max(self.ends[node * 2], self.ends[node * 2 + 1]). |
| 64 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 65 | <code>    def at(self, timestamp, tolerance=0.000001):</code> | Define function/method at. Uses binary search on starts and max-end pruning to return intervals overlapping the timestamp, allowing one microsecond tolerance. |
| 66 | <code>        bound = bisect_right(self.starts, timestamp + tolerance)</code> | Find how many intervals start no later than timestamp plus tolerance; intervals beyond this index cannot contain the packet. |
| 67 | <code>        stack = [(1, 0, self.size)]</code> | Set stack. Build the ordered list below; order is retained. |
| 68 | <code>        result = []</code> | Set result. Build the ordered list below; order is retained. |
| 69 | <code>        while stack:</code> | Repeat the indented body while stack remains true; the body must advance state or terminate. |
| 70 | <code>            node, low, high = stack.pop()</code> | Set (node, low, high). Call stack.pop with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 71 | <code>            if low &gt;= bound or self.ends[node] &lt; timestamp - tolerance:</code> | Prune a tree branch if all its starts are too late or its maximum end is too early, saving repeated historical scans. |
| 72 | <code>                continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 73 | <code>            if high - low == 1:</code> | Branch only if high - low == 1 is true; otherwise skip this indented block or take its following elif/else. |
| 74 | <code>                result.append(self.intervals[low])</code> | Append self.intervals[low] to the end of result. |
| 75 | <code>            else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 76 | <code>                middle = (low + high) // 2</code> | Set middle. Calculate (low + high) // 2 using floor-divide; / returns a floating-point ratio and // floors division where used. |
| 77 | <code>                stack.extend([(node * 2, low, middle), (node * 2 + 1, middle, high)])</code> | Call stack.extend with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 78 | <code>        return result</code> | Return to the caller: Read result from the current function/object state. |
| 79 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 80 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 81 | <code>class FlowLabels:</code> | Define class FlowLabels. Groups the following statements into a named reusable operation. |
| 82 | <code>    def __init__(self, path):</code> | Define function/method __init__. Loads/validates the prepared numeric interval table, groups matching endpoints/protocols, and builds an interval index for each group. |
| 83 | <code>        grouped = defaultdict(list)</code> | Set grouped. Call defaultdict with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 84 | <code>        self.rows = 0</code> | Set self.rows. Use the literal 0. |
| 85 | <code>        self.unjoinable_rows = 0</code> | Set self.unjoinable_rows. Use the literal 0. |
| 86 | <code>        with Path(path).open(newline=&quot;&quot;, encoding=&quot;utf-8-sig&quot;) as stream:</code> | Enter managed resource/lock context Path(path).open(newline='', encoding='utf-8-sig') as stream. Exiting the block releases/closes it, including on exceptions. |
| 87 | <code>            reader = csv.DictReader(stream)</code> | Set reader. Call csv.DictReader with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 88 | <code>            required = {</code> | Set required. Read {'start_epoch', 'end_epoch', 'src_ip', 'dst_ip', 'src_port', 'dst_port', 'protocol', 'label', 'attack_family', 'offset'} from the current function/object state. |
| 89 | <code>                &quot;start_epoch&quot;,</code> | Literal component of the surrounding statement: 'start_epoch'. Its role is determined by the field/call immediately above. |
| 90 | <code>                &quot;end_epoch&quot;,</code> | Literal component of the surrounding statement: 'end_epoch'. Its role is determined by the field/call immediately above. |
| 91 | <code>                &quot;src_ip&quot;,</code> | Literal component of the surrounding statement: 'src_ip'. Its role is determined by the field/call immediately above. |
| 92 | <code>                &quot;dst_ip&quot;,</code> | Literal component of the surrounding statement: 'dst_ip'. Its role is determined by the field/call immediately above. |
| 93 | <code>                &quot;src_port&quot;,</code> | Literal component of the surrounding statement: 'src_port'. Its role is determined by the field/call immediately above. |
| 94 | <code>                &quot;dst_port&quot;,</code> | Literal component of the surrounding statement: 'dst_port'. Its role is determined by the field/call immediately above. |
| 95 | <code>                &quot;protocol&quot;,</code> | Literal component of the surrounding statement: 'protocol'. Its role is determined by the field/call immediately above. |
| 96 | <code>                &quot;label&quot;,</code> | Literal component of the surrounding statement: 'label'. Its role is determined by the field/call immediately above. |
| 97 | <code>                &quot;attack_family&quot;,</code> | Literal component of the surrounding statement: 'attack_family'. Its role is determined by the field/call immediately above. |
| 98 | <code>                &quot;offset&quot;,</code> | Literal component of the surrounding statement: 'offset'. Its role is determined by the field/call immediately above. |
| 99 | <code>            }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 100 | <code>            if not required.issubset(reader.fieldnames or []):</code> | Branch only if not required.issubset(reader.fieldnames or []) is true; otherwise skip this indented block or take its following elif/else. |
| 101 | <code>                raise ValueError(&quot;Flow label table lacks the verified numeric/time schema&quot;)</code> | Raise ValueError('Flow label table lacks the verified numeric/time schema') and stop this operation; the caller can record/report this invalid condition. |
| 102 | <code>            for row in reader:</code> | Loop: assign each item from reader into row, then execute the indented body. |
| 103 | <code>                self.rows += 1</code> | Increase self.rows by 1 and retain the updated state. |
| 104 | <code>                start, end = float(row[&quot;start_epoch&quot;]), float(row[&quot;end_epoch&quot;])</code> | Set (start, end). Bundle these values in a tuple: (float(row['start_epoch']), float(row['end_epoch'])). |
| 105 | <code>                if not math.isfinite(start) or not math.isfinite(end) or end &lt; start:</code> | Branch only if not math.isfinite(start) or not math.isfinite(end) or end < start is true; otherwise skip this indented block or take its following elif/else. |
| 106 | <code>                    raise ValueError(&quot;Invalid official flow interval&quot;)</code> | Raise ValueError('Invalid official flow interval') and stop this operation; the caller can record/report this invalid condition. |
| 107 | <code>                label = int(row[&quot;label&quot;])</code> | Set label. Convert row['label'] to int. |
| 108 | <code>                family = row[&quot;attack_family&quot;]</code> | Set family. Read row['attack_family'] from the current function/object state. |
| 109 | <code>                if (</code> | Branch only if label == 0 and family != 'Benign' or (label == 1 and family not in POSITIVE_FAMILIES) or label not in (0, 1) is true; otherwise skip this indented block or take its following elif/else. |
| 110 | <code>                    (label == 0 and family != &quot;Benign&quot;)</code> | Continuation of the statement above. Evaluate label == 0 and family != 'Benign' or (label == 1 and family not in POSITIVE_FAMILIES) or label not in (0, 1) left to right with short-circuit or. |
| 111 | <code>                    or (label == 1 and family not in POSITIVE_FAMILIES)</code> | Continuation of the statement above. Evaluate label == 1 and family not in POSITIVE_FAMILIES left to right with short-circuit and. |
| 112 | <code>                    or label not in (0, 1)</code> | Continuation of the statement above. Evaluate the comparison label not in (0, 1) to True/False; comparisons may short-circuit. |
| 113 | <code>                ):</code> | Continue the surrounding FlowLabels.__init__ statement: ):. The indentation and open brackets connect it to the operation above. |
| 114 | <code>                    raise ValueError(&quot;Conflicting flow label/family&quot;)</code> | Raise ValueError('Conflicting flow label/family') and stop this operation; the caller can record/report this invalid condition. |
| 115 | <code>                protocol = {&quot;tcp&quot;: 6, &quot;udp&quot;: 17, &quot;icmp&quot;: 1, &quot;ipv6-icmp&quot;: 58}.get(</code> | Set protocol. Look up row['protocol'].strip().lower() in {'tcp': 6, 'udp': 17, 'icmp': 1, 'ipv6-icmp': 58}; use the explicit default if supplied, otherwise None. |
| 116 | <code>                    row[&quot;protocol&quot;].strip().lower()</code> | Continuation of the statement above. Call row['protocol'].strip().lower with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 117 | <code>                )</code> | Close the call to {'tcp': 6, 'udp': 17, 'icmp': 1, 'ipv6-icmp': 58}.get begun above; this is punctuation, not a separate operation. |
| 118 | <code>                if protocol is None:</code> | Branch only if protocol is None is true; otherwise skip this indented block or take its following elif/else. |
| 119 | <code>                    self.unjoinable_rows += 1</code> | Increase self.unjoinable_rows by 1 and retain the updated state. |
| 120 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 121 | <code>                ports = []</code> | Set ports. Build the ordered list below; order is retained. |
| 122 | <code>                for key in (&quot;src_port&quot;, &quot;dst_port&quot;):</code> | Loop: assign each item from ('src_port', 'dst_port') into key, then execute the indented body. |
| 123 | <code>                    text = row[key].strip()</code> | Set text. Call row[key].strip with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 124 | <code>                    if text and (not text.isdecimal() or not 0 &lt;= int(text) &lt;= 65535):</code> | Branch only if text and (not text.isdecimal() or not 0 <= int(text) <= 65535) is true; otherwise skip this indented block or take its following elif/else. |
| 125 | <code>                        raise ValueError(</code> | Raise ValueError('Flow ports must be numeric; service-name guesses are forbidden') and stop this operation; the caller can record/report this invalid condition. |
| 126 | <code>                            &quot;Flow ports must be numeric; service-name guesses are forbidden&quot;</code> | Literal component of the surrounding statement: 'Flow ports must be numeric; service-name guesses are forbidden'. Its role is determined by the field/call immediately above. |
| 127 | <code>                        )</code> | Close the call to ValueError begun above; this is punctuation, not a separate operation. |
| 128 | <code>                    ports.append(int(text) if text else None)</code> | Append int(text) if text else None to the end of ports. |
| 129 | <code>                key = flow_key(row[&quot;src_ip&quot;], row[&quot;dst_ip&quot;], protocol, *ports)</code> | Set key. Construct a canonical bidirectional protocol/endpoint key. |
| 130 | <code>                if key is None:</code> | Branch only if key is None is true; otherwise skip this indented block or take its following elif/else. |
| 131 | <code>                    self.unjoinable_rows += 1</code> | Increase self.unjoinable_rows by 1 and retain the updated state. |
| 132 | <code>                else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 133 | <code>                    grouped[key].append((start, end, label, family))</code> | Append (start, end, label, family) to the end of grouped[key]. |
| 134 | <code>        self.index = {key: IntervalIndex(rows) for key, rows in grouped.items()}</code> | Set self.index. Build a collection by iterating the for clauses and retaining entries passing the if clauses: {key: IntervalIndex(rows) for key, rows in grouped.items()}. |
| 135 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 136 | <code>    def match(self, header, timestamp):</code> | Define function/method match. Finds candidate official intervals for one original packet. Zero matches or mixed binary labels return unknown; same binary label with several families becomes mixed_flood. |
| 137 | <code>        key = packet_key(header)</code> | Set key. Call packet_key with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 138 | <code>        index = self.index.get(key)</code> | Set index. Look up key in self.index; use the explicit default if supplied, otherwise None. |
| 139 | <code>        if index is None:</code> | Branch only if index is None is true; otherwise skip this indented block or take its following elif/else. |
| 140 | <code>            return None, &quot;unknown&quot;</code> | Return to the caller: Bundle these values in a tuple: (None, 'unknown'). |
| 141 | <code>        candidates = index.at(timestamp)</code> | Set candidates. Call index.at with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 142 | <code>        labels = {row[2] for row in candidates}</code> | Set labels. Build a collection by iterating the for clauses and retaining entries passing the if clauses: {row[2] for row in candidates}. |
| 143 | <code>        if len(labels) != 1:</code> | Require one unambiguous binary label among matches: zero candidates or contradictory benign/attack candidates remain unknown. |
| 144 | <code>            return None, &quot;unknown&quot;</code> | Return to the caller: Bundle these values in a tuple: (None, 'unknown'). |
| 145 | <code>        label = next(iter(labels))</code> | Set label. Call next with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 146 | <code>        families = {row[3] for row in candidates}</code> | Set families. Build a collection by iterating the for clauses and retaining entries passing the if clauses: {row[3] for row in candidates}. |
| 147 | <code>        return label, next(iter(families)) if len(families) == 1 else &quot;mixed_flood&quot;</code> | Return to the caller: Bundle these values in a tuple: (label, next(iter(families)) if len(families) == 1 else 'mixed_flood'). |
| 148 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 149 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 150 | <code>class WindowTruth:</code> | Define class WindowTruth. Groups the following statements into a named reusable operation. |
| 151 | <code>    def __init__(self):</code> | Define function/method __init__. Tracks all original packets and authoritative positive families for one window, independently of sampled features. |
| 152 | <code>        self.packets = 0</code> | Set self.packets. Use the literal 0. |
| 153 | <code>        self.unknown = 0</code> | Set self.unknown. Use the literal 0. |
| 154 | <code>        self.positive_families = set()</code> | Set self.positive_families. Call set with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 155 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 156 | <code>    def add(self, label, family):</code> | Define function/method add. Counts each original packet, counts unknown labels, and records positive attack families. |
| 157 | <code>        self.packets += 1</code> | Increase self.packets by 1 and retain the updated state. |
| 158 | <code>        self.unknown += label is None</code> | Count unknown original packets using boolean arithmetic (True contributes one). |
| 159 | <code>        if label == 1:</code> | Branch only if label == 1 is true; otherwise skip this indented block or take its following elif/else. |
| 160 | <code>            self.positive_families.add(family)</code> | Insert family into self.positive_families; set insertion keeps unique values. |
| 161 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 162 | <code>    def label(self):</code> | Define function/method label. Any known flood packet makes a positive window; otherwise unknown packets make it unscored; no unknown/positive packets means benign, including empty windows. |
| 163 | <code>        if self.positive_families:</code> | Branch only if self.positive_families is true; otherwise skip this indented block or take its following elif/else. |
| 164 | <code>            family = (</code> | Set family. Choose next(iter(self.positive_families)) when len(self.positive_families) == 1 is true; otherwise choose 'mixed_flood'. |
| 165 | <code>                next(iter(self.positive_families))</code> | Continuation of the statement above. Choose next(iter(self.positive_families)) when len(self.positive_families) == 1 is true; otherwise choose 'mixed_flood'. |
| 166 | <code>                if len(self.positive_families) == 1</code> | Continuation of the statement above. Evaluate the comparison len(self.positive_families) == 1 to True/False; comparisons may short-circuit. |
| 167 | <code>                else &quot;mixed_flood&quot;</code> | Literal component of the surrounding statement: 'mixed_flood'. Its role is determined by the field/call immediately above. |
| 168 | <code>            )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 169 | <code>            return 1, family</code> | Return to the caller: Bundle these values in a tuple: (1, family). |
| 170 | <code>        if self.unknown:</code> | Branch only if self.unknown is true; otherwise skip this indented block or take its following elif/else. |
| 171 | <code>            return None, &quot;unknown&quot;</code> | Return to the caller: Bundle these values in a tuple: (None, 'unknown'). |
| 172 | <code>        return 0, &quot;Benign&quot;</code> | Return to the caller: Bundle these values in a tuple: (0, 'Benign'). |

## src/m3/labels.py

**Explicit label intervals.** Loads documented timeline annotations, validates interval bounds, and labels only windows fully covered by an interval. A verified flag is an input assertion with a source reference; this class does not independently prove that the annotations are scientifically correct.

Snapshot: 39 lines; SHA256 `b1bfe98ebdad8df896736d299325d83b8402f39abaa9803ef225d1322bbb1e97`.

### Named operations

- `LabelTimeline.__init__` (L7): Accepts no annotations (all unknown) or validates a source-marked JSON timeline with finite non-overlapping bounds and allowed labels.
- `LabelTimeline.label` (L33): Translates relative to epoch time if needed and only returns an interval label when it fully covers the requested window.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 2 | <code>import math</code> | Import math to check finite numbers, calculate time-bin floors and access numeric constants. |
| 3 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 6 | <code>class LabelTimeline:</code> | Define class LabelTimeline. Groups the following statements into a named reusable operation. |
| 7 | <code>    def __init__(self, path=None):</code> | Define function/method __init__. Accepts no annotations (all unknown) or validates a source-marked JSON timeline with finite non-overlapping bounds and allowed labels. |
| 8 | <code>        self.intervals = []</code> | Set self.intervals. Build the ordered list below; order is retained. |
| 9 | <code>        self.source = None</code> | Set self.source. Use the literal None (None means unavailable/not set). |
| 10 | <code>        self.verified = False</code> | Set self.verified. Use the literal False. |
| 11 | <code>        self.time_basis = &quot;relative_seconds&quot;</code> | Set self.time_basis. Use the literal 'relative_seconds'. |
| 12 | <code>        if path:</code> | Branch only if path is true; otherwise skip this indented block or take its following elif/else. |
| 13 | <code>            data = json.loads(Path(path).read_text(encoding=&quot;utf-8&quot;))</code> | Set data. Call json.loads with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 14 | <code>            if data.get(&quot;verified&quot;) is not True or not data.get(&quot;source&quot;):</code> | Branch only if data.get('verified') is not True or not data.get('source') is true; otherwise skip this indented block or take its following elif/else. |
| 15 | <code>                raise ValueError(&quot;Packet labels require a verified, documented ground-truth source&quot;)</code> | Raise ValueError('Packet labels require a verified, documented ground-truth source') and stop this operation; the caller can record/report this invalid condition. |
| 16 | <code>            self.source, self.verified = data[&quot;source&quot;], True</code> | Set (self.source, self.verified). Bundle these values in a tuple: (data['source'], True). |
| 17 | <code>            self.time_basis = data.get(&quot;time_basis&quot;, &quot;relative_seconds&quot;)</code> | Set self.time_basis. Look up 'time_basis' in data; use the explicit default if supplied, otherwise None. |
| 18 | <code>            if self.time_basis not in {&quot;relative_seconds&quot;, &quot;epoch_seconds&quot;}:</code> | Branch only if self.time_basis not in {'relative_seconds', 'epoch_seconds'} is true; otherwise skip this indented block or take its following elif/else. |
| 19 | <code>                raise ValueError(&quot;Unknown label time basis&quot;)</code> | Raise ValueError('Unknown label time basis') and stop this operation; the caller can record/report this invalid condition. |
| 20 | <code>            self.intervals = sorted(data.get(&quot;intervals&quot;, []), key=lambda x: x[&quot;start&quot;])</code> | Set self.intervals. Create a sorted copy using the supplied ordering/key: sorted(data.get('intervals', []), key=lambda x: x['start']). |
| 21 | <code>            previous = float(&quot;-inf&quot;)</code> | Set previous. Convert '-inf' to float. |
| 22 | <code>            for item in self.intervals:</code> | Loop: assign each item from self.intervals into item, then execute the indented body. |
| 23 | <code>                if (</code> | Branch only if not all((math.isfinite(item[k]) for k in ('start', 'end'))) or item['start'] < previous or item['end'] <= item['start'] is true; otherwise skip this indented block or take its following elif/else. |
| 24 | <code>                    not all(math.isfinite(item[k]) for k in (&quot;start&quot;, &quot;end&quot;))</code> | Continuation of the statement above. Evaluate not all((math.isfinite(item[k]) for k in ('start', 'end'))) or item['start'] < previous or item['end'] <= item['start'] left to right with short-circuit or. |
| 25 | <code>                    or item[&quot;start&quot;] &lt; previous</code> | Continuation of the statement above. Evaluate the comparison item['start'] < previous to True/False; comparisons may short-circuit. |
| 26 | <code>                    or item[&quot;end&quot;] &lt;= item[&quot;start&quot;]</code> | Continuation of the statement above. Evaluate the comparison item['end'] <= item['start'] to True/False; comparisons may short-circuit. |
| 27 | <code>                ):</code> | Continue the surrounding LabelTimeline.__init__ statement: ):. The indentation and open brackets connect it to the operation above. |
| 28 | <code>                    raise ValueError(&quot;Labels overlap or have invalid bounds&quot;)</code> | Raise ValueError('Labels overlap or have invalid bounds') and stop this operation; the caller can record/report this invalid condition. |
| 29 | <code>                if item[&quot;label&quot;] not in (0, 1, None):</code> | Branch only if item['label'] not in (0, 1, None) is true; otherwise skip this indented block or take its following elif/else. |
| 30 | <code>                    raise ValueError(&quot;Labels must be 0, 1 or null&quot;)</code> | Raise ValueError('Labels must be 0, 1 or null') and stop this operation; the caller can record/report this invalid condition. |
| 31 | <code>                previous = item[&quot;end&quot;]</code> | Set previous. Read item['end'] from the current function/object state. |
| 32 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 33 | <code>    def label(self, start, end, origin):</code> | Define function/method label. Translates relative to epoch time if needed and only returns an interval label when it fully covers the requested window. |
| 34 | <code>        if self.time_basis == &quot;epoch_seconds&quot;:</code> | Branch only if self.time_basis == 'epoch_seconds' is true; otherwise skip this indented block or take its following elif/else. |
| 35 | <code>            start, end = start + origin, end + origin</code> | Set (start, end). Bundle these values in a tuple: (start + origin, end + origin). |
| 36 | <code>        for item in self.intervals:</code> | Loop: assign each item from self.intervals into item, then execute the indented body. |
| 37 | <code>            if item[&quot;start&quot;] &lt;= start and item[&quot;end&quot;] &gt;= end:</code> | Branch only if item['start'] <= start and item['end'] >= end is true; otherwise skip this indented block or take its following elif/else. |
| 38 | <code>                return item[&quot;label&quot;], item.get(&quot;attack_family&quot;, &quot;unknown&quot;)</code> | Return to the caller: Bundle these values in a tuple: (item['label'], item.get('attack_family', 'unknown')). |
| 39 | <code>        return None, &quot;unknown&quot;</code> | Return to the caller: Bundle these values in a tuple: (None, 'unknown'). |

## src/m3/sflow.py

**Bounded binary sFlow v5 decoder.** Converts UDP payload bytes exported by OVS into Packet objects. Bounds checks and length-prefixed records prevent reading beyond available bytes. Unsupported sample/record types are skipped by length. This decoder is intentionally narrower than a complete sFlow implementation.

Snapshot: 79 lines; SHA256 `b2fc1e1166b1fcaff16081dff2c7fe451294d74d636edc805088487171c836c2`.

### Named operations

- `DecodeError` (L8): A ValueError subclass specifically identifying malformed or unsupported sFlow datagrams.
- `Reader.__init__` (L13): Retains the byte buffer and a cursor starting at zero.
- `Reader.take` (L16): Checks that a read stays in bounds, slices exactly size bytes, advances the cursor, and returns the bytes.
- `Reader.integer` (L23): Reads four bytes as one unsigned big-endian 32-bit integer.
- `Reader.record` (L26): Reads tag and length, extracts the body, skips 4-byte alignment padding, and returns tag/body.
- `decode_datagram` (L33): Checks sFlow v5 framing, walks compact/expanded flow samples and raw packet records, and returns supported parsed packets plus agent health metadata.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;Bounded sFlow v5 decoding; unsupported record types are skipped by their lengths.&quot;&quot;&quot;</code> | Documentation string: Bounded sFlow v5 decoding; unsupported record types are skipped by their lengths. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>import struct</code> | Import struct to decode/encode network byte-order integers and binary framing. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <code>from m3.packets import parse_header</code> | Import parse_header from m3.packets. These are project definitions; follow the named module in this guide to see their implementation. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <code>class DecodeError(ValueError):</code> | Define class DecodeError. A ValueError subclass specifically identifying malformed or unsupported sFlow datagrams. |
| 9 | <code>    pass</code> | Empty body placeholder; this subclass/block adds no extra executable behavior. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <code>class Reader:</code> | Define class Reader. Groups the following statements into a named reusable operation. |
| 13 | <code>    def __init__(self, data):</code> | Define function/method __init__. Retains the byte buffer and a cursor starting at zero. |
| 14 | <code>        self.data, self.position = data, 0</code> | Set (self.data, self.position). Bundle these values in a tuple: (data, 0). |
| 15 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 16 | <code>    def take(self, size):</code> | Define function/method take. Checks that a read stays in bounds, slices exactly size bytes, advances the cursor, and returns the bytes. |
| 17 | <code>        if size &lt; 0 or self.position + size &gt; len(self.data):</code> | Branch only if size < 0 or self.position + size > len(self.data) is true; otherwise skip this indented block or take its following elif/else. |
| 18 | <code>            raise DecodeError(&quot;Truncated sFlow datagram&quot;)</code> | Raise DecodeError('Truncated sFlow datagram') and stop this operation; the caller can record/report this invalid condition. |
| 19 | <code>        result = self.data[self.position : self.position + size]</code> | Set result. Read self.data[self.position:self.position + size] from the current function/object state. |
| 20 | <code>        self.position += size</code> | Increase self.position by size and retain the updated state. |
| 21 | <code>        return result</code> | Return to the caller: Read result from the current function/object state. |
| 22 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 23 | <code>    def integer(self):</code> | Define function/method integer. Reads four bytes as one unsigned big-endian 32-bit integer. |
| 24 | <code>        return struct.unpack(&quot;!I&quot;, self.take(4))[0]</code> | Return to the caller: Read struct.unpack('!I', self.take(4))[0] from the current function/object state. |
| 25 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 26 | <code>    def record(self):</code> | Define function/method record. Reads tag and length, extracts the body, skips 4-byte alignment padding, and returns tag/body. |
| 27 | <code>        tag, length = self.integer(), self.integer()</code> | Set (tag, length). Bundle these values in a tuple: (self.integer(), self.integer()). |
| 28 | <code>        body = self.take(length)</code> | Set body. Call self.take with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 29 | <code>        self.take((-length) % 4)</code> | Call self.take with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>        return tag, body</code> | Return to the caller: Bundle these values in a tuple: (tag, body). |
| 31 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 32 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 33 | <code>def decode_datagram(data: bytes, timestamp: float):</code> | Define function/method decode_datagram. Checks sFlow v5 framing, walks compact/expanded flow samples and raw packet records, and returns supported parsed packets plus agent health metadata. |
| 34 | <code>    reader = Reader(data)</code> | Set reader. Construct a new Reader using data. |
| 35 | <code>    if reader.integer() != 5:</code> | Branch only if reader.integer() != 5 is true; otherwise skip this indented block or take its following elif/else. |
| 36 | <code>        raise DecodeError(&quot;Only sFlow version 5 is supported&quot;)</code> | Raise DecodeError('Only sFlow version 5 is supported') and stop this operation; the caller can record/report this invalid condition. |
| 37 | <code>    address_type = reader.integer()</code> | Set address_type. Call reader.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 38 | <code>    if address_type not in (1, 2):</code> | Branch only if address_type not in (1, 2) is true; otherwise skip this indented block or take its following elif/else. |
| 39 | <code>        raise DecodeError(&quot;Invalid agent address type&quot;)</code> | Raise DecodeError('Invalid agent address type') and stop this operation; the caller can record/report this invalid condition. |
| 40 | <code>    agent = reader.take(4 if address_type == 1 else 16).hex()</code> | Set agent. Call reader.take(4 if address_type == 1 else 16).hex with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 41 | <code>    subagent, sequence, uptime = reader.integer(), reader.integer(), reader.integer()</code> | Set (subagent, sequence, uptime). Bundle these values in a tuple: (reader.integer(), reader.integer(), reader.integer()). |
| 42 | <code>    samples = reader.integer()</code> | Set samples. Call reader.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 43 | <code>    packets = []</code> | Set packets. Build the ordered list below; order is retained. |
| 44 | <code>    drops = 0</code> | Set drops. Use the literal 0. |
| 45 | <code>    for _ in range(samples):</code> | Loop: assign each item from range(samples) into _, then execute the indented body. |
| 46 | <code>        tag, body = reader.record()</code> | Set (tag, body). Call reader.record with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 47 | <code>        if tag not in (1, 3):</code> | Branch only if tag not in (1, 3) is true; otherwise skip this indented block or take its following elif/else. |
| 48 | <code>            continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 49 | <code>        sample = Reader(body)</code> | Set sample. Construct a new Reader using body. |
| 50 | <code>        sample.integer()  # sample sequence</code> | Call sample.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 51 | <code>        sample.integer()  # compact source ID / expanded source type</code> | Call sample.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 52 | <code>        if tag == 3:</code> | Branch only if tag == 3 is true; otherwise skip this indented block or take its following elif/else. |
| 53 | <code>            sample.integer()  # expanded source index</code> | Call sample.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 54 | <code>        rate, _pool, sample_drops = sample.integer(), sample.integer(), sample.integer()</code> | Set (rate, _pool, sample_drops). Bundle these values in a tuple: (sample.integer(), sample.integer(), sample.integer()). |
| 55 | <code>        if rate &lt; 1:</code> | Branch only if rate < 1 is true; otherwise skip this indented block or take its following elif/else. |
| 56 | <code>            raise DecodeError(&quot;Invalid sampling rate&quot;)</code> | Raise DecodeError('Invalid sampling rate') and stop this operation; the caller can record/report this invalid condition. |
| 57 | <code>        drops = max(drops, sample_drops)  # cumulative counter, not additive per sample</code> | Set drops. Select the largest supplied value from max(drops, sample_drops). |
| 58 | <code>        for _ in range(4 if tag == 3 else 2):</code> | Loop: assign each item from range(4 if tag == 3 else 2) into _, then execute the indented body. |
| 59 | <code>            sample.integer()  # input/output interfaces and optional formats</code> | Call sample.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 60 | <code>        count = sample.integer()</code> | Set count. Call sample.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 61 | <code>        for _ in range(count):</code> | Loop: assign each item from range(count) into _, then execute the indented body. |
| 62 | <code>            record_tag, record_body = sample.record()</code> | Set (record_tag, record_body). Call sample.record with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 63 | <code>            if record_tag != 1:</code> | Branch only if record_tag != 1 is true; otherwise skip this indented block or take its following elif/else. |
| 64 | <code>                continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 65 | <code>            header = Reader(record_body)</code> | Set header. Construct a new Reader using record_body. |
| 66 | <code>            protocol, length = header.integer(), header.integer()</code> | Set (protocol, length). Bundle these values in a tuple: (header.integer(), header.integer()). |
| 67 | <code>            header.integer()  # stripped bytes</code> | Call header.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 68 | <code>            header_length = header.integer()</code> | Set header_length. Call header.integer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 69 | <code>            raw = header.take(header_length)</code> | Set raw. Call header.take with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 70 | <code>            packet = parse_header(raw, timestamp, length, rate, protocol)</code> | Set packet. Parse supported packet-header bytes defensively; unsupported/truncated input produces None. |
| 71 | <code>            if packet is not None:</code> | Branch only if packet is not None is true; otherwise skip this indented block or take its following elif/else. |
| 72 | <code>                packets.append(packet)</code> | Append packet to the end of packets. |
| 73 | <code>    return packets, {</code> | Return to the caller: Bundle these values in a tuple: (packets, {'agent': agent, 'subagent': subagent, 'sequence': sequence, 'uptime': uptime, 'drops': drops}). |
| 74 | <code>        &quot;agent&quot;: agent,</code> | Field agent: Named entry in the surrounding dictionary. Its value is agent; consumers access it by this key. |
| 75 | <code>        &quot;subagent&quot;: subagent,</code> | Field subagent: Named entry in the surrounding dictionary. Its value is subagent; consumers access it by this key. |
| 76 | <code>        &quot;sequence&quot;: sequence,</code> | Field sequence: Named entry in the surrounding dictionary. Its value is sequence; consumers access it by this key. |
| 77 | <code>        &quot;uptime&quot;: uptime,</code> | Field uptime: Named entry in the surrounding dictionary. Its value is uptime; consumers access it by this key. |
| 78 | <code>        &quot;drops&quot;: drops,</code> | Field drops: Named entry in the surrounding dictionary. Its value is drops; consumers access it by this key. |
| 79 | <code>    }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |

## src/m3/live.py

**Live UDP collector.** Binds a UDP socket, saves raw received sFlow datagrams, decodes sampled headers, forms windows, and invokes Evaluation. It does not sample again after OVS sampling. Labels come from separately supplied LabelTimeline annotations; immediate online training requires those experimental labels.

Snapshot: 112 lines; SHA256 `38699a758a1d423919d38e69e4f2bbb3acac6bba2627179c0e13e8a852225de7`.

### Named operations

- `run_live` (L14): Creates a UDP collector for live_sflow only, captures raw payloads and health counts, forms windows by receipt time, evaluates them, and finalizes on success or failure.
- `run_live.observe` (L38): Looks up a full-window annotation and sends the labeled window, sampled count, warm-up flag and actual relative observation time to Evaluation.

Live time is collector receipt/wall-clock time rather than original packet capture time. Raw frame matching is not performed in this collector: it uses LabelTimeline. It cannot claim independently counted original packets-to-detect from received samples alone. No input trace is replayed by this function; SDN orchestration creates traffic separately.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import socket</code> | Import socket to receive actual UDP datagrams from the sFlow exporter. |
| 2 | <code>import time</code> | Import time to measure elapsed work with monotonic timers and live collection with epoch wall-clock time. |
| 3 | <code>from dataclasses import replace</code> | Import replace from dataclasses. This makes the named library helpers available without the module prefix. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <code>from m3.engine import Evaluation</code> | Import Evaluation from m3.engine. These are project definitions; follow the named module in this guide to see their implementation. |
| 6 | <code>from m3.labels import LabelTimeline</code> | Import LabelTimeline from m3.labels. These are project definitions; follow the named module in this guide to see their implementation. |
| 7 | <code>from m3.packets import WindowAccumulator</code> | Import WindowAccumulator from m3.packets. These are project definitions; follow the named module in this guide to see their implementation. |
| 8 | <code>from m3.provenance import verify_input</code> | Import verify_input from m3.provenance. These are project definitions; follow the named module in this guide to see their implementation. |
| 9 | <code>from m3.resources import ResourceMonitor</code> | Import ResourceMonitor from m3.resources. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <code>from m3.sflow import DecodeError, decode_datagram</code> | Import DecodeError, decode_datagram from m3.sflow. These are project definitions; follow the named module in this guide to see their implementation. |
| 11 | <code>from m3.store import RunWriter</code> | Import RunWriter from m3.store. These are project definitions; follow the named module in this guide to see their implementation. |
| 12 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 13 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 14 | <code>def run_live(config):</code> | Define function/method run_live. Creates a UDP collector for live_sflow only, captures raw payloads and health counts, forms windows by receipt time, evaluates them, and finalizes on success or failure. |
| 15 | <code>    if config.mode != &quot;live_sflow&quot;:</code> | Branch only if config.mode != 'live_sflow' is true; otherwise skip this indented block or take its following elif/else. |
| 16 | <code>        raise ValueError(&quot;Live collector requires mode=live_sflow&quot;)</code> | Raise ValueError('Live collector requires mode=live_sflow') and stop this operation; the caller can record/report this invalid condition. |
| 17 | <code>    provenance = (</code> | Set provenance. Choose verify_input(config.input_path, config.manifest_path) when config.input_path is true; otherwise choose None. |
| 18 | <code>        verify_input(config.input_path, config.manifest_path) if config.input_path else None</code> | Continuation of the statement above. Choose verify_input(config.input_path, config.manifest_path) when config.input_path is true; otherwise choose None. |
| 19 | <code>    )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 20 | <code>    labels = LabelTimeline(config.labels_path)</code> | Set labels. Construct a new LabelTimeline using config.labels_path. |
| 21 | <code>    writer = RunWriter(</code> | Set writer. Construct a new RunWriter using config, 'official_5g_nidd' if provenance and labels.verified else 'live_sflow', provenance. |
| 22 | <code>        config, &quot;official_5g_nidd&quot; if provenance and labels.verified else &quot;live_sflow&quot;, provenance</code> | Continuation of the statement above. Choose 'official_5g_nidd' when provenance and labels.verified is true; otherwise choose 'live_sflow'. |
| 23 | <code>    )</code> | Close the call to RunWriter begun above; this is punctuation, not a separate operation. |
| 24 | <code>    evaluator = Evaluation(config, writer)</code> | Set evaluator. Call Evaluation with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 25 | <code>    resources = ResourceMonitor(writer, config.controller_pid)</code> | Set resources. Construct a new ResourceMonitor using writer, config.controller_pid. |
| 26 | <code>    accumulator = WindowAccumulator(config.window_seconds)</code> | Set accumulator. Construct a new WindowAccumulator using config.window_seconds. |
| 27 | <code>    start = config.start_epoch or time.time()</code> | Set start. Evaluate config.start_epoch or time.time() left to right with short-circuit or. |
| 28 | <code>    issues = {&quot;malformed_datagrams&quot;: 0, &quot;sampling_mismatches&quot;: 0, &quot;agent_reported_drops&quot;: 0}</code> | Set issues. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 29 | <code>    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)</code> | Set sock. Call socket.socket with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>    error = None</code> | Set error. Use the literal None (None means unavailable/not set). |
| 31 | <code>    try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 32 | <code>        sock.bind((config.bind, config.port))</code> | Call sock.bind with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 33 | <code>        sock.settimeout(0.2)</code> | Call sock.settimeout with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 34 | <code>        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)</code> | Call sock.setsockopt with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 35 | <code>        resources.start()</code> | Call resources.start with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 36 | <code>        print(f&quot;Collector ready on {config.bind}:{config.port}; run={writer.run_id}&quot;, flush=True)</code> | Call print with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 37 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 38 | <code>        def observe(item):</code> | Define function/method observe. Looks up a full-window annotation and sends the labeled window, sampled count, warm-up flag and actual relative observation time to Evaluation. |
| 39 | <code>            record, count = item</code> | Set (record, count). Read item from the current function/object state. |
| 40 | <code>            label, family = labels.label(record.time, record.time + config.window_seconds, start)</code> | Set (label, family). Use full-window annotation coverage; uncovered or boundary-crossing windows stay unknown. |
| 41 | <code>            evaluator.observe(</code> | Send an observation into predict-log-score-learn, with warm-up and label availability kept explicit. |
| 42 | <code>                replace(record, label=label, attack_family=family),</code> | Continuation of the statement above. Create a new dataclass instance with selected fields changed; the original remains unchanged: replace(record, label=label, attack_family=family). |
| 43 | <code>                record.time &lt; config.warmup_seconds,</code> | Continuation of the statement above. Evaluate the comparison record.time < config.warmup_seconds to True/False; comparisons may short-circuit. |
| 44 | <code>                count,</code> | Continuation of the statement above. Read count from the current function/object state. |
| 45 | <code>                time.time() - start,</code> | Continuation of the statement above. Calculate time.time() - start using subtract; / returns a floating-point ratio and // floors division where used. |
| 46 | <code>            )</code> | Close the call to evaluator.observe begun above; this is punctuation, not a separate operation. |
| 47 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 48 | <code>        with (writer.path / &quot;sflow.datagrams&quot;).open(&quot;wb&quot;) as raw:</code> | Enter managed resource/lock context (writer.path / 'sflow.datagrams').open('wb') as raw. Exiting the block releases/closes it, including on exceptions. |
| 49 | <code>            while time.time() - start &lt; config.duration_seconds:</code> | Repeat the indented body while time.time() - start < config.duration_seconds remains true; the body must advance state or terminate. |
| 50 | <code>                now = time.time()</code> | Set now. Call time.time with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 51 | <code>                if now &lt; start:</code> | Branch only if now < start is true; otherwise skip this indented block or take its following elif/else. |
| 52 | <code>                    time.sleep(min(0.1, start - now))</code> | Call time.sleep with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 53 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 54 | <code>                for item in accumulator.advance(min(now - start, config.duration_seconds)):</code> | Loop: assign each item from accumulator.advance(min(now - start, config.duration_seconds)) into item, then execute the indented body. |
| 55 | <code>                    observe(item)</code> | Call observe with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 56 | <code>                try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 57 | <code>                    payload, _peer = sock.recvfrom(65535)</code> | Set (payload, _peer). Call sock.recvfrom with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 58 | <code>                except TimeoutError:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 59 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 60 | <code>                received = time.time()</code> | Set received. Call time.time with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 61 | <code>                resources.telemetry_bytes += len(payload)</code> | Increase resources.telemetry_bytes by len(payload) and retain the updated state. |
| 62 | <code>                # Length-prefixed datagrams preserve raw export evidence without pickle.</code> | Source comment: Length-prefixed datagrams preserve raw export evidence without pickle. This documents intent and does not execute. |
| 63 | <code>                import struct</code> | Import struct to decode/encode network byte-order integers and binary framing. |
| 64 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 65 | <code>                raw.write(struct.pack(&quot;!dI&quot;, received, len(payload)))</code> | Call raw.write with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 66 | <code>                raw.write(payload)</code> | Call raw.write with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 67 | <code>                raw.flush()</code> | Flush buffered output in raw so another reader can see the written bytes; this is not an fsync durability guarantee. |
| 68 | <code>                try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 69 | <code>                    packets, metadata = decode_datagram(payload, received)</code> | Set (packets, metadata). Decode sFlow v5 payload records with explicit byte bounds and return parsed packets plus health metadata. |
| 70 | <code>                except DecodeError:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 71 | <code>                    issues[&quot;malformed_datagrams&quot;] += 1</code> | Increase issues['malformed_datagrams'] by 1 and retain the updated state. |
| 72 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 73 | <code>                issues[&quot;agent_reported_drops&quot;] = max(</code> | Set issues['agent_reported_drops']. Select the largest supplied value from max(issues['agent_reported_drops'], metadata['drops']). |
| 74 | <code>                    issues[&quot;agent_reported_drops&quot;], metadata[&quot;drops&quot;]</code> | Continuation of the statement above. Read issues['agent_reported_drops'] from the current function/object state. |
| 75 | <code>                )</code> | Close the call to max begun above; this is punctuation, not a separate operation. |
| 76 | <code>                for packet in packets:</code> | Loop: assign each item from packets into packet, then execute the indented body. |
| 77 | <code>                    writer.summary[&quot;counts&quot;][&quot;input&quot;] += 1</code> | Increase writer.summary['counts']['input'] by 1 and retain the updated state. |
| 78 | <code>                    if packet.sample_rate != config.sampling_rate:</code> | Branch only if packet.sample_rate != config.sampling_rate is true; otherwise skip this indented block or take its following elif/else. |
| 79 | <code>                        issues[&quot;sampling_mismatches&quot;] += 1</code> | Increase issues['sampling_mismatches'] by 1 and retain the updated state. |
| 80 | <code>                        continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 81 | <code>                    if packet.time - start &gt;= config.duration_seconds:</code> | Branch only if packet.time - start >= config.duration_seconds is true; otherwise skip this indented block or take its following elif/else. |
| 82 | <code>                        continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 83 | <code>                    writer.summary[&quot;counts&quot;][&quot;sampled&quot;] += 1</code> | Increase writer.summary['counts']['sampled'] by 1 and retain the updated state. |
| 84 | <code>                    for item in accumulator.add(packet, start):</code> | Loop: assign each item from accumulator.add(packet, start) into item, then execute the indented body. |
| 85 | <code>                        observe(item)</code> | Call observe with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 86 | <code>            for item in accumulator.advance(config.duration_seconds):</code> | Loop: assign each item from accumulator.advance(config.duration_seconds) into item, then execute the indented body. |
| 87 | <code>                observe(item)</code> | Call observe with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 88 | <code>            writer.summary[&quot;telemetry_health&quot;] = issues</code> | Set writer.summary['telemetry_health']. Read issues from the current function/object state. |
| 89 | <code>            writer.summary[&quot;notes&quot;] = [</code> | Set writer.summary['notes']. Build the ordered list below; order is retained. |
| 90 | <code>                &quot;Input count is received sample headers, not unsampled data-plane packets&quot;,</code> | Literal component of the surrounding statement: 'Input count is received sample headers, not unsampled data-plane packets'. Its role is determined by the field/call immediately above. |
| 91 | <code>                &quot;Bandwidth measures received sFlow UDP payload, excluding IP/UDP overhead&quot;,</code> | Literal component of the surrounding statement: 'Bandwidth measures received sFlow UDP payload, excluding IP/UDP overhead'. Its role is determined by the field/call immediately above. |
| 92 | <code>                &quot;Ground truth is scored only for fully covered, verified label intervals&quot;,</code> | Literal component of the surrounding statement: 'Ground truth is scored only for fully covered, verified label intervals'. Its role is determined by the field/call immediately above. |
| 93 | <code>            ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 94 | <code>            if not writer.summary[&quot;counts&quot;][&quot;sampled&quot;]:</code> | Branch only if not writer.summary['counts']['sampled'] is true; otherwise skip this indented block or take its following elif/else. |
| 95 | <code>                raise ValueError(&quot;No matching decoded sFlow packet samples received&quot;)</code> | Raise ValueError('No matching decoded sFlow packet samples received') and stop this operation; the caller can record/report this invalid condition. |
| 96 | <code>            if issues[&quot;sampling_mismatches&quot;]:</code> | Branch only if issues['sampling_mismatches'] is true; otherwise skip this indented block or take its following elif/else. |
| 97 | <code>                raise ValueError(&quot;Switch sampling rate changed/mismatched during the run&quot;)</code> | Raise ValueError('Switch sampling rate changed/mismatched during the run') and stop this operation; the caller can record/report this invalid condition. |
| 98 | <code>    except BaseException as exc:  # noqa: BLE001 - interrupts must close files and mark the run failed</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 99 | <code>        error = exc</code> | Set error. Read exc from the current function/object state. |
| 100 | <code>    finally:</code> | Always execute cleanup below when leaving the associated try block, whether it succeeded or raised. |
| 101 | <code>        sock.close()</code> | Close sock and release its file/socket/plot resource. |
| 102 | <code>        if resources.thread.is_alive():</code> | Branch only if resources.thread.is_alive() is true; otherwise skip this indented block or take its following elif/else. |
| 103 | <code>            cost = resources.finish(live=True)</code> | Set cost. Stop background sampling and finalize resource/lab metrics; live=True marks received sFlow bytes as measured. |
| 104 | <code>        else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 105 | <code>            cost = {}</code> | Set cost. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 106 | <code>        writer.summary[&quot;telemetry_health&quot;] = issues</code> | Set writer.summary['telemetry_health']. Read issues from the current function/object state. |
| 107 | <code>        writer.finish({**evaluator.summary(), **cost}, error)</code> | Persist final run status, metrics and any failure, then close raw CSV files. |
| 108 | <code>    if error:</code> | Branch only if error is true; otherwise skip this indented block or take its following elif/else. |
| 109 | <code>        raise RuntimeError(</code> | Raise RuntimeError(f'Live run {writer.run_id} failed; evidence retained: {error}') and stop this operation; chain the original cause for diagnostics. |
| 110 | <code>            f&quot;Live run {writer.run_id} failed; evidence retained: {error}&quot;</code> | Continuation of the statement above. Read f'Live run {writer.run_id} failed; evidence retained: {error}' from the current function/object state. |
| 111 | <code>        ) from error</code> | Continuation of the statement above. Read error from the current function/object state. |
| 112 | <code>    return writer.summary</code> | Return to the caller: Read writer.summary from the current function/object state. |

## src/m3/resources.py

**Background process/resource measurement.** Samples collector/detector process CPU and RSS about once per second, optionally samples a separate controller PID, and delegates switch/OpenFlow observations to LabMeasurements. CPU percent uses one logical CPU as 100%; it may exceed 100 for a multithreaded process.

Snapshot: 91 lines; SHA256 `456ff4f6423e070466508aeec620a03ae86f2520d1c258f19d79d4075e2ad73e`.

### Named operations

- `ResourceMonitor.__init__` (L13): Binds this process and optional controller process, constructs lab observers, and prepares a daemon thread and stop event.
- `ResourceMonitor.start` (L27): Starts independent lab collection, primes CPU counters, then starts the background loop.
- `ResourceMonitor.sample` (L35): Takes one process/controller resource snapshot, asks OVS for entries, retains it and appends it to resources.csv.
- `ResourceMonitor._loop` (L53): Waits one second at a time on a stop event; samples until stopping is requested.
- `ResourceMonitor.finish` (L57): Stops and joins the background thread, takes a final snapshot, summarizes samples and converts payload bytes / elapsed time to kbit/s.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import threading</code> | Import threading to run resource sampling in the background and coordinate stop events/writer locks. |
| 2 | <code>import time</code> | Import time to measure elapsed work with monotonic timers and live collection with epoch wall-clock time. |
| 3 | <code>from statistics import mean</code> | Import mean from statistics. This makes the named library helpers available without the module prefix. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <code>import numpy as np</code> | Import numpy as np to calculate numeric means and percentiles. |
| 6 | <code>import psutil</code> | Import psutil to read OS process CPU and resident-memory measurements. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <code>from m3.lab import LabMeasurements</code> | Import LabMeasurements from m3.lab. These are project definitions; follow the named module in this guide to see their implementation. |
| 9 | <code>from m3.metrics import measurement</code> | Import measurement from m3.metrics. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <code>class ResourceMonitor:</code> | Define class ResourceMonitor. Groups the following statements into a named reusable operation. |
| 13 | <code>    def __init__(self, writer, controller_pid=None):</code> | Define function/method __init__. Binds this process and optional controller process, constructs lab observers, and prepares a daemon thread and stop event. |
| 14 | <code>        self.writer = writer</code> | Set self.writer. Read writer from the current function/object state. |
| 15 | <code>        self.lab = LabMeasurements(writer)</code> | Set self.lab. Construct a new LabMeasurements using writer. |
| 16 | <code>        self.process = psutil.Process()</code> | Set self.process. Call psutil.Process with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 17 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 18 | <code>            self.controller = psutil.Process(controller_pid) if controller_pid else None</code> | Set self.controller. Choose psutil.Process(controller_pid) when controller_pid is true; otherwise choose None. |
| 19 | <code>        except psutil.NoSuchProcess:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 20 | <code>            self.controller = None</code> | Set self.controller. Use the literal None (None means unavailable/not set). |
| 21 | <code>        self.rows = []</code> | Set self.rows. Build the ordered list below; order is retained. |
| 22 | <code>        self.telemetry_bytes = 0</code> | Set self.telemetry_bytes. Use the literal 0. |
| 23 | <code>        self.stop_event = threading.Event()</code> | Set self.stop_event. Call threading.Event with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 24 | <code>        self.started = time.perf_counter()</code> | Set self.started. Call time.perf_counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 25 | <code>        self.thread = threading.Thread(target=self._loop, daemon=True)</code> | Set self.thread. Call threading.Thread with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 26 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 27 | <code>    def start(self):</code> | Define function/method start. Starts independent lab collection, primes CPU counters, then starts the background loop. |
| 28 | <code>        self.started = time.perf_counter()</code> | Set self.started. Call time.perf_counter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 29 | <code>        self.lab.start()</code> | Call self.lab.start with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>        self.process.cpu_percent()</code> | Call self.process.cpu_percent with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 31 | <code>        if self.controller:</code> | Branch only if self.controller is true; otherwise skip this indented block or take its following elif/else. |
| 32 | <code>            self.controller.cpu_percent()</code> | Call self.controller.cpu_percent with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 33 | <code>        self.thread.start()</code> | Begin background resource sampling concurrently with the experiment. |
| 34 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 35 | <code>    def sample(self):</code> | Define function/method sample. Takes one process/controller resource snapshot, asks OVS for entries, retains it and appends it to resources.csv. |
| 36 | <code>        controller_cpu = None</code> | Set controller_cpu. Use the literal None (None means unavailable/not set). |
| 37 | <code>        if self.controller:</code> | Branch only if self.controller is true; otherwise skip this indented block or take its following elif/else. |
| 38 | <code>            try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 39 | <code>                controller_cpu = self.controller.cpu_percent()</code> | Set controller_cpu. Call self.controller.cpu_percent with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 40 | <code>            except (psutil.NoSuchProcess, psutil.AccessDenied):</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 41 | <code>                self.controller = None</code> | Set self.controller. Use the literal None (None means unavailable/not set). |
| 42 | <code>        row = {</code> | Set row. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 43 | <code>            &quot;time&quot;: time.perf_counter() - self.started,</code> | Field time: Named entry in the surrounding dictionary. Its value is time.perf_counter() - self.started; consumers access it by this key. |
| 44 | <code>            &quot;cpu_percent&quot;: self.process.cpu_percent(),</code> | Field cpu_percent: Named entry in the surrounding dictionary. Its value is self.process.cpu_percent(); consumers access it by this key. |
| 45 | <code>            &quot;rss_mb&quot;: self.process.memory_info().rss / 1024**2,</code> | Field rss_mb: Named entry in the surrounding dictionary. Its value is self.process.memory_info().rss / 1024**2; consumers access it by this key. |
| 46 | <code>            &quot;telemetry_bytes&quot;: self.telemetry_bytes,</code> | Field telemetry_bytes: Named entry in the surrounding dictionary. Its value is self.telemetry_bytes; consumers access it by this key. |
| 47 | <code>            &quot;controller_cpu_percent&quot;: controller_cpu,</code> | Field controller_cpu_percent: Named entry in the surrounding dictionary. Its value is controller_cpu; consumers access it by this key. |
| 48 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 49 | <code>        row[&quot;flow_table_entries&quot;] = self.lab.sample()</code> | Set row['flow_table_entries']. Read an actual OVS flow snapshot; failures yield None rather than a fake entry count. |
| 50 | <code>        self.rows.append(row)</code> | Append row to the end of self.rows. |
| 51 | <code>        self.writer.append(&quot;resources&quot;, row)</code> | Append one raw evidence row to the named CSV and flush it immediately. |
| 52 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 53 | <code>    def _loop(self):</code> | Define function/method _loop. Waits one second at a time on a stop event; samples until stopping is requested. |
| 54 | <code>        while not self.stop_event.wait(1):</code> | Repeat the indented body while not self.stop_event.wait(1) remains true; the body must advance state or terminate. |
| 55 | <code>            self.sample()</code> | Call self.sample with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 56 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 57 | <code>    def finish(self, live=False):</code> | Define function/method finish. Stops and joins the background thread, takes a final snapshot, summarizes samples and converts payload bytes / elapsed time to kbit/s. |
| 58 | <code>        self.stop_event.set()</code> | Signal the monitor thread to stop. |
| 59 | <code>        self.thread.join()</code> | Wait for the resource thread to stop before calculating final summaries. |
| 60 | <code>        self.sample()</code> | Call self.sample with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 61 | <code>        elapsed = max(time.perf_counter() - self.started, 1e-9)</code> | Set elapsed. Select the largest supplied value from max(time.perf_counter() - self.started, 1e-09). |
| 62 | <code>        cpus = [r[&quot;cpu_percent&quot;] for r in self.rows]</code> | Set cpus. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [r['cpu_percent'] for r in self.rows]. |
| 63 | <code>        controllers = [</code> | Set controllers. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [r['controller_cpu_percent'] for r in self.rows if r['controller_cpu_percent'] is not None]. |
| 64 | <code>            r[&quot;controller_cpu_percent&quot;]</code> | Continuation of the statement above. Read r['controller_cpu_percent'] from the current function/object state. |
| 65 | <code>            for r in self.rows</code> | Continuation of the statement above. Read self.rows from the current function/object state. |
| 66 | <code>            if r[&quot;controller_cpu_percent&quot;] is not None</code> | Continuation of the statement above. Evaluate the comparison r['controller_cpu_percent'] is not None to True/False; comparisons may short-circuit. |
| 67 | <code>        ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 68 | <code>        return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 69 | <code>            **self.lab.finish(elapsed),</code> | Continuation of the statement above. Finish the independent OpenFlow capture and summarize OVS entries. |
| 70 | <code>            &quot;cpu_percent_mean&quot;: measurement(mean(cpus), &quot;% of one logical CPU&quot;),</code> | Field cpu_percent_mean: Named entry in the surrounding dictionary. Its value is measurement(mean(cpus), "% of one logical CPU"); consumers access it by this key. |
| 71 | <code>            &quot;cpu_percent_p95&quot;: measurement(np.percentile(cpus, 95), &quot;% of one logical CPU&quot;),</code> | Field cpu_percent_p95: Named entry in the surrounding dictionary. Its value is measurement(np.percentile(cpus, 95), "% of one logical CPU"); consumers access it by this key. |
| 72 | <code>            &quot;rss_mb_peak&quot;: measurement(max(r[&quot;rss_mb&quot;] for r in self.rows), &quot;MiB&quot;),</code> | Field rss_mb_peak: Named entry in the surrounding dictionary. Its value is measurement(max(r["rss_mb"] for r in self.rows), "MiB"); consumers access it by this key. |
| 73 | <code>            &quot;telemetry_bandwidth_kbps&quot;: measurement(</code> | Field telemetry_bandwidth_kbps: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 74 | <code>                self.telemetry_bytes * 8 / elapsed / 1000,</code> | Continuation of the statement above. Calculate self.telemetry_bytes * 8 / elapsed / 1000 using divide; / returns a floating-point ratio and // floors division where used. |
| 75 | <code>                &quot;kbit/s&quot;,</code> | Literal component of the surrounding statement: 'kbit/s'. Its role is determined by the field/call immediately above. |
| 76 | <code>                status=&quot;measured&quot; if live else &quot;estimated&quot;,</code> | Keyword argument status for the call above. Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 77 | <code>                reason=None</code> | Keyword argument reason for the call above. Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 78 | <code>                if live</code> | Continuation of the statement above. Read live from the current function/object state. |
| 79 | <code>                else &quot;Serialized feature payload proxy, not an SDN channel measurement&quot;,</code> | Literal component of the surrounding statement: 'Serialized feature payload proxy, not an SDN channel measurement'. Its role is determined by the field/call immediately above. |
| 80 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 81 | <code>            &quot;controller_cpu_percent_mean&quot;: measurement(</code> | Field controller_cpu_percent_mean: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 82 | <code>                mean(controllers) if controllers else None,</code> | Continuation of the statement above. Choose mean(controllers) when controllers is true; otherwise choose None. |
| 83 | <code>                &quot;% of one logical CPU&quot;,</code> | Literal component of the surrounding statement: '% of one logical CPU'. Its role is determined by the field/call immediately above. |
| 84 | <code>                reason=&quot;No live controller PID was monitored&quot;,</code> | Keyword argument reason for the call above. Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 85 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 86 | <code>            &quot;controller_cpu_percent_p95&quot;: measurement(</code> | Field controller_cpu_percent_p95: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 87 | <code>                np.percentile(controllers, 95) if controllers else None,</code> | Continuation of the statement above. Choose np.percentile(controllers, 95) when controllers is true; otherwise choose None. |
| 88 | <code>                &quot;% of one logical CPU&quot;,</code> | Literal component of the surrounding statement: '% of one logical CPU'. Its role is determined by the field/call immediately above. |
| 89 | <code>                reason=&quot;No live controller PID was monitored&quot;,</code> | Keyword argument reason for the call above. Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 90 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 91 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |

## src/m3/lab.py

**Independent lab observations.** Reads OVS flow-table snapshots and captures loopback OpenFlow traffic with tcpdump in Linux. These are separate observations from received sFlow bytes. The subprocess argument lists are explicit; no shell command string is assembled from bridge names.

Snapshot: 103 lines; SHA256 `eef3df4094748f83ca5f3876c7e03d12e7cd05660c62267405d84ea918f19c08`.

### Named operations

- `LabMeasurements.__init__` (L13): Enables OVS/OpenFlow observations only for a configured live run; initializes unavailable reasons for unconfigured measurements.
- `LabMeasurements.start` (L24): Starts tcpdump on Linux loopback for the configured OpenFlow TCP port and preserves its diagnostics.
- `LabMeasurements.sample` (L53): Runs a read-only ovs-ofctl flow dump with a one-second timeout and counts flow-entry lines; errors yield unavailable.
- `LabMeasurements.finish` (L73): Stops tcpdump cleanly, reads captured frame bytes, releases resources, then returns independent OpenFlow bandwidth and mean OVS entries.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;Read-only OVS observation and loopback-only OpenFlow capture for the isolated lab.&quot;&quot;&quot;</code> | Documentation string: Read-only OVS observation and loopback-only OpenFlow capture for the isolated lab. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>import signal</code> | Import signal to request a clean tcpdump shutdown with SIGINT. |
| 4 | <code>import subprocess</code> | Import subprocess to invoke independent lab tools with explicit argument lists. |
| 5 | <code>import sys</code> | Import sys to check which operating system is running. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <code>import dpkt</code> | Import dpkt to read packet-capture files and parse packet structures. |
| 8 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 9 | <code>from m3.metrics import measurement</code> | Import measurement from m3.metrics. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <code>class LabMeasurements:</code> | Define class LabMeasurements. Groups the following statements into a named reusable operation. |
| 13 | <code>    def __init__(self, writer):</code> | Define function/method __init__. Enables OVS/OpenFlow observations only for a configured live run; initializes unavailable reasons for unconfigured measurements. |
| 14 | <code>        self.writer = writer</code> | Set self.writer. Read writer from the current function/object state. |
| 15 | <code>        config = writer.summary[&quot;config&quot;]</code> | Set config. Read writer.summary['config'] from the current function/object state. |
| 16 | <code>        self.bridge = config.get(&quot;ovs_bridge&quot;) if config[&quot;mode&quot;] == &quot;live_sflow&quot; else None</code> | Set self.bridge. Choose config.get('ovs_bridge') when config['mode'] == 'live_sflow' is true; otherwise choose None. |
| 17 | <code>        self.port = config.get(&quot;openflow_port&quot;) if config[&quot;mode&quot;] == &quot;live_sflow&quot; else None</code> | Set self.port. Choose config.get('openflow_port') when config['mode'] == 'live_sflow' is true; otherwise choose None. |
| 18 | <code>        self.capture = None</code> | Set self.capture. Use the literal None (None means unavailable/not set). |
| 19 | <code>        self.log = None</code> | Set self.log. Use the literal None (None means unavailable/not set). |
| 20 | <code>        self.flow_counts = []</code> | Set self.flow_counts. Build the ordered list below; order is retained. |
| 21 | <code>        self.flow_error = &quot;OVS observation was not configured&quot;</code> | Set self.flow_error. Use the literal 'OVS observation was not configured'. |
| 22 | <code>        self.capture_error = &quot;Independent OpenFlow capture was not configured&quot;</code> | Set self.capture_error. Use the literal 'Independent OpenFlow capture was not configured'. |
| 23 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 24 | <code>    def start(self):</code> | Define function/method start. Starts tcpdump on Linux loopback for the configured OpenFlow TCP port and preserves its diagnostics. |
| 25 | <code>        if self.port is None:</code> | Branch only if self.port is None is true; otherwise skip this indented block or take its following elif/else. |
| 26 | <code>            return</code> | Return to the caller with None. |
| 27 | <code>        if sys.platform != &quot;linux&quot;:</code> | Branch only if sys.platform != 'linux' is true; otherwise skip this indented block or take its following elif/else. |
| 28 | <code>            self.capture_error = &quot;OpenFlow capture must run inside the Linux SDN namespace&quot;</code> | Set self.capture_error. Use the literal 'OpenFlow capture must run inside the Linux SDN namespace'. |
| 29 | <code>            return</code> | Return to the caller with None. |
| 30 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 31 | <code>            self.log = (self.writer.path / &quot;openflow_capture.log&quot;).open(&quot;wb&quot;)</code> | Set self.log. Open the named file using the shown text/binary mode and encoding: (self.writer.path / 'openflow_capture.log').open('wb'). |
| 32 | <code>            self.capture = subprocess.Popen(</code> | Set self.capture. Start a child process using an explicit argument list and retain a handle for cleanup. |
| 33 | <code>                [</code> | Continuation of the statement above. Build the ordered list below; order is retained. |
| 34 | <code>                    &quot;tcpdump&quot;,</code> | Literal component of the surrounding statement: 'tcpdump'. Its role is determined by the field/call immediately above. |
| 35 | <code>                    &quot;-i&quot;,</code> | Literal component of the surrounding statement: '-i'. Its role is determined by the field/call immediately above. |
| 36 | <code>                    &quot;lo&quot;,</code> | Literal component of the surrounding statement: 'lo'. Its role is determined by the field/call immediately above. |
| 37 | <code>                    &quot;-U&quot;,</code> | Literal component of the surrounding statement: '-U'. Its role is determined by the field/call immediately above. |
| 38 | <code>                    &quot;-w&quot;,</code> | Literal component of the surrounding statement: '-w'. Its role is determined by the field/call immediately above. |
| 39 | <code>                    str(self.writer.path / &quot;openflow.pcap&quot;),</code> | Continuation of the statement above. Convert self.writer.path / 'openflow.pcap' to str. |
| 40 | <code>                    &quot;tcp&quot;,</code> | Literal component of the surrounding statement: 'tcp'. Its role is determined by the field/call immediately above. |
| 41 | <code>                    &quot;port&quot;,</code> | Literal component of the surrounding statement: 'port'. Its role is determined by the field/call immediately above. |
| 42 | <code>                    str(self.port),</code> | Continuation of the statement above. Convert self.port to str. |
| 43 | <code>                ],</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 44 | <code>                stdout=self.log,</code> | Keyword argument stdout for the call above. Pass the shown value self.log into that parameter. |
| 45 | <code>                stderr=subprocess.STDOUT,</code> | Keyword argument stderr for the call above. Pass the shown value subprocess.STDOUT into that parameter. |
| 46 | <code>            )</code> | Close the call to subprocess.Popen begun above; this is punctuation, not a separate operation. |
| 47 | <code>        except OSError as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 48 | <code>            self.capture_error = f&quot;OpenFlow capture could not start: {exc}&quot;</code> | Set self.capture_error. Read f'OpenFlow capture could not start: {exc}' from the current function/object state. |
| 49 | <code>            if self.log:</code> | Branch only if self.log is true; otherwise skip this indented block or take its following elif/else. |
| 50 | <code>                self.log.close()</code> | Close self.log and release its file/socket/plot resource. |
| 51 | <code>                self.log = None</code> | Set self.log. Use the literal None (None means unavailable/not set). |
| 52 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 53 | <code>    def sample(self):</code> | Define function/method sample. Runs a read-only ovs-ofctl flow dump with a one-second timeout and counts flow-entry lines; errors yield unavailable. |
| 54 | <code>        if not self.bridge:</code> | Branch only if not self.bridge is true; otherwise skip this indented block or take its following elif/else. |
| 55 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 56 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 57 | <code>            result = subprocess.run(</code> | Set result. Run the read-only external command with captured output and configured timeout/error checks. |
| 58 | <code>                [&quot;ovs-ofctl&quot;, &quot;-O&quot;, &quot;OpenFlow13&quot;, &quot;dump-flows&quot;, self.bridge],</code> | Continuation of the statement above. Build the ordered list below; order is retained. |
| 59 | <code>                capture_output=True,</code> | Keyword argument capture_output for the call above. Pass the shown value True into that parameter. |
| 60 | <code>                text=True,</code> | Keyword argument text for the call above. Pass the shown value True into that parameter. |
| 61 | <code>                timeout=1,</code> | Keyword argument timeout for the call above. Pass the shown value 1 into that parameter. |
| 62 | <code>                check=True,</code> | Keyword argument check for the call above. Pass the shown value True into that parameter. |
| 63 | <code>            )</code> | Close the call to subprocess.run begun above; this is punctuation, not a separate operation. |
| 64 | <code>            if &quot;OFPST_FLOW&quot; not in result.stdout and &quot;OFPMP_FLOW&quot; not in result.stdout:</code> | Branch only if 'OFPST_FLOW' not in result.stdout and 'OFPMP_FLOW' not in result.stdout is true; otherwise skip this indented block or take its following elif/else. |
| 65 | <code>                raise ValueError(&quot;OVS did not return a flow-statistics reply&quot;)</code> | Raise ValueError('OVS did not return a flow-statistics reply') and stop this operation; the caller can record/report this invalid condition. |
| 66 | <code>            count = sum(&quot;cookie=&quot; in line for line in result.stdout.splitlines())</code> | Set count. Add the values yielded by ('cookie=' in line for line in result.stdout.splitlines()); booleans count as 1 for True and 0 for False. |
| 67 | <code>            self.flow_counts.append(count)</code> | Append count to the end of self.flow_counts. |
| 68 | <code>            return count</code> | Return to the caller: Read count from the current function/object state. |
| 69 | <code>        except (OSError, subprocess.SubprocessError, ValueError) as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 70 | <code>            self.flow_error = f&quot;OVS flow observation unavailable: {exc}&quot;</code> | Set self.flow_error. Read f'OVS flow observation unavailable: {exc}' from the current function/object state. |
| 71 | <code>            return None</code> | Return to the caller: Use the literal None (None means unavailable/not set). |
| 72 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 73 | <code>    def finish(self, elapsed):</code> | Define function/method finish. Stops tcpdump cleanly, reads captured frame bytes, releases resources, then returns independent OpenFlow bandwidth and mean OVS entries. |
| 74 | <code>        byte_count = None</code> | Set byte_count. Use the literal None (None means unavailable/not set). |
| 75 | <code>        if self.capture:</code> | Branch only if self.capture is true; otherwise skip this indented block or take its following elif/else. |
| 76 | <code>            try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 77 | <code>                if self.capture.poll() is None:</code> | Branch only if self.capture.poll() is None is true; otherwise skip this indented block or take its following elif/else. |
| 78 | <code>                    self.capture.send_signal(signal.SIGINT)</code> | Call self.capture.send_signal with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 79 | <code>                self.capture.wait(timeout=3)</code> | Call self.capture.wait with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 80 | <code>                if self.capture.returncode != 0:</code> | Branch only if self.capture.returncode != 0 is true; otherwise skip this indented block or take its following elif/else. |
| 81 | <code>                    raise ValueError(&quot;tcpdump failed; inspect openflow_capture.log&quot;)</code> | Raise ValueError('tcpdump failed; inspect openflow_capture.log') and stop this operation; the caller can record/report this invalid condition. |
| 82 | <code>                with (self.writer.path / &quot;openflow.pcap&quot;).open(&quot;rb&quot;) as stream:</code> | Enter managed resource/lock context (self.writer.path / 'openflow.pcap').open('rb') as stream. Exiting the block releases/closes it, including on exceptions. |
| 83 | <code>                    byte_count = sum(len(packet) for _, packet in dpkt.pcap.Reader(stream))</code> | Set byte_count. Add the values yielded by (len(packet) for _, packet in dpkt.pcap.Reader(stream)); booleans count as 1 for True and 0 for False. |
| 84 | <code>            except (OSError, ValueError, dpkt.UnpackError, subprocess.SubprocessError) as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 85 | <code>                self.capture_error = f&quot;OpenFlow capture unavailable: {exc}&quot;</code> | Set self.capture_error. Read f'OpenFlow capture unavailable: {exc}' from the current function/object state. |
| 86 | <code>            finally:</code> | Always execute cleanup below when leaving the associated try block, whether it succeeded or raised. |
| 87 | <code>                if self.capture.poll() is None:</code> | Branch only if self.capture.poll() is None is true; otherwise skip this indented block or take its following elif/else. |
| 88 | <code>                    self.capture.kill()</code> | Call self.capture.kill with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 89 | <code>                    self.capture.wait(timeout=3)</code> | Call self.capture.wait with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 90 | <code>                if self.log:</code> | Branch only if self.log is true; otherwise skip this indented block or take its following elif/else. |
| 91 | <code>                    self.log.close()</code> | Close self.log and release its file/socket/plot resource. |
| 92 | <code>        return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 93 | <code>            &quot;openflow_bandwidth_kbps&quot;: measurement(</code> | Field openflow_bandwidth_kbps: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 94 | <code>                byte_count * 8 / elapsed / 1000 if byte_count is not None else None,</code> | Continuation of the statement above. Choose byte_count * 8 / elapsed / 1000 when byte_count is not None is true; otherwise choose None. |
| 95 | <code>                &quot;kbit/s&quot;,</code> | Literal component of the surrounding statement: 'kbit/s'. Its role is determined by the field/call immediately above. |
| 96 | <code>                self.capture_error,</code> | Continuation of the statement above. Read self.capture_error from the current function/object state. |
| 97 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 98 | <code>            &quot;flow_table_entries&quot;: measurement(</code> | Field flow_table_entries: Named entry in the surrounding dictionary. Its value is measurement(; consumers access it by this key. |
| 99 | <code>                sum(self.flow_counts) / len(self.flow_counts) if self.flow_counts else None,</code> | Continuation of the statement above. Choose sum(self.flow_counts) / len(self.flow_counts) when self.flow_counts is true; otherwise choose None. |
| 100 | <code>                &quot;entries (snapshot mean)&quot;,</code> | Literal component of the surrounding statement: 'entries (snapshot mean)'. Its role is determined by the field/call immediately above. |
| 101 | <code>                self.flow_error,</code> | Continuation of the statement above. Read self.flow_error from the current function/object state. |
| 102 | <code>            ),</code> | Close the call to measurement begun above; the comma separates it from the next surrounding argument/item. |
| 103 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |

## src/m3/provenance.py

**Data identity and checksum checks.** Hashes files in chunks and checks their identity against the official dataset manifest. Matching a local manifest is necessary for these runs; the upstream download/checksum verification in scripts/fetch_dataset.py is what establishes how manifest entries were produced.

Snapshot: 33 lines; SHA256 `06bb4a015d87b6ea526f4bc195c695efb1d9468dcaf7501fc8ded2c28989e41e`.

### Named operations

- `sha256` (L8): Hashes a file incrementally in one-MiB chunks; the digest is a fingerprint of exact bytes.
- `verify_input` (L16): Checks official manifest identity, per-file verification status and actual SHA256. Unknown, unverified or modified files are rejected.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import hashlib</code> | Import hashlib to calculate SHA256 fingerprints of exact source bytes. |
| 2 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 3 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 4 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 5 | <code>OFFICIAL_DOI = &quot;10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361&quot;</code> | Set OFFICIAL_DOI. Use the literal '10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361'. |
| 6 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <code>def sha256(path: str &#124; Path) -&gt; str:</code> | Define function/method sha256. Hashes a file incrementally in one-MiB chunks; the digest is a fingerprint of exact bytes. |
| 9 | <code>    digest = hashlib.sha256()</code> | Set digest. Call hashlib.sha256 with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 10 | <code>    with Path(path).open(&quot;rb&quot;) as stream:</code> | Enter managed resource/lock context Path(path).open('rb') as stream. Exiting the block releases/closes it, including on exceptions. |
| 11 | <code>        for chunk in iter(lambda: stream.read(1024 * 1024), b&quot;&quot;):</code> | Loop: assign each item from iter(lambda: stream.read(1024 * 1024), b'') into chunk, then execute the indented body. |
| 12 | <code>            digest.update(chunk)</code> | Call digest.update with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 13 | <code>    return digest.hexdigest()</code> | Return to the caller: Call digest.hexdigest with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 14 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 15 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 16 | <code>def verify_input(path: str &#124; Path, manifest_path: str &#124; Path) -&gt; dict:</code> | Define function/method verify_input. Checks official manifest identity, per-file verification status and actual SHA256. Unknown, unverified or modified files are rejected. |
| 17 | <code>    source = Path(path).resolve()</code> | Set source. Call Path(path).resolve with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 18 | <code>    manifest = json.loads(Path(manifest_path).read_text(encoding=&quot;utf-8&quot;))</code> | Set manifest. Call json.loads with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 19 | <code>    if manifest.get(&quot;dataset&quot;) != &quot;5G-NIDD&quot; or manifest.get(&quot;doi&quot;) != OFFICIAL_DOI:</code> | Branch only if manifest.get('dataset') != '5G-NIDD' or manifest.get('doi') != OFFICIAL_DOI is true; otherwise skip this indented block or take its following elif/else. |
| 20 | <code>        raise ValueError(&quot;Input requires the official 5G-NIDD provenance manifest&quot;)</code> | Raise ValueError('Input requires the official 5G-NIDD provenance manifest') and stop this operation; the caller can record/report this invalid condition. |
| 21 | <code>    for entry in manifest.get(&quot;files&quot;, []):</code> | Loop: assign each item from manifest.get('files', []) into entry, then execute the indented body. |
| 22 | <code>        if Path(entry[&quot;path&quot;]).resolve() == source:</code> | Branch only if Path(entry['path']).resolve() == source is true; otherwise skip this indented block or take its following elif/else. |
| 23 | <code>            if (</code> | Branch only if manifest.get('status') != 'verified' and entry.get('verification_status') != 'verified' and (entry.get('verified') is not True) is true; otherwise skip this indented block or take its following elif/else. |
| 24 | <code>                manifest.get(&quot;status&quot;) != &quot;verified&quot;</code> | Continuation of the statement above. Evaluate manifest.get('status') != 'verified' and entry.get('verification_status') != 'verified' and (entry.get('verified') is not True) left to right with short-circuit and. |
| 25 | <code>                and entry.get(&quot;verification_status&quot;) != &quot;verified&quot;</code> | Continuation of the statement above. Evaluate the comparison entry.get('verification_status') != 'verified' to True/False; comparisons may short-circuit. |
| 26 | <code>                and entry.get(&quot;verified&quot;) is not True</code> | Continuation of the statement above. Evaluate the comparison entry.get('verified') is not True to True/False; comparisons may short-circuit. |
| 27 | <code>            ):</code> | Continue the surrounding verify_input statement: ):. The indentation and open brackets connect it to the operation above. |
| 28 | <code>                raise ValueError(&quot;Selected official file is not yet verified&quot;)</code> | Raise ValueError('Selected official file is not yet verified') and stop this operation; the caller can record/report this invalid condition. |
| 29 | <code>            actual = sha256(source)</code> | Set actual. Call sha256 with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>            if actual != entry.get(&quot;sha256&quot;):</code> | Branch only if actual != entry.get('sha256') is true; otherwise skip this indented block or take its following elif/else. |
| 31 | <code>                raise ValueError(&quot;Dataset checksum mismatch: preserve the verified original&quot;)</code> | Raise ValueError('Dataset checksum mismatch: preserve the verified original') and stop this operation; the caller can record/report this invalid condition. |
| 32 | <code>            return {&quot;dataset&quot;: &quot;5G-NIDD&quot;, &quot;doi&quot;: OFFICIAL_DOI, **entry}</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 33 | <code>    raise ValueError(&quot;Input is not registered in the official dataset manifest&quot;)</code> | Raise ValueError('Input is not registered in the official dataset manifest') and stop this operation; the caller can record/report this invalid condition. |

## src/m3/store.py

**Evidence writer and read-only run repository.** RunWriter creates a unique directory, appends raw CSV evidence, and replaces JSON summaries atomically. RunRepository reads the summaries and a limited series for the dashboard. It validates run IDs and rejects run-directory symlinks. The API series is a visualization sample, not the data from which experimental metrics should be recalculated.

Snapshot: 182 lines; SHA256 `1d6e7674d40e71c71b04c96850503b2feccc8abd4c06509f2674c4524ca6836d`.

### Named operations

- `utc_now` (L13): Returns an ISO 8601 UTC time string for run bookkeeping, independent of client timezone.
- `dependency_versions` (L17): Reads installed package versions for reproducibility; missing distributions are recorded explicitly.
- `atomic_json` (L27): Writes valid JSON to a sibling temporary path, then replaces the visible target so readers avoid a partially written JSON document.
- `RunWriter.__init__` (L34): Creates a UUID-named run directory, raw CSV files with fixed schemas, and an initial running summary with model/config/data provenance.
- `RunWriter.append` (L102): Uses a lock to append and immediately flush one raw CSV row; this is raw evidence, not dashboard formatting.
- `RunWriter.save` (L107): Uses the same lock to atomically replace the run JSON summary.
- `RunWriter.finish` (L111): Marks status/error/end time, saves final metrics, then closes raw evidence streams.
- `RunRepository.__init__` (L125): Resolves the configured evidence root to an absolute filesystem location.
- `RunRepository.directory` (L128): Allows only a 32-character lowercase-hex run ID and a real nonsymlink run directory beneath the evidence root.
- `RunRepository.get` (L136): Loads the chosen run_summary.json through the checked directory lookup.
- `RunRepository.list` (L139): Finds valid readable run summaries and sorts newest first; absent roots return an empty list, in-progress unreadable files are skipped.
- `RunRepository.series` (L151): Counts CSV records, chooses evenly spaced row indices if needed, rereads selected rows and converts values for JSON using bounded result memory.

CSV series first scans to count rows and then scans again; memory is bounded by the selected result size, but work still grows with file length. Uniform series downsampling can omit brief spikes or drift events. Atomic replacement protects readers against partial JSON; it does not provide a full database transaction or fsync guarantee.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>import csv</code> | Import csv to stream CSV records and write raw tabular evidence. |
| 2 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 3 | <code>import re</code> | Import re to validate bridge names and run IDs with regular expressions. |
| 4 | <code>import threading</code> | Import threading to run resource sampling in the background and coordinate stop events/writer locks. |
| 5 | <code>import uuid</code> | Import uuid to create unique identifiers for evidence directories. |
| 6 | <code>from datetime import UTC, datetime</code> | Import UTC, datetime from datetime. This makes the named library helpers available without the module prefix. |
| 7 | <code>from importlib.metadata import PackageNotFoundError, version</code> | Import PackageNotFoundError, version from importlib.metadata. This makes the named library helpers available without the module prefix. |
| 8 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 9 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 10 | <code>RUN_ID = re.compile(r&quot;^[0-9a-f]{32}$&quot;)</code> | Set RUN_ID. Call re.compile with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 13 | <code>def utc_now():</code> | Define function/method utc_now. Returns an ISO 8601 UTC time string for run bookkeeping, independent of client timezone. |
| 14 | <code>    return datetime.now(UTC).isoformat()</code> | Return to the caller: Call datetime.now(UTC).isoformat with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 15 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 16 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 17 | <code>def dependency_versions():</code> | Define function/method dependency_versions. Reads installed package versions for reproducibility; missing distributions are recorded explicitly. |
| 18 | <code>    result = {}</code> | Set result. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 19 | <code>    for name in (&quot;m3-sdn&quot;, &quot;river&quot;, &quot;numpy&quot;, &quot;psutil&quot;, &quot;dpkt&quot;):</code> | Loop: assign each item from ('m3-sdn', 'river', 'numpy', 'psutil', 'dpkt') into name, then execute the indented body. |
| 20 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 21 | <code>            result[name] = version(name)</code> | Set result[name]. Call version with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 22 | <code>        except PackageNotFoundError:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 23 | <code>            result[name] = &quot;not installed&quot;</code> | Set result[name]. Use the literal 'not installed'. |
| 24 | <code>    return result</code> | Return to the caller: Read result from the current function/object state. |
| 25 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 26 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 27 | <code>def atomic_json(path: Path, value):</code> | Define function/method atomic_json. Writes valid JSON to a sibling temporary path, then replaces the visible target so readers avoid a partially written JSON document. |
| 28 | <code>    temporary = path.with_suffix(path.suffix + &quot;.tmp&quot;)</code> | Set temporary. Call path.with_suffix with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 29 | <code>    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding=&quot;utf-8&quot;)</code> | Call temporary.write_text with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>    temporary.replace(path)</code> | Replace the visible summary only after the temporary JSON is fully written; readers see an old or new complete document. |
| 31 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 32 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 33 | <code>class RunWriter:</code> | Define class RunWriter. Groups the following statements into a named reusable operation. |
| 34 | <code>    def __init__(self, config, source, provenance=None):</code> | Define function/method __init__. Creates a UUID-named run directory, raw CSV files with fixed schemas, and an initial running summary with model/config/data provenance. |
| 35 | <code>        self.run_id = uuid.uuid4().hex</code> | Set self.run_id. Read uuid.uuid4().hex from the current function/object state. |
| 36 | <code>        self.path = Path(config.output_root) / self.run_id</code> | Set self.path. Calculate Path(config.output_root) / self.run_id using divide; / returns a floating-point ratio and // floors division where used. |
| 37 | <code>        self.path.mkdir(parents=True, exist_ok=False)</code> | Create the new UUID directory and refuse an already existing one, avoiding accidental run overwrite. |
| 38 | <code>        self.lock = threading.Lock()</code> | Set self.lock. Call threading.Lock with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 39 | <code>        self.streams = {}</code> | Set self.streams. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 40 | <code>        self.writers = {}</code> | Set self.writers. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 41 | <code>        fields = {</code> | Set fields. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 42 | <code>            &quot;predictions&quot;: [</code> | Field predictions: Named entry in the surrounding dictionary. Its value is [; consumers access it by this key. |
| 43 | <code>                &quot;index&quot;,</code> | Literal component of the surrounding statement: 'index'. Its role is determined by the field/call immediately above. |
| 44 | <code>                &quot;time&quot;,</code> | Literal component of the surrounding statement: 'time'. Its role is determined by the field/call immediately above. |
| 45 | <code>                &quot;y_true&quot;,</code> | Literal component of the surrounding statement: 'y_true'. Its role is determined by the field/call immediately above. |
| 46 | <code>                &quot;y_pred&quot;,</code> | Literal component of the surrounding statement: 'y_pred'. Its role is determined by the field/call immediately above. |
| 47 | <code>                &quot;score&quot;,</code> | Literal component of the surrounding statement: 'score'. Its role is determined by the field/call immediately above. |
| 48 | <code>                &quot;latency_ms&quot;,</code> | Literal component of the surrounding statement: 'latency_ms'. Its role is determined by the field/call immediately above. |
| 49 | <code>                &quot;phase&quot;,</code> | Literal component of the surrounding statement: 'phase'. Its role is determined by the field/call immediately above. |
| 50 | <code>                &quot;attack_family&quot;,</code> | Literal component of the surrounding statement: 'attack_family'. Its role is determined by the field/call immediately above. |
| 51 | <code>                &quot;sampled_packets&quot;,</code> | Literal component of the surrounding statement: 'sampled_packets'. Its role is determined by the field/call immediately above. |
| 52 | <code>                &quot;observed_time&quot;,</code> | Literal component of the surrounding statement: 'observed_time'. Its role is determined by the field/call immediately above. |
| 53 | <code>                &quot;ground_truth_packets&quot;,</code> | Literal component of the surrounding statement: 'ground_truth_packets'. Its role is determined by the field/call immediately above. |
| 54 | <code>            ],</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 55 | <code>            &quot;resources&quot;: [</code> | Field resources: Named entry in the surrounding dictionary. Its value is [; consumers access it by this key. |
| 56 | <code>                &quot;time&quot;,</code> | Literal component of the surrounding statement: 'time'. Its role is determined by the field/call immediately above. |
| 57 | <code>                &quot;cpu_percent&quot;,</code> | Literal component of the surrounding statement: 'cpu_percent'. Its role is determined by the field/call immediately above. |
| 58 | <code>                &quot;rss_mb&quot;,</code> | Literal component of the surrounding statement: 'rss_mb'. Its role is determined by the field/call immediately above. |
| 59 | <code>                &quot;telemetry_bytes&quot;,</code> | Literal component of the surrounding statement: 'telemetry_bytes'. Its role is determined by the field/call immediately above. |
| 60 | <code>                &quot;controller_cpu_percent&quot;,</code> | Literal component of the surrounding statement: 'controller_cpu_percent'. Its role is determined by the field/call immediately above. |
| 61 | <code>                &quot;flow_table_entries&quot;,</code> | Literal component of the surrounding statement: 'flow_table_entries'. Its role is determined by the field/call immediately above. |
| 62 | <code>            ],</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 63 | <code>            &quot;drift&quot;: [&quot;time&quot;, &quot;index&quot;, &quot;event&quot;, &quot;detector&quot;],</code> | Field drift: Named entry in the surrounding dictionary. Its value is ["time", "index", "event", "detector"]; consumers access it by this key. |
| 64 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 65 | <code>        for name, columns in fields.items():</code> | Loop: assign each item from fields.items() into (name, columns), then execute the indented body. |
| 66 | <code>            stream = (self.path / f&quot;{name}.csv&quot;).open(&quot;w&quot;, newline=&quot;&quot;, encoding=&quot;utf-8&quot;)</code> | Set stream. Open the named file using the shown text/binary mode and encoding: (self.path / f'{name}.csv').open('w', newline='', encoding='utf-8'). |
| 67 | <code>            writer = csv.DictWriter(stream, fieldnames=columns)</code> | Set writer. Call csv.DictWriter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 68 | <code>            writer.writeheader()</code> | Call writer.writeheader with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 69 | <code>            stream.flush()</code> | Publish CSV headers/rows from Python's output buffer promptly so readers can observe current evidence. |
| 70 | <code>            self.streams[name], self.writers[name] = stream, writer</code> | Set (self.streams[name], self.writers[name]). Bundle these values in a tuple: (stream, writer). |
| 71 | <code>        self.summary = {</code> | Set self.summary. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 72 | <code>            &quot;schema_version&quot;: 1,</code> | Field schema_version: Named entry in the surrounding dictionary. Its value is 1; consumers access it by this key. |
| 73 | <code>            &quot;run_id&quot;: self.run_id,</code> | Field run_id: Named entry in the surrounding dictionary. Its value is self.run_id; consumers access it by this key. |
| 74 | <code>            &quot;source&quot;: source,</code> | Field source: Evidence origin; fixture, live_sflow, and official_5g_nidd must not be treated as interchangeable validation. |
| 75 | <code>            &quot;mode&quot;: config.mode,</code> | Field mode: Selects csv_replay, pcap_replay, or live_sflow, which have different units, features and evidence strength. |
| 76 | <code>            &quot;status&quot;: &quot;running&quot;,</code> | Field status: Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 77 | <code>            &quot;sampling_rate&quot;: config.sampling_rate,</code> | Field sampling_rate: Inverse sampling probability N; allowed values are 1, 2, 5, 10, 20, 50. Offline uses Bernoulli draws with probability 1/N; it does not deterministically retain every Nth row. |
| 78 | <code>            &quot;seed&quot;: config.seed,</code> | Field seed: Seed for reproducible offline random selection and HAT randomness; live OVS sampling is not made deterministic by this Python seed. |
| 79 | <code>            &quot;scenario&quot;: config.scenario,</code> | Field scenario: Experiment category baseline/drift/unseen. Choosing drift alone does not change the data. unseen excludes SYNFlood warm-up observations. |
| 80 | <code>            &quot;unit&quot;: &quot;flow&quot; if config.mode == &quot;csv_replay&quot; else &quot;window&quot;,</code> | Field unit: Measurement units or observation unit; flow for CSV and window for packet/live replay. |
| 81 | <code>            &quot;feature_schema&quot;: &quot;flow-v1&quot; if config.mode == &quot;csv_replay&quot; else &quot;packet-window-v1&quot;,</code> | Field feature_schema: Separates flow-v1 from packet-window-v1 so incompatible input feature definitions remain visible. |
| 82 | <code>            &quot;created_at&quot;: utc_now(),</code> | Field created_at: Named entry in the surrounding dictionary. Its value is utc_now(); consumers access it by this key. |
| 83 | <code>            &quot;ended_at&quot;: None,</code> | Field ended_at: Named entry in the surrounding dictionary. Its value is None; consumers access it by this key. |
| 84 | <code>            &quot;counts&quot;: {</code> | Field counts: Named entry in the surrounding dictionary. Its value is {; consumers access it by this key. |
| 85 | <code>                key: 0</code> | Continuation of the statement above. Read key from the current function/object state. |
| 86 | <code>                for key in [&quot;input&quot;, &quot;sampled&quot;, &quot;evaluated&quot;, &quot;warmup&quot;, &quot;excluded&quot;, &quot;unlabeled&quot;]</code> | Continuation of the statement above. Build the ordered list below; order is retained. |
| 87 | <code>            },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 88 | <code>            &quot;metrics&quot;: {},</code> | Field metrics: Named entry in the surrounding dictionary. Its value is {}; consumers access it by this key. |
| 89 | <code>            &quot;drift_count&quot;: 0,</code> | Field drift_count: Named entry in the surrounding dictionary. Its value is 0; consumers access it by this key. |
| 90 | <code>            &quot;error&quot;: None,</code> | Field error: Named entry in the surrounding dictionary. Its value is None; consumers access it by this key. |
| 91 | <code>            &quot;config&quot;: config.to_dict(),</code> | Field config: Named entry in the surrounding dictionary. Its value is config.to_dict(); consumers access it by this key. |
| 92 | <code>            &quot;provenance&quot;: provenance,</code> | Field provenance: Named entry in the surrounding dictionary. Its value is provenance; consumers access it by this key. |
| 93 | <code>            &quot;model&quot;: {</code> | Field model: Saved model metadata or the wrapped River learner, depending on the surrounding object. |
| 94 | <code>                &quot;implementation&quot;: &quot;river.HoeffdingAdaptiveTreeClassifier&quot;,</code> | Field implementation: Named entry in the surrounding dictionary. Its value is "river.HoeffdingAdaptiveTreeClassifier"; consumers access it by this key. |
| 95 | <code>                &quot;version&quot;: &quot;0.1.0&quot;,</code> | Field version: Named entry in the surrounding dictionary. Its value is "0.1.0"; consumers access it by this key. |
| 96 | <code>                &quot;learning_policy&quot;: &quot;predict-log-score-learn; oracle labels after prediction&quot;,</code> | Field learning_policy: Named entry in the surrounding dictionary. Its value is "predict-log-score-learn; oracle labels after prediction"; consumers access it by this key. |
| 97 | <code>            },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 98 | <code>            &quot;dependencies&quot;: dependency_versions(),</code> | Field dependencies: Named entry in the surrounding dictionary. Its value is dependency_versions(); consumers access it by this key. |
| 99 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 100 | <code>        self.save()</code> | Call self.save with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 101 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 102 | <code>    def append(self, kind, row):</code> | Define function/method append. Uses a lock to append and immediately flush one raw CSV row; this is raw evidence, not dashboard formatting. |
| 103 | <code>        with self.lock:</code> | Enter managed resource/lock context self.lock. Exiting the block releases/closes it, including on exceptions. |
| 104 | <code>            self.writers[kind].writerow(row)</code> | Call self.writers[kind].writerow with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 105 | <code>            self.streams[kind].flush()</code> | Flush buffered output in self.streams[kind] so another reader can see the written bytes; this is not an fsync durability guarantee. |
| 106 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 107 | <code>    def save(self):</code> | Define function/method save. Uses the same lock to atomically replace the run JSON summary. |
| 108 | <code>        with self.lock:</code> | Enter managed resource/lock context self.lock. Exiting the block releases/closes it, including on exceptions. |
| 109 | <code>            atomic_json(self.path / &quot;run_summary.json&quot;, self.summary)</code> | Write JSON to a sibling temporary file then replace the target, avoiding partial JSON reads. |
| 110 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 111 | <code>    def finish(self, metrics, error=None):</code> | Define function/method finish. Marks status/error/end time, saves final metrics, then closes raw evidence streams. |
| 112 | <code>        self.summary.update(</code> | Call self.summary.update with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 113 | <code>            status=&quot;failed&quot; if error else &quot;completed&quot;,</code> | Keyword argument status for the call above. Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 114 | <code>            metrics=metrics,</code> | Keyword argument metrics for the call above. Pass the shown value metrics into that parameter. |
| 115 | <code>            error=str(error) if error else None,</code> | Keyword argument error for the call above. Pass the shown value str(error) if error else None into that parameter. |
| 116 | <code>            ended_at=utc_now(),</code> | Keyword argument ended_at for the call above. Pass the shown value utc_now() into that parameter. |
| 117 | <code>        )</code> | Close the call to self.summary.update begun above; this is punctuation, not a separate operation. |
| 118 | <code>        self.save()</code> | Call self.save with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 119 | <code>        with self.lock:</code> | Enter managed resource/lock context self.lock. Exiting the block releases/closes it, including on exceptions. |
| 120 | <code>            for stream in self.streams.values():</code> | Loop: assign each item from self.streams.values() into stream, then execute the indented body. |
| 121 | <code>                stream.close()</code> | Close stream and release its file/socket/plot resource. |
| 122 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 123 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 124 | <code>class RunRepository:</code> | Define class RunRepository. Groups the following statements into a named reusable operation. |
| 125 | <code>    def __init__(self, root):</code> | Define function/method __init__. Resolves the configured evidence root to an absolute filesystem location. |
| 126 | <code>        self.root = Path(root).resolve()</code> | Set self.root. Call Path(root).resolve with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 127 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 128 | <code>    def directory(self, run_id):</code> | Define function/method directory. Allows only a 32-character lowercase-hex run ID and a real nonsymlink run directory beneath the evidence root. |
| 129 | <code>        if not RUN_ID.fullmatch(run_id):</code> | Branch only if not RUN_ID.fullmatch(run_id) is true; otherwise skip this indented block or take its following elif/else. |
| 130 | <code>            raise FileNotFoundError(&quot;Invalid run ID&quot;)</code> | Raise FileNotFoundError('Invalid run ID') and stop this operation; the caller can record/report this invalid condition. |
| 131 | <code>        path = self.root / run_id</code> | Set path. Calculate self.root / run_id using divide; / returns a floating-point ratio and // floors division where used. |
| 132 | <code>        if path.is_symlink() or not path.is_dir():</code> | Branch only if path.is_symlink() or not path.is_dir() is true; otherwise skip this indented block or take its following elif/else. |
| 133 | <code>            raise FileNotFoundError(&quot;Run not found&quot;)</code> | Raise FileNotFoundError('Run not found') and stop this operation; the caller can record/report this invalid condition. |
| 134 | <code>        return path</code> | Return to the caller: Read path from the current function/object state. |
| 135 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 136 | <code>    def get(self, run_id):</code> | Define function/method get. Loads the chosen run_summary.json through the checked directory lookup. |
| 137 | <code>        return json.loads((self.directory(run_id) / &quot;run_summary.json&quot;).read_text(encoding=&quot;utf-8&quot;))</code> | Return to the caller: Call json.loads with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 138 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 139 | <code>    def list(self):</code> | Define function/method list. Finds valid readable run summaries and sorts newest first; absent roots return an empty list, in-progress unreadable files are skipped. |
| 140 | <code>        if not self.root.is_dir():</code> | Branch only if not self.root.is_dir() is true; otherwise skip this indented block or take its following elif/else. |
| 141 | <code>            return []</code> | Return to the caller: Build the ordered list below; order is retained. |
| 142 | <code>        result = []</code> | Set result. Build the ordered list below; order is retained. |
| 143 | <code>        for path in self.root.iterdir():</code> | Loop: assign each item from self.root.iterdir() into path, then execute the indented body. |
| 144 | <code>            if RUN_ID.fullmatch(path.name):</code> | Branch only if RUN_ID.fullmatch(path.name) is true; otherwise skip this indented block or take its following elif/else. |
| 145 | <code>                try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 146 | <code>                    result.append(self.get(path.name))</code> | Append self.get(path.name) to the end of result. |
| 147 | <code>                except (FileNotFoundError, json.JSONDecodeError):</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 148 | <code>                    continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 149 | <code>        return sorted(result, key=lambda run: run[&quot;created_at&quot;], reverse=True)</code> | Return to the caller: Create a sorted copy using the supplied ordering/key: sorted(result, key=lambda run: run['created_at'], reverse=True). |
| 150 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 151 | <code>    def series(self, run_id, limit=1000):</code> | Define function/method series. Counts CSV records, chooses evenly spaced row indices if needed, rereads selected rows and converts values for JSON using bounded result memory. |
| 152 | <code>        if limit &lt; 2:</code> | Branch only if limit < 2 is true; otherwise skip this indented block or take its following elif/else. |
| 153 | <code>            raise ValueError(&quot;Series limit must be at least two&quot;)</code> | Raise ValueError('Series limit must be at least two') and stop this operation; the caller can record/report this invalid condition. |
| 154 | <code>        result = {}</code> | Set result. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 155 | <code>        for name in [&quot;predictions&quot;, &quot;resources&quot;, &quot;drift&quot;]:</code> | Loop: assign each item from ['predictions', 'resources', 'drift'] into name, then execute the indented body. |
| 156 | <code>            rows = []</code> | Set rows. Build the ordered list below; order is retained. |
| 157 | <code>            path = self.directory(run_id) / f&quot;{name}.csv&quot;</code> | Set path. Calculate self.directory(run_id) / f'{name}.csv' using divide; / returns a floating-point ratio and // floors division where used. |
| 158 | <code>            # Count first, then parse only selected rows: bounded memory even for million-flow runs.</code> | Source comment: Count first, then parse only selected rows: bounded memory even for million-flow runs. This documents intent and does not execute. |
| 159 | <code>            with path.open(newline=&quot;&quot;, encoding=&quot;utf-8&quot;) as stream:</code> | Enter managed resource/lock context path.open(newline='', encoding='utf-8') as stream. Exiting the block releases/closes it, including on exceptions. |
| 160 | <code>                total = sum(1 for _ in csv.DictReader(stream))</code> | Set total. Add the values yielded by (1 for _ in csv.DictReader(stream)); booleans count as 1 for True and 0 for False. |
| 161 | <code>            selected = (</code> | Build a bounded set of evenly spread original row indices when the evidence is longer than the dashboard series limit. |
| 162 | <code>                {round(i * (total - 1) / (limit - 1)) for i in range(limit)}</code> | Continuation of the statement above. Choose {round(i * (total - 1) / (limit - 1)) for i in range(limit)} when total > limit is true; otherwise choose None. |
| 163 | <code>                if total &gt; limit</code> | Continuation of the statement above. Evaluate the comparison total > limit to True/False; comparisons may short-circuit. |
| 164 | <code>                else None</code> | Literal component of the surrounding statement: None. Its role is determined by the field/call immediately above. |
| 165 | <code>            )</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 166 | <code>            with path.open(newline=&quot;&quot;, encoding=&quot;utf-8&quot;) as stream:</code> | Enter managed resource/lock context path.open(newline='', encoding='utf-8') as stream. Exiting the block releases/closes it, including on exceptions. |
| 167 | <code>                for index, row in enumerate(csv.DictReader(stream)):</code> | Loop: assign each item from enumerate(csv.DictReader(stream)) into (index, row), then execute the indented body. |
| 168 | <code>                    if index &gt;= total or (selected is not None and index not in selected):</code> | Branch only if index >= total or (selected is not None and index not in selected) is true; otherwise skip this indented block or take its following elif/else. |
| 169 | <code>                        continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 170 | <code>                    if None in row or any(value is None for value in row.values()):</code> | Branch only if None in row or any((value is None for value in row.values())) is true; otherwise skip this indented block or take its following elif/else. |
| 171 | <code>                        continue  # A live writer may be between writes; retry on the next poll.</code> | Skip the rest of this loop iteration and move to the next item. |
| 172 | <code>                    for key, value in row.items():</code> | Loop: assign each item from row.items() into (key, value), then execute the indented body. |
| 173 | <code>                        if value == &quot;&quot;:</code> | Branch only if value == '' is true; otherwise skip this indented block or take its following elif/else. |
| 174 | <code>                            row[key] = None</code> | Set row[key]. Use the literal None (None means unavailable/not set). |
| 175 | <code>                        elif key not in {&quot;phase&quot;, &quot;attack_family&quot;, &quot;event&quot;, &quot;detector&quot;}:</code> | Branch only if key not in {'phase', 'attack_family', 'event', 'detector'} is true; otherwise skip this indented block or take its following elif/else. |
| 176 | <code>                            try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 177 | <code>                                row[key] = float(value)</code> | Set row[key]. Convert value to float. |
| 178 | <code>                            except ValueError:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 179 | <code>                                pass</code> | Empty body placeholder; this subclass/block adds no extra executable behavior. |
| 180 | <code>                    rows.append(row)</code> | Append row to the end of rows. |
| 181 | <code>            result[name] = rows</code> | Set result[name]. Read rows from the current function/object state. |
| 182 | <code>        return result</code> | Return to the caller: Read result from the current function/object state. |

## src/m3/analysis.py

**Comparable-trial aggregation and Pareto charts.** Groups matching evidence/settings, summarizes repeated trials, and plots quality/cost. It filters fixture and incomplete runs from aggregation while preserving failed-run information. Pareto-efficient means no other point is at least as accurate and at most as costly with one strict improvement. This module does not automatically choose a knee point or prove the required full experiment matrix is complete.

Snapshot: 234 lines; SHA256 `b6117bd3a5df59fb84a18684c7a8022227921d4ce7bbb2debde89005bd361f2b`.

### Named operations

- `comparison_key` (L22): Serializes source/mode/unit/scenario/schema/checksum/model settings into a stable key so incompatible runs do not get averaged together.
- `pareto` (L37): Keeps a point unless another has at least its F1 and no more cost, with one strict improvement. Exact ties are both retained.
- `aggregate` (L51): Groups completed nonfixture runs by comparison key and N, calculates metric mean/sample standard deviation/min/max, and retains reasons and actual valid counts.
- `analyse` (L88): Loads runs, saves aggregates and failures, produces headless plots, and exports measured-bandwidth Pareto fronts. No automatic knee-point selector is implemented here.

A sampling sweep is not automatically a valid finished study: inspect actual trial counts, distinct seeds, source, settings and scenarios. The key does not include every possible label annotation or software revision, so verify those manually before comparing. `front` is the set of nondominated points; selecting an operational knee still needs an agreed rule and independent verification.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;Aggregate only comparable trials; never conflate offline proxies with live cost.&quot;&quot;&quot;</code> | Documentation string: Aggregate only comparable trials; never conflate offline proxies with live cost. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>import csv</code> | Import csv to stream CSV records and write raw tabular evidence. |
| 4 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 5 | <code>from collections import defaultdict</code> | Import defaultdict from collections. This makes the named library helpers available without the module prefix. |
| 6 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 7 | <code>from statistics import mean, stdev</code> | Import mean, stdev from statistics. This makes the named library helpers available without the module prefix. |
| 8 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 9 | <code>from m3.store import RunRepository, atomic_json</code> | Import RunRepository, atomic_json from m3.store. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <code>SIGNATURE_KEYS = (</code> | Set SIGNATURE_KEYS. Bundle these values in a tuple: ('threshold', 'grace_period', 'drift_delta', 'window_seconds', 'warmup_records', 'warmup_seconds', 'max_records'). |
| 12 | <code>    &quot;threshold&quot;,</code> | Literal component of the surrounding statement: 'threshold'. Its role is determined by the field/call immediately above. |
| 13 | <code>    &quot;grace_period&quot;,</code> | Literal component of the surrounding statement: 'grace_period'. Its role is determined by the field/call immediately above. |
| 14 | <code>    &quot;drift_delta&quot;,</code> | Literal component of the surrounding statement: 'drift_delta'. Its role is determined by the field/call immediately above. |
| 15 | <code>    &quot;window_seconds&quot;,</code> | Literal component of the surrounding statement: 'window_seconds'. Its role is determined by the field/call immediately above. |
| 16 | <code>    &quot;warmup_records&quot;,</code> | Literal component of the surrounding statement: 'warmup_records'. Its role is determined by the field/call immediately above. |
| 17 | <code>    &quot;warmup_seconds&quot;,</code> | Literal component of the surrounding statement: 'warmup_seconds'. Its role is determined by the field/call immediately above. |
| 18 | <code>    &quot;max_records&quot;,</code> | Literal component of the surrounding statement: 'max_records'. Its role is determined by the field/call immediately above. |
| 19 | <code>)</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 20 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 21 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 22 | <code>def comparison_key(run):</code> | Define function/method comparison_key. Serializes source/mode/unit/scenario/schema/checksum/model settings into a stable key so incompatible runs do not get averaged together. |
| 23 | <code>    return json.dumps(</code> | Return to the caller: Call json.dumps with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 24 | <code>        {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 25 | <code>            &quot;source&quot;: run[&quot;source&quot;],</code> | Field source: Evidence origin; fixture, live_sflow, and official_5g_nidd must not be treated as interchangeable validation. |
| 26 | <code>            &quot;mode&quot;: run[&quot;mode&quot;],</code> | Field mode: Selects csv_replay, pcap_replay, or live_sflow, which have different units, features and evidence strength. |
| 27 | <code>            &quot;unit&quot;: run[&quot;unit&quot;],</code> | Field unit: Measurement units or observation unit; flow for CSV and window for packet/live replay. |
| 28 | <code>            &quot;scenario&quot;: run[&quot;scenario&quot;],</code> | Field scenario: Experiment category baseline/drift/unseen. Choosing drift alone does not change the data. unseen excludes SYNFlood warm-up observations. |
| 29 | <code>            &quot;feature_schema&quot;: run.get(&quot;feature_schema&quot;),</code> | Field feature_schema: Separates flow-v1 from packet-window-v1 so incompatible input feature definitions remain visible. |
| 30 | <code>            &quot;checksum&quot;: (run.get(&quot;provenance&quot;) or {}).get(&quot;sha256&quot;),</code> | Field checksum: Named entry in the surrounding dictionary. Its value is (run.get("provenance") or {}).get("sha256"); consumers access it by this key. |
| 31 | <code>            &quot;settings&quot;: {k: run[&quot;config&quot;].get(k) for k in SIGNATURE_KEYS},</code> | Field settings: Named entry in the surrounding dictionary. Its value is {k: run["config"].get(k) for k in SIGNATURE_KEYS}; consumers access it by this key. |
| 32 | <code>        },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 33 | <code>        sort_keys=True,</code> | Keyword argument sort_keys for the call above. Pass the shown value True into that parameter. |
| 34 | <code>    )</code> | Close the call to json.dumps begun above; this is punctuation, not a separate operation. |
| 35 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 36 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 37 | <code>def pareto(points):</code> | Define function/method pareto. Keeps a point unless another has at least its F1 and no more cost, with one strict improvement. Exact ties are both retained. |
| 38 | <code>    &quot;&quot;&quot;Maximise F1 and minimise measured bandwidth. Equality preserves ties.&quot;&quot;&quot;</code> | Documentation string: Maximise F1 and minimise measured bandwidth. Equality preserves ties. It explains the module/class/function; it is not an extra experiment step. |
| 39 | <code>    return [</code> | Return to the caller: Build a collection by iterating the for clauses and retaining entries passing the if clauses: [point for point in points if not any((other['f1'] >= point['f1'] and other['cost'] <= point['cost'] and (other['f1'] > point['f1'] or other['cost'] < point['cost']) for other in points))]. |
| 40 | <code>        point</code> | Continuation of the statement above. Read point from the current function/object state. |
| 41 | <code>        for point in points</code> | Continuation of the statement above. Read points from the current function/object state. |
| 42 | <code>        if not any(</code> | Continuation of the statement above. Read not any((other['f1'] >= point['f1'] and other['cost'] <= point['cost'] and (other['f1'] > point['f1'] or other['cost'] < point['cost']) for other in points)) from the current function/object state. |
| 43 | <code>            other[&quot;f1&quot;] &gt;= point[&quot;f1&quot;]</code> | Continuation of the statement above. Evaluate other['f1'] >= point['f1'] and other['cost'] <= point['cost'] and (other['f1'] > point['f1'] or other['cost'] < point['cost']) left to right with short-circuit and. |
| 44 | <code>            and other[&quot;cost&quot;] &lt;= point[&quot;cost&quot;]</code> | Continuation of the statement above. Evaluate the comparison other['cost'] <= point['cost'] to True/False; comparisons may short-circuit. |
| 45 | <code>            and (other[&quot;f1&quot;] &gt; point[&quot;f1&quot;] or other[&quot;cost&quot;] &lt; point[&quot;cost&quot;])</code> | Continuation of the statement above. Evaluate other['f1'] > point['f1'] or other['cost'] < point['cost'] left to right with short-circuit or. |
| 46 | <code>            for other in points</code> | Continuation of the statement above. Read points from the current function/object state. |
| 47 | <code>        )</code> | Close the call to any begun above; this is punctuation, not a separate operation. |
| 48 | <code>    ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 49 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 50 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 51 | <code>def aggregate(runs):</code> | Define function/method aggregate. Groups completed nonfixture runs by comparison key and N, calculates metric mean/sample standard deviation/min/max, and retains reasons and actual valid counts. |
| 52 | <code>    grouped = defaultdict(list)</code> | Set grouped. Call defaultdict with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 53 | <code>    for run in runs:</code> | Loop: assign each item from runs into run, then execute the indented body. |
| 54 | <code>        if run[&quot;status&quot;] == &quot;completed&quot; and run[&quot;source&quot;] != &quot;fixture&quot;:</code> | Branch only if run['status'] == 'completed' and run['source'] != 'fixture' is true; otherwise skip this indented block or take its following elif/else. |
| 55 | <code>            grouped[(comparison_key(run), run[&quot;sampling_rate&quot;])].append(run)</code> | Append run to the end of grouped[comparison_key(run), run['sampling_rate']]. |
| 56 | <code>    rows = []</code> | Set rows. Build the ordered list below; order is retained. |
| 57 | <code>    for (key, rate), group in sorted(grouped.items()):</code> | Loop: assign each item from sorted(grouped.items()) into ((key, rate), group), then execute the indented body. |
| 58 | <code>        row = {</code> | Set row. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 59 | <code>            &quot;comparison_group&quot;: key,</code> | Field comparison_group: Named entry in the surrounding dictionary. Its value is key; consumers access it by this key. |
| 60 | <code>            &quot;sampling_rate&quot;: rate,</code> | Field sampling_rate: Inverse sampling probability N; allowed values are 1, 2, 5, 10, 20, 50. Offline uses Bernoulli draws with probability 1/N; it does not deterministically retain every Nth row. |
| 61 | <code>            &quot;run_ids&quot;: [r[&quot;run_id&quot;] for r in group],</code> | Field run_ids: Named entry in the surrounding dictionary. Its value is [r["run_id"] for r in group]; consumers access it by this key. |
| 62 | <code>            &quot;trials&quot;: len(group),</code> | Field trials: Named entry in the surrounding dictionary. Its value is len(group); consumers access it by this key. |
| 63 | <code>            &quot;distinct_seeds&quot;: len({r[&quot;seed&quot;] for r in group}),</code> | Field distinct_seeds: Named entry in the surrounding dictionary. Its value is len({r["seed"] for r in group}); consumers access it by this key. |
| 64 | <code>            &quot;metrics&quot;: {},</code> | Field metrics: Named entry in the surrounding dictionary. Its value is {}; consumers access it by this key. |
| 65 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 66 | <code>        names = sorted({name for r in group for name in r[&quot;metrics&quot;]})</code> | Set names. Create a sorted copy using the supplied ordering/key: sorted({name for r in group for name in r['metrics']}). |
| 67 | <code>        for name in names:</code> | Loop: assign each item from names into name, then execute the indented body. |
| 68 | <code>            metrics = [r[&quot;metrics&quot;].get(name, {}) for r in group]</code> | Set metrics. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [r['metrics'].get(name, {}) for r in group]. |
| 69 | <code>            values = [m[&quot;value&quot;] for m in metrics if m.get(&quot;value&quot;) is not None]</code> | Set values. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [m['value'] for m in metrics if m.get('value') is not None]. |
| 70 | <code>            signatures = {</code> | Set signatures. Build a collection by iterating the for clauses and retaining entries passing the if clauses: {(m.get('unit'), m.get('status')) for m in metrics if m.get('value') is not None}. |
| 71 | <code>                (m.get(&quot;unit&quot;), m.get(&quot;status&quot;)) for m in metrics if m.get(&quot;value&quot;) is not None</code> | Continuation of the statement above. Bundle these values in a tuple: (m.get('unit'), m.get('status')). |
| 72 | <code>            }</code> | Close the multiline statement begun above; this is punctuation, not a separate operation. |
| 73 | <code>            compatible = len(signatures) == 1</code> | Set compatible. Evaluate the comparison len(signatures) == 1 to True/False; comparisons may short-circuit. |
| 74 | <code>            row[&quot;metrics&quot;][name] = {</code> | Set row['metrics'][name]. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 75 | <code>                &quot;mean&quot;: mean(values) if values and compatible else None,</code> | Field mean: Named entry in the surrounding dictionary. Its value is mean(values) if values and compatible else None; consumers access it by this key. |
| 76 | <code>                &quot;std&quot;: stdev(values) if len(values) &gt; 1 and compatible else None,</code> | Field std: Named entry in the surrounding dictionary. Its value is stdev(values) if len(values) > 1 and compatible else None; consumers access it by this key. |
| 77 | <code>                &quot;min&quot;: min(values) if values and compatible else None,</code> | Field min: Named entry in the surrounding dictionary. Its value is min(values) if values and compatible else None; consumers access it by this key. |
| 78 | <code>                &quot;max&quot;: max(values) if values and compatible else None,</code> | Field max: Named entry in the surrounding dictionary. Its value is max(values) if values and compatible else None; consumers access it by this key. |
| 79 | <code>                &quot;n&quot;: len(values),</code> | Field n: Named entry in the surrounding dictionary. Its value is len(values); consumers access it by this key. |
| 80 | <code>                &quot;unit&quot;: next(iter(signatures))[0] if compatible else None,</code> | Field unit: Measurement units or observation unit; flow for CSV and window for packet/live replay. |
| 81 | <code>                &quot;status&quot;: next(iter(signatures))[1] if compatible else &quot;unavailable&quot;,</code> | Field status: Evidence status measured/estimated/unavailable, or run status running/completed/failed, according to enclosing object. |
| 82 | <code>                &quot;reasons&quot;: sorted({m.get(&quot;reason&quot;) for m in metrics if m.get(&quot;reason&quot;)}),</code> | Field reasons: Named entry in the surrounding dictionary. Its value is sorted({m.get("reason") for m in metrics if m.get("reason")}); consumers access it by this key. |
| 83 | <code>            }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 84 | <code>        rows.append(row)</code> | Append row to the end of rows. |
| 85 | <code>    return rows</code> | Return to the caller: Read rows from the current function/object state. |
| 86 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 87 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 88 | <code>def analyse(root, output):</code> | Define function/method analyse. Loads runs, saves aggregates and failures, produces headless plots, and exports measured-bandwidth Pareto fronts. No automatic knee-point selector is implemented here. |
| 89 | <code>    output = Path(output)</code> | Set output. Construct a new Path using output. |
| 90 | <code>    output.mkdir(parents=True, exist_ok=True)</code> | Create the output directory with the specified parent/existence options: output.mkdir(parents=True, exist_ok=True). |
| 91 | <code>    runs = RunRepository(root).list()</code> | Set runs. Call RunRepository(root).list with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 92 | <code>    rows = aggregate(runs)</code> | Set rows. Call aggregate with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 93 | <code>    atomic_json(</code> | Write JSON to a sibling temporary file then replace the target, avoiding partial JSON reads. |
| 94 | <code>        output / &quot;aggregated_metrics.json&quot;,</code> | Continuation of the statement above. Calculate output / 'aggregated_metrics.json' using divide; / returns a floating-point ratio and // floors division where used. |
| 95 | <code>        {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 96 | <code>            &quot;groups&quot;: rows,</code> | Field groups: Named entry in the surrounding dictionary. Its value is rows; consumers access it by this key. |
| 97 | <code>            &quot;failed_runs&quot;: [</code> | Field failed_runs: Named entry in the surrounding dictionary. Its value is [; consumers access it by this key. |
| 98 | <code>                {&quot;run_id&quot;: r[&quot;run_id&quot;], &quot;error&quot;: r[&quot;error&quot;]}</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 99 | <code>                for r in runs</code> | Continuation of the statement above. Read runs from the current function/object state. |
| 100 | <code>                if r[&quot;status&quot;] == &quot;failed&quot;</code> | Continuation of the statement above. Evaluate the comparison r['status'] == 'failed' to True/False; comparisons may short-circuit. |
| 101 | <code>            ],</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 102 | <code>            &quot;notes&quot;: [</code> | Field notes: Named entry in the surrounding dictionary. Its value is [; consumers access it by this key. |
| 103 | <code>                &quot;Standard deviation uses ddof=1; n&lt;2 yields null.&quot;,</code> | Literal component of the surrounding statement: 'Standard deviation uses ddof=1; n<2 yields null.'. Its role is determined by the field/call immediately above. |
| 104 | <code>                &quot;Three distinct seeds are required per N; incomplete groups remain visible.&quot;,</code> | Literal component of the surrounding statement: 'Three distinct seeds are required per N; incomplete groups remain visible.'. Its role is determined by the field/call immediately above. |
| 105 | <code>            ],</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 106 | <code>        },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 107 | <code>    )</code> | Close the call to atomic_json begun above; this is punctuation, not a separate operation. |
| 108 | <code>    with (output / &quot;aggregated_metrics.csv&quot;).open(&quot;w&quot;, newline=&quot;&quot;, encoding=&quot;utf-8&quot;) as stream:</code> | Enter managed resource/lock context (output / 'aggregated_metrics.csv').open('w', newline='', encoding='utf-8') as stream. Exiting the block releases/closes it, including on exceptions. |
| 109 | <code>        writer = csv.writer(stream)</code> | Set writer. Call csv.writer with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 110 | <code>        writer.writerow(</code> | Call writer.writerow with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 111 | <code>            [</code> | Continuation of the statement above. Build the ordered list below; order is retained. |
| 112 | <code>                &quot;comparison_group&quot;,</code> | Literal component of the surrounding statement: 'comparison_group'. Its role is determined by the field/call immediately above. |
| 113 | <code>                &quot;N&quot;,</code> | Literal component of the surrounding statement: 'N'. Its role is determined by the field/call immediately above. |
| 114 | <code>                &quot;trials&quot;,</code> | Literal component of the surrounding statement: 'trials'. Its role is determined by the field/call immediately above. |
| 115 | <code>                &quot;distinct_seeds&quot;,</code> | Literal component of the surrounding statement: 'distinct_seeds'. Its role is determined by the field/call immediately above. |
| 116 | <code>                &quot;metric&quot;,</code> | Literal component of the surrounding statement: 'metric'. Its role is determined by the field/call immediately above. |
| 117 | <code>                &quot;mean&quot;,</code> | Literal component of the surrounding statement: 'mean'. Its role is determined by the field/call immediately above. |
| 118 | <code>                &quot;std&quot;,</code> | Literal component of the surrounding statement: 'std'. Its role is determined by the field/call immediately above. |
| 119 | <code>                &quot;n&quot;,</code> | Literal component of the surrounding statement: 'n'. Its role is determined by the field/call immediately above. |
| 120 | <code>                &quot;unit&quot;,</code> | Literal component of the surrounding statement: 'unit'. Its role is determined by the field/call immediately above. |
| 121 | <code>                &quot;status&quot;,</code> | Literal component of the surrounding statement: 'status'. Its role is determined by the field/call immediately above. |
| 122 | <code>            ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 123 | <code>        )</code> | Close the call to writer.writerow begun above; this is punctuation, not a separate operation. |
| 124 | <code>        for row in rows:</code> | Loop: assign each item from rows into row, then execute the indented body. |
| 125 | <code>            for name, metric in row[&quot;metrics&quot;].items():</code> | Loop: assign each item from row['metrics'].items() into (name, metric), then execute the indented body. |
| 126 | <code>                writer.writerow(</code> | Call writer.writerow with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 127 | <code>                    [</code> | Continuation of the statement above. Build the ordered list below; order is retained. |
| 128 | <code>                        row[&quot;comparison_group&quot;],</code> | Continuation of the statement above. Read row['comparison_group'] from the current function/object state. |
| 129 | <code>                        row[&quot;sampling_rate&quot;],</code> | Continuation of the statement above. Read row['sampling_rate'] from the current function/object state. |
| 130 | <code>                        row[&quot;trials&quot;],</code> | Continuation of the statement above. Read row['trials'] from the current function/object state. |
| 131 | <code>                        row[&quot;distinct_seeds&quot;],</code> | Continuation of the statement above. Read row['distinct_seeds'] from the current function/object state. |
| 132 | <code>                        name,</code> | Continuation of the statement above. Read name from the current function/object state. |
| 133 | <code>                        metric[&quot;mean&quot;],</code> | Continuation of the statement above. Read metric['mean'] from the current function/object state. |
| 134 | <code>                        metric[&quot;std&quot;],</code> | Continuation of the statement above. Read metric['std'] from the current function/object state. |
| 135 | <code>                        metric[&quot;n&quot;],</code> | Continuation of the statement above. Read metric['n'] from the current function/object state. |
| 136 | <code>                        metric[&quot;unit&quot;],</code> | Continuation of the statement above. Read metric['unit'] from the current function/object state. |
| 137 | <code>                        metric[&quot;status&quot;],</code> | Continuation of the statement above. Read metric['status'] from the current function/object state. |
| 138 | <code>                    ]</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 139 | <code>                )</code> | Close the call to writer.writerow begun above; this is punctuation, not a separate operation. |
| 140 | <code>    charts = []</code> | Set charts. Build the ordered list below; order is retained. |
| 141 | <code>    by_group = defaultdict(list)</code> | Set by_group. Call defaultdict with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 142 | <code>    for row in rows:</code> | Loop: assign each item from rows into row, then execute the indented body. |
| 143 | <code>        by_group[row[&quot;comparison_group&quot;]].append(row)</code> | Append row to the end of by_group[row['comparison_group']]. |
| 144 | <code>    import matplotlib</code> | Import matplotlib to render saved scientific charts without a desktop display. |
| 145 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 146 | <code>    matplotlib.use(&quot;Agg&quot;)</code> | Select the noninteractive Agg rendering backend before importing pyplot. |
| 147 | <code>    import matplotlib.pyplot as plt</code> | Import matplotlib.pyplot as plt to use its functions/classes in this module. |
| 148 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 149 | <code>    fronts = []</code> | Set fronts. Build the ordered list below; order is retained. |
| 150 | <code>    for index, (key, group) in enumerate(by_group.items()):</code> | Loop: assign each item from enumerate(by_group.items()) into (index, (key, group)), then execute the indented body. |
| 151 | <code>        for name in (&quot;f1&quot;, &quot;recall&quot;, &quot;cpu_percent_mean&quot;, &quot;telemetry_bandwidth_kbps&quot;):</code> | Loop: assign each item from ('f1', 'recall', 'cpu_percent_mean', 'telemetry_bandwidth_kbps') into name, then execute the indented body. |
| 152 | <code>            values = [(r[&quot;sampling_rate&quot;], r[&quot;metrics&quot;].get(name, {})) for r in group]</code> | Set values. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [(r['sampling_rate'], r['metrics'].get(name, {})) for r in group]. |
| 153 | <code>            values = [(n, m) for n, m in values if m.get(&quot;mean&quot;) is not None]</code> | Set values. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [(n, m) for n, m in values if m.get('mean') is not None]. |
| 154 | <code>            if not values:</code> | Branch only if not values is true; otherwise skip this indented block or take its following elif/else. |
| 155 | <code>                continue</code> | Skip the rest of this loop iteration and move to the next item. |
| 156 | <code>            fig, ax = plt.subplots(figsize=(7, 4))</code> | Set (fig, ax). Call plt.subplots with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 157 | <code>            ax.errorbar(</code> | Call ax.errorbar with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 158 | <code>                [n for n, _ in values],</code> | Continuation of the statement above. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [n for n, _ in values]. |
| 159 | <code>                [m[&quot;mean&quot;] for _, m in values],</code> | Continuation of the statement above. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [m['mean'] for _, m in values]. |
| 160 | <code>                yerr=[m[&quot;std&quot;] or 0 for _, m in values],</code> | Keyword argument yerr for the call above. Pass the shown value [m["std"] or 0 for _, m in values] into that parameter. |
| 161 | <code>                marker=&quot;o&quot;,</code> | Keyword argument marker for the call above. Pass the shown value "o" into that parameter. |
| 162 | <code>                capsize=3,</code> | Keyword argument capsize for the call above. Pass the shown value 3 into that parameter. |
| 163 | <code>            )</code> | Close the call to ax.errorbar begun above; this is punctuation, not a separate operation. |
| 164 | <code>            ax.set(</code> | Call ax.set with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 165 | <code>                xlabel=&quot;Sampling N&quot;,</code> | Keyword argument xlabel for the call above. Pass the shown value "Sampling N" into that parameter. |
| 166 | <code>                ylabel=f&quot;{name} ({values[0][1][&#x27;unit&#x27;]})&quot;,</code> | Keyword argument ylabel for the call above. Pass the shown value f"{name} ({values[0][1]['unit']})" into that parameter. |
| 167 | <code>                title=f&quot;M3 {name} - {values[0][1][&#x27;status&#x27;]} / group {index + 1}&quot;,</code> | Keyword argument title for the call above. Pass the shown value f"M3 {name} - {values[0][1]['status']} / group {index + 1}" into that parameter. |
| 168 | <code>            )</code> | Close the call to ax.set begun above; this is punctuation, not a separate operation. |
| 169 | <code>            ax.grid(alpha=0.2)</code> | Call ax.grid with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 170 | <code>            fig.tight_layout()</code> | Call fig.tight_layout with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 171 | <code>            path = output / f&quot;group_{index + 1}_{name}.png&quot;</code> | Set path. Calculate output / f'group_{index + 1}_{name}.png' using divide; / returns a floating-point ratio and // floors division where used. |
| 172 | <code>            fig.savefig(path, dpi=160)</code> | Call fig.savefig with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 173 | <code>            plt.close(fig)</code> | Close plt and release its file/socket/plot resource. |
| 174 | <code>            charts.append(str(path))</code> | Append str(path) to the end of charts. |
| 175 | <code>        points = []</code> | Set points. Build the ordered list below; order is retained. |
| 176 | <code>        for row in group:</code> | Loop: assign each item from group into row, then execute the indented body. |
| 177 | <code>            quality, cost = (</code> | Set (quality, cost). Bundle these values in a tuple: (row['metrics'].get('f1', {}), row['metrics'].get('telemetry_bandwidth_kbps', {})). |
| 178 | <code>                row[&quot;metrics&quot;].get(&quot;f1&quot;, {}),</code> | Continuation of the statement above. Look up 'f1' in row['metrics']; use the explicit default if supplied, otherwise None. |
| 179 | <code>                row[&quot;metrics&quot;].get(&quot;telemetry_bandwidth_kbps&quot;, {}),</code> | Continuation of the statement above. Look up 'telemetry_bandwidth_kbps' in row['metrics']; use the explicit default if supplied, otherwise None. |
| 180 | <code>            )</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 181 | <code>            if (</code> | Branch only if quality.get('mean') is not None and cost.get('mean') is not None and (cost.get('status') == 'measured') is true; otherwise skip this indented block or take its following elif/else. |
| 182 | <code>                quality.get(&quot;mean&quot;) is not None</code> | Continuation of the statement above. Evaluate quality.get('mean') is not None and cost.get('mean') is not None and (cost.get('status') == 'measured') left to right with short-circuit and. |
| 183 | <code>                and cost.get(&quot;mean&quot;) is not None</code> | Continuation of the statement above. Evaluate the comparison cost.get('mean') is not None to True/False; comparisons may short-circuit. |
| 184 | <code>                and cost.get(&quot;status&quot;) == &quot;measured&quot;</code> | Continuation of the statement above. Evaluate the comparison cost.get('status') == 'measured' to True/False; comparisons may short-circuit. |
| 185 | <code>            ):</code> | Continue the surrounding analyse statement: ):. The indentation and open brackets connect it to the operation above. |
| 186 | <code>                points.append(</code> | Append {'N': row['sampling_rate'], 'f1': quality['mean'], 'cost': cost['mean']} to the end of points. |
| 187 | <code>                    {&quot;N&quot;: row[&quot;sampling_rate&quot;], &quot;f1&quot;: quality[&quot;mean&quot;], &quot;cost&quot;: cost[&quot;mean&quot;]}</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 188 | <code>                )</code> | Close the call to points.append begun above; this is punctuation, not a separate operation. |
| 189 | <code>        fronts.append(</code> | Append {'comparison_group': key, 'front': pareto(points), 'reason': None if points else 'No comparable measured quality and live bandwidth'} to the end of fronts. |
| 190 | <code>            {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 191 | <code>                &quot;comparison_group&quot;: key,</code> | Field comparison_group: Named entry in the surrounding dictionary. Its value is key; consumers access it by this key. |
| 192 | <code>                &quot;front&quot;: pareto(points),</code> | Field front: Named entry in the surrounding dictionary. Its value is pareto(points); consumers access it by this key. |
| 193 | <code>                &quot;reason&quot;: None if points else &quot;No comparable measured quality and live bandwidth&quot;,</code> | Field reason: Explicit explanation for unavailable or estimated values; a missing value is not a measured zero. |
| 194 | <code>            }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 195 | <code>        )</code> | Close the call to fronts.append begun above; this is punctuation, not a separate operation. |
| 196 | <code>        if points:</code> | Branch only if points is true; otherwise skip this indented block or take its following elif/else. |
| 197 | <code>            fig, ax = plt.subplots(figsize=(7, 4))</code> | Set (fig, ax). Call plt.subplots with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 198 | <code>            ax.scatter(</code> | Call ax.scatter with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 199 | <code>                [p[&quot;cost&quot;] for p in points], [p[&quot;f1&quot;] for p in points], label=&quot;Configurations&quot;</code> | Continuation of the statement above. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [p['cost'] for p in points]. |
| 200 | <code>            )</code> | Close the call to ax.scatter begun above; this is punctuation, not a separate operation. |
| 201 | <code>            efficient = sorted(pareto(points), key=lambda p: p[&quot;cost&quot;])</code> | Set efficient. Create a sorted copy using the supplied ordering/key: sorted(pareto(points), key=lambda p: p['cost']). |
| 202 | <code>            ax.plot(</code> | Call ax.plot with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 203 | <code>                [p[&quot;cost&quot;] for p in efficient],</code> | Continuation of the statement above. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [p['cost'] for p in efficient]. |
| 204 | <code>                [p[&quot;f1&quot;] for p in efficient],</code> | Continuation of the statement above. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [p['f1'] for p in efficient]. |
| 205 | <code>                color=&quot;#21618C&quot;,</code> | Keyword argument color for the call above. Pass the shown value "#21618C" into that parameter. |
| 206 | <code>                linestyle=&quot;--&quot;,</code> | Keyword argument linestyle for the call above. Pass the shown value "--" into that parameter. |
| 207 | <code>                label=&quot;Pareto-efficient&quot;,</code> | Keyword argument label for the call above. Pass the shown value "Pareto-efficient" into that parameter. |
| 208 | <code>            )</code> | Close the call to ax.plot begun above; this is punctuation, not a separate operation. |
| 209 | <code>            for point in points:</code> | Loop: assign each item from points into point, then execute the indented body. |
| 210 | <code>                ax.annotate(</code> | Call ax.annotate with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 211 | <code>                    f&quot;N={point[&#x27;N&#x27;]}&quot;,</code> | Continuation of the statement above. Read f'N={point['N']}' from the current function/object state. |
| 212 | <code>                    (point[&quot;cost&quot;], point[&quot;f1&quot;]),</code> | Continuation of the statement above. Bundle these values in a tuple: (point['cost'], point['f1']). |
| 213 | <code>                    xytext=(4, 4),</code> | Keyword argument xytext for the call above. Pass the shown value (4, 4) into that parameter. |
| 214 | <code>                    textcoords=&quot;offset points&quot;,</code> | Keyword argument textcoords for the call above. Pass the shown value "offset points" into that parameter. |
| 215 | <code>                )</code> | Close the call to ax.annotate begun above; this is punctuation, not a separate operation. |
| 216 | <code>            ax.set(</code> | Call ax.set with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 217 | <code>                xlabel=&quot;Measured received sFlow payload (kbit/s)&quot;,</code> | Keyword argument xlabel for the call above. Pass the shown value "Measured received sFlow payload (kbit/s)" into that parameter. |
| 218 | <code>                ylabel=&quot;F1&quot;,</code> | Keyword argument ylabel for the call above. Pass the shown value "F1" into that parameter. |
| 219 | <code>                title=f&quot;Accuracy versus measured overhead - group {index + 1}&quot;,</code> | Keyword argument title for the call above. Pass the shown value f"Accuracy versus measured overhead - group {index + 1}" into that parameter. |
| 220 | <code>            )</code> | Close the call to ax.set begun above; this is punctuation, not a separate operation. |
| 221 | <code>            ax.legend()</code> | Call ax.legend with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 222 | <code>            fig.tight_layout()</code> | Call fig.tight_layout with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 223 | <code>            path = output / f&quot;group_{index + 1}_pareto.png&quot;</code> | Set path. Calculate output / f'group_{index + 1}_pareto.png' using divide; / returns a floating-point ratio and // floors division where used. |
| 224 | <code>            fig.savefig(path, dpi=160)</code> | Call fig.savefig with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 225 | <code>            plt.close(fig)</code> | Close plt and release its file/socket/plot resource. |
| 226 | <code>            charts.append(str(path))</code> | Append str(path) to the end of charts. |
| 227 | <code>    atomic_json(output / &quot;pareto_fronts.json&quot;, {&quot;groups&quot;: fronts})</code> | Write JSON to a sibling temporary file then replace the target, avoiding partial JSON reads. |
| 228 | <code>    return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 229 | <code>        &quot;groups&quot;: len(by_group),</code> | Field groups: Named entry in the surrounding dictionary. Its value is len(by_group); consumers access it by this key. |
| 230 | <code>        &quot;configurations&quot;: len(rows),</code> | Field configurations: Named entry in the surrounding dictionary. Its value is len(rows); consumers access it by this key. |
| 231 | <code>        &quot;charts&quot;: charts,</code> | Field charts: Named entry in the surrounding dictionary. Its value is charts; consumers access it by this key. |
| 232 | <code>        &quot;output&quot;: str(output),</code> | Field output: Named entry in the surrounding dictionary. Its value is str(output); consumers access it by this key. |
| 233 | <code>        &quot;excluded_fixture_runs&quot;: sum(r[&quot;source&quot;] == &quot;fixture&quot; for r in runs),</code> | Field excluded_fixture_runs: Named entry in the surrounding dictionary. Its value is sum(r["source"] == "fixture" for r in runs); consumers access it by this key. |
| 234 | <code>    }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |

## src/m3/api.py

**Read-only HTTP results interface.** FastAPI exposes saved runs and timelines to the browser. The HTTP server does not train the model, start sweeps, or perform live collection. The process running m3 run/live writes evidence; the separate m3 serve process reads it.

Snapshot: 64 lines; SHA256 `5caf834a79dc8eb42075c91aa790e387a1f8420cedf712d73b89b9d6bb17ef9b`.

### Named operations

- `create_app` (L9): Builds a read-only FastAPI app with local development CORS, an evidence repository, API routes, and an optional static dashboard mount.
- `create_app.health` (L20): Simple service/schema health response; does not inspect model accuracy or completeness of evidence.
- `create_app.runs` (L24): Returns the repository run list, including status and source distinctions.
- `create_app.overview` (L28): Counts statuses and reports the maximum F1 among completed runs; this endpoint does not enforce scientific comparability for best_run_id.
- `create_app.run` (L42): Returns one summary, converting invalid/missing run directory errors to HTTP 404.
- `create_app.series` (L49): Returns sampled visualization series for one run; FastAPI validates the limit between 2 and 10,000.

Path indexing example: for Project/src/m3/api.py, parents[0] is m3, parents[1] is src and parents[2] is Project. The optional static mount therefore correctly targets project-root frontend/dist, and is enabled only when that build directory exists. `best_run_id` in overview is a raw maximum across completed runs; it is not a fair cross-scenario ranking.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>from fastapi import FastAPI, HTTPException, Query</code> | Import FastAPI, HTTPException, Query from fastapi. This makes the named library helpers available without the module prefix. |
| 4 | <code>from fastapi.middleware.cors import CORSMiddleware</code> | Import CORSMiddleware from fastapi.middleware.cors. This makes the named library helpers available without the module prefix. |
| 5 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 6 | <code>from m3.store import RunRepository</code> | Import RunRepository from m3.store. These are project definitions; follow the named module in this guide to see their implementation. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 9 | <code>def create_app(root=&quot;output/runs&quot;):</code> | Define function/method create_app. Builds a read-only FastAPI app with local development CORS, an evidence repository, API routes, and an optional static dashboard mount. |
| 10 | <code>    app = FastAPI(title=&quot;M3 experimental results&quot;, version=&quot;0.1.0&quot;)</code> | Set app. Call FastAPI with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 11 | <code>    app.add_middleware(</code> | Call app.add_middleware with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 12 | <code>        CORSMiddleware,</code> | Continuation of the statement above. Read CORSMiddleware from the current function/object state. |
| 13 | <code>        allow_origins=[&quot;http://localhost:5173&quot;, &quot;http://127.0.0.1:5173&quot;],</code> | Keyword argument allow_origins for the call above. Pass the shown value ["http://localhost:5173", "http://127.0.0.1:5173"] into that parameter. |
| 14 | <code>        allow_methods=[&quot;GET&quot;],</code> | Keyword argument allow_methods for the call above. Pass the shown value ["GET"] into that parameter. |
| 15 | <code>        allow_headers=[&quot;*&quot;],</code> | Keyword argument allow_headers for the call above. Pass the shown value ["*"] into that parameter. |
| 16 | <code>    )</code> | Close the call to app.add_middleware begun above; this is punctuation, not a separate operation. |
| 17 | <code>    repository = RunRepository(root)</code> | Set repository. Construct a new RunRepository using root. |
| 18 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 19 | <code>    @app.get(&quot;/api/health&quot;)</code> | Register the following function as an HTTP GET handler for the path shown; the decorator runs while create_app builds the app. |
| 20 | <code>    def health():</code> | Define function/method health. Simple service/schema health response; does not inspect model accuracy or completeness of evidence. |
| 21 | <code>        return {&quot;status&quot;: &quot;ok&quot;, &quot;schema_version&quot;: 1}</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 22 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 23 | <code>    @app.get(&quot;/api/runs&quot;)</code> | Register the following function as an HTTP GET handler for the path shown; the decorator runs while create_app builds the app. |
| 24 | <code>    def runs():</code> | Define function/method runs. Returns the repository run list, including status and source distinctions. |
| 25 | <code>        return {&quot;runs&quot;: repository.list()}</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 26 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 27 | <code>    @app.get(&quot;/api/overview&quot;)</code> | Register the following function as an HTTP GET handler for the path shown; the decorator runs while create_app builds the app. |
| 28 | <code>    def overview():</code> | Define function/method overview. Counts statuses and reports the maximum F1 among completed runs; this endpoint does not enforce scientific comparability for best_run_id. |
| 29 | <code>        all_runs = repository.list()</code> | Set all_runs. Call repository.list with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>        completed = [r for r in all_runs if r[&quot;status&quot;] == &quot;completed&quot;]</code> | Set completed. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [r for r in all_runs if r['status'] == 'completed']. |
| 31 | <code>        candidates = [r for r in completed if r[&quot;metrics&quot;].get(&quot;f1&quot;, {}).get(&quot;value&quot;) is not None]</code> | Set candidates. Build a collection by iterating the for clauses and retaining entries passing the if clauses: [r for r in completed if r['metrics'].get('f1', {}).get('value') is not None]. |
| 32 | <code>        best = max(candidates, key=lambda r: r[&quot;metrics&quot;][&quot;f1&quot;][&quot;value&quot;], default=None)</code> | Set best. Select the largest supplied value from max(candidates, key=lambda r: r['metrics']['f1']['value'], default=None). |
| 33 | <code>        return {</code> | Return to the caller: Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 34 | <code>            &quot;total_runs&quot;: len(all_runs),</code> | Field total_runs: Named entry in the surrounding dictionary. Its value is len(all_runs); consumers access it by this key. |
| 35 | <code>            &quot;completed_runs&quot;: len(completed),</code> | Field completed_runs: Named entry in the surrounding dictionary. Its value is len(completed); consumers access it by this key. |
| 36 | <code>            &quot;running_runs&quot;: sum(r[&quot;status&quot;] == &quot;running&quot; for r in all_runs),</code> | Field running_runs: Named entry in the surrounding dictionary. Its value is sum(r["status"] == "running" for r in all_runs); consumers access it by this key. |
| 37 | <code>            &quot;failed_runs&quot;: sum(r[&quot;status&quot;] == &quot;failed&quot; for r in all_runs),</code> | Field failed_runs: Named entry in the surrounding dictionary. Its value is sum(r["status"] == "failed" for r in all_runs); consumers access it by this key. |
| 38 | <code>            &quot;best_run_id&quot;: best[&quot;run_id&quot;] if best else None,</code> | Field best_run_id: Named entry in the surrounding dictionary. Its value is best["run_id"] if best else None; consumers access it by this key. |
| 39 | <code>        }</code> | Close the collection/expression begun above; this is punctuation, not a separate operation. |
| 40 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 41 | <code>    @app.get(&quot;/api/runs/{run_id}&quot;)</code> | Register the following function as an HTTP GET handler for the path shown; the decorator runs while create_app builds the app. |
| 42 | <code>    def run(run_id: str):</code> | Define function/method run. Returns one summary, converting invalid/missing run directory errors to HTTP 404. |
| 43 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 44 | <code>            return repository.get(run_id)</code> | Return to the caller: Look up run_id in repository; use the explicit default if supplied, otherwise None. |
| 45 | <code>        except FileNotFoundError as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 46 | <code>            raise HTTPException(404, str(exc)) from exc</code> | Raise HTTPException(404, str(exc)) and stop this operation; chain the original cause for diagnostics. |
| 47 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 48 | <code>    @app.get(&quot;/api/runs/{run_id}/series&quot;)</code> | Register the following function as an HTTP GET handler for the path shown; the decorator runs while create_app builds the app. |
| 49 | <code>    def series(run_id: str, limit: int = Query(1000, ge=2, le=10000)):</code> | Define function/method series. Returns sampled visualization series for one run; FastAPI validates the limit between 2 and 10,000. |
| 50 | <code>        try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 51 | <code>            return repository.series(run_id, limit)</code> | Return to the caller: Call repository.series with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 52 | <code>        except FileNotFoundError as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 53 | <code>            raise HTTPException(404, str(exc)) from exc</code> | Raise HTTPException(404, str(exc)) and stop this operation; chain the original cause for diagnostics. |
| 54 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 55 | <code>    # A frontend production build is optional; API remains usable without Node.</code> | Source comment: A frontend production build is optional; API remains usable without Node. This documents intent and does not execute. |
| 56 | <code>    frontend = Path(__file__).resolve().parents[2] / &quot;frontend&quot; / &quot;dist&quot;</code> | Set frontend. Calculate Path(__file__).resolve().parents[2] / 'frontend' / 'dist' using divide; / returns a floating-point ratio and // floors division where used. |
| 57 | <code>    if frontend.is_dir():</code> | Branch only if frontend.is_dir() is true; otherwise skip this indented block or take its following elif/else. |
| 58 | <code>        from fastapi.staticfiles import StaticFiles</code> | Import StaticFiles from fastapi.staticfiles. This makes the named library helpers available without the module prefix. |
| 59 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 60 | <code>        app.mount(&quot;/&quot;, StaticFiles(directory=frontend, html=True), name=&quot;dashboard&quot;)</code> | Call app.mount with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 61 | <code>    return app</code> | Return to the caller: Read app from the current function/object state. |
| 62 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 63 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 64 | <code>app = create_app()</code> | Set app. Call create_app with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |

## src/m3/cli.py

**Command-line entry point.** argparse translates m3 audit/run/live/sweep/analyse/serve arguments into function calls. pyproject.toml registers m3 = m3.cli:main. Running this file as a module also calls main because of the __name__ guard.

Snapshot: 88 lines; SHA256 `ce248ea2370c40aa98de2c2126ea32411822470f4cca62dca65023713bcccedd`.

### Named operations

- `main` (L12): Parses one required CLI subcommand, dispatches the selected operation and turns expected errors into a readable exit code 1.

### Line-by-line source and explanation

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>&quot;&quot;&quot;Local-only commands. Production runs always enforce official data provenance.&quot;&quot;&quot;</code> | Documentation string: Local-only commands. Production runs always enforce official data provenance. It explains the module/class/function; it is not an extra experiment step. |
| 2 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 3 | <code>import argparse</code> | Import argparse to parse and validate command-line arguments. |
| 4 | <code>import json</code> | Import json to encode/decode configuration, manifest and run-summary JSON. |
| 5 | <code>from dataclasses import replace</code> | Import replace from dataclasses. This makes the named library helpers available without the module prefix. |
| 6 | <code>from pathlib import Path</code> | Import Path from pathlib. This makes the named library helpers available without the module prefix. |
| 7 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 8 | <code>from m3.config import SAMPLING_RATES, RunConfig</code> | Import SAMPLING_RATES, RunConfig from m3.config. These are project definitions; follow the named module in this guide to see their implementation. |
| 9 | <code>from m3.store import atomic_json</code> | Import atomic_json from m3.store. These are project definitions; follow the named module in this guide to see their implementation. |
| 10 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 11 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 12 | <code>def main():</code> | Define function/method main. Parses one required CLI subcommand, dispatches the selected operation and turns expected errors into a readable exit code 1. |
| 13 | <code>    parser = argparse.ArgumentParser(</code> | Set parser. Call argparse.ArgumentParser with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 14 | <code>        description=&quot;M3 official-data evaluation and live sFlow collector&quot;</code> | Keyword argument description for the call above. Pass the shown value "M3 official-data evaluation and live sFlow collector" into that parameter. |
| 15 | <code>    )</code> | Close the call to argparse.ArgumentParser begun above; this is punctuation, not a separate operation. |
| 16 | <code>    sub = parser.add_subparsers(dest=&quot;command&quot;, required=True)</code> | Set sub. Call parser.add_subparsers with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 17 | <code>    audit = sub.add_parser(&quot;audit&quot;, help=&quot;Verify and inspect an official CSV&quot;)</code> | Set audit. Call sub.add_parser with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 18 | <code>    audit.add_argument(&quot;input&quot;)</code> | Call audit.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 19 | <code>    audit.add_argument(&quot;--manifest&quot;, default=&quot;data/manifest.json&quot;)</code> | Call audit.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 20 | <code>    audit.add_argument(&quot;--output&quot;, default=&quot;output/analysis/dataset_audit.json&quot;)</code> | Call audit.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 21 | <code>    for name in (&quot;run&quot;, &quot;live&quot;, &quot;sweep&quot;):</code> | Loop: assign each item from ('run', 'live', 'sweep') into name, then execute the indented body. |
| 22 | <code>        command = sub.add_parser(name)</code> | Set command. Call sub.add_parser with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 23 | <code>        command.add_argument(&quot;--config&quot;, required=True)</code> | Call command.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 24 | <code>    analysis = sub.add_parser(&quot;analyse&quot;)</code> | Set analysis. Call sub.add_parser with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 25 | <code>    analysis.add_argument(&quot;--runs&quot;, default=&quot;output/runs&quot;)</code> | Call analysis.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 26 | <code>    analysis.add_argument(&quot;--output&quot;, default=&quot;output/analysis&quot;)</code> | Call analysis.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 27 | <code>    serve = sub.add_parser(&quot;serve&quot;)</code> | Set serve. Call sub.add_parser with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 28 | <code>    serve.add_argument(&quot;--runs&quot;, default=&quot;output/runs&quot;)</code> | Call serve.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 29 | <code>    serve.add_argument(&quot;--port&quot;, type=int, default=8000)</code> | Call serve.add_argument with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 30 | <code>    args = parser.parse_args()</code> | Set args. Call parser.parse_args with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 31 | <code>    try:</code> | Start a protected block. A matching except below records/handles failures; a finally block, if present, always performs cleanup. |
| 32 | <code>        if args.command == &quot;audit&quot;:</code> | Branch only if args.command == 'audit' is true; otherwise skip this indented block or take its following elif/else. |
| 33 | <code>            from m3.data import audit_csv</code> | Import audit_csv from m3.data. These are project definitions; follow the named module in this guide to see their implementation. |
| 34 | <code>            from m3.provenance import verify_input</code> | Import verify_input from m3.provenance. These are project definitions; follow the named module in this guide to see their implementation. |
| 35 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 36 | <code>            value = {&quot;provenance&quot;: verify_input(args.input, args.manifest), **audit_csv(args.input)}</code> | Set value. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 37 | <code>            target = Path(args.output)</code> | Set target. Construct a new Path using args.output. |
| 38 | <code>            target.parent.mkdir(parents=True, exist_ok=True)</code> | Create the output directory with the specified parent/existence options: target.parent.mkdir(parents=True, exist_ok=True). |
| 39 | <code>            atomic_json(target, value)</code> | Write JSON to a sibling temporary file then replace the target, avoiding partial JSON reads. |
| 40 | <code>            print(</code> | Call print with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 41 | <code>                json.dumps(</code> | Continuation of the statement above. Call json.dumps with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 42 | <code>                    {</code> | Continuation of the statement above. Build the dictionary below; each key names an evidence/configuration value and ** merges another dictionary. |
| 43 | <code>                        &quot;output&quot;: str(target),</code> | Field output: Named entry in the surrounding dictionary. Its value is str(target); consumers access it by this key. |
| 44 | <code>                        &quot;rows&quot;: value[&quot;rows&quot;],</code> | Field rows: Named entry in the surrounding dictionary. Its value is value["rows"]; consumers access it by this key. |
| 45 | <code>                        &quot;attack_counts&quot;: value[&quot;attack_counts&quot;],</code> | Field attack_counts: Named entry in the surrounding dictionary. Its value is value["attack_counts"]; consumers access it by this key. |
| 46 | <code>                    },</code> | Close the collection/expression begun above; the comma separates it from the next surrounding argument/item. |
| 47 | <code>                    indent=2,</code> | Keyword argument indent for the call above. Pass the shown value 2 into that parameter. |
| 48 | <code>                )</code> | Close the call to json.dumps begun above; this is punctuation, not a separate operation. |
| 49 | <code>            )</code> | Close the call to print begun above; this is punctuation, not a separate operation. |
| 50 | <code>        elif args.command in (&quot;run&quot;, &quot;live&quot;, &quot;sweep&quot;):</code> | Branch only if args.command in ('run', 'live', 'sweep') is true; otherwise skip this indented block or take its following elif/else. |
| 51 | <code>            from m3.engine import run_replay</code> | Import run_replay from m3.engine. These are project definitions; follow the named module in this guide to see their implementation. |
| 52 | <code>            from m3.live import run_live</code> | Import run_live from m3.live. These are project definitions; follow the named module in this guide to see their implementation. |
| 53 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 54 | <code>            config = RunConfig.load(args.config)</code> | Set config. Call RunConfig.load with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 55 | <code>            if args.command == &quot;live&quot;:</code> | Branch only if args.command == 'live' is true; otherwise skip this indented block or take its following elif/else. |
| 56 | <code>                result = run_live(config)</code> | Set result. Call run_live with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 57 | <code>            elif args.command == &quot;sweep&quot;:</code> | Branch only if args.command == 'sweep' is true; otherwise skip this indented block or take its following elif/else. |
| 58 | <code>                if config.mode == &quot;live_sflow&quot;:</code> | Branch only if config.mode == 'live_sflow' is true; otherwise skip this indented block or take its following elif/else. |
| 59 | <code>                    raise ValueError(</code> | Raise ValueError('Live sweeps require the SDN orchestrator to reconfigure the switch each time') and stop this operation; the caller can record/report this invalid condition. |
| 60 | <code>                        &quot;Live sweeps require the SDN orchestrator to reconfigure the switch each time&quot;</code> | Literal component of the surrounding statement: 'Live sweeps require the SDN orchestrator to reconfigure the switch each time'. Its role is determined by the field/call immediately above. |
| 61 | <code>                    )</code> | Close the call to ValueError begun above; this is punctuation, not a separate operation. |
| 62 | <code>                result = []</code> | Set result. Build the ordered list below; order is retained. |
| 63 | <code>                for rate in SAMPLING_RATES:</code> | Loop: assign each item from SAMPLING_RATES into rate, then execute the indented body. |
| 64 | <code>                    for trial in range(3):</code> | Loop: assign each item from range(3) into trial, then execute the indented body. |
| 65 | <code>                        run = run_replay(</code> | Set run. Call run_replay with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 66 | <code>                            replace(config, sampling_rate=rate, seed=config.seed + trial)</code> | Continuation of the statement above. Create a new dataclass instance with selected fields changed; the original remains unchanged: replace(config, sampling_rate=rate, seed=config.seed + trial). |
| 67 | <code>                        )</code> | Close the call to run_replay begun above; this is punctuation, not a separate operation. |
| 68 | <code>                        result.append({&quot;run_id&quot;: run[&quot;run_id&quot;], &quot;N&quot;: rate, &quot;seed&quot;: run[&quot;seed&quot;]})</code> | Append {'run_id': run['run_id'], 'N': rate, 'seed': run['seed']} to the end of result. |
| 69 | <code>                        print(json.dumps(result[-1]), flush=True)</code> | Call print with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 70 | <code>            else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 71 | <code>                result = run_replay(config)</code> | Set result. Call run_replay with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 72 | <code>            print(json.dumps(result, indent=2, allow_nan=False))</code> | Call print with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 73 | <code>        elif args.command == &quot;analyse&quot;:</code> | Branch only if args.command == 'analyse' is true; otherwise skip this indented block or take its following elif/else. |
| 74 | <code>            from m3.analysis import analyse</code> | Import analyse from m3.analysis. These are project definitions; follow the named module in this guide to see their implementation. |
| 75 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 76 | <code>            print(json.dumps(analyse(args.runs, args.output), indent=2))</code> | Call print with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
| 77 | <code>        else:</code> | Fallback branch: execute this indented block only when the corresponding if/for/try alternative selects it. |
| 78 | <code>            import uvicorn</code> | Import uvicorn to use its functions/classes in this module. |
| 79 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 80 | <code>            from m3.api import create_app</code> | Import create_app from m3.api. These are project definitions; follow the named module in this guide to see their implementation. |
| 81 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 82 | <code>            uvicorn.run(create_app(args.runs), host=&quot;127.0.0.1&quot;, port=args.port)</code> | Start the local HTTP results server; this does not run model training. |
| 83 | <code>    except (OSError, ValueError, RuntimeError) as exc:</code> | Handle the exception types shown here; an as-name retains the exception for the saved failure/error message. |
| 84 | <code>        parser.exit(1, f&quot;M3: {exc}\n&quot;)</code> | Exit with code 1 and a readable CLI error message. |
| 85 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 86 | <em>blank</em> | Blank line: separates imports, definitions, or logical steps; no instruction executes here. |
| 87 | <code>if __name__ == &quot;__main__&quot;:</code> | Branch only if __name__ == '__main__' is true; otherwise skip this indented block or take its following elif/else. |
| 88 | <code>    main()</code> | Call main with the shown arguments. Its returned value is used here; see the corresponding function section for its full operation. |
