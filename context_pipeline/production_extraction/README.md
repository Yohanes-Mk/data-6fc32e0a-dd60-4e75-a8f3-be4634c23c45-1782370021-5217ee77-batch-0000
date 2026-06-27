# Production Extraction — Stage 5B

Stage 5B is the frozen-framework production extraction stage. It processes all remaining
in-scope conversations, project documents, and design chats under the Stage 5A frozen
ontology, decision rules, confirmed resolutions, and review thresholds.

## Status

- **Frozen framework version:** 5A (freeze date 2026-06-25)
- **Frozen rule count:** 23
- **Production denominator (before Batch 01):** 223 conversations, 34 project documents, 0 design chats
- **Overall status:** Batch 01 in progress

## Batch plan

| Batch | Conversations | Documents | Status |
|-------|--------------|-----------|--------|
| 01    | 75           | 0         | in_progress |
| 02    | ~60          | ~15       | pending |
| 03    | ~70          | ~5        | pending |
| 04    | ~18          | ~14       | pending |

## Evidence boundary

Source: Stage 3R (extraction_staging_repair) with Stage 3R-P (provenance_patch) overlays.
Universe: 286 conversations. Six normalized conversations outside the 286-universe are deferred.

## Do not modify

The frozen framework files in `context_pipeline/framework_freeze/` must not be altered.
Prior-stage corpus files must not be altered.
