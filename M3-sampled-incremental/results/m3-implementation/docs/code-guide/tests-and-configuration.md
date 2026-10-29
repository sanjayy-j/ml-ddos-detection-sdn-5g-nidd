# Tests and configuration: every source line explained

This guide documents the source snapshot read for this walkthrough. Each numbered table row corresponds to one physical source line, including blank lines and closing delimiters. The middle column reproduces the line; indentation is retained in the inline source text but Markdown may visually collapse it. Read the original file alongside this guide when indentation matters.

## How to read the tests

An `assert` expresses an invariant: the test passes only if its expression is true. `pytest.raises(...)` passes only if the enclosed operation raises the expected exception; `match=` additionally checks the message. A `test_...` function is discovered automatically by pytest. `@pytest.mark.parametrize` repeats the same test with different input values.

`tmp_path` is a pytest fixture that gives each test an isolated temporary directory. `monkeypatch` temporarily replaces a function/attribute and restores it after the test. These names are provided by pytest, not passed from production code. `fixture=True` in the replay engine explicitly marks fabricated test data so it cannot silently enter official experiment aggregation.

`SpyModel` records call order and always returns fixed predictions; `AlwaysAttack` always predicts an attack. Neither implements HAT learning, and their hardcoded latency values are artificial. Only `test_real_hat_and_adwin` in `test_core.py` directly exercises the real detector's learning and monitor. Protocol fixture builders create byte layouts for software validation; they do not recreate the official 5G-NIDD experiment.

Passing this suite establishes these particular behaviors. It does not prove publication claims, unseen-attack robustness on the real dataset, performance on all sampling rates and seeds, an actual SDN deployment's resource savings, or a valid knee point. Those require the saved experiments described elsewhere in the project.

## Configuration facts that affect interpretation

JSON supplies settings to `RunConfig`; omitted fields inherit the defaults in `src/m3/config.py`. Relative paths resolve from the process working directory. Neither JSON file is a data preparation script or training program. CSV replay follows CSV row order and uses row indices as its internal time, so physical detection delay is unavailable for that mode. CSV sampling is seeded Bernoulli row selection with probability `1 / sampling_rate`, not a claim of packet-level sFlow.

`scenario="drift"` records the scenario name; it does not generate a traffic distribution change. A drift experiment needs suitably ordered data/traffic and documented boundaries. `scenario="unseen"` has implemented special treatment: warm-up SYNFlood examples are excluded, and the summary enables the held-out SYNFlood recall. The caller still needs to prepare data and keep tuning separate. A live run learns only where verified labels are actually supplied; ADWIN monitors supervised error and does not invent ground truth.

Run the normal tests through the project's installed environment with `pytest`; `pyproject.toml` selects the tests directory and quiet output. The live test uses a short local UDP session, while the lab tests mock OVS subprocess output. This documentation task reads and explains the tests; it does not claim a new test execution.

## tests/test_core.py

Configuration validation, feature leakage prevention, metrics, data provenance, sampled windows, protocol decoding, test-then-train order, persisted failure evidence, API behavior, Pareto filtering, aggregation, and an actual HAT/ADWIN smoke test.

Physical lines: 285.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `import csv` | Import the standard-library CSV reader/writer. |
| 2 | `import json` | Import the standard-library JSON serializer. |
| 3 | `import struct` | Import binary integer packing for generated protocol fixtures. |
| 4 | `from dataclasses import replace` | Import dataclasses.replace, which creates a modified copy of an immutable dataclass. |
| 5 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 6 | `import pytest` | Import pytest's parametrization, expected-exception, and approximate-number helpers. |
| 7 | `from fastapi.testclient import TestClient` | Import FastAPI's in-process HTTP test client. |
| 8 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 9 | `from m3.analysis import aggregate, pareto` | Import the run aggregation and strict Pareto filtering functions. |
| 10 | `from m3.api import create_app` | Import the FastAPI application factory. |
| 11 | `from m3.config import RunConfig` | Import the validated, immutable run configuration class. |
| 12 | `from m3.data import binary_label, extract_flow_features` | Import flow target conversion and the allowlisted feature extractor. |
| 13 | `from m3.engine import run_replay` | Import the actual CSV/PCAP replay pipeline. |
| 14 | `from m3.labels import LabelTimeline` | Import the validated interval label reader. |
| 15 | `from m3.metrics import QualityMetrics, measurement, roc_auc` | Import quality accumulation, measurement formatting, and ROC-AUC calculation. |
| 16 | `from m3.model import OnlineDetector` | Import the real online HAT/ADWIN wrapper. |
| 17 | `from m3.packets import Packet, WindowAccumulator, parse_header` | Import packet records, sampled-window feature accumulation, and packet-header decoding. |
| 18 | `from m3.provenance import OFFICIAL_DOI, sha256, verify_input` | Import the dataset identity constant, content hashing, and manifest verification. |
| 19 | `from m3.sflow import DecodeError, decode_datagram` | Import the sFlow-specific decode exception and binary decoder. |
| 20 | `from m3.store import RunRepository` | Import the saved-run reader. |
| 21 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 22 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 23 | `@pytest.mark.parametrize("rate", [1, 2, 5, 10, 20, 50])` | Run the next test six times, once for each allowed 1-in-N sampling rate. |
| 24 | `def test_valid_config(rate):` | Define a test that receives the current parametrized rate. |
| 25 | `    assert RunConfig(input_path="x", sampling_rate=rate).sampling_rate == rate` | Require configuration validation to preserve each permitted integer rate. |
| 26 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 27 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 28 | `@pytest.mark.parametrize(` | Start a parametrization decorator for invalid configurations. |
| 29 | `    "kwargs",` | Name the argument that will receive each dictionary of invalid fields. |
| 30 | `    [` | Start the list of invalid input dictionaries. |
| 31 | `        {"sampling_rate": 3},` | Use unsupported sampling rate 3; the accepted rates are the project's fixed experimental choices. |
| 32 | `        {"sampling_rate": True},` | Use Boolean True: Python treats bool as an int subclass, so this verifies the stricter exact-integer validation. |
| 33 | `        {"threshold": float("nan")},` | Use NaN, a floating-point value that is not finite and cannot be a usable probability threshold. |
| 34 | `        {"window_seconds": 0},` | Use a zero-second window, which cannot define valid per-second features. |
| 35 | `        {"max_records": 0},` | Use zero as the record limit, which would permit no records. |
| 36 | `        {"mode": "bad"},` | Use an unrecognized execution mode. |
| 37 | `    ],` | Close the list started above; the comma separates it from the next argument or collection item. |
| 38 | `)` | Close the multiline call or parenthesized expression started above. |
| 39 | `def test_invalid_config(kwargs):` | Receive one invalid configuration dictionary per test invocation. |
| 40 | `    with pytest.raises(ValueError):` | Require the enclosed construction to raise ValueError; an accepted invalid configuration fails the test. |
| 41 | `        RunConfig(input_path="x", **kwargs)` | Supply a placeholder replay path and unpack the invalid field dictionary with **kwargs. |
| 42 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 43 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 44 | `def test_labels_and_leakage():` | Define test_labels_and_leakage; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 45 | `    assert binary_label("SYNFlood", "Malicious") == 1` | Require the SYNFlood attack family with a malicious label to map to binary attack class 1. |
| 46 | `    assert binary_label("UDPFlood", "UDPFlood") == 1` | Require UDPFlood supplied in both fields to map to attack class 1. |
| 47 | `    assert binary_label("Benign", "Benign") == 0` | Require explicitly benign traffic to map to normal class 0. |
| 48 | `    assert binary_label("UDPScan", "Malicious") is None` | Require scanning traffic outside the supported flood task to be excluded with None. |
| 49 | `    with pytest.raises(ValueError):` | Require inconsistent family-versus-label information to be rejected. |
| 50 | `        binary_label("SYNFlood", "Benign")` | Provide an attack family paired with a benign label to exercise that rejection. |
| 51 | `    with pytest.raises(ValueError):` | Require a synthetic-looking unsupported family name to be rejected. |
| 52 | `        binary_label("SYNTH_UDPFlood", "Malicious")` | Exercise rejection of SYNTH_UDPFlood even when its general label says malicious. |
| 53 | `    row = {` | Construct a raw CSV-like row to check feature extraction and information leakage. |
| 54 | `        "Dur": "nan",` | Represent a nonfinite duration as the string nan. |
| 55 | `        "Proto": "UDP",` | Provide an uppercase categorical protocol to test normalization. |
| 56 | `        "Label": "Malicious",` | Include the answer label, which must never become a predictive feature. |
| 57 | `        "Attack Tool": "hping",` | Include the attack-tool metadata, which could reveal the answer. |
| 58 | `        "SrcAddr": "10.0.0.1",` | Include a source address, excluded by this flow feature schema. |
| 59 | `        "Seq": "99",` | Include row/sequence metadata, excluded from features. |
| 60 | `        "Offset": "123",` | Include a source offset, excluded from features. |
| 61 | `    }` | Close the dictionary started above. |
| 62 | `    features = extract_flow_features(row)` | Convert the raw row into the model's allowed feature dictionary. |
| 63 | `    assert features["missing_Dur"] == 1 and features["Dur"] == 0` | Require nonfinite duration to become numeric zero with a separate missing_Dur flag of 1. |
| 64 | `    assert features["Proto"] == "udp"` | Require the protocol category to normalize to lowercase udp. |
| 65 | `    assert not {"Label", "Attack Tool", "SrcAddr", "Seq", "Offset"} & features.keys()` | Intersect forbidden column names with feature keys; require the intersection to be empty. |
| 66 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 67 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 68 | `def test_metrics_missing_zero_and_auc():` | Define test_metrics_missing_zero_and_auc; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 69 | `    assert measurement(None)["status"] == "unavailable"` | Require missing measurements to carry status unavailable. |
| 70 | `    assert measurement(0)["value"] == 0` | Require a real numeric zero to remain zero rather than be treated as missing. |
| 71 | `    assert roc_auc([0, 1], [0.5, 0.5]) == 0.5` | Require tied positive and negative scores to produce chance ROC-AUC 0.5. |
| 72 | `    assert roc_auc([0, 1, 0, 1], [0.1, 0.8, 0.2, 0.9]) == 1` | Require perfectly ranked positive examples to produce ROC-AUC 1. |
| 73 | `    assert roc_auc([1, 1], [0.1, 0.2]) is None` | Require ROC-AUC to be unavailable when there is no negative class for comparison. |
| 74 | `    quality = QualityMetrics()` | Create an empty quality-metric accumulator. |
| 75 | `    for actual, predicted in [(1, 1), (1, 0), (0, 1), (0, 0)]:` | Iterate through one true positive, false negative, false positive, and true negative. |
| 76 | `        quality.update(actual, predicted, predicted, 1, "SYNFlood")` | Feed each example into the accumulator; use predicted as the score, time 1, and SYNFlood as its family. |
| 77 | `    metrics = quality.summary(True)` | Request the summary with unseen-attack metrics enabled. |
| 78 | `    for name in ("precision", "recall", "f1", "false_positive_rate", "unseen_attack_recall"):` | Check the five listed metric names using the same expected balanced confusion matrix. |
| 79 | `        assert metrics[name]["value"] == 0.5` | Require precision, recall, F1, false-positive rate, and unseen-attack recall each to equal 0.5. |
| 80 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 81 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 82 | `def test_provenance_rejects_mutation(tmp_path):` | Define test_provenance_rejects_mutation; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 83 | `    source = tmp_path / "source.csv"` | Create a source-file path under pytest's unique temporary directory. |
| 84 | `    source.write_text("official bytes", encoding="utf-8")` | Write deliberately fake bytes for checksum behavior testing; the words do not certify official data. |
| 85 | `    manifest = tmp_path / "manifest.json"` | Create a companion manifest path in the same temporary directory. |
| 86 | `    manifest.write_text(` | Begin writing the manifest text. |
| 87 | `        json.dumps(` | Serialize the following Python dictionary as JSON. |
| 88 | `            {` | Begin a dictionary object containing the following named fields. |
| 89 | `                "dataset": "5G-NIDD",` | Set the manifest's expected dataset identifier. |
| 90 | `                "doi": OFFICIAL_DOI,` | Use the application's official DOI constant so the fixture passes the identifier check. |
| 91 | `                "status": "partial",` | Declare a partial manifest rather than claiming a complete dataset download. |
| 92 | `                "files": [` | Start the list of manifest file entries. |
| 93 | `                    {` | Begin a dictionary object containing the following named fields. |
| 94 | `                        "path": str(source),` | Record the temporary source file's filesystem path as a string. |
| 95 | `                        "sha256": sha256(source),` | Compute and record a SHA-256 digest of the current file contents. |
| 96 | `                        "verification_status": "verified",` | Mark the fabricated fixture entry verified to exercise the verification path. |
| 97 | `                    }` | Close the dictionary started above. |
| 98 | `                ],` | Close the list started above; the comma separates it from the next argument or collection item. |
| 99 | `            }` | Close the dictionary started above. |
| 100 | `        )` | Close the multiline call or parenthesized expression started above. |
| 101 | `    )` | Close the multiline call or parenthesized expression started above. |
| 102 | `    assert verify_input(source, manifest)["sha256"] == sha256(source)` | Require verify_input to return the same digest computed independently for the current file. |
| 103 | `    source.write_text("changed", encoding="utf-8")` | Replace the source contents after creating its manifest to simulate data modification. |
| 104 | `    with pytest.raises(ValueError, match="checksum"):` | Require the next verification to raise ValueError containing checksum. |
| 105 | `        verify_input(source, manifest)` | Attempt verification against the now-stale manifest. |
| 106 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 107 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 108 | `def test_window_sampling_and_empty_windows():` | Define test_window_sampling_and_empty_windows; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 109 | `    accumulator = WindowAccumulator(1)` | Create an accumulator with one-second windows. |
| 110 | `    assert list(accumulator.add(Packet(100.1, 80, 6, True, 10), 100)) == []` | Add one 80-byte TCP SYN sample at epoch 100.1 with sampling weight 10 and origin 100; require no complete window yet. |
| 111 | `    windows = list(accumulator.advance(3.1))` | Advance relative time to 3.1 seconds and materialize all completed windows from the generator. |
| 112 | `    assert len(windows) == 3` | Require three elapsed one-second windows, including windows with no observed packets. |
| 113 | `    first, count = windows[0]` | Unpack the first result into its Record and sampled-packet count. |
| 114 | `    assert count == 1 and first.features["packets_per_second"] == 10` | Require one actual sample but an estimated rate of ten packets per second. |
| 115 | `    assert first.features["bytes_per_second"] == 800` | Require 80 bytes times weight 10 over one second to produce 800 bytes per second. |
| 116 | `    assert first.features["syn_fraction"] == 1` | Require the only sampled packet being SYN to produce SYN fraction 1. |
| 117 | `    assert windows[1][0].features["empty_window"] == 1` | Require an explicitly marked empty second window rather than silently omitting it. |
| 118 | `    with pytest.raises(ValueError, match="backwards"):` | Require a backwards time advance to raise a clear ValueError. |
| 119 | `        list(accumulator.advance(1))` | Attempt to rewind to relative second 1 after already advancing to 3.1. |
| 120 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 121 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 122 | `def udp_header():` | Define a small helper that creates protocol-header bytes for decoder tests. |
| 123 | `    ethernet = b"\x00" * 12 + b"\x08\x00"` | Build twelve zero address bytes followed by Ethernet type 0x0800 for IPv4. |
| 124 | `    ip = bytearray(20)` | Allocate a mutable twenty-byte IPv4 header. |
| 125 | `    ip[0], ip[9] = 0x45, 17` | Set IPv4 version/header-length byte 0x45 and protocol byte 17 for UDP. |
| 126 | `    return ethernet + ip + b"\x00" * 8` | Return Ethernet plus IPv4 plus eight zero UDP-header bytes; this is a decoder fixture, not real captured traffic. |
| 127 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 128 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 129 | `def sflow_datagram(rate=10, expanded=False):` | Define an sFlow fixture builder with default rate 10 and compact samples unless expanded=True. |
| 130 | `    def ints(*values):` | Define a nested helper accepting any number of unsigned integer values. |
| 131 | `        return struct.pack("!" + "I" * len(values), *values)` | Pack values as network-order, four-byte unsigned integers; ! selects big endian and I an unsigned 32-bit integer. |
| 132 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 133 | `    def record(tag, body):` | Define a nested helper wrapping an sFlow tagged record. |
| 134 | `        return ints(tag, len(body)) + body + b"\x00" * ((-len(body)) % 4)` | Prefix the tag and body length, append bytes, and add zero padding to a four-byte boundary. |
| 135 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 136 | `    header = udp_header()` | Generate the raw packet header to embed in the sFlow sample. |
| 137 | `    raw = ints(1, len(header), 0, len(header)) + header` | Build a raw-header record body: Ethernet protocol 1, frame length, stripped bytes 0, captured-header length, then header bytes. |
| 138 | `    sample = (` | Start the conditional expression assembling a flow-sample body. |
| 139 | `        ints(1, 0, 1, rate, 100, 0, 0, 1, 0, 2, 1)` | Encode expanded sample fields, including sampling rate and one embedded flow record. |
| 140 | `        if expanded` | Choose the previous expanded body when expanded is true. |
| 141 | `        else ints(1, 0, rate, 100, 0, 1, 2, 1)` | Otherwise encode the shorter compact sample fields. |
| 142 | `    )` | Close the multiline call or parenthesized expression started above. |
| 143 | `    return (` | Start concatenating the full sFlow datagram. |
| 144 | `        ints(5, 1)` | Encode sFlow version 5 and agent-address type 1 (IPv4). |
| 145 | `        + b"\x7f\x00\x00\x01"` | Append agent IPv4 bytes for 127.0.0.1. |
| 146 | `        + ints(0, 1, 1000, 1)` | Append sub-agent 0, sequence 1, uptime 1000, and sample count 1. |
| 147 | `        + record(3 if expanded else 1, sample + record(1, raw))` | Wrap the packet header in record tag 1, then the sample in expanded tag 3 or compact tag 1. |
| 148 | `    )` | Close the multiline call or parenthesized expression started above. |
| 149 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 150 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 151 | `@pytest.mark.parametrize("expanded", [False, True])` | Execute decoder tests for both compact and expanded sample encodings. |
| 152 | `def test_sflow_decode_and_truncation(expanded):` | Receive the selected encoding through pytest parametrization. |
| 153 | `    datagram = sflow_datagram(expanded=expanded)` | Build one complete datagram using that encoding. |
| 154 | `    packets, metadata = decode_datagram(datagram, 100)` | Decode it using receipt timestamp 100 and unpack packets and metadata. |
| 155 | `    assert len(packets) == 1 and packets[0].sample_rate == 10 and packets[0].protocol == 17` | Require exactly one decoded UDP packet with sample weight 10 and protocol identifier 17. |
| 156 | `    assert metadata["sequence"] == 1` | Require the decoded datagram sequence number to be 1. |
| 157 | `    for size in range(len(datagram)):` | Iterate every proper prefix length, from empty through one byte short of the full datagram. |
| 158 | `        with pytest.raises((DecodeError, ValueError)):` | Require every truncated prefix to raise a supported decoding/validation exception. |
| 159 | `            decode_datagram(datagram[:size], 100)` | Attempt decoding that truncated prefix at timestamp 100. |
| 160 | `    assert parse_header(b"short", 0, 5) is None` | Require an undersized Ethernet header to return None rather than fabricate a packet. |
| 161 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 162 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 163 | `def test_label_intervals(tmp_path):` | Define test_label_intervals; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 164 | `    path = tmp_path / "labels.json"` | Choose a temporary JSON label-timeline file. |
| 165 | `    data = {` | Construct the verified timeline fixture. |
| 166 | `        "verified": True,` | Set the flag required to use this label source. |
| 167 | `        "source": "test fixture only",` | Explicitly identify the label evidence as a test fixture. |
| 168 | `        "intervals": [` | Start the list of labeled time intervals. |
| 169 | `            {"start": 0, "end": 2, "label": 0, "attack_family": "Benign"},` | Define benign class 0 from relative time 0 to 2. |
| 170 | `            {"start": 2, "end": 4, "label": 1, "attack_family": "SYNFlood"},` | Define SYNFlood class 1 from relative time 2 to 4. |
| 171 | `        ],` | Close the list started above; the comma separates it from the next argument or collection item. |
| 172 | `    }` | Close the dictionary started above. |
| 173 | `    path.write_text(json.dumps(data))` | Write the timeline fixture as JSON. |
| 174 | `    labels = LabelTimeline(path)` | Load and validate it through the actual timeline reader. |
| 175 | `    assert labels.label(0, 1, 100) == (0, "Benign")` | Require a window entirely inside the benign interval to receive benign truth. |
| 176 | `    assert labels.label(1.5, 2.5, 100) == (None, "unknown")` | Require a window crossing the benign/attack boundary to remain unknown. |
| 177 | `    data["intervals"][1]["start"] = 1` | Move the second interval's start backward to create overlap. |
| 178 | `    path.write_text(json.dumps(data))` | Rewrite the file with the invalid overlap. |
| 179 | `    with pytest.raises(ValueError, match="overlap"):` | Require timeline validation to raise a ValueError mentioning overlap. |
| 180 | `        LabelTimeline(path)` | Construct the invalid timeline to trigger validation. |
| 181 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 182 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 183 | `class SpyModel:` | Define a fake model that records call order instead of learning. |
| 184 | `    def __init__(self):` | Initialize a new spy-model instance. |
| 185 | `        self.events = []` | Create an empty call-event list owned by this instance. |
| 186 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 187 | `    def predict(self, features):` | Provide the predict method expected by the replay engine. |
| 188 | `        self.events.append("predict")` | Append a prediction event before returning the fixed answer. |
| 189 | `        return 0, 0.25, 0.1` | Always return normal prediction 0, attack score 0.25, and artificial latency 0.1. |
| 190 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 191 | `    def learn(self, features, label, predicted, monitor=True):` | Provide the learn interface, accepting features, truth, prior prediction, and an optional monitoring flag. |
| 192 | `        self.events.append("learn")` | Record that a learning call occurred; no fitted model is updated. |
| 193 | `        return False` | Report no drift event from this fake learning operation. |
| 194 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 195 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 196 | `def fixture_csv(path):` | Define a helper writing a tiny synthetic CSV at the supplied path. |
| 197 | `    with path.open("w", newline="") as stream:` | Open the fixture for text writing with newline handling suitable for csv.writer. |
| 198 | `        writer = csv.writer(stream)` | Create a standard-library CSV writer. |
| 199 | `        writer.writerow(["Label", "Attack Type", "Proto", "Dur", "TotPkts", "TotBytes"])` | Write exactly the columns needed by the flow reader. |
| 200 | `        for i in range(30):` | Generate thirty example rows. |
| 201 | `            family = "Benign" if i % 2 == 0 else "SYNFlood"` | Alternate normal and SYNFlood families based on even/odd row number. |
| 202 | `            writer.writerow(` | Begin writing one CSV row. |
| 203 | `                ["Benign" if family == "Benign" else "Malicious", family, "udp", 1, 10, 100]` | Write consistent binary-label text, the family, udp, duration 1, packet count 10, and byte count 100. |
| 204 | `            )` | Close the multiline call or parenthesized expression started above. |
| 205 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 206 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 207 | `def test_pipeline_api_and_fixture_separation(tmp_path):` | Define test_pipeline_api_and_fixture_separation; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 208 | `    path = tmp_path / "fixture.csv"` | Choose a temporary path for the synthetic flow fixture. |
| 209 | `    fixture_csv(path)` | Create the thirty-row input CSV. |
| 210 | `    config = RunConfig(input_path=str(path), output_root=str(tmp_path / "runs"), warmup_records=2)` | Configure replay outputs under the temporary directory and reserve two eligible records for warm-up. |
| 211 | `    model = SpyModel()` | Use a call-order spy rather than training the actual HAT in this integration test. |
| 212 | `    run = run_replay(config, fixture=True, model=model)` | Execute replay with fixture=True so these synthetic results are explicitly separated from research evidence. |
| 213 | `    assert run["counts"]["evaluated"] == 28` | Require thirty records minus two warm-up records to yield 28 evaluated examples. |
| 214 | `    assert model.events == ["predict", "learn"] * 30` | Require predict then learn for every one of thirty records, including warm-up. |
| 215 | `    assert run["metrics"]["detection_time_seconds"]["value"] is None` | Require detection time to remain unavailable for CSV data without a valid timing basis. |
| 216 | `    assert run["metrics"]["telemetry_bandwidth_kbps"]["status"] == "estimated"` | Require CSV telemetry bandwidth to be labeled estimated, not measured. |
| 217 | `    assert aggregate([run]) == []` | Require aggregate to exclude this fixture run from official research aggregation. |
| 218 | `    repository = RunRepository(config.output_root)` | Open the actual run repository over the temporary output root. |
| 219 | `    assert len(repository.series(run["run_id"], 3)["predictions"]) == 3` | Require a requested series limit of three to return exactly three prediction entries. |
| 220 | `    with TestClient(create_app(config.output_root)) as client:` | Build FastAPI's in-process client over that repository; this does not launch an external server. |
| 221 | `        assert client.get("/api/health").status_code == 200` | Require the health endpoint to respond successfully. |
| 222 | `        assert client.get("/api/runs").json()["runs"][0]["feature_schema"] == "flow-v1"` | Require the listed run to identify the CSV feature schema as flow-v1. |
| 223 | `        assert client.get("/api/runs/invalid").status_code == 404` | Require an unknown run ID to return HTTP 404. |
| 224 | `        assert client.get(f"/api/runs/{run['run_id']}/series?limit=1").status_code == 422` | Require series limit 1 to fail request validation with HTTP 422. |
| 225 | `    with pytest.raises(FileNotFoundError):` | Require invalid repository path input to raise FileNotFoundError. |
| 226 | `        repository.directory("..")` | Attempt a parent-directory traversal string as a run identifier. |
| 227 | `    other = run_replay(replace(config, sampling_rate=10), fixture=True, model=SpyModel())` | Clone the immutable config with sampling rate 10 and run a second independent spy model. |
| 228 | `    assert other["counts"]["sampled"] < run["counts"]["sampled"]` | Require the more aggressive sampling to retain fewer records than rate 1. |
| 229 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 230 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 231 | `def test_failed_run_keeps_evidence(tmp_path):` | Define test_failed_run_keeps_evidence; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 232 | `    source = tmp_path / "bad.csv"` | Choose a temporary malformed CSV path. |
| 233 | `    source.write_text("bad,columns\n1,2\n")` | Write a CSV whose column names cannot satisfy the actual reader. |
| 234 | `    config = RunConfig(input_path=str(source), output_root=str(tmp_path / "runs"))` | Configure its output directory so failure evidence can be inspected. |
| 235 | `    with pytest.raises(RuntimeError, match="raw logs preserved"):` | Require replay failure to mention preserved raw logs. |
| 236 | `        run_replay(config, fixture=True, model=SpyModel())` | Run the bad fixture through replay with the fake model. |
| 237 | `    run = RunRepository(config.output_root).list()[0]` | Load the persisted run entry after replay raises. |
| 238 | `    assert run["status"] == "failed" and run["error"]` | Require failure status and a nonempty error message to survive in saved evidence. |
| 239 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 240 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 241 | `def test_pareto_strict_dominance():` | Define test_pareto_strict_dominance; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 242 | `    points = [{"f1": 0.8, "cost": 10}, {"f1": 0.7, "cost": 20}, {"f1": 0.9, "cost": 30}]` | Create three quality/cost points: one dominates the second while the third trades extra quality for extra cost. |
| 243 | `    assert pareto(points) == [points[0], points[2]]` | Require Pareto filtering to remove only the lower-F1, higher-cost second point. |
| 244 | `    assert len(pareto([points[0], points[0]])) == 2` | Require identical points to survive; equality alone is not strict dominance. |
| 245 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 246 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 247 | `def test_aggregate_variation_and_status():` | Define test_aggregate_variation_and_status; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 248 | `    base = {` | Construct metadata shared by three synthetic aggregation inputs. |
| 249 | `        "source": "official_5g_nidd",` | Set the source field to the official-data category needed to enter aggregation. |
| 250 | `        "status": "completed",` | Set completed status so these fixture dictionaries qualify for aggregation. |
| 251 | `        "mode": "live_sflow",` | Use live sFlow mode to define a compatible comparison group. |
| 252 | `        "unit": "window",` | Declare metrics scored per time window. |
| 253 | `        "scenario": "baseline",` | Use the baseline scenario group. |
| 254 | `        "config": {},` | Supply an empty configuration object for this isolated aggregation test. |
| 255 | `        "feature_schema": "packet-window-v1",` | Declare the packet-window-v1 feature schema. |
| 256 | `        "sampling_rate": 1,` | Use full sampling rate 1 for all three comparison runs. |
| 257 | `        "provenance": {"sha256": "a"},` | Supply the same input provenance fingerprint for their initial shared group. |
| 258 | `    }` | Close the dictionary started above. |
| 259 | `    runs = [` | Start a list comprehension building three run summaries. |
| 260 | `        {**base, "run_id": str(i), "seed": i, "metrics": {"f1": measurement(value)}}` | Copy shared fields, assign unique IDs and seeds, and wrap each F1 value using the measurement format. |
| 261 | `        for i, value in enumerate([0.5, 0.6, 0.7])` | Enumerate F1 values 0.5, 0.6, and 0.7 with seeds 0, 1, and 2. |
| 262 | `    ]` | Close the list started above. |
| 263 | `    row = aggregate(runs)[0]` | Aggregate the three compatible runs and select the first resulting group. |
| 264 | `    assert row["metrics"]["f1"]["mean"] == pytest.approx(0.6)` | Require their average F1 to be approximately 0.6, tolerating floating-point rounding. |
| 265 | `    assert row["metrics"]["f1"]["std"] == pytest.approx(0.1)` | Require sample standard deviation to be approximately 0.1. |
| 266 | `    assert row["distinct_seeds"] == 3` | Require all three distinct seeds to be counted. |
| 267 | `    runs[0]["provenance"] = {"sha256": "different"}` | Change one run's provenance fingerprint to represent a different dataset input. |
| 268 | `    assert len(aggregate(runs)) == 2` | Require aggregation to split the changed fingerprint into a second group. |
| 269 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 270 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 271 | `def test_real_hat_and_adwin():` | Define test_real_hat_and_adwin; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 272 | `    detector = OnlineDetector(RunConfig(input_path="fixture"))` | Instantiate the actual River-backed detector using a valid placeholder replay configuration. |
| 273 | `    for i in range(5000):` | Generate 5,000 learning observations. |
| 274 | `        label = i % 2` | Alternate ground-truth classes 0 and 1. |
| 275 | `        features = {"Dur": float(label * 100), "TotPkts": float(1 + label * 100), "Proto": "udp"}` | Construct easily separable numeric features and a constant udp category. |
| 276 | `        predicted, score, latency = detector.predict(features)` | Obtain the detector's real prediction, attack probability, and measured prediction latency. |
| 277 | `        assert 0 <= score <= 1 and latency >= 0` | Require a probability between zero and one and nonnegative latency. |
| 278 | `        detector.learn(features, label, predicted)` | Learn only after predicting, preserving the stream evaluation ordering. |
| 279 | `    assert detector.predict({"Dur": 100.0, "TotPkts": 101.0, "Proto": "udp"})[0] == 1` | Require a representative learned attack example to be predicted as class 1. |
| 280 | `    detector.monitor.reset() if hasattr(detector.monitor, "reset") else None` | Call a monitor reset method only if the installed monitor exposes it; otherwise evaluate to None. |
| 281 | `    alarms = []` | Initialize a list of drift flags. |
| 282 | `    for error in [0] * 500 + [1] * 500:` | Create an abrupt error-rate change: 500 error-free updates followed by 500 errors. |
| 283 | `        detector.monitor.update(error)` | Feed one error bit directly to the ADWIN monitor. |
| 284 | `        alarms.append(detector.monitor.drift_detected)` | Record whether ADWIN flags change after that update. |
| 285 | `    assert any(alarms)` | Require at least one change alarm across the synthetic error sequence. |

## tests/test_ground_truth.py

Checks packet truth independently from sampled model inputs: tuple/time joining, reverse traffic, conflicts, interval lookup correctness, full-stream window labels, and replay quality metrics.

Physical lines: 112.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `import csv` | Import the standard-library CSV reader/writer. |
| 2 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 3 | `import dpkt` | Import the packet encoding/decoding dependency. |
| 4 | `import pytest` | Import pytest's parametrization, expected-exception, and approximate-number helpers. |
| 5 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 6 | `from m3.config import RunConfig` | Import the validated, immutable run configuration class. |
| 7 | `from m3.engine import run_replay` | Import the actual CSV/PCAP replay pipeline. |
| 8 | `from m3.ground_truth import FlowLabels, IntervalIndex, WindowTruth, packet_key` | Import flow-to-packet labels, time interval indexing, full-window truth, and packet tuple extraction. |
| 9 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 10 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 11 | `def udp_packet(source=b"\x0a\x00\x00\x01", destination=b"\x0a\x00\x00\x02", sport=123, dport=456):` | Define a helper producing Ethernet/IPv4/UDP bytes; defaults use 10.0.0.1 to 10.0.0.2 and ports 123 to 456. |
| 12 | `    udp = dpkt.udp.UDP(sport=sport, dport=dport, data=b"payload")` | Create a UDP segment with the chosen ports and a small byte payload. |
| 13 | `    udp.ulen = len(udp)` | Set the UDP length to include its header and payload. |
| 14 | `    ip = dpkt.ip.IP(src=source, dst=destination, p=17, data=udp)` | Wrap UDP in IPv4, identifying protocol 17. |
| 15 | `    ip.len = len(ip)` | Set the IPv4 total length before serializing. |
| 16 | `    return bytes(dpkt.ethernet.Ethernet(src=b"\x00" * 6, dst=b"\x01" * 6, type=0x0800, data=ip))` | Wrap IPv4 in Ethernet type 0x0800 and serialize it as bytes; MAC addresses are harmless fixture values. |
| 17 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 18 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 19 | `def test_numeric_time_tuple_join_and_conflicts(tmp_path):` | Define test_numeric_time_tuple_join_and_conflicts; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 20 | `    path = tmp_path / "test_flow_labels.csv"` | Choose a temporary flow-label CSV file. |
| 21 | `    columns = [` | Start the required label-file column names. |
| 22 | `        "start_epoch",` | Start time of the flow interval expressed as numeric epoch seconds. |
| 23 | `        "end_epoch",` | End time of the flow interval expressed as numeric epoch seconds. |
| 24 | `        "src_ip",` | Source IPv4 address used to join packet and flow. |
| 25 | `        "dst_ip",` | Destination IPv4 address used to join packet and flow. |
| 26 | `        "src_port",` | Numeric source transport port used in the join. |
| 27 | `        "dst_port",` | Numeric destination transport port used in the join. |
| 28 | `        "protocol",` | Transport protocol identifier/name used in the join. |
| 29 | `        "label",` | Binary normal/attack target value. |
| 30 | `        "attack_family",` | Human-readable attack family used for labels and reporting. |
| 31 | `        "offset",` | Source flow offset retained as row metadata. |
| 32 | `    ]` | Close the list started above. |
| 33 | `    with path.open("w", newline="") as stream:` | Open the temporary CSV with standard CSV newline handling. |
| 34 | `        writer = csv.writer(stream)` | Create its CSV writer. |
| 35 | `        writer.writerow(columns)` | Write the complete column header. |
| 36 | `        writer.writerow([100, 101, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 1, "UDPFlood", 128])` | Add an attack-labeled UDP flow covering time 100 through 101. |
| 37 | `        writer.writerow([100.5, 100.6, "10.0.0.1", "10.0.0.2", 123, 456, "udp", 0, "Benign", 256])` | Add an overlapping benign label for the same tuple at 100.5 through 100.6, deliberately creating conflicting truth. |
| 38 | `    labels = FlowLabels(path)` | Build the flow-label lookup index from these rows. |
| 39 | `    assert labels.match(udp_packet(), 100.1) == (1, "UDPFlood")` | Require an unambiguous tuple/time match at 100.1 to return UDPFlood class 1. |
| 40 | `    assert labels.match(udp_packet(b"\x0a\x00\x00\x02", b"\x0a\x00\x00\x01", 456, 123), 100.1) == (` | Require the same flow to match in reverse direction after swapping both IP addresses and ports. |
| 41 | `        1,` | The expected reverse-direction tuple begins with attack label 1. |
| 42 | `        "UDPFlood",` | The expected reverse-direction tuple uses family UDPFlood. |
| 43 | `    )` | Close the multiline call or parenthesized expression started above. |
| 44 | `    assert labels.match(udp_packet(), 100.55) == (None, "unknown")` | Require contradictory overlapping truth at 100.55 to yield unknown rather than choosing an arbitrary label. |
| 45 | `    assert labels.match(udp_packet(), 101.1) == (None, "unknown")` | Require a packet outside all matching intervals to yield unknown. |
| 46 | `    assert labels.match(udp_packet(sport=999), 100.1) == (None, "unknown")` | Require a source-port mismatch to yield unknown even when time and addresses match. |
| 47 | `    assert packet_key(b"invalid") is None` | Require malformed packet bytes to yield no join key. |
| 48 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 49 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 50 | `def test_interval_index_matches_brute_force():` | Define test_interval_index_matches_brute_force; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 51 | `    rows = [(float(i), float(i + (20 if i % 5 == 0 else 1)), i % 2, "family") for i in range(200)]` | Build 200 intervals with alternating labels; every fifth interval lasts 20 seconds and others last one second. |
| 52 | `    index = IntervalIndex(rows)` | Create the optimized interval index being tested. |
| 53 | `    for time in range(225):` | Check lookup behavior at 225 time positions. |
| 54 | `        assert sorted(index.at(time + 0.2)) == sorted(` | Compare sorted indexed results with independently calculated brute-force results. |
| 55 | `            row for row in rows if row[0] <= time + 0.2 <= row[1]` | Select all reference rows whose inclusive start/end contain time + 0.2. |
| 56 | `        )` | Close the multiline call or parenthesized expression started above. |
| 57 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 58 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 59 | `def test_window_uses_all_ground_truth_not_sampled_labels():` | Define test_window_uses_all_ground_truth_not_sampled_labels; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 60 | `    truth = WindowTruth()` | Create an empty accumulator of full-stream window truth. |
| 61 | `    assert truth.label() == (0, "Benign")` | Require an empty packet window to default to benign. |
| 62 | `    truth.add(0, "Benign")` | Add one known benign packet. |
| 63 | `    truth.add(None, "unknown")` | Add one packet with unknown truth. |
| 64 | `    assert truth.label() == (None, "unknown")` | Require uncertainty to propagate when no positively known attack is present. |
| 65 | `    truth.add(1, "SYNFlood")` | Add a packet known to belong to SYNFlood. |
| 66 | `    assert truth.label() == (1, "SYNFlood")` | Require known attack presence to determine attack truth for the window. |
| 67 | `    assert truth.packets == 3 and truth.unknown == 1` | Require all three packets and the single unknown packet to remain counted. |
| 68 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 69 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 70 | `def test_service_names_are_not_guessed(tmp_path):` | Define test_service_names_are_not_guessed; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 71 | `    path = tmp_path / "bad.csv"` | Choose a temporary invalid flow-label file. |
| 72 | `    path.write_text(` | Begin writing its contents. |
| 73 | `        "start_epoch,end_epoch,src_ip,dst_ip,src_port,dst_port,protocol,label,attack_family,offset\n100,101,10.0.0.1,10.0.0.2,http,456,udp,1,UDPFlood,128\n"` | Write a correctly named CSV header but put the service-name string http in the numeric source-port field. |
| 74 | `    )` | Close the multiline call or parenthesized expression started above. |
| 75 | `    with pytest.raises(ValueError, match="service-name"):` | Require a ValueError explicitly identifying the unsupported service-name situation. |
| 76 | `        FlowLabels(path)` | Load the invalid CSV to exercise that validation. |
| 77 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 78 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 79 | `def test_packet_pipeline_scores_full_ground_truth_before_sampling(tmp_path):` | Define test_packet_pipeline_scores_full_ground_truth_before_sampling; pytest discovers names beginning test_ and injects requested fixtures by parameter name. |
| 80 | `    path = tmp_path / "flow_labels.csv"` | Choose the temporary label CSV used by the end-to-end packet replay. |
| 81 | `    path.write_text(` | Begin writing the two flow-label intervals. |
| 82 | `        "start_epoch,end_epoch,src_ip,dst_ip,src_port,dst_port,protocol,label,attack_family,offset\n100,100.5,10.0.0.1,10.0.0.2,123,456,udp,1,UDPFlood,128\n101,102,10.0.0.1,10.0.0.2,123,456,udp,0,Benign,256\n"` | Write a UDPFlood interval at 100–100.5 and a benign interval at 101–102 for the same UDP tuple. |
| 83 | `    )` | Close the multiline call or parenthesized expression started above. |
| 84 | `    capture = tmp_path / "fixture.pcap"` | Choose a temporary PCAP file for synthetic packets. |
| 85 | `    with capture.open("wb") as stream:` | Open it in binary mode for writing. |
| 86 | `        writer = dpkt.pcap.Writer(stream)` | Use dpkt's PCAP writer to generate a standards-formatted capture. |
| 87 | `        for timestamp, port in [(100, 123), (100.2, 123), (101.2, 123), (103.2, 999)]:` | Create two attack packets, one benign packet, and one late unmatched packet with port 999. |
| 88 | `            writer.writepkt(udp_packet(sport=port), timestamp)` | Write each generated Ethernet packet with the stated capture timestamp. |
| 89 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 90 | `    class AlwaysAttack:` | Define a fake classifier to make replay outcomes predictable. |
| 91 | `        def predict(self, features):` | Expose the prediction interface expected by the replay engine. |
| 92 | `            return 1, 0.9, 0.1` | Always predict attack class 1 with fixed attack score 0.9 and artificial latency 0.1. |
| 93 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 94 | `        def learn(self, features, label, predicted, monitor=True):` | Expose the learner interface without actually training a model. |
| 95 | `            return False` | Return no drift signal from the fake learner. |
| 96 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 97 | `    run = run_replay(` | Begin an end-to-end replay call. |
| 98 | `        RunConfig(` | Construct its validated replay configuration. |
| 99 | `            mode="pcap_replay",` | Select packet-capture replay rather than CSV rows or a live collector. |
| 100 | `            input_path=str(capture),` | Point replay at the generated capture. |
| 101 | `            flow_labels_path=str(path),` | Use tuple/time flow labels as the packet truth source. |
| 102 | `            output_root=str(tmp_path / "runs"),` | Keep output evidence inside the test's temporary runs directory. |
| 103 | `            warmup_seconds=0,` | Disable warm-up so eligible windows contribute immediately to evaluation. |
| 104 | `        ),` | Close the multiline call or parenthesized expression started above; the trailing comma permits another argument/item. |
| 105 | `        fixture=True,` | Mark the run as synthetic fixture evidence. |
| 106 | `        model=AlwaysAttack(),` | Inject the deterministic AlwaysAttack classifier. |
| 107 | `    )` | Close the multiline call or parenthesized expression started above. |
| 108 | `    assert run["counts"]["evaluated"] == 3` | Require three labeled windows to be evaluated; unknown truth is not scored. |
| 109 | `    assert run["packet_label_coverage"] == {"matched": 3, "unknown": 1, "unjoinable_flow_rows": 0}` | Require three packets with matched truth, one unknown packet, and no unjoinable CSV rows. |
| 110 | `    assert run["metrics"]["packets_to_detect"]["value"] == 2` | Require detection after the two attack packets contributing to the first completed attack window. |
| 111 | `    assert run["metrics"]["detection_time_seconds"]["value"] == 1` | Require the first attack alarm at window end one second after the attack onset. |
| 112 | `    assert run["metrics"]["f1"]["value"] == 0.5` | Require window-level F1 0.5 for this fixed always-attack prediction sequence. |

## tests/test_lab.py

Tests lab measurements with subprocess replacements. These tests do not require an installed OVS bridge or packet capture and do not prove the real lab is configured correctly.

Physical lines: 37.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `from types import SimpleNamespace` | Import a minimal attribute container to stand in for the run writer. |
| 2 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 3 | `from m3.lab import LabMeasurements` | Import the OVS/OpenFlow laboratory measurement collector. |
| 4 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 5 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 6 | `def test_ovs_real_zero_vs_missing(monkeypatch, tmp_path):` | Define a test using pytest's monkeypatch replacement fixture and isolated temporary path. |
| 7 | `    writer = SimpleNamespace(` | Create a lightweight object with only the writer fields LabMeasurements needs. |
| 8 | `        path=tmp_path,` | Set the output path to the test's temporary directory. |
| 9 | `        summary={"config": {"mode": "live_sflow", "ovs_bridge": "m3s1", "openflow_port": None}},` | Configure live sFlow on bridge m3s1 and explicitly omit OpenFlow bandwidth capture. |
| 10 | `    )` | Close the multiline call or parenthesized expression started above. |
| 11 | `    lab = LabMeasurements(writer)` | Construct the measurement collector using the fake writer. |
| 12 | `    monkeypatch.setattr(` | Begin replacing the collector's subprocess runner for this test. |
| 13 | `        "m3.lab.subprocess.run", lambda *a, **kw: SimpleNamespace(stdout="OFPST_FLOW reply:\n")` | Return a valid OVS flow-reply header with no flow lines; *a and **kw accept arbitrary call arguments. |
| 14 | `    )` | Close the multiline call or parenthesized expression started above. |
| 15 | `    assert lab.sample() == 0` | Require a valid empty flow-table response to mean measured zero. |
| 16 | `    assert lab.finish(1)["flow_table_entries"]["value"] == 0` | Require the finalized flow-entry measurement to preserve that zero. |
| 17 | `    assert lab.finish(1)["openflow_bandwidth_kbps"]["value"] is None` | Require OpenFlow bandwidth to remain unavailable when no measurement port was configured. |
| 18 | `    monkeypatch.setattr("m3.lab.subprocess.run", lambda *a, **kw: SimpleNamespace(stdout="invalid"))` | Replace subprocess output with malformed text to test failed measurement parsing. |
| 19 | `    assert lab.sample() is None` | Require malformed output to yield None instead of a misleading zero. |
| 20 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 21 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 22 | `def test_ovs_counts_and_safe_argv(monkeypatch, tmp_path):` | Define a test for counted flow entries and safe subprocess invocation. |
| 23 | `    writer = SimpleNamespace(` | Create the minimum writer substitute. |
| 24 | `        path=tmp_path, summary={"config": {"mode": "live_sflow", "ovs_bridge": "m3s1"}}` | Supply the temporary path and live bridge configuration. |
| 25 | `    )` | Close the multiline call or parenthesized expression started above. |
| 26 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 27 | `    def run(args, **kwargs):` | Define a replacement subprocess runner that validates its received command and options. |
| 28 | `        assert args == ["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "m3s1"]` | Require a structured argument list selecting OpenFlow13 dump-flows on exactly bridge m3s1. |
| 29 | `        assert kwargs["timeout"] == 1 and not kwargs.get("shell")` | Require a one-second timeout and no shell execution. |
| 30 | `        return SimpleNamespace(` | Return an object shaped like subprocess.CompletedProcess for the collector. |
| 31 | `            stdout="OFPST_FLOW reply:\n cookie=0x0, priority=1\n cookie=0x1, priority=2\n"` | Provide the OVS reply header and two cookie-prefixed flow-entry rows. |
| 32 | `        )` | Close the multiline call or parenthesized expression started above. |
| 33 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 34 | `    monkeypatch.setattr("m3.lab.subprocess.run", run)` | Install the validating subprocess replacement only for this test. |
| 35 | `    lab = LabMeasurements(writer)` | Construct the collector with the writer substitute. |
| 36 | `    assert lab.sample() == 2` | Require one sample to count the two flow-entry rows. |
| 37 | `    assert lab.finish(1)["flow_table_entries"]["value"] == 2` | Require finalized output to preserve that count of two. |

## tests/test_live.py

Exercises an actual short loopback UDP collector with generated sFlow datagrams, including rate mismatch failure and raw evidence retention. This creates local sockets and a thread, but does not contact an external service.

Physical lines: 50.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `import socket` | Import UDP socket support for a loopback-only collector test. |
| 2 | `import threading` | Import threads so a local sender can run while the collector listens. |
| 3 | `import time` | Import time to pace datagrams and exercise a short live collection period. |
| 4 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 5 | `import pytest` | Import pytest's parametrization, expected-exception, and approximate-number helpers. |
| 6 | `from test_core import sflow_datagram` | Reuse the generated sFlow datagram helper from test_core. |
| 7 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 8 | `from m3.config import RunConfig` | Import the validated, immutable run configuration class. |
| 9 | `from m3.live import run_live` | Import the real live sFlow collection pipeline. |
| 10 | `from m3.store import RunRepository` | Import the saved-run reader. |
| 11 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 12 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 13 | `@pytest.mark.parametrize("rate,expected", [(1, "completed"), (10, "failed")])` | Run once with matching rate 1 expecting completion and once with rate 10 expecting failure. |
| 14 | `def test_udp_collector_health_and_raw_evidence(tmp_path, rate, expected):` | Receive the temporary directory and the current rate/expected-status parameters. |
| 15 | `    # Generated protocol fixtures test software only and stay in pytest's temporary directory.` | Document that generated packets validate software behavior and are not official dataset evidence. |
| 16 | `    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:` | Open a temporary IPv4 UDP socket as a local port probe. |
| 17 | `        probe.bind(("127.0.0.1", 0))` | Bind loopback with port 0 so the operating system chooses an available port. |
| 18 | `        port = probe.getsockname()[1]` | Read the chosen port; leaving the context closes the probe before the collector binds. |
| 19 | `    config = RunConfig(` | Start constructing the actual live collector configuration. |
| 20 | `        mode="live_sflow",` | Select live UDP sFlow ingestion. |
| 21 | `        output_root=str(tmp_path / "runs"),` | Store results under the isolated temporary directory. |
| 22 | `        sampling_rate=1,` | Declare expected sampling rate 1; rate-10 datagrams deliberately contradict it. |
| 23 | `        port=port,` | Listen on the selected ephemeral port. |
| 24 | `        duration_seconds=0.6,` | Run collection for approximately 0.6 seconds. |
| 25 | `        window_seconds=0.1,` | Aggregate data into 0.1-second windows. |
| 26 | `        warmup_seconds=0.1,` | Reserve the first 0.1 seconds as warm-up. |
| 27 | `    )` | Close the multiline call or parenthesized expression started above. |
| 28 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 29 | `    def send():` | Define the background packet-sending function. |
| 30 | `        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:` | Open a local UDP socket for sending fixture datagrams. |
| 31 | `            for _ in range(20):` | Send twenty datagrams in this background job. |
| 32 | `                time.sleep(0.04)` | Wait 0.04 seconds between sends so the collector has time to receive and form windows. |
| 33 | `                sender.sendto(sflow_datagram(rate), ("127.0.0.1", port))` | Send a generated datagram carrying the parametrized sampling rate to the loopback collector. |
| 34 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 35 | `    thread = threading.Thread(target=send)` | Create a thread that will execute send. |
| 36 | `    thread.start()` | Start sending concurrently with the collector. |
| 37 | `    try:` | Begin a block whose cleanup will wait for the sender even when collection raises. |
| 38 | `        if expected == "failed":` | Take the deliberate-rate-mismatch branch when failure is expected. |
| 39 | `            with pytest.raises(RuntimeError, match="evidence retained"):` | Require a RuntimeError whose message says evidence was retained. |
| 40 | `                run_live(config)` | Run the collector to exercise its rate-consistency failure path. |
| 41 | `        else:` | Otherwise handle the matching-rate success case. |
| 42 | `            run = run_live(config)` | Execute live collection and retain its run summary. |
| 43 | `            assert run["counts"]["unlabeled"] > 0` | Require at least one unlabeled observation because the test supplies no verified label source. |
| 44 | `            assert run["metrics"]["f1"]["value"] is None` | Require F1 to remain unavailable without truth labels. |
| 45 | `            assert run["metrics"]["telemetry_bandwidth_kbps"]["status"] == "measured"` | Require received UDP telemetry bandwidth to be classified as measured. |
| 46 | `    finally:` | Start cleanup guaranteed after either success or failure. |
| 47 | `        thread.join()` | Wait for the sender thread to finish before inspecting files and ending the test. |
| 48 | `    run = RunRepository(config.output_root).list()[0]` | Load the persisted run summary from the real repository. |
| 49 | `    assert run["status"] == expected` | Require persisted status to match completed or failed for this parameter case. |
| 50 | `    assert (tmp_path / "runs" / run["run_id"] / "sflow.datagrams").stat().st_size > 0` | Require a nonempty raw sFlow datagram file even when collection failed. |

## pyproject.toml

Defines Python packaging, supported versions, runtime and developer dependencies, the m3 console command, and pytest/Ruff defaults.

Physical lines: 30.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `[build-system]` | Open the standard Python build-system configuration table. |
| 2 | `requires = ["setuptools>=75"]` | Require setuptools version 75 or later to build the distributable package. |
| 3 | `build-backend = "setuptools.build_meta"` | Select setuptools.build_meta as the PEP 517 build backend. |
| 4 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 5 | `[project]` | Open package metadata and runtime dependency declarations. |
| 6 | `name = "m3-sdn"` | Name the installable distribution m3-sdn; Python imports still use m3. |
| 7 | `version = "0.1.0"` | Declare package version 0.1.0. |
| 8 | `description = "Reproducible sampled-telemetry SDN DDoS experiments with HAT and ADWIN"` | Provide the package description displayed by packaging tools. |
| 9 | `requires-python = ">=3.12,<3.15"` | Allow Python 3.12, 3.13, and 3.14; reject older versions and Python 3.15 or newer. |
| 10 | `dependencies = [` | Begin the runtime dependency list. |
| 11 | `  "river>=0.22,<0.24", "fastapi>=0.115,<1", "uvicorn>=0.30,<1",` | Install River for online learning, FastAPI for the API, and Uvicorn as its server, within these version ranges. |
| 12 | `  "psutil>=6,<8", "dpkt>=1.9.8,<2", "numpy>=2,<3", "matplotlib>=3.9,<4"` | Install psutil for process measurements, dpkt for packet formats, NumPy for numerics, and Matplotlib for plots. |
| 13 | `]` | Close the list started above. |
| 14 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 15 | `[project.optional-dependencies]` | Open optional dependency groups. |
| 16 | `dev = ["pytest>=8,<10", "httpx>=0.27,<1", "ruff>=0.8,<1"]` | Define the dev extra: pytest for tests, httpx for the API test client, and Ruff for linting. |
| 17 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 18 | `[project.scripts]` | Open console-command entry points. |
| 19 | `m3 = "m3.cli:main"` | Install the m3 command and route it to the main function in m3.cli. |
| 20 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 21 | `[tool.setuptools.packages.find]` | Configure setuptools package discovery. |
| 22 | `where = ["src"]` | Find Python packages below src, matching this repository's src/m3 layout. |
| 23 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 24 | `[tool.pytest.ini_options]` | Configure pytest. |
| 25 | `testpaths = ["tests"]` | Search tests for tests by default. |
| 26 | `addopts = "-q"` | Pass quiet mode by default, reducing routine test output. |
| 27 | *(blank)* | Blank line separating imports, definitions, or logical blocks; it performs no operation. |
| 28 | `[tool.ruff]` | Configure Ruff. |
| 29 | `line-length = 100` | Set Ruff's preferred maximum line length to 100 characters. |
| 30 | `target-version = "py312"` | Tell Ruff to target Python 3.12 syntax/features as the minimum supported version. |

## configs/official_csv_pilot.json

A small official-file CSV pilot configuration. The referenced local dataset and a valid matching manifest must exist. This file targets one named UDPFlood CSV; it does not establish class balance, chronology, or broad generalization.

Physical lines: 11.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `{` | Begin a dictionary object containing the following named fields. |
| 2 | `  "mode": "csv_replay",` | Select CSV flow replay. This exercises flow-row sampling and does not itself implement packet-level sFlow sampling. |
| 3 | `  "input_path": "data/raw/BS2_each_attack_csv/BS2_each_attack_csv/UDPFlood2.csv",` | Read UDPFlood2.csv from the specified local official-data download location relative to the working directory. |
| 4 | `  "manifest_path": "data/manifest.json",` | Use this manifest to verify the input file's official provenance and checksum before a normal non-fixture replay. |
| 5 | `  "sampling_rate": 1,` | Use sampling rate 1, retaining every eligible flow row. |
| 6 | `  "seed": 42,` | Use seed 42 for the Bernoulli row-selection decisions; this seed does not shuffle the CSV. |
| 7 | `  "scenario": "baseline",` | Select the baseline scenario tag. The configuration does not create a balanced benign/attack dataset or reorder rows. |
| 8 | `  "warmup_records": 1000,` | Use the first 1,000 eligible records for model warm-up; their predictions do not enter evaluated quality counts. |
| 9 | `  "max_records": 20000,` | Stop after at most 20,000 input rows, before label exclusions and sampling; the engine enforces this cap. |
| 10 | `  "output_root": "output/runs"` | Write this run's configuration, predictions, summary, and evidence beneath output/runs. |
| 11 | `}` | Close the dictionary started above. |

## configs/live_telemetry_validation.json

A 30-second local sFlow configuration with optional OVS and OpenFlow measurements. It supplies no label file or controller PID, so supervised quality and controller-specific CPU are not automatically available.

Physical lines: 14.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `{` | Begin a dictionary object containing the following named fields. |
| 2 | `  "mode": "live_sflow",` | Select the live UDP sFlow collector. |
| 3 | `  "sampling_rate": 1,` | Expect incoming exporter samples to declare sampling rate 1. |
| 4 | `  "seed": 42,` | Set the recorded/seeded run seed to 42. |
| 5 | `  "scenario": "baseline",` | Select the baseline scenario tag; this does not generate traffic or supply ground-truth labels. |
| 6 | `  "bind": "127.0.0.1",` | Bind to IPv4 loopback; this configuration receives local traffic, not all host interfaces. |
| 7 | `  "port": 6343,` | Listen on UDP port 6343 for sFlow datagrams. |
| 8 | `  "duration_seconds": 30,` | Collect for 30 seconds. |
| 9 | `  "warmup_seconds": 10,` | Use the first ten seconds for model warm-up when verified labels are available. |
| 10 | `  "window_seconds": 1,` | Create one-second sampled packet feature windows. |
| 11 | `  "ovs_bridge": "m3s1",` | Query OVS bridge m3s1 when attempting flow-table measurements. |
| 12 | `  "openflow_port": 6653,` | Use TCP port 6653 for the configured OpenFlow bandwidth measurement path, when its capture prerequisites are available. |
| 13 | `  "output_root": "output/runs"` | Store run outputs in output/runs. |
| 14 | `}` | Close the dictionary started above. |

## .gitignore

Keeps local environments, large data, and generated outputs out of new Git tracking. Ignore rules do not remove files that Git already tracks.

Physical lines: 23.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `.venv/` | Exclude the default local Python virtual environment. |
| 2 | `.venv-linux/` | Exclude the Linux-specific Python virtual environment. |
| 3 | `.venv-sdn/` | Exclude the SDN-specific Python virtual environment. |
| 4 | `.tools/` | Exclude locally installed/helper tool files. |
| 5 | `tmp/` | Exclude temporary project files. |
| 6 | `Partner Work/` | Exclude the local Partner Work directory from new Git tracking. |
| 7 | `__pycache__/` | Exclude compiled Python bytecode-cache directories. |
| 8 | `.pytest_cache/` | Exclude pytest's local cache. |
| 9 | `.ruff_cache/` | Exclude Ruff's local cache. |
| 10 | `*.egg-info/` | Exclude generated setuptools package metadata directories. |
| 11 | `frontend/node_modules/` | Exclude downloaded frontend dependencies. |
| 12 | `frontend/dist/` | Exclude generated frontend production-build files. |
| 13 | `frontend/.npm-cache/` | Exclude the frontend's local npm cache. |
| 14 | `frontend/test-artifacts/` | Exclude generated browser/test artifacts. |
| 15 | `data/raw/` | Exclude large raw dataset files. |
| 16 | `data/prepared/` | Exclude prepared dataset outputs. |
| 17 | `output/runs/` | Exclude generated run evidence/results. |
| 18 | `output/analysis/` | Exclude generated analysis outputs. |
| 19 | `output/sdn/` | Exclude generated SDN evidence/artifacts. |
| 20 | `output/pdf/` | Exclude generated PDF documents. |
| 21 | `*.pcap` | Exclude classic PCAP capture files wherever this pattern applies. |
| 22 | `*.pcapng` | Exclude PCAPNG capture files wherever this pattern applies. |
| 23 | `*.log` | Exclude log files. |

## .gitattributes

Controls Git text normalization and identifies binary artifacts.

Physical lines: 4.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `* text=auto eol=lf` | Let Git detect text files automatically and normalize checked-out text to LF line endings. |
| 2 | `*.png binary` | Treat PNG images as binary, disabling text conversion/diff behavior. |
| 3 | `*.pdf binary` | Treat PDFs as binary, preserving their bytes. |
| 4 | `*.zip binary` | Treat ZIP archives as binary, preserving their bytes. |

## frontend/.gitignore

Frontend-local rules for downloaded dependencies and generated outputs.

Physical lines: 5.

| Line | Original source | Explanation |
| --- | --- | --- |
| 1 | `node_modules/` | Exclude frontend dependency downloads. |
| 2 | `dist/` | Exclude the generated frontend build directory. |
| 3 | `.npm-cache/` | Exclude the local npm package cache. |
| 4 | `*.tsbuildinfo` | Exclude TypeScript incremental-compilation metadata. |
| 5 | `coverage/` | Exclude generated test-coverage reports. |

## Reproducibility notes

The Python dependency declarations are version ranges, not a complete exact-version environment lock. Reproducing a research run also needs the actual installed versions, input hashes, configuration, seed, software revision, and raw saved outputs. Frontend `package-lock.json` records the npm dependency tree and integrity metadata for reproducible dependency installation; its generated package entries are not manually authored application behavior and are explained by purpose rather than line by line in this guide. Markdown documents explain usage and evidence; they are prose, not executable source.


