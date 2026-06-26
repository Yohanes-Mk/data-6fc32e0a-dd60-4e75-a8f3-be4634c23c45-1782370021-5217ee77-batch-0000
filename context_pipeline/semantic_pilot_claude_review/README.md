# Stage 4B — Independent Claude Code Semantic Cross-Review

This directory contains an independent, blind semantic extraction over the same eight
selected conversation bundles used by the Stage 4A-R Codex repair, followed by a
candidate-level cross-review of the two outputs.

All semantic decisions (what is a project, what knowledge type, confidence, endorsement,
relationships) were made by the language model reading the bundles. Scripts only read/write
JSONL, resolve references, count, checksum, and validate.

## Method

- **Phase 1 (blind):** read only `selected_conversations.jsonl` and
  `conversation_context_bundles.jsonl`. Produced the blind extraction and self-review, then
  checksum-locked it (`manifests/blind_extraction_lock.json`) **before** reading any Codex
  result/audit/report. Anti-anchoring respected.
- **Phase 2 (compare):** read the Codex `results/`, `audit/`, `reports/`, schema, and policy;
  produced alignment, missing-from lists, disputes, a human-review queue, and metrics.

## Layout

- `config/review_policy.json` — review policy for this stage.
- `schemas/` — Claude candidate schema (markdown + JSON Schema).
- `blind_extraction/` — Phase-1 outputs (candidates, relationships, excluded, conversation
  completeness, unresolved items).
- `comparison/` — Phase-2 alignment, missing-from-codex / missing-from-claude, disputes,
  human-review queue, relationship alignment.
- `reports/` — blind extraction report, cross-review report, semantic quality (self) review,
  review sample, validation report.
- `manifests/` — repair checksums before/after (immutability proof) + blind-extraction lock.
- `scripts_validate.py` — self-contained structural validator (no external packages).

## Key results

- Claude: **43 entities + 4 non-knowledge, 41 relationships, 2 strict projects, 9 context entities.**
- Codex: **21 entities + 22 non-knowledge, 12 relationships, 6 projects, 0 context entities.**
- Codex false positives: **1 false project (14f3c888)** and **1 over-merge (94f53cfc)**; all 6
  project titles copy message openings; rich projects are under-extracted to a 1-project template.
- Claude self-introduced risks (the 94f53cfc umbrella, cross-conversation identity, the
  assistant-inferred Accenture role) are flagged, not asserted.
- **Structural validation:** pass. **Semantic review:** conditional_pass.
- **Checksums:** Stage 4A-R repair directory unchanged (22/22 files identical before & after);
  no existing file changed.

## Final recommendation

**Merge both schemas before another pilot.** Adopt the Codex repair's policy/schema spine
(strict project test, discard reasons, specific relationship types, conservative endorsement,
checksum/immutability discipline) but **add the granularity and execution Claude demonstrated**:
the broader work-entity ontology (assignment / job_application / exam_preparation / initiative /
recurring_responsibility), context entities, the full project-knowledge type set with descriptive
canonical titles, calibrated confidence (use low), per-project temporal status, and
provenance-correct handling that never mislabels assistant/tool text as user tasks.

**Readiness:** Not ready for a larger subscription-only batch or full-corpus extraction yet, and
not ready for later API automation. Run **one more small subscription-only pilot** on the merged
schema (with the strict project test, descriptive-title rule, and semantic-not-template extraction
enforced, and the eight human-review questions resolved). Re-using the Codex repair output as-is
for the database is not advised; re-using its schema, with Claude-style extraction, is.
