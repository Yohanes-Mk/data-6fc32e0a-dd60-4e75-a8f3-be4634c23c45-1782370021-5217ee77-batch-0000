# Stage 4D — Final Expanded Semantic Pilot

The final controlled pilot before deciding on larger-scale Claude-history extraction. 24 cases
(6 benchmark + 18 blind, locked before semantic inspection), extracted by language-model semantic
judgment over **Stage 3R + the mandatory Stage 3R-P overlay** (3R-P wins on patched metadata).

## Layout
- `config/expanded_pilot_policy.json` — ontology, strict project test, confidence/endorsement/status/
  attachment/missing-source/relationship/clustering/profile policies, evidence priority, confirmed resolutions.
- `schemas/` — expanded knowledge schema (markdown) + candidate/relationship JSON Schemas
  (adds `status_current_confidence`, `co_authored_flag`).
- `selection/` — 24 selected cases, excluded selection candidates, selection report, **selection_lock.json**.
- `evidence_bundles/` — per-case bundles with the 3R-P attachment overlay (filenames preserved null).
- `results/` — case_extractions, candidate_entities, candidate_relationships, candidate_evidence,
  excluded_interactions, missing_source_impacts, unresolved_items.
- `synthesis/` — work_entity_clusters, possible_duplicate_entities, profile_level_knowledge, expanded_project_landscape.
- `evaluation/` — benchmark_results, case_quality_scores, readiness_assessment.
- `reports/` — pilot_report, semantic_quality_review, comparison_to_stage4c, human_review_queue, review_sample, validation_report.
- `manifests/` — checksums before/after.
- `scripts_validate.py` — self-contained structural validator.

## Headline results
- 24/24 cases processed (22 with candidates; ex-07/ex-15 recorded as empty, not substituted).
- 35 candidates: work_entity 16 (**2 projects**), project_knowledge 8, context_entity 7, non_project 4; +4 excluded.
- Confidence high 24 / med 10 / low 1; separate status_current_confidence high 8 / med 19 / low 8.
- 20 relationships; 6 clusters; 4 profile-level knowledge records.
- Attachment policy (3R-P): Fleet Command 92→88 unique, 0 filenames (null preserved), 0 binaries; populated filenames used only where present.
- 6 missing-source impacts, all do_not_infer; nothing reconstructed.
- **Benchmarks 11/11 pass**; all confirmed resolutions honored (incl. co-authored Client Radar, historical AVATAR).
- Gates: **structural pass · provenance pass · semantic conditional_pass · scaling conditional_pass**.
- Checksums: 174 prior files unchanged; **no existing file modified**.

## Recommendation
Proceed to a **~50-case subscription-only batch after codifying the recurring human-review decision
rules**; then re-assess full-corpus readiness. **Not** ready for full-corpus subscription extraction or
batch-API automation yet (mixed-origin segmentation and attachment-filename propagation need upstream
fixes; empty-conversation handling needs a defined rule at scale). See `reports/pilot_report.md` and
`evaluation/readiness_assessment.json`.
