# Guide verification

Verified on 15 October 2026 against the current working-tree source.

- 61 tracked project files inventoried with SHA256 fingerprints.
- 56 files covered by numbered explanations, totaling 7,953 physical source/reference lines. This includes comments, blanks, JSON metadata and dependency-lock entries.
- Each numbered sequence checked for gaps, duplicates and unexpected rows.
- Reproduced source text checked against the corresponding current file after decoding Markdown/HTML presentation escapes: zero mismatches.
- Browser edition contains six chapters. DOM-based checks passed for chapter navigation, active state, search and clearing search, all 7,953 source rows and three-column line/source/explanation tables.
- Frontend chapter additionally expands the compressed CSS into 222 rules and 684 declarations.
- Application source was not edited. No model training, dataset downloads, attack replay or experiment suite was executed for this explanation request.
- A new persistent code-only Graphify map was built: 371 nodes and 904 edges. Seven code files produced no symbols in the extractor; their source was still inspected directly and included in the line guide. The graph was used as a structural aid, not a completeness proof. No semantic extraction or clustering was performed.
- Three focused documentation reviews covered frontend, SDN/data tooling, and tests/configuration; the primary review covered the Python backend and integrated the overview and source checks.

A browser visual preview was attempted but blocked by an existing Chrome debugging profile lock. Layout has not been visually verified; navigation/search were verified against the generated HTML in jsdom. Markdown chapters provide an independent readable edition.

## Scope

The maintained source and configuration are explained line by line. Existing prose documents are identified by purpose in the overview; frontend README is also annotated. Installed library internals, downloaded dataset records, generated model-run output rows, caches, virtual environments and executable binaries are not part of the code annotations. They are identified by role so source is distinguishable from environment and evidence.

The backend chapter combines symbol-level teaching notes, specific explanations of model/evaluation/metric/protocol decisions and a line-level syntax walkthrough. Closing punctuation and blank-line descriptions intentionally repeat. An annotation is an explanation of source, not proof that every possible runtime path has been tested.

## Review assessment

| Criterion | Assessment | Evidence and limit |
|---|---:|---|
| Accuracy | 4/5 | Exact source matching and inspected call flow; external library internals are explained at their repository call boundary, and not exhaustively audited. |
| Completeness | 4/5 | All 56 source/config/reference files have continuous coverage; installed dependencies, generated data and existing prose are covered by role instead of exhaustive internal annotations. |
| Clarity | 4/5 | Overview, reading order, observation example, glossary and source tables; line tables still require studying a whole statement across continuation lines. |
| Actionability | 4/5 | Searchable offline HTML, Markdown and portable ZIP; browser rendering lacks visual verification because its existing profile was locked. |
| Conciseness | 4/5 | Core teaching chapters are separate from repetitive manifest/lock metadata; exhaustive physical-line coverage necessarily includes repeated syntax explanations. |

Overall: 4.0/5. The highest-value next study step is to trace one CSV record through engine.py with the source table open, then explain the separate feature/truth paths for packet windows. A future code change requires refreshing the corresponding source snapshot and coverage checks. This guide does not itself establish that pending live research experiments have been completed.
