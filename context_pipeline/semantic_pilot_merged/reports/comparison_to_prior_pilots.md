# Stage 4C — Comparison to Prior Pilots

| Dimension | Stage 4A-R (Codex repair) | Stage 4B (Claude blind) | Stage 4C (merged) |
|---|---|---|---|
| Cases / conversations | 8 conversations | 8 conversations | **12 cases** (6 benchmark + 6 new structural) |
| Evidence boundary | Stage 3 bundles | Stage 3 bundles | **Stage 3R** (corrected provenance/attachments/docs/missing-sources) |
| Candidate entities | 21 | 43 (+4 excluded) | **48** (+5 excluded) |
| `project` count | 6 (incl. 1 false project + 1 over-merge) | 2 | **2** |
| Other work-entity types | none (only `project`) | assignment, job_application, exam_prep, initiative, recurring_responsibility, standalone_idea | assignment×3, job_application×2, client_engagement×2, initiative, exam_prep, research_effort, subproject |
| Context entities | **0** | 9 | **10** (person, employer, platform, tool, institution, …) |
| Distinct knowledge types | 4 | 17 | **~20** (adds status_update/next_step/research_finding/blocker/open_question, etc.) |
| Titles | copied message openings | descriptive | **descriptive** (banned-list enforced by validator) |
| Confidence spread | high 7 / med 14 / low 0 | high 39 / med 7 / low 1 | **high 38 / med 10 / low 0** |
| Temporal discipline | all "current" | per-project | **per-project, seeded by hr-007/008/009** (1 current, Fleet/Tsotsi unresolved) |
| Relationships | 12 (intra-conversation only) | 41 | **39** incl. cross-case `part_of`/`associated_with` |
| Attachment dedup | not reported | flagged (0 surfaced) | **92 occ → 88 unique, binaries unavailable, reported explicitly** |
| Missing sources | not modeled | flagged in unresolved | **9 impact records, do_not_infer** |
| Cross-case clustering | none | none (single-stage) | **6 clusters, 5 possible-duplicates, no auto-merge** |

## What the merged approach fixes from each predecessor

**From Codex (4A-R) it keeps** the conservative project-admission spine and the strict
project test, but **fixes** Codex's three execution failures:
- the false project (14f3c888) — here mc-01 is a one-off, not a project;
- the over-merge (94f53cfc) — here mc-03 is five separate work entities;
- copied-opening titles, generic boilerplate descriptions, and assistant/tool text mislabeled
  as user tasks — here titles are descriptive and provenance is carried from Stage 3R.

**From Claude (4B) it keeps** the broad ontology, context entities, descriptive titles, and
calibrated confidence, but **adds** what 4B lacked:
- Stage 3R provenance fields (`transport_author_roles`, `content_origins`, `assertion_relationships`)
  so mixed-origin messages are handled at the field level, not just prose;
- explicit attachment occurrence-vs-unique accounting (the 4B "attachment_heavy yet 0 surfaced"
  gap is now quantified: 92→88, binaries unavailable);
- per-missing-source impact records with `do_not_infer`;
- a cross-case clustering/synthesis pass producing a reviewable landscape.

## Benchmark agreement vs prior human resolutions

All 9 benchmark expectations pass (see `validation_report.json`), and the six confirmed human
resolutions (hr-001…hr-010) are honored: transcript = not a project; pesticide = assignment;
mixed-2024 = not merged; roadmap = active; Fleet Command & Tsotsi = status unresolved; ExamPro
skip = assistant proposal; Accenture = confirmed; GDD/SDD = source.

## Qualitative precision / recall (no ground truth → qualitative)

- **Precision tendency:** high. Only 2 strict projects; every work entity records criteria and
  competing classifications; no false project; assistant/tool content excluded from user facts.
- **Recall tendency:** high for the structured corpus — context entities, decisions, artifacts,
  milestones, blockers, research, and cross-case links are all recovered. The main recall gaps are
  intentional: content behind unavailable binaries and missing deep-research results is **not**
  reconstructed (recorded as impacts instead).
