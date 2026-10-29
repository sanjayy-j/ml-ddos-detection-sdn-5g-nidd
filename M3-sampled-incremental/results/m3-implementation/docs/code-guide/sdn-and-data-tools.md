# SDN and dataset tools: every source line explained

This guide covers the nine files listed below exactly as inspected in the working tree. Each physical source line has one numbered table row, including blank lines and closing punctuation. Source is reproduced beside its explanation so that line numbers remain meaningful even if the application later changes. These are explanations of implementation, not claims that network experiments were run during guide creation.

## How these files fit together

1. `fetch_dataset.py` obtains and verifies official bytes; its manifest provides file lineage.
2. `inspect_session_labels.py` checks whether CSV tuples have conflicting classes. This is an audit, not packet labeling.
3. `prepare_flow_labels.py` joins official labels to numerical Argus flow intervals using exact record offsets.
4. `setup_sdn.sh` provisions Linux dependencies and `preflight.py` checks them.
5. `controller.py` supplies learning-switch forwarding; `topology.py` creates a separate virtual testbed with real OVS sFlow.
6. `validate_sflow.py` checks received telemetry bytes at two sampling rates. `run_live_validation.py` checks the actual M3 collector against benign telemetry.

A publisher checksum proves that a file matches the publisher's advertised bytes. It does not prove a label is scientifically correct. A successful CSV/Argus join proves record correspondence under the checks implemented here. It does not prove every PCAP packet has an unambiguous label. Live benign telemetry proves that the collection path runs. It does not measure attack detection quality.

## Syntax used repeatedly

`with` closes files/sockets after a block, even on errors. `try/finally` arranges cleanup. `subprocess.Popen` starts a child asynchronously; `subprocess.run` waits. A subprocess argument list passes each argument separately rather than composing a shell command. `poll() is None` means a process is still running. `time.monotonic()` is for elapsed deadlines; `time.time()` is wall-clock epoch time. Python indentation defines blocks. A trailing comma is allowed in multiline calls and containers.

| Source file | Physical lines |
| --- | ---: |
| `scripts/fetch_dataset.py` | 250 |
| `scripts/setup_sdn.sh` | 23 |
| `sdn/controller.py` | 71 |
| `sdn/inspect_session_labels.py` | 105 |
| `sdn/preflight.py` | 34 |
| `sdn/prepare_flow_labels.py` | 252 |
| `sdn/run_live_validation.py` | 109 |
| `sdn/topology.py` | 133 |
| `sdn/validate_sflow.py` | 133 |

## scripts/fetch_dataset.py

Downloads selected official 5G-NIDD release files from Fairdata/Etsin, verifies publisher size/SHA256, extracts selected ZIP members, and writes provenance in data/manifest.json. Uses Python standard-library modules only and network access to the publisher. It does not clean training data, train a model, establish chronological ordering, or label packets.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Fetch only the authors' public Fairdata release, checking publisher SHA256.</code> | Docstring states the downloader's provenance and publisher SHA256 goal. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>Usage: python scripts/fetch_dataset.py [--captures] [--list]</code> | Document the default command and optional capture/list switches. |
| 4 | <code>Requires no third-party packages. ZIP members are preserved byte-for-byte.</code> | State that only the standard library is required and extraction preserves member contents. |
| 5 | <code>"""</code> | Close the module documentation string. |
| 6 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 7 | <code>from __future__ import annotations</code> | Postpone evaluation of annotations so types can be described without eager evaluation. |
| 8 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 9 | <code>import argparse</code> | Import command-line option parsing. |
| 10 | <code>import hashlib</code> | Import SHA256 hashing. |
| 11 | <code>import json</code> | Import JSON request/manifest encoding. |
| 12 | <code>import shutil</code> | Import disk-space inspection and stream copying. |
| 13 | <code>import sys</code> | Import stderr access. |
| 14 | <code>import time</code> | Import UTC timestamp formatting. |
| 15 | <code>import urllib.parse</code> | Import URL parsing and query encoding. |
| 16 | <code>import urllib.request</code> | Import HTTP request and response handling. |
| 17 | <code>import zipfile</code> | Import ZIP inspection and extraction streams. |
| 18 | <code>from pathlib import Path</code> | Import portable filesystem paths. |
| 19 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 20 | <code>ROOT = Path(__file__).resolve().parents[1]</code> | Resolve this script and select its grandparent as repository root. |
| 21 | <code>DATASET_ID = "9d13ef28-2ca7-44b0-9950-225359afac65"</code> | Identify the exact Fairdata dataset release. |
| 22 | <code>DOI = "10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361"</code> | Record the release DOI for provenance. |
| 23 | <code>PAGE = f"https://etsin.fairdata.fi/dataset/{DATASET_ID}"</code> | Build its Etsin landing page URL using an f-string. |
| 24 | <code>LIST_URL = "https://metax.fairdata.fi/v3/directories?" + urllib.parse.urlencode(</code> | Start constructing the metadata directory-list URL by encoding query parameters. |
| 25 | <code>    {</code> | Open the dictionary of Fairdata metadata query parameters passed to urlencode. |
| 26 | <code>        "path": "/",</code> | Request the dataset's root directory. |
| 27 | <code>        "storage_service": "ida",</code> | Identify the IDA storage service. |
| 28 | <code>        "csc_project": "2006938",</code> | Select the publisher's CSC project. |
| 29 | <code>        "dataset": DATASET_ID,</code> | Restrict listing to the specified dataset identifier. |
| 30 | <code>        "pagination": "false",</code> | Request an unpaginated response. |
| 31 | <code>    }</code> | Close the dictionary begun above. |
| 32 | <code>)</code> | Close the multiline call or parenthesized expression begun above. |
| 33 | <code>AUTHORIZE = "https://etsin.fairdata.fi/api/download/authorize"</code> | Define Etsin's public download authorization endpoint. |
| 34 | <code>DEFAULT = ["README.pdf", "Combined.zip", "BS1_each_attack_csv.zip", "BS2_each_attack_csv.zip"]</code> | Choose the README, combined data and two base-station CSV archives as defaults. |
| 35 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 36 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 37 | <code>def request_json(url: str, body: dict &#124; None = None) -&gt; dict:</code> | Define an HTTP JSON helper; body can be a dictionary or None and the documented return is a dictionary. |
| 38 | <code>    data = None if body is None else json.dumps(body).encode()</code> | Use no request body for GET; otherwise encode a JSON request body into bytes. |
| 39 | <code>    request = urllib.request.Request(</code> | Begin constructing a urllib request. |
| 40 | <code>        url,</code> | Pass the target URL. |
| 41 | <code>        data=data,</code> | Pass optional body bytes, which makes urllib choose POST when present. |
| 42 | <code>        headers={</code> | Begin HTTP headers. |
| 43 | <code>            "User-Agent": "M3-5G-NIDD-research/1.0",</code> | Identify this research downloader in User-Agent. |
| 44 | <code>            "Content-Type": "application/json",</code> | Describe the body as JSON. |
| 45 | <code>        },</code> | Close the dictionary begun above; the trailing comma separates it from the next argument/item. |
| 46 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 47 | <code>    with urllib.request.urlopen(request, timeout=90) as response:</code> | Open the HTTP response with a 90-second socket timeout and close it after the block. |
| 48 | <code>        return json.load(response)</code> | Parse the response body directly as JSON. |
| 49 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 50 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 51 | <code>def digest(path: Path) -&gt; str:</code> | Define a helper returning a file's SHA256 hexadecimal digest. |
| 52 | <code>    result = hashlib.sha256()</code> | Create a fresh incremental SHA256 accumulator. |
| 53 | <code>    with path.open("rb") as stream:</code> | Open the file as binary bytes. |
| 54 | <code>        for chunk in iter(lambda: stream.read(1024 * 1024), b""):</code> | Read 1 MiB chunks using iter(callable, sentinel), stopping when read returns empty bytes. |
| 55 | <code>            result.update(chunk)</code> | Feed each chunk into SHA256 without loading the entire file. |
| 56 | <code>    return result.hexdigest()</code> | Return the digest as hexadecimal text. |
| 57 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 58 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 59 | <code>def save_manifest(path: Path, manifest: dict) -&gt; None:</code> | Define manifest saving with existing-entry preservation. |
| 60 | <code>    if path.exists():</code> | Check for a previously saved manifest. |
| 61 | <code>        current = json.loads(path.read_text(encoding="utf-8"))</code> | Read UTF-8 JSON into a dictionary. |
| 62 | <code>        by_path = {item["path"]: item for item in current.get("files", [])}</code> | Index prior file records by relative path; missing files defaults to an empty list. |
| 63 | <code>        by_path.update({item["path"]: item for item in manifest.get("files", [])})</code> | Merge supplied records, letting new records for the same path replace old ones. |
| 64 | <code>        manifest["files"] = list(by_path.values())</code> | Store merged records as a list. |
| 65 | <code>    temporary = path.with_suffix(".json.tmp")</code> | Use a sibling .json.tmp file for staging the manifest. |
| 66 | <code>    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")</code> | Write readable UTF-8 JSON and a final newline. |
| 67 | <code>    temporary.replace(path)</code> | Replace the destination with the staged file, reducing incomplete-manifest exposure. |
| 68 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 69 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 70 | <code>def fetch(record: dict, target: Path) -&gt; None:</code> | Define retrieval and verification for one official metadata record. |
| 71 | <code>    expected = record["checksum"].removeprefix("sha256:")</code> | Remove a literal sha256: prefix to get the expected hexadecimal digest. |
| 72 | <code>    if target.exists():</code> | Check whether the target already exists. |
| 73 | <code>        if target.stat().st_size == record["size"] and digest(target) == expected:</code> | Require both the official size and digest to match before reusing it. |
| 74 | <code>            print(f"Verified existing {target.name}", flush=True)</code> | Report a verified existing file immediately using flush=True. |
| 75 | <code>            return</code> | Skip redownloading this verified target. |
| 76 | <code>        raise ValueError(</code> | Begin rejecting an existing file that failed verification. |
| 77 | <code>            f"Existing {target} does not match the official checksum; preserve it and investigate."</code> | Explain the mismatch and preserve that file for investigation. |
| 78 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 79 | <code>    # This is the public authorization API used by Etsin's download button.</code> | Comment identifies the portal's download-button API. |
| 80 | <code>    # Its signed URL is transient and is deliberately not saved to the manifest.</code> | Comment explains why an expiring signed URL is excluded from persistent provenance. |
| 81 | <code>    transient_url = request_json(AUTHORIZE, {"cr_id": DATASET_ID, "file": record["pathname"]})[</code> | Request authorization for this dataset/file pathname, then index the response. |
| 82 | <code>        "url"</code> | Select the returned temporary URL. |
| 83 | <code>    ]</code> | Close the list or indexing expression begun above. |
| 84 | <code>    if urllib.parse.urlparse(transient_url).hostname != "download.fairdata.fi":</code> | Allow only the expected download.fairdata.fi hostname; this does not constrain a later HTTP redirect. |
| 85 | <code>        raise ValueError("Portal returned an unexpected download host")</code> | Reject an unexpected authorization-response host. |
| 86 | <code>    partial = target.with_suffix(target.suffix + ".partial")</code> | Create a sibling filename ending in the original suffix plus .partial. |
| 87 | <code>    if partial.exists():</code> | Detect a partial download left from an earlier attempt. |
| 88 | <code>        raise ValueError(</code> | Begin rejecting ambiguous continuation of an earlier partial download. |
| 89 | <code>            f"Partial download exists at {partial}; preserve or remove it before retrying."</code> | Tell the operator to resolve the saved partial before retrying. |
| 90 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 91 | <code>    print(f"Downloading {target.name} ({record['size']:,} bytes)", flush=True)</code> | Print the filename and comma-formatted expected byte count. |
| 92 | <code>    with (</code> | Begin two simultaneous managed resources. |
| 93 | <code>        urllib.request.urlopen(transient_url, timeout=120) as response,</code> | Open the download with a 120-second socket timeout. |
| 94 | <code>        partial.open("xb") as output,</code> | Exclusively create a binary partial file; xb refuses to overwrite an existing file. |
| 95 | <code>    ):</code> | Close the multiline call or parenthesized expression begun above; the colon begins its indented block. |
| 96 | <code>        while chunk := response.read(1024 * 1024):</code> | Use the walrus operator to read/store a chunk and stop at EOF. |
| 97 | <code>            output.write(chunk)</code> | Write the downloaded chunk unchanged. |
| 98 | <code>    if partial.stat().st_size != record["size"] or digest(partial) != expected:</code> | Reject the file if either its byte count or digest is wrong. |
| 99 | <code>        raise ValueError(f"Publisher checksum verification failed for {partial}")</code> | Raise a publisher-verification error while retaining the partial. |
| 100 | <code>    partial.rename(target)</code> | Rename the verified partial to its final target path. |
| 101 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 102 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 103 | <code>def entry(path: Path, record: dict, parent: str &#124; None = None) -&gt; dict:</code> | Define a manifest record builder for an archive or an extracted member. |
| 104 | <code>    item = {</code> | Begin the provenance dictionary. |
| 105 | <code>        "path": path.relative_to(ROOT).as_posix(),</code> | Store a repository-relative POSIX-style path for portability. |
| 106 | <code>        "sha256": digest(path),</code> | Compute the local file digest. |
| 107 | <code>        "verification_status": "verified",</code> | Mark this record verified after the preceding checks. |
| 108 | <code>        "size_bytes": path.stat().st_size,</code> | Record actual file size. |
| 109 | <code>        "download_url": AUTHORIZE,</code> | Record the stable authorization endpoint rather than a temporary signed URL. |
| 110 | <code>        "official_filename": record["filename"],</code> | Preserve the publisher's original filename. |
| 111 | <code>        "official_file_id": record["id"],</code> | Preserve the publisher's file identifier. |
| 112 | <code>        "official_path": record["pathname"],</code> | Preserve its storage pathname. |
| 113 | <code>    }</code> | Close the dictionary begun above. |
| 114 | <code>    if parent:</code> | Distinguish extracted members by presence of a parent archive digest. |
| 115 | <code>        item.update(</code> | Begin attaching extraction provenance. |
| 116 | <code>            parent_sha256=parent, transformations=["ZIP extraction only; member bytes unchanged"]</code> | Record the parent SHA256 and declare that only ZIP extraction changed representation. |
| 117 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 118 | <code>    else:</code> | Handle the downloaded original archive/document. |
| 119 | <code>        item["publisher_sha256"] = record["checksum"].removeprefix("sha256:")</code> | Preserve the publisher's advertised digest separately. |
| 120 | <code>    return item</code> | Return the completed provenance entry. |
| 121 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 122 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 123 | <code>def main() -&gt; int:</code> | Define the CLI entry point with an integer exit status. |
| 124 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Use the module docstring for command help. |
| 125 | <code>    parser.add_argument(</code> | Begin registering the capture switch. |
| 126 | <code>        "--captures",</code> | Name the optional switch --captures. |
| 127 | <code>        action="store_true",</code> | Make it a Boolean that becomes true when supplied. |
| 128 | <code>        help="Also obtain both GTP-removed capture archives (~3.9 GB)",</code> | Explain that it adds both large GTP-removed archives. |
| 129 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 130 | <code>    parser.add_argument(</code> | Begin registering a selected-file option. |
| 131 | <code>        "--file",</code> | Name the option --file. |
| 132 | <code>        action="append",</code> | Append repeated values rather than replacing earlier ones. |
| 133 | <code>        dest="files",</code> | Expose the collected values as args.files. |
| 134 | <code>        help="Download a selected official filename instead of defaults (repeatable)",</code> | Explain that explicit filenames replace the default download set. |
| 135 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 136 | <code>    parser.add_argument(</code> | Begin registering metadata-list-only behavior. |
| 137 | <code>        "--list", action="store_true", help="Print official filenames and sizes only"</code> | Create a Boolean --list option and its help text. |
| 138 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 139 | <code>    args = parser.parse_args()</code> | Parse process command-line arguments. |
| 140 | <code>    raw = ROOT / "data" / "raw"</code> | Choose data/raw under the repository. |
| 141 | <code>    raw.mkdir(parents=True, exist_ok=True)</code> | Create raw-data folders if needed; this also happens for --list. |
| 142 | <code>    manifest_path = ROOT / "data" / "manifest.json"</code> | Choose data/manifest.json as the provenance store. |
| 143 | <code>    manifest = {</code> | Begin a new manifest template. |
| 144 | <code>        "dataset": "5G-NIDD",</code> | Name the dataset 5G-NIDD. |
| 145 | <code>        "doi": DOI,</code> | Copy the release DOI. |
| 146 | <code>        "source_url": PAGE,</code> | Copy the source landing page. |
| 147 | <code>        "license": "CC-BY-4.0",</code> | Record the license string declared by this code; this is not a live license lookup. |
| 148 | <code>        "files": [],</code> | Initialize file records. |
| 149 | <code>        "status": "blocked",</code> | Default to blocked so incomplete work cannot accidentally report success. |
| 150 | <code>        "notes": [],</code> | Initialize explanatory notes. |
| 151 | <code>    }</code> | Close the dictionary begun above. |
| 152 | <code>    if manifest_path.exists():</code> | Check for previous provenance. |
| 153 | <code>        previous = json.loads(manifest_path.read_text(encoding="utf-8"))</code> | Read previous UTF-8 manifest JSON. |
| 154 | <code>        manifest["files"] = previous.get("files", [])</code> | Preserve its file entries, while template metadata and notes start fresh. |
| 155 | <code>    try:</code> | Start handling expected retrieval/verification errors. |
| 156 | <code>        listing = request_json(LIST_URL)</code> | Fetch the official metadata listing. |
| 157 | <code>        records = {record["filename"]: record for record in listing["files"]}</code> | Map filename to metadata record for direct selection. |
| 158 | <code>        if args.list:</code> | Branch when the user only wants a listing. |
| 159 | <code>            print(</code> | Begin printing the listing. |
| 160 | <code>                json.dumps(</code> | Serialize a readable JSON array. |
| 161 | <code>                    [</code> | Open the list comprehension of official file summaries to serialize as JSON. |
| 162 | <code>                        {</code> | Open one file-summary dictionary produced by that comprehension. |
| 163 | <code>                            "filename": r["filename"],</code> | Show each original filename. |
| 164 | <code>                            "size_bytes": r["size"],</code> | Show the publisher's byte count. |
| 165 | <code>                            "sha256": r["checksum"],</code> | Show the publisher's checksum field. |
| 166 | <code>                        }</code> | Close the dictionary begun above. |
| 167 | <code>                        for r in records.values()</code> | Generate one row for each metadata record. |
| 168 | <code>                    ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 169 | <code>                    indent=2,</code> | Indent JSON by two spaces. |
| 170 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 171 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 172 | <code>            return 0</code> | Exit successfully without downloading or saving a new manifest. |
| 173 | <code>        manifest["metadata_url"] = LIST_URL</code> | Record which metadata endpoint supplied the listing. |
| 174 | <code>        manifest["retrieved_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())</code> | Record retrieval time in UTC ISO-style text; gmtime avoids local timezone ambiguity. |
| 175 | <code>        names = (args.files or DEFAULT) + (</code> | Choose explicit filenames when present, otherwise defaults, and append optional captures. |
| 176 | <code>            ["BS1_GTP_removed.zip", "BS2 GTP removed.zip"] if args.captures else []</code> | Add the exact two capture filenames only when --captures is set. |
| 177 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 178 | <code>        for name in names:</code> | Process requested official files sequentially. |
| 179 | <code>            record = records[name]</code> | Look up the requested name; an absent filename raises KeyError. |
| 180 | <code>            target = raw / name</code> | Place its downloaded original under data/raw. |
| 181 | <code>            fetch(record, target)</code> | Download or verify the existing file. |
| 182 | <code>            new_entries = [entry(target, record)]</code> | Create provenance for that original. |
| 183 | <code>            if target.suffix == ".zip":</code> | Extract only files whose final suffix is .zip. |
| 184 | <code>                parent = digest(target)</code> | Compute the parent archive digest for extracted-member lineage. |
| 185 | <code>                destination = raw / target.stem</code> | Choose an extraction folder from the archive basename without .zip. |
| 186 | <code>                with zipfile.ZipFile(target) as archive:</code> | Open the ZIP as a managed resource. |
| 187 | <code>                    members = [member for member in archive.infolist() if not member.is_dir()]</code> | Collect non-directory members. |
| 188 | <code>                    if sum(member.file_size for member in members) &gt; 8 * 1024**3:</code> | Apply restricted extraction when total uncompressed size exceeds eight GiB. |
| 189 | <code>                        members = [</code> | Begin building the restricted member list. |
| 190 | <code>                            member</code> | Retain the original ZipInfo member object. |
| 191 | <code>                            for member in members</code> | Iterate the archive's selected members. |
| 192 | <code>                            if any(</code> | Accept a member if any allowed text fragment appears in its filename. |
| 193 | <code>                                name in member.filename.lower()</code> | Compare against the lowercase member filename. |
| 194 | <code>                                for name in ("icmp", "udp", "synflood")</code> | Restrict to icmp, udp and synflood name fragments. |
| 195 | <code>                            )</code> | Close the multiline call or parenthesized expression begun above. |
| 196 | <code>                        ]</code> | Close the list or indexing expression begun above. |
| 197 | <code>                        manifest["notes"].append(</code> | Begin recording the restricted-extraction reason. |
| 198 | <code>                            "Large capture archive: extraction limited to network-flood members."</code> | Explain that large captures only extract network-flood members. |
| 199 | <code>                        )</code> | Close the multiline call or parenthesized expression begun above. |
| 200 | <code>                    required = sum(</code> | Begin estimating additional storage required. |
| 201 | <code>                        member.file_size</code> | Add the member's declared uncompressed byte count. |
| 202 | <code>                        for member in members</code> | Visit selected members. |
| 203 | <code>                        if not (destination / member.filename).exists()</code> | Only count members whose destination does not already exist. |
| 204 | <code>                    )</code> | Close the multiline call or parenthesized expression begun above. |
| 205 | <code>                    if required + 1024**3 &gt; shutil.disk_usage(raw).free:</code> | Require free space for new members plus a one-GiB reserve. |
| 206 | <code>                        raise ValueError(</code> | Begin reporting insufficient free space. |
| 207 | <code>                            "Insufficient disk space to extract safely with a 1GB reserve; verified archive retained."</code> | Explain that the verified downloaded archive is retained. |
| 208 | <code>                        )</code> | Close the multiline call or parenthesized expression begun above. |
| 209 | <code>                    for member in members:</code> | Visit each selected ZIP member. |
| 210 | <code>                        if member.is_dir():</code> | Recheck for a directory entry, redundant with initial filtering. |
| 211 | <code>                            continue</code> | Skip directory entries defensively. |
| 212 | <code>                        member_path = destination / member.filename</code> | Construct the target member path. |
| 213 | <code>                        if not member_path.resolve().is_relative_to(destination.resolve()):</code> | Resolve paths and require the member to remain beneath the extraction directory, preventing ../ traversal. |
| 214 | <code>                            raise ValueError("Archive contains an unsafe path")</code> | Reject an unsafe archive path. |
| 215 | <code>                        member_path.parent.mkdir(parents=True, exist_ok=True)</code> | Create the member's parent folders. |
| 216 | <code>                        with archive.open(member) as source:</code> | Open a decompressed member stream. |
| 217 | <code>                            checksum = hashlib.sha256()</code> | Create a digest accumulator for the member's actual decompressed bytes. |
| 218 | <code>                            for chunk in iter(lambda: source.read(1024 * 1024), b""):</code> | Read the member in one-MiB chunks. |
| 219 | <code>                                checksum.update(chunk)</code> | Hash each member chunk. |
| 220 | <code>                        if member_path.exists() and digest(member_path) != checksum.hexdigest():</code> | If an extracted file already exists, require it to match the archive member's content. |
| 221 | <code>                            raise ValueError(f"Existing extracted member differs: {member_path}")</code> | Reject a differing extracted file without replacing it. |
| 222 | <code>                        if not member_path.exists():</code> | Only create a member that is not already present. |
| 223 | <code>                            with archive.open(member) as source, member_path.open("xb") as output:</code> | Open the archive member and exclusively create its binary output. |
| 224 | <code>                                shutil.copyfileobj(source, output, 1024 * 1024)</code> | Copy decompressed member bytes with a one-MiB buffer. |
| 225 | <code>                        new_entries.append(entry(member_path, record, parent))</code> | Add member provenance pointing to the archive's digest. |
| 226 | <code>            replaced = {item["path"] for item in new_entries}</code> | Collect all paths produced by this archive/document. |
| 227 | <code>            manifest["files"] = [</code> | Begin replacing only matching manifest entries. |
| 228 | <code>                item for item in manifest["files"] if item["path"] not in replaced</code> | Retain older entries whose paths are not in this update. |
| 229 | <code>            ] + new_entries</code> | Append the newly verified entries. |
| 230 | <code>            save_manifest(manifest_path, manifest)</code> | Checkpoint manifest progress after each requested official file. |
| 231 | <code>        manifest["status"] = "verified"</code> | Mark the requested download operation verified after its loop finishes. |
| 232 | <code>        manifest["notes"] += [</code> | Begin appending interpretation/provenance notes. |
| 233 | <code>            "Publisher SHA256 checked for each downloaded archive. Extracted files have local SHA256 and parent archive provenance.",</code> | Explain publisher archive verification versus local extracted-member hashes. |
| 234 | <code>            "Combined.csv order must not be claimed chronological without further evidence.",</code> | Explicitly reject an unsupported claim that combined CSV order is chronological. |
| 235 | <code>            "Capture filenames alone do not provide packet-level attack ground truth.",</code> | Explicitly reject deriving per-packet attack labels from capture filenames. |
| 236 | <code>        ]</code> | Close the list or indexing expression begun above. |
| 237 | <code>        if not any("GTP" in name for name in names):</code> | Check whether any requested filename contains GTP. |
| 238 | <code>            manifest["notes"].append(</code> | Begin a note about absent captures. |
| 239 | <code>                "Packet capture archives have not been downloaded. Use --captures when needed."</code> | Tell the operator that --captures obtains packet archives. |
| 240 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 241 | <code>    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:</code> | Catch OS, validation, missing-field/file and invalid-ZIP errors; other exception types still propagate. |
| 242 | <code>        manifest["notes"].append(f"Download blocked: {type(error).__name__}: {error}")</code> | Record error type and message as a blocked-download note. |
| 243 | <code>        print(manifest["notes"][-1], file=sys.stderr)</code> | Print the most recent failure note to stderr. |
| 244 | <code>    save_manifest(manifest_path, manifest)</code> | Save final progress, whether successful or blocked. |
| 245 | <code>    print(f"Saved {manifest_path}")</code> | Print the manifest destination. |
| 246 | <code>    return 0 if manifest["status"] == "verified" else 1</code> | Return zero only for verified status; otherwise return one. |
| 247 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 248 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 249 | <code>if __name__ == "__main__":</code> | Execute the CLI only when this module is run directly. |
| 250 | <code>    raise SystemExit(main())</code> | Turn main's return value into the process exit status. |

## scripts/setup_sdn.sh

Provisions a Linux/Ubuntu or WSL SDN environment. Requires root, package-network access and a Linux service environment; installs OVS, Mininet, capture/replay and Argus tooling, a project-local uv, Python 3.12, and the editable project. This installer changes the system and executes a downloaded uv installer. The guide explains it without executing it.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>#!/usr/bin/env bash</code> | Shebang selects bash through PATH when executed directly. |
| 2 | <code># Provision only the isolated Linux/WSL environment for this project.</code> | Comment states this installer targets the project's Linux/WSL environment. |
| 3 | <code>set -euo pipefail</code> | Abort on failing commands, undefined variables, or failing pipeline stages. |
| 4 | <code>project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." &amp;&amp; pwd)"</code> | Find this script's directory via BASH_SOURCE[0], move one parent up, and store its absolute working path; quoting preserves spaces. |
| 5 | <code>if [[ "$(id -u)" != 0 ]]; then</code> | Compare numeric user ID with root's ID 0. |
| 6 | <code>  echo 'Run this installer with sudo inside Ubuntu.' &gt;&amp;2</code> | Print the sudo requirement to standard error using >&2. |
| 7 | <code>  exit 1</code> | Return failure exit status 1. |
| 8 | <code>fi</code> | Close the root-check conditional. |
| 9 | <code>apt-get update</code> | Refresh Ubuntu's package index; this modifies the Linux environment. |
| 10 | <code>apt-get install -y openvswitch-switch mininet iproute2 iputils-ping tcpdump tcpreplay curl python3-venv argus-client</code> | Install OVS switching, Mininet emulation, network/ping tools, packet capture/replay tools, curl, virtual environments, and the Argus reader. |
| 11 | <code>if [[ ! -x "$project_root/.tools/uv" ]]; then</code> | Test whether the project-local uv executable is missing or not executable. |
| 12 | <code>  curl --fail --location https://astral.sh/uv/install.sh &#124; env UV_INSTALL_DIR="$project_root/.tools" UV_NO_MODIFY_PATH=1 sh</code> | Download and execute Astral's installer; environment settings place uv under .tools and prevent shell PATH modification. This line executes downloaded code. |
| 13 | <code>fi</code> | Close the uv-install conditional. |
| 14 | <code>sdn_env="${M3_SDN_ENV:-/opt/m3-sdn}"</code> | Choose M3_SDN_ENV when set and nonempty; otherwise use /opt/m3-sdn. |
| 15 | <code>"$project_root/.tools/uv" python install 3.12</code> | Ask uv to install/manage Python 3.12. |
| 16 | <code>if [[ ! -x "$sdn_env/bin/python" ]]; then</code> | Check whether the selected virtual environment already has an executable Python. |
| 17 | <code>  "$project_root/.tools/uv" venv --python 3.12 "$sdn_env"</code> | Create that virtual environment with Python 3.12. |
| 18 | <code>fi</code> | Close the environment-creation conditional. |
| 19 | <code>"$project_root/.tools/uv" pip install --python "$sdn_env/bin/python" \</code> | Start installing packages into the selected Python; trailing backslash continues the shell command. |
| 20 | <code>  'os-ken==3.1.1' 'setuptools&lt;81' 'mininet==2.3.0.dev6'</code> | Pin OS-Ken 3.1.1 and Mininet 2.3.0.dev6, and constrain setuptools below 81 for compatibility. |
| 21 | <code>"$project_root/.tools/uv" pip install --python "$sdn_env/bin/python" -e "$project_root"</code> | Install this repository in editable mode, so its Python source changes are used without reinstalling it. |
| 22 | <code>service openvswitch-switch start</code> | Start the Open vSwitch service. |
| 23 | <code>"$sdn_env/bin/python" "$project_root/sdn/preflight.py"</code> | Run prerequisite checks with the SDN environment's Python; its exit code becomes this script's final status. |

## sdn/controller.py

OS-Ken Ethernet learning-switch application. Requires the OS-Ken environment and an OpenFlow 1.3 switch. On switch connection, installs a table-miss rule; on unknown destinations, floods; on known destinations, installs a 30-second-idle learned rule. M3 and the attack labels do not enter forwarding rules. There is no attack-blocking or mitigation logic in this file.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Learning-switch controller for the isolated M3 topology (OpenFlow 1.3).</code> | Docstring introduces an OpenFlow 1.3 Ethernet learning switch. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>Run: /opt/m3-sdn/bin/osken-manager --ofp-tcp-listen-port 6653 sdn/controller.py</code> | Document the OS-Ken launch command and listening port 6653. |
| 4 | <code>The model and labels never enter the controller's forwarding rules.</code> | State that model predictions and ground truth never drive forwarding in this controller. |
| 5 | <code>"""</code> | Close the module documentation string. |
| 6 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 7 | <code>from typing import ClassVar</code> | Import ClassVar to identify a type annotation that belongs to the class. |
| 8 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 9 | <code>from os_ken.base import app_manager</code> | Import OS-Ken's application base class. |
| 10 | <code>from os_ken.controller import ofp_event</code> | Import OpenFlow event classes. |
| 11 | <code>from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls</code> | Import connection-state constants and the event-handler decorator. |
| 12 | <code>from os_ken.lib.packet import ether_types, ethernet, packet</code> | Import Ethernet parsing, packet decoding and EtherType constants. |
| 13 | <code>from os_ken.ofproto import ofproto_v1_3</code> | Import the OpenFlow 1.3 protocol version definitions. |
| 14 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 15 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 16 | <code>class M3LearningSwitch(app_manager.OSKenApp):</code> | Define an OS-Ken application by inheriting OSKenApp. |
| 17 | <code>    OFP_VERSIONS: ClassVar[list[int]] = [ofproto_v1_3.OFP_VERSION]</code> | Advertise only OpenFlow 1.3; ClassVar[list[int]] describes a class-level list of integers. |
| 18 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 19 | <code>    def __init__(self, *args, **kwargs):</code> | Constructor accepts arbitrary positional and keyword arguments required by the framework. |
| 20 | <code>        super().__init__(*args, **kwargs)</code> | Initialize the framework superclass with those same arguments. |
| 21 | <code>        self.mac_to_port = {}</code> | Create a mapping from switch ID to learned MAC-address/port mappings. |
| 22 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 23 | <code>    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)</code> | Register the following method for switch-feature events during configuration. |
| 24 | <code>    def switch_features(self, event):</code> | Define the initial switch-configuration handler. |
| 25 | <code>        datapath = event.msg.datapath</code> | Extract the switch connection object from the event message. |
| 26 | <code>        parser, proto = datapath.ofproto_parser, datapath.ofproto</code> | Get that switch's message constructors and protocol constants. |
| 27 | <code>        actions = [parser.OFPActionOutput(proto.OFPP_CONTROLLER, proto.OFPCML_NO_BUFFER)]</code> | Create an action sending unmatched traffic to the controller with full packet data instead of relying on switch buffering. |
| 28 | <code>        self.install(datapath, 0, parser.OFPMatch(), actions)</code> | Install priority-zero match-all table-miss forwarding to the controller. |
| 29 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 30 | <code>    def install(self, datapath, priority, match, actions):</code> | Define a reusable flow-installation helper. |
| 31 | <code>        parser = datapath.ofproto_parser</code> | Read the connected switch's OpenFlow message constructors. |
| 32 | <code>        instruction = parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)</code> | Wrap output actions in an APPLY_ACTIONS instruction. |
| 33 | <code>        datapath.send_msg(</code> | Send the constructed flow modification over the controller connection. |
| 34 | <code>            parser.OFPFlowMod(</code> | Begin constructing an OpenFlow flow modification. |
| 35 | <code>                datapath=datapath,</code> | Associate this rule with the target switch. |
| 36 | <code>                priority=priority,</code> | Use the caller-provided rule priority. |
| 37 | <code>                idle_timeout=30 if priority else 0,</code> | Expire learned priority-nonzero rules after 30 idle seconds; preserve the priority-zero miss rule indefinitely. |
| 38 | <code>                match=match,</code> | Use the caller's packet-field match. |
| 39 | <code>                instructions=[instruction],</code> | Attach the single action instruction. |
| 40 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 41 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 42 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 43 | <code>    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)</code> | Register the following handler for packet-in events on established switch connections. |
| 44 | <code>    def packet_in(self, event):</code> | Define the packet-in handler. |
| 45 | <code>        message = event.msg</code> | Extract the actual OpenFlow message. |
| 46 | <code>        datapath = message.datapath</code> | Find which switch sent it. |
| 47 | <code>        parser, proto = datapath.ofproto_parser, datapath.ofproto</code> | Get message constructors and protocol constants for that switch. |
| 48 | <code>        incoming = message.match["in_port"]</code> | Read the switch ingress port from the message match. |
| 49 | <code>        header = packet.Packet(message.data).get_protocol(ethernet.ethernet)</code> | Decode bytes as an Ethernet packet and obtain the Ethernet header. |
| 50 | <code>        if header is None or header.ethertype == ether_types.ETH_TYPE_LLDP:</code> | Reject packets without an Ethernet header and LLDP discovery frames. |
| 51 | <code>            return</code> | Return immediately without forwarding those rejected frames. |
| 52 | <code>        addresses = self.mac_to_port.setdefault(datapath.id, {})</code> | Get or create the MAC table for this switch ID using setdefault. |
| 53 | <code>        addresses[header.src] = incoming</code> | Learn that the source MAC is reachable through the ingress port. |
| 54 | <code>        outgoing = addresses.get(header.dst, proto.OFPP_FLOOD)</code> | Choose the destination's learned port, otherwise use OpenFlow flooding. |
| 55 | <code>        actions = [parser.OFPActionOutput(outgoing)]</code> | Build the output action for the selected port. |
| 56 | <code>        if outgoing != proto.OFPP_FLOOD:</code> | Install a learned rule only when the destination port is known. |
| 57 | <code>            self.install(</code> | Begin calling the flow-installation helper. |
| 58 | <code>                datapath,</code> | Pass the current switch connection. |
| 59 | <code>                1,</code> | Give learned forwarding priority 1, higher than table-miss priority 0. |
| 60 | <code>                parser.OFPMatch(in_port=incoming, eth_src=header.src, eth_dst=header.dst),</code> | Match ingress port plus source and destination Ethernet addresses. |
| 61 | <code>                actions,</code> | Pass the output actions selected above. |
| 62 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 63 | <code>        datapath.send_msg(</code> | Send a packet-out so the current packet is forwarded immediately. |
| 64 | <code>            parser.OFPPacketOut(</code> | Begin constructing the packet-out message. |
| 65 | <code>                datapath=datapath,</code> | Target the current switch connection. |
| 66 | <code>                buffer_id=message.buffer_id,</code> | Pass through the packet's switch buffer ID. |
| 67 | <code>                in_port=incoming,</code> | Supply the packet ingress port. |
| 68 | <code>                actions=actions,</code> | Attach the output action. |
| 69 | <code>                data=message.data if message.buffer_id == proto.OFP_NO_BUFFER else None,</code> | Include original bytes only when the switch did not buffer the packet; otherwise identify the buffered packet by ID. |
| 70 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 71 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |

## sdn/inspect_session_labels.py

Audits official CSV tuples before considering packet-label matching. Uses standard-library CSV, local service lookup and JSON. Produces one JSON report per input CSV, including conflicting labels and unsupported rows. It canonicalizes TCP/UDP direction and audits ICMP only by endpoint pair. It never asserts that a conflict-free tuple proves complete packet ground truth.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Audit whether official session flow tuples have unambiguous labels.</code> | Docstring defines an audit of label consistency for official session tuples. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>TCP/UDP ports are normalized from Argus numbers, hexadecimal or known services.</code> | Document that ports may appear as decimal numbers, hexadecimal values or service names. |
| 4 | <code>ICMP is audited by endpoint pair only because Argus pseudo-port semantics must</code> | Document that ICMP is grouped only by endpoint addresses. |
| 5 | <code>be verified before packet matching. Unknown protocols/ports remain unjoined.</code> | Warn that unsupported ports/protocols remain outside tuple matching. |
| 6 | <code>"""</code> | Close the module documentation string. |
| 7 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 8 | <code>import argparse</code> | Import command-line argument parsing. |
| 9 | <code>import csv</code> | Import CSV dictionaries. |
| 10 | <code>import json</code> | Import JSON report serialization. |
| 11 | <code>import socket</code> | Import local service-name to port-number lookup. |
| 12 | <code>from collections import Counter, defaultdict</code> | Import counting dictionaries and default-created sets. |
| 13 | <code>from functools import lru_cache</code> | Import memoization for repeated port conversions. |
| 14 | <code>from pathlib import Path</code> | Import filesystem path objects. |
| 15 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 16 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 17 | <code>@lru_cache(maxsize=10000)</code> | Cache up to 10,000 port/protocol conversion results. |
| 18 | <code>def port_number(value, protocol):</code> | Define conversion from textual Argus port representation to integer or None. |
| 19 | <code>    value = value.strip()</code> | Strip surrounding whitespace from the port value. |
| 20 | <code>    if value.isdecimal():</code> | Detect decimal-only text. |
| 21 | <code>        return int(value)</code> | Return its decimal integer value. |
| 22 | <code>    if value.lower().startswith("0x"):</code> | Detect a case-insensitive hexadecimal 0x prefix. |
| 23 | <code>        return int(value, 16)</code> | Parse hexadecimal text with base 16; malformed hexadecimal raises ValueError. |
| 24 | <code>    try:</code> | Begin handling service-name lookup failure. |
| 25 | <code>        return socket.getservbyname(value, protocol)</code> | Resolve a name such as http using the local services database and the specified transport protocol. |
| 26 | <code>    except OSError:</code> | Catch an unknown service lookup. |
| 27 | <code>        return None</code> | Return None so the caller can count this row as unsupported. |
| 28 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 29 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 30 | <code>def inspect(path):</code> | Define an audit for one input CSV path. |
| 31 | <code>    tuples = defaultdict(set)</code> | Map canonical tuples to sets of (label, attack-family) pairs. |
| 32 | <code>    row_counts = Counter()</code> | Count rows per original label/family combination. |
| 33 | <code>    unsupported = Counter()</code> | Count unsupported rows by rejection reason. |
| 34 | <code>    examples = {}</code> | Prepare one representative source row per family. |
| 35 | <code>    with path.open(newline="", encoding="utf-8-sig") as source:</code> | Open CSV with correct newline handling and optional UTF-8 BOM removal. |
| 36 | <code>        reader = csv.DictReader(source)</code> | Treat CSV headers as dictionary keys. |
| 37 | <code>        for row in reader:</code> | Visit every data row. |
| 38 | <code>            label = row["Label"].strip()</code> | Read the original label and trim whitespace. |
| 39 | <code>            family = row["Attack Type"].strip()</code> | Read the attack family and trim whitespace. |
| 40 | <code>            row_counts[f"{label}/{family}"] += 1</code> | Increment the combined class count before filtering unsupported protocols. |
| 41 | <code>            protocol = row["Proto"].strip().lower()</code> | Normalize protocol text to lowercase. |
| 42 | <code>            src, dst = row["SrcAddr"].strip(), row["DstAddr"].strip()</code> | Read and trim source and destination addresses. |
| 43 | <code>            if protocol in ("tcp", "udp"):</code> | Handle TCP and UDP with address/port endpoint pairs. |
| 44 | <code>                sport, dport = (</code> | Begin unpacking the two normalized ports. |
| 45 | <code>                    port_number(row["Sport"], protocol),</code> | Convert the source port. |
| 46 | <code>                    port_number(row["Dport"], protocol),</code> | Convert the destination port. |
| 47 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 48 | <code>                if sport is None or dport is None:</code> | Check if either conversion failed. |
| 49 | <code>                    unsupported[f"{protocol}:unknown_port"] += 1</code> | Count this protocol's unknown-port row. |
| 50 | <code>                    continue</code> | Skip tuple labeling for that row. |
| 51 | <code>                key = (protocol, *sorted([(src, sport), (dst, dport)]))</code> | Sort address/port endpoints so both directions share one key, prefixed by protocol. |
| 52 | <code>            elif protocol == "icmp":</code> | Handle ICMP separately because transport-style ports do not apply. |
| 53 | <code>                key = (protocol, *sorted([src, dst]))</code> | Sort its two addresses into a direction-independent key; type/code is not included. |
| 54 | <code>            else:</code> | Handle every other protocol. |
| 55 | <code>                unsupported[protocol] += 1</code> | Count the unsupported protocol. |
| 56 | <code>                continue</code> | Skip that row's tuple analysis. |
| 57 | <code>            tuples[key].add((label, family))</code> | Add its label/family pair to this tuple's set; duplicates collapse naturally. |
| 58 | <code>            if family not in examples:</code> | Store an example only for the family's first supported row. |
| 59 | <code>                examples[family] = {</code> | Begin that representative-row dictionary. |
| 60 | <code>                    field: row[field]</code> | Copy each selected field with its original source value. |
| 61 | <code>                    for field in (</code> | Begin the selected field-name sequence. |
| 62 | <code>                        "SrcAddr",</code> | Include source address. |
| 63 | <code>                        "DstAddr",</code> | Include destination address. |
| 64 | <code>                        "Proto",</code> | Include original protocol text. |
| 65 | <code>                        "Sport",</code> | Include original source port. |
| 66 | <code>                        "Dport",</code> | Include original destination port. |
| 67 | <code>                        "StartTime",</code> | Include displayed start time. |
| 68 | <code>                        "LastTime",</code> | Include displayed end time. |
| 69 | <code>                        "Dur",</code> | Include flow duration. |
| 70 | <code>                        "Label",</code> | Include original benign/malicious label. |
| 71 | <code>                        "Attack Type",</code> | Include attack family. |
| 72 | <code>                    )</code> | Close the multiline call or parenthesized expression begun above. |
| 73 | <code>                }</code> | Close the dictionary begun above. |
| 74 | <code>    ambiguous = [key for key, labels in tuples.items() if len(labels) &gt; 1]</code> | Find canonical tuples associated with more than one label/family pair. |
| 75 | <code>    by_protocol = Counter(key[0] for key in ambiguous)</code> | Count ambiguous tuples by protocol. |
| 76 | <code>    return {</code> | Begin the audit report dictionary. |
| 77 | <code>        "path": str(path),</code> | Record the audited source path. |
| 78 | <code>        "flow_rows": sum(row_counts.values()),</code> | Count all input flow rows, including unsupported rows. |
| 79 | <code>        "class_counts": dict(row_counts),</code> | Export label/family row counts as an ordinary dictionary. |
| 80 | <code>        "normalized_tuple_count": len(tuples),</code> | Report the number of supported unique canonical tuples. |
| 81 | <code>        "ambiguous_tuple_count": len(ambiguous),</code> | Report how many tuples have conflicting class/family assignments. |
| 82 | <code>        "ambiguous_by_protocol": dict(by_protocol),</code> | Export ambiguity counts by protocol. |
| 83 | <code>        "unjoined_rows_by_reason": dict(unsupported),</code> | Export unsupported-row counts and reasons. |
| 84 | <code>        "examples": examples,</code> | Include the representative rows. |
| 85 | <code>        "notes": [</code> | Begin interpretive notes. |
| 86 | <code>            "TCP/UDP tuple direction canonicalized; reverse packets share a key.",</code> | Explain why reverse traffic shares a TCP/UDP tuple. |
| 87 | <code>            "ICMP audit uses endpoint pair, not validated ICMP type/code mapping.",</code> | State the ICMP key limitation explicitly. |
| 88 | <code>            "A conflict-free CSV tuple still requires capture tuple-coverage verification before packet labeling.",</code> | Warn that label consistency alone does not prove packet capture coverage. |
| 89 | <code>        ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 90 | <code>    }</code> | Close the dictionary begun above. |
| 91 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 92 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 93 | <code>def main():</code> | Define the command-line entry point. |
| 94 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Use the module docstring as argument help. |
| 95 | <code>    parser.add_argument("paths", nargs="+", type=Path)</code> | Require one or more CSV paths and convert them to Path objects. |
| 96 | <code>    parser.add_argument("--output", type=Path, default=Path("output/sdn/tuple_label_audit.json"))</code> | Allow a JSON output path with a default under output/sdn. |
| 97 | <code>    args = parser.parse_args()</code> | Parse the user's command-line choices. |
| 98 | <code>    results = [inspect(path) for path in args.paths]</code> | Audit each requested CSV independently. |
| 99 | <code>    args.output.parent.mkdir(parents=True, exist_ok=True)</code> | Create the report's parent folders. |
| 100 | <code>    args.output.write_text(json.dumps(results, indent=2) + "\n")</code> | Write readable JSON with a trailing newline; default text encoding is platform-dependent here. |
| 101 | <code>    print(json.dumps(results, indent=2))</code> | Print the same reports to the terminal. |
| 102 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 103 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 104 | <code>if __name__ == "__main__":</code> | Only run the entry point on direct execution. |
| 105 | <code>    main()</code> | Invoke main; exceptions remain visible and cause process failure. |

## sdn/preflight.py

Read-only inspection of Linux/root/device/tool/package availability and OVS database connectivity. Requires the environment it inspects; reports Boolean checks as JSON and exits nonzero if any fail. It starts no topology or traffic.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Read-only checks for Linux/WSL SDN prerequisites."""</code> | Module docstring describes prerequisite inspection rather than provisioning. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>import json</code> | Import JSON formatting for the displayed check report. |
| 4 | <code>import os</code> | Import operating-system identity and path helpers. |
| 5 | <code>import shutil</code> | Import executable discovery. |
| 6 | <code>import subprocess</code> | Import subprocess execution for the OVS database check. |
| 7 | <code>import sys</code> | Import Python's platform identifier. |
| 8 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 9 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 10 | <code>def main():</code> | Define the prerequisite-check entry point. |
| 11 | <code>    checks = {</code> | Start a dictionary of named Boolean checks. |
| 12 | <code>        "linux": sys.platform == "linux",</code> | Require the Python platform identifier to be linux. |
| 13 | <code>        "root": hasattr(os, "geteuid") and os.geteuid() == 0,</code> | Require geteuid support and effective user ID 0; short-circuiting avoids calling an absent Windows API. |
| 14 | <code>        "tun_device": os.path.exists("/dev/net/tun"),</code> | Check that the Linux TUN device exists. |
| 15 | <code>    }</code> | Close the dictionary begun above. |
| 16 | <code>    for executable in ["ovs-vsctl", "ovs-vswitchd", "ip", "ping", "tcpreplay", "tcpdump"]:</code> | Visit the six external executables used by switching, networking, capture and replay. |
| 17 | <code>        checks[executable] = bool(shutil.which(executable))</code> | Record whether PATH lookup finds each executable. |
| 18 | <code>    for package in ["mininet", "os_ken"]:</code> | Visit the two Python packages required by the SDN testbed. |
| 19 | <code>        try:</code> | Start import-failure handling. |
| 20 | <code>            __import__(package)</code> | Dynamically import the package by its current string name. |
| 21 | <code>            checks[package] = True</code> | Mark that package available after a successful import. |
| 22 | <code>        except ImportError:</code> | Catch ImportError for an unavailable or broken import. |
| 23 | <code>            checks[package] = False</code> | Mark that package unavailable. |
| 24 | <code>    if checks["ovs-vsctl"]:</code> | Only query OVS when ovs-vsctl exists. |
| 25 | <code>        result = subprocess.run(</code> | Begin capturing an OVS diagnostic subprocess result. |
| 26 | <code>            ["ovs-vsctl", "--timeout=3", "show"], check=False, capture_output=True, text=True</code> | Run ovs-vsctl show with a three-second OVS timeout; keep failures as return codes and collect both output streams. |
| 27 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 28 | <code>        checks["ovs_database"] = result.returncode == 0</code> | Record database connectivity based on return code zero. |
| 29 | <code>    print(json.dumps(checks, indent=2))</code> | Print the dictionary as readable JSON. |
| 30 | <code>    return 0 if all(checks.values()) else 1</code> | Return success only when every recorded check passes. |
| 31 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 32 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 33 | <code>if __name__ == "__main__":</code> | Run the entry point only when invoked directly. |
| 34 | <code>    raise SystemExit(main())</code> | Convert main's integer result into the operating-system process exit code. |

## sdn/prepare_flow_labels.py

Uses verified official BS2 CSV and Argus sources to create flow-interval labels with epoch times, endpoints and binary labels. Requires Ubuntu Argus ra, previously fetched CSV and Argus archives, and data/manifest.json. Exact Offset identity, endpoint/protocol/count comparisons and duration/displayed-time consistency establish the join. Output consists of retained ra export, normalized flow labels, a JSON join audit and updated/checkpointed provenance. It does not establish capture packet coverage by itself.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Strictly join official per-session labels to Argus numeric/time exports.</code> | Docstring states that official session labels are joined to Argus numeric/epoch exports. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>Run inside Ubuntu with argus-client installed. Any mismatch prevents a verified</code> | Document the Ubuntu Argus-client requirement and mismatch rejection. |
| 4 | <code>manifest entry; raw &#96;ra&#96; output is retained for investigation.</code> | Explain that raw ra output remains available for investigation. |
| 5 | <code>"""</code> | Close the module documentation string. |
| 6 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 7 | <code>import argparse</code> | Import command-line argument parsing. |
| 8 | <code>import csv</code> | Import CSV parsing/writing. |
| 9 | <code>import hashlib</code> | Import SHA256 provenance hashing. |
| 10 | <code>import json</code> | Import JSON manifest/audit encoding. |
| 11 | <code>import math</code> | Import finite-number validation. |
| 12 | <code>import os</code> | Import the process ID for unique partial-output filenames. |
| 13 | <code>import shutil</code> | Import file copying. |
| 14 | <code>import subprocess</code> | Import external Argus command execution. |
| 15 | <code>import tempfile</code> | Import automatically cleaned temporary directories. |
| 16 | <code>from pathlib import Path</code> | Import filesystem paths. |
| 17 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 18 | <code>ROOT = Path(__file__).resolve().parents[1]</code> | Compute the repository root from this script's location. |
| 19 | <code>FIELDS = [</code> | Begin the ordered output-column schema. |
| 20 | <code>    "start_epoch",</code> | Store interval start in epoch seconds. |
| 21 | <code>    "end_epoch",</code> | Store interval end in epoch seconds. |
| 22 | <code>    "src_ip",</code> | Store source IP address. |
| 23 | <code>    "dst_ip",</code> | Store destination IP address. |
| 24 | <code>    "src_port",</code> | Store source transport port when applicable. |
| 25 | <code>    "dst_port",</code> | Store destination transport port when applicable. |
| 26 | <code>    "protocol",</code> | Store protocol name. |
| 27 | <code>    "label",</code> | Store binary benign/attack ground truth. |
| 28 | <code>    "attack_family",</code> | Store the original attack-family name. |
| 29 | <code>    "offset",</code> | Store Argus Offset, the record identity used for the join. |
| 30 | <code>]</code> | Close the list or indexing expression begun above. |
| 31 | <code>EXPORT = [</code> | Begin the ordered fields requested from Argus ra. |
| 32 | <code>    "stime",</code> | Request start time. |
| 33 | <code>    "ltime",</code> | Request last/end time. |
| 34 | <code>    "saddr",</code> | Request source address. |
| 35 | <code>    "daddr",</code> | Request destination address. |
| 36 | <code>    "sport",</code> | Request source port. |
| 37 | <code>    "dport",</code> | Request destination port. |
| 38 | <code>    "proto",</code> | Request protocol. |
| 39 | <code>    "seq",</code> | Request record sequence information. |
| 40 | <code>    "dur",</code> | Request duration. |
| 41 | <code>    "offset",</code> | Request record offset for exact joining. |
| 42 | <code>    "pkts",</code> | Request total packet count. |
| 43 | <code>    "bytes",</code> | Request total byte count. |
| 44 | <code>]</code> | Close the list or indexing expression begun above. |
| 45 | <code>FLOODS = {"UDPFlood", "SYNFlood", "ICMPFlood"}</code> | Limit supported malicious families to UDPFlood, SYNFlood and ICMPFlood. |
| 46 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 47 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 48 | <code>def sha(path):</code> | Define SHA256 calculation for a file. |
| 49 | <code>    value = hashlib.sha256()</code> | Create the hash accumulator. |
| 50 | <code>    with path.open("rb") as source:</code> | Open binary input. |
| 51 | <code>        for chunk in iter(lambda: source.read(1024 * 1024), b""):</code> | Read one-MiB chunks until EOF. |
| 52 | <code>            value.update(chunk)</code> | Update the hash with each chunk. |
| 53 | <code>    return value.hexdigest()</code> | Return the hexadecimal digest. |
| 54 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 55 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 56 | <code>def verify_source(path, manifest):</code> | Define a source-file lookup against the supplied provenance manifest. |
| 57 | <code>    relative = path.resolve().relative_to(ROOT).as_posix()</code> | Resolve the source beneath ROOT and store its portable relative path; outside-root files raise ValueError. |
| 58 | <code>    matches = [</code> | Begin finding matching manifest entries. |
| 59 | <code>        item</code> | Select the manifest item object. |
| 60 | <code>        for item in manifest["files"]</code> | Visit every existing manifest file entry. |
| 61 | <code>        if item["path"] == relative and item["sha256"] == sha(path)</code> | Require both exact relative path and current-file digest equality; this function does not separately inspect verification_status or requery the publisher. |
| 62 | <code>    ]</code> | Close the list or indexing expression begun above. |
| 63 | <code>    if len(matches) != 1:</code> | Require exactly one matching entry. |
| 64 | <code>        raise ValueError(f"Official source checksum not verified: {path}")</code> | Reject missing, duplicate or checksum-mismatched provenance. |
| 65 | <code>    return matches[0]["sha256"]</code> | Return that matching source digest for parent lineage. |
| 66 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 67 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 68 | <code>def time_match(display, epoch):</code> | Define comparison between displayed minute/second text and an epoch value. |
| 69 | <code>    try:</code> | Begin handling malformed display/epoch numbers. |
| 70 | <code>        minute, second = display.strip().split(":")</code> | Split the stripped display into minute and second components. |
| 71 | <code>        expected = int(minute) * 60 + float(second)</code> | Convert the displayed time to seconds within an hour. |
| 72 | <code>        observed = float(epoch) % 3600</code> | Reduce epoch seconds modulo one hour. |
| 73 | <code>        distance = abs(expected - observed)</code> | Compute absolute within-hour distance. |
| 74 | <code>        return min(distance, 3600 - distance) &lt;= 0.11</code> | Accept at most 0.11 seconds difference, including wraparound at an hour boundary. |
| 75 | <code>    except ValueError:</code> | Catch conversion/unpacking ValueError. |
| 76 | <code>        return False</code> | Treat invalid displayed time as a mismatch. |
| 77 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 78 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 79 | <code>def prepare(family, manifest):</code> | Define preparation for one named family/session. |
| 80 | <code>    csv_path = ROOT / "data/raw/BS2_each_attack_csv/BS2_each_attack_csv" / f"{family}2.csv"</code> | Select the official BS2 per-attack CSV using its nested extracted folder and family2.csv name. |
| 81 | <code>    argus_path = ROOT / "data/raw/BS2_each_attack_argus/BS2_each_attack_argus" / f"{family}2.argus"</code> | Select the corresponding official BS2 Argus binary file; that archive must already be fetched separately. |
| 82 | <code>    parents = [verify_source(csv_path, manifest), verify_source(argus_path, manifest)]</code> | Verify both source files against the manifest and collect their digests. |
| 83 | <code>    prepared = ROOT / "data/prepared"</code> | Choose data/prepared for derived artifacts. |
| 84 | <code>    prepared.mkdir(parents=True, exist_ok=True)</code> | Create the prepared-data directory. |
| 85 | <code>    raw_output = prepared / f"BS2_{family}_ra_numeric.csv"</code> | Choose the retained raw numeric Argus export path. |
| 86 | <code>    command = ["ra", "-n", "-u", "-r", str(argus_path), "-c", ",", "-s", *EXPORT]</code> | Build ra argv: numeric addresses/ports, numeric/epoch time, input file, comma separator and selected export fields. |
| 87 | <code>    # Argus performs small per-record reads/writes. Native temporary files avoid</code> | Comment explains Argus' many small file accesses. |
| 88 | <code>    # hundreds of thousands of slow DrvFS operations on a Windows project mount.</code> | Comment explains moving working files off a Windows-mounted path to native temporary storage for speed. |
| 89 | <code>    with tempfile.TemporaryDirectory(prefix="m3_argus_") as temporary:</code> | Create an automatically cleaned native temporary directory. |
| 90 | <code>        native_input = Path(temporary) / argus_path.name</code> | Choose the temporary Argus input path. |
| 91 | <code>        native_output = Path(temporary) / "numeric.csv"</code> | Choose the temporary CSV output path. |
| 92 | <code>        shutil.copyfile(argus_path, native_input)</code> | Copy the official Argus file unchanged into temporary storage. |
| 93 | <code>        runtime_command = [*command]</code> | Copy the command list so its recorded source command stays unchanged. |
| 94 | <code>        runtime_command[runtime_command.index("-r") + 1] = str(native_input)</code> | Replace only the argv item following -r with the temporary input path. |
| 95 | <code>        with native_output.open("w") as output:</code> | Open temporary output text. |
| 96 | <code>            subprocess.run(runtime_command, stdout=output, check=True)</code> | Run ra, write stdout into that file, and raise if its exit status is nonzero. |
| 97 | <code>        shutil.copyfile(native_output, raw_output)</code> | Copy the complete numeric export into data/prepared before temporary cleanup. |
| 98 | <code>    labels = {}</code> | Create the dictionary mapping source Offset to official CSV row. |
| 99 | <code>    with csv_path.open(newline="", encoding="utf-8-sig") as source:</code> | Open official CSV with BOM-aware UTF-8 and CSV newline handling. |
| 100 | <code>        for row in csv.DictReader(source):</code> | Visit its rows as dictionaries. |
| 101 | <code>            offset = int(row["Offset"])</code> | Parse the CSV Offset as an integer. |
| 102 | <code>            if offset in labels:</code> | Check for duplicate source record identity. |
| 103 | <code>                raise ValueError(f"Repeated CSV Offset {offset}")</code> | Reject duplicate offsets rather than choosing an arbitrary label. |
| 104 | <code>            labels[offset] = row</code> | Index the entire original row by Offset. |
| 105 | <code>    result_path = prepared / f"BS2_{family}_flow_labels.csv"</code> | Choose the final derived flow-interval-label CSV filename. |
| 106 | <code>    partial = result_path.with_suffix(f".csv.partial.{os.getpid()}")</code> | Use a .partial.<process-id> suffix so concurrent processes have distinct staging names. |
| 107 | <code>    seen = set()</code> | Track offsets seen in Argus output. |
| 108 | <code>    management_records = 0</code> | Count Argus management rows that are not traffic flows. |
| 109 | <code>    contradictions = []</code> | Accumulate content contradictions rather than silently accepting mismatches. |
| 110 | <code>    with raw_output.open(newline="") as source, partial.open("w", newline="") as output:</code> | Open retained numeric input and staged CSV output together with CSV newline handling. |
| 111 | <code>        writer = csv.DictWriter(output, fieldnames=FIELDS)</code> | Create an output writer using the exact FIELDS column order. |
| 112 | <code>        writer.writeheader()</code> | Write the CSV header. |
| 113 | <code>        for row in csv.DictReader(source):</code> | Visit numeric Argus rows. |
| 114 | <code>            if row["Proto"].strip() == "man":</code> | Identify Argus management records by stripped Proto value man. |
| 115 | <code>                management_records += 1</code> | Count excluded management records. |
| 116 | <code>                continue</code> | Skip management records before flow joining. |
| 117 | <code>            offset = int(row["Offset"])</code> | Parse the numeric record Offset. |
| 118 | <code>            if offset in seen or offset not in labels:</code> | Reject both repeated Argus identities and Argus records absent from the official label CSV. |
| 119 | <code>                raise ValueError(f"Repeated or absent Argus Offset {offset}")</code> | Raise with the offending Offset. |
| 120 | <code>            seen.add(offset)</code> | Mark the current Argus identity seen. |
| 121 | <code>            label_row = labels[offset]</code> | Select its official CSV label row using exact Offset. |
| 122 | <code>            for field in ("SrcAddr", "DstAddr", "Proto", "TotPkts", "TotBytes"):</code> | Compare endpoint addresses, protocol and total packet/byte counts. |
| 123 | <code>                if row[field].strip() != label_row[field].strip():</code> | Trim only surrounding whitespace before comparing these strings. |
| 124 | <code>                    contradictions.append(</code> | Begin appending a descriptive field contradiction. |
| 125 | <code>                        f"Offset {offset}: {field}: Argus {row[field]} != CSV {label_row[field]}"</code> | Record the offset, field and both disagreeing source values. |
| 126 | <code>                    )</code> | Close the multiline call or parenthesized expression begun above. |
| 127 | <code>            if abs(float(row["Dur"]) - float(label_row["Dur"])) &gt; 0.00001:</code> | Allow at most 0.00001 difference between numeric durations. |
| 128 | <code>                contradictions.append(f"Offset {offset}: Dur mismatch")</code> | Record a duration contradiction. |
| 129 | <code>            if not time_match(label_row["StartTime"], row["StartTime"]) or not time_match(</code> | Require the displayed start time to match its numeric export and begin the end-time check. |
| 130 | <code>                label_row["LastTime"], row["LastTime"]</code> | Compare displayed and numeric end times. |
| 131 | <code>            ):</code> | Close the multiline call or parenthesized expression begun above; the colon begins its indented block. |
| 132 | <code>                contradictions.append(f"Offset {offset}: displayed timestamp mismatch")</code> | Record a displayed-time contradiction if either comparison fails. |
| 133 | <code>            attack = label_row["Attack Type"].strip()</code> | Read and trim official attack family. |
| 134 | <code>            original = label_row["Label"].strip()</code> | Read and trim official label. |
| 135 | <code>            if attack == "Benign" and original == "Benign":</code> | Accept a benign label only when both official fields explicitly say Benign. |
| 136 | <code>                label = 0</code> | Assign binary label zero. |
| 137 | <code>            elif attack in FLOODS and original in ("Malicious", attack):</code> | Accept malicious supported floods when label is Malicious or repeats the attack-family name. |
| 138 | <code>                label = 1</code> | Assign binary label one. |
| 139 | <code>            else:</code> | Handle any unexpected label/family combination. |
| 140 | <code>                raise ValueError(f"Unexpected label pair {original}/{attack} in session {family}")</code> | Reject it rather than silently relabeling. |
| 141 | <code>            proto = row["Proto"].strip()</code> | Read the exported protocol name. |
| 142 | <code>            src_port, dst_port = row["Sport"].strip(), row["Dport"].strip()</code> | Read exported source and destination ports as text. |
| 143 | <code>            if proto not in ("tcp", "udp"):</code> | Check for protocols without TCP/UDP transport ports. |
| 144 | <code>                src_port = dst_port = ""</code> | Clear both ports for those protocols, including ICMP. |
| 145 | <code>            elif (src_port and not src_port.isdecimal()) or (dst_port and not dst_port.isdecimal()):</code> | For TCP/UDP, reject a nonempty port that contains nondecimal text. |
| 146 | <code>                raise ValueError("Non-numeric TCP/UDP port in ra -n output")</code> | Raise a numeric-port export error. |
| 147 | <code>            start, end = float(row["StartTime"]), float(row["LastTime"])</code> | Parse start and end epoch values into floats. |
| 148 | <code>            if not math.isfinite(start) or not math.isfinite(end) or end &lt; start:</code> | Reject NaN, infinities and an end time earlier than start. |
| 149 | <code>                raise ValueError("Invalid epoch interval")</code> | Raise invalid-interval error. |
| 150 | <code>            writer.writerow(</code> | Begin writing the normalized output row into the staged file. |
| 151 | <code>                dict(</code> | Construct a dictionary from paired fields/values. |
| 152 | <code>                    zip(</code> | Pair each output-column name with its corresponding value via zip. |
| 153 | <code>                        FIELDS,</code> | Use the FIELDS order defined near the top. |
| 154 | <code>                        [</code> | Open the ordered output values that zip pairs with the FIELDS column names. |
| 155 | <code>                            start,</code> | Write start epoch. |
| 156 | <code>                            end,</code> | Write end epoch. |
| 157 | <code>                            row["SrcAddr"],</code> | Write source address. |
| 158 | <code>                            row["DstAddr"],</code> | Write destination address. |
| 159 | <code>                            src_port,</code> | Write normalized source port. |
| 160 | <code>                            dst_port,</code> | Write normalized destination port. |
| 161 | <code>                            proto,</code> | Write protocol. |
| 162 | <code>                            label,</code> | Write binary ground truth. |
| 163 | <code>                            attack,</code> | Write original attack family. |
| 164 | <code>                            offset,</code> | Write joining Offset. |
| 165 | <code>                        ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 166 | <code>                    )</code> | Close the multiline call or parenthesized expression begun above. |
| 167 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 168 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 169 | <code>    audit = {</code> | Begin a persistent join audit dictionary. |
| 170 | <code>        "session": family,</code> | Identify the requested session/family. |
| 171 | <code>        "csv_rows": len(labels),</code> | Count official CSV labels. |
| 172 | <code>        "argus_flow_rows": len(seen),</code> | Count joined Argus flow identities. |
| 173 | <code>        "argus_management_records_excluded": management_records,</code> | Report excluded management records. |
| 174 | <code>        "missing_offsets": len(labels.keys() - seen),</code> | Count official CSV offsets absent from exported Argus flows. |
| 175 | <code>        "contradiction_count": len(contradictions),</code> | Count all recorded field/time/duration contradictions. |
| 176 | <code>        "contradiction_examples": contradictions[:10],</code> | Keep the first ten contradiction details for practical investigation. |
| 177 | <code>        "parent_sha256s": parents,</code> | Record source-file hashes. |
| 178 | <code>        "ra_command": command,</code> | Record the logical ra command using the original project input path. |
| 179 | <code>        "ra_version": subprocess.run(</code> | Begin collecting Argus tool identity information. |
| 180 | <code>            ["ra", "-h"], check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True</code> | Run ra -h, combine stdout/stderr, and retain a nonzero help status without raising. |
| 181 | <code>        ).stdout.splitlines()[:2],</code> | Retain only the first two help-output lines as version evidence. |
| 182 | <code>    }</code> | Close the dictionary begun above. |
| 183 | <code>    audit_path = prepared / f"BS2_{family}_join_audit.json"</code> | Choose this family's JSON audit output. |
| 184 | <code>    audit_path.write_text(json.dumps(audit, indent=2) + "\n")</code> | Write the audit before the final pass/fail decision. |
| 185 | <code>    if contradictions or seen != labels.keys():</code> | Reject any contradictions or any mismatch between CSV identities and exported identities. |
| 186 | <code>        raise ValueError(</code> | Begin the failure exception. |
| 187 | <code>            f"Official label join failed for {family}; inspect {audit_path}; unverified partial retained"</code> | Point to saved audit evidence and explicitly preserve unverified staged output. |
| 188 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 189 | <code>    partial.replace(result_path)</code> | Promote staged label output to its final path only after successful validation. |
| 190 | <code>    entries = []</code> | Initialize provenance entries for the derived artifacts. |
| 191 | <code>    for path in (raw_output, result_path, audit_path):</code> | Visit raw export, verified joined CSV and join-audit JSON. |
| 192 | <code>        entries.append(</code> | Begin adding an artifact provenance record. |
| 193 | <code>            {</code> | Open the derived-artifact provenance dictionary being appended to entries. |
| 194 | <code>                "path": path.relative_to(ROOT).as_posix(),</code> | Store the repository-relative POSIX path. |
| 195 | <code>                "sha256": sha(path),</code> | Compute its actual file SHA256. |
| 196 | <code>                "size_bytes": path.stat().st_size,</code> | Record actual byte size. |
| 197 | <code>                "verification_status": "verified",</code> | Mark this successfully prepared artifact verified. |
| 198 | <code>                "download_url": manifest["source_url"],</code> | Carry the original dataset landing page as source. |
| 199 | <code>                "parent_sha256s": parents,</code> | Record both source parents' digests. |
| 200 | <code>                "transformations": [</code> | Begin describing transformations. |
| 201 | <code>                    "ra -n -u numeric/time export",</code> | Declare the numeric/time Argus export operation. |
| 202 | <code>                    "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks",</code> | Declare the exact Offset join and consistency checks performed; note ports themselves are normalized but not compared against CSV ports above. |
| 203 | <code>                ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 204 | <code>                "label_scope": "Flow intervals only; packet coverage and overlap conflicts still require validation",</code> | Limit validity to flow intervals: packet coverage and conflicting interval overlap still require separate validation. |
| 205 | <code>            }</code> | Close the dictionary begun above. |
| 206 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 207 | <code>    return entries</code> | Return the list of derived artifact records. |
| 208 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 209 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 210 | <code>def main():</code> | Define the script's command-line entry point. |
| 211 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Use module documentation as CLI help. |
| 212 | <code>    parser.add_argument("--family", choices=sorted(FLOODS), action="append")</code> | Allow repeated --family selections drawn only from supported flood families. |
| 213 | <code>    parser.add_argument(</code> | Begin registering provenance restoration mode. |
| 214 | <code>        "--restore-checkpoint",</code> | Name the switch --restore-checkpoint. |
| 215 | <code>        action="store_true",</code> | Make it Boolean. |
| 216 | <code>        help="Merge verified prepared provenance after an older concurrent fetch completed",</code> | Explain it restores prepared lineage after an older concurrent fetch. |
| 217 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 218 | <code>    args = parser.parse_args()</code> | Parse CLI arguments. |
| 219 | <code>    manifest_path = ROOT / "data/manifest.json"</code> | Choose the shared dataset manifest. |
| 220 | <code>    manifest = json.loads(manifest_path.read_text())</code> | Read existing manifest JSON. |
| 221 | <code>    if args.restore_checkpoint:</code> | Branch into checkpoint restoration when requested. |
| 222 | <code>        checkpoint = json.loads((ROOT / "data/prepared/provenance_checkpoint.json").read_text())</code> | Read the previously saved prepared provenance checkpoint. |
| 223 | <code>        by_path = {item["path"]: item for item in manifest["files"]}</code> | Index current manifest entries by path. |
| 224 | <code>        for item in checkpoint["files"]:</code> | Visit checkpoint entries. |
| 225 | <code>            target = (ROOT / item["path"]).resolve()</code> | Resolve each checkpoint's target against repository root. |
| 226 | <code>            if not target.is_relative_to(ROOT) or sha(target) != item["sha256"]:</code> | Require containment in ROOT and verify the current target's digest. |
| 227 | <code>                raise ValueError(f"Checkpoint checksum mismatch: {item['path']}")</code> | Reject an altered or escaping checkpoint target. |
| 228 | <code>            by_path[item["path"]] = item</code> | Merge the verified checkpoint entry by path. |
| 229 | <code>        manifest["files"] = list(by_path.values())</code> | Save merged entries back into the manifest object. |
| 230 | <code>        temporary = manifest_path.with_suffix(".json.tmp")</code> | Choose a temporary manifest staging path. |
| 231 | <code>        temporary.write_text(json.dumps(manifest, indent=2) + "\n")</code> | Write readable JSON with a trailing newline. |
| 232 | <code>        temporary.replace(manifest_path)</code> | Replace the main manifest with its staged version. |
| 233 | <code>        print("Restored verified checkpoint provenance without removing current capture entries.")</code> | Report the provenance merge. |
| 234 | <code>        return</code> | Stop after restoration without regenerating labels. |
| 235 | <code>    entries = []</code> | Initialize newly prepared artifact records. |
| 236 | <code>    for family in args.family or sorted(FLOODS):</code> | Process explicitly selected families, otherwise all supported families in sorted order. |
| 237 | <code>        entries.extend(prepare(family, manifest))</code> | Prepare that family and append its output entries. |
| 238 | <code>    # Merge current manifest again in case a concurrent official capture completed.</code> | Comment explains rereading shared provenance after potentially concurrent downloads. |
| 239 | <code>    latest = json.loads(manifest_path.read_text())</code> | Read the current manifest again immediately before merging. |
| 240 | <code>    paths = {item["path"] for item in entries}</code> | Collect newly prepared paths. |
| 241 | <code>    latest["files"] = [item for item in latest["files"] if item["path"] not in paths] + entries</code> | Retain unrelated current entries and replace only this run's matching prepared paths. |
| 242 | <code>    temporary = manifest_path.with_suffix(".json.tmp")</code> | Choose a staging path for the manifest. |
| 243 | <code>    temporary.write_text(json.dumps(latest, indent=2) + "\n")</code> | Write the updated manifest as readable JSON. |
| 244 | <code>    temporary.replace(manifest_path)</code> | Replace the manifest using its staged file. |
| 245 | <code>    (ROOT / "data/prepared/provenance_checkpoint.json").write_text(</code> | Begin saving a full provenance snapshot for possible restoration. |
| 246 | <code>        json.dumps(latest, indent=2) + "\n"</code> | Serialize the just-merged manifest into the checkpoint. |
| 247 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 248 | <code>    print(json.dumps(entries, indent=2))</code> | Print the new prepared records as readable JSON. |
| 249 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 250 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 251 | <code>if __name__ == "__main__":</code> | Only call main when directly executed. |
| 252 | <code>    main()</code> | Run preparation; unhandled errors cause nonzero process termination. |

## sdn/run_live_validation.py

Orchestrates the genuine M3 live_sflow collector, an OS-Ken controller and the isolated topology's benign ICMP probe. Assumes all executables share one Python environment and the Linux SDN setup works. Writes logs, saved config, topology evidence and normal run artifacts. labels_path=None means this is telemetry and resource-path validation, not attack-recall validation or labeled online-training evidence.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Run the genuine M3 collector against an isolated benign sFlow probe.</code> | Docstring introduces a real M3 collector check against an isolated benign probe. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>The resulting run is telemetry validation with no attack-quality labels.</code> | State that the produced run validates telemetry without attack-quality labels. |
| 4 | <code>"""</code> | Close the module documentation string. |
| 5 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 6 | <code>import json</code> | Import JSON configuration writing. |
| 7 | <code>import socket</code> | Import TCP readiness checks. |
| 8 | <code>import subprocess</code> | Import controller, collector and topology process execution. |
| 9 | <code>import sys</code> | Import the current Python executable path. |
| 10 | <code>import time</code> | Import monotonic deadlines and sleeps. |
| 11 | <code>from pathlib import Path</code> | Import paths. |
| 12 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 13 | <code>ROOT = Path(__file__).resolve().parents[1]</code> | Locate repository root relative to this script. |
| 14 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 15 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 16 | <code>def main():</code> | Define orchestration entry point. |
| 17 | <code>    output = ROOT / "output" / "sdn"</code> | Choose output/sdn for diagnostics. |
| 18 | <code>    output.mkdir(parents=True, exist_ok=True)</code> | Create diagnostic folders. |
| 19 | <code>    binaries = Path(sys.executable).parent</code> | Find executables beside the running Python, assuming OS-Ken and m3 are installed in the same environment. |
| 20 | <code>    with (</code> | Begin opening managed log files. |
| 21 | <code>        (output / "live_controller.log").open("w") as controller_log,</code> | Open controller log in write mode, replacing prior contents. |
| 22 | <code>        (output / "live_collector.log").open("w") as collector_log,</code> | Open collector log in write mode. |
| 23 | <code>        (output / "live_topology.log").open("w") as topology_log,</code> | Open topology log in write mode. |
| 24 | <code>    ):</code> | Close the multiline call or parenthesized expression begun above; the colon begins its indented block. |
| 25 | <code>        controller = subprocess.Popen(</code> | Start the external controller process asynchronously. |
| 26 | <code>            [</code> | Open the controller executable and argument list supplied to subprocess.Popen. |
| 27 | <code>                str(binaries / "osken-manager"),</code> | Select this environment's osken-manager executable. |
| 28 | <code>                "--ofp-tcp-listen-port",</code> | Specify the controller listening-port argument. |
| 29 | <code>                "6653",</code> | Choose TCP port 6653. |
| 30 | <code>                str(ROOT / "sdn" / "controller.py"),</code> | Load this repository's learning-switch controller. |
| 31 | <code>            ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 32 | <code>            stdout=controller_log,</code> | Redirect controller stdout to its log. |
| 33 | <code>            stderr=subprocess.STDOUT,</code> | Merge controller stderr into the same log. |
| 34 | <code>        )</code> | Close the multiline call or parenthesized expression begun above. |
| 35 | <code>        collector = None</code> | Initialize collector state before entering failure/cleanup handling. |
| 36 | <code>        try:</code> | Start a cleanup-protected orchestration block. |
| 37 | <code>            deadline = time.monotonic() + 60</code> | Set a controller readiness deadline 60 seconds in the monotonic future. |
| 38 | <code>            while True:</code> | Retry readiness until success or explicit failure. |
| 39 | <code>                if controller.poll() is not None:</code> | Check if the controller has already exited. |
| 40 | <code>                    raise RuntimeError("Controller failed; inspect live_controller.log")</code> | Raise a diagnostic pointing to its log. |
| 41 | <code>                try:</code> | Begin a connection attempt. |
| 42 | <code>                    with socket.create_connection(("127.0.0.1", 6653), timeout=0.5):</code> | Try opening loopback TCP port 6653 with a half-second timeout; this verifies a listener, not a completed switch handshake. |
| 43 | <code>                        break</code> | Leave the readiness loop after a successful connection. |
| 44 | <code>                except OSError:</code> | Handle connection failure. |
| 45 | <code>                    if time.monotonic() &gt; deadline:</code> | Check whether the readiness deadline passed. |
| 46 | <code>                        raise RuntimeError("Controller startup timed out")</code> | Raise startup timeout after 60 seconds. |
| 47 | <code>                    time.sleep(0.25)</code> | Pause a quarter-second between attempts. |
| 48 | <code>            config = {</code> | Begin the M3 live-run configuration. |
| 49 | <code>                "mode": "live_sflow",</code> | Select genuine live_sflow collector mode. |
| 50 | <code>                "sampling_rate": 1,</code> | Set sampling metadata to one, matching topology configuration below. |
| 51 | <code>                "seed": 42,</code> | Choose reproducibility seed 42. |
| 52 | <code>                "scenario": "baseline",</code> | Name the scenario baseline. |
| 53 | <code>                "output_root": str(ROOT / "output" / "runs"),</code> | Save standardized run artifacts under output/runs. |
| 54 | <code>                "bind": "127.0.0.1",</code> | Bind the telemetry collector to loopback only. |
| 55 | <code>                "port": 6343,</code> | Listen for sFlow on UDP port 6343. |
| 56 | <code>                "duration_seconds": 22,</code> | Collect for 22 seconds. |
| 57 | <code>                "warmup_seconds": 2,</code> | Reserve a two-second warm-up. |
| 58 | <code>                "window_seconds": 1,</code> | Aggregate features in one-second windows. |
| 59 | <code>                "threshold": 0.5,</code> | Use attack-probability threshold 0.5. |
| 60 | <code>                "labels_path": None,</code> | Provide no ground-truth file; this run cannot produce valid supervised attack-quality evaluation. |
| 61 | <code>                "controller_pid": controller.pid,</code> | Identify the controller process for resource measurement. |
| 62 | <code>                "ovs_bridge": "m3s1",</code> | Identify m3s1 for switch metrics. |
| 63 | <code>                "openflow_port": 6653,</code> | Identify TCP port 6653 for OpenFlow observations. |
| 64 | <code>            }</code> | Close the dictionary begun above. |
| 65 | <code>            config_path = output / "live_validation_config.json"</code> | Choose the saved configuration filename. |
| 66 | <code>            config_path.write_text(json.dumps(config, indent=2) + "\n")</code> | Write readable configuration JSON and a trailing newline. |
| 67 | <code>            collector = subprocess.Popen(</code> | Launch the real M3 CLI collector asynchronously. |
| 68 | <code>                [str(binaries / "m3"), "live", "--config", str(config_path)],</code> | Execute m3 live with the saved config in this same environment. |
| 69 | <code>                stdout=collector_log,</code> | Log collector stdout. |
| 70 | <code>                stderr=subprocess.STDOUT,</code> | Combine collector stderr with stdout. |
| 71 | <code>                cwd=ROOT,</code> | Run with repository root as working directory. |
| 72 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 73 | <code>            time.sleep(4)</code> | Wait four seconds before creating the test topology. |
| 74 | <code>            if collector.poll() is not None:</code> | Check for early collector termination. |
| 75 | <code>                raise RuntimeError("Collector failed; inspect live_collector.log")</code> | Raise a collector-start error with its log location. |
| 76 | <code>            topology = subprocess.run(</code> | Run the topology synchronously. |
| 77 | <code>                [</code> | Open the topology executable and argument list supplied to subprocess.run. |
| 78 | <code>                    sys.executable,</code> | Use the same Python interpreter. |
| 79 | <code>                    str(ROOT / "sdn" / "topology.py"),</code> | Select the topology source file. |
| 80 | <code>                    "--sampling",</code> | Pass its sampling option. |
| 81 | <code>                    "1",</code> | Use actual switch sampling N=1. |
| 82 | <code>                    "--probe",</code> | Request the benign ICMP probe. |
| 83 | <code>                    "--duration",</code> | Pass its duration option. |
| 84 | <code>                    "8",</code> | Generate an eight-second timed topology run. |
| 85 | <code>                    "--evidence",</code> | Pass the evidence-file option. |
| 86 | <code>                    str(output / "live_topology.json"),</code> | Save topology evidence in live_topology.json. |
| 87 | <code>                ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 88 | <code>                check=False,</code> | Retain nonzero topology exit status instead of immediately raising. |
| 89 | <code>                stdout=topology_log,</code> | Redirect topology stdout to its log. |
| 90 | <code>                stderr=subprocess.STDOUT,</code> | Merge topology stderr into that log. |
| 91 | <code>                cwd=ROOT,</code> | Use repository-root working directory. |
| 92 | <code>                timeout=45,</code> | Require topology execution to finish within 45 seconds. |
| 93 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 94 | <code>            collector.wait(timeout=40)</code> | Wait up to 40 further seconds for collector completion. |
| 95 | <code>            if topology.returncode or collector.returncode:</code> | Treat nonzero topology or collector exit codes as failure. |
| 96 | <code>                raise RuntimeError("Live validation failed; inspect saved logs")</code> | Raise a saved-logs diagnostic for that failure. |
| 97 | <code>            print(</code> | Begin printing the completion message. |
| 98 | <code>                "Genuine M3 collector run saved in output/runs; source=live_sflow, labels unavailable."</code> | State that genuine live_sflow run artifacts were produced and labels remain unavailable. |
| 99 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 100 | <code>        finally:</code> | Enter cleanup whether collection succeeded or raised. |
| 101 | <code>            if collector and collector.poll() is None:</code> | Check whether a collector exists and still runs. |
| 102 | <code>                collector.terminate()</code> | Request collector termination. |
| 103 | <code>                collector.wait(timeout=10)</code> | Wait up to ten seconds for collector exit; there is no kill fallback if it ignores termination. |
| 104 | <code>            controller.terminate()</code> | Request controller termination. |
| 105 | <code>            controller.wait(timeout=10)</code> | Wait up to ten seconds for controller exit. |
| 106 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 107 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 108 | <code>if __name__ == "__main__":</code> | Only launch orchestration on direct execution. |
| 109 | <code>    main()</code> | Call the entry point; exceptions remain visible to the operator. |

## sdn/topology.py

Creates four Mininet hosts connected through a named OVS bridge to an external controller. Configures real switch-side sFlow, checks connectivity, optionally generates benign ICMP or replays a prepared Ethernet PCAP, saves evidence and cleans up. Requires Linux privileges and SDN tools. No physical uplink is added. Replay requires externally documented Ethernet/address mapping and separately supplied ground truth.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Create an isolated four-host SDN testbed and export switch-side sFlow.</code> | Docstring describes a four-host emulated SDN network with switch-side sFlow. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>No link to the host's physical network is created. PCAP replay injects only</code> | Document that the topology creates no physical-network link. |
| 4 | <code>through a named Mininet host interface. Capture labels must be supplied to</code> | Explain replay uses a named virtual host interface and labels belong to the separate runner. |
| 5 | <code>the separate M3 runner and are never inferred from an attack filename.</code> | Warn that capture filenames never become ground truth here. |
| 6 | <code>"""</code> | Close the module documentation string. |
| 7 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 8 | <code>import argparse</code> | Import command-line options. |
| 9 | <code>import json</code> | Import JSON evidence writing. |
| 10 | <code>import subprocess</code> | Import OVS commands and capture-replay processes. |
| 11 | <code>import time</code> | Import startup pauses and timestamps. |
| 12 | <code>from pathlib import Path</code> | Import path objects. |
| 13 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 14 | <code>from mininet.cli import CLI</code> | Import the optional interactive Mininet console. |
| 15 | <code>from mininet.log import setLogLevel</code> | Import Mininet logging-level control. |
| 16 | <code>from mininet.net import Mininet</code> | Import the emulated-network builder. |
| 17 | <code>from mininet.node import OVSSwitch, RemoteController</code> | Import OVS switches and connection to an independently running controller. |
| 18 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 19 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 20 | <code>def ovs(*args):</code> | Define a helper accepting a variable number of OVS arguments. |
| 21 | <code>    return subprocess.check_output(["ovs-vsctl", *map(str, args)], text=True).strip()</code> | Run ovs-vsctl with arguments converted to strings, capture decoded stdout and strip whitespace; failures raise. |
| 22 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 23 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 24 | <code>def set_sampling(rate, target):</code> | Define switch telemetry configuration for a sampling rate and collector target. |
| 25 | <code>    if rate &lt; 1:</code> | Require positive sampling denominator N. |
| 26 | <code>        raise ValueError("Sampling N must be positive")</code> | Reject nonpositive N. |
| 27 | <code>    ovs(</code> | Begin one OVS database transaction. |
| 28 | <code>        "--",</code> | Separate OVS commands/options. |
| 29 | <code>        "--id=@m3sf",</code> | Name the new database row @m3sf for reuse within this transaction. |
| 30 | <code>        "create",</code> | Request creation of a database row. |
| 31 | <code>        "sflow",</code> | Choose the sflow table. |
| 32 | <code>        "agent=lo",</code> | Use loopback as the sFlow agent interface. |
| 33 | <code>        f'targets=["{target}"]',</code> | Set the collector destination list to the supplied host:port. |
| 34 | <code>        f"sampling={rate}",</code> | Configure the switch's sampling denominator; N describes switch packet sampling, not dropping preaggregated CSV rows. |
| 35 | <code>        "polling=1",</code> | Request counter polling every second. |
| 36 | <code>        "header=256",</code> | Export up to 256 header bytes per sampled packet. |
| 37 | <code>        "--",</code> | Separate creation from the next OVS operation. |
| 38 | <code>        "set",</code> | Request modification of an existing row. |
| 39 | <code>        "bridge",</code> | Target the bridge table. |
| 40 | <code>        "m3s1",</code> | Select this testbed's m3s1 bridge. |
| 41 | <code>        "sflow=@m3sf",</code> | Attach the newly created sFlow row to that bridge. |
| 42 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 43 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 44 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 45 | <code>def main():</code> | Define the topology entry point. |
| 46 | <code>    parser = argparse.ArgumentParser(description=__doc__)</code> | Use module documentation as command help. |
| 47 | <code>    parser.add_argument("--sampling", type=int, default=1)</code> | Accept integer sampling N, default one. |
| 48 | <code>    parser.add_argument("--collector", default="127.0.0.1:6343")</code> | Accept collector destination, default loopback UDP port 6343. |
| 49 | <code>    parser.add_argument("--controller-port", type=int, default=6653)</code> | Accept the remote controller's TCP port, default 6653. |
| 50 | <code>    parser.add_argument("--datapath", choices=["user", "kernel"], default="user")</code> | Allow user or kernel datapath, default user. |
| 51 | <code>    parser.add_argument("--duration", type=float, default=0, help="0 opens Mininet CLI")</code> | Accept runtime seconds; zero selects interactive console mode. |
| 52 | <code>    parser.add_argument(</code> | Begin capture-input argument registration. |
| 53 | <code>        "--pcap", type=Path, help="Prepared Ethernet PCAP with documented address mapping"</code> | Accept a Path pointing to an Ethernet PCAP; address mapping must be prepared/documented externally. |
| 54 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 55 | <code>    parser.add_argument("--pps", type=float, default=1000)</code> | Accept replay packets per second, default 1000. |
| 56 | <code>    parser.add_argument(</code> | Begin diagnostic-probe argument registration. |
| 57 | <code>        "--probe", action="store_true", help="Generate only benign ICMP for telemetry validation"</code> | Enable a benign ICMP probe with a Boolean --probe switch. |
| 58 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 59 | <code>    parser.add_argument("--evidence", type=Path, default=Path("output/sdn/topology.json"))</code> | Choose the topology-evidence JSON output path. |
| 60 | <code>    args = parser.parse_args()</code> | Parse CLI choices. |
| 61 | <code>    if not 0 &lt; args.pps &lt;= 10000:</code> | Require positive replay rate at most 10,000 packets/second, even when no PCAP is supplied. |
| 62 | <code>        parser.error("Replay rate must be between 0 and 10000 packets/s")</code> | Stop with CLI usage error if rate is invalid. |
| 63 | <code>    if args.pcap and not args.pcap.resolve().is_file():</code> | If a PCAP is supplied, require its resolved path to name a file. |
| 64 | <code>        parser.error("Capture does not exist")</code> | Stop if that input file is absent. |
| 65 | <code>    setLogLevel("info")</code> | Enable informational Mininet logging. |
| 66 | <code>    # Only this testbed's named bridge is removed, including after a prior failure.</code> | Comment scopes cleanup to the bridge with this project's fixed name. |
| 67 | <code>    ovs("--timeout=5", "--if-exists", "del-br", "m3s1")</code> | Remove an existing m3s1 bridge with a five-second timeout; running this does modify local OVS state. |
| 68 | <code>    net = Mininet(controller=None, switch=OVSSwitch, autoSetMacs=True, autoStaticArp=True)</code> | Build an OVS-backed Mininet network with deterministic MAC assignment and static ARP. |
| 69 | <code>    net.addController(</code> | Begin adding a remote controller object. |
| 70 | <code>        "m3c0", controller=RemoteController, ip="127.0.0.1", port=args.controller_port</code> | Name it m3c0 and connect to loopback at the requested controller port. |
| 71 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 72 | <code>    switch = net.addSwitch(</code> | Begin adding the virtual OVS switch. |
| 73 | <code>        "m3s1", protocols="OpenFlow13", datapath=args.datapath, failMode="secure"</code> | Name it m3s1, use OpenFlow 1.3 and selected datapath, and use secure fail mode rather than autonomous switching without a controller. |
| 74 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 75 | <code>    hosts = [</code> | Begin creating the four hosts. |
| 76 | <code>        net.addHost(name, ip=f"10.77.0.{index}/24")</code> | Give each named host a numbered 10.77.0.x/24 address. |
| 77 | <code>        for index, name in enumerate(["m3a1", "m3a2", "m3benign", "m3victim"], start=1)</code> | Enumerate attacker-named hosts, benign host and victim from index one; names alone do not generate attacks. |
| 78 | <code>    ]</code> | Close the list or indexing expression begun above. |
| 79 | <code>    for host in hosts:</code> | Visit each virtual host. |
| 80 | <code>        net.addLink(host, switch)</code> | Connect it to the one switch. |
| 81 | <code>    try:</code> | Start a cleanup-protected running phase; earlier topology construction failures are outside this finally. |
| 82 | <code>        net.start()</code> | Start hosts, links, switch and controller connection. |
| 83 | <code>        time.sleep(2)</code> | Wait two seconds for startup. |
| 84 | <code>        set_sampling(args.sampling, args.collector)</code> | Apply real switch-side sFlow configuration. |
| 85 | <code>        loss = net.pingAll(timeout="2")</code> | Ping all host pairs and record percentage packet loss. |
| 86 | <code>        args.evidence.parent.mkdir(parents=True, exist_ok=True)</code> | Create evidence-output folders. |
| 87 | <code>        evidence = {</code> | Begin collecting topology evidence. |
| 88 | <code>            "topology": "isolated_m3_four_hosts",</code> | Identify this topology configuration. |
| 89 | <code>            "sampling_rate": args.sampling,</code> | Record chosen sampling denominator. |
| 90 | <code>            "collector": args.collector,</code> | Record collector address. |
| 91 | <code>            "ping_loss_percent": loss,</code> | Record connectivity loss. |
| 92 | <code>            "datapath": args.datapath,</code> | Record selected datapath mode. |
| 93 | <code>            "flow_table": subprocess.check_output(</code> | Begin querying installed switch forwarding rules. |
| 94 | <code>                ["ovs-ofctl", "-O", "OpenFlow13", "dump-flows", "m3s1"], text=True</code> | Run ovs-ofctl dump-flows explicitly with OpenFlow13. |
| 95 | <code>            ),</code> | Close the multiline call or parenthesized expression begun above; the trailing comma continues the surrounding expression. |
| 96 | <code>            "pcap": str(args.pcap.resolve()) if args.pcap else None,</code> | Record the absolute PCAP path when present, otherwise JSON null. |
| 97 | <code>            "replay_pps": args.pps if args.pcap else None,</code> | Record replay rate only when replay is configured. |
| 98 | <code>            "started_epoch": time.time(),</code> | Record current epoch time after startup/connectivity checks, before probe/replay. |
| 99 | <code>            "quality_ground_truth": "supplied separately; not inferred",</code> | Explicitly record that quality labels must come from a separate source. |
| 100 | <code>        }</code> | Close the dictionary begun above. |
| 101 | <code>        args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")</code> | Write evidence before rejecting connectivity failure. |
| 102 | <code>        if loss:</code> | Treat any nonzero ping loss as failure. |
| 103 | <code>            raise RuntimeError("Controller/topology connectivity failed; inspect controller log")</code> | Raise an error directing investigation to the controller log. |
| 104 | <code>        if args.probe:</code> | Generate diagnostic traffic only if --probe is enabled. |
| 105 | <code>            hosts[2].cmd(</code> | Run the following command inside host index two, m3benign. |
| 106 | <code>                f"ping -q -i 0.01 -c {max(100, int(args.duration * 80))} 10.77.0.4 &gt;/dev/null 2&gt;&amp;1 &amp;"</code> | Launch background quiet ping toward 10.77.0.4 every 0.01 seconds, with at least 100 requests or duration*80; discard its output. |
| 107 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 108 | <code>        if args.pcap:</code> | Branch when a prepared capture is provided. |
| 109 | <code>            # pcap paths are passed as argv, never interpolated into a shell command.</code> | Comment explains the PCAP path is passed as a subprocess argument rather than shell interpolation. |
| 110 | <code>            replay = hosts[0].popen(</code> | Start capture replay inside the first virtual host. |
| 111 | <code>                [</code> | Open the tcpreplay executable and argument list passed to the virtual host process launcher. |
| 112 | <code>                    "tcpreplay",</code> | Select the external tcpreplay program. |
| 113 | <code>                    "--intf1=m3a1-eth0",</code> | Inject only on m3a1-eth0, that host's virtual interface. |
| 114 | <code>                    f"--pps={args.pps}",</code> | Set the requested packets-per-second rate. |
| 115 | <code>                    "--loop=1",</code> | Replay the capture once. |
| 116 | <code>                    str(args.pcap.resolve()),</code> | Pass the resolved capture filename as a separate argument. |
| 117 | <code>                ]</code> | Close the list or indexing expression begun above. |
| 118 | <code>            )</code> | Close the multiline call or parenthesized expression begun above. |
| 119 | <code>        else:</code> | Handle absence of capture replay. |
| 120 | <code>            replay = None</code> | Record that there is no replay process. |
| 121 | <code>        if args.duration:</code> | For any nonzero duration, use timed execution. |
| 122 | <code>            time.sleep(args.duration)</code> | Sleep that number of seconds; negative duration is not checked earlier and will fail here. |
| 123 | <code>        else:</code> | Use interactive mode when duration is zero. |
| 124 | <code>            CLI(net)</code> | Open Mininet's console for this network. |
| 125 | <code>        if replay and replay.poll() is None:</code> | If replay is still running when the duration/console finishes, clean it up. |
| 126 | <code>            replay.terminate()</code> | Request replay termination. |
| 127 | <code>            replay.wait(timeout=5)</code> | Wait up to five seconds for replay exit. |
| 128 | <code>    finally:</code> | Always enter network cleanup after the protected block. |
| 129 | <code>        net.stop()</code> | Stop Mininet and its virtual network resources; no result here establishes attack-detection accuracy. |
| 130 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 131 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 132 | <code>if __name__ == "__main__":</code> | Run only when this module is the launched program. |
| 133 | <code>    main()</code> | Invoke the topology entry point. |

## sdn/validate_sflow.py

Runs a simple UDP receiver and benign topology twice, at N=1 and N=10, to check controller connectivity and actual OVS sFlow export. Requires the Linux SDN environment. Saves raw datagrams as hexadecimal, per-N topology evidence/logs and validation.json. Its small parser counts sample containers; it does not reconstruct features, run M3, validate packet labels or prove sampling effectiveness quantitatively.

| Line | Source | Explanation |
| ---: | --- | --- |
| 1 | <code>"""Verify controller connectivity and real OVS sFlow export at N=1 and N=10.</code> | Docstring introduces real OVS sFlow diagnostics at sampling N=1 and N=10. |
| 2 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 3 | <code>This diagnostic uses benign ICMP only, receives actual UDP datagrams, and saves</code> | Document that only benign ICMP is generated and actual UDP telemetry is retained. |
| 4 | <code>evidence. It is not the M3 learning collector or an attack-quality experiment.</code> | Limit the claim to telemetry/connectivity rather than M3 training or attack quality. |
| 5 | <code>"""</code> | Close the module documentation string. |
| 6 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 7 | <code>import json</code> | Import JSON evidence serialization. |
| 8 | <code>import socket</code> | Import TCP/UDP sockets. |
| 9 | <code>import struct</code> | Import binary network-integer decoding. |
| 10 | <code>import subprocess</code> | Import controller/topology process handling. |
| 11 | <code>import sys</code> | Import current-interpreter location and exit handling. |
| 12 | <code>import time</code> | Import monotonic deadlines and brief waits. |
| 13 | <code>from pathlib import Path</code> | Import filesystem paths. |
| 14 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 15 | <code>ROOT = Path(__file__).resolve().parents[1]</code> | Resolve the repository root. |
| 16 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 17 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 18 | <code>def flow_sample_count(payload):</code> | Define a small top-level sFlow flow-sample counter, not a complete sFlow decoder. |
| 19 | <code>    if len(payload) &lt; 28 or struct.unpack_from("!I", payload)[0] != 5:</code> | Require at least 28 bytes and sFlow version 5; !I means one unsigned 32-bit big-endian integer. |
| 20 | <code>        return 0</code> | Count zero for a too-short/non-v5 datagram. |
| 21 | <code>    kind = struct.unpack_from("!I", payload, 4)[0]</code> | Read agent-address type from byte offset four. |
| 22 | <code>    if kind not in (1, 2):</code> | Support only IPv4 type one and IPv6 type two. |
| 23 | <code>        return 0</code> | Count zero for unsupported address types. |
| 24 | <code>    offset = 12 if kind == 1 else 24</code> | Choose header offset after the IPv4 or IPv6 agent address. |
| 25 | <code>    if len(payload) &lt; offset + 16:</code> | Require enough bytes for subagent, sequence, uptime and sample count. |
| 26 | <code>        return 0</code> | Count zero for truncated header. |
| 27 | <code>    count = struct.unpack_from("!I", payload, offset + 12)[0]</code> | Read number of top-level samples twelve bytes into this header section. |
| 28 | <code>    offset += 16</code> | Advance past its 16-byte fixed portion. |
| 29 | <code>    flows = 0</code> | Initialize flow-sample count. |
| 30 | <code>    for _ in range(count):</code> | Visit the advertised number of sample records. |
| 31 | <code>        if len(payload) &lt; offset + 8:</code> | Require at least the next sample's tag and length header. |
| 32 | <code>            break</code> | Stop if this outer header is truncated. |
| 33 | <code>        tag, length = struct.unpack_from("!II", payload, offset)</code> | Decode two unsigned big-endian integers: sample tag and body length. |
| 34 | <code>        flows += int(tag in (1, 3))</code> | Count ordinary flow sample tag one or expanded flow sample tag three; other sample kinds do not increment. |
| 35 | <code>        offset += 8 + length</code> | Skip the eight-byte sample header plus advertised body; payload length and inner content are not validated here. |
| 36 | <code>    return flows</code> | Return the count observed by this lightweight diagnostic. |
| 37 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 38 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 39 | <code>def main():</code> | Define diagnostic-run entry point. |
| 40 | <code>    output = ROOT / "output" / "sdn"</code> | Choose output/sdn. |
| 41 | <code>    output.mkdir(parents=True, exist_ok=True)</code> | Create its directories. |
| 42 | <code>    manager = Path(sys.executable).parent / "osken-manager"</code> | Locate osken-manager beside the current Python interpreter. |
| 43 | <code>    controller_log = (output / "controller.log").open("w")</code> | Open controller.log in overwrite mode. |
| 44 | <code>    controller = subprocess.Popen(</code> | Launch the learning-switch controller asynchronously. |
| 45 | <code>        [str(manager), "--ofp-tcp-listen-port", "6653", str(ROOT / "sdn" / "controller.py")],</code> | Pass TCP port 6653 and the controller source path as argv. |
| 46 | <code>        stdout=controller_log,</code> | Redirect controller stdout into the log. |
| 47 | <code>        stderr=subprocess.STDOUT,</code> | Merge controller stderr into stdout. |
| 48 | <code>    )</code> | Close the multiline call or parenthesized expression begun above. |
| 49 | <code>    evidence = []</code> | Initialize one evidence row per sampling configuration. |
| 50 | <code>    try:</code> | Start cleanup-protected diagnostics. |
| 51 | <code>        deadline = time.monotonic() + 60</code> | Set a 60-second controller readiness deadline. |
| 52 | <code>        ready = False</code> | Track whether readiness has been observed. |
| 53 | <code>        while time.monotonic() &lt; deadline:</code> | Retry while before the monotonic deadline. |
| 54 | <code>            if controller.poll() is not None:</code> | Detect controller process exit. |
| 55 | <code>                raise RuntimeError("Controller exited; inspect output/sdn/controller.log")</code> | Raise an error pointing to controller.log. |
| 56 | <code>            try:</code> | Begin a connection attempt. |
| 57 | <code>                with socket.create_connection(("127.0.0.1", 6653), timeout=0.5):</code> | Attempt loopback TCP port 6653 with a half-second timeout. |
| 58 | <code>                    ready = True</code> | Mark the listener reachable. |
| 59 | <code>                    break</code> | Leave the readiness loop. |
| 60 | <code>            except OSError:</code> | Handle socket connection failure. |
| 61 | <code>                time.sleep(0.25)</code> | Pause a quarter-second before another attempt. |
| 62 | <code>        if not ready:</code> | Check whether all readiness attempts failed. |
| 63 | <code>            raise RuntimeError("Controller did not listen within 60 seconds")</code> | Raise a controller-start timeout. |
| 64 | <code>        for rate in (1, 10):</code> | Run the same benign diagnostic once at N=1 and once at N=10. |
| 65 | <code>            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:</code> | Create a managed IPv4 UDP socket. |
| 66 | <code>                listener.bind(("127.0.0.1", 6343))</code> | Bind it to loopback port 6343; an existing collector on that port causes bind failure. |
| 67 | <code>                listener.settimeout(0.5)</code> | Set half-second receive timeout so process status can be checked regularly. |
| 68 | <code>                topology_log = (output / f"topology_N{rate}.log").open("w")</code> | Open a per-N topology log. |
| 69 | <code>                topology = subprocess.Popen(</code> | Start the matching topology process asynchronously. |
| 70 | <code>                    [</code> | Open the topology executable and argument list for this sampling-rate diagnostic subprocess. |
| 71 | <code>                        sys.executable,</code> | Use the current Python executable. |
| 72 | <code>                        str(ROOT / "sdn" / "topology.py"),</code> | Run this repository's topology script. |
| 73 | <code>                        "--sampling",</code> | Pass the sampling option name. |
| 74 | <code>                        str(rate),</code> | Pass this iteration's N as a string. |
| 75 | <code>                        "--probe",</code> | Request only a benign ICMP diagnostic probe. |
| 76 | <code>                        "--duration",</code> | Pass a duration option. |
| 77 | <code>                        "8",</code> | Use eight seconds. |
| 78 | <code>                        "--evidence",</code> | Pass an evidence destination option. |
| 79 | <code>                        str(output / f"topology_N{rate}.json"),</code> | Write topology evidence into a per-N JSON file. |
| 80 | <code>                    ],</code> | Close the list or indexing expression begun above; a trailing comma is permitted. |
| 81 | <code>                    stdout=topology_log,</code> | Redirect topology stdout into the per-N log. |
| 82 | <code>                    stderr=subprocess.STDOUT,</code> | Merge topology stderr into that log. |
| 83 | <code>                    cwd=ROOT,</code> | Use the repository as working directory. |
| 84 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 85 | <code>                deadline = time.monotonic() + 60</code> | Set a 60-second reception/process deadline. |
| 86 | <code>                packets = []</code> | Collect received raw UDP payloads in memory. |
| 87 | <code>                while time.monotonic() &lt; deadline:</code> | Continue until the deadline. |
| 88 | <code>                    try:</code> | Begin a timed receive attempt. |
| 89 | <code>                        payload, _source = listener.recvfrom(65535)</code> | Read up to 65,535 bytes and keep the sender in an intentionally unused _source variable. |
| 90 | <code>                        packets.append(payload)</code> | Append this actual received UDP datagram. |
| 91 | <code>                    except TimeoutError:</code> | Handle receive timeout. |
| 92 | <code>                        pass</code> | Do nothing on timeout; proceed to inspect process status. |
| 93 | <code>                    if topology.poll() is not None:</code> | Check whether the topology subprocess has finished. |
| 94 | <code>                        break</code> | Stop reception after topology exit; queued later datagrams are not drained. |
| 95 | <code>                if topology.poll() is None:</code> | Detect a topology still running after the deadline. |
| 96 | <code>                    topology.terminate()</code> | Request its termination. |
| 97 | <code>                    topology.wait(timeout=10)</code> | Wait up to ten seconds for its exit. |
| 98 | <code>                    raise RuntimeError("Topology timed out; inspect its log")</code> | Raise an error pointing to its log. |
| 99 | <code>                topology_log.close()</code> | Close this iteration's topology log. |
| 100 | <code>                topology_data = (</code> | Begin selecting available topology evidence. |
| 101 | <code>                    json.loads((output / f"topology_N{rate}.json").read_text())</code> | Read and parse its JSON if present. |
| 102 | <code>                    if (output / f"topology_N{rate}.json").exists()</code> | Test existence of the per-N evidence file. |
| 103 | <code>                    else {}</code> | Use an empty dictionary if topology produced no evidence. |
| 104 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 105 | <code>                flows = sum(flow_sample_count(packet) for packet in packets)</code> | Count all ordinary/expanded flow samples in the collected datagrams. |
| 106 | <code>                (output / f"sflow_N{rate}.hex").write_text(</code> | Begin saving raw telemetry as hexadecimal text. |
| 107 | <code>                    "\n".join(packet.hex() for packet in packets) + "\n"</code> | Write one datagram per line and a final newline; this preserves bytes as hex, not as a PCAP. |
| 108 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 109 | <code>                row = {</code> | Begin this configuration's evidence row. |
| 110 | <code>                    "sampling_rate": rate,</code> | Record sampling denominator N. |
| 111 | <code>                    "controller_pid": controller.pid,</code> | Record the actual controller PID. |
| 112 | <code>                    "topology_exit_code": topology.returncode,</code> | Record topology process status. |
| 113 | <code>                    "ping_loss_percent": topology_data.get("ping_loss_percent"),</code> | Read connectivity loss from topology evidence, returning None if unavailable. |
| 114 | <code>                    "datagrams": len(packets),</code> | Count received UDP datagrams. |
| 115 | <code>                    "received_bytes": sum(map(len, packets)),</code> | Sum UDP payload lengths; this excludes link/IP/UDP overhead and is not total OpenFlow bandwidth. |
| 116 | <code>                    "flow_samples": flows,</code> | Record counted sFlow flow samples. |
| 117 | <code>                    "traffic": "benign ICMP diagnostic",</code> | Identify the generated traffic as a benign diagnostic. |
| 118 | <code>                }</code> | Close the dictionary begun above. |
| 119 | <code>                row["passed"] = (</code> | Begin computing this iteration's pass condition. |
| 120 | <code>                    topology.returncode == 0 and row["ping_loss_percent"] == 0 and flows &gt; 0</code> | Pass only for successful topology exit, zero ping loss and at least one received flow sample. |
| 121 | <code>                )</code> | Close the multiline call or parenthesized expression begun above. |
| 122 | <code>                evidence.append(row)</code> | Append this result to the evidence collection. |
| 123 | <code>                print(json.dumps(row), flush=True)</code> | Print it immediately as JSON. |
| 124 | <code>    finally:</code> | Enter cleanup even if diagnostics fail. |
| 125 | <code>        controller.terminate()</code> | Terminate the controller. |
| 126 | <code>        controller.wait(timeout=10)</code> | Wait up to ten seconds for it to exit. |
| 127 | <code>        controller_log.close()</code> | Close the controller log. |
| 128 | <code>        (output / "validation.json").write_text(json.dumps(evidence, indent=2) + "\n")</code> | Write all evidence rows collected so far into validation.json. |
| 129 | <code>    return 0 if len(evidence) == 2 and all(row["passed"] for row in evidence) else 1</code> | Return success only when both N configurations exist and each passed; does not test whether the sample count ratio equals ten. |
| 130 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 131 | <code>&#160;</code> | Blank line for visual separation; no runtime operation. |
| 132 | <code>if __name__ == "__main__":</code> | Run the diagnostic only on direct execution. |
| 133 | <code>    raise SystemExit(main())</code> | Convert its integer result to process exit status. |

## Questions you should be able to answer after reading

- Why do raw downloads need a publisher hash while extracted members also need parent hashes?
- Why is an Offset join stronger than guessing labels from capture filenames?
- Why does joining an ICMP endpoint pair require care about overlapping flow intervals and packet coverage?
- Why is controller forwarding independent of M3's ground truth and predictions here?
- Which script counts sFlow containers and which launches the actual M3 collector?
- Why can an unlabeled benign live run demonstrate telemetry collection without demonstrating attack recall?
- Why is received UDP payload size different from complete network bandwidth or controller control-channel traffic?

## Implementation boundaries and observations

These files support several different evidence levels. Keep publisher download verification, flow-record join verification, packet ground-truth verification, and live attack-quality evaluation separate in your explanation and report.

The downloader refuses to overwrite mismatching originals and partial files. It verifies member contents before reusing extracted files and rejects paths that escape the extraction directory. Its signed-URL hostname check happens before opening the URL; redirects are not independently host-restricted. The manifest writes stage a file before replacement but provide no general concurrent-writer lock.

The strict flow-label preparation currently targets BS2 sessions for UDPFlood, SYNFlood and ICMPFlood. It requires the separately downloaded per-session Argus inputs. It compares addresses, protocol, packet/byte counts, duration and displayed times; it does not compare source/destination ports to the CSV ports. Displayed-time validation checks minute/second distance within an hour, whereas the saved epoch times come from Argus. A manifest entry matching path/digest is required, but `verify_source` does not explicitly test its verification_status. These describe the actual checks without changing them.

The lightweight sFlow diagnostic checks version, agent-address type and outer sample headers. It does not comprehensively validate nested record lengths. Passing diagnostics requires received flow samples for both rates, not a proven 10:1 ratio, detection accuracy or learned adaptation.

The live collector validation has no labels path. Ground truth cannot be obtained from the model's own predictions. Labeled online test-then-train learning, drift-error signals and accuracy require a valid external label source elsewhere in the application.

Topology setup removes the existing fixed-name m3s1 bridge, creates a local testbed, and stops it afterward. Timed orchestration uses real delays and bounded process waits. Some timeout paths have no force-kill fallback. Nothing here was executed to create this guide; source inspection and line-coverage verification were the checks performed.

