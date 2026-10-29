# Reference JSON: provenance and dependency identity

These are structured records rather than model algorithms. Every physical line is paired below so a field can be understood without mistaking metadata for runtime detection logic. Repeated archive/package entries follow the same schema. Hash strings are byte fingerprints; their individual characters are not instructions.

## data/manifest.json

Physical source lines: 650.

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>{</code> | Open a JSON object (named fields). |
| 2 | <code>  &quot;dataset&quot;: &quot;5G-NIDD&quot;,</code> | dataset: Exact dataset identity. The runner requires 5G-NIDD. |
| 3 | <code>  &quot;doi&quot;: &quot;10.23729/e80ac9df-d9fb-47e7-8d0d-01384a415361&quot;,</code> | doi: Stable official dataset release identifier checked by provenance.py. |
| 4 | <code>  &quot;source_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | source_url: Publisher landing page retained for provenance; loading this JSON does not visit it. |
| 5 | <code>  &quot;license&quot;: &quot;CC-BY-4.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 6 | <code>  &quot;files&quot;: [</code> | files: Begin/continue the list of registered original or prepared data artifacts. |
| 7 | <code>    {</code> | Open a JSON object (named fields). |
| 8 | <code>      &quot;path&quot;: &quot;data/raw/README.pdf&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 9 | <code>      &quot;sha256&quot;: &quot;9a8540d4279a49790fe4671aa772f1e70632dd96aea42052b0dcde997f96a8a4&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 10 | <code>      &quot;size_bytes&quot;: 147386,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 11 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 12 | <code>      &quot;official_filename&quot;: &quot;README.pdf&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 13 | <code>      &quot;official_file_id&quot;: &quot;fb96e657-1ffa-436b-8472-d45c0ab99499&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 14 | <code>      &quot;official_path&quot;: &quot;/README.pdf&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 15 | <code>      &quot;publisher_sha256&quot;: &quot;9a8540d4279a49790fe4671aa772f1e70632dd96aea42052b0dcde997f96a8a4&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 16 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 17 | <code>    {</code> | Open a JSON object (named fields). |
| 18 | <code>      &quot;path&quot;: &quot;data/raw/Combined.zip&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 19 | <code>      &quot;sha256&quot;: &quot;07531b251f3f35be70bf1d3dcca2e27274bd1b267c5a057c0fcea18668b9293d&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 20 | <code>      &quot;size_bytes&quot;: 28028224,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 21 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 22 | <code>      &quot;official_filename&quot;: &quot;Combined.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 23 | <code>      &quot;official_file_id&quot;: &quot;b8f5a22c-ee6e-4c0f-8021-8bc66bec4755&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 24 | <code>      &quot;official_path&quot;: &quot;/Combined.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 25 | <code>      &quot;publisher_sha256&quot;: &quot;07531b251f3f35be70bf1d3dcca2e27274bd1b267c5a057c0fcea18668b9293d&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 26 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 27 | <code>    {</code> | Open a JSON object (named fields). |
| 28 | <code>      &quot;path&quot;: &quot;data/raw/Combined/Combined.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 29 | <code>      &quot;sha256&quot;: &quot;fa36f80859585f474504ca69eb951a079b35145537976c86b00aae3aab46ee59&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 30 | <code>      &quot;size_bytes&quot;: 275265610,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 31 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 32 | <code>      &quot;official_filename&quot;: &quot;Combined.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 33 | <code>      &quot;official_file_id&quot;: &quot;b8f5a22c-ee6e-4c0f-8021-8bc66bec4755&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 34 | <code>      &quot;official_path&quot;: &quot;/Combined.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 35 | <code>      &quot;parent_sha256&quot;: &quot;07531b251f3f35be70bf1d3dcca2e27274bd1b267c5a057c0fcea18668b9293d&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 36 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 37 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/Combined/Combined.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 38 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 39 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 40 | <code>    {</code> | Open a JSON object (named fields). |
| 41 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv.zip&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 42 | <code>      &quot;sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 43 | <code>      &quot;size_bytes&quot;: 24613162,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 44 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 45 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 46 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 47 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 48 | <code>      &quot;publisher_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 49 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 50 | <code>    {</code> | Open a JSON object (named fields). |
| 51 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Goldeneye1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 52 | <code>      &quot;sha256&quot;: &quot;e093e8f62842379743d040b5fbf7c7bc30db08e8464e8d1388f2f2a799dabc0b&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 53 | <code>      &quot;size_bytes&quot;: 37532795,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 54 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 55 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 56 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 57 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 58 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 59 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 60 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Goldeneye1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 61 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 62 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 63 | <code>    {</code> | Open a JSON object (named fields). |
| 64 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/ICMPFlood1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 65 | <code>      &quot;sha256&quot;: &quot;7660b7b87e9ff95af4218b779c88036612ee025759cb13f200bd89f8bc1fa9e6&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 66 | <code>      &quot;size_bytes&quot;: 5932192,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 67 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 68 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 69 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 70 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 71 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 72 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 73 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/ICMPFlood1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 74 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 75 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 76 | <code>    {</code> | Open a JSON object (named fields). |
| 77 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Slowloris1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 78 | <code>      &quot;sha256&quot;: &quot;f04729e388275d77b4aa2e916733d02e4a5d946cf60cd6fd19bddc6c6e5215f5&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 79 | <code>      &quot;size_bytes&quot;: 10565865,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 80 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 81 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 82 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 83 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 84 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 85 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 86 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Slowloris1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 87 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 88 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 89 | <code>    {</code> | Open a JSON object (named fields). |
| 90 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SSH1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 91 | <code>      &quot;sha256&quot;: &quot;3531a7aed3a263a1a8ff34ecdfe2218ead6db2ad4d56c36a53fb82f4976dd2d6&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 92 | <code>      &quot;size_bytes&quot;: 595485,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 93 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 94 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 95 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 96 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 97 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 98 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 99 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SSH1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 100 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 101 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 102 | <code>    {</code> | Open a JSON object (named fields). |
| 103 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SYNFlood1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 104 | <code>      &quot;sha256&quot;: &quot;8f841f07491cbf5363a73753e7c942e07e0129686276a6fbb1a103a07b9739b5&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 105 | <code>      &quot;size_bytes&quot;: 14311032,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 106 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 107 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 108 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 109 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 110 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 111 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 112 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SYNFlood1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 113 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 114 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 115 | <code>    {</code> | Open a JSON object (named fields). |
| 116 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SYNScan1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 117 | <code>      &quot;sha256&quot;: &quot;cdb6b51eaad6284ef950d3e7721dde9f21b0228f9cf9210a45ed73eb978e7b32&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 118 | <code>      &quot;size_bytes&quot;: 3617343,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 119 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 120 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 121 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 122 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 123 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 124 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 125 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/SYNScan1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 126 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 127 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 128 | <code>    {</code> | Open a JSON object (named fields). |
| 129 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/TCPConnect1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 130 | <code>      &quot;sha256&quot;: &quot;d703ee3ee5c707c786b65dd11259de25ff962b89fefff3745b08f0bdf4e4e36a&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 131 | <code>      &quot;size_bytes&quot;: 3825843,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 132 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 133 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 134 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 135 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 136 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 137 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 138 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/TCPConnect1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 139 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 140 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 141 | <code>    {</code> | Open a JSON object (named fields). |
| 142 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Torshammer1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 143 | <code>      &quot;sha256&quot;: &quot;18082b7ae8d4b653f2aa4e06eaf9c95cf48b5734749901cd0c83decae3b3377f&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 144 | <code>      &quot;size_bytes&quot;: 16993694,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 145 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 146 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 147 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 148 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 149 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 150 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 151 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/Torshammer1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 152 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 153 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 154 | <code>    {</code> | Open a JSON object (named fields). |
| 155 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/UDPFlood1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 156 | <code>      &quot;sha256&quot;: &quot;ae13e398acc735e081ab1d1e5953cd806392c6d6305b4d93263f2d02a35bf68d&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 157 | <code>      &quot;size_bytes&quot;: 155166901,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 158 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 159 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 160 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 161 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 162 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 163 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 164 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/UDPFlood1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 165 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 166 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 167 | <code>    {</code> | Open a JSON object (named fields). |
| 168 | <code>      &quot;path&quot;: &quot;data/raw/BS1_each_attack_csv/BS1_each_attack_csv/UDPScan1.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 169 | <code>      &quot;sha256&quot;: &quot;8bc5d91d995013c1ef305fa2e761ca16c7b2520e12edd331c9d26700f8ab803b&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 170 | <code>      &quot;size_bytes&quot;: 3100867,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 171 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 172 | <code>      &quot;official_filename&quot;: &quot;BS1_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 173 | <code>      &quot;official_file_id&quot;: &quot;a61b3852-3bd4-4348-831d-a6bcdf1f28db&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 174 | <code>      &quot;official_path&quot;: &quot;/BS1_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 175 | <code>      &quot;parent_sha256&quot;: &quot;b0e28ce972465aa1463113de6225b883a383b9f3bc34d8a21283070f192883e9&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 176 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 177 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS1_each_attack_csv/BS1_each_attack_csv/UDPScan1.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 178 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 179 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 180 | <code>    {</code> | Open a JSON object (named fields). |
| 181 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv.zip&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 182 | <code>      &quot;sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 183 | <code>      &quot;size_bytes&quot;: 18096710,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 184 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 185 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 186 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 187 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 188 | <code>      &quot;publisher_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 189 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 190 | <code>    {</code> | Open a JSON object (named fields). |
| 191 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Goldeneye2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 192 | <code>      &quot;sha256&quot;: &quot;9ca771f50464352ccb26a0960a759223f5f6c78da92115f7f11d47e3fed6142d&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 193 | <code>      &quot;size_bytes&quot;: 36125725,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 194 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 195 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 196 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 197 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 198 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 199 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 200 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Goldeneye2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 201 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 202 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 203 | <code>    {</code> | Open a JSON object (named fields). |
| 204 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/ICMPFlood2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 205 | <code>      &quot;sha256&quot;: &quot;82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 206 | <code>      &quot;size_bytes&quot;: 4728357,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 207 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 208 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 209 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 210 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 211 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 212 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 213 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/ICMPFlood2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 214 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 215 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 216 | <code>    {</code> | Open a JSON object (named fields). |
| 217 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Slowloris2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 218 | <code>      &quot;sha256&quot;: &quot;bf55e1f7ff74701397547b700a8a27935ece31ffb54d3beb1b25aa7bb4aadf01&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 219 | <code>      &quot;size_bytes&quot;: 5105130,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 220 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 221 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 222 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 223 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 224 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 225 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 226 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Slowloris2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 227 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 228 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 229 | <code>    {</code> | Open a JSON object (named fields). |
| 230 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SSH2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 231 | <code>      &quot;sha256&quot;: &quot;d1eb15b0b26f3deac4f0d1cf1163a073049c54374bd82342c2e73d45748dade8&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 232 | <code>      &quot;size_bytes&quot;: 492133,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 233 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 234 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 235 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 236 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 237 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 238 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 239 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SSH2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 240 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 241 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 242 | <code>    {</code> | Open a JSON object (named fields). |
| 243 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SYNFlood2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 244 | <code>      &quot;sha256&quot;: &quot;14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 245 | <code>      &quot;size_bytes&quot;: 5031035,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 246 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 247 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 248 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 249 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 250 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 251 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 252 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SYNFlood2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 253 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 254 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 255 | <code>    {</code> | Open a JSON object (named fields). |
| 256 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SYNScan2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 257 | <code>      &quot;sha256&quot;: &quot;cb857da5662a8aeb26a9a218dd3d18f34ad6beebd99dc1b363657335547966eb&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 258 | <code>      &quot;size_bytes&quot;: 3657768,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 259 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 260 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 261 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 262 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 263 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 264 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 265 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/SYNScan2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 266 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 267 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 268 | <code>    {</code> | Open a JSON object (named fields). |
| 269 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/TCPConnect2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 270 | <code>      &quot;sha256&quot;: &quot;638df746989af267eb9e4d18437f98f7e677371c220dea3aaead99664c832ec8&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 271 | <code>      &quot;size_bytes&quot;: 3839373,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 272 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 273 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 274 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 275 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 276 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 277 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 278 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/TCPConnect2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 279 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 280 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 281 | <code>    {</code> | Open a JSON object (named fields). |
| 282 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Torshammer2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 283 | <code>      &quot;sha256&quot;: &quot;16b638416a9fe71933e983cbfe374a6d8a44789d042ca042321f3f39e2d2abb6&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 284 | <code>      &quot;size_bytes&quot;: 14831875,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 285 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 286 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 287 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 288 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 289 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 290 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 291 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/Torshammer2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 292 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 293 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 294 | <code>    {</code> | Open a JSON object (named fields). |
| 295 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/UDPFlood2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 296 | <code>      &quot;sha256&quot;: &quot;6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 297 | <code>      &quot;size_bytes&quot;: 94425119,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 298 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 299 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 300 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 301 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 302 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 303 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 304 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/UDPFlood2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 305 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 306 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 307 | <code>    {</code> | Open a JSON object (named fields). |
| 308 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_csv/BS2_each_attack_csv/UDPScan2.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 309 | <code>      &quot;sha256&quot;: &quot;16b6fcd0d449949c9ef21356f7bc596770322f2112ed619d2a7c5a83db05330c&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 310 | <code>      &quot;size_bytes&quot;: 3172386,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 311 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 312 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_csv.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 313 | <code>      &quot;official_file_id&quot;: &quot;7f97a49a-f623-46f9-ae25-61388ac9a870&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 314 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_csv.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 315 | <code>      &quot;parent_sha256&quot;: &quot;7ca4f39180cbd598730241c570eca898be41ce67aacafc024bb098714595fdc6&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 316 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 317 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_csv/BS2_each_attack_csv/UDPScan2.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 318 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 319 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 320 | <code>    {</code> | Open a JSON object (named fields). |
| 321 | <code>      &quot;path&quot;: &quot;data/raw/BTS1_BTS2_fields_preserved.zip&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 322 | <code>      &quot;sha256&quot;: &quot;625f4d178c8a8224018cdedaba09ae397c804853c8db0ee1108773fbcf8f2a9d&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 323 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 324 | <code>      &quot;size_bytes&quot;: 46527823,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 325 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 326 | <code>      &quot;official_filename&quot;: &quot;BTS1_BTS2_fields_preserved.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 327 | <code>      &quot;official_file_id&quot;: &quot;b8fbee67-32f2-4f07-a37c-b2c8da768ac4&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 328 | <code>      &quot;official_path&quot;: &quot;/BTS1_BTS2_fields_preserved.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 329 | <code>      &quot;publisher_sha256&quot;: &quot;625f4d178c8a8224018cdedaba09ae397c804853c8db0ee1108773fbcf8f2a9d&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 330 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 331 | <code>    {</code> | Open a JSON object (named fields). |
| 332 | <code>      &quot;path&quot;: &quot;data/raw/BTS1_BTS2_fields_preserved/BTS1_BTS2_fields_preserved.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 333 | <code>      &quot;sha256&quot;: &quot;37287d5188006135d9575687439e47148c5b7adb1a139bd7cd37acc11cec1b9d&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 334 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 335 | <code>      &quot;size_bytes&quot;: 472438689,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 336 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 337 | <code>      &quot;official_filename&quot;: &quot;BTS1_BTS2_fields_preserved.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 338 | <code>      &quot;official_file_id&quot;: &quot;b8fbee67-32f2-4f07-a37c-b2c8da768ac4&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 339 | <code>      &quot;official_path&quot;: &quot;/BTS1_BTS2_fields_preserved.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 340 | <code>      &quot;parent_sha256&quot;: &quot;625f4d178c8a8224018cdedaba09ae397c804853c8db0ee1108773fbcf8f2a9d&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 341 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 342 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BTS1_BTS2_fields_preserved/BTS1_BTS2_fields_preserved.csv): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 343 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 344 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 345 | <code>    {</code> | Open a JSON object (named fields). |
| 346 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus.zip&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 347 | <code>      &quot;sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 348 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 349 | <code>      &quot;size_bytes&quot;: 10733149,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 350 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 351 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 352 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 353 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 354 | <code>      &quot;publisher_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;</code> | publisher_sha256: Checksum advertised by the publisher, checked during the downloader workflow. |
| 355 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 356 | <code>    {</code> | Open a JSON object (named fields). |
| 357 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Goldeneye2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 358 | <code>      &quot;sha256&quot;: &quot;00db85d9c2be1e57dfd3ddfae82092dc7f8671b030c2c106fe5eb80daeb5d8e2&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 359 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 360 | <code>      &quot;size_bytes&quot;: 17316356,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 361 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 362 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 363 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 364 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 365 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 366 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 367 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Goldeneye2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 368 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 369 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 370 | <code>    {</code> | Open a JSON object (named fields). |
| 371 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/ICMPFlood2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 372 | <code>      &quot;sha256&quot;: &quot;e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 373 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 374 | <code>      &quot;size_bytes&quot;: 1957068,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 375 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 376 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 377 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 378 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 379 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 380 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 381 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/ICMPFlood2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 382 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 383 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 384 | <code>    {</code> | Open a JSON object (named fields). |
| 385 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Slowloris2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 386 | <code>      &quot;sha256&quot;: &quot;fa1b18032122223027096ddf4fa32237c6959e6b11adbd36cc3de46b6f41dd77&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 387 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 388 | <code>      &quot;size_bytes&quot;: 2183188,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 389 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 390 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 391 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 392 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 393 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 394 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 395 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Slowloris2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 396 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 397 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 398 | <code>    {</code> | Open a JSON object (named fields). |
| 399 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SSH2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 400 | <code>      &quot;sha256&quot;: &quot;b8c5b51ee02e38222d9a3cba49686eb0804e98f9d6ff974c10b6b7f853f36512&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 401 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 402 | <code>      &quot;size_bytes&quot;: 191036,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 403 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 404 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 405 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 406 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 407 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 408 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 409 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SSH2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 410 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 411 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 412 | <code>    {</code> | Open a JSON object (named fields). |
| 413 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SYNFlood2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 414 | <code>      &quot;sha256&quot;: &quot;96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 415 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 416 | <code>      &quot;size_bytes&quot;: 2307104,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 417 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 418 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 419 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 420 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 421 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 422 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 423 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SYNFlood2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 424 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 425 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 426 | <code>    {</code> | Open a JSON object (named fields). |
| 427 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SYNScan2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 428 | <code>      &quot;sha256&quot;: &quot;6a144aa84550f86a50fd5e9f7f0a98ba7eca0252df44084883d16ca3924d5fff&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 429 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 430 | <code>      &quot;size_bytes&quot;: 1130532,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 431 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 432 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 433 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 434 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 435 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 436 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 437 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/SYNScan2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 438 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 439 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 440 | <code>    {</code> | Open a JSON object (named fields). |
| 441 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/TCPConnect2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 442 | <code>      &quot;sha256&quot;: &quot;56e53da0d19f6002dd0cc35ee2bce352bd4090d366ece3e37f2f972696a614fc&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 443 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 444 | <code>      &quot;size_bytes&quot;: 1148028,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 445 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 446 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 447 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 448 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 449 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 450 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 451 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/TCPConnect2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 452 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 453 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 454 | <code>    {</code> | Open a JSON object (named fields). |
| 455 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Torshammer2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 456 | <code>      &quot;sha256&quot;: &quot;8f0c242e2ed5c8acc05577d1291fc69ddb70cc6f83f25c4ba4a1139285eea08e&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 457 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 458 | <code>      &quot;size_bytes&quot;: 6507848,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 459 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 460 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 461 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 462 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 463 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 464 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 465 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/Torshammer2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 466 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 467 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 468 | <code>    {</code> | Open a JSON object (named fields). |
| 469 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/UDPFlood2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 470 | <code>      &quot;sha256&quot;: &quot;ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 471 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 472 | <code>      &quot;size_bytes&quot;: 24146000,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 473 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 474 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 475 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 476 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 477 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 478 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 479 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/UDPFlood2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 480 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 481 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 482 | <code>    {</code> | Open a JSON object (named fields). |
| 483 | <code>      &quot;path&quot;: &quot;data/raw/BS2_each_attack_argus/BS2_each_attack_argus/UDPScan2.argus&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 484 | <code>      &quot;sha256&quot;: &quot;9f6b0fc9021696bc828bc0402f264c22db5d091497e036addefa4adb4874322b&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 485 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 486 | <code>      &quot;size_bytes&quot;: 943904,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 487 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/api/download/authorize&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 488 | <code>      &quot;official_filename&quot;: &quot;BS2_each_attack_argus.zip&quot;,</code> | official_filename: Publisher archive/original filename associated with this artifact. |
| 489 | <code>      &quot;official_file_id&quot;: &quot;31c692a1-4a2d-4ed8-98ab-7dc025e32f2c&quot;,</code> | official_file_id: Publisher file identifier retained to trace origin. |
| 490 | <code>      &quot;official_path&quot;: &quot;/BS2_each_attack_argus.zip&quot;,</code> | official_path: Publisher storage path retained to trace origin. |
| 491 | <code>      &quot;parent_sha256&quot;: &quot;c40a87ce621da30a0501fa212ec506111f5f3bd4f0dcefa33b9dc77b8fa56921&quot;,</code> | parent_sha256: Checksum of the original parent archive/input from which this derived artifact came. |
| 492 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 493 | <code>        &quot;ZIP extraction only; member bytes unchanged&quot;</code> | Array item for the current artifact (data/raw/BS2_each_attack_argus/BS2_each_attack_argus/UDPScan2.argus): "ZIP extraction only; member bytes unchanged". This is metadata, not a code statement. |
| 494 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 495 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 496 | <code>    {</code> | Open a JSON object (named fields). |
| 497 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_ICMPFlood_ra_numeric.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 498 | <code>      &quot;sha256&quot;: &quot;396393b5c99973f427065cec099855cf8bae720d8b98ab125ed9ac4098935203&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 499 | <code>      &quot;size_bytes&quot;: 1516617,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 500 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 501 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 502 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 503 | <code>        &quot;82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_ra_numeric.csv): "82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f". This is metadata, not a code statement. |
| 504 | <code>        &quot;e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_ra_numeric.csv): "e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3". This is metadata, not a code statement. |
| 505 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 506 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 507 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_ra_numeric.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 508 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_ra_numeric.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 509 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 510 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_ICMPFlood_ra_numeric.csv; the shown value belongs to this manifest entry. |
| 511 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 512 | <code>    {</code> | Open a JSON object (named fields). |
| 513 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_ICMPFlood_flow_labels.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 514 | <code>      &quot;sha256&quot;: &quot;43374a31e4c68180f75c695a52b6c1268baf38a39b6744d5eeffd0ee23e9ab38&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 515 | <code>      &quot;size_bytes&quot;: 1287402,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 516 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 517 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 518 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 519 | <code>        &quot;82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_flow_labels.csv): "82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f". This is metadata, not a code statement. |
| 520 | <code>        &quot;e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_flow_labels.csv): "e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3". This is metadata, not a code statement. |
| 521 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 522 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 523 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_flow_labels.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 524 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_flow_labels.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 525 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 526 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_ICMPFlood_flow_labels.csv; the shown value belongs to this manifest entry. |
| 527 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 528 | <code>    {</code> | Open a JSON object (named fields). |
| 529 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_ICMPFlood_join_audit.json&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 530 | <code>      &quot;sha256&quot;: &quot;4bebeac95eee7aa20eccbfaedb1e82019eef4bbe5f1e2dae36ac819b62222126&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 531 | <code>      &quot;size_bytes&quot;: 814,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 532 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 533 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 534 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 535 | <code>        &quot;82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_join_audit.json): "82f0da146d9416956c2dd9f8209dba39477bee955d2a1b63d6878a3342cc1e9f". This is metadata, not a code statement. |
| 536 | <code>        &quot;e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_join_audit.json): "e274de7cd5fc1b593c2773a9a56e8d3b80d67801839dcbbef02a0b1a91340af3". This is metadata, not a code statement. |
| 537 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 538 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 539 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_join_audit.json): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 540 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_ICMPFlood_join_audit.json): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 541 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 542 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_ICMPFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 543 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 544 | <code>    {</code> | Open a JSON object (named fields). |
| 545 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_SYNFlood_ra_numeric.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 546 | <code>      &quot;sha256&quot;: &quot;762c0786b885e0d3f5036d933bbaeb886586081aaa5e7bd1683f6ff6ea2bf448&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 547 | <code>      &quot;size_bytes&quot;: 1478252,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 548 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 549 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 550 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 551 | <code>        &quot;14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_ra_numeric.csv): "14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5". This is metadata, not a code statement. |
| 552 | <code>        &quot;96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_ra_numeric.csv): "96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4". This is metadata, not a code statement. |
| 553 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 554 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 555 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_ra_numeric.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 556 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_ra_numeric.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 557 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 558 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_SYNFlood_ra_numeric.csv; the shown value belongs to this manifest entry. |
| 559 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 560 | <code>    {</code> | Open a JSON object (named fields). |
| 561 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_SYNFlood_flow_labels.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 562 | <code>      &quot;sha256&quot;: &quot;921c76162cf42d996f4ece45686d670c9e00d22391025523a1bcd49ee86def94&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 563 | <code>      &quot;size_bytes&quot;: 1268436,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 564 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 565 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 566 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 567 | <code>        &quot;14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_flow_labels.csv): "14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5". This is metadata, not a code statement. |
| 568 | <code>        &quot;96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_flow_labels.csv): "96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4". This is metadata, not a code statement. |
| 569 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 570 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 571 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_flow_labels.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 572 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_flow_labels.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 573 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 574 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_SYNFlood_flow_labels.csv; the shown value belongs to this manifest entry. |
| 575 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 576 | <code>    {</code> | Open a JSON object (named fields). |
| 577 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_SYNFlood_join_audit.json&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 578 | <code>      &quot;sha256&quot;: &quot;5a81747fd4d9d7e5463af278f793fbd3d0946113e55409114fe77b483992dc36&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 579 | <code>      &quot;size_bytes&quot;: 812,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 580 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 581 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 582 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 583 | <code>        &quot;14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_join_audit.json): "14571da7fb49603b3bf981bf1fa5132a69625352ca72ff9081bcf9f6000c2aa5". This is metadata, not a code statement. |
| 584 | <code>        &quot;96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_join_audit.json): "96295f00af0a4d6d598d39d58b87ad72b18fd0ae45b0a70fe69c69c1b45e90a4". This is metadata, not a code statement. |
| 585 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 586 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 587 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_join_audit.json): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 588 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_SYNFlood_join_audit.json): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 589 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 590 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_SYNFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 591 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 592 | <code>    {</code> | Open a JSON object (named fields). |
| 593 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_UDPFlood_ra_numeric.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 594 | <code>      &quot;sha256&quot;: &quot;dd6ed181f296541478ca8b549c843a1ffb91a84a0a4048cf64d4cdf787ebe9cc&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 595 | <code>      &quot;size_bytes&quot;: 30114643,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 596 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 597 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 598 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 599 | <code>        &quot;6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_ra_numeric.csv): "6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93". This is metadata, not a code statement. |
| 600 | <code>        &quot;ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_ra_numeric.csv): "ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb". This is metadata, not a code statement. |
| 601 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 602 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 603 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_ra_numeric.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 604 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_ra_numeric.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 605 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 606 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_UDPFlood_ra_numeric.csv; the shown value belongs to this manifest entry. |
| 607 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 608 | <code>    {</code> | Open a JSON object (named fields). |
| 609 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_UDPFlood_flow_labels.csv&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 610 | <code>      &quot;sha256&quot;: &quot;45d74968bd5855f10bdfb6db723651aefb7cd19b2f4680f85fbf282921197d33&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 611 | <code>      &quot;size_bytes&quot;: 26377759,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 612 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 613 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 614 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 615 | <code>        &quot;6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_flow_labels.csv): "6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93". This is metadata, not a code statement. |
| 616 | <code>        &quot;ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_flow_labels.csv): "ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb". This is metadata, not a code statement. |
| 617 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 618 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 619 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_flow_labels.csv): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 620 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_flow_labels.csv): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 621 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 622 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_UDPFlood_flow_labels.csv; the shown value belongs to this manifest entry. |
| 623 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 624 | <code>    {</code> | Open a JSON object (named fields). |
| 625 | <code>      &quot;path&quot;: &quot;data/prepared/BS2_UDPFlood_join_audit.json&quot;,</code> | path: Local input artifact path. verify_input resolves it and compares against the requested file. |
| 626 | <code>      &quot;sha256&quot;: &quot;dedd591ba06cf3589da2a220b365426323663f9cce6afb16e4f55114e5b8625c&quot;,</code> | sha256: Expected SHA256 of these exact file bytes; the runner recomputes and compares it. |
| 627 | <code>      &quot;size_bytes&quot;: 814,</code> | size_bytes: Recorded file length in bytes. This field is metadata; verify_input itself compares hashes. |
| 628 | <code>      &quot;verification_status&quot;: &quot;verified&quot;,</code> | verification_status: Per-file validation state. The runner checks this or compatible manifest flags. |
| 629 | <code>      &quot;download_url&quot;: &quot;https://etsin.fairdata.fi/dataset/9d13ef28-2ca7-44b0-9950-225359afac65&quot;,</code> | download_url: Stable portal endpoint used to obtain an authorized publisher download URL. |
| 630 | <code>      &quot;parent_sha256s&quot;: [</code> | parent_sha256s: Fingerprints of multiple parent sources needed to reproduce a transformation. |
| 631 | <code>        &quot;6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "6b0b6d7471c558eaba05c1b9e1f8867462314aae3b6e296f570e378e1351eb93". This is metadata, not a code statement. |
| 632 | <code>        &quot;ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "ff6e24363624ddfb640b1c58e609ce22306fc6c615abb53d07ae5db692d390bb". This is metadata, not a code statement. |
| 633 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 634 | <code>      &quot;transformations&quot;: [</code> | transformations: Recorded preparation/extraction operations connecting derived bytes to parents. |
| 635 | <code>        &quot;ra -n -u numeric/time export&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "ra -n -u numeric/time export". This is metadata, not a code statement. |
| 636 | <code>        &quot;one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "one-to-one Offset join with endpoint/protocol/count/duration/time consistency checks". This is metadata, not a code statement. |
| 637 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 638 | <code>      &quot;label_scope&quot;: &quot;Flow intervals only; packet coverage and overlap conflicts still require validation&quot;</code> | label_scope: Recorded provenance property label_scope for data/prepared/BS2_UDPFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 639 | <code>    }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 640 | <code>  ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 641 | <code>  &quot;status&quot;: &quot;verified&quot;,</code> | status: Manifest-level status; partial means some entries may still be individually verified. |
| 642 | <code>  &quot;notes&quot;: [</code> | notes: Recorded provenance property notes for data/prepared/BS2_UDPFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 643 | <code>    &quot;Publisher SHA256 checked for each downloaded archive. Extracted files have local SHA256 and parent archive provenance.&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "Publisher SHA256 checked for each downloaded archive. Extracted files have local SHA256 and parent archive provenance.". This is metadata, not a code statement. |
| 644 | <code>    &quot;Combined.csv order must not be claimed chronological without further evidence.&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "Combined.csv order must not be claimed chronological without further evidence.". This is metadata, not a code statement. |
| 645 | <code>    &quot;Capture filenames alone do not provide packet-level attack ground truth.&quot;,</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "Capture filenames alone do not provide packet-level attack ground truth.". This is metadata, not a code statement. |
| 646 | <code>    &quot;Packet capture archives have not been downloaded. Use --captures when needed.&quot;</code> | Array item for the current artifact (data/prepared/BS2_UDPFlood_join_audit.json): "Packet capture archives have not been downloaded. Use --captures when needed.". This is metadata, not a code statement. |
| 647 | <code>  ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 648 | <code>  &quot;metadata_url&quot;: &quot;https://metax.fairdata.fi/v3/directories?path=%2F&amp;storage_service=ida&amp;csc_project=2006938&amp;dataset=9d13ef28-2ca7-44b0-9950-225359afac65&amp;pagination=false&quot;,</code> | metadata_url: Recorded provenance property metadata_url for data/prepared/BS2_UDPFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 649 | <code>  &quot;retrieved_utc&quot;: &quot;2026-10-11T10:02:34Z&quot;</code> | retrieved_utc: Recorded provenance property retrieved_utc for data/prepared/BS2_UDPFlood_join_audit.json; the shown value belongs to this manifest entry. |
| 650 | <code>}</code> | Close the preceding JSON object/array; a comma separates it from the next item. |

## frontend/package-lock.json

Physical source lines: 3084.

| Line | Source | Explanation |
|---:|---|---|
| 1 | <code>{</code> | Open a JSON object (named fields). |
| 2 | <code>  &quot;name&quot;: &quot;m3-observatory&quot;,</code> | name: npm project/package name; identifies the package described by this object. |
| 3 | <code>  &quot;version&quot;: &quot;1.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 4 | <code>  &quot;lockfileVersion&quot;: 3,</code> | lockfileVersion: Version of npm lockfile schema used to interpret the dependency resolution. |
| 5 | <code>  &quot;requires&quot;: true,</code> | requires: npm lock metadata indicating dependency resolution is represented. |
| 6 | <code>  &quot;packages&quot;: {</code> | packages: Map from installation paths to the exact resolved npm dependency records. |
| 7 | <code>    &quot;&quot;: {</code> | Array item for the current artifact (root npm project): "": {. This is metadata, not a code statement. |
| 8 | <code>      &quot;name&quot;: &quot;m3-observatory&quot;,</code> | name: npm project/package name; identifies the package described by this object. |
| 9 | <code>      &quot;version&quot;: &quot;1.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 10 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 11 | <code>        &quot;react&quot;: &quot;^19.0.0&quot;,</code> | react: Dependency requirement or executable metadata named react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 12 | <code>        &quot;react-dom&quot;: &quot;^19.0.0&quot;</code> | react-dom: Dependency requirement or executable metadata named react-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 13 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 14 | <code>      &quot;devDependencies&quot;: {</code> | devDependencies: Build/test/type-tool dependencies used during development. |
| 15 | <code>        &quot;@testing-library/jest-dom&quot;: &quot;^6.6.0&quot;,</code> | @testing-library/jest-dom: Dependency requirement or executable metadata named @testing-library/jest-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 16 | <code>        &quot;@testing-library/react&quot;: &quot;^16.1.0&quot;,</code> | @testing-library/react: Dependency requirement or executable metadata named @testing-library/react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 17 | <code>        &quot;@types/react&quot;: &quot;^19.0.0&quot;,</code> | @types/react: Dependency requirement or executable metadata named @types/react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 18 | <code>        &quot;@types/react-dom&quot;: &quot;^19.0.0&quot;,</code> | @types/react-dom: Dependency requirement or executable metadata named @types/react-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 19 | <code>        &quot;@vitejs/plugin-react&quot;: &quot;^4.3.4&quot;,</code> | @vitejs/plugin-react: Dependency requirement or executable metadata named @vitejs/plugin-react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 20 | <code>        &quot;jsdom&quot;: &quot;^26.0.0&quot;,</code> | jsdom: Dependency requirement or executable metadata named jsdom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 21 | <code>        &quot;typescript&quot;: &quot;^5.7.3&quot;,</code> | typescript: Dependency requirement or executable metadata named typescript. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 22 | <code>        &quot;vite&quot;: &quot;^6.1.0&quot;,</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 23 | <code>        &quot;vitest&quot;: &quot;^3.0.0&quot;</code> | vitest: Dependency requirement or executable metadata named vitest. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 24 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 25 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 26 | <code>    &quot;node_modules/@adobe/css-tools&quot;: {</code> | node_modules/@adobe/css-tools: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 27 | <code>      &quot;version&quot;: &quot;4.5.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 28 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@adobe/css-tools/-/css-tools-4.5.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 29 | <code>      &quot;integrity&quot;: &quot;sha512-6OzddxPio9UiWTCemp4N8cYLV2ZN1ncRnV1cVGtve7dhPOtRkleRyx32GQCYSwDYgaHU3USMm84tNsvKzRCa1Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 30 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 31 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 32 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 33 | <code>    &quot;node_modules/@asamuzakjp/css-color&quot;: {</code> | node_modules/@asamuzakjp/css-color: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 34 | <code>      &quot;version&quot;: &quot;3.2.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 35 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@asamuzakjp/css-color/-/css-color-3.2.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 36 | <code>      &quot;integrity&quot;: &quot;sha512-K1A6z8tS3XsmCMM86xoWdn7Fkdn9m6RSVtocUrJYIwZnFVkng/PvkEoWtOWmP+Scc6saYWHWZYbndEEXxl24jw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 37 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 38 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 39 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 40 | <code>        &quot;@csstools/css-calc&quot;: &quot;^2.1.3&quot;,</code> | @csstools/css-calc: Dependency requirement or executable metadata named @csstools/css-calc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 41 | <code>        &quot;@csstools/css-color-parser&quot;: &quot;^3.0.9&quot;,</code> | @csstools/css-color-parser: Dependency requirement or executable metadata named @csstools/css-color-parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 42 | <code>        &quot;@csstools/css-parser-algorithms&quot;: &quot;^3.0.4&quot;,</code> | @csstools/css-parser-algorithms: Dependency requirement or executable metadata named @csstools/css-parser-algorithms. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 43 | <code>        &quot;@csstools/css-tokenizer&quot;: &quot;^3.0.3&quot;,</code> | @csstools/css-tokenizer: Dependency requirement or executable metadata named @csstools/css-tokenizer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 44 | <code>        &quot;lru-cache&quot;: &quot;^10.4.3&quot;</code> | lru-cache: Dependency requirement or executable metadata named lru-cache. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 45 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 46 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 47 | <code>    &quot;node_modules/@asamuzakjp/css-color/node_modules/lru-cache&quot;: {</code> | node_modules/@asamuzakjp/css-color/node_modules/lru-cache: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 48 | <code>      &quot;version&quot;: &quot;10.4.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 49 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/lru-cache/-/lru-cache-10.4.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 50 | <code>      &quot;integrity&quot;: &quot;sha512-JNAzZcXrCt42VGLuYz0zfAzDfAvJWW6AfYlDBQyDV5DClI2m5sAmK+OIO7s59XfsRsWHp02jAJrRadPRGTt6SQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 51 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 52 | <code>      &quot;license&quot;: &quot;ISC&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 53 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 54 | <code>    &quot;node_modules/@babel/code-frame&quot;: {</code> | node_modules/@babel/code-frame: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 55 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 56 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 57 | <code>      &quot;integrity&quot;: &quot;sha512-Aup7aUOfpbAUg2ROOJN6Iw5f9DMBlzu0mIkm/malLQFN/YQgO48wCj0Kxa3sEHJvPVFg7siR+qRInwXd2qhQKw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 58 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 59 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 60 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 61 | <code>        &quot;@babel/helper-validator-identifier&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-validator-identifier: Dependency requirement or executable metadata named @babel/helper-validator-identifier. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 62 | <code>        &quot;js-tokens&quot;: &quot;^4.0.0&quot;,</code> | js-tokens: Dependency requirement or executable metadata named js-tokens. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 63 | <code>        &quot;picocolors&quot;: &quot;^1.1.1&quot;</code> | picocolors: Dependency requirement or executable metadata named picocolors. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 64 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 65 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 66 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 67 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 68 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 69 | <code>    &quot;node_modules/@babel/compat-data&quot;: {</code> | node_modules/@babel/compat-data: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 70 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 71 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/compat-data/-/compat-data-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 72 | <code>      &quot;integrity&quot;: &quot;sha512-locTkQyKvwIEgBzVrn8693ebc97F2U8ZHjbXwDXJ5Fn2TCpNwTlKcaKLkdHop5c/icOFE7qt7Q9JC5hnKNa6Gg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 73 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 74 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 75 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 76 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 77 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 78 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 79 | <code>    &quot;node_modules/@babel/core&quot;: {</code> | node_modules/@babel/core: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 80 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 81 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/core/-/core-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 82 | <code>      &quot;integrity&quot;: &quot;sha512-RgHBCvtjbOK2gXSNBNIkNoEc9qoVEtau3hj8gEqKQuL3HZAibKarWFEI3Lfm6EYKkLalOh8eSrj9b+ch9H/VBA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 83 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 84 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 85 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 86 | <code>        &quot;@babel/code-frame&quot;: &quot;^7.29.7&quot;,</code> | @babel/code-frame: Dependency requirement or executable metadata named @babel/code-frame. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 87 | <code>        &quot;@babel/generator&quot;: &quot;^7.29.7&quot;,</code> | @babel/generator: Dependency requirement or executable metadata named @babel/generator. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 88 | <code>        &quot;@babel/helper-compilation-targets&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-compilation-targets: Dependency requirement or executable metadata named @babel/helper-compilation-targets. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 89 | <code>        &quot;@babel/helper-module-transforms&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-module-transforms: Dependency requirement or executable metadata named @babel/helper-module-transforms. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 90 | <code>        &quot;@babel/helpers&quot;: &quot;^7.29.7&quot;,</code> | @babel/helpers: Dependency requirement or executable metadata named @babel/helpers. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 91 | <code>        &quot;@babel/parser&quot;: &quot;^7.29.7&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 92 | <code>        &quot;@babel/template&quot;: &quot;^7.29.7&quot;,</code> | @babel/template: Dependency requirement or executable metadata named @babel/template. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 93 | <code>        &quot;@babel/traverse&quot;: &quot;^7.29.7&quot;,</code> | @babel/traverse: Dependency requirement or executable metadata named @babel/traverse. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 94 | <code>        &quot;@babel/types&quot;: &quot;^7.29.7&quot;,</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 95 | <code>        &quot;@jridgewell/remapping&quot;: &quot;^2.3.5&quot;,</code> | @jridgewell/remapping: Dependency requirement or executable metadata named @jridgewell/remapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 96 | <code>        &quot;convert-source-map&quot;: &quot;^2.0.0&quot;,</code> | convert-source-map: Dependency requirement or executable metadata named convert-source-map. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 97 | <code>        &quot;debug&quot;: &quot;^4.1.0&quot;,</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 98 | <code>        &quot;gensync&quot;: &quot;^1.0.0-beta.2&quot;,</code> | gensync: Dependency requirement or executable metadata named gensync. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 99 | <code>        &quot;json5&quot;: &quot;^2.2.3&quot;,</code> | json5: Dependency requirement or executable metadata named json5. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 100 | <code>        &quot;semver&quot;: &quot;^6.3.1&quot;</code> | semver: Dependency requirement or executable metadata named semver. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 101 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 102 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 103 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 104 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 105 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 106 | <code>        &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 107 | <code>        &quot;url&quot;: &quot;https://opencollective.com/babel&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 108 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 109 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 110 | <code>    &quot;node_modules/@babel/generator&quot;: {</code> | node_modules/@babel/generator: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 111 | <code>      &quot;version&quot;: &quot;7.29.8&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 112 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/generator/-/generator-7.29.8.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 113 | <code>      &quot;integrity&quot;: &quot;sha512-gZbepsdh3WDtgZKWL+vTPh71LSBrm/Y4/QDZBVCcYfmeTEEuoOYwlSy+G1StfJg+/Zy550u/3TATbm7qDbbMtg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 114 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 115 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 116 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 117 | <code>        &quot;@babel/parser&quot;: &quot;^7.29.8&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 118 | <code>        &quot;@babel/types&quot;: &quot;^7.29.8&quot;,</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 119 | <code>        &quot;@jridgewell/gen-mapping&quot;: &quot;^0.3.12&quot;,</code> | @jridgewell/gen-mapping: Dependency requirement or executable metadata named @jridgewell/gen-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 120 | <code>        &quot;@jridgewell/trace-mapping&quot;: &quot;^0.3.28&quot;,</code> | @jridgewell/trace-mapping: Dependency requirement or executable metadata named @jridgewell/trace-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 121 | <code>        &quot;jsesc&quot;: &quot;^3.0.2&quot;</code> | jsesc: Dependency requirement or executable metadata named jsesc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 122 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 123 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 124 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 125 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 126 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 127 | <code>    &quot;node_modules/@babel/helper-compilation-targets&quot;: {</code> | node_modules/@babel/helper-compilation-targets: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 128 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 129 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-compilation-targets/-/helper-compilation-targets-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 130 | <code>      &quot;integrity&quot;: &quot;sha512-wem6WaBj4NaVYVdNhLPPVacES6ZJ+KBBfSkTMD3YZxbP3rm3Di85tJU5ljaUNhaOynt+Aj0xruhYuzQBt8n71g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 131 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 132 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 133 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 134 | <code>        &quot;@babel/compat-data&quot;: &quot;^7.29.7&quot;,</code> | @babel/compat-data: Dependency requirement or executable metadata named @babel/compat-data. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 135 | <code>        &quot;@babel/helper-validator-option&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-validator-option: Dependency requirement or executable metadata named @babel/helper-validator-option. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 136 | <code>        &quot;browserslist&quot;: &quot;^4.24.0&quot;,</code> | browserslist: Dependency requirement or executable metadata named browserslist. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 137 | <code>        &quot;lru-cache&quot;: &quot;^5.1.1&quot;,</code> | lru-cache: Dependency requirement or executable metadata named lru-cache. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 138 | <code>        &quot;semver&quot;: &quot;^6.3.1&quot;</code> | semver: Dependency requirement or executable metadata named semver. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 139 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 140 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 141 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 142 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 143 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 144 | <code>    &quot;node_modules/@babel/helper-globals&quot;: {</code> | node_modules/@babel/helper-globals: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 145 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 146 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-globals/-/helper-globals-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 147 | <code>      &quot;integrity&quot;: &quot;sha512-3nQVUAtvkKH9zahfWgw96Jc/uFOmjACE1kQz82E2lqWmHBgjzbNlsC22nuQTfahmWeQtTq5nQ/4Nnd2A1wj4zA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 148 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 149 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 150 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 151 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 152 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 153 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 154 | <code>    &quot;node_modules/@babel/helper-module-imports&quot;: {</code> | node_modules/@babel/helper-module-imports: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 155 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 156 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 157 | <code>      &quot;integrity&quot;: &quot;sha512-ejHwrQQYcm9xnTivShn2IDOlIzInN34AXskvq9QicvCtEzq1Vzclu/tKF8Jq1Cg8JG2GL6/EmjgsCT7lXepE3g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 158 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 159 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 160 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 161 | <code>        &quot;@babel/traverse&quot;: &quot;^7.29.7&quot;,</code> | @babel/traverse: Dependency requirement or executable metadata named @babel/traverse. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 162 | <code>        &quot;@babel/types&quot;: &quot;^7.29.7&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 163 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 164 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 165 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 166 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 167 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 168 | <code>    &quot;node_modules/@babel/helper-module-transforms&quot;: {</code> | node_modules/@babel/helper-module-transforms: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 169 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 170 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-module-transforms/-/helper-module-transforms-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 171 | <code>      &quot;integrity&quot;: &quot;sha512-UPUVSyXbOh627KiCIGQSgwWzGeBKLkaJ9PJEdrngIwMSzxLR4jS4+f1f1jb7VzBbg8nFLaYotvVPFCTqdrmTAg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 172 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 173 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 174 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 175 | <code>        &quot;@babel/helper-module-imports&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-module-imports: Dependency requirement or executable metadata named @babel/helper-module-imports. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 176 | <code>        &quot;@babel/helper-validator-identifier&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-validator-identifier: Dependency requirement or executable metadata named @babel/helper-validator-identifier. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 177 | <code>        &quot;@babel/traverse&quot;: &quot;^7.29.7&quot;</code> | @babel/traverse: Dependency requirement or executable metadata named @babel/traverse. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 178 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 179 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 180 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 181 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 182 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 183 | <code>        &quot;@babel/core&quot;: &quot;^7.0.0&quot;</code> | @babel/core: Dependency requirement or executable metadata named @babel/core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 184 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 185 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 186 | <code>    &quot;node_modules/@babel/helper-plugin-utils&quot;: {</code> | node_modules/@babel/helper-plugin-utils: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 187 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 188 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-plugin-utils/-/helper-plugin-utils-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 189 | <code>      &quot;integrity&quot;: &quot;sha512-G7sHYigPY17oO5SYWnfD/0MTBwVR781S/JI643e/JhUYgVgWE/61SoW3NH9KWUKyKq5LVh3npif99Wkt6j86Jw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 190 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 191 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 192 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 193 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 194 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 195 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 196 | <code>    &quot;node_modules/@babel/helper-string-parser&quot;: {</code> | node_modules/@babel/helper-string-parser: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 197 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 198 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 199 | <code>      &quot;integrity&quot;: &quot;sha512-Pb5ijPrZ89GDH8223L4UP8i6QApWxs04RbPQJTeWDV0/keR2E36MeKnyr6LYmUUvqRRI+Iv87SuF1W6ErINzYw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 200 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 201 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 202 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 203 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 204 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 205 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 206 | <code>    &quot;node_modules/@babel/helper-validator-identifier&quot;: {</code> | node_modules/@babel/helper-validator-identifier: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 207 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 208 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 209 | <code>      &quot;integrity&quot;: &quot;sha512-qehxGkRj55h/ff8EMaJ+cYhyaKlHIxqYDn682wQD7RNp9UujOQsHog2uS0r2vzr4pW+sXf90NeeayjcNaX3fFg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 210 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 211 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 212 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 213 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 214 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 215 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 216 | <code>    &quot;node_modules/@babel/helper-validator-option&quot;: {</code> | node_modules/@babel/helper-validator-option: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 217 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 218 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helper-validator-option/-/helper-validator-option-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 219 | <code>      &quot;integrity&quot;: &quot;sha512-N9ZErrD+yW5geCDtBqnOoxmR8+tNKiGuxKlDpuJxfsqpa2dFcexaziGAE/qoHLiDDreVNMupxGmSoNlyvsA3gw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 220 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 221 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 222 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 223 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 224 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 225 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 226 | <code>    &quot;node_modules/@babel/helpers&quot;: {</code> | node_modules/@babel/helpers: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 227 | <code>      &quot;version&quot;: &quot;7.29.10&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 228 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/helpers/-/helpers-7.29.10.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 229 | <code>      &quot;integrity&quot;: &quot;sha512-EMCx3AGZ3WfAl6ht7AyQoPm2Lh+BGYEMdc4Q6Hf7uSCDOZFuLq44qNwL+iaim8VlyYhRAo4X43+weadK8ZB4Yg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 230 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 231 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 232 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 233 | <code>        &quot;@babel/template&quot;: &quot;^7.29.7&quot;,</code> | @babel/template: Dependency requirement or executable metadata named @babel/template. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 234 | <code>        &quot;@babel/types&quot;: &quot;^7.29.8&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 235 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 236 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 237 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 238 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 239 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 240 | <code>    &quot;node_modules/@babel/parser&quot;: {</code> | node_modules/@babel/parser: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 241 | <code>      &quot;version&quot;: &quot;7.29.9&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 242 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/parser/-/parser-7.29.9.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 243 | <code>      &quot;integrity&quot;: &quot;sha512-CjXrNHTnvqBVqHgdBysY3vk2T8tpJHb5/RMeHJBTyVa9xgugCB0CJTx/3oO8RV2QRQP391RWpB7D6hLjm8V9uA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 244 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 245 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 246 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 247 | <code>        &quot;@babel/types&quot;: &quot;^7.29.8&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 248 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 249 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 250 | <code>        &quot;parser&quot;: &quot;bin/babel-parser.js&quot;</code> | parser: Dependency requirement or executable metadata named parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 251 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 252 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 253 | <code>        &quot;node&quot;: &quot;&gt;=6.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 254 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 255 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 256 | <code>    &quot;node_modules/@babel/plugin-transform-react-jsx-self&quot;: {</code> | node_modules/@babel/plugin-transform-react-jsx-self: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 257 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 258 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/plugin-transform-react-jsx-self/-/plugin-transform-react-jsx-self-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 259 | <code>      &quot;integrity&quot;: &quot;sha512-TL0hMc9xzy86VD31nUiwzd5otRAcyEPcsegCxolO0PvcXuH1v0kECe/UIznYFihpkvU5wg/jk4v0TTEFfm53fw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 260 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 261 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 262 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 263 | <code>        &quot;@babel/helper-plugin-utils&quot;: &quot;^7.29.7&quot;</code> | @babel/helper-plugin-utils: Dependency requirement or executable metadata named @babel/helper-plugin-utils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 264 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 265 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 266 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 267 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 268 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 269 | <code>        &quot;@babel/core&quot;: &quot;^7.0.0-0&quot;</code> | @babel/core: Dependency requirement or executable metadata named @babel/core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 270 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 271 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 272 | <code>    &quot;node_modules/@babel/plugin-transform-react-jsx-source&quot;: {</code> | node_modules/@babel/plugin-transform-react-jsx-source: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 273 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 274 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/plugin-transform-react-jsx-source/-/plugin-transform-react-jsx-source-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 275 | <code>      &quot;integrity&quot;: &quot;sha512-06IyK09H3wi4cGbhDBwp5gUGo0IKtnYa8tyTiephirPCK6fbobVGiXMMI5zLQ4aKEYP3wZ3ArU44o+8KMrSG/Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 276 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 277 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 278 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 279 | <code>        &quot;@babel/helper-plugin-utils&quot;: &quot;^7.29.7&quot;</code> | @babel/helper-plugin-utils: Dependency requirement or executable metadata named @babel/helper-plugin-utils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 280 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 281 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 282 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 283 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 284 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 285 | <code>        &quot;@babel/core&quot;: &quot;^7.0.0-0&quot;</code> | @babel/core: Dependency requirement or executable metadata named @babel/core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 286 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 287 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 288 | <code>    &quot;node_modules/@babel/runtime&quot;: {</code> | node_modules/@babel/runtime: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 289 | <code>      &quot;version&quot;: &quot;7.29.10&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 290 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/runtime/-/runtime-7.29.10.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 291 | <code>      &quot;integrity&quot;: &quot;sha512-NpugTzbKgGrNe45Ui32cN8vCFFMxVtP/9rtfwv0nP5FRDAjvYBxJcLVpYA9mr1jxP6cnIT7x9LUzuDTbWYYNRA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 292 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 293 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 294 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 295 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 296 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 297 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 298 | <code>    &quot;node_modules/@babel/template&quot;: {</code> | node_modules/@babel/template: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 299 | <code>      &quot;version&quot;: &quot;7.29.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 300 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/template/-/template-7.29.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 301 | <code>      &quot;integrity&quot;: &quot;sha512-puq+Gf35oI24FeN11LkoUQFqv9uwNeWpxXZi/Ji3rRIoKAzKnxRaZ+Gkj0vKS9ZCiTESfng1N9LyOyXvo+m+Gg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 302 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 303 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 304 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 305 | <code>        &quot;@babel/code-frame&quot;: &quot;^7.29.7&quot;,</code> | @babel/code-frame: Dependency requirement or executable metadata named @babel/code-frame. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 306 | <code>        &quot;@babel/parser&quot;: &quot;^7.29.7&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 307 | <code>        &quot;@babel/types&quot;: &quot;^7.29.7&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 308 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 309 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 310 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 311 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 312 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 313 | <code>    &quot;node_modules/@babel/traverse&quot;: {</code> | node_modules/@babel/traverse: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 314 | <code>      &quot;version&quot;: &quot;7.29.10&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 315 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/traverse/-/traverse-7.29.10.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 316 | <code>      &quot;integrity&quot;: &quot;sha512-B3lYAs2nkKskbgQ1nfy8Ma9ao9Q1rntTAQHrzzyDuj+TSO+X3le6PfWwqDvodsb+OumE10eMFfuMCTQSQ5iuIQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 317 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 318 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 319 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 320 | <code>        &quot;@babel/code-frame&quot;: &quot;^7.29.7&quot;,</code> | @babel/code-frame: Dependency requirement or executable metadata named @babel/code-frame. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 321 | <code>        &quot;@babel/generator&quot;: &quot;^7.29.8&quot;,</code> | @babel/generator: Dependency requirement or executable metadata named @babel/generator. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 322 | <code>        &quot;@babel/helper-globals&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-globals: Dependency requirement or executable metadata named @babel/helper-globals. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 323 | <code>        &quot;@babel/parser&quot;: &quot;^7.29.9&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 324 | <code>        &quot;@babel/template&quot;: &quot;^7.29.7&quot;,</code> | @babel/template: Dependency requirement or executable metadata named @babel/template. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 325 | <code>        &quot;@babel/types&quot;: &quot;^7.29.8&quot;,</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 326 | <code>        &quot;debug&quot;: &quot;^4.3.1&quot;</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 327 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 328 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 329 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 330 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 331 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 332 | <code>    &quot;node_modules/@babel/types&quot;: {</code> | node_modules/@babel/types: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 333 | <code>      &quot;version&quot;: &quot;7.29.8&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 334 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@babel/types/-/types-7.29.8.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 335 | <code>      &quot;integrity&quot;: &quot;sha512-Vj1jF3cPfxg7OAfoI7QnVKLoILlm2JF9pnVHrX8qx7AHMiYWT+NDAA7jChlNgRS4WTLc/fD1lXLmPixluj+3Gg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 336 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 337 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 338 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 339 | <code>        &quot;@babel/helper-string-parser&quot;: &quot;^7.29.7&quot;,</code> | @babel/helper-string-parser: Dependency requirement or executable metadata named @babel/helper-string-parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 340 | <code>        &quot;@babel/helper-validator-identifier&quot;: &quot;^7.29.7&quot;</code> | @babel/helper-validator-identifier: Dependency requirement or executable metadata named @babel/helper-validator-identifier. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 341 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 342 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 343 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 344 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 345 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 346 | <code>    &quot;node_modules/@csstools/color-helpers&quot;: {</code> | node_modules/@csstools/color-helpers: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 347 | <code>      &quot;version&quot;: &quot;5.1.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 348 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@csstools/color-helpers/-/color-helpers-5.1.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 349 | <code>      &quot;integrity&quot;: &quot;sha512-S11EXWJyy0Mz5SYvRmY8nJYTFFd1LCNV+7cXyAgQtOOuzb4EsgfqDufL+9esx72/eLhsRdGZwaldu/h+E4t4BA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 350 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 351 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 352 | <code>        {</code> | Open a JSON object (named fields). |
| 353 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 354 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 355 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 356 | <code>        {</code> | Open a JSON object (named fields). |
| 357 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 358 | <code>          &quot;url&quot;: &quot;https://opencollective.com/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 359 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 360 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 361 | <code>      &quot;license&quot;: &quot;MIT-0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 362 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 363 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 364 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 365 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 366 | <code>    &quot;node_modules/@csstools/css-calc&quot;: {</code> | node_modules/@csstools/css-calc: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 367 | <code>      &quot;version&quot;: &quot;2.1.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 368 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@csstools/css-calc/-/css-calc-2.1.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 369 | <code>      &quot;integrity&quot;: &quot;sha512-3N8oaj+0juUw/1H3YwmDDJXCgTB1gKU6Hc/bB502u9zR0q2vd786XJH9QfrKIEgFlZmhZiq6epXl4rHqhzsIgQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 370 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 371 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 372 | <code>        {</code> | Open a JSON object (named fields). |
| 373 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 374 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 375 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 376 | <code>        {</code> | Open a JSON object (named fields). |
| 377 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 378 | <code>          &quot;url&quot;: &quot;https://opencollective.com/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 379 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 380 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 381 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 382 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 383 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 384 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 385 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 386 | <code>        &quot;@csstools/css-parser-algorithms&quot;: &quot;^3.0.5&quot;,</code> | @csstools/css-parser-algorithms: Dependency requirement or executable metadata named @csstools/css-parser-algorithms. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 387 | <code>        &quot;@csstools/css-tokenizer&quot;: &quot;^3.0.4&quot;</code> | @csstools/css-tokenizer: Dependency requirement or executable metadata named @csstools/css-tokenizer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 388 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 389 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 390 | <code>    &quot;node_modules/@csstools/css-color-parser&quot;: {</code> | node_modules/@csstools/css-color-parser: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 391 | <code>      &quot;version&quot;: &quot;3.1.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 392 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@csstools/css-color-parser/-/css-color-parser-3.1.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 393 | <code>      &quot;integrity&quot;: &quot;sha512-nbtKwh3a6xNVIp/VRuXV64yTKnb1IjTAEEh3irzS+HkKjAOYLTGNb9pmVNntZ8iVBHcWDA2Dof0QtPgFI1BaTA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 394 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 395 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 396 | <code>        {</code> | Open a JSON object (named fields). |
| 397 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 398 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 399 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 400 | <code>        {</code> | Open a JSON object (named fields). |
| 401 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 402 | <code>          &quot;url&quot;: &quot;https://opencollective.com/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 403 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 404 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 405 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 406 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 407 | <code>        &quot;@csstools/color-helpers&quot;: &quot;^5.1.0&quot;,</code> | @csstools/color-helpers: Dependency requirement or executable metadata named @csstools/color-helpers. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 408 | <code>        &quot;@csstools/css-calc&quot;: &quot;^2.1.4&quot;</code> | @csstools/css-calc: Dependency requirement or executable metadata named @csstools/css-calc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 409 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 410 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 411 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 412 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 413 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 414 | <code>        &quot;@csstools/css-parser-algorithms&quot;: &quot;^3.0.5&quot;,</code> | @csstools/css-parser-algorithms: Dependency requirement or executable metadata named @csstools/css-parser-algorithms. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 415 | <code>        &quot;@csstools/css-tokenizer&quot;: &quot;^3.0.4&quot;</code> | @csstools/css-tokenizer: Dependency requirement or executable metadata named @csstools/css-tokenizer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 416 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 417 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 418 | <code>    &quot;node_modules/@csstools/css-parser-algorithms&quot;: {</code> | node_modules/@csstools/css-parser-algorithms: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 419 | <code>      &quot;version&quot;: &quot;3.0.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 420 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@csstools/css-parser-algorithms/-/css-parser-algorithms-3.0.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 421 | <code>      &quot;integrity&quot;: &quot;sha512-DaDeUkXZKjdGhgYaHNJTV9pV7Y9B3b644jCLs9Upc3VeNGg6LWARAT6O+Q+/COo+2gg/bM5rhpMAtf70WqfBdQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 422 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 423 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 424 | <code>        {</code> | Open a JSON object (named fields). |
| 425 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 426 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 427 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 428 | <code>        {</code> | Open a JSON object (named fields). |
| 429 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 430 | <code>          &quot;url&quot;: &quot;https://opencollective.com/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 431 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 432 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 433 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 434 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 435 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 436 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 437 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 438 | <code>        &quot;@csstools/css-tokenizer&quot;: &quot;^3.0.4&quot;</code> | @csstools/css-tokenizer: Dependency requirement or executable metadata named @csstools/css-tokenizer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 439 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 440 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 441 | <code>    &quot;node_modules/@csstools/css-tokenizer&quot;: {</code> | node_modules/@csstools/css-tokenizer: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 442 | <code>      &quot;version&quot;: &quot;3.0.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 443 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@csstools/css-tokenizer/-/css-tokenizer-3.0.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 444 | <code>      &quot;integrity&quot;: &quot;sha512-Vd/9EVDiu6PPJt9yAh6roZP6El1xHrdvIVGjyBsHR0RYwNHgL7FJPyIIW4fANJNG6FtyZfvlRPpFI4ZM/lubvw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 445 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 446 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 447 | <code>        {</code> | Open a JSON object (named fields). |
| 448 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 449 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 450 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 451 | <code>        {</code> | Open a JSON object (named fields). |
| 452 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 453 | <code>          &quot;url&quot;: &quot;https://opencollective.com/csstools&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 454 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 455 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 456 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 457 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 458 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 459 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 460 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 461 | <code>    &quot;node_modules/@esbuild/aix-ppc64&quot;: {</code> | node_modules/@esbuild/aix-ppc64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 462 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 463 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/aix-ppc64/-/aix-ppc64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 464 | <code>      &quot;integrity&quot;: &quot;sha512-Hhmwd6CInZ3dwpuGTF8fJG6yoWmsToE+vYgD4nytZVxcu1ulHpUQRAB1UJ8+N1Am3Mz4+xOByoQoSZf4D+CpkA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 465 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 466 | <code>        &quot;ppc64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/aix-ppc64): "ppc64". This is metadata, not a code statement. |
| 467 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 468 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 469 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 470 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 471 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 472 | <code>        &quot;aix&quot;</code> | Array item for the current artifact (node_modules/@esbuild/aix-ppc64): "aix". This is metadata, not a code statement. |
| 473 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 474 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 475 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 476 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 477 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 478 | <code>    &quot;node_modules/@esbuild/android-arm&quot;: {</code> | node_modules/@esbuild/android-arm: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 479 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 480 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/android-arm/-/android-arm-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 481 | <code>      &quot;integrity&quot;: &quot;sha512-VJ+sKvNA/GE7Ccacc9Cha7bpS8nyzVv0jdVgwNDaR4gDMC/2TTRc33Ip8qrNYUcpkOHUT5OZ0bUcNNVZQ9RLlg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 482 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 483 | <code>        &quot;arm&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-arm): "arm". This is metadata, not a code statement. |
| 484 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 485 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 486 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 487 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 488 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 489 | <code>        &quot;android&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-arm): "android". This is metadata, not a code statement. |
| 490 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 491 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 492 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 493 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 494 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 495 | <code>    &quot;node_modules/@esbuild/android-arm64&quot;: {</code> | node_modules/@esbuild/android-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 496 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 497 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/android-arm64/-/android-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 498 | <code>      &quot;integrity&quot;: &quot;sha512-6AAmLG7zwD1Z159jCKPvAxZd4y/VTO0VkprYy+3N2FtJ8+BQWFXU+OxARIwA46c5tdD9SsKGZ/1ocqBS/gAKHg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 499 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 500 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-arm64): "arm64". This is metadata, not a code statement. |
| 501 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 502 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 503 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 504 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 505 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 506 | <code>        &quot;android&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-arm64): "android". This is metadata, not a code statement. |
| 507 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 508 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 509 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 510 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 511 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 512 | <code>    &quot;node_modules/@esbuild/android-x64&quot;: {</code> | node_modules/@esbuild/android-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 513 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 514 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/android-x64/-/android-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 515 | <code>      &quot;integrity&quot;: &quot;sha512-5jbb+2hhDHx5phYR2By8GTWEzn6I9UqR11Kwf22iKbNpYrsmRB18aX/9ivc5cabcUiAT/wM+YIZ6SG9QO6a8kg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 516 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 517 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-x64): "x64". This is metadata, not a code statement. |
| 518 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 519 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 520 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 521 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 522 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 523 | <code>        &quot;android&quot;</code> | Array item for the current artifact (node_modules/@esbuild/android-x64): "android". This is metadata, not a code statement. |
| 524 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 525 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 526 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 527 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 528 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 529 | <code>    &quot;node_modules/@esbuild/darwin-arm64&quot;: {</code> | node_modules/@esbuild/darwin-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 530 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 531 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/darwin-arm64/-/darwin-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 532 | <code>      &quot;integrity&quot;: &quot;sha512-N3zl+lxHCifgIlcMUP5016ESkeQjLj/959RxxNYIthIg+CQHInujFuXeWbWMgnTo4cp5XVHqFPmpyu9J65C1Yg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 533 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 534 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/darwin-arm64): "arm64". This is metadata, not a code statement. |
| 535 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 536 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 537 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 538 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 539 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 540 | <code>        &quot;darwin&quot;</code> | Array item for the current artifact (node_modules/@esbuild/darwin-arm64): "darwin". This is metadata, not a code statement. |
| 541 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 542 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 543 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 544 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 545 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 546 | <code>    &quot;node_modules/@esbuild/darwin-x64&quot;: {</code> | node_modules/@esbuild/darwin-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 547 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 548 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/darwin-x64/-/darwin-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 549 | <code>      &quot;integrity&quot;: &quot;sha512-HQ9ka4Kx21qHXwtlTUVbKJOAnmG1ipXhdWTmNXiPzPfWKpXqASVcWdnf2bnL73wgjNrFXAa3yYvBSd9pzfEIpA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 550 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 551 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/darwin-x64): "x64". This is metadata, not a code statement. |
| 552 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 553 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 554 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 555 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 556 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 557 | <code>        &quot;darwin&quot;</code> | Array item for the current artifact (node_modules/@esbuild/darwin-x64): "darwin". This is metadata, not a code statement. |
| 558 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 559 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 560 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 561 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 562 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 563 | <code>    &quot;node_modules/@esbuild/freebsd-arm64&quot;: {</code> | node_modules/@esbuild/freebsd-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 564 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 565 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/freebsd-arm64/-/freebsd-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 566 | <code>      &quot;integrity&quot;: &quot;sha512-gA0Bx759+7Jve03K1S0vkOu5Lg/85dou3EseOGUes8flVOGxbhDDh/iZaoek11Y8mtyKPGF3vP8XhnkDEAmzeg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 567 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 568 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/freebsd-arm64): "arm64". This is metadata, not a code statement. |
| 569 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 570 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 571 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 572 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 573 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 574 | <code>        &quot;freebsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/freebsd-arm64): "freebsd". This is metadata, not a code statement. |
| 575 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 576 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 577 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 578 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 579 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 580 | <code>    &quot;node_modules/@esbuild/freebsd-x64&quot;: {</code> | node_modules/@esbuild/freebsd-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 581 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 582 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/freebsd-x64/-/freebsd-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 583 | <code>      &quot;integrity&quot;: &quot;sha512-TGbO26Yw2xsHzxtbVFGEXBFH0FRAP7gtcPE7P5yP7wGy7cXK2oO7RyOhL5NLiqTlBh47XhmIUXuGciXEqYFfBQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 584 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 585 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/freebsd-x64): "x64". This is metadata, not a code statement. |
| 586 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 587 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 588 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 589 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 590 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 591 | <code>        &quot;freebsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/freebsd-x64): "freebsd". This is metadata, not a code statement. |
| 592 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 593 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 594 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 595 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 596 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 597 | <code>    &quot;node_modules/@esbuild/linux-arm&quot;: {</code> | node_modules/@esbuild/linux-arm: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 598 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 599 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-arm/-/linux-arm-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 600 | <code>      &quot;integrity&quot;: &quot;sha512-lPDGyC1JPDou8kGcywY0YILzWlhhnRjdof3UlcoqYmS9El818LLfJJc3PXXgZHrHCAKs/Z2SeZtDJr5MrkxtOw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 601 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 602 | <code>        &quot;arm&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-arm): "arm". This is metadata, not a code statement. |
| 603 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 604 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 605 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 606 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 607 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 608 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-arm): "linux". This is metadata, not a code statement. |
| 609 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 610 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 611 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 612 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 613 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 614 | <code>    &quot;node_modules/@esbuild/linux-arm64&quot;: {</code> | node_modules/@esbuild/linux-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 615 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 616 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-arm64/-/linux-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 617 | <code>      &quot;integrity&quot;: &quot;sha512-8bwX7a8FghIgrupcxb4aUmYDLp8pX06rGh5HqDT7bB+8Rdells6mHvrFHHW2JAOPZUbnjUpKTLg6ECyzvas2AQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 618 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 619 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-arm64): "arm64". This is metadata, not a code statement. |
| 620 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 621 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 622 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 623 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 624 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 625 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-arm64): "linux". This is metadata, not a code statement. |
| 626 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 627 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 628 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 629 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 630 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 631 | <code>    &quot;node_modules/@esbuild/linux-ia32&quot;: {</code> | node_modules/@esbuild/linux-ia32: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 632 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 633 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-ia32/-/linux-ia32-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 634 | <code>      &quot;integrity&quot;: &quot;sha512-0y9KrdVnbMM2/vG8KfU0byhUN+EFCny9+8g202gYqSSVMonbsCfLjUO+rCci7pM0WBEtz+oK/PIwHkzxkyharA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 635 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 636 | <code>        &quot;ia32&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-ia32): "ia32". This is metadata, not a code statement. |
| 637 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 638 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 639 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 640 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 641 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 642 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-ia32): "linux". This is metadata, not a code statement. |
| 643 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 644 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 645 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 646 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 647 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 648 | <code>    &quot;node_modules/@esbuild/linux-loong64&quot;: {</code> | node_modules/@esbuild/linux-loong64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 649 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 650 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-loong64/-/linux-loong64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 651 | <code>      &quot;integrity&quot;: &quot;sha512-h///Lr5a9rib/v1GGqXVGzjL4TMvVTv+s1DPoxQdz7l/AYv6LDSxdIwzxkrPW438oUXiDtwM10o9PmwS/6Z0Ng==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 652 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 653 | <code>        &quot;loong64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-loong64): "loong64". This is metadata, not a code statement. |
| 654 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 655 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 656 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 657 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 658 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 659 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-loong64): "linux". This is metadata, not a code statement. |
| 660 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 661 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 662 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 663 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 664 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 665 | <code>    &quot;node_modules/@esbuild/linux-mips64el&quot;: {</code> | node_modules/@esbuild/linux-mips64el: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 666 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 667 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-mips64el/-/linux-mips64el-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 668 | <code>      &quot;integrity&quot;: &quot;sha512-iyRrM1Pzy9GFMDLsXn1iHUm18nhKnNMWscjmp4+hpafcZjrr2WbT//d20xaGljXDBYHqRcl8HnxbX6uaA/eGVw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 669 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 670 | <code>        &quot;mips64el&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-mips64el): "mips64el". This is metadata, not a code statement. |
| 671 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 672 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 673 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 674 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 675 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 676 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-mips64el): "linux". This is metadata, not a code statement. |
| 677 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 678 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 679 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 680 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 681 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 682 | <code>    &quot;node_modules/@esbuild/linux-ppc64&quot;: {</code> | node_modules/@esbuild/linux-ppc64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 683 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 684 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-ppc64/-/linux-ppc64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 685 | <code>      &quot;integrity&quot;: &quot;sha512-9meM/lRXxMi5PSUqEXRCtVjEZBGwB7P/D4yT8UG/mwIdze2aV4Vo6U5gD3+RsoHXKkHCfSxZKzmDssVlRj1QQA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 686 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 687 | <code>        &quot;ppc64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-ppc64): "ppc64". This is metadata, not a code statement. |
| 688 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 689 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 690 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 691 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 692 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 693 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-ppc64): "linux". This is metadata, not a code statement. |
| 694 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 695 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 696 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 697 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 698 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 699 | <code>    &quot;node_modules/@esbuild/linux-riscv64&quot;: {</code> | node_modules/@esbuild/linux-riscv64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 700 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 701 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-riscv64/-/linux-riscv64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 702 | <code>      &quot;integrity&quot;: &quot;sha512-Zr7KR4hgKUpWAwb1f3o5ygT04MzqVrGEGXGLnj15YQDJErYu/BGg+wmFlIDOdJp0PmB0lLvxFIOXZgFRrdjR0w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 703 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 704 | <code>        &quot;riscv64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-riscv64): "riscv64". This is metadata, not a code statement. |
| 705 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 706 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 707 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 708 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 709 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 710 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-riscv64): "linux". This is metadata, not a code statement. |
| 711 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 712 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 713 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 714 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 715 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 716 | <code>    &quot;node_modules/@esbuild/linux-s390x&quot;: {</code> | node_modules/@esbuild/linux-s390x: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 717 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 718 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-s390x/-/linux-s390x-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 719 | <code>      &quot;integrity&quot;: &quot;sha512-MsKncOcgTNvdtiISc/jZs/Zf8d0cl/t3gYWX8J9ubBnVOwlk65UIEEvgBORTiljloIWnBzLs4qhzPkJcitIzIg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 720 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 721 | <code>        &quot;s390x&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-s390x): "s390x". This is metadata, not a code statement. |
| 722 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 723 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 724 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 725 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 726 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 727 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-s390x): "linux". This is metadata, not a code statement. |
| 728 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 729 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 730 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 731 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 732 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 733 | <code>    &quot;node_modules/@esbuild/linux-x64&quot;: {</code> | node_modules/@esbuild/linux-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 734 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 735 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 736 | <code>      &quot;integrity&quot;: &quot;sha512-uqZMTLr/zR/ed4jIGnwSLkaHmPjOjJvnm6TVVitAa08SLS9Z0VM8wIRx7gWbJB5/J54YuIMInDquWyYvQLZkgw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 737 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 738 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-x64): "x64". This is metadata, not a code statement. |
| 739 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 740 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 741 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 742 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 743 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 744 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@esbuild/linux-x64): "linux". This is metadata, not a code statement. |
| 745 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 746 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 747 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 748 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 749 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 750 | <code>    &quot;node_modules/@esbuild/netbsd-arm64&quot;: {</code> | node_modules/@esbuild/netbsd-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 751 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 752 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/netbsd-arm64/-/netbsd-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 753 | <code>      &quot;integrity&quot;: &quot;sha512-xXwcTq4GhRM7J9A8Gv5boanHhRa/Q9KLVmcyXHCTaM4wKfIpWkdXiMog/KsnxzJ0A1+nD+zoecuzqPmCRyBGjg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 754 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 755 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/netbsd-arm64): "arm64". This is metadata, not a code statement. |
| 756 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 757 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 758 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 759 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 760 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 761 | <code>        &quot;netbsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/netbsd-arm64): "netbsd". This is metadata, not a code statement. |
| 762 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 763 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 764 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 765 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 766 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 767 | <code>    &quot;node_modules/@esbuild/netbsd-x64&quot;: {</code> | node_modules/@esbuild/netbsd-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 768 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 769 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/netbsd-x64/-/netbsd-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 770 | <code>      &quot;integrity&quot;: &quot;sha512-Ld5pTlzPy3YwGec4OuHh1aCVCRvOXdH8DgRjfDy/oumVovmuSzWfnSJg+VtakB9Cm0gxNO9BzWkj6mtO1FMXkQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 771 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 772 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/netbsd-x64): "x64". This is metadata, not a code statement. |
| 773 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 774 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 775 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 776 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 777 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 778 | <code>        &quot;netbsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/netbsd-x64): "netbsd". This is metadata, not a code statement. |
| 779 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 780 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 781 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 782 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 783 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 784 | <code>    &quot;node_modules/@esbuild/openbsd-arm64&quot;: {</code> | node_modules/@esbuild/openbsd-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 785 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 786 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/openbsd-arm64/-/openbsd-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 787 | <code>      &quot;integrity&quot;: &quot;sha512-fF96T6KsBo/pkQI950FARU9apGNTSlZGsv1jZBAlcLL1MLjLNIWPBkj5NlSz8aAzYKg+eNqknrUJ24QBybeR5A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 788 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 789 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openbsd-arm64): "arm64". This is metadata, not a code statement. |
| 790 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 791 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 792 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 793 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 794 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 795 | <code>        &quot;openbsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openbsd-arm64): "openbsd". This is metadata, not a code statement. |
| 796 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 797 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 798 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 799 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 800 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 801 | <code>    &quot;node_modules/@esbuild/openbsd-x64&quot;: {</code> | node_modules/@esbuild/openbsd-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 802 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 803 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/openbsd-x64/-/openbsd-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 804 | <code>      &quot;integrity&quot;: &quot;sha512-MZyXUkZHjQxUvzK7rN8DJ3SRmrVrke8ZyRusHlP+kuwqTcfWLyqMOE3sScPPyeIXN/mDJIfGXvcMqCgYKekoQw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 805 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 806 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openbsd-x64): "x64". This is metadata, not a code statement. |
| 807 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 808 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 809 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 810 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 811 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 812 | <code>        &quot;openbsd&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openbsd-x64): "openbsd". This is metadata, not a code statement. |
| 813 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 814 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 815 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 816 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 817 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 818 | <code>    &quot;node_modules/@esbuild/openharmony-arm64&quot;: {</code> | node_modules/@esbuild/openharmony-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 819 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 820 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/openharmony-arm64/-/openharmony-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 821 | <code>      &quot;integrity&quot;: &quot;sha512-rm0YWsqUSRrjncSXGA7Zv78Nbnw4XL6/dzr20cyrQf7ZmRcsovpcRBdhD43Nuk3y7XIoW2OxMVvwuRvk9XdASg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 822 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 823 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openharmony-arm64): "arm64". This is metadata, not a code statement. |
| 824 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 825 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 826 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 827 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 828 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 829 | <code>        &quot;openharmony&quot;</code> | Array item for the current artifact (node_modules/@esbuild/openharmony-arm64): "openharmony". This is metadata, not a code statement. |
| 830 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 831 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 832 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 833 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 834 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 835 | <code>    &quot;node_modules/@esbuild/sunos-x64&quot;: {</code> | node_modules/@esbuild/sunos-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 836 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 837 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/sunos-x64/-/sunos-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 838 | <code>      &quot;integrity&quot;: &quot;sha512-3wGSCDyuTHQUzt0nV7bocDy72r2lI33QL3gkDNGkod22EsYl04sMf0qLb8luNKTOmgF/eDEDP5BFNwoBKH441w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 839 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 840 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/sunos-x64): "x64". This is metadata, not a code statement. |
| 841 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 842 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 843 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 844 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 845 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 846 | <code>        &quot;sunos&quot;</code> | Array item for the current artifact (node_modules/@esbuild/sunos-x64): "sunos". This is metadata, not a code statement. |
| 847 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 848 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 849 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 850 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 851 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 852 | <code>    &quot;node_modules/@esbuild/win32-arm64&quot;: {</code> | node_modules/@esbuild/win32-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 853 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 854 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/win32-arm64/-/win32-arm64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 855 | <code>      &quot;integrity&quot;: &quot;sha512-rMmLrur64A7+DKlnSuwqUdRKyd3UE7oPJZmnljqEptesKM8wx9J8gx5u0+9Pq0fQQW8vqeKebwNXdfOyP+8Bsg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 856 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 857 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-arm64): "arm64". This is metadata, not a code statement. |
| 858 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 859 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 860 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 861 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 862 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 863 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-arm64): "win32". This is metadata, not a code statement. |
| 864 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 865 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 866 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 867 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 868 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 869 | <code>    &quot;node_modules/@esbuild/win32-ia32&quot;: {</code> | node_modules/@esbuild/win32-ia32: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 870 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 871 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/win32-ia32/-/win32-ia32-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 872 | <code>      &quot;integrity&quot;: &quot;sha512-HkqnmmBoCbCwxUKKNPBixiWDGCpQGVsrQfJoVGYLPT41XWF8lHuE5N6WhVia2n4o5QK5M4tYr21827fNhi4byQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 873 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 874 | <code>        &quot;ia32&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-ia32): "ia32". This is metadata, not a code statement. |
| 875 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 876 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 877 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 878 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 879 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 880 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-ia32): "win32". This is metadata, not a code statement. |
| 881 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 882 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 883 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 884 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 885 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 886 | <code>    &quot;node_modules/@esbuild/win32-x64&quot;: {</code> | node_modules/@esbuild/win32-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 887 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 888 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@esbuild/win32-x64/-/win32-x64-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 889 | <code>      &quot;integrity&quot;: &quot;sha512-alJC0uCZpTFrSL0CCDjcgleBXPnCrEAhTBILpeAp7M/OFgoqtAetfBzX0xM00MUsVVPpVjlPuMbREqnZCXaTnA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 890 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 891 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-x64): "x64". This is metadata, not a code statement. |
| 892 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 893 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 894 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 895 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 896 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 897 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@esbuild/win32-x64): "win32". This is metadata, not a code statement. |
| 898 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 899 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 900 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 901 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 902 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 903 | <code>    &quot;node_modules/@jridgewell/gen-mapping&quot;: {</code> | node_modules/@jridgewell/gen-mapping: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 904 | <code>      &quot;version&quot;: &quot;0.3.13&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 905 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.13.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 906 | <code>      &quot;integrity&quot;: &quot;sha512-2kkt/7niJ6MgEPxF0bYdQ6etZaA+fQvDcLKckhy1yIQOzaoKjBBjSj63/aLVjYE3qhRt5dvM+uUyfCg6UKCBbA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 907 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 908 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 909 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 910 | <code>        &quot;@jridgewell/sourcemap-codec&quot;: &quot;^1.5.0&quot;,</code> | @jridgewell/sourcemap-codec: Dependency requirement or executable metadata named @jridgewell/sourcemap-codec. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 911 | <code>        &quot;@jridgewell/trace-mapping&quot;: &quot;^0.3.24&quot;</code> | @jridgewell/trace-mapping: Dependency requirement or executable metadata named @jridgewell/trace-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 912 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 913 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 914 | <code>    &quot;node_modules/@jridgewell/remapping&quot;: {</code> | node_modules/@jridgewell/remapping: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 915 | <code>      &quot;version&quot;: &quot;2.3.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 916 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@jridgewell/remapping/-/remapping-2.3.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 917 | <code>      &quot;integrity&quot;: &quot;sha512-LI9u/+laYG4Ds1TDKSJW2YPrIlcVYOwi2fUC6xB43lueCjgxV4lffOCZCtYFiH6TNOX+tQKXx97T4IKHbhyHEQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 918 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 919 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 920 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 921 | <code>        &quot;@jridgewell/gen-mapping&quot;: &quot;^0.3.5&quot;,</code> | @jridgewell/gen-mapping: Dependency requirement or executable metadata named @jridgewell/gen-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 922 | <code>        &quot;@jridgewell/trace-mapping&quot;: &quot;^0.3.24&quot;</code> | @jridgewell/trace-mapping: Dependency requirement or executable metadata named @jridgewell/trace-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 923 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 924 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 925 | <code>    &quot;node_modules/@jridgewell/resolve-uri&quot;: {</code> | node_modules/@jridgewell/resolve-uri: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 926 | <code>      &quot;version&quot;: &quot;3.1.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 927 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 928 | <code>      &quot;integrity&quot;: &quot;sha512-bRISgCIjP20/tbWSPWMEi54QVPRZExkuD9lJL+UIxUKtwVJA8wW1Trb1jMs1RFXo1CBTNZ/5hpC9QvmKWdopKw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 929 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 930 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 931 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 932 | <code>        &quot;node&quot;: &quot;&gt;=6.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 933 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 934 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 935 | <code>    &quot;node_modules/@jridgewell/sourcemap-codec&quot;: {</code> | node_modules/@jridgewell/sourcemap-codec: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 936 | <code>      &quot;version&quot;: &quot;1.6.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 937 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.6.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 938 | <code>      &quot;integrity&quot;: &quot;sha512-T7jf+5zgsZHwNJ4lvQ7/aezbyk0nNX+zJVWpmHA7VYsEx7a7qr5Rg5IbtJFqkgze5Y2sruq1RUY8Q837Od7iFw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 939 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 940 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 941 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 942 | <code>    &quot;node_modules/@jridgewell/trace-mapping&quot;: {</code> | node_modules/@jridgewell/trace-mapping: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 943 | <code>      &quot;version&quot;: &quot;0.3.31&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 944 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.31.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 945 | <code>      &quot;integrity&quot;: &quot;sha512-zzNR+SdQSDJzc8joaeP8QQoCQr8NuYx2dIIytl1QeBEZHJ9uW6hebsrYgbz8hJwUQao3TWCMtmfV8Nu1twOLAw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 946 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 947 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 948 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 949 | <code>        &quot;@jridgewell/resolve-uri&quot;: &quot;^3.1.0&quot;,</code> | @jridgewell/resolve-uri: Dependency requirement or executable metadata named @jridgewell/resolve-uri. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 950 | <code>        &quot;@jridgewell/sourcemap-codec&quot;: &quot;^1.4.14&quot;</code> | @jridgewell/sourcemap-codec: Dependency requirement or executable metadata named @jridgewell/sourcemap-codec. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 951 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 952 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 953 | <code>    &quot;node_modules/@napi-rs/lzma-linux-x64-gnu&quot;: {</code> | node_modules/@napi-rs/lzma-linux-x64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 954 | <code>      &quot;version&quot;: &quot;1.5.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 955 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@napi-rs/lzma-linux-x64-gnu/-/lzma-linux-x64-gnu-1.5.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 956 | <code>      &quot;integrity&quot;: &quot;sha512-oTXEIha4SsuXdTA4Iyskj0kpdx2yVXdhd75c2v3xGrHFfVMsbhTPZU/nMPL4sWKo4pBHm3aucLaqGlF696dTyQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 957 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 958 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@napi-rs/lzma-linux-x64-gnu): "x64". This is metadata, not a code statement. |
| 959 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 960 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 961 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 962 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@napi-rs/lzma-linux-x64-gnu): "glibc". This is metadata, not a code statement. |
| 963 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 964 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 965 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 966 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 967 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@napi-rs/lzma-linux-x64-gnu): "linux". This is metadata, not a code statement. |
| 968 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 969 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 970 | <code>        &quot;node&quot;: &quot;^22.20 &#124;&#124; ^24.12 &#124;&#124; &gt;=25&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 971 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 972 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 973 | <code>    &quot;node_modules/@rolldown/pluginutils&quot;: {</code> | node_modules/@rolldown/pluginutils: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 974 | <code>      &quot;version&quot;: &quot;1.0.0-beta.27&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 975 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rolldown/pluginutils/-/pluginutils-1.0.0-beta.27.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 976 | <code>      &quot;integrity&quot;: &quot;sha512-+d0F4MKMCbeVUJwG96uQ4SgAznZNSq93I3V+9NHA4OpvqG8mRCpGdKmK8l/dl02h2CCDHwW2FqilnTyDcAnqjA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 977 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 978 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 979 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 980 | <code>    &quot;node_modules/@rollup/rollup-android-arm-eabi&quot;: {</code> | node_modules/@rollup/rollup-android-arm-eabi: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 981 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 982 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-android-arm-eabi/-/rollup-android-arm-eabi-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 983 | <code>      &quot;integrity&quot;: &quot;sha512-MrfgRQSpD5hkkRg6XI16B6EDLb+6+xp8xje6bpdSwkYw+qxrBKbUVrRAQu9h82UT+QumSIVQ8HXsXjPd2dlhqw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 984 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 985 | <code>        &quot;arm&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-android-arm-eabi): "arm". This is metadata, not a code statement. |
| 986 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 987 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 988 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 989 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 990 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 991 | <code>        &quot;android&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-android-arm-eabi): "android". This is metadata, not a code statement. |
| 992 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 993 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 994 | <code>    &quot;node_modules/@rollup/rollup-android-arm64&quot;: {</code> | node_modules/@rollup/rollup-android-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 995 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 996 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-android-arm64/-/rollup-android-arm64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 997 | <code>      &quot;integrity&quot;: &quot;sha512-+uu2p/R9Tzn8GpoQyX1pAo5dmKT1DhXevfaCzqzmPFhnLjHLWw7uWkaVGlxmhwYoRiYYhsGfRcD5cTBpL7rgSw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 998 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 999 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-android-arm64): "arm64". This is metadata, not a code statement. |
| 1000 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1001 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1002 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1003 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1004 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1005 | <code>        &quot;android&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-android-arm64): "android". This is metadata, not a code statement. |
| 1006 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1007 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1008 | <code>    &quot;node_modules/@rollup/rollup-darwin-arm64&quot;: {</code> | node_modules/@rollup/rollup-darwin-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1009 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1010 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-darwin-arm64/-/rollup-darwin-arm64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1011 | <code>      &quot;integrity&quot;: &quot;sha512-17dys+YEmzwzzFVHQAVDONg5FALXY9kd99HFEpfk4gJVHYxoh5bGea3D4t1fXXnwkTcOe25wPyd6nWS0I8IdLQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1012 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1013 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-darwin-arm64): "arm64". This is metadata, not a code statement. |
| 1014 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1015 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1016 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1017 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1018 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1019 | <code>        &quot;darwin&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-darwin-arm64): "darwin". This is metadata, not a code statement. |
| 1020 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1021 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1022 | <code>    &quot;node_modules/@rollup/rollup-darwin-x64&quot;: {</code> | node_modules/@rollup/rollup-darwin-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1023 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1024 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-darwin-x64/-/rollup-darwin-x64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1025 | <code>      &quot;integrity&quot;: &quot;sha512-wg0zQEKkEvFZf1UaaX1UELOoPs//OSKUG7D+yITuqOsAvza7LvHTv5Wu4nmMfzNG7EYI2jp2PJC7Id6OETmsYQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1026 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1027 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-darwin-x64): "x64". This is metadata, not a code statement. |
| 1028 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1029 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1030 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1031 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1032 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1033 | <code>        &quot;darwin&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-darwin-x64): "darwin". This is metadata, not a code statement. |
| 1034 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1035 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1036 | <code>    &quot;node_modules/@rollup/rollup-freebsd-arm64&quot;: {</code> | node_modules/@rollup/rollup-freebsd-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1037 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1038 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-freebsd-arm64/-/rollup-freebsd-arm64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1039 | <code>      &quot;integrity&quot;: &quot;sha512-CoJmWcpEMuwin+TZ/ev/H9uDyF/uxUKQSWXdmIPn/UBx/uGV9+4ebMp0FwnlhWR9PE1AdzYsKf3bZevhif38+A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1040 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1041 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-freebsd-arm64): "arm64". This is metadata, not a code statement. |
| 1042 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1043 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1044 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1045 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1046 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1047 | <code>        &quot;freebsd&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-freebsd-arm64): "freebsd". This is metadata, not a code statement. |
| 1048 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1049 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1050 | <code>    &quot;node_modules/@rollup/rollup-freebsd-x64&quot;: {</code> | node_modules/@rollup/rollup-freebsd-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1051 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1052 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-freebsd-x64/-/rollup-freebsd-x64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1053 | <code>      &quot;integrity&quot;: &quot;sha512-PxZnLAaTUAL5xG0W2BXLeYPKrK2b3LIASV2/e/Kf7PZvSLI1iAQIm9B9aJD+YyFIT7hc6qaMV3+OOO35R28LfA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1054 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1055 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-freebsd-x64): "x64". This is metadata, not a code statement. |
| 1056 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1057 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1058 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1059 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1060 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1061 | <code>        &quot;freebsd&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-freebsd-x64): "freebsd". This is metadata, not a code statement. |
| 1062 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1063 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1064 | <code>    &quot;node_modules/@rollup/rollup-linux-arm-gnueabihf&quot;: {</code> | node_modules/@rollup/rollup-linux-arm-gnueabihf: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1065 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1066 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-arm-gnueabihf/-/rollup-linux-arm-gnueabihf-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1067 | <code>      &quot;integrity&quot;: &quot;sha512-uPo3IvnONjhbFXwWgroBeFwOicuhT7ZwQrnzkzmOtBJzeQbkUJUE1SJDfDI31ijQ5+ZUIA6sPrdUMxTSnxUWAg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1068 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1069 | <code>        &quot;arm&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-gnueabihf): "arm". This is metadata, not a code statement. |
| 1070 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1071 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1072 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1073 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-gnueabihf): "glibc". This is metadata, not a code statement. |
| 1074 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1075 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1076 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1077 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1078 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-gnueabihf): "linux". This is metadata, not a code statement. |
| 1079 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1080 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1081 | <code>    &quot;node_modules/@rollup/rollup-linux-arm-musleabihf&quot;: {</code> | node_modules/@rollup/rollup-linux-arm-musleabihf: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1082 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1083 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-arm-musleabihf/-/rollup-linux-arm-musleabihf-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1084 | <code>      &quot;integrity&quot;: &quot;sha512-ywI8Jyuc4LyHYTjC0mw4yA1ulvZBkHusdpWnoiEBsmBuHvSnt90btTBGCZ+s/2y+YNNfVAEKy33nPo5UI9zTmg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1085 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1086 | <code>        &quot;arm&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-musleabihf): "arm". This is metadata, not a code statement. |
| 1087 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1088 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1089 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1090 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-musleabihf): "musl". This is metadata, not a code statement. |
| 1091 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1092 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1093 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1094 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1095 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm-musleabihf): "linux". This is metadata, not a code statement. |
| 1096 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1097 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1098 | <code>    &quot;node_modules/@rollup/rollup-linux-arm64-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-arm64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1099 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1100 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-arm64-gnu/-/rollup-linux-arm64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1101 | <code>      &quot;integrity&quot;: &quot;sha512-tmuXJoQ/3ovSr637aykZMdQteU/CB2APAz2CrvsbibuoHZi1BS1Db13cVViBdEARGwXCLn1DSJ8wsjoThLJPGA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1102 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1103 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-gnu): "arm64". This is metadata, not a code statement. |
| 1104 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1105 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1106 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1107 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-gnu): "glibc". This is metadata, not a code statement. |
| 1108 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1109 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1110 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1111 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1112 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-gnu): "linux". This is metadata, not a code statement. |
| 1113 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1114 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1115 | <code>    &quot;node_modules/@rollup/rollup-linux-arm64-musl&quot;: {</code> | node_modules/@rollup/rollup-linux-arm64-musl: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1116 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1117 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-arm64-musl/-/rollup-linux-arm64-musl-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1118 | <code>      &quot;integrity&quot;: &quot;sha512-5FMjSYNcUOHx7oW8Qu9KB6jGPpvF/8sG7+BDHwU/Ihh1/6FMJ9ySmsFG4tJ1qbNRuP8OLzCBDso4sF0mQaLuFQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1119 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1120 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-musl): "arm64". This is metadata, not a code statement. |
| 1121 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1122 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1123 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1124 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-musl): "musl". This is metadata, not a code statement. |
| 1125 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1126 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1127 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1128 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1129 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-arm64-musl): "linux". This is metadata, not a code statement. |
| 1130 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1131 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1132 | <code>    &quot;node_modules/@rollup/rollup-linux-loong64-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-loong64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1133 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1134 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-loong64-gnu/-/rollup-linux-loong64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1135 | <code>      &quot;integrity&quot;: &quot;sha512-K8ZJ+neLDbUkIrL8dqF/5LtuVCrKwo27kREgOlxjBEjlOXwHvDnHLU8Z/UKv/B49qi7e8hsSDOyoJwhwqhvX4w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1136 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1137 | <code>        &quot;loong64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-gnu): "loong64". This is metadata, not a code statement. |
| 1138 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1139 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1140 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1141 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-gnu): "glibc". This is metadata, not a code statement. |
| 1142 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1143 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1144 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1145 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1146 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-gnu): "linux". This is metadata, not a code statement. |
| 1147 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1148 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1149 | <code>    &quot;node_modules/@rollup/rollup-linux-loong64-musl&quot;: {</code> | node_modules/@rollup/rollup-linux-loong64-musl: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1150 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1151 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-loong64-musl/-/rollup-linux-loong64-musl-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1152 | <code>      &quot;integrity&quot;: &quot;sha512-NlVxsq7PFPv0DBKGuNWRDKixQYQCjM53zl04mxEcKMBmJbCBIUm1JdPfIWDRHyOOFzzYPmLQzfeEwh4716ayQg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1153 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1154 | <code>        &quot;loong64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-musl): "loong64". This is metadata, not a code statement. |
| 1155 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1156 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1157 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1158 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-musl): "musl". This is metadata, not a code statement. |
| 1159 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1160 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1161 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1162 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1163 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-loong64-musl): "linux". This is metadata, not a code statement. |
| 1164 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1165 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1166 | <code>    &quot;node_modules/@rollup/rollup-linux-ppc64-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-ppc64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1167 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1168 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-ppc64-gnu/-/rollup-linux-ppc64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1169 | <code>      &quot;integrity&quot;: &quot;sha512-ARhRHJYs5eCFet5azfrHD97vOkD8OzNW2RSMlvo5CcBqXaTOLfp0OHDtUQh7/K5AL5fUYoFp2fgC9KDg4vVYMQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1170 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1171 | <code>        &quot;ppc64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-gnu): "ppc64". This is metadata, not a code statement. |
| 1172 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1173 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1174 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1175 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-gnu): "glibc". This is metadata, not a code statement. |
| 1176 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1177 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1178 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1179 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1180 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-gnu): "linux". This is metadata, not a code statement. |
| 1181 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1182 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1183 | <code>    &quot;node_modules/@rollup/rollup-linux-ppc64-musl&quot;: {</code> | node_modules/@rollup/rollup-linux-ppc64-musl: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1184 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1185 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-ppc64-musl/-/rollup-linux-ppc64-musl-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1186 | <code>      &quot;integrity&quot;: &quot;sha512-atSgreM5C7jpxd9aEXN+6vJ5wTd05iYw+S3FiQpw7VsoEl8B90llbq35ARON+GOHj5QlVQEq2vOKWCHTob/BSQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1187 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1188 | <code>        &quot;ppc64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-musl): "ppc64". This is metadata, not a code statement. |
| 1189 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1190 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1191 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1192 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-musl): "musl". This is metadata, not a code statement. |
| 1193 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1194 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1195 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1196 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1197 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-ppc64-musl): "linux". This is metadata, not a code statement. |
| 1198 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1199 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1200 | <code>    &quot;node_modules/@rollup/rollup-linux-riscv64-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-riscv64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1201 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1202 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-riscv64-gnu/-/rollup-linux-riscv64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1203 | <code>      &quot;integrity&quot;: &quot;sha512-vmlmwBFGnjVWxSRoVabNkyYuscSmg52Pd0fM8jEbNT3Jmka4A6HcB84x4uAmuumznWfBVaxKOqU6jbEgomWKCA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1204 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1205 | <code>        &quot;riscv64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-gnu): "riscv64". This is metadata, not a code statement. |
| 1206 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1207 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1208 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1209 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-gnu): "glibc". This is metadata, not a code statement. |
| 1210 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1211 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1212 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1213 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1214 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-gnu): "linux". This is metadata, not a code statement. |
| 1215 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1216 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1217 | <code>    &quot;node_modules/@rollup/rollup-linux-riscv64-musl&quot;: {</code> | node_modules/@rollup/rollup-linux-riscv64-musl: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1218 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1219 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-riscv64-musl/-/rollup-linux-riscv64-musl-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1220 | <code>      &quot;integrity&quot;: &quot;sha512-hhJrP6S9WkbsbcHgUkvCBS5Cn8IdsG8XjlLZyxjnv9+NdoYfbbZE4TWJYr8apdaj1M5t5Y1id2StnEslxpNFyA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1221 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1222 | <code>        &quot;riscv64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-musl): "riscv64". This is metadata, not a code statement. |
| 1223 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1224 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1225 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1226 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-musl): "musl". This is metadata, not a code statement. |
| 1227 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1228 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1229 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1230 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1231 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-riscv64-musl): "linux". This is metadata, not a code statement. |
| 1232 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1233 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1234 | <code>    &quot;node_modules/@rollup/rollup-linux-s390x-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-s390x-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1235 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1236 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-s390x-gnu/-/rollup-linux-s390x-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1237 | <code>      &quot;integrity&quot;: &quot;sha512-NNVCyN9pGrwFmQa4bf+Cnf5aVH3g6ZpnlOg1Cs/H9swIHT9bRixijfzUqyEIWm1WtiAuR1LJ+rJH6zpBm8kgQA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1238 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1239 | <code>        &quot;s390x&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-s390x-gnu): "s390x". This is metadata, not a code statement. |
| 1240 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1241 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1242 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1243 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-s390x-gnu): "glibc". This is metadata, not a code statement. |
| 1244 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1245 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1246 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1247 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1248 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-s390x-gnu): "linux". This is metadata, not a code statement. |
| 1249 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1250 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1251 | <code>    &quot;node_modules/@rollup/rollup-linux-x64-gnu&quot;: {</code> | node_modules/@rollup/rollup-linux-x64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1252 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1253 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-x64-gnu/-/rollup-linux-x64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1254 | <code>      &quot;integrity&quot;: &quot;sha512-dR9nd6OKnvSS60Ifz/L7Mj5zzYyoqyRn2NwTuaOONKaa3xsVGXyp8YusMbvFyEOR94DxnwgcbgsFqkHd29ZSzQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1255 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1256 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-gnu): "x64". This is metadata, not a code statement. |
| 1257 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1258 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1259 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1260 | <code>        &quot;glibc&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-gnu): "glibc". This is metadata, not a code statement. |
| 1261 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1262 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1263 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1264 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1265 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-gnu): "linux". This is metadata, not a code statement. |
| 1266 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1267 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1268 | <code>    &quot;node_modules/@rollup/rollup-linux-x64-musl&quot;: {</code> | node_modules/@rollup/rollup-linux-x64-musl: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1269 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1270 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-linux-x64-musl/-/rollup-linux-x64-musl-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1271 | <code>      &quot;integrity&quot;: &quot;sha512-1tzsMjaqhsh3bAO6SJiJqh8hIr9sSPRd+i2vPPxJHod8/XYnf9TEnK0z/u3r1z1AkI347X0KbRSg9dWcxeGahw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1272 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1273 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-musl): "x64". This is metadata, not a code statement. |
| 1274 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1275 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1276 | <code>      &quot;libc&quot;: [</code> | libc: Dependency requirement or executable metadata named libc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1277 | <code>        &quot;musl&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-musl): "musl". This is metadata, not a code statement. |
| 1278 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1279 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1280 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1281 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1282 | <code>        &quot;linux&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-linux-x64-musl): "linux". This is metadata, not a code statement. |
| 1283 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1284 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1285 | <code>    &quot;node_modules/@rollup/rollup-openbsd-x64&quot;: {</code> | node_modules/@rollup/rollup-openbsd-x64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1286 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1287 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-openbsd-x64/-/rollup-openbsd-x64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1288 | <code>      &quot;integrity&quot;: &quot;sha512-01mWMQblKoXXsmk28KXtpbA96w7g/aOWUoV3AC16fdHdqkykGalqyyM+5u8M7uP5/MEMiiPv69Hv7iv/hEH/dA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1289 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1290 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-openbsd-x64): "x64". This is metadata, not a code statement. |
| 1291 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1292 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1293 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1294 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1295 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1296 | <code>        &quot;openbsd&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-openbsd-x64): "openbsd". This is metadata, not a code statement. |
| 1297 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1298 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1299 | <code>    &quot;node_modules/@rollup/rollup-openharmony-arm64&quot;: {</code> | node_modules/@rollup/rollup-openharmony-arm64: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1300 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1301 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-openharmony-arm64/-/rollup-openharmony-arm64-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1302 | <code>      &quot;integrity&quot;: &quot;sha512-trdnMPb/DNm4V/CgsaoGgr90HfQQ071wfK0KoIs4YpLvjBgVQGXhGabg2Z6nK4EcYNilrb9ZZPcsP6+zpJIdxQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1303 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1304 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-openharmony-arm64): "arm64". This is metadata, not a code statement. |
| 1305 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1306 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1307 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1308 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1309 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1310 | <code>        &quot;openharmony&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-openharmony-arm64): "openharmony". This is metadata, not a code statement. |
| 1311 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1312 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1313 | <code>    &quot;node_modules/@rollup/rollup-win32-arm64-msvc&quot;: {</code> | node_modules/@rollup/rollup-win32-arm64-msvc: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1314 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1315 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-win32-arm64-msvc/-/rollup-win32-arm64-msvc-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1316 | <code>      &quot;integrity&quot;: &quot;sha512-x2LxZlfdfsw99T6/qb9EqE/Qi84JWzibjyOJyhJsgFJy6CafaTiqIXCCnslCGrV5XWNh7fwrS3FbRENcuKnooA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1317 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1318 | <code>        &quot;arm64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-arm64-msvc): "arm64". This is metadata, not a code statement. |
| 1319 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1320 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1321 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1322 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1323 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1324 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-arm64-msvc): "win32". This is metadata, not a code statement. |
| 1325 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1326 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1327 | <code>    &quot;node_modules/@rollup/rollup-win32-ia32-msvc&quot;: {</code> | node_modules/@rollup/rollup-win32-ia32-msvc: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1328 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1329 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-win32-ia32-msvc/-/rollup-win32-ia32-msvc-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1330 | <code>      &quot;integrity&quot;: &quot;sha512-/Qd/9aDQIo0+jmItgBmPIs8195YVbDxRRApn47GyufgbutCDOh7eP5vSKKlI4QNFeaI+wKQAkSMsPnF3EuMpaA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1331 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1332 | <code>        &quot;ia32&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-ia32-msvc): "ia32". This is metadata, not a code statement. |
| 1333 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1334 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1335 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1336 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1337 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1338 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-ia32-msvc): "win32". This is metadata, not a code statement. |
| 1339 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1340 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1341 | <code>    &quot;node_modules/@rollup/rollup-win32-x64-gnu&quot;: {</code> | node_modules/@rollup/rollup-win32-x64-gnu: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1342 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1343 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-win32-x64-gnu/-/rollup-win32-x64-gnu-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1344 | <code>      &quot;integrity&quot;: &quot;sha512-ngUJ/XvOWrqbd2IMsfXfh2xXFLTP3sY7sCKvxbGvYdBZ1KmXFd3ewDZ9n3/GNzAUgzRuhLT/UvJRivbNoAQRBw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1345 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1346 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-x64-gnu): "x64". This is metadata, not a code statement. |
| 1347 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1348 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1349 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1350 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1351 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1352 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-x64-gnu): "win32". This is metadata, not a code statement. |
| 1353 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1354 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1355 | <code>    &quot;node_modules/@rollup/rollup-win32-x64-msvc&quot;: {</code> | node_modules/@rollup/rollup-win32-x64-msvc: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1356 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1357 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@rollup/rollup-win32-x64-msvc/-/rollup-win32-x64-msvc-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1358 | <code>      &quot;integrity&quot;: &quot;sha512-IhV6ew/DuzUWwHaYmlh7MrPCV3lKFUq/amTEwysi4r/mwNPAEfAMh5dYWeTSPTeMy2pFHGMEWYtPkHzfX3tG5A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1359 | <code>      &quot;cpu&quot;: [</code> | cpu: CPU architectures for which the optional binary package is applicable. |
| 1360 | <code>        &quot;x64&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-x64-msvc): "x64". This is metadata, not a code statement. |
| 1361 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1362 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1363 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1364 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 1365 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 1366 | <code>        &quot;win32&quot;</code> | Array item for the current artifact (node_modules/@rollup/rollup-win32-x64-msvc): "win32". This is metadata, not a code statement. |
| 1367 | <code>      ]</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1368 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1369 | <code>    &quot;node_modules/@testing-library/dom&quot;: {</code> | node_modules/@testing-library/dom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1370 | <code>      &quot;version&quot;: &quot;10.4.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1371 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@testing-library/dom/-/dom-10.4.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1372 | <code>      &quot;integrity&quot;: &quot;sha512-yzr2S9HyAIdhz2/6qHgbs665Q7PKVcDF05vsOlHPxG1mo36gKVesdYVeDLnXgfjJ03CrKRk08knc6+E/9m8v2Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1373 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1374 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1375 | <code>      &quot;peer&quot;: true,</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 1376 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1377 | <code>        &quot;@babel/code-frame&quot;: &quot;^7.10.4&quot;,</code> | @babel/code-frame: Dependency requirement or executable metadata named @babel/code-frame. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1378 | <code>        &quot;@babel/runtime&quot;: &quot;^7.12.5&quot;,</code> | @babel/runtime: Dependency requirement or executable metadata named @babel/runtime. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1379 | <code>        &quot;@types/aria-query&quot;: &quot;^5.0.1&quot;,</code> | @types/aria-query: Dependency requirement or executable metadata named @types/aria-query. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1380 | <code>        &quot;aria-query&quot;: &quot;5.3.0&quot;,</code> | aria-query: Dependency requirement or executable metadata named aria-query. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1381 | <code>        &quot;dom-accessibility-api&quot;: &quot;^0.5.9&quot;,</code> | dom-accessibility-api: Dependency requirement or executable metadata named dom-accessibility-api. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1382 | <code>        &quot;lz-string&quot;: &quot;^1.5.0&quot;,</code> | lz-string: Dependency requirement or executable metadata named lz-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1383 | <code>        &quot;picocolors&quot;: &quot;1.1.1&quot;,</code> | picocolors: Dependency requirement or executable metadata named picocolors. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1384 | <code>        &quot;pretty-format&quot;: &quot;^27.0.2&quot;</code> | pretty-format: Dependency requirement or executable metadata named pretty-format. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1385 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1386 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1387 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1388 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1389 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1390 | <code>    &quot;node_modules/@testing-library/jest-dom&quot;: {</code> | node_modules/@testing-library/jest-dom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1391 | <code>      &quot;version&quot;: &quot;6.9.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1392 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@testing-library/jest-dom/-/jest-dom-6.9.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1393 | <code>      &quot;integrity&quot;: &quot;sha512-zIcONa+hVtVSSep9UT3jZ5rizo2BsxgyDYU7WFD5eICBE7no3881HGeb/QkGfsJs6JTkY1aQhT7rIPC7e+0nnA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1394 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1395 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1396 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1397 | <code>        &quot;@adobe/css-tools&quot;: &quot;^4.4.0&quot;,</code> | @adobe/css-tools: Dependency requirement or executable metadata named @adobe/css-tools. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1398 | <code>        &quot;aria-query&quot;: &quot;^5.0.0&quot;,</code> | aria-query: Dependency requirement or executable metadata named aria-query. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1399 | <code>        &quot;css.escape&quot;: &quot;^1.5.1&quot;,</code> | css.escape: Dependency requirement or executable metadata named css.escape. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1400 | <code>        &quot;dom-accessibility-api&quot;: &quot;^0.6.3&quot;,</code> | dom-accessibility-api: Dependency requirement or executable metadata named dom-accessibility-api. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1401 | <code>        &quot;picocolors&quot;: &quot;^1.1.1&quot;,</code> | picocolors: Dependency requirement or executable metadata named picocolors. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1402 | <code>        &quot;redent&quot;: &quot;^3.0.0&quot;</code> | redent: Dependency requirement or executable metadata named redent. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1403 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1404 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1405 | <code>        &quot;node&quot;: &quot;&gt;=14&quot;,</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1406 | <code>        &quot;npm&quot;: &quot;&gt;=6&quot;,</code> | npm: npm version constraint inside engines. |
| 1407 | <code>        &quot;yarn&quot;: &quot;&gt;=1&quot;</code> | yarn: Dependency requirement or executable metadata named yarn. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1408 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1409 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1410 | <code>    &quot;node_modules/@testing-library/jest-dom/node_modules/dom-accessibility-api&quot;: {</code> | node_modules/@testing-library/jest-dom/node_modules/dom-accessibility-api: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1411 | <code>      &quot;version&quot;: &quot;0.6.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1412 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/dom-accessibility-api/-/dom-accessibility-api-0.6.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1413 | <code>      &quot;integrity&quot;: &quot;sha512-7ZgogeTnjuHbo+ct10G9Ffp0mif17idi0IyWNVA/wcwcm7NPOD/WEHVP3n7n3MhXqxoIYm8d6MuZohYWIZ4T3w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1414 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1415 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1416 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1417 | <code>    &quot;node_modules/@testing-library/react&quot;: {</code> | node_modules/@testing-library/react: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1418 | <code>      &quot;version&quot;: &quot;16.3.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1419 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@testing-library/react/-/react-16.3.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1420 | <code>      &quot;integrity&quot;: &quot;sha512-Uo193NgQbPMz6lrrhtRQQFcMC6Re/ELLFbbuVL30WDlZxlpZf9/lMHTAVxPRLw1q1iu9OJmR1c2BLiENRstdBg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1421 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1422 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1423 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1424 | <code>        &quot;@babel/runtime&quot;: &quot;^7.12.5&quot;</code> | @babel/runtime: Dependency requirement or executable metadata named @babel/runtime. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1425 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1426 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1427 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1428 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1429 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 1430 | <code>        &quot;@testing-library/dom&quot;: &quot;^10.0.0&quot;,</code> | @testing-library/dom: Dependency requirement or executable metadata named @testing-library/dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1431 | <code>        &quot;@types/react&quot;: &quot;^18.0.0 &#124;&#124; ^19.0.0&quot;,</code> | @types/react: Dependency requirement or executable metadata named @types/react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1432 | <code>        &quot;@types/react-dom&quot;: &quot;^18.0.0 &#124;&#124; ^19.0.0&quot;,</code> | @types/react-dom: Dependency requirement or executable metadata named @types/react-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1433 | <code>        &quot;react&quot;: &quot;^18.0.0 &#124;&#124; ^19.0.0&quot;,</code> | react: Dependency requirement or executable metadata named react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1434 | <code>        &quot;react-dom&quot;: &quot;^18.0.0 &#124;&#124; ^19.0.0&quot;</code> | react-dom: Dependency requirement or executable metadata named react-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1435 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1436 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 1437 | <code>        &quot;@types/react&quot;: {</code> | @types/react: Dependency requirement or executable metadata named @types/react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1438 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 1439 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1440 | <code>        &quot;@types/react-dom&quot;: {</code> | @types/react-dom: Dependency requirement or executable metadata named @types/react-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1441 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 1442 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1443 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1444 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1445 | <code>    &quot;node_modules/@types/aria-query&quot;: {</code> | node_modules/@types/aria-query: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1446 | <code>      &quot;version&quot;: &quot;5.0.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1447 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/aria-query/-/aria-query-5.0.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1448 | <code>      &quot;integrity&quot;: &quot;sha512-rfT93uj5s0PRL7EzccGMs3brplhcrghnDoV26NqKhCAS1hVo+WdNsPvE/yb6ilfr5hi2MEk6d5EWJTKdxg8jVw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1449 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1450 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1451 | <code>      &quot;peer&quot;: true</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 1452 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1453 | <code>    &quot;node_modules/@types/babel__core&quot;: {</code> | node_modules/@types/babel__core: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1454 | <code>      &quot;version&quot;: &quot;7.20.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1455 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/babel__core/-/babel__core-7.20.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1456 | <code>      &quot;integrity&quot;: &quot;sha512-qoQprZvz5wQFJwMDqeseRXWv3rqMvhgpbXFfVyWhbx9X47POIA6i/+dXefEmZKoAgOaTdaIgNSMqMIU61yRyzA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1457 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1458 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1459 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1460 | <code>        &quot;@babel/parser&quot;: &quot;^7.20.7&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1461 | <code>        &quot;@babel/types&quot;: &quot;^7.20.7&quot;,</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1462 | <code>        &quot;@types/babel__generator&quot;: &quot;*&quot;,</code> | @types/babel__generator: Dependency requirement or executable metadata named @types/babel__generator. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1463 | <code>        &quot;@types/babel__template&quot;: &quot;*&quot;,</code> | @types/babel__template: Dependency requirement or executable metadata named @types/babel__template. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1464 | <code>        &quot;@types/babel__traverse&quot;: &quot;*&quot;</code> | @types/babel__traverse: Dependency requirement or executable metadata named @types/babel__traverse. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1465 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1466 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1467 | <code>    &quot;node_modules/@types/babel__generator&quot;: {</code> | node_modules/@types/babel__generator: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1468 | <code>      &quot;version&quot;: &quot;7.27.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1469 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/babel__generator/-/babel__generator-7.27.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1470 | <code>      &quot;integrity&quot;: &quot;sha512-ufFd2Xi92OAVPYsy+P4n7/U7e68fex0+Ee8gSG9KX7eo084CWiQ4sdxktvdl0bOPupXtVJPY19zk6EwWqUQ8lg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1471 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1472 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1473 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1474 | <code>        &quot;@babel/types&quot;: &quot;^7.0.0&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1475 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1476 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1477 | <code>    &quot;node_modules/@types/babel__template&quot;: {</code> | node_modules/@types/babel__template: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1478 | <code>      &quot;version&quot;: &quot;7.4.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1479 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/babel__template/-/babel__template-7.4.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1480 | <code>      &quot;integrity&quot;: &quot;sha512-h/NUaSyG5EyxBIp8YRxo4RMe2/qQgvyowRwVMzhYhBCONbW8PUsg4lkFMrhgZhUe5z3L3MiLDuvyJ/CaPa2A8A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1481 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1482 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1483 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1484 | <code>        &quot;@babel/parser&quot;: &quot;^7.1.0&quot;,</code> | @babel/parser: Dependency requirement or executable metadata named @babel/parser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1485 | <code>        &quot;@babel/types&quot;: &quot;^7.0.0&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1486 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1487 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1488 | <code>    &quot;node_modules/@types/babel__traverse&quot;: {</code> | node_modules/@types/babel__traverse: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1489 | <code>      &quot;version&quot;: &quot;7.28.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1490 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/babel__traverse/-/babel__traverse-7.28.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1491 | <code>      &quot;integrity&quot;: &quot;sha512-8PvcXf70gTDZBgt9ptxJ8elBeBjcLOAcOtoO/mPJjtji1+CdGbHgm77om1GrsPxsiE+uXIpNSK64UYaIwQXd4Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1492 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1493 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1494 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1495 | <code>        &quot;@babel/types&quot;: &quot;^7.28.2&quot;</code> | @babel/types: Dependency requirement or executable metadata named @babel/types. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1496 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1497 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1498 | <code>    &quot;node_modules/@types/chai&quot;: {</code> | node_modules/@types/chai: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1499 | <code>      &quot;version&quot;: &quot;5.2.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1500 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/chai/-/chai-5.2.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1501 | <code>      &quot;integrity&quot;: &quot;sha512-Mw558oeA9fFbv65/y4mHtXDs9bPnFMZAL/jxdPFUpOHHIXX91mcgEHbS5Lahr+pwZFR8A7GQleRWeI6cGFC2UA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1502 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1503 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1504 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1505 | <code>        &quot;@types/deep-eql&quot;: &quot;*&quot;,</code> | @types/deep-eql: Dependency requirement or executable metadata named @types/deep-eql. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1506 | <code>        &quot;assertion-error&quot;: &quot;^2.0.1&quot;</code> | assertion-error: Dependency requirement or executable metadata named assertion-error. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1507 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1508 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1509 | <code>    &quot;node_modules/@types/deep-eql&quot;: {</code> | node_modules/@types/deep-eql: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1510 | <code>      &quot;version&quot;: &quot;4.0.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1511 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/deep-eql/-/deep-eql-4.0.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1512 | <code>      &quot;integrity&quot;: &quot;sha512-c9h9dVVMigMPc4bwTvC5dxqtqJZwQPePsWjPlpSOnojbor6pGqdk541lfA7AqFQr5pB1BRdq0juY9db81BwyFw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1513 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1514 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1515 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1516 | <code>    &quot;node_modules/@types/estree&quot;: {</code> | node_modules/@types/estree: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1517 | <code>      &quot;version&quot;: &quot;1.0.9&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1518 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/estree/-/estree-1.0.9.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1519 | <code>      &quot;integrity&quot;: &quot;sha512-GhdPgy1el4/ImP05X05Uw4cw2/M93BCUmnEvWZNStlCzEKME4Fkk+YpoA5OiHNQmoS7Cafb8Xa3Pya8m1Qrzeg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1520 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1521 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1522 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1523 | <code>    &quot;node_modules/@types/react&quot;: {</code> | node_modules/@types/react: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1524 | <code>      &quot;version&quot;: &quot;19.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1525 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/react/-/react-19.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1526 | <code>      &quot;integrity&quot;: &quot;sha512-N0rFCuH9YoxG9/m61l9MfpJKfmLOVU0em7ipIz6TRgSSkvReLB9vL85GB+yr8Bs5leqpvg96JSwF4ZS1s4viQg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1527 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1528 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1529 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1530 | <code>        &quot;csstype&quot;: &quot;^3.2.2&quot;</code> | csstype: Dependency requirement or executable metadata named csstype. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1531 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1532 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1533 | <code>    &quot;node_modules/@types/react-dom&quot;: {</code> | node_modules/@types/react-dom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1534 | <code>      &quot;version&quot;: &quot;19.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1535 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@types/react-dom/-/react-dom-19.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1536 | <code>      &quot;integrity&quot;: &quot;sha512-ZI7bU42mZXXKHn/qNLEw2IrbiINU7X5+vfgdixBHkCNpYWXjKgfQ/P+uyGb5CjOLB9UcnTeg3rylQtV2hym44Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1537 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1538 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1539 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 1540 | <code>        &quot;@types/react&quot;: &quot;^19.3.0&quot;</code> | @types/react: Dependency requirement or executable metadata named @types/react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1541 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1542 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1543 | <code>    &quot;node_modules/@vitejs/plugin-react&quot;: {</code> | node_modules/@vitejs/plugin-react: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1544 | <code>      &quot;version&quot;: &quot;4.7.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1545 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitejs/plugin-react/-/plugin-react-4.7.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1546 | <code>      &quot;integrity&quot;: &quot;sha512-gUu9hwfWvvEDBBmgtAowQCojwZmJ5mcLn3aufeCsitijs3+f2NsrPtlAWIR6OPiqljl96GVCUbLe0HyqIpVaoA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1547 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1548 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1549 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1550 | <code>        &quot;@babel/core&quot;: &quot;^7.28.0&quot;,</code> | @babel/core: Dependency requirement or executable metadata named @babel/core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1551 | <code>        &quot;@babel/plugin-transform-react-jsx-self&quot;: &quot;^7.27.1&quot;,</code> | @babel/plugin-transform-react-jsx-self: Dependency requirement or executable metadata named @babel/plugin-transform-react-jsx-self. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1552 | <code>        &quot;@babel/plugin-transform-react-jsx-source&quot;: &quot;^7.27.1&quot;,</code> | @babel/plugin-transform-react-jsx-source: Dependency requirement or executable metadata named @babel/plugin-transform-react-jsx-source. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1553 | <code>        &quot;@rolldown/pluginutils&quot;: &quot;1.0.0-beta.27&quot;,</code> | @rolldown/pluginutils: Dependency requirement or executable metadata named @rolldown/pluginutils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1554 | <code>        &quot;@types/babel__core&quot;: &quot;^7.20.5&quot;,</code> | @types/babel__core: Dependency requirement or executable metadata named @types/babel__core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1555 | <code>        &quot;react-refresh&quot;: &quot;^0.17.0&quot;</code> | react-refresh: Dependency requirement or executable metadata named react-refresh. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1556 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1557 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1558 | <code>        &quot;node&quot;: &quot;^14.18.0 &#124;&#124; &gt;=16.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1559 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1560 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 1561 | <code>        &quot;vite&quot;: &quot;^4.2.0 &#124;&#124; ^5.0.0 &#124;&#124; ^6.0.0 &#124;&#124; ^7.0.0&quot;</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1562 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1563 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1564 | <code>    &quot;node_modules/@vitest/expect&quot;: {</code> | node_modules/@vitest/expect: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1565 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1566 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/expect/-/expect-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1567 | <code>      &quot;integrity&quot;: &quot;sha512-E8eBXaKibuvH2pSZErOjdVb5vF4PbKYcrnluBTYxEk1l/VhhwZg1kZQsdtjq+CsF5CFydf2Rdkz7jDHKSisi3w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1568 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1569 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1570 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1571 | <code>        &quot;@types/chai&quot;: &quot;^5.2.2&quot;,</code> | @types/chai: Dependency requirement or executable metadata named @types/chai. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1572 | <code>        &quot;@vitest/spy&quot;: &quot;3.2.7&quot;,</code> | @vitest/spy: Dependency requirement or executable metadata named @vitest/spy. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1573 | <code>        &quot;@vitest/utils&quot;: &quot;3.2.7&quot;,</code> | @vitest/utils: Dependency requirement or executable metadata named @vitest/utils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1574 | <code>        &quot;chai&quot;: &quot;^5.2.0&quot;,</code> | chai: Dependency requirement or executable metadata named chai. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1575 | <code>        &quot;tinyrainbow&quot;: &quot;^2.0.0&quot;</code> | tinyrainbow: Dependency requirement or executable metadata named tinyrainbow. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1576 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1577 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1578 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1579 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1580 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1581 | <code>    &quot;node_modules/@vitest/mocker&quot;: {</code> | node_modules/@vitest/mocker: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1582 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1583 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/mocker/-/mocker-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1584 | <code>      &quot;integrity&quot;: &quot;sha512-Trr0hYO9CM3Wj6ksWHRhK9IZpIY6wTMO5u/MqXurMxT57sWBaOPEtP3Oq60ihZuh5JsiagKfz95OcxdEP6dBrA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1585 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1586 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1587 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1588 | <code>        &quot;@vitest/spy&quot;: &quot;3.2.7&quot;,</code> | @vitest/spy: Dependency requirement or executable metadata named @vitest/spy. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1589 | <code>        &quot;estree-walker&quot;: &quot;^3.0.3&quot;,</code> | estree-walker: Dependency requirement or executable metadata named estree-walker. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1590 | <code>        &quot;magic-string&quot;: &quot;^0.30.17&quot;</code> | magic-string: Dependency requirement or executable metadata named magic-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1591 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1592 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1593 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1594 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1595 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 1596 | <code>        &quot;msw&quot;: &quot;^2.4.9&quot;,</code> | msw: Dependency requirement or executable metadata named msw. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1597 | <code>        &quot;vite&quot;: &quot;^5.0.0 &#124;&#124; ^6.0.0 &#124;&#124; ^7.0.0-0&quot;</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1598 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1599 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 1600 | <code>        &quot;msw&quot;: {</code> | msw: Dependency requirement or executable metadata named msw. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1601 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 1602 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1603 | <code>        &quot;vite&quot;: {</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1604 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 1605 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1606 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1607 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1608 | <code>    &quot;node_modules/@vitest/pretty-format&quot;: {</code> | node_modules/@vitest/pretty-format: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1609 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1610 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/pretty-format/-/pretty-format-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1611 | <code>      &quot;integrity&quot;: &quot;sha512-KUHlwqVu0sRlhCdyPdQ/wBoTfRahjUky1MubOmYw9fWfIZy1gNoHpuaaQBPAaMaVYdQYHJLurzj8ECCj5OwTqA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1612 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1613 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1614 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1615 | <code>        &quot;tinyrainbow&quot;: &quot;^2.0.0&quot;</code> | tinyrainbow: Dependency requirement or executable metadata named tinyrainbow. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1616 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1617 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1618 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1619 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1620 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1621 | <code>    &quot;node_modules/@vitest/runner&quot;: {</code> | node_modules/@vitest/runner: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1622 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1623 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/runner/-/runner-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1624 | <code>      &quot;integrity&quot;: &quot;sha512-sB9y4ovltoQP+WaUPwmSxO9WIg9Ig694Di5PalVPsYHklAdE027mehpWF2SQSVq+k6sFgaivbTjTJwZLSHbedA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1625 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1626 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1627 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1628 | <code>        &quot;@vitest/utils&quot;: &quot;3.2.7&quot;,</code> | @vitest/utils: Dependency requirement or executable metadata named @vitest/utils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1629 | <code>        &quot;pathe&quot;: &quot;^2.0.3&quot;,</code> | pathe: Dependency requirement or executable metadata named pathe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1630 | <code>        &quot;strip-literal&quot;: &quot;^3.0.0&quot;</code> | strip-literal: Dependency requirement or executable metadata named strip-literal. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1631 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1632 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1633 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1634 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1635 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1636 | <code>    &quot;node_modules/@vitest/snapshot&quot;: {</code> | node_modules/@vitest/snapshot: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1637 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1638 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/snapshot/-/snapshot-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1639 | <code>      &quot;integrity&quot;: &quot;sha512-7C+MwShwtBSI5Buwoyg3s/iY1eHL9PKAf+O1wVh/TdnjXUtkoL/9YQtre90i4MtNXM6edP1wJ2zOBpfCyhIS7g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1640 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1641 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1642 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1643 | <code>        &quot;@vitest/pretty-format&quot;: &quot;3.2.7&quot;,</code> | @vitest/pretty-format: Dependency requirement or executable metadata named @vitest/pretty-format. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1644 | <code>        &quot;magic-string&quot;: &quot;^0.30.17&quot;,</code> | magic-string: Dependency requirement or executable metadata named magic-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1645 | <code>        &quot;pathe&quot;: &quot;^2.0.3&quot;</code> | pathe: Dependency requirement or executable metadata named pathe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1646 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1647 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1648 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1649 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1650 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1651 | <code>    &quot;node_modules/@vitest/spy&quot;: {</code> | node_modules/@vitest/spy: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1652 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1653 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/spy/-/spy-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1654 | <code>      &quot;integrity&quot;: &quot;sha512-Q2eQGI6d2L/hBtZ0qNuKcAGid68XK6cv1xsoaIma6PaJhHPoqcEJhYpXZ/5myCMqkNgtP6UKuBhbc0nHKnrkuQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1655 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1656 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1657 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1658 | <code>        &quot;tinyspy&quot;: &quot;^4.0.3&quot;</code> | tinyspy: Dependency requirement or executable metadata named tinyspy. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1659 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1660 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1661 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1662 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1663 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1664 | <code>    &quot;node_modules/@vitest/utils&quot;: {</code> | node_modules/@vitest/utils: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1665 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1666 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/@vitest/utils/-/utils-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1667 | <code>      &quot;integrity&quot;: &quot;sha512-x6BDOd7dyo3PFLY3I9/HJ25X/6OurhGXk2/B9gOZNPF7XDVjeBK4k01lQE5uvDpbuheErh91qYuE1E2OEjK3Rw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1668 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1669 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1670 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1671 | <code>        &quot;@vitest/pretty-format&quot;: &quot;3.2.7&quot;,</code> | @vitest/pretty-format: Dependency requirement or executable metadata named @vitest/pretty-format. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1672 | <code>        &quot;loupe&quot;: &quot;^3.1.4&quot;,</code> | loupe: Dependency requirement or executable metadata named loupe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1673 | <code>        &quot;tinyrainbow&quot;: &quot;^2.0.0&quot;</code> | tinyrainbow: Dependency requirement or executable metadata named tinyrainbow. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1674 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1675 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1676 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1677 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1678 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1679 | <code>    &quot;node_modules/agent-base&quot;: {</code> | node_modules/agent-base: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1680 | <code>      &quot;version&quot;: &quot;7.1.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1681 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/agent-base/-/agent-base-7.1.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1682 | <code>      &quot;integrity&quot;: &quot;sha512-MnA+YT8fwfJPgBx3m60MNqakm30XOkyIoH1y6huTQvC0PwZG7ki8NacLBcrPbNoo8vEZy7Jpuk7+jMO+CUovTQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1683 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1684 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1685 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1686 | <code>        &quot;node&quot;: &quot;&gt;= 14&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1687 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1688 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1689 | <code>    &quot;node_modules/ansi-regex&quot;: {</code> | node_modules/ansi-regex: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1690 | <code>      &quot;version&quot;: &quot;5.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1691 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/ansi-regex/-/ansi-regex-5.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1692 | <code>      &quot;integrity&quot;: &quot;sha512-quJQXlTSUGL2LH9SUXo8VwsY4soanhgo6LNSm84E1LBcE8s3O0wpdiRzyR9z/ZZJMlMWv37qOOb9pdJlMUEKFQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1693 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1694 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1695 | <code>      &quot;peer&quot;: true,</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 1696 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1697 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1698 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1699 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1700 | <code>    &quot;node_modules/ansi-styles&quot;: {</code> | node_modules/ansi-styles: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1701 | <code>      &quot;version&quot;: &quot;5.2.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1702 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/ansi-styles/-/ansi-styles-5.2.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1703 | <code>      &quot;integrity&quot;: &quot;sha512-Cxwpt2SfTzTtXcfOlzGEee8O+c+MmUgGrNiBcXnuWxuFJHe6a5Hz7qwhwe5OgaSYI0IJvkLqWX1ASG+cJOkEiA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1704 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1705 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1706 | <code>      &quot;peer&quot;: true,</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 1707 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1708 | <code>        &quot;node&quot;: &quot;&gt;=10&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1709 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1710 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1711 | <code>        &quot;url&quot;: &quot;https://github.com/chalk/ansi-styles?sponsor=1&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1712 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1713 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1714 | <code>    &quot;node_modules/aria-query&quot;: {</code> | node_modules/aria-query: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1715 | <code>      &quot;version&quot;: &quot;5.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1716 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/aria-query/-/aria-query-5.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1717 | <code>      &quot;integrity&quot;: &quot;sha512-b0P0sZPKtyu8HkeRAfCq0IfURZK+SuwMjY1UXGBU27wpAiTwQAIlq56IbIO+ytk/JjS1fMR14ee5WBBfKi5J6A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1718 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1719 | <code>      &quot;license&quot;: &quot;Apache-2.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1720 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1721 | <code>        &quot;dequal&quot;: &quot;^2.0.3&quot;</code> | dequal: Dependency requirement or executable metadata named dequal. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1722 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1723 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1724 | <code>    &quot;node_modules/assertion-error&quot;: {</code> | node_modules/assertion-error: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1725 | <code>      &quot;version&quot;: &quot;2.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1726 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/assertion-error/-/assertion-error-2.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1727 | <code>      &quot;integrity&quot;: &quot;sha512-Izi8RQcffqCeNVgFigKli1ssklIbpHnCYc6AknXGYoB6grJqyeby7jv12JUQgmTAnIDnbck1uxksT4dzN3PWBA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1728 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1729 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1730 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1731 | <code>        &quot;node&quot;: &quot;&gt;=12&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1732 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1733 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1734 | <code>    &quot;node_modules/baseline-browser-mapping&quot;: {</code> | node_modules/baseline-browser-mapping: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1735 | <code>      &quot;version&quot;: &quot;2.11.28&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1736 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/baseline-browser-mapping/-/baseline-browser-mapping-2.11.28.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1737 | <code>      &quot;integrity&quot;: &quot;sha512-br0LOmjJqr6Rt4AEkadbcNf67Zpo7EPwKsWbjnRrJIa1QYFHQBqM4C7F2WTbV8ahTEcg1Eo+Y0aWjjORInYFyA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1738 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1739 | <code>      &quot;license&quot;: &quot;Apache-2.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1740 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 1741 | <code>        &quot;baseline-browser-mapping&quot;: &quot;dist/cli.cjs&quot;</code> | baseline-browser-mapping: Dependency requirement or executable metadata named baseline-browser-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1742 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1743 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1744 | <code>        &quot;node&quot;: &quot;&gt;=6.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1745 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1746 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1747 | <code>    &quot;node_modules/browserslist&quot;: {</code> | node_modules/browserslist: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1748 | <code>      &quot;version&quot;: &quot;4.29.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1749 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/browserslist/-/browserslist-4.29.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1750 | <code>      &quot;integrity&quot;: &quot;sha512-1R4kiYKXGViqEN0CnoDrXc1StD9niAwu+j2dukWzrD4bJgsD4lDmEp0CRbc6E/vYJIfTHwPmwyaKtVSudICdPA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1751 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1752 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1753 | <code>        {</code> | Open a JSON object (named fields). |
| 1754 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1755 | <code>          &quot;url&quot;: &quot;https://opencollective.com/browserslist&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1756 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1757 | <code>        {</code> | Open a JSON object (named fields). |
| 1758 | <code>          &quot;type&quot;: &quot;tidelift&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1759 | <code>          &quot;url&quot;: &quot;https://tidelift.com/funding/github/npm/browserslist&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1760 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1761 | <code>        {</code> | Open a JSON object (named fields). |
| 1762 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1763 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/ai&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1764 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1765 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1766 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1767 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1768 | <code>        &quot;baseline-browser-mapping&quot;: &quot;^2.11.26&quot;,</code> | baseline-browser-mapping: Dependency requirement or executable metadata named baseline-browser-mapping. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1769 | <code>        &quot;caniuse-lite&quot;: &quot;^1.0.30001813&quot;,</code> | caniuse-lite: Dependency requirement or executable metadata named caniuse-lite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1770 | <code>        &quot;electron-to-chromium&quot;: &quot;^1.5.439&quot;,</code> | electron-to-chromium: Dependency requirement or executable metadata named electron-to-chromium. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1771 | <code>        &quot;node-releases&quot;: &quot;^2.0.57&quot;,</code> | node-releases: Dependency requirement or executable metadata named node-releases. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1772 | <code>        &quot;update-browserslist-db&quot;: &quot;^1.3.3&quot;</code> | update-browserslist-db: Dependency requirement or executable metadata named update-browserslist-db. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1773 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1774 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 1775 | <code>        &quot;browserslist&quot;: &quot;cli.js&quot;</code> | browserslist: Dependency requirement or executable metadata named browserslist. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1776 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1777 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1778 | <code>        &quot;node&quot;: &quot;^6 &#124;&#124; ^7 &#124;&#124; ^8 &#124;&#124; ^9 &#124;&#124; ^10 &#124;&#124; ^11 &#124;&#124; ^12 &#124;&#124; &gt;=13.7&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1779 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1780 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1781 | <code>    &quot;node_modules/cac&quot;: {</code> | node_modules/cac: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1782 | <code>      &quot;version&quot;: &quot;6.7.14&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1783 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/cac/-/cac-6.7.14.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1784 | <code>      &quot;integrity&quot;: &quot;sha512-b6Ilus+c3RrdDk+JhLKUAQfzzgLEPy6wcXqS7f/xe1EETvsDP6GORG7SFuOs6cID5YkqchW/LXZbX5bc8j7ZcQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1785 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1786 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1787 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1788 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1789 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1790 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1791 | <code>    &quot;node_modules/caniuse-lite&quot;: {</code> | node_modules/caniuse-lite: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1792 | <code>      &quot;version&quot;: &quot;1.0.30001815&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1793 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001815.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1794 | <code>      &quot;integrity&quot;: &quot;sha512-uDybUEyfgbyJJ93J1vikTylBX31AkdVYeVPeffMQpf8XN7hSfr0oZOn4VFOIMNvtU5+rHvC5Udg2TgtJKHm23Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1795 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1796 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1797 | <code>        {</code> | Open a JSON object (named fields). |
| 1798 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1799 | <code>          &quot;url&quot;: &quot;https://opencollective.com/browserslist&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1800 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1801 | <code>        {</code> | Open a JSON object (named fields). |
| 1802 | <code>          &quot;type&quot;: &quot;tidelift&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1803 | <code>          &quot;url&quot;: &quot;https://tidelift.com/funding/github/npm/caniuse-lite&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1804 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1805 | <code>        {</code> | Open a JSON object (named fields). |
| 1806 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 1807 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/ai&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1808 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1809 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1810 | <code>      &quot;license&quot;: &quot;CC-BY-4.0&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1811 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1812 | <code>    &quot;node_modules/chai&quot;: {</code> | node_modules/chai: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1813 | <code>      &quot;version&quot;: &quot;5.3.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1814 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/chai/-/chai-5.3.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1815 | <code>      &quot;integrity&quot;: &quot;sha512-4zNhdJD/iOjSH0A05ea+Ke6MU5mmpQcbQsSOkgdaUMJ9zTlDTD/GYlwohmIE2u0gaxHYiVHEn1Fw9mZ/ktJWgw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1816 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1817 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1818 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1819 | <code>        &quot;assertion-error&quot;: &quot;^2.0.1&quot;,</code> | assertion-error: Dependency requirement or executable metadata named assertion-error. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1820 | <code>        &quot;check-error&quot;: &quot;^2.1.1&quot;,</code> | check-error: Dependency requirement or executable metadata named check-error. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1821 | <code>        &quot;deep-eql&quot;: &quot;^5.0.1&quot;,</code> | deep-eql: Dependency requirement or executable metadata named deep-eql. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1822 | <code>        &quot;loupe&quot;: &quot;^3.1.0&quot;,</code> | loupe: Dependency requirement or executable metadata named loupe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1823 | <code>        &quot;pathval&quot;: &quot;^2.0.0&quot;</code> | pathval: Dependency requirement or executable metadata named pathval. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1824 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1825 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1826 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1827 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1828 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1829 | <code>    &quot;node_modules/check-error&quot;: {</code> | node_modules/check-error: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1830 | <code>      &quot;version&quot;: &quot;2.1.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1831 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/check-error/-/check-error-2.1.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1832 | <code>      &quot;integrity&quot;: &quot;sha512-PAJdDJusoxnwm1VwW07VWwUN1sl7smmC3OKggvndJFadxxDRyFJBX/ggnu/KE4kQAB7a3Dp8f/YXC1FlUprWmA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1833 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1834 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1835 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1836 | <code>        &quot;node&quot;: &quot;&gt;= 16&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1837 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1838 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1839 | <code>    &quot;node_modules/convert-source-map&quot;: {</code> | node_modules/convert-source-map: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1840 | <code>      &quot;version&quot;: &quot;2.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1841 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/convert-source-map/-/convert-source-map-2.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1842 | <code>      &quot;integrity&quot;: &quot;sha512-Kvp459HrV2FEJ1CAsi1Ku+MY3kasH19TFykTz2xWmMeq6bk2NU3XXvfJ+Q61m0xktWwt+1HSYf3JZsTms3aRJg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1843 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1844 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1845 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1846 | <code>    &quot;node_modules/css.escape&quot;: {</code> | node_modules/css.escape: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1847 | <code>      &quot;version&quot;: &quot;1.5.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1848 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/css.escape/-/css.escape-1.5.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1849 | <code>      &quot;integrity&quot;: &quot;sha512-YUifsXXuknHlUsmlgyY0PKzgPOr7/FjCePfHNt0jxm83wHZi44VDMQ7/fGNkjY3/jV1MC+1CmZbaHzugyeRtpg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1850 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1851 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1852 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1853 | <code>    &quot;node_modules/cssstyle&quot;: {</code> | node_modules/cssstyle: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1854 | <code>      &quot;version&quot;: &quot;4.6.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1855 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/cssstyle/-/cssstyle-4.6.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1856 | <code>      &quot;integrity&quot;: &quot;sha512-2z+rWdzbbSZv6/rhtvzvqeZQHrBaqgogqt85sqFNbabZOuFbCVFb8kPeEtZjiKkbrm395irpNKiYeFeLiQnFPg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1857 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1858 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1859 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1860 | <code>        &quot;@asamuzakjp/css-color&quot;: &quot;^3.2.0&quot;,</code> | @asamuzakjp/css-color: Dependency requirement or executable metadata named @asamuzakjp/css-color. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1861 | <code>        &quot;rrweb-cssom&quot;: &quot;^0.8.0&quot;</code> | rrweb-cssom: Dependency requirement or executable metadata named rrweb-cssom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1862 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1863 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1864 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1865 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1866 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1867 | <code>    &quot;node_modules/csstype&quot;: {</code> | node_modules/csstype: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1868 | <code>      &quot;version&quot;: &quot;3.2.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1869 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/csstype/-/csstype-3.2.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1870 | <code>      &quot;integrity&quot;: &quot;sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1871 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1872 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1873 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1874 | <code>    &quot;node_modules/data-urls&quot;: {</code> | node_modules/data-urls: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1875 | <code>      &quot;version&quot;: &quot;5.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1876 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/data-urls/-/data-urls-5.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1877 | <code>      &quot;integrity&quot;: &quot;sha512-ZYP5VBHshaDAiVZxjbRVcFJpc+4xGgT0bK3vzy1HLN8jTO975HEbuYzZJcHoQEY5K1a0z8YayJkyVETa08eNTg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1878 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1879 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1880 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1881 | <code>        &quot;whatwg-mimetype&quot;: &quot;^4.0.0&quot;,</code> | whatwg-mimetype: Dependency requirement or executable metadata named whatwg-mimetype. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1882 | <code>        &quot;whatwg-url&quot;: &quot;^14.0.0&quot;</code> | whatwg-url: Dependency requirement or executable metadata named whatwg-url. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1883 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1884 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1885 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1886 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1887 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1888 | <code>    &quot;node_modules/debug&quot;: {</code> | node_modules/debug: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1889 | <code>      &quot;version&quot;: &quot;4.4.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1890 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/debug/-/debug-4.4.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1891 | <code>      &quot;integrity&quot;: &quot;sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1892 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1893 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1894 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 1895 | <code>        &quot;ms&quot;: &quot;^2.1.3&quot;</code> | ms: Dependency requirement or executable metadata named ms. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1896 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1897 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1898 | <code>        &quot;node&quot;: &quot;&gt;=6.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1899 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1900 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 1901 | <code>        &quot;supports-color&quot;: {</code> | supports-color: Dependency requirement or executable metadata named supports-color. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1902 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 1903 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1904 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1905 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1906 | <code>    &quot;node_modules/decimal.js&quot;: {</code> | node_modules/decimal.js: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1907 | <code>      &quot;version&quot;: &quot;10.6.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1908 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/decimal.js/-/decimal.js-10.6.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1909 | <code>      &quot;integrity&quot;: &quot;sha512-YpgQiITW3JXGntzdUmyUR1V812Hn8T1YVXhCu+wO3OpS4eU9l4YdD3qjyiKdV6mvV29zapkMeD390UVEf2lkUg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1910 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1911 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1912 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1913 | <code>    &quot;node_modules/deep-eql&quot;: {</code> | node_modules/deep-eql: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1914 | <code>      &quot;version&quot;: &quot;5.0.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1915 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/deep-eql/-/deep-eql-5.0.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1916 | <code>      &quot;integrity&quot;: &quot;sha512-h5k/5U50IJJFpzfL6nO9jaaumfjO/f2NjK/oYB2Djzm4p9L+3T9qWpZqZ2hAbLPuuYq9wrU08WQyBTL5GbPk5Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1917 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1918 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1919 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1920 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1921 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1922 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1923 | <code>    &quot;node_modules/dequal&quot;: {</code> | node_modules/dequal: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1924 | <code>      &quot;version&quot;: &quot;2.0.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1925 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/dequal/-/dequal-2.0.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1926 | <code>      &quot;integrity&quot;: &quot;sha512-0je+qPKHEMohvfRTCEo3CrPG6cAzAYgmzKyxRiYSSDkS6eGJdyVJm7WaYA5ECaAD9wLB2T4EEeymA5aFVcYXCA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1927 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1928 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1929 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1930 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1931 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1932 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1933 | <code>    &quot;node_modules/dom-accessibility-api&quot;: {</code> | node_modules/dom-accessibility-api: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1934 | <code>      &quot;version&quot;: &quot;0.5.16&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1935 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/dom-accessibility-api/-/dom-accessibility-api-0.5.16.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1936 | <code>      &quot;integrity&quot;: &quot;sha512-X7BJ2yElsnOJ30pZF4uIIDfBEVgF4XEBxL9Bxhy6dnrm5hkzqmsWHGTiHqRiITNhMyFLyAiWndIJP7Z1NTteDg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1937 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1938 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1939 | <code>      &quot;peer&quot;: true</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 1940 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1941 | <code>    &quot;node_modules/electron-to-chromium&quot;: {</code> | node_modules/electron-to-chromium: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1942 | <code>      &quot;version&quot;: &quot;1.5.452&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1943 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.452.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1944 | <code>      &quot;integrity&quot;: &quot;sha512-cVvk1YBSj6571VmV6hdJTqj94Y79xSu8cj6Y9t6ae4Y4431z8/7EJFvu3rVp90xhfuv9BpPKUmaLfTo4+FOGBg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1945 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1946 | <code>      &quot;license&quot;: &quot;ISC&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1947 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1948 | <code>    &quot;node_modules/entities&quot;: {</code> | node_modules/entities: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1949 | <code>      &quot;version&quot;: &quot;6.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1950 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/entities/-/entities-6.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1951 | <code>      &quot;integrity&quot;: &quot;sha512-aN97NXWF6AWBTahfVOIrB/NShkzi5H7F9r1s9mD3cDj4Ko5f2qhhVoYMibXF7GlLveb/D2ioWay8lxI97Ven3g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1952 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1953 | <code>      &quot;license&quot;: &quot;BSD-2-Clause&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1954 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1955 | <code>        &quot;node&quot;: &quot;&gt;=0.12&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1956 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1957 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 1958 | <code>        &quot;url&quot;: &quot;https://github.com/fb55/entities?sponsor=1&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 1959 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1960 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1961 | <code>    &quot;node_modules/es-module-lexer&quot;: {</code> | node_modules/es-module-lexer: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1962 | <code>      &quot;version&quot;: &quot;1.7.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1963 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/es-module-lexer/-/es-module-lexer-1.7.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1964 | <code>      &quot;integrity&quot;: &quot;sha512-jEQoCwk8hyb2AZziIOLhDqpm5+2ww5uIE6lkO/6jcOCusfk6LhMHpXXfBLXTZ7Ydyt0j4VoUQv6uGNYbdW+kBA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1965 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1966 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1967 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1968 | <code>    &quot;node_modules/esbuild&quot;: {</code> | node_modules/esbuild: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 1969 | <code>      &quot;version&quot;: &quot;0.25.12&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 1970 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/esbuild/-/esbuild-0.25.12.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 1971 | <code>      &quot;integrity&quot;: &quot;sha512-bbPBYYrtZbkt6Os6FiTLCTFxvq4tt3JKall1vRwshA3fdVztsLAatFaZobhkBC8/BrPetoa0oksYoKXoG4ryJg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 1972 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 1973 | <code>      &quot;hasInstallScript&quot;: true,</code> | hasInstallScript: npm records that this dependency has install-time script behavior. |
| 1974 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 1975 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 1976 | <code>        &quot;esbuild&quot;: &quot;bin/esbuild&quot;</code> | esbuild: Dependency requirement or executable metadata named esbuild. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1977 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1978 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 1979 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 1980 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 1981 | <code>      &quot;optionalDependencies&quot;: {</code> | optionalDependencies: Dependencies whose absence may be tolerated, often platform-specific binaries. |
| 1982 | <code>        &quot;@esbuild/aix-ppc64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/aix-ppc64: Dependency requirement or executable metadata named @esbuild/aix-ppc64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1983 | <code>        &quot;@esbuild/android-arm&quot;: &quot;0.25.12&quot;,</code> | @esbuild/android-arm: Dependency requirement or executable metadata named @esbuild/android-arm. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1984 | <code>        &quot;@esbuild/android-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/android-arm64: Dependency requirement or executable metadata named @esbuild/android-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1985 | <code>        &quot;@esbuild/android-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/android-x64: Dependency requirement or executable metadata named @esbuild/android-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1986 | <code>        &quot;@esbuild/darwin-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/darwin-arm64: Dependency requirement or executable metadata named @esbuild/darwin-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1987 | <code>        &quot;@esbuild/darwin-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/darwin-x64: Dependency requirement or executable metadata named @esbuild/darwin-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1988 | <code>        &quot;@esbuild/freebsd-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/freebsd-arm64: Dependency requirement or executable metadata named @esbuild/freebsd-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1989 | <code>        &quot;@esbuild/freebsd-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/freebsd-x64: Dependency requirement or executable metadata named @esbuild/freebsd-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1990 | <code>        &quot;@esbuild/linux-arm&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-arm: Dependency requirement or executable metadata named @esbuild/linux-arm. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1991 | <code>        &quot;@esbuild/linux-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-arm64: Dependency requirement or executable metadata named @esbuild/linux-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1992 | <code>        &quot;@esbuild/linux-ia32&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-ia32: Dependency requirement or executable metadata named @esbuild/linux-ia32. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1993 | <code>        &quot;@esbuild/linux-loong64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-loong64: Dependency requirement or executable metadata named @esbuild/linux-loong64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1994 | <code>        &quot;@esbuild/linux-mips64el&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-mips64el: Dependency requirement or executable metadata named @esbuild/linux-mips64el. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1995 | <code>        &quot;@esbuild/linux-ppc64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-ppc64: Dependency requirement or executable metadata named @esbuild/linux-ppc64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1996 | <code>        &quot;@esbuild/linux-riscv64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-riscv64: Dependency requirement or executable metadata named @esbuild/linux-riscv64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1997 | <code>        &quot;@esbuild/linux-s390x&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-s390x: Dependency requirement or executable metadata named @esbuild/linux-s390x. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1998 | <code>        &quot;@esbuild/linux-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/linux-x64: Dependency requirement or executable metadata named @esbuild/linux-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 1999 | <code>        &quot;@esbuild/netbsd-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/netbsd-arm64: Dependency requirement or executable metadata named @esbuild/netbsd-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2000 | <code>        &quot;@esbuild/netbsd-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/netbsd-x64: Dependency requirement or executable metadata named @esbuild/netbsd-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2001 | <code>        &quot;@esbuild/openbsd-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/openbsd-arm64: Dependency requirement or executable metadata named @esbuild/openbsd-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2002 | <code>        &quot;@esbuild/openbsd-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/openbsd-x64: Dependency requirement or executable metadata named @esbuild/openbsd-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2003 | <code>        &quot;@esbuild/openharmony-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/openharmony-arm64: Dependency requirement or executable metadata named @esbuild/openharmony-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2004 | <code>        &quot;@esbuild/sunos-x64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/sunos-x64: Dependency requirement or executable metadata named @esbuild/sunos-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2005 | <code>        &quot;@esbuild/win32-arm64&quot;: &quot;0.25.12&quot;,</code> | @esbuild/win32-arm64: Dependency requirement or executable metadata named @esbuild/win32-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2006 | <code>        &quot;@esbuild/win32-ia32&quot;: &quot;0.25.12&quot;,</code> | @esbuild/win32-ia32: Dependency requirement or executable metadata named @esbuild/win32-ia32. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2007 | <code>        &quot;@esbuild/win32-x64&quot;: &quot;0.25.12&quot;</code> | @esbuild/win32-x64: Dependency requirement or executable metadata named @esbuild/win32-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2008 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2009 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2010 | <code>    &quot;node_modules/escalade&quot;: {</code> | node_modules/escalade: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2011 | <code>      &quot;version&quot;: &quot;3.2.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2012 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2013 | <code>      &quot;integrity&quot;: &quot;sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2014 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2015 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2016 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2017 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2018 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2019 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2020 | <code>    &quot;node_modules/estree-walker&quot;: {</code> | node_modules/estree-walker: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2021 | <code>      &quot;version&quot;: &quot;3.0.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2022 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/estree-walker/-/estree-walker-3.0.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2023 | <code>      &quot;integrity&quot;: &quot;sha512-7RUKfXgSMMkzt6ZuXmqapOurLGPPfgj6l9uRZ7lRGolvk0y2yocc35LdcxKC5PQZdn2DMqioAQ2NoWcrTKmm6g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2024 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2025 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2026 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2027 | <code>        &quot;@types/estree&quot;: &quot;^1.0.0&quot;</code> | @types/estree: Dependency requirement or executable metadata named @types/estree. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2028 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2029 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2030 | <code>    &quot;node_modules/expect-type&quot;: {</code> | node_modules/expect-type: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2031 | <code>      &quot;version&quot;: &quot;1.4.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2032 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/expect-type/-/expect-type-1.4.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2033 | <code>      &quot;integrity&quot;: &quot;sha512-KfYbmpRm0VbLjEvVa9yGwCi9GI34xvi7A/HXYWQO65CSD2u3MczUJSuwXKFIxlGsgBQizV9q5J9NHj4VG0n+pA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2034 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2035 | <code>      &quot;license&quot;: &quot;Apache-2.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2036 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2037 | <code>        &quot;node&quot;: &quot;&gt;=12.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2038 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2039 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2040 | <code>    &quot;node_modules/fdir&quot;: {</code> | node_modules/fdir: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2041 | <code>      &quot;version&quot;: &quot;6.5.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2042 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2043 | <code>      &quot;integrity&quot;: &quot;sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2044 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2045 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2046 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2047 | <code>        &quot;node&quot;: &quot;&gt;=12.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2048 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2049 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2050 | <code>        &quot;picomatch&quot;: &quot;^3 &#124;&#124; ^4&quot;</code> | picomatch: Dependency requirement or executable metadata named picomatch. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2051 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2052 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 2053 | <code>        &quot;picomatch&quot;: {</code> | picomatch: Dependency requirement or executable metadata named picomatch. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2054 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2055 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2056 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2057 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2058 | <code>    &quot;node_modules/fsevents&quot;: {</code> | node_modules/fsevents: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2059 | <code>      &quot;version&quot;: &quot;2.3.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2060 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/fsevents/-/fsevents-2.3.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2061 | <code>      &quot;integrity&quot;: &quot;sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2062 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2063 | <code>      &quot;hasInstallScript&quot;: true,</code> | hasInstallScript: npm records that this dependency has install-time script behavior. |
| 2064 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2065 | <code>      &quot;optional&quot;: true,</code> | optional: True marks an optional dependency/peer record. |
| 2066 | <code>      &quot;os&quot;: [</code> | os: Operating systems supported by the dependency record. |
| 2067 | <code>        &quot;darwin&quot;</code> | Array item for the current artifact (node_modules/fsevents): "darwin". This is metadata, not a code statement. |
| 2068 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2069 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2070 | <code>        &quot;node&quot;: &quot;^8.16.0 &#124;&#124; ^10.6.0 &#124;&#124; &gt;=11.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2071 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2072 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2073 | <code>    &quot;node_modules/gensync&quot;: {</code> | node_modules/gensync: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2074 | <code>      &quot;version&quot;: &quot;1.0.0-beta.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2075 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/gensync/-/gensync-1.0.0-beta.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2076 | <code>      &quot;integrity&quot;: &quot;sha512-3hN7NaskYvMDLQY55gnW3NQ+mesEAepTqlg+VEbj7zzqEMBVNhzcGYYeqFo/TlYz6eQiFcp1HcsCZO+nGgS8zg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2077 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2078 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2079 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2080 | <code>        &quot;node&quot;: &quot;&gt;=6.9.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2081 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2082 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2083 | <code>    &quot;node_modules/html-encoding-sniffer&quot;: {</code> | node_modules/html-encoding-sniffer: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2084 | <code>      &quot;version&quot;: &quot;4.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2085 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/html-encoding-sniffer/-/html-encoding-sniffer-4.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2086 | <code>      &quot;integrity&quot;: &quot;sha512-Y22oTqIU4uuPgEemfz7NDJz6OeKf12Lsu+QC+s3BVpda64lTiMYCyGwg5ki4vFxkMwQdeZDl2adZoqUgdFuTgQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2087 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2088 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2089 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2090 | <code>        &quot;whatwg-encoding&quot;: &quot;^3.1.1&quot;</code> | whatwg-encoding: Dependency requirement or executable metadata named whatwg-encoding. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2091 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2092 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2093 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2094 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2095 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2096 | <code>    &quot;node_modules/http-proxy-agent&quot;: {</code> | node_modules/http-proxy-agent: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2097 | <code>      &quot;version&quot;: &quot;7.0.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2098 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/http-proxy-agent/-/http-proxy-agent-7.0.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2099 | <code>      &quot;integrity&quot;: &quot;sha512-T1gkAiYYDWYx3V5Bmyu7HcfcvL7mUrTWiM6yOfa3PIphViJ/gFPbvidQ+veqSOHci/PxBcDabeUNCzpOODJZig==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2100 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2101 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2102 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2103 | <code>        &quot;agent-base&quot;: &quot;^7.1.0&quot;,</code> | agent-base: Dependency requirement or executable metadata named agent-base. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2104 | <code>        &quot;debug&quot;: &quot;^4.3.4&quot;</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2105 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2106 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2107 | <code>        &quot;node&quot;: &quot;&gt;= 14&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2108 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2109 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2110 | <code>    &quot;node_modules/https-proxy-agent&quot;: {</code> | node_modules/https-proxy-agent: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2111 | <code>      &quot;version&quot;: &quot;7.0.6&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2112 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/https-proxy-agent/-/https-proxy-agent-7.0.6.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2113 | <code>      &quot;integrity&quot;: &quot;sha512-vK9P5/iUfdl95AI+JVyUuIcVtd4ofvtrOr3HNtM2yxC9bnMbEdp3x01OhQNnjb8IJYi38VlTE3mBXwcfvywuSw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2114 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2115 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2116 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2117 | <code>        &quot;agent-base&quot;: &quot;^7.1.2&quot;,</code> | agent-base: Dependency requirement or executable metadata named agent-base. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2118 | <code>        &quot;debug&quot;: &quot;4&quot;</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2119 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2120 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2121 | <code>        &quot;node&quot;: &quot;&gt;= 14&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2122 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2123 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2124 | <code>    &quot;node_modules/iconv-lite&quot;: {</code> | node_modules/iconv-lite: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2125 | <code>      &quot;version&quot;: &quot;0.6.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2126 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/iconv-lite/-/iconv-lite-0.6.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2127 | <code>      &quot;integrity&quot;: &quot;sha512-4fCk79wshMdzMp2rH06qWrJE4iolqLhCUH+OiuIgU++RB0+94NlDL81atO7GX55uUKueo0txHNtvEyI6D7WdMw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2128 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2129 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2130 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2131 | <code>        &quot;safer-buffer&quot;: &quot;&gt;= 2.1.2 &lt; 3.0.0&quot;</code> | safer-buffer: Dependency requirement or executable metadata named safer-buffer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2132 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2133 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2134 | <code>        &quot;node&quot;: &quot;&gt;=0.10.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2135 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2136 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2137 | <code>    &quot;node_modules/indent-string&quot;: {</code> | node_modules/indent-string: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2138 | <code>      &quot;version&quot;: &quot;4.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2139 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/indent-string/-/indent-string-4.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2140 | <code>      &quot;integrity&quot;: &quot;sha512-EdDDZu4A2OyIK7Lr/2zG+w5jmbuk1DVBnEwREQvBzspBJkCEbRa8GxU1lghYcaGJCnRWibjDXlq779X1/y5xwg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2141 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2142 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2143 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2144 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2145 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2146 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2147 | <code>    &quot;node_modules/is-potential-custom-element-name&quot;: {</code> | node_modules/is-potential-custom-element-name: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2148 | <code>      &quot;version&quot;: &quot;1.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2149 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/is-potential-custom-element-name/-/is-potential-custom-element-name-1.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2150 | <code>      &quot;integrity&quot;: &quot;sha512-bCYeRA2rVibKZd+s2625gGnGF/t7DSqDs4dP7CrLA1m7jKWz6pps0LpYLJN8Q64HtmPKJ1hrN3nzPNKFEKOUiQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2151 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2152 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2153 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2154 | <code>    &quot;node_modules/js-tokens&quot;: {</code> | node_modules/js-tokens: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2155 | <code>      &quot;version&quot;: &quot;4.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2156 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2157 | <code>      &quot;integrity&quot;: &quot;sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2158 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2159 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2160 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2161 | <code>    &quot;node_modules/jsdom&quot;: {</code> | node_modules/jsdom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2162 | <code>      &quot;version&quot;: &quot;26.1.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2163 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/jsdom/-/jsdom-26.1.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2164 | <code>      &quot;integrity&quot;: &quot;sha512-Cvc9WUhxSMEo4McES3P7oK3QaXldCfNWp7pl2NNeiIFlCoLr3kfq9kb1fxftiwk1FLV7CvpvDfonxtzUDeSOPg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2165 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2166 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2167 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2168 | <code>        &quot;cssstyle&quot;: &quot;^4.2.1&quot;,</code> | cssstyle: Dependency requirement or executable metadata named cssstyle. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2169 | <code>        &quot;data-urls&quot;: &quot;^5.0.0&quot;,</code> | data-urls: Dependency requirement or executable metadata named data-urls. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2170 | <code>        &quot;decimal.js&quot;: &quot;^10.5.0&quot;,</code> | decimal.js: Dependency requirement or executable metadata named decimal.js. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2171 | <code>        &quot;html-encoding-sniffer&quot;: &quot;^4.0.0&quot;,</code> | html-encoding-sniffer: Dependency requirement or executable metadata named html-encoding-sniffer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2172 | <code>        &quot;http-proxy-agent&quot;: &quot;^7.0.2&quot;,</code> | http-proxy-agent: Dependency requirement or executable metadata named http-proxy-agent. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2173 | <code>        &quot;https-proxy-agent&quot;: &quot;^7.0.6&quot;,</code> | https-proxy-agent: Dependency requirement or executable metadata named https-proxy-agent. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2174 | <code>        &quot;is-potential-custom-element-name&quot;: &quot;^1.0.1&quot;,</code> | is-potential-custom-element-name: Dependency requirement or executable metadata named is-potential-custom-element-name. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2175 | <code>        &quot;nwsapi&quot;: &quot;^2.2.16&quot;,</code> | nwsapi: Dependency requirement or executable metadata named nwsapi. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2176 | <code>        &quot;parse5&quot;: &quot;^7.2.1&quot;,</code> | parse5: Dependency requirement or executable metadata named parse5. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2177 | <code>        &quot;rrweb-cssom&quot;: &quot;^0.8.0&quot;,</code> | rrweb-cssom: Dependency requirement or executable metadata named rrweb-cssom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2178 | <code>        &quot;saxes&quot;: &quot;^6.0.0&quot;,</code> | saxes: Dependency requirement or executable metadata named saxes. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2179 | <code>        &quot;symbol-tree&quot;: &quot;^3.2.4&quot;,</code> | symbol-tree: Dependency requirement or executable metadata named symbol-tree. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2180 | <code>        &quot;tough-cookie&quot;: &quot;^5.1.1&quot;,</code> | tough-cookie: Dependency requirement or executable metadata named tough-cookie. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2181 | <code>        &quot;w3c-xmlserializer&quot;: &quot;^5.0.0&quot;,</code> | w3c-xmlserializer: Dependency requirement or executable metadata named w3c-xmlserializer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2182 | <code>        &quot;webidl-conversions&quot;: &quot;^7.0.0&quot;,</code> | webidl-conversions: Dependency requirement or executable metadata named webidl-conversions. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2183 | <code>        &quot;whatwg-encoding&quot;: &quot;^3.1.1&quot;,</code> | whatwg-encoding: Dependency requirement or executable metadata named whatwg-encoding. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2184 | <code>        &quot;whatwg-mimetype&quot;: &quot;^4.0.0&quot;,</code> | whatwg-mimetype: Dependency requirement or executable metadata named whatwg-mimetype. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2185 | <code>        &quot;whatwg-url&quot;: &quot;^14.1.1&quot;,</code> | whatwg-url: Dependency requirement or executable metadata named whatwg-url. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2186 | <code>        &quot;ws&quot;: &quot;^8.18.0&quot;,</code> | ws: Dependency requirement or executable metadata named ws. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2187 | <code>        &quot;xml-name-validator&quot;: &quot;^5.0.0&quot;</code> | xml-name-validator: Dependency requirement or executable metadata named xml-name-validator. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2188 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2189 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2190 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2191 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2192 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2193 | <code>        &quot;canvas&quot;: &quot;^3.0.0&quot;</code> | canvas: Dependency requirement or executable metadata named canvas. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2194 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2195 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 2196 | <code>        &quot;canvas&quot;: {</code> | canvas: Dependency requirement or executable metadata named canvas. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2197 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2198 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2199 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2200 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2201 | <code>    &quot;node_modules/jsesc&quot;: {</code> | node_modules/jsesc: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2202 | <code>      &quot;version&quot;: &quot;3.1.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2203 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/jsesc/-/jsesc-3.1.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2204 | <code>      &quot;integrity&quot;: &quot;sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2205 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2206 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2207 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2208 | <code>        &quot;jsesc&quot;: &quot;bin/jsesc&quot;</code> | jsesc: Dependency requirement or executable metadata named jsesc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2209 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2210 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2211 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2212 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2213 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2214 | <code>    &quot;node_modules/json5&quot;: {</code> | node_modules/json5: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2215 | <code>      &quot;version&quot;: &quot;2.2.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2216 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/json5/-/json5-2.2.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2217 | <code>      &quot;integrity&quot;: &quot;sha512-XmOWe7eyHYH14cLdVPoyg+GOH3rYX++KpzrylJwSW98t3Nk+U8XOl8FWKOgwtzdb8lXGf6zYwDUzeHMWfxasyg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2218 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2219 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2220 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2221 | <code>        &quot;json5&quot;: &quot;lib/cli.js&quot;</code> | json5: Dependency requirement or executable metadata named json5. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2222 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2223 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2224 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2225 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2226 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2227 | <code>    &quot;node_modules/loupe&quot;: {</code> | node_modules/loupe: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2228 | <code>      &quot;version&quot;: &quot;3.2.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2229 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/loupe/-/loupe-3.2.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2230 | <code>      &quot;integrity&quot;: &quot;sha512-CdzqowRJCeLU72bHvWqwRBBlLcMEtIvGrlvef74kMnV2AolS9Y8xUv1I0U/MNAWMhBlKIoyuEgoJ0t/bbwHbLQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2231 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2232 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2233 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2234 | <code>    &quot;node_modules/lru-cache&quot;: {</code> | node_modules/lru-cache: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2235 | <code>      &quot;version&quot;: &quot;5.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2236 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/lru-cache/-/lru-cache-5.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2237 | <code>      &quot;integrity&quot;: &quot;sha512-KpNARQA3Iwv+jTA0utUVVbrh+Jlrr1Fv0e56GGzAFOXN7dk/FviaDW8LHmK52DlcH4WP2n6gI8vN1aesBFgo9w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2238 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2239 | <code>      &quot;license&quot;: &quot;ISC&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2240 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2241 | <code>        &quot;yallist&quot;: &quot;^3.0.2&quot;</code> | yallist: Dependency requirement or executable metadata named yallist. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2242 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2243 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2244 | <code>    &quot;node_modules/lz-string&quot;: {</code> | node_modules/lz-string: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2245 | <code>      &quot;version&quot;: &quot;1.5.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2246 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/lz-string/-/lz-string-1.5.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2247 | <code>      &quot;integrity&quot;: &quot;sha512-h5bgJWpxJNswbU7qCrV0tIKQCaS3blPDrqKWx+QxzuzL1zGUzij9XCWLrSLsJPu5t+eWA/ycetzYAO5IOMcWAQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2248 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2249 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2250 | <code>      &quot;peer&quot;: true,</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 2251 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2252 | <code>        &quot;lz-string&quot;: &quot;bin/bin.js&quot;</code> | lz-string: Dependency requirement or executable metadata named lz-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2253 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2254 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2255 | <code>    &quot;node_modules/magic-string&quot;: {</code> | node_modules/magic-string: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2256 | <code>      &quot;version&quot;: &quot;0.30.21&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2257 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/magic-string/-/magic-string-0.30.21.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2258 | <code>      &quot;integrity&quot;: &quot;sha512-vd2F4YUyEXKGcLHoq+TEyCjxueSeHnFxyyjNp80yg0XV4vUhnDer/lvvlqM/arB5bXQN5K2/3oinyCRyx8T2CQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2259 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2260 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2261 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2262 | <code>        &quot;@jridgewell/sourcemap-codec&quot;: &quot;^1.5.5&quot;</code> | @jridgewell/sourcemap-codec: Dependency requirement or executable metadata named @jridgewell/sourcemap-codec. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2263 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2264 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2265 | <code>    &quot;node_modules/min-indent&quot;: {</code> | node_modules/min-indent: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2266 | <code>      &quot;version&quot;: &quot;1.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2267 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/min-indent/-/min-indent-1.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2268 | <code>      &quot;integrity&quot;: &quot;sha512-I9jwMn07Sy/IwOj3zVkVik2JTvgpaykDZEigL6Rx6N9LbMywwUSMtxET+7lVoDLLd3O3IXwJwvuuns8UB/HeAg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2269 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2270 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2271 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2272 | <code>        &quot;node&quot;: &quot;&gt;=4&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2273 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2274 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2275 | <code>    &quot;node_modules/ms&quot;: {</code> | node_modules/ms: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2276 | <code>      &quot;version&quot;: &quot;2.1.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2277 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/ms/-/ms-2.1.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2278 | <code>      &quot;integrity&quot;: &quot;sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2279 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2280 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2281 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2282 | <code>    &quot;node_modules/nanoid&quot;: {</code> | node_modules/nanoid: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2283 | <code>      &quot;version&quot;: &quot;3.3.20&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2284 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/nanoid/-/nanoid-3.3.20.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2285 | <code>      &quot;integrity&quot;: &quot;sha512-uKdg2G3GNCKQn9byYOpxbGqrT2fGO5KRt5J/8b3pok8rT6qxGWF6hxMyJiEYtAf+FVyYuD9hRaDqX5uPFYJ4ZQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2286 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2287 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2288 | <code>        {</code> | Open a JSON object (named fields). |
| 2289 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2290 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/ai&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2291 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2292 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2293 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2294 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2295 | <code>        &quot;nanoid&quot;: &quot;bin/nanoid.cjs&quot;</code> | nanoid: Dependency requirement or executable metadata named nanoid. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2296 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2297 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2298 | <code>        &quot;node&quot;: &quot;^10 &#124;&#124; ^12 &#124;&#124; ^13.7 &#124;&#124; ^14 &#124;&#124; &gt;=15.0.1&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2299 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2300 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2301 | <code>    &quot;node_modules/node-releases&quot;: {</code> | node_modules/node-releases: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2302 | <code>      &quot;version&quot;: &quot;2.0.58&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2303 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/node-releases/-/node-releases-2.0.58.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2304 | <code>      &quot;integrity&quot;: &quot;sha512-BdiKAgbfRlvfMq/XzO/AF9NPmaA8a+YpLAyAFTVFBj3gARrAIfWvNq7Q7NE4se3KgFu0KkrvQMxTS0XVnsGzHg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2305 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2306 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2307 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2308 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2309 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2310 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2311 | <code>    &quot;node_modules/nwsapi&quot;: {</code> | node_modules/nwsapi: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2312 | <code>      &quot;version&quot;: &quot;2.2.28&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2313 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/nwsapi/-/nwsapi-2.2.28.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2314 | <code>      &quot;integrity&quot;: &quot;sha512-IlVB7OS7qrOsVYlpnFIkETjMwT9jwvmocJmmM+GZU/PAB3uGi9Ezd7vcWhWBUnSc0ya4ppmQITOyP1ez9gg8cg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2315 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2316 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2317 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2318 | <code>    &quot;node_modules/parse5&quot;: {</code> | node_modules/parse5: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2319 | <code>      &quot;version&quot;: &quot;7.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2320 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/parse5/-/parse5-7.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2321 | <code>      &quot;integrity&quot;: &quot;sha512-IInvU7fabl34qmi9gY8XOVxhYyMyuH2xUNpb2q8/Y+7552KlejkRvqvD19nMoUW/uQGGbqNpA6Tufu5FL5BZgw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2322 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2323 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2324 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2325 | <code>        &quot;entities&quot;: &quot;^6.0.0&quot;</code> | entities: Dependency requirement or executable metadata named entities. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2326 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2327 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2328 | <code>        &quot;url&quot;: &quot;https://github.com/inikulin/parse5?sponsor=1&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2329 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2330 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2331 | <code>    &quot;node_modules/pathe&quot;: {</code> | node_modules/pathe: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2332 | <code>      &quot;version&quot;: &quot;2.0.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2333 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/pathe/-/pathe-2.0.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2334 | <code>      &quot;integrity&quot;: &quot;sha512-WUjGcAqP1gQacoQe+OBJsFA7Ld4DyXuUIjZ5cc75cLHvJ7dtNsTugphxIADwspS+AraAUePCKrSVtPLFj/F88w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2335 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2336 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2337 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2338 | <code>    &quot;node_modules/pathval&quot;: {</code> | node_modules/pathval: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2339 | <code>      &quot;version&quot;: &quot;2.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2340 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/pathval/-/pathval-2.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2341 | <code>      &quot;integrity&quot;: &quot;sha512-//nshmD55c46FuFw26xV/xFAaB5HF9Xdap7HJBBnrKdAd6/GxDBaNA1870O79+9ueg61cZLSVc+OaFlfmObYVQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2342 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2343 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2344 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2345 | <code>        &quot;node&quot;: &quot;&gt;= 14.16&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2346 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2347 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2348 | <code>    &quot;node_modules/picocolors&quot;: {</code> | node_modules/picocolors: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2349 | <code>      &quot;version&quot;: &quot;1.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2350 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2351 | <code>      &quot;integrity&quot;: &quot;sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2352 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2353 | <code>      &quot;license&quot;: &quot;ISC&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2354 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2355 | <code>    &quot;node_modules/picomatch&quot;: {</code> | node_modules/picomatch: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2356 | <code>      &quot;version&quot;: &quot;4.0.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2357 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/picomatch/-/picomatch-4.0.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2358 | <code>      &quot;integrity&quot;: &quot;sha512-qcJu88Q2IWqJsDD529JKMdwGm/dvInW4HvQnRwiH9JtihJvzGOscDtHE3x1pBKeUOTysQ8kVmLnJ2kJu7yhcGA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2359 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2360 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2361 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2362 | <code>        &quot;node&quot;: &quot;&gt;=12&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2363 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2364 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2365 | <code>        &quot;url&quot;: &quot;https://github.com/sponsors/jonschlinkert&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2366 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2367 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2368 | <code>    &quot;node_modules/postcss&quot;: {</code> | node_modules/postcss: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2369 | <code>      &quot;version&quot;: &quot;8.5.29&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2370 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/postcss/-/postcss-8.5.29.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2371 | <code>      &quot;integrity&quot;: &quot;sha512-49cGhUbXj8Qenv0iTMxA1cFBzxXoctpC9Ujd77t1WcbJIr6nF/eI7g/8MgxrYldFRuAXvja7xQRwavoW7kgrxQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2372 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2373 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2374 | <code>        {</code> | Open a JSON object (named fields). |
| 2375 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2376 | <code>          &quot;url&quot;: &quot;https://opencollective.com/postcss/&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2377 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2378 | <code>        {</code> | Open a JSON object (named fields). |
| 2379 | <code>          &quot;type&quot;: &quot;tidelift&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2380 | <code>          &quot;url&quot;: &quot;https://tidelift.com/funding/github/npm/postcss&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2381 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2382 | <code>        {</code> | Open a JSON object (named fields). |
| 2383 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2384 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/ai&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2385 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2386 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2387 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2388 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2389 | <code>        &quot;nanoid&quot;: &quot;^3.3.19&quot;,</code> | nanoid: Dependency requirement or executable metadata named nanoid. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2390 | <code>        &quot;picocolors&quot;: &quot;^1.1.1&quot;,</code> | picocolors: Dependency requirement or executable metadata named picocolors. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2391 | <code>        &quot;source-map-js&quot;: &quot;^1.2.2&quot;</code> | source-map-js: Dependency requirement or executable metadata named source-map-js. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2392 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2393 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2394 | <code>        &quot;node&quot;: &quot;^10 &#124;&#124; ^12 &#124;&#124; &gt;=14&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2395 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2396 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2397 | <code>    &quot;node_modules/pretty-format&quot;: {</code> | node_modules/pretty-format: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2398 | <code>      &quot;version&quot;: &quot;27.5.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2399 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/pretty-format/-/pretty-format-27.5.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2400 | <code>      &quot;integrity&quot;: &quot;sha512-Qb1gy5OrP5+zDf2Bvnzdl3jsTf1qXVMazbvCoKhtKqVs4/YK4ozX4gKQJJVyNe+cajNPn0KoC0MC3FUmaHWEmQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2401 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2402 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2403 | <code>      &quot;peer&quot;: true,</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 2404 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2405 | <code>        &quot;ansi-regex&quot;: &quot;^5.0.1&quot;,</code> | ansi-regex: Dependency requirement or executable metadata named ansi-regex. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2406 | <code>        &quot;ansi-styles&quot;: &quot;^5.0.0&quot;,</code> | ansi-styles: Dependency requirement or executable metadata named ansi-styles. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2407 | <code>        &quot;react-is&quot;: &quot;^17.0.1&quot;</code> | react-is: Dependency requirement or executable metadata named react-is. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2408 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2409 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2410 | <code>        &quot;node&quot;: &quot;^10.13.0 &#124;&#124; ^12.13.0 &#124;&#124; ^14.15.0 &#124;&#124; &gt;=15.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2411 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2412 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2413 | <code>    &quot;node_modules/punycode&quot;: {</code> | node_modules/punycode: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2414 | <code>      &quot;version&quot;: &quot;2.3.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2415 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2416 | <code>      &quot;integrity&quot;: &quot;sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2417 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2418 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2419 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2420 | <code>        &quot;node&quot;: &quot;&gt;=6&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2421 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2422 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2423 | <code>    &quot;node_modules/react&quot;: {</code> | node_modules/react: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2424 | <code>      &quot;version&quot;: &quot;19.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2425 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/react/-/react-19.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2426 | <code>      &quot;integrity&quot;: &quot;sha512-E8LUcbtBWt20bbl2YoHfx4ZDBdxVTfOKtCZn9cDSJ4l6/nuoApcpIBcj47t2wZoVX8g2ZHuMHbiShgCR1T5Sog==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2427 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2428 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2429 | <code>        &quot;node&quot;: &quot;&gt;=0.10.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2430 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2431 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2432 | <code>    &quot;node_modules/react-dom&quot;: {</code> | node_modules/react-dom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2433 | <code>      &quot;version&quot;: &quot;19.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2434 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/react-dom/-/react-dom-19.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2435 | <code>      &quot;integrity&quot;: &quot;sha512-JDk8dgif51OjFoDE70+OT9ICyYr+69HlmihNwp1+Nsfbna3t5sIiCa9ZJktDmQ4/1b/rn26hIAR2uYXDMr5r0Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2436 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2437 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2438 | <code>        &quot;scheduler&quot;: &quot;^0.28.0&quot;</code> | scheduler: Dependency requirement or executable metadata named scheduler. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2439 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2440 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2441 | <code>        &quot;react&quot;: &quot;^19.3.0&quot;</code> | react: Dependency requirement or executable metadata named react. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2442 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2443 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2444 | <code>    &quot;node_modules/react-is&quot;: {</code> | node_modules/react-is: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2445 | <code>      &quot;version&quot;: &quot;17.0.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2446 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/react-is/-/react-is-17.0.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2447 | <code>      &quot;integrity&quot;: &quot;sha512-w2GsyukL62IJnlaff/nRegPQR94C/XXamvMWmSHRJ4y7Ts/4ocGRmTHvOs8PSE6pB3dWOrD/nueuU5sduBsQ4w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2448 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2449 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2450 | <code>      &quot;peer&quot;: true</code> | peer: True indicates resolution tied to a peer dependency relationship. |
| 2451 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2452 | <code>    &quot;node_modules/react-refresh&quot;: {</code> | node_modules/react-refresh: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2453 | <code>      &quot;version&quot;: &quot;0.17.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2454 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/react-refresh/-/react-refresh-0.17.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2455 | <code>      &quot;integrity&quot;: &quot;sha512-z6F7K9bV85EfseRCp2bzrpyQ0Gkw1uLoCel9XBVWPg/TjRj94SkJzUTGfOa4bs7iJvBWtQG0Wq7wnI0syw3EBQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2456 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2457 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2458 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2459 | <code>        &quot;node&quot;: &quot;&gt;=0.10.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2460 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2461 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2462 | <code>    &quot;node_modules/redent&quot;: {</code> | node_modules/redent: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2463 | <code>      &quot;version&quot;: &quot;3.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2464 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/redent/-/redent-3.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2465 | <code>      &quot;integrity&quot;: &quot;sha512-6tDA8g98We0zd0GvVeMT9arEOnTw9qM03L9cJXaCjrip1OO764RDBLBfrB4cwzNGDj5OA5ioymC9GkizgWJDUg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2466 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2467 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2468 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2469 | <code>        &quot;indent-string&quot;: &quot;^4.0.0&quot;,</code> | indent-string: Dependency requirement or executable metadata named indent-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2470 | <code>        &quot;strip-indent&quot;: &quot;^3.0.0&quot;</code> | strip-indent: Dependency requirement or executable metadata named strip-indent. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2471 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2472 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2473 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2474 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2475 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2476 | <code>    &quot;node_modules/rollup&quot;: {</code> | node_modules/rollup: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2477 | <code>      &quot;version&quot;: &quot;4.64.5&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2478 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/rollup/-/rollup-4.64.5.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2479 | <code>      &quot;integrity&quot;: &quot;sha512-EAP5ZHcz2ijbgCWwPkpI7zh6bfsri2Ez5FtCy2dCp1k62duXzfG7DLGGh7RU2QQXWwavT+u4qpvDF/TWOiiGTw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2480 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2481 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2482 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2483 | <code>        &quot;@types/estree&quot;: &quot;1.0.9&quot;</code> | @types/estree: Dependency requirement or executable metadata named @types/estree. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2484 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2485 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2486 | <code>        &quot;rollup&quot;: &quot;dist/bin/rollup&quot;</code> | rollup: Dependency requirement or executable metadata named rollup. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2487 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2488 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2489 | <code>        &quot;node&quot;: &quot;&gt;=18.0.0&quot;,</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2490 | <code>        &quot;npm&quot;: &quot;&gt;=8.0.0&quot;</code> | npm: npm version constraint inside engines. |
| 2491 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2492 | <code>      &quot;optionalDependencies&quot;: {</code> | optionalDependencies: Dependencies whose absence may be tolerated, often platform-specific binaries. |
| 2493 | <code>        &quot;@napi-rs/lzma-linux-x64-gnu&quot;: &quot;1.5.1&quot;,</code> | @napi-rs/lzma-linux-x64-gnu: Dependency requirement or executable metadata named @napi-rs/lzma-linux-x64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2494 | <code>        &quot;@rollup/rollup-android-arm-eabi&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-android-arm-eabi: Dependency requirement or executable metadata named @rollup/rollup-android-arm-eabi. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2495 | <code>        &quot;@rollup/rollup-android-arm64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-android-arm64: Dependency requirement or executable metadata named @rollup/rollup-android-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2496 | <code>        &quot;@rollup/rollup-darwin-arm64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-darwin-arm64: Dependency requirement or executable metadata named @rollup/rollup-darwin-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2497 | <code>        &quot;@rollup/rollup-darwin-x64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-darwin-x64: Dependency requirement or executable metadata named @rollup/rollup-darwin-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2498 | <code>        &quot;@rollup/rollup-freebsd-arm64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-freebsd-arm64: Dependency requirement or executable metadata named @rollup/rollup-freebsd-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2499 | <code>        &quot;@rollup/rollup-freebsd-x64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-freebsd-x64: Dependency requirement or executable metadata named @rollup/rollup-freebsd-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2500 | <code>        &quot;@rollup/rollup-linux-arm-gnueabihf&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-arm-gnueabihf: Dependency requirement or executable metadata named @rollup/rollup-linux-arm-gnueabihf. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2501 | <code>        &quot;@rollup/rollup-linux-arm-musleabihf&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-arm-musleabihf: Dependency requirement or executable metadata named @rollup/rollup-linux-arm-musleabihf. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2502 | <code>        &quot;@rollup/rollup-linux-arm64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-arm64-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-arm64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2503 | <code>        &quot;@rollup/rollup-linux-arm64-musl&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-arm64-musl: Dependency requirement or executable metadata named @rollup/rollup-linux-arm64-musl. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2504 | <code>        &quot;@rollup/rollup-linux-loong64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-loong64-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-loong64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2505 | <code>        &quot;@rollup/rollup-linux-loong64-musl&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-loong64-musl: Dependency requirement or executable metadata named @rollup/rollup-linux-loong64-musl. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2506 | <code>        &quot;@rollup/rollup-linux-ppc64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-ppc64-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-ppc64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2507 | <code>        &quot;@rollup/rollup-linux-ppc64-musl&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-ppc64-musl: Dependency requirement or executable metadata named @rollup/rollup-linux-ppc64-musl. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2508 | <code>        &quot;@rollup/rollup-linux-riscv64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-riscv64-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-riscv64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2509 | <code>        &quot;@rollup/rollup-linux-riscv64-musl&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-riscv64-musl: Dependency requirement or executable metadata named @rollup/rollup-linux-riscv64-musl. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2510 | <code>        &quot;@rollup/rollup-linux-s390x-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-s390x-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-s390x-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2511 | <code>        &quot;@rollup/rollup-linux-x64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-x64-gnu: Dependency requirement or executable metadata named @rollup/rollup-linux-x64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2512 | <code>        &quot;@rollup/rollup-linux-x64-musl&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-linux-x64-musl: Dependency requirement or executable metadata named @rollup/rollup-linux-x64-musl. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2513 | <code>        &quot;@rollup/rollup-openbsd-x64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-openbsd-x64: Dependency requirement or executable metadata named @rollup/rollup-openbsd-x64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2514 | <code>        &quot;@rollup/rollup-openharmony-arm64&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-openharmony-arm64: Dependency requirement or executable metadata named @rollup/rollup-openharmony-arm64. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2515 | <code>        &quot;@rollup/rollup-win32-arm64-msvc&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-win32-arm64-msvc: Dependency requirement or executable metadata named @rollup/rollup-win32-arm64-msvc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2516 | <code>        &quot;@rollup/rollup-win32-ia32-msvc&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-win32-ia32-msvc: Dependency requirement or executable metadata named @rollup/rollup-win32-ia32-msvc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2517 | <code>        &quot;@rollup/rollup-win32-x64-gnu&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-win32-x64-gnu: Dependency requirement or executable metadata named @rollup/rollup-win32-x64-gnu. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2518 | <code>        &quot;@rollup/rollup-win32-x64-msvc&quot;: &quot;4.64.5&quot;,</code> | @rollup/rollup-win32-x64-msvc: Dependency requirement or executable metadata named @rollup/rollup-win32-x64-msvc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2519 | <code>        &quot;fsevents&quot;: &quot;~2.3.2&quot;</code> | fsevents: Dependency requirement or executable metadata named fsevents. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2520 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2521 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2522 | <code>    &quot;node_modules/rrweb-cssom&quot;: {</code> | node_modules/rrweb-cssom: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2523 | <code>      &quot;version&quot;: &quot;0.8.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2524 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/rrweb-cssom/-/rrweb-cssom-0.8.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2525 | <code>      &quot;integrity&quot;: &quot;sha512-guoltQEx+9aMf2gDZ0s62EcV8lsXR+0w8915TC3ITdn2YueuNjdAYh/levpU9nFaoChh9RUS5ZdQMrKfVEN9tw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2526 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2527 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2528 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2529 | <code>    &quot;node_modules/safer-buffer&quot;: {</code> | node_modules/safer-buffer: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2530 | <code>      &quot;version&quot;: &quot;2.1.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2531 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/safer-buffer/-/safer-buffer-2.1.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2532 | <code>      &quot;integrity&quot;: &quot;sha512-YZo3K82SD7Riyi0E1EQPojLz7kpepnSQI9IyPbHHg1XXXevb5dJI7tpyN2ADxGcQbHG7vcyRHk0cbwqcQriUtg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2533 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2534 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2535 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2536 | <code>    &quot;node_modules/saxes&quot;: {</code> | node_modules/saxes: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2537 | <code>      &quot;version&quot;: &quot;6.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2538 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/saxes/-/saxes-6.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2539 | <code>      &quot;integrity&quot;: &quot;sha512-xAg7SOnEhrm5zI3puOOKyy1OMcMlIJZYNJY7xLBwSze0UjhPLnWfj2GF2EpT0jmzaJKIWKHLsaSSajf35bcYnA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2540 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2541 | <code>      &quot;license&quot;: &quot;ISC&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2542 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2543 | <code>        &quot;xmlchars&quot;: &quot;^2.2.0&quot;</code> | xmlchars: Dependency requirement or executable metadata named xmlchars. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2544 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2545 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2546 | <code>        &quot;node&quot;: &quot;&gt;=v12.22.7&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2547 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2548 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2549 | <code>    &quot;node_modules/scheduler&quot;: {</code> | node_modules/scheduler: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2550 | <code>      &quot;version&quot;: &quot;0.28.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2551 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/scheduler/-/scheduler-0.28.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2552 | <code>      &quot;integrity&quot;: &quot;sha512-juorfCmIkIw8tT+p5BXSm6PJjQF/ycEYmKyzURCIt/RaZIhL+PulbQ9Yu2z1HdOJDdqDTlxA1+xKBmHXJsczAw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2553 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2554 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2555 | <code>    &quot;node_modules/semver&quot;: {</code> | node_modules/semver: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2556 | <code>      &quot;version&quot;: &quot;6.3.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2557 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/semver/-/semver-6.3.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2558 | <code>      &quot;integrity&quot;: &quot;sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2559 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2560 | <code>      &quot;license&quot;: &quot;ISC&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2561 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2562 | <code>        &quot;semver&quot;: &quot;bin/semver.js&quot;</code> | semver: Dependency requirement or executable metadata named semver. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2563 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2564 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2565 | <code>    &quot;node_modules/siginfo&quot;: {</code> | node_modules/siginfo: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2566 | <code>      &quot;version&quot;: &quot;2.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2567 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/siginfo/-/siginfo-2.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2568 | <code>      &quot;integrity&quot;: &quot;sha512-ybx0WO1/8bSBLEWXZvEd7gMW3Sn3JFlW3TvX1nREbDLRNQNaeNN8WK0meBwPdAaOI7TtRRRJn/Es1zhrrCHu7g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2569 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2570 | <code>      &quot;license&quot;: &quot;ISC&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2571 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2572 | <code>    &quot;node_modules/source-map-js&quot;: {</code> | node_modules/source-map-js: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2573 | <code>      &quot;version&quot;: &quot;1.2.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2574 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2575 | <code>      &quot;integrity&quot;: &quot;sha512-KGj/8Y43x35aZVDtt+J4mK1hoLGHULMYfSkODJNQjNDC3oW1PqPoxMwo0pLUsWM/UEGzON/NxeHywEfNXNP3Vw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2576 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2577 | <code>      &quot;license&quot;: &quot;BSD-3-Clause&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2578 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2579 | <code>        &quot;node&quot;: &quot;&gt;=0.10.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2580 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2581 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2582 | <code>    &quot;node_modules/stackback&quot;: {</code> | node_modules/stackback: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2583 | <code>      &quot;version&quot;: &quot;0.0.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2584 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/stackback/-/stackback-0.0.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2585 | <code>      &quot;integrity&quot;: &quot;sha512-1XMJE5fQo1jGH6Y/7ebnwPOBEkIEnT4QF32d5R1+VXdXveM0IBMJt8zfaxX1P3QhVwrYe+576+jkANtSS2mBbw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2586 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2587 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2588 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2589 | <code>    &quot;node_modules/std-env&quot;: {</code> | node_modules/std-env: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2590 | <code>      &quot;version&quot;: &quot;3.10.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2591 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/std-env/-/std-env-3.10.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2592 | <code>      &quot;integrity&quot;: &quot;sha512-5GS12FdOZNliM5mAOxFRg7Ir0pWz8MdpYm6AY6VPkGpbA7ZzmbzNcBJQ0GPvvyWgcY7QAhCgf9Uy89I03faLkg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2593 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2594 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2595 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2596 | <code>    &quot;node_modules/strip-indent&quot;: {</code> | node_modules/strip-indent: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2597 | <code>      &quot;version&quot;: &quot;3.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2598 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/strip-indent/-/strip-indent-3.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2599 | <code>      &quot;integrity&quot;: &quot;sha512-laJTa3Jb+VQpaC6DseHhF7dXVqHTfJPCRDaEbid/drOhgitgYku/letMUqOXFoWV0zIIUbjpdH2t+tYj4bQMRQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2600 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2601 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2602 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2603 | <code>        &quot;min-indent&quot;: &quot;^1.0.0&quot;</code> | min-indent: Dependency requirement or executable metadata named min-indent. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2604 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2605 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2606 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2607 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2608 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2609 | <code>    &quot;node_modules/strip-literal&quot;: {</code> | node_modules/strip-literal: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2610 | <code>      &quot;version&quot;: &quot;3.1.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2611 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/strip-literal/-/strip-literal-3.1.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2612 | <code>      &quot;integrity&quot;: &quot;sha512-8r3mkIM/2+PpjHoOtiAW8Rg3jJLHaV7xPwG+YRGrv6FP0wwk/toTpATxWYOW0BKdWwl82VT2tFYi5DlROa0Mxg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2613 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2614 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2615 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2616 | <code>        &quot;js-tokens&quot;: &quot;^9.0.1&quot;</code> | js-tokens: Dependency requirement or executable metadata named js-tokens. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2617 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2618 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2619 | <code>        &quot;url&quot;: &quot;https://github.com/sponsors/antfu&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2620 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2621 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2622 | <code>    &quot;node_modules/strip-literal/node_modules/js-tokens&quot;: {</code> | node_modules/strip-literal/node_modules/js-tokens: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2623 | <code>      &quot;version&quot;: &quot;9.0.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2624 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/js-tokens/-/js-tokens-9.0.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2625 | <code>      &quot;integrity&quot;: &quot;sha512-mxa9E9ITFOt0ban3j6L5MpjwegGz6lBQmM1IJkWeBZGcMxto50+eWdjC/52xDbS2vy0k7vIMK0Fe2wfL9OQSpQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2626 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2627 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2628 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2629 | <code>    &quot;node_modules/symbol-tree&quot;: {</code> | node_modules/symbol-tree: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2630 | <code>      &quot;version&quot;: &quot;3.2.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2631 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/symbol-tree/-/symbol-tree-3.2.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2632 | <code>      &quot;integrity&quot;: &quot;sha512-9QNk5KwDF+Bvz+PyObkmSYjI5ksVUYtjW7AU22r2NKcfLJcXp96hkDWU3+XndOsUb+AQ9QhfzfCT2O+CNWT5Tw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2633 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2634 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2635 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2636 | <code>    &quot;node_modules/tinybench&quot;: {</code> | node_modules/tinybench: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2637 | <code>      &quot;version&quot;: &quot;2.9.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2638 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinybench/-/tinybench-2.9.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2639 | <code>      &quot;integrity&quot;: &quot;sha512-0+DUvqWMValLmha6lr4kD8iAMK1HzV0/aKnCtWb9v9641TnP/MFb7Pc2bxoxQjTXAErryXVgUOfv2YqNllqGeg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2640 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2641 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2642 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2643 | <code>    &quot;node_modules/tinyexec&quot;: {</code> | node_modules/tinyexec: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2644 | <code>      &quot;version&quot;: &quot;0.3.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2645 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinyexec/-/tinyexec-0.3.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2646 | <code>      &quot;integrity&quot;: &quot;sha512-KQQR9yN7R5+OSwaK0XQoj22pwHoTlgYqmUscPYoknOoWCWfj/5/ABTMRi69FrKU5ffPVh5QcFikpWJI/P1ocHA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2647 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2648 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2649 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2650 | <code>    &quot;node_modules/tinyglobby&quot;: {</code> | node_modules/tinyglobby: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2651 | <code>      &quot;version&quot;: &quot;0.2.17&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2652 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.17.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2653 | <code>      &quot;integrity&quot;: &quot;sha512-wXR/dYpcqKmfWpEdZjiKJOwCNFndD0DMnrW/cYjVGttEkBfVgcLFHoNrlj47mjOVic9yyNu65alsgF4NQyTa2g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2654 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2655 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2656 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2657 | <code>        &quot;fdir&quot;: &quot;^6.5.0&quot;,</code> | fdir: Dependency requirement or executable metadata named fdir. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2658 | <code>        &quot;picomatch&quot;: &quot;^4.0.4&quot;</code> | picomatch: Dependency requirement or executable metadata named picomatch. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2659 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2660 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2661 | <code>        &quot;node&quot;: &quot;&gt;=12.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2662 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2663 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2664 | <code>        &quot;url&quot;: &quot;https://github.com/sponsors/SuperchupuDev&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2665 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2666 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2667 | <code>    &quot;node_modules/tinypool&quot;: {</code> | node_modules/tinypool: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2668 | <code>      &quot;version&quot;: &quot;1.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2669 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinypool/-/tinypool-1.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2670 | <code>      &quot;integrity&quot;: &quot;sha512-Zba82s87IFq9A9XmjiX5uZA/ARWDrB03OHlq+Vw1fSdt0I+4/Kutwy8BP4Y/y/aORMo61FQ0vIb5j44vSo5Pkg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2671 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2672 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2673 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2674 | <code>        &quot;node&quot;: &quot;^18.0.0 &#124;&#124; &gt;=20.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2675 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2676 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2677 | <code>    &quot;node_modules/tinyrainbow&quot;: {</code> | node_modules/tinyrainbow: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2678 | <code>      &quot;version&quot;: &quot;2.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2679 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinyrainbow/-/tinyrainbow-2.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2680 | <code>      &quot;integrity&quot;: &quot;sha512-op4nsTR47R6p0vMUUoYl/a+ljLFVtlfaXkLQmqfLR1qHma1h/ysYk4hEXZ880bf2CYgTskvTa/e196Vd5dDQXw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2681 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2682 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2683 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2684 | <code>        &quot;node&quot;: &quot;&gt;=14.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2685 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2686 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2687 | <code>    &quot;node_modules/tinyspy&quot;: {</code> | node_modules/tinyspy: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2688 | <code>      &quot;version&quot;: &quot;4.0.6&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2689 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tinyspy/-/tinyspy-4.0.6.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2690 | <code>      &quot;integrity&quot;: &quot;sha512-u8KszXvGfU68hVcZpRHKG28T0krMuv2G5nDhiHaMLen/gIuFEgIJhaJuO69qjnXg5paSrbPMFfx3brNuN8eVSg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2691 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2692 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2693 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2694 | <code>        &quot;node&quot;: &quot;&gt;=14.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2695 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2696 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2697 | <code>    &quot;node_modules/tldts&quot;: {</code> | node_modules/tldts: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2698 | <code>      &quot;version&quot;: &quot;6.1.86&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2699 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tldts/-/tldts-6.1.86.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2700 | <code>      &quot;integrity&quot;: &quot;sha512-WMi/OQ2axVTf/ykqCQgXiIct+mSQDFdH2fkwhPwgEwvJ1kSzZRiinb0zF2Xb8u4+OqPChmyI6MEu4EezNJz+FQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2701 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2702 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2703 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2704 | <code>        &quot;tldts-core&quot;: &quot;^6.1.86&quot;</code> | tldts-core: Dependency requirement or executable metadata named tldts-core. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2705 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2706 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2707 | <code>        &quot;tldts&quot;: &quot;bin/cli.js&quot;</code> | tldts: Dependency requirement or executable metadata named tldts. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2708 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2709 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2710 | <code>    &quot;node_modules/tldts-core&quot;: {</code> | node_modules/tldts-core: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2711 | <code>      &quot;version&quot;: &quot;6.1.86&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2712 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tldts-core/-/tldts-core-6.1.86.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2713 | <code>      &quot;integrity&quot;: &quot;sha512-Je6p7pkk+KMzMv2XXKmAE3McmolOQFdxkKw0R8EYNr7sELW46JqnNeTX8ybPiQgvg1ymCoF8LXs5fzFaZvJPTA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2714 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2715 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2716 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2717 | <code>    &quot;node_modules/tough-cookie&quot;: {</code> | node_modules/tough-cookie: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2718 | <code>      &quot;version&quot;: &quot;5.1.2&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2719 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tough-cookie/-/tough-cookie-5.1.2.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2720 | <code>      &quot;integrity&quot;: &quot;sha512-FVDYdxtnj0G6Qm/DhNPSb8Ju59ULcup3tuJxkFb5K8Bv2pUXILbf0xZWU8PX8Ov19OXljbUyveOFwRMwkXzO+A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2721 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2722 | <code>      &quot;license&quot;: &quot;BSD-3-Clause&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2723 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2724 | <code>        &quot;tldts&quot;: &quot;^6.1.32&quot;</code> | tldts: Dependency requirement or executable metadata named tldts. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2725 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2726 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2727 | <code>        &quot;node&quot;: &quot;&gt;=16&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2728 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2729 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2730 | <code>    &quot;node_modules/tr46&quot;: {</code> | node_modules/tr46: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2731 | <code>      &quot;version&quot;: &quot;5.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2732 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/tr46/-/tr46-5.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2733 | <code>      &quot;integrity&quot;: &quot;sha512-hdF5ZgjTqgAntKkklYw0R03MG2x/bSzTtkxmIRw/sTNV8YXsCJ1tfLAX23lhxhHJlEf3CRCOCGGWw3vI3GaSPw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2734 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2735 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2736 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2737 | <code>        &quot;punycode&quot;: &quot;^2.3.1&quot;</code> | punycode: Dependency requirement or executable metadata named punycode. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2738 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2739 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2740 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2741 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2742 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2743 | <code>    &quot;node_modules/typescript&quot;: {</code> | node_modules/typescript: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2744 | <code>      &quot;version&quot;: &quot;5.9.3&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2745 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/typescript/-/typescript-5.9.3.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2746 | <code>      &quot;integrity&quot;: &quot;sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2747 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2748 | <code>      &quot;license&quot;: &quot;Apache-2.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2749 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2750 | <code>        &quot;tsc&quot;: &quot;bin/tsc&quot;,</code> | tsc: Dependency requirement or executable metadata named tsc. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2751 | <code>        &quot;tsserver&quot;: &quot;bin/tsserver&quot;</code> | tsserver: Dependency requirement or executable metadata named tsserver. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2752 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2753 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2754 | <code>        &quot;node&quot;: &quot;&gt;=14.17&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2755 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2756 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2757 | <code>    &quot;node_modules/update-browserslist-db&quot;: {</code> | node_modules/update-browserslist-db: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2758 | <code>      &quot;version&quot;: &quot;1.3.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2759 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.3.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2760 | <code>      &quot;integrity&quot;: &quot;sha512-t8wonIOdQyOjtPd2VktlBu6QjTVTks6v8bSi7kd0r2Vll8TK1JYDZtRRdbmCHOAMphkZgrzK+L+vXK4pyZ8t4A==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2761 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2762 | <code>      &quot;funding&quot;: [</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2763 | <code>        {</code> | Open a JSON object (named fields). |
| 2764 | <code>          &quot;type&quot;: &quot;opencollective&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2765 | <code>          &quot;url&quot;: &quot;https://opencollective.com/browserslist&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2766 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2767 | <code>        {</code> | Open a JSON object (named fields). |
| 2768 | <code>          &quot;type&quot;: &quot;tidelift&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2769 | <code>          &quot;url&quot;: &quot;https://tidelift.com/funding/github/npm/browserslist&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2770 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2771 | <code>        {</code> | Open a JSON object (named fields). |
| 2772 | <code>          &quot;type&quot;: &quot;github&quot;,</code> | type: Category of the surrounding metadata record, such as a funding service. |
| 2773 | <code>          &quot;url&quot;: &quot;https://github.com/sponsors/ai&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2774 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2775 | <code>      ],</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2776 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2777 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2778 | <code>        &quot;escalade&quot;: &quot;^3.2.0&quot;,</code> | escalade: Dependency requirement or executable metadata named escalade. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2779 | <code>        &quot;picocolors&quot;: &quot;^1.1.1&quot;</code> | picocolors: Dependency requirement or executable metadata named picocolors. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2780 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2781 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2782 | <code>        &quot;update-browserslist-db&quot;: &quot;cli.js&quot;</code> | update-browserslist-db: Dependency requirement or executable metadata named update-browserslist-db. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2783 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2784 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2785 | <code>        &quot;browserslist&quot;: &quot;&gt;= 4.21.0&quot;</code> | browserslist: Dependency requirement or executable metadata named browserslist. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2786 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2787 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2788 | <code>    &quot;node_modules/vite&quot;: {</code> | node_modules/vite: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2789 | <code>      &quot;version&quot;: &quot;6.4.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2790 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/vite/-/vite-6.4.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2791 | <code>      &quot;integrity&quot;: &quot;sha512-xGjU/SyjeNyb0E4KxXBvYz/1C+3JXuujvf2hXNOtnlcE+58o5ajd9N2/n2VhkiJvpCP2qQasnUpx5PXNeI+p1Q==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2792 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2793 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2794 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2795 | <code>        &quot;esbuild&quot;: &quot;^0.25.0&quot;,</code> | esbuild: Dependency requirement or executable metadata named esbuild. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2796 | <code>        &quot;fdir&quot;: &quot;^6.4.4&quot;,</code> | fdir: Dependency requirement or executable metadata named fdir. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2797 | <code>        &quot;picomatch&quot;: &quot;^4.0.2&quot;,</code> | picomatch: Dependency requirement or executable metadata named picomatch. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2798 | <code>        &quot;postcss&quot;: &quot;^8.5.3&quot;,</code> | postcss: Dependency requirement or executable metadata named postcss. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2799 | <code>        &quot;rollup&quot;: &quot;^4.34.9&quot;,</code> | rollup: Dependency requirement or executable metadata named rollup. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2800 | <code>        &quot;tinyglobby&quot;: &quot;^0.2.13&quot;</code> | tinyglobby: Dependency requirement or executable metadata named tinyglobby. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2801 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2802 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2803 | <code>        &quot;vite&quot;: &quot;bin/vite.js&quot;</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2804 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2805 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2806 | <code>        &quot;node&quot;: &quot;^18.0.0 &#124;&#124; ^20.0.0 &#124;&#124; &gt;=22.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2807 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2808 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2809 | <code>        &quot;url&quot;: &quot;https://github.com/vitejs/vite?sponsor=1&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2810 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2811 | <code>      &quot;optionalDependencies&quot;: {</code> | optionalDependencies: Dependencies whose absence may be tolerated, often platform-specific binaries. |
| 2812 | <code>        &quot;fsevents&quot;: &quot;~2.3.3&quot;</code> | fsevents: Dependency requirement or executable metadata named fsevents. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2813 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2814 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2815 | <code>        &quot;@types/node&quot;: &quot;^18.0.0 &#124;&#124; ^20.0.0 &#124;&#124; &gt;=22.0.0&quot;,</code> | @types/node: Dependency requirement or executable metadata named @types/node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2816 | <code>        &quot;jiti&quot;: &quot;&gt;=1.21.0&quot;,</code> | jiti: Dependency requirement or executable metadata named jiti. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2817 | <code>        &quot;less&quot;: &quot;*&quot;,</code> | less: Dependency requirement or executable metadata named less. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2818 | <code>        &quot;lightningcss&quot;: &quot;^1.21.0&quot;,</code> | lightningcss: Dependency requirement or executable metadata named lightningcss. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2819 | <code>        &quot;sass&quot;: &quot;*&quot;,</code> | sass: Dependency requirement or executable metadata named sass. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2820 | <code>        &quot;sass-embedded&quot;: &quot;*&quot;,</code> | sass-embedded: Dependency requirement or executable metadata named sass-embedded. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2821 | <code>        &quot;stylus&quot;: &quot;*&quot;,</code> | stylus: Dependency requirement or executable metadata named stylus. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2822 | <code>        &quot;sugarss&quot;: &quot;*&quot;,</code> | sugarss: Dependency requirement or executable metadata named sugarss. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2823 | <code>        &quot;terser&quot;: &quot;^5.16.0&quot;,</code> | terser: Dependency requirement or executable metadata named terser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2824 | <code>        &quot;tsx&quot;: &quot;^4.8.1&quot;,</code> | tsx: Dependency requirement or executable metadata named tsx. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2825 | <code>        &quot;yaml&quot;: &quot;^2.4.2&quot;</code> | yaml: Dependency requirement or executable metadata named yaml. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2826 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2827 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 2828 | <code>        &quot;@types/node&quot;: {</code> | @types/node: Dependency requirement or executable metadata named @types/node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2829 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2830 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2831 | <code>        &quot;jiti&quot;: {</code> | jiti: Dependency requirement or executable metadata named jiti. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2832 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2833 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2834 | <code>        &quot;less&quot;: {</code> | less: Dependency requirement or executable metadata named less. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2835 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2836 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2837 | <code>        &quot;lightningcss&quot;: {</code> | lightningcss: Dependency requirement or executable metadata named lightningcss. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2838 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2839 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2840 | <code>        &quot;sass&quot;: {</code> | sass: Dependency requirement or executable metadata named sass. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2841 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2842 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2843 | <code>        &quot;sass-embedded&quot;: {</code> | sass-embedded: Dependency requirement or executable metadata named sass-embedded. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2844 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2845 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2846 | <code>        &quot;stylus&quot;: {</code> | stylus: Dependency requirement or executable metadata named stylus. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2847 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2848 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2849 | <code>        &quot;sugarss&quot;: {</code> | sugarss: Dependency requirement or executable metadata named sugarss. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2850 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2851 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2852 | <code>        &quot;terser&quot;: {</code> | terser: Dependency requirement or executable metadata named terser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2853 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2854 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2855 | <code>        &quot;tsx&quot;: {</code> | tsx: Dependency requirement or executable metadata named tsx. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2856 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2857 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2858 | <code>        &quot;yaml&quot;: {</code> | yaml: Dependency requirement or executable metadata named yaml. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2859 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2860 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2861 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2862 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2863 | <code>    &quot;node_modules/vite-node&quot;: {</code> | node_modules/vite-node: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2864 | <code>      &quot;version&quot;: &quot;3.2.4&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2865 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/vite-node/-/vite-node-3.2.4.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2866 | <code>      &quot;integrity&quot;: &quot;sha512-EbKSKh+bh1E1IFxeO0pg1n4dvoOTt0UDiXMd/qn++r98+jPO1xtJilvXldeuQ8giIB5IkpjCgMleHMNEsGH6pg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2867 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2868 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2869 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2870 | <code>        &quot;cac&quot;: &quot;^6.7.14&quot;,</code> | cac: Dependency requirement or executable metadata named cac. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2871 | <code>        &quot;debug&quot;: &quot;^4.4.1&quot;,</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2872 | <code>        &quot;es-module-lexer&quot;: &quot;^1.7.0&quot;,</code> | es-module-lexer: Dependency requirement or executable metadata named es-module-lexer. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2873 | <code>        &quot;pathe&quot;: &quot;^2.0.3&quot;,</code> | pathe: Dependency requirement or executable metadata named pathe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2874 | <code>        &quot;vite&quot;: &quot;^5.0.0 &#124;&#124; ^6.0.0 &#124;&#124; ^7.0.0-0&quot;</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2875 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2876 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2877 | <code>        &quot;vite-node&quot;: &quot;vite-node.mjs&quot;</code> | vite-node: Dependency requirement or executable metadata named vite-node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2878 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2879 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2880 | <code>        &quot;node&quot;: &quot;^18.0.0 &#124;&#124; ^20.0.0 &#124;&#124; &gt;=22.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2881 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2882 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2883 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2884 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2885 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2886 | <code>    &quot;node_modules/vitest&quot;: {</code> | node_modules/vitest: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2887 | <code>      &quot;version&quot;: &quot;3.2.7&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2888 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/vitest/-/vitest-3.2.7.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2889 | <code>      &quot;integrity&quot;: &quot;sha512-KrxIJ62Fd89gfysR4WotlgZABiz2dqFPgqGzX7s+CwsqLFomRH7777ZcrOD6+WVAh7khPQP41A+BKbpcJFrdEg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2890 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2891 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2892 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2893 | <code>        &quot;@types/chai&quot;: &quot;^5.2.2&quot;,</code> | @types/chai: Dependency requirement or executable metadata named @types/chai. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2894 | <code>        &quot;@vitest/expect&quot;: &quot;3.2.7&quot;,</code> | @vitest/expect: Dependency requirement or executable metadata named @vitest/expect. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2895 | <code>        &quot;@vitest/mocker&quot;: &quot;3.2.7&quot;,</code> | @vitest/mocker: Dependency requirement or executable metadata named @vitest/mocker. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2896 | <code>        &quot;@vitest/pretty-format&quot;: &quot;^3.2.7&quot;,</code> | @vitest/pretty-format: Dependency requirement or executable metadata named @vitest/pretty-format. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2897 | <code>        &quot;@vitest/runner&quot;: &quot;3.2.7&quot;,</code> | @vitest/runner: Dependency requirement or executable metadata named @vitest/runner. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2898 | <code>        &quot;@vitest/snapshot&quot;: &quot;3.2.7&quot;,</code> | @vitest/snapshot: Dependency requirement or executable metadata named @vitest/snapshot. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2899 | <code>        &quot;@vitest/spy&quot;: &quot;3.2.7&quot;,</code> | @vitest/spy: Dependency requirement or executable metadata named @vitest/spy. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2900 | <code>        &quot;@vitest/utils&quot;: &quot;3.2.7&quot;,</code> | @vitest/utils: Dependency requirement or executable metadata named @vitest/utils. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2901 | <code>        &quot;chai&quot;: &quot;^5.2.0&quot;,</code> | chai: Dependency requirement or executable metadata named chai. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2902 | <code>        &quot;debug&quot;: &quot;^4.4.1&quot;,</code> | debug: Dependency requirement or executable metadata named debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2903 | <code>        &quot;expect-type&quot;: &quot;^1.2.1&quot;,</code> | expect-type: Dependency requirement or executable metadata named expect-type. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2904 | <code>        &quot;magic-string&quot;: &quot;^0.30.17&quot;,</code> | magic-string: Dependency requirement or executable metadata named magic-string. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2905 | <code>        &quot;pathe&quot;: &quot;^2.0.3&quot;,</code> | pathe: Dependency requirement or executable metadata named pathe. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2906 | <code>        &quot;picomatch&quot;: &quot;^4.0.2&quot;,</code> | picomatch: Dependency requirement or executable metadata named picomatch. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2907 | <code>        &quot;std-env&quot;: &quot;^3.9.0&quot;,</code> | std-env: Dependency requirement or executable metadata named std-env. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2908 | <code>        &quot;tinybench&quot;: &quot;^2.9.0&quot;,</code> | tinybench: Dependency requirement or executable metadata named tinybench. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2909 | <code>        &quot;tinyexec&quot;: &quot;^0.3.2&quot;,</code> | tinyexec: Dependency requirement or executable metadata named tinyexec. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2910 | <code>        &quot;tinyglobby&quot;: &quot;^0.2.14&quot;,</code> | tinyglobby: Dependency requirement or executable metadata named tinyglobby. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2911 | <code>        &quot;tinypool&quot;: &quot;^1.1.1&quot;,</code> | tinypool: Dependency requirement or executable metadata named tinypool. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2912 | <code>        &quot;tinyrainbow&quot;: &quot;^2.0.0&quot;,</code> | tinyrainbow: Dependency requirement or executable metadata named tinyrainbow. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2913 | <code>        &quot;vite&quot;: &quot;^5.0.0 &#124;&#124; ^6.0.0 &#124;&#124; ^7.0.0-0&quot;,</code> | vite: Dependency requirement or executable metadata named vite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2914 | <code>        &quot;vite-node&quot;: &quot;3.2.4&quot;,</code> | vite-node: Dependency requirement or executable metadata named vite-node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2915 | <code>        &quot;why-is-node-running&quot;: &quot;^2.3.0&quot;</code> | why-is-node-running: Dependency requirement or executable metadata named why-is-node-running. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2916 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2917 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 2918 | <code>        &quot;vitest&quot;: &quot;vitest.mjs&quot;</code> | vitest: Dependency requirement or executable metadata named vitest. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2919 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2920 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2921 | <code>        &quot;node&quot;: &quot;^18.0.0 &#124;&#124; ^20.0.0 &#124;&#124; &gt;=22.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2922 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2923 | <code>      &quot;funding&quot;: {</code> | funding: Package-maintainer funding metadata; loading this lockfile does not initiate payment. |
| 2924 | <code>        &quot;url&quot;: &quot;https://opencollective.com/vitest&quot;</code> | url: Metadata URL used by the enclosing funding/source record. |
| 2925 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2926 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 2927 | <code>        &quot;@edge-runtime/vm&quot;: &quot;*&quot;,</code> | @edge-runtime/vm: Dependency requirement or executable metadata named @edge-runtime/vm. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2928 | <code>        &quot;@types/debug&quot;: &quot;^4.1.12&quot;,</code> | @types/debug: Dependency requirement or executable metadata named @types/debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2929 | <code>        &quot;@types/node&quot;: &quot;^18.0.0 &#124;&#124; ^20.0.0 &#124;&#124; &gt;=22.0.0&quot;,</code> | @types/node: Dependency requirement or executable metadata named @types/node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2930 | <code>        &quot;@vitest/browser&quot;: &quot;3.2.7&quot;,</code> | @vitest/browser: Dependency requirement or executable metadata named @vitest/browser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2931 | <code>        &quot;@vitest/ui&quot;: &quot;3.2.7&quot;,</code> | @vitest/ui: Dependency requirement or executable metadata named @vitest/ui. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2932 | <code>        &quot;happy-dom&quot;: &quot;*&quot;,</code> | happy-dom: Dependency requirement or executable metadata named happy-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2933 | <code>        &quot;jsdom&quot;: &quot;*&quot;</code> | jsdom: Dependency requirement or executable metadata named jsdom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2934 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2935 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 2936 | <code>        &quot;@edge-runtime/vm&quot;: {</code> | @edge-runtime/vm: Dependency requirement or executable metadata named @edge-runtime/vm. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2937 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2938 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2939 | <code>        &quot;@types/debug&quot;: {</code> | @types/debug: Dependency requirement or executable metadata named @types/debug. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2940 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2941 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2942 | <code>        &quot;@types/node&quot;: {</code> | @types/node: Dependency requirement or executable metadata named @types/node. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2943 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2944 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2945 | <code>        &quot;@vitest/browser&quot;: {</code> | @vitest/browser: Dependency requirement or executable metadata named @vitest/browser. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2946 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2947 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2948 | <code>        &quot;@vitest/ui&quot;: {</code> | @vitest/ui: Dependency requirement or executable metadata named @vitest/ui. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2949 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2950 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2951 | <code>        &quot;happy-dom&quot;: {</code> | happy-dom: Dependency requirement or executable metadata named happy-dom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2952 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2953 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2954 | <code>        &quot;jsdom&quot;: {</code> | jsdom: Dependency requirement or executable metadata named jsdom. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2955 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 2956 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2957 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2958 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2959 | <code>    &quot;node_modules/w3c-xmlserializer&quot;: {</code> | node_modules/w3c-xmlserializer: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2960 | <code>      &quot;version&quot;: &quot;5.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2961 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/w3c-xmlserializer/-/w3c-xmlserializer-5.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2962 | <code>      &quot;integrity&quot;: &quot;sha512-o8qghlI8NZHU1lLPrpi2+Uq7abh4GGPpYANlalzWxyWteJOCsr/P+oPBA49TOLu5FTZO4d3F9MnWJfiMo4BkmA==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2963 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2964 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2965 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2966 | <code>        &quot;xml-name-validator&quot;: &quot;^5.0.0&quot;</code> | xml-name-validator: Dependency requirement or executable metadata named xml-name-validator. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2967 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2968 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2969 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2970 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2971 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2972 | <code>    &quot;node_modules/webidl-conversions&quot;: {</code> | node_modules/webidl-conversions: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2973 | <code>      &quot;version&quot;: &quot;7.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2974 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/webidl-conversions/-/webidl-conversions-7.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2975 | <code>      &quot;integrity&quot;: &quot;sha512-VwddBukDzu71offAQR975unBIGqfKZpM+8ZX6ySk8nYhVoo5CYaZyzt3YBvYtRtO+aoGlqxPg/B87NGVZ/fu6g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2976 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2977 | <code>      &quot;license&quot;: &quot;BSD-2-Clause&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2978 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2979 | <code>        &quot;node&quot;: &quot;&gt;=12&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2980 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2981 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2982 | <code>    &quot;node_modules/whatwg-encoding&quot;: {</code> | node_modules/whatwg-encoding: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2983 | <code>      &quot;version&quot;: &quot;3.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2984 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/whatwg-encoding/-/whatwg-encoding-3.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2985 | <code>      &quot;integrity&quot;: &quot;sha512-6qN4hJdMwfYBtE3YBTTHhoeuUrDBPZmbQaxWAqSALV/MeEnR5z1xd8UKud2RAkFoPkmB+hli1TZSnyi84xz1vQ==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 2986 | <code>      &quot;deprecated&quot;: &quot;Use @exodus/bytes instead for a more spec-conformant and faster implementation&quot;,</code> | deprecated: Dependency requirement or executable metadata named deprecated. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2987 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 2988 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 2989 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 2990 | <code>        &quot;iconv-lite&quot;: &quot;0.6.3&quot;</code> | iconv-lite: Dependency requirement or executable metadata named iconv-lite. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 2991 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2992 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 2993 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 2994 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2995 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 2996 | <code>    &quot;node_modules/whatwg-mimetype&quot;: {</code> | node_modules/whatwg-mimetype: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 2997 | <code>      &quot;version&quot;: &quot;4.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 2998 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/whatwg-mimetype/-/whatwg-mimetype-4.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 2999 | <code>      &quot;integrity&quot;: &quot;sha512-QaKxh0eNIi2mE9p2vEdzfagOKHCcj1pJ56EEHGQOVxp8r9/iszLUUV7v89x9O1p/T+NlTM5W7jW6+cz4Fq1YVg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3000 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3001 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3002 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 3003 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 3004 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3005 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3006 | <code>    &quot;node_modules/whatwg-url&quot;: {</code> | node_modules/whatwg-url: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3007 | <code>      &quot;version&quot;: &quot;14.2.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3008 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/whatwg-url/-/whatwg-url-14.2.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3009 | <code>      &quot;integrity&quot;: &quot;sha512-De72GdQZzNTUBBChsXueQUnPKDkg/5A5zp7pFDuQAj5UFoENpiACU0wlCvzpAGnTkj++ihpKwKyYewn/XNUbKw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3010 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3011 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3012 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 3013 | <code>        &quot;tr46&quot;: &quot;^5.1.0&quot;,</code> | tr46: Dependency requirement or executable metadata named tr46. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3014 | <code>        &quot;webidl-conversions&quot;: &quot;^7.0.0&quot;</code> | webidl-conversions: Dependency requirement or executable metadata named webidl-conversions. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3015 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3016 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 3017 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 3018 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3019 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3020 | <code>    &quot;node_modules/why-is-node-running&quot;: {</code> | node_modules/why-is-node-running: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3021 | <code>      &quot;version&quot;: &quot;2.3.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3022 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/why-is-node-running/-/why-is-node-running-2.3.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3023 | <code>      &quot;integrity&quot;: &quot;sha512-hUrmaWBdVDcxvYqnyh09zunKzROWjbZTiNy8dBEjkS7ehEDQibXJ7XvlmtbwuTclUiIyN+CyXQD4Vmko8fNm8w==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3024 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3025 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3026 | <code>      &quot;dependencies&quot;: {</code> | dependencies: Declared runtime dependency requirements for this package; nested values are version constraints. |
| 3027 | <code>        &quot;siginfo&quot;: &quot;^2.0.0&quot;,</code> | siginfo: Dependency requirement or executable metadata named siginfo. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3028 | <code>        &quot;stackback&quot;: &quot;0.0.2&quot;</code> | stackback: Dependency requirement or executable metadata named stackback. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3029 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3030 | <code>      &quot;bin&quot;: {</code> | bin: Map of installed command names to package-provided executable entry files. |
| 3031 | <code>        &quot;why-is-node-running&quot;: &quot;cli.js&quot;</code> | why-is-node-running: Dependency requirement or executable metadata named why-is-node-running. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3032 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3033 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 3034 | <code>        &quot;node&quot;: &quot;&gt;=8&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 3035 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3036 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3037 | <code>    &quot;node_modules/ws&quot;: {</code> | node_modules/ws: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3038 | <code>      &quot;version&quot;: &quot;8.22.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3039 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/ws/-/ws-8.22.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3040 | <code>      &quot;integrity&quot;: &quot;sha512-Ydggc987+RO0AnWtZ/7Wq9FtNvcrL1b/RO0ud9mWjUPgDrsAAwQSF51sm2hm1XofbU/4jkpGEsLFsZZxU+1DOg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3041 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3042 | <code>      &quot;license&quot;: &quot;MIT&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3043 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 3044 | <code>        &quot;node&quot;: &quot;&gt;=10.0.0&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 3045 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3046 | <code>      &quot;peerDependencies&quot;: {</code> | peerDependencies: Version requirements for dependencies expected from the consuming environment. |
| 3047 | <code>        &quot;bufferutil&quot;: &quot;^4.0.1&quot;,</code> | bufferutil: Dependency requirement or executable metadata named bufferutil. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3048 | <code>        &quot;utf-8-validate&quot;: &quot;&gt;=5.0.2&quot;</code> | utf-8-validate: Dependency requirement or executable metadata named utf-8-validate. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3049 | <code>      },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3050 | <code>      &quot;peerDependenciesMeta&quot;: {</code> | peerDependenciesMeta: Extra metadata such as whether an expected peer dependency is optional. |
| 3051 | <code>        &quot;bufferutil&quot;: {</code> | bufferutil: Dependency requirement or executable metadata named bufferutil. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3052 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 3053 | <code>        },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3054 | <code>        &quot;utf-8-validate&quot;: {</code> | utf-8-validate: Dependency requirement or executable metadata named utf-8-validate. The displayed value is interpreted by its containing dependency/bin/engine map. |
| 3055 | <code>          &quot;optional&quot;: true</code> | optional: True marks an optional dependency/peer record. |
| 3056 | <code>        }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3057 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3058 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3059 | <code>    &quot;node_modules/xml-name-validator&quot;: {</code> | node_modules/xml-name-validator: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3060 | <code>      &quot;version&quot;: &quot;5.0.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3061 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/xml-name-validator/-/xml-name-validator-5.0.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3062 | <code>      &quot;integrity&quot;: &quot;sha512-EvGK8EJ3DhaHfbRlETOWAS5pO9MZITeauHKJyb8wyajUfQUenkIg2MvLDTZ4T/TgIcm3HU0TFBgWWboAZ30UHg==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3063 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3064 | <code>      &quot;license&quot;: &quot;Apache-2.0&quot;,</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3065 | <code>      &quot;engines&quot;: {</code> | engines: Supported Node/npm engine version ranges for the package. |
| 3066 | <code>        &quot;node&quot;: &quot;&gt;=18&quot;</code> | node: Node.js version constraint inside engines; not Python or experiment configuration. |
| 3067 | <code>      }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3068 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3069 | <code>    &quot;node_modules/xmlchars&quot;: {</code> | node_modules/xmlchars: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3070 | <code>      &quot;version&quot;: &quot;2.2.0&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3071 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/xmlchars/-/xmlchars-2.2.0.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3072 | <code>      &quot;integrity&quot;: &quot;sha512-JZnDKK8B0RCDw84FNdDAIpZK+JuJw+s7Lz8nksI7SIuU3UXJJslUthsi+uWBUYOwPFwW7W7PRLRfUKpxjtjFCw==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3073 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3074 | <code>      &quot;license&quot;: &quot;MIT&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3075 | <code>    },</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3076 | <code>    &quot;node_modules/yallist&quot;: {</code> | node_modules/yallist: Begin the resolved dependency record for this npm installation path; following fields describe its version, integrity and dependencies. |
| 3077 | <code>      &quot;version&quot;: &quot;3.1.1&quot;,</code> | version: Recorded resolved package version. It does not select a HAT model or dataset version. |
| 3078 | <code>      &quot;resolved&quot;: &quot;https://registry.npmjs.org/yallist/-/yallist-3.1.1.tgz&quot;,</code> | resolved: Location from which npm obtains this resolved package archive. |
| 3079 | <code>      &quot;integrity&quot;: &quot;sha512-a4UGQaWPH59mOXUYnAG2ewncQS4i4F43Tv3JoAM+s2VDAmS9NsK8GpDMLrCHPksFT7h3K6TOoUNn2pb7RoXx4g==&quot;,</code> | integrity: Subresource-integrity hash npm uses to verify package archive bytes. |
| 3080 | <code>      &quot;dev&quot;: true,</code> | dev: True marks a dependency record as development-only in the resolved tree. |
| 3081 | <code>      &quot;license&quot;: &quot;ISC&quot;</code> | license: Recorded licence for this dataset/package; not executable logic. |
| 3082 | <code>    }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3083 | <code>  }</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
| 3084 | <code>}</code> | Close the preceding JSON object/array; a comma separates it from the next item. |
