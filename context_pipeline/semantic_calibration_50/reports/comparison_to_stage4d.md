# Stage 4E vs Stage 4D Comparison

| dimension | Stage 4D | Stage 4E |
|---|---|---|
| cases | 24 (6 benchmark + 18 blind) | 50 (10 benchmark + 40 blind) |
| candidates | 35 | 63 |
| strict projects | 2 | 5 |
| benchmarks | 11/11 pass | 16/16 pass |
| empty cases | 2 (ex-07/ex-15) | 7 (recorded, not substituted) |
| recurring rules | not yet codified | 22 codified + applied |
| human-review | per-case, needs codification | 32% → 10% after rules |
| semantic gate | conditional_pass | pass |
| scaling gate | conditional_pass (need rules codified) | conditional_pass (rules codified; ready for 50-100 batch) |
| framework freeze | not assessed | **recommended** |

## What changed

- The exact gap Stage 4D named ('Ready once recurring decision rules are codified') is now closed: all four recurring decision-rule families (multi-session phase-merge, employer shared-context separation, author-identity/group ownership, document source-vs-artifact/linkage) are codified as hr-006..hr-022 and auto-applied, dropping per-case human review to 10%.

- 40 fresh blind cases (vs 18) confirm generalization: no false-project pattern, 0 provenance violations, and previously-manual questions (Client Radar phase merge, Accenture separation, marketing umbrella, group ownership) are now resolved automatically.

- Two upstream data caveats from 4D persist (mixed-origin segmentation; null attachment filenames) and are carried forward as monitored conditions, not blockers.

