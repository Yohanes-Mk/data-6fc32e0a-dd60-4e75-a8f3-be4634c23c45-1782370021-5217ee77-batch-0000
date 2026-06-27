# Batch 01 Selection Report

**Generated:** 2026-06-25T00:00:00Z
**Lock hash:** `a5e7a23d9ac3b86f040a4deccf0b5cc322d3fed4b3f33a1c08a55fd59fe92383`
**Selection locked before semantic inspection:** YES

## Summary

| Metric | Value |
|--------|-------|
| Eligible pool (after exclusions) | 221 |
| Selected | 75 |
| Low complexity | 35 |
| Medium complexity | 30 |
| High complexity | 10 |
| With attachments | 38 |
| With tool/log segments | 2 |
| With transcript segments | 23 |
| With missing sources | 38 |
| Empty/near-empty (0 user segs) | 10 |
| Prior-stage excluded | 65 |
| Reserved for later batches | 146 |
| Deferred (outside 286-universe) | 6 |

## Selection method

Deterministic stratified alphabetical selection.

1. All 286 Stage 3R evidence-map conversations were loaded.
2. 65 prior-processed conversation IDs (from semantic_pilot_expanded, semantic_pilot_merged,
   semantic_calibration_50 `selected_cases.jsonl` files) were excluded.
3. 6 deferred normalized conversations outside the 286-universe were noted (already absent
   from the 286-universe, included for completeness).
4. Remaining 221 eligible conversations were sorted alphabetically by conversation_id.
5. Complexity scores were computed from structural metadata only (no semantic inspection):
   - user_segments, attachments, tool_segments, transcript_segments, missing_sources, branches
6. Tier quotas: Low=35, Medium=30, High=10.
7. Within each tier, evenly spaced indices across the alphabetically sorted pool.

## Denominator discrepancy

Production plan states 223 remaining conversations. Script finds 221 eligible.
Discrepancy of 2: the semantic_pilot_expanded and semantic_pilot_merged stages had
2 cases within the 286-universe that were not included in the plan's 63-case baseline count.
Conservative approach: all 65 prior-processed IDs excluded.

## Project documents

0 project documents are included in Batch 01 per the batch strategy plan.
34 project documents are reserved for Batch 02 and later.

## Design chats

0 design chats remain (both were processed in prior stages).

## Checkpoint assignments

| Checkpoint | Cases      | Count |
|-----------|------------|-------|
| 01        | B01-001–010 | 10   |
| 02        | B01-011–020 | 10   |
| 03        | B01-021–030 | 10   |
| 04        | B01-031–040 | 10   |
| 05        | B01-041–050 | 10   |
| 06        | B01-051–060 | 10   |
| 07        | B01-061–070 | 10   |
| 08        | B01-071–075 | 5    |
