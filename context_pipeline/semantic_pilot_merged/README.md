# Stage 4C — Merged-Schema Semantic Pilot

A controlled 12-case semantic-extraction pilot that merges Codex's conservative project-admission
discipline (Stage 4A-R) with Claude's broader work-entity / project-knowledge ontology (Stage 4B),
grounded on **Stage 3R** (`extraction_staging_repair/corpus/`) as the authoritative evidence layer.

All semantic decisions (candidate type, project boundary, title, status, confidence, relationships)
were made by the language model. Scripts only load JSONL, select cases, resolve references, write
outputs, validate, count, and checksum.

## Layout

- `config/merged_pilot_policy.json` — pilot policy (ontology, strict project test, status/endorsement/attachment/missing-source/relationship/clustering policies, evidence priority).
- `schemas/` — merged knowledge schema (markdown) + candidate/relationship JSON Schemas.
- `selection/` — the 12 selected cases + deterministic selection report.
- `evidence_bundles/` — per-case semantic evidence bundles (priority-ordered, with provenance, attachments, missing sources).
- `results/` — case_extractions, candidate_entities, candidate_relationships, candidate_evidence, excluded_interactions, missing_source_impacts, unresolved_items.
- `synthesis/` — work_entity_clusters, possible_duplicate_entities, pilot_project_landscape.
- `reports/` — pilot_report, semantic_quality_review, comparison_to_prior_pilots, human_review_queue, review_sample, validation_report.
- `manifests/` — checksums before/after (immutability proof).
- `scripts_validate.py` — self-contained structural validator (no external packages).

## Headline results

- 12/12 cases processed; Stage 3R is the input boundary.
- 48 candidates: work_entity 13 (**2 projects**), project_knowledge 23, context_entity 10, non_project_interaction 2; +5 excluded.
- Confidence high 38 / medium 10 / low 0; endorsement conservative (4 explicit_acceptance, all user-evidenced).
- 39 relationships; 6 cross-case clusters; 5 possible-duplicates (no auto-merge).
- Attachment dedup (Fleet Command): 92 occurrences → 88 unique hashes, binaries unavailable, no GDD/SDD binary present.
- 9 missing-source impact records (do_not_infer), 143 refs covered, no findings reconstructed.
- **Benchmarks 9/9 pass**; all confirmed human resolutions (hr-001…hr-010) honored.
- **structural_validation_status: pass** (0 errors/warnings); **semantic_quality_status: conditional_pass**.
- Checksums: 130 tracked files unchanged; **no existing file modified**.

## Recommendation

Run one more (slightly larger) subscription-only pilot, then a larger subscription-only batch once
the 7 human-review questions are answered. **Not** ready for full-corpus subscription extraction or
batch-API automation yet — pending an upstream provenance refinement for mixed-origin segments and
populated attachment filenames. See `reports/pilot_report.md` for the full rationale.
