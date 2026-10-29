# GitHub backup and restoration

The project backup release is named `m3-backup-2026-10-29` in
`sanjayy-j/ml-ddos-detection-sdn-5g-nidd`. Source remains under
`M3-sampled-incremental/results/m3-implementation/`; M1 and M2 are preserved.

## Backup contents

The source tree contains the app, diagnostics, tests, code guide, latest study
package and report-preparation instructions. Large release archives additionally
preserve original/derived data, every historical and latest experiment's raw
evidence, failures and retry records, reports/slides, partner files, spreadsheet
exports, graphs and authored temporary work. This is wider than the small
derived-evidence ZIP used for dashboard viewing.

`BACKUP_MANIFEST.json` lists every archived project-relative file with its byte
size and SHA256, and each archive part with its size/hash. A separate Git bundle
preserves the implementation repository's pre-backup history. Backup metadata
generated afterward is published separately in the repository/release.

Archives are gzip tar streams divided into parts smaller than GitHub's 2 GiB
asset limit. Part names and order are explicit in the manifest. Download and
verify all parts; a partial set is not a complete backup.

The backup excludes reinstallable virtual environments, dependencies/tool
downloads, bytecode/test caches, Git internals (history is bundled separately),
junction targets outside the project, and the backup's own working directory.
The manifest records exclusions. Authored scripts and evidence under `tmp/`
are included; `tmp/` is not treated wholesale as disposable.

## Before deleting the local project

Check `BACKUP_VERIFICATION.json`: it is created only after uploads and remote
checks finish. It must identify the complete release, exact source commit,
every asset's matching size/hash, and successful restoration checks. An
unfinished upload, a Git commit alone, or a populated release page is not this
verification. If the receipt is absent/incomplete, retain the local project.

This backup covers `CN Project/Project`. It does not back up the whole computer,
Windows, other folders, credentials or software installed outside this project.

## Restore the complete project

Clone the shared repository. From its implementation directory, use Python 3.12+
and choose a new, empty restoration directory. No model packages are needed just
to restore bytes:

```powershell
python scripts/restore_project_backup.py `
  --manifest BACKUP_MANIFEST.json `
  --assets C:/M3_Backup_Assets `
  --destination C:/M3_Restored `
  --download
```

`--download` fetches missing public release assets. Files already downloaded are
verified, not blindly trusted. The tool verifies all asset hashes, rejects unsafe
archive paths/types and verifies every extracted file against the manifest. A
successful full restore writes `.m3_restore_verification.json`. Keep enough free
space for both compressed assets and the uncompressed project.

Use the current restoration script from the repository. It enables Windows
extended-length paths for deeply nested historical evidence and temporary work.
The archive preserves the earlier source snapshot; backup tooling fixes and
verification metadata committed afterward remain available in the GitHub source.

For an offline asset check, use `--verify-only` with the manifest and asset
directory. This checks payload/member hashes as well as archive parts; it does
not recreate a project tree. For exact pre-backup Git history, clone the separate
`.bundle` into another empty directory; restore artifacts to a separate folder.

Reinstall Python/Node dependencies and rebuild the frontend to run the app.
Live experiments additionally require the isolated Linux/WSL Mininet/OVS setup.
See the README and dependency snapshots. Library installations and fresh-machine
setup are separate from byte-for-byte backup restoration. OVS sampling and host
scheduling prevent a promise of identical future experimental scores.

Historical run summaries retain original absolute paths as provenance. For raw
audit on a different machine, resolve those roots to the restored files in an
audit copy; keep the archived originals unchanged. Fresh runs generate paths for
their new location.

## Dataset attribution

Original 5G-NIDD publisher files and derived packet/label/measurement evidence
are included. Source: [official Fairdata release](https://doi.org/10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361),
by the 5G-NIDD dataset authors, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Publisher archives retain their original bytes. Derived transformations include
label joins, packet selection, Ethernet MAC rewriting, constructed replay timing,
switch sampling and feature/metric extraction. Attribution/provenance remains in
`data/manifest.json`, the dataset README and per-run evidence. No endorsement by
the dataset authors is implied.
