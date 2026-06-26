# Stage 4D — Final Expanded Semantic Pilot Report

A 24-case pilot (6 benchmark + 18 blind, locked before inspection) testing whether the merged
semantic framework generalizes to a broader, mostly-unseen sample, grounded on Stage 3R with the
mandatory Stage 3R-P overlay. Extraction was done by language-model semantic judgment; scripts only
selected deterministically, resolved references, wrote, validated, counted, and checksummed.

## 1. Selected 24 cases
Benchmarks: ex-01 transcript (14f3c888), ex-02 pesticide (2838a734), ex-03 mixed-2024 (94f53cfc),
ex-04 roadmap (b8366901), ex-05 Fleet Command (e2fc5641), ex-06 Client Radar (design-chat + f04cc5a5).
Blind (18, deterministic structural): ex-07..ex-09 low; ex-10..ex-14 medium; ex-15..ex-19 high;
ex-20..ex-22 extreme; ex-23 project-document (AD Campaigns marketing KB); ex-24 design-chat
(Trending animation). Blind selection lock sha256 recorded before any content was read.

## 2. Candidate counts (by layer / type)
35 candidates: **work_entity 16, project_knowledge 8, context_entity 7, non_project_interaction 4**
(+4 excluded). Work-entity types: assignment 5, client_engagement 2, initiative 2, standalone_idea 2,
**project 2**, exam_preparation 1, job_application 1, recurring_responsibility 1.

## 3. Work-entity & project counts
16 work entities; **2 strict projects** (AI roadmap — active; Fleet Command — status unresolved).

## 4. Confidence / endorsement / relationships
- `confidence`: high 24 / medium 10 / low 1; separate `status_current_confidence`: high 8 / med 19 / low 8.
- Endorsement: not_applicable 21, implicit_continuation 6, modification 6, no_endorsement 2 (no unjustified explicit acceptance).
- Relationships: 20 — associated_with 8, informed_by 3, uses 3, created_for 3, part_of 3.

## 5. Evidence coverage
35/35 candidates carry resolved evidence. Empty cases ex-07/ex-15 produce no candidates (recorded).

## 6. Attachment & filename results (3R-P)
Fleet Command (ex-05): 92 occurrences → 88 unique hashes, **0 populated filenames (preserved null,
never invented)**, 0 binaries, text available. Where 3R-P populated filenames (ex-16: Project3.pdf;
ex-19: a11y_issues.md / repo_summary.md), they were used as-is; null filenames in ex-21 kept null.

## 7. Missing-source impacts
6 impact records (ex-05/06/16/19/21/04), all `do_not_infer:true`; nothing reconstructed.

## 8. Benchmark results
**11/11 pass** (`evaluation/benchmark_results.jsonl`), all confirmed resolutions honored, including
the 3R-P Client Radar (one engagement, two facets, co-authored audit) and AVATAR (historical).

## 9. Blind-case quality
Avg case score 22.1/30 (non-empty). Blind cases span academic (ex-10/13/16/20/21), career
(ex-09/17/22), technical (ex-11/21), business/client (ex-18/19), personal-planning (ex-14),
research-adjacent, and no-project/empty (ex-07/08/11/12/15) — genuine semantic variation, **no
template-driven extraction**. Per-case scores and "safe-for-scaling" flags in
`evaluation/case_quality_scores.jsonl`.

## 10. Cross-case synthesis
6 clusters (Client Radar phase, Accenture shared-context, marketing insufficient-evidence, user
profile, academic-assignment stream, AVATAR historical), 4 possible-duplicates, and 4 profile-level
records (voice preference, Accenture employment, SCSU identity, AI-tooling habit). No automatic merges.

## 11. Semantic defects
13 defect classes reviewed and resolved (`semantic_quality_review.md`); residual risks are
boundary/merge/identity decisions carried to the human-review queue, not extraction errors.

## 12. Statuses (Part 17 gates)
- **structural_validation_status: pass** (0 errors/warnings; 174 prior files unchanged).
- **provenance_quality_status: pass** (user evidence distinct; pasted/tool/log excluded; co-authorship
  represented; filenames not invented; occurrences not inflated).
- **semantic_quality_status: conditional_pass** (clean classification + calibration; material
  boundary/merge/identity decisions need human confirmation).
- **scaling_readiness_status: conditional_pass.**

## 13. Scaling readiness (Part 17)
- **Another pilot:** pass — framework generalized to 18 blind cases.
- **50-case subscription batch:** conditional_pass — ready once recurring decision rules (multi-session
  phase-merge, employer shared-context separation, author-identity disambiguation, project-document
  linkage) are codified.
- **Full-corpus subscription extraction:** fail (not yet) — mixed-origin "user_authored" segments still
  carry pasted assistant/tool content upstream, attachment filenames are largely null (hash-only
  identity), and empty-conversation handling needs a defined rule at scale.
- **Later API automation:** fail (not yet) — defer until the schema is stable across the 50-case batch
  and the human-review decision rules are settled.

## 14. Recommendation for the next stage
**Proceed to a ~50-case subscription-only batch after codifying the recurring human-review decision
rules**, then re-evaluate full-corpus readiness. Do **not** start full-corpus extraction or API
automation yet. Structural passing is necessary but not sufficient; the recommendation is gated on the
provenance and semantic statuses and the open boundary/merge/identity rules, two of which require an
upstream fix (mixed-origin segmentation; attachment filename propagation) before full scale.
