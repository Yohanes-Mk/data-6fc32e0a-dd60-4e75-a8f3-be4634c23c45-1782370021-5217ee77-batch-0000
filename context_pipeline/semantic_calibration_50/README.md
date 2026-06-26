# Stage 4E — 50-Case Subscription-Only Semantic Calibration Batch

The final calibration stage before larger-scale Claude-history extraction. **50 cases**
(10 benchmark/policy + 40 blind, locked before semantic inspection), processed in **five checkpointed
batches** by language-model semantic judgment over **Stage 3R + the mandatory Stage 3R-P overlay**
(3R-P wins on patched metadata). Purpose: **finalize reusable decision rules and decide framework
freeze** — not another open-ended pilot. No full-corpus processing, no external API, no network.

## Layout
- `config/` — `calibration_policy.json`, **`recurring_decision_rules.json`** (22 codified rules),
  `confirmed_resolutions.json` (3R-P + Stage 4E confirmed human decisions).
- `schemas/` — calibration knowledge schema (md) + candidate/relationship JSON Schemas (adds
  `applied_decision_rule_ids`, `review_classification`).
- `selection/` — 50 selected cases, **`selection_lock.json`** (SHA over 40 blind targets, pre-semantic),
  excluded candidates, selection report.
- `evidence_bundles/` — per-case provenance bundles (3R-P attachment overlay; null filenames preserved).
- `batches/batch_01..05/` — case ids, extraction slice, rules applied, quality review, unresolved,
  validation summary, completion manifest.
- `results/` — case_extractions, candidate_entities, candidate_relationships, candidate_evidence,
  excluded_interactions, missing_source_impacts, unresolved_items.
- `synthesis/` — work_entity_clusters, possible_duplicate_entities, profile_level_knowledge,
  recurring_responsibilities, calibration_project_landscape.
- `evaluation/` — benchmark_results, case_quality_scores, failure_patterns, human_review_metrics,
  decision_rule_evaluation, readiness_assessment.
- `reports/` — calibration_report, semantic_quality_review, provenance_review, human_review_queue,
  decision_rule_report, comparison_to_stage4d, review_sample, validation_report.
- `manifests/` — checksums before/after. `scripts_validate.py` — structural validator.

## Headline results
- 50/50 cases processed (7 empty recorded, **not** substituted). 63 candidates: 25 work_entity
  (**5 strict projects**), 18 project_knowledge, 7 context_entity, 13 non_project.
- Confidence high 40 / med 21 / low 2; separate status-current confidence high 20 / med 27 / low 16.
- 22 relationships (all evidence-backed); 7 clusters; 3 possible-duplicate sets; 4 profile facts; 3
  recurring responsibilities.
- **Benchmarks 16/16 pass.** All confirmed resolutions honored (Client Radar active/co-authored &
  separate from completed onboarding; CSCI Project 3 group_owned; marketing umbrella personal/family
  only; AVATAR completed/historical).
- Human-review rate **32% → 10%** after recurring rules; 11 questions auto-resolved by existing rules.
  Review items: 9 covered_by_existing_rule, 2 case_specific_exception, 1 genuinely_unresolved (2%),
  1 new_reusable_rule proposed (hr-008a).
- 13 missing-source impacts (all do_not_infer); 149 null attachment filenames preserved (0 invented);
  occurrence-vs-hash dedup applied; 0 binaries inspected; **0 provenance violations**.
- Gates: structural **pass** · provenance **pass** · semantic **pass** · calibration **pass** ·
  framework-freeze **recommended** · scaling **conditional_pass**.
- 209 prior-stage files unchanged; **no existing file modified**.

## Recommendation
**Freeze the schema and the 22-rule set.** No systemic failure recurred across ≥3 cases, so another
calibration pilot is **not** warranted. Next stage: a **50–100 case subscription extraction batch**
under the frozen rules (only novel ambiguities enter human review), then re-assess full-corpus and
batch-API automation. Full-corpus and API automation remain **conditional** pending the two carried
upstream data caveats (mixed-origin segmentation; null attachment filenames). See
`evaluation/readiness_assessment.json` and `reports/calibration_report.md`.
