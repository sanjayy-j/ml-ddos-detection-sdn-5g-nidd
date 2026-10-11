# Official 5G-NIDD data provenance

The project uses the authors' Fairdata release, not Kaggle or a synthetic substitute:

- DOI: https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361
- Publication record: https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65
- Authors' repository: https://github.com/yushan1986/5g-nidd
- Citation: Y. Siriwardhana et al., *Descriptor: 5G Wireless Network Intrusion Detection Dataset (5G-NIDD)*, IEEE Data Descriptions, DOI 10.1109/IEEEDATA.2025.3592888.
- Dataset license: CC BY 4.0, as stated in the dataset's access-rights metadata.

Run `python scripts/fetch_dataset.py` for the official README, Combined archive,
and both per-attack CSV archives. `--captures` adds both GTP-removed capture
archives (approximately 3.9 GB); `--list` prints all official file sizes/checksums.

Public metadata is obtained from Fairdata's Metax v3 `/directories` endpoint using
the dataset ID, IDA storage service and project 2006938. The downloader uses the
same Etsin public `/api/download/authorize` endpoint as the site's download button.
Metax v3 download authorization currently returns `Download is not enabled`, so
the verified public legacy portal endpoint is used instead. Signed URLs are
transient and are not stored. Stable endpoint, official path, file identifier,
publisher checksum, and local checksum are recorded in `data/manifest.json`.

ZIP archives and extracted member bytes remain unchanged. Derived files must
record their parent checksum and each transformation. The model runner verifies
its input SHA256 against the manifest before claiming official data provenance.

## Scope and ground truth

CSV `Label` and `Attack Type` fields provide supervision and never model inputs.
Use Benign as negative and UDPFlood, SYNFlood and ICMPFlood as positive in the
network-flood experiment. Exclude scans, HTTPFlood, and SlowrateDoS. This is a
project scope decision: the official dataset describes both DoS and port scans,
so its broader `Malicious` label is not a binary DDoS definition by itself.

Combined CSV order is not automatically chronological. Verify timestamp/session
metadata and document any constructed sequence. CSV rows are flows; subsampling
rows measures flow sampling, whereas live OVS sFlow samples packets. Keep these
evaluation modes and their metric units identifiable.

Packet labels must be linked to verified session timing and endpoint metadata.
An attack-named capture can also contain benign traffic, so its filename alone
does not authorize labeling every packet malicious. Live replay remains unscored
until those mappings and transformed capture provenance are established.
