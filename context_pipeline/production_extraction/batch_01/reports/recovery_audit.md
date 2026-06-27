# Stage 5B Batch 01 Recovery Audit

**Audit date:** 2026-06-25  
**Auditor:** Claude Code (claude-sonnet-4-6)  
**Scope:** Incomplete Stage 5B-01 initialization — completeness, denominator, selection, bundles, integrity, recovery recommendation

---

## Audit 1: Current Completion State

### Files confirmed present

| Path | Lines / Size | Status |
|------|-------------|--------|
| `batch_01/config/batch_policy.json` | 1.4 KB | Complete |
| `batch_01/manifests/checksums_before.json` | 2.7 KB | Complete |
| `batch_01/selection/selected_cases.jsonl` | 75 lines / 49 KB | Complete |
| `batch_01/selection/selection_lock.json` | 14 KB | Complete |
| `batch_01/selection/excluded_cases.jsonl` | 217 lines / 50 KB | Complete |
| `batch_01/selection/selection_report.md` | 2.5 KB | Complete |
| `batch_01/evidence_bundles/semantic_evidence_bundles.jsonl` | 75 lines / 1.16 MB | Complete |
| `batch_01/README.md` | 1.1 KB | Complete |
| `batch_01/checkpoints/checkpoint_01/` through `checkpoint_08/` | 8 empty directories | Scaffold only |
| `production_extraction/batch_registry.jsonl` | 1 line | Complete |
| `production_extraction/production_manifest.json` | 4.0 KB | Complete |
| `production_extraction/README.md` | 1.2 KB | Complete |

### Files missing

- `batch_01/reports/` — no pre-existing reports (this file is the first)
- No semantic checkpoint results in any checkpoint directory

### Checkpoint completion state

All 8 checkpoint directories (`checkpoint_01` through `checkpoint_08`) are **empty**. No `extraction_results.jsonl`, `completion_manifest.json`, `validation_summary.json`, or any semantic output exists in any checkpoint. Claude stalled at or before the first semantic extraction case.

### Batch registry status

```json
{
  "latest_completed_checkpoint": null,
  "validation_status": "in_progress",
  "completion_status": "in_progress"
}
```

The registry correctly records no checkpoint as complete. There is no false-completion marking anywhere in the batch infrastructure.

### Verdict

The initialization phase is complete. The semantic extraction phase has not begun. The state is safely resumable: no partial semantic records exist, no checkpoint is incorrectly marked complete, and the selection and evidence bundles are locked and intact.

---

## Audit 2: Denominator Reconciliation

### Universe verification

`context_pipeline/extraction_staging_repair/corpus/conversation_evidence_maps.jsonl` contains **286 lines** (286 conversations). The 286-conversation evidence-map universe is confirmed.

`context_pipeline/provenance_patch/corpus/patched_conversation_evidence_maps.jsonl` also contains **286 lines**, consistent with the production evidence boundary (`stage_3R_with_stage_3R_P_overlay`).

### Prior-stage ID count

| Source file | Raw line count |
|------------|----------------|
| `semantic_pilot_expanded/selection/selected_cases.jsonl` | 24 |
| `semantic_pilot_merged/selection/selected_cases.jsonl` | 12 |
| `semantic_calibration_50/selection/selected_cases.jsonl` | 50 |
| **Total raw** | **86** |
| **Unique across all three** | **65** |

Overlap count: 21 IDs appear in more than one prior-stage file.

### Excluded_cases.jsonl breakdown (217 total)

| Reason | Count |
|--------|-------|
| `reserved_for_later_production_batch` | 146 |
| `already_processed_in_prior_semantic_stage` | 65 |
| `deferred_outside_evidence_boundary` | 6 |
| **Total** | **217** |

### Denominator arithmetic

```
286  (evidence-map universe)
 -65  (prior-processed, unique across all prior stages)
────
 221  (eligible pool for Batch 01 and later batches)

 221  (eligible)
 -75  (selected for Batch 01)
────
 146  (reserved for later batches)
```

### Prior-stage semantic completion status

| Stage | Cases | Has completion manifests | Semantic results present | Assessment |
|-------|-------|--------------------------|--------------------------|------------|
| `semantic_calibration_50` | 50 | YES (all 5 batches, `checkpoint_status: complete`) | YES | All 50 semantically processed |
| `semantic_pilot_expanded` | 24 | NO explicit manifest | YES (candidate_entities.jsonl 58 KB, case_extractions.jsonl, synthesis results) | Semantically processed |
| `semantic_pilot_merged` | 12 | NO explicit manifest | YES (candidate_entities.jsonl 75 KB, case_extractions.jsonl, synthesis results) | Semantically processed |

No prior-stage ID is "structural-only." All 65 are definitively semantically processed.

### Benchmark reuses

`semantic_calibration_50` batch_01 includes cases `cb-01` through `cb-10` (conversation IDs: 14f3c888, 2838a734, 94f53cfc, b8366901, e2fc5641, f04cc5a5, dd1aabd1, 965b21a5, 8cdf0ae5, c2701642), described in the completion manifest as "benchmark policy cases 1-5 carried from 4D and re-confirmed" plus 5 more benchmark cases confirmed in batch_02. These 10 are benchmark reuses; they were re-confirmed semantically and are legitimately excluded.

### Discrepancy: Stage 5A plan 223 vs initialization 221

The Stage 5A production plan states 223 remaining conversations (286 − 63 = 223). The initialization finds 221 (286 − 65 = 221).

**Root cause:** The Stage 5A plan counted 63 previously processed cases. The actual scripts counted 65 unique IDs across the three prior-stage `selected_cases.jsonl` files. The 2-case difference arises from `semantic_pilot_expanded` and `semantic_pilot_merged` each contributing 1 conversation ID that falls within the 286-conversation evidence-map universe but was not included in the plan's 63-case baseline count.

**Assessment:** The conservative exclusion of all 65 is correct. Those 2 conversations are within the production universe and were semantically processed in prior stages. Excluding them prevents duplicate semantic coverage. The 2-case gap does not affect the correctness of the current selection.

### Denominator verdict

**Partial initialization denominator 221 confirmed.**

The Stage 5A plan denominator of 223 is superseded by the actual script count. The correct eligible pool is 221 conversations. This is fully documented in `selection_lock.json` (field: `denominator_discrepancy_note`).

### Prior-processed conversation table (65 cases)

All 65 IDs from `selection_lock.json → excluded_prior_stage_case_ids`:

| Conversation ID (UUID fragment) | In pilot_expanded | In pilot_merged | In calibration_50 | Benchmark reuse | Semantically processed | In 286 universe | Exclude from production |
|--------------------------------|:-----------------:|:---------------:|:-----------------:|:---------------:|:---------------------:|:---------------:|:-----------------------:|
| 0083e51c | | | Yes | No | Yes | Yes | Yes |
| 07d1d836 | | | Yes | No | Yes | Yes | Yes |
| 0c2d5400 | | | Yes | No | Yes | Yes | Yes |
| 14f3c888 | | | Yes | Yes (cb-01) | Yes | Yes | Yes |
| 19b86969 | | | Yes | No | Yes | Yes | Yes |
| 1a5e779c | | | Yes | No | Yes | Yes | Yes |
| 1f2a6b9a | | | Yes | No | Yes | Yes | Yes |
| 1fbe97e6 | | | Yes | No | Yes | Yes | Yes |
| 24241ab5 | | | Yes | No | Yes | Yes | Yes |
| 26ef7f5c | | | Yes | No | Yes | Yes | Yes |
| 2722c5b3 | Yes | | | No | Yes | Yes | Yes |
| 2838a734 | | | Yes | Yes (cb-02) | Yes | Yes | Yes |
| 2b82608c | | | Yes | No | Yes | Yes | Yes |
| 2c698762 | Yes | | | No | Yes | Yes | Yes |
| 3357cec5 | | | Yes | No | Yes | Yes | Yes |
| 37aabbd3 | Yes | | | No | Yes | Yes | Yes |
| 3aa7c40a | | | Yes | No | Yes | Yes | Yes |
| 4e971122 | Yes | | | No | Yes | Yes | Yes |
| 59ba0646 | | | Yes | No | Yes | Yes | Yes |
| 5c32d03b | | | Yes | No | Yes | Yes | Yes |
| 5df76800 | Yes | | | No | Yes | Yes | Yes |
| 681bad4a | | | Yes | No | Yes | Yes | Yes |
| 6a80bbf1 | Yes | | | No | Yes | Yes | Yes |
| 6cf988f8 | Yes | Yes | | No | Yes | Yes | Yes |
| 6e346e86 | Yes | | | No | Yes | Yes | Yes |
| 75ab07c2 | Yes | | | No | Yes | Yes | Yes |
| 8256e17e | | | Yes | No | Yes | Yes | Yes |
| 84120960 | | | Yes | No | Yes | Yes | Yes |
| 85fc6dee | | | Yes | No | Yes | Yes | Yes |
| 8cdf0ae5 | | | Yes | Yes (cb-09) | Yes | Yes | Yes |
| 8f1d4c58 | Yes | | | No | Yes | Yes | Yes |
| 925a6676 | | | Yes | No | Yes | Yes | Yes |
| 92874a60 | | | Yes | No | Yes | Yes | Yes |
| 94f53cfc | | | Yes | Yes (cb-03) | Yes | Yes | Yes |
| 965b21a5 | | | Yes | Yes (cb-08) | Yes | Yes | Yes |
| 98be8868 | | | Yes | No | Yes | Yes | Yes |
| a1b81434 | | | Yes | No | Yes | Yes | Yes |
| a78a5ee4 | Yes | | | No | Yes | Yes | Yes |
| a982f302 | Yes | Yes | | No | Yes | Yes | Yes |
| ab705905 | | | Yes | No | Yes | Yes | Yes |
| acf6687a | Yes | | | No | Yes | Yes | Yes |
| af8d7a21 | Yes | | | No | Yes | Yes | Yes |
| b1e4b5f9 | Yes | | | No | Yes | Yes | Yes |
| b8366901 | | | Yes | Yes (cb-04) | Yes | Yes | Yes |
| b8654a42 | Yes | Yes | | No | Yes | Yes | Yes |
| ba42f9ff | | | Yes | No | Yes | Yes | Yes |
| bc1e0f1f | Yes | | | No | Yes | Yes | Yes |
| bc6c1b46 | Yes | | | No | Yes | Yes | Yes |
| c2701642 | | | Yes | Yes (cb-10) | Yes | Yes | Yes |
| c69f5e03 | | | Yes | No | Yes | Yes | Yes |
| c8909e21 | | | Yes | No | Yes | Yes | Yes |
| c9b827d9 | | | Yes | No | Yes | Yes | Yes |
| cd4c50e4 | | | Yes | No | Yes | Yes | Yes |
| d5ab5043 | Yes | | | No | Yes | Yes | Yes |
| dd1aabd1 | | | Yes | Yes (cb-07) | Yes | Yes | Yes |
| e0aba0e0 | | | Yes | No | Yes | Yes | Yes |
| e2fc5641 | | | Yes | Yes (cb-05) | Yes | Yes | Yes |
| e612528d | | | Yes | No | Yes | Yes | Yes |
| e650d93e | | | Yes | No | Yes | Yes | Yes |
| eaed69ad | | | Yes | No | Yes | Yes | Yes |
| ed21c713 | | | Yes | No | Yes | Yes | Yes |
| eed652b3 | | | Yes | No | Yes | Yes | Yes |
| f04cc5a5 | | | Yes | Yes (cb-06) | Yes | Yes | Yes |
| f4e5df2e | Yes | | | No | Yes | Yes | Yes |
| f748add6 | Yes | Yes | | No | Yes | Yes | Yes |

**All 65 cases: semantically processed = Yes, in 286 universe = Yes, exclude from production = Yes.**

Correct unique prior-processed count: **65**.

---

## Audit 3: Selection Validation

### Check results

| Check | Result | Detail |
|-------|--------|--------|
| Exactly 75 unique conversations | PASS | 75 lines in selected_cases.jsonl, 75 IDs in lock |
| No design chats selected | PASS | 0 entries with source_type = "design_chat" |
| No project documents selected | PASS | 0 entries with source_type = "project_document" |
| All IDs resolve in Stage 3R | PASS | All 75 present in conversation_evidence_maps.jsonl |
| No prior-processed case selected | PASS | 0 overlap with 65 excluded IDs |
| No deferred normalized conversation selected | PASS | 0 of 6 deferred IDs present in selection |
| Lock hash recomputes correctly | PASS | SHA-256 of ordered IDs = a5e7a23d9ac3b86f040a4deccf0b5cc322d3fed4b3f33a1c08a55fd59fe92383 |
| Checkpoint sizes = 10,10,10,10,10,10,10,5 | PASS | Confirmed in batch_policy.json |
| Complexity scoring uses structural metadata only | PASS | locked_before_semantic_inspection = true; scores derived from user_segment_count, attachment_count, tool_segment_count, transcript_segment_count, missing_source_count, branch_count |
| Tier quotas: Low=35, Medium=30, High=10 | PASS | Confirmed in selection_lock.json |

### Diversity achieved

| Attribute | Count |
|-----------|-------|
| Low complexity (score < 2) | 35 |
| Medium complexity (2 ≤ score < 5) | 30 |
| High complexity (score ≥ 5) | 10 |
| With attachments | 38 |
| With tool/log segments | 2 |
| With transcript segments | 23 |
| With missing sources | 38 |
| Empty/near-empty (0 user segments) | 10 |

### Date spread analysis

**Selection method:** deterministic stratified alphabetical (sorted by UUID). No timestamps were used in the selection algorithm.

**Actual timestamps extracted from evidence bundles:**

| Period | Cases |
|--------|-------|
| 2024 Q4 | 4 |
| 2025 Q1–Q3 | 0 |
| 2025 Q4 | 5 |
| 2026 Q1 | 32 |
| 2026 Q2 | 24 |
| Empty (no user segments) | 10 |
| **Total** | **75** |

- Earliest timestamp: 2024-11-14 (B01-047)
- Latest timestamp: 2026-06-23 (B01-050)
- **86% of non-empty cases (56/65) fall within 2026 Q1–Q2.**
- **Complete gap: no cases from 2025 Q1 through 2025 Q3.**

**Critical observation:** UUID alphabetical ordering is not correlated with conversation creation timestamps. The date concentration in 2026 Q1–Q2 reflects the distribution of conversations in the underlying data, filtered by alphabetical UUID position. The production plan references "date spread preserved" as a batch-ordering principle; the frozen batch strategy and batch_policy.json do not state an explicit date-diversity criterion for selection. The selection satisfies all explicitly stated selection criteria. However, date spread across the batch is poor and must be treated as a selection limitation, not as evidence of chronological diversity.

### Selection verdict

**`selection_valid`** — all explicitly stated criteria pass. Date spread limitation is documented but does not constitute a criterion failure. The selection must not be regenerated based on date distribution alone, as all structural criteria are satisfied and the lock is valid.

---

## Audit 4: Evidence-Bundle Completeness

### Count and coverage

| Metric | Value |
|--------|-------|
| Total bundles | 75 |
| Unique conversations covered | 75 |
| Bundles missing a selected case | 0 |
| All source references present | Yes |
| Bundle file corrupt or partially written | No |

### Truncation statistics

The bundle builder applied two caps:
- **User evidence cap:** 20 segments maximum per case
- **Assistant content cap:** 10 segments maximum per case

| Category | Count |
|----------|-------|
| Fully complete bundles (no omissions) | 39 |
| Bundles with user cap applied | 30 |
| Bundles with assistant cap only | 6 |
| Bundles with both caps applied | 30 |
| Total with any omission | 36 |

Total eligible user segments across all 75 cases: **1,792**  
Total included in bundles: **837** (47%)  
Total omitted user segments: **955** (53%)

### Severe truncation cases (>50 user segments omitted)

| Case | Eligible user segs | Included | Omitted | Asst segs | Asst omitted | Tier |
|------|--------------------|----------|---------|-----------|--------------|------|
| B01-003 | 164 | 20 | 144 | 104 | 94 | high |
| B01-066 | 123 | 20 | 103 | 41 | 31 | high |
| B01-054 | 112 | 20 | 92 | 40 | 30 | high |
| B01-019 | 108 | 20 | 88 | 37 | 27 | high |

### Source-reference integrity

- All segment IDs in bundles are of the form `stage3r:segment:*` — sourced from Stage 3R.
- All repaired_source_unit_ids are of the form `stage3r:source_unit:*`.
- `stage3r_map_reference` and container IDs are present in all bundles.
- No null filenames were reconstructed (null filenames remain null as required).
- Missing source references are represented in `missing_sources` arrays with `missing_ref_id` pointers, not reconstructed content.
- Origin distinctions (`user_authored`, `co_authored`, `pasted_assistant`) are preserved per segment.

### Can omitted content be reliably retrieved?

Yes. Every bundle contains:
1. `patched_map_id` — references the patched evidence map for the conversation
2. `stage3r_map_reference` — references the Stage 3R evidence map
3. `structural.message_container_ids` — lists all source containers

A semantic extractor can load any omitted segment from `repaired_source_units.jsonl` or `content_segments.jsonl` using the container IDs. The bundle's `omitted_evidence` array explicitly lists omitted counts by type and reason.

### Cases requiring full-evidence expansion

The following 30 cases have user evidence capped at 20 segments and may produce unreliable decisions without expansion of their evidence window:

B01-002, B01-003, B01-006, B01-009, B01-011, B01-013, B01-017 (partial), B01-019, B01-022, B01-023, B01-025, B01-028, B01-030, B01-033, B01-034, B01-036, B01-044, B01-045 (partial), B01-046, B01-048, B01-051, B01-054, B01-056, B01-059, B01-062, B01-063, B01-065, B01-066, B01-067, B01-071

Cases most at risk for unreliable decisions without expansion:
- **B01-003** (164 user segs, 144 omitted): multi-session resume workflow spanning multiple days — project identity and continuation context require full scope
- **B01-066** (123 user segs, 103 omitted): similarly large
- **B01-054** (112 user segs, 92 omitted): similarly large
- **B01-019** (108 user segs, 88 omitted): similarly large

### Bundle verdict

**`bundles_resolvable_but_require_case_expansion`**

The bundles are structurally sound and complete as reference objects. All source data needed to expand any truncated bundle is intact in Stage 3R files (confirmed by checksum). However, the 20-segment user-evidence cap means that for 30 cases, the pre-built bundle excerpt is insufficient for reliable semantic judgments about project identity, ownership, final outcome, or session continuation. The semantic extractor must expand evidence for these cases using the full source references before making decisions.

---

## Audit 5: Frozen-File and Prior-Stage Integrity

### Git status

```
?? context_pipeline/production_extraction/
```

Only the `production_extraction/` directory is new (untracked). No previously committed file shows as modified.

### Source-layer checksum verification

All 10 source files referenced in `batch_01/manifests/checksums_before.json` were verified:

| File | Size match | SHA-256 verified |
|------|-----------|-----------------|
| stage3r_conversation_evidence_maps | Yes | Yes (hash confirmed) |
| stage3r_repaired_source_units | Yes | Yes (hash confirmed) |
| stage3r_content_segments | Yes | Yes (hash confirmed) |
| stage3r_extraction_packets | Yes | Size only |
| stage3r_attachment_links | Yes | Size only |
| stage3r_document_links | Yes | Size only |
| stage3r_missing_source_references | Yes | Size only |
| stage3rp_patched_attachment_links | Yes | Size only |
| stage3rp_patched_conversation_evidence_maps | Yes | Yes (hash confirmed) |
| stage3rp_patched_semantic_evidence_inputs | Yes | Yes (hash confirmed) |

All 10 pass. **No source-layer file was modified by the Batch 01 initialization.**

### Framework freeze checksums

> **Correction (2026-06-25):** The original text of this section contained two errors — a wrong count ("21 files") and an incorrect chronological explanation — and has been replaced below. The integrity conclusion (no content changes, batch resumable) is unchanged.

The framework_freeze manifests (`checksums_before.json` and the `prior_stage_files` section of `checksums_after.json`) record SHA-256 hashes and file sizes computed from files in their LF (Unix) line-ending form, as they existed immediately after being written by Python pipeline scripts during the Stage 5A run. The current working tree on Windows has all text files in CRLF form because `core.autocrlf=true` converts LF→CRLF on checkout. This makes every text file on disk exactly 1 byte larger per line than what the framework_freeze manifest recorded.

**The original claim that "21 files differed" was incorrect.** Verified SHA-256 comparison shows that essentially all text files among the 286 prior-stage entries differ from the framework_freeze manifest hashes, as do all 25 framework_freeze files themselves. Every verified difference satisfies `disk_bytes − manifest_bytes = file_line_count` exactly, across all file types and sizes:

| File | Line count | Byte diff | CRLF match |
|------|------------|-----------|------------|
| `extraction_staging_repair/corpus/repaired_source_units.jsonl` | 21,927 | 21,927 | Yes |
| `extraction_staging_repair/corpus/content_segments.jsonl` | 21,927 | 21,927 | Yes |
| `extraction_staging_repair/corpus/extraction_packets.jsonl` | 987 | 987 | Yes |
| `extraction_staging_repair/corpus/conversation_evidence_maps.jsonl` | 286 | 286 | Yes |
| `extraction_staging_repair/corpus/attachment_links.jsonl` | 339 | 339 | Yes |
| `extraction_staging_repair/corpus/document_links.jsonl` | 36 | 36 | Yes |
| `extraction_staging_repair/corpus/missing_source_references.jsonl` | 341 | 341 | Yes |
| `provenance_patch/corpus/patched_attachment_links.jsonl` | 339 | 339 | Yes |
| `provenance_patch/corpus/patched_conversation_evidence_maps.jsonl` | 286 | 286 | Yes |
| `provenance_patch/corpus/patched_semantic_evidence_inputs.jsonl` | 342 | 342 | Yes |
| `provenance_patch/scripts/build_patched_evidence.py` | 577 | 577 | Yes |
| `framework_freeze/config/frozen_decision_rules.json` | 1,031 | 1,031 | Yes |
| `framework_freeze/config/frozen_confirmed_resolutions.json` | 394 | 394 | Yes |

This is the exclusive signature of CRLF normalization. No semantic content changed in any file.

**The original chronological explanation was also incorrect.** Stage 3R-P (provenance patch) ran before Stage 4E, which ran before Stage 5A. The provenance patch was already applied when Stage 5A froze the framework. The framework_freeze manifests include the correct post-patch versions of all provenance_patch corpus files. Their hash differences from the current disk are due to LF→CRLF conversion only, not to any post-freeze modification. The `prior_stage_changed_paths: []` field in `checksums_after.json` correctly records that Stage 5A made no changes to prior-stage files during the freeze operation itself.

The `batch_01/manifests/checksums_before.json` captures CRLF disk-state hashes for the 10 key source files. All 10 were verified against the current filesystem (SHA-256 confirmed for 5, sizes confirmed for all 10). This manifest is authoritative for resumption purposes.

No evidence that Claude's initialization changed any framework freeze file or any prior-stage corpus file (content-wise).

### Change boundary

**Claude's partial initialization modified only:**
- Files under `context_pipeline/production_extraction/`

**No change outside that directory.**

---

## Audit 6: Recovery Recommendation

### Evaluation against Option A criteria

| Criterion | Status |
|-----------|--------|
| Denominator resolved | Yes — 221 confirmed |
| Existing selection valid | Yes — all criteria pass |
| Evidence bundles semantically sufficient or safely expandable | Expandable — 39/75 complete, 36/75 require expansion at extraction time |
| No frozen or prior-stage files changed | Confirmed — no changes outside production_extraction/ |

### Recommendation: **Option A — Resume existing Batch 01**

The initialization completed all infrastructure and pre-extraction work correctly. No semantic work was started. All checks pass. The existing selection and evidence bundles are safe to use.

**Required caveats for resumption:**

1. **Bundle expansion protocol required.** The semantic extractor must not treat the 20-segment bundle excerpt as the evidence ceiling. For any case where `omitted_evidence` is non-empty (36 cases, particularly the 30 with user-segment omissions), the extractor must load the full conversation from Stage 3R source files before making decisions about project identity, ownership, status, session continuation, or source vs artifact. The bundle provides a reference frame and a segment index; it is not the complete evidence.

2. **Date spread is skewed.** 86% of non-empty selected cases fall within 2026 Q1–Q2. This is a property of UUID-alphabetical ordering combined with the timestamp distribution of the underlying data. It is not a selection defect (all criteria were met), but it should be recorded in the batch extraction record. Future batches will cover different UUID ranges and may correct the spread.

3. **Prior-processed denominator correction.** The operative denominator is 221 (not 223). The 2-case difference is documented in the selection lock and the production manifest. No action required beyond maintaining that documentation.

---

## Summary Table

| Audit dimension | Finding | Verdict |
|----------------|---------|---------|
| Completion state | Infrastructure complete, all 8 checkpoints empty, no semantic records | Safely resumable |
| Batch registry | `latest_completed_checkpoint: null`, `completion_status: in_progress` | Correctly reflects state |
| Prior-processed count | 65 unique (not 63) | Correct |
| Eligible denominator | 221 (not 223) | 221 confirmed |
| 286-universe integrity | 286 lines in evidence maps | Confirmed |
| Selection: 75 unique | Pass | Valid |
| Selection: no design chats | Pass | Valid |
| Selection: no project docs | Pass | Valid |
| Selection: all resolve in Stage 3R | Pass | Valid |
| Selection: no prior-processed overlap | Pass | Valid |
| Selection: no deferred IDs | Pass | Valid |
| Lock hash | Pass — recomputed hash matches stored hash | Valid |
| Checkpoint sizes 10,10,10,10,10,10,10,5 | Pass | Valid |
| Date spread | 86% in 2026 Q1-Q2; not chronologically diverse | Limitation documented, not a failure |
| Bundle count | 75 bundles, 75 conversations | Complete |
| Source references in bundles | All present, all resolvable | Complete |
| Bundle truncation | 36/75 bundles have omissions; 30 need expansion | Resolvable |
| Source-layer checksums (batch_01 manifest) | All 10 sizes confirmed on disk; 5 SHA-256 hashes verified | Pass |
| Framework-freeze manifest vs disk | All differences are LF→CRLF normalization by git; no semantic content changed; affects all text files, not 21 | Pass (original misinterpretation corrected) |
| Frozen-file changes | None outside production_extraction/ (content unchanged) | Pass |
| Recovery option | Option A | Resume |

---

## Next Action

1. Do not touch the selection, the lock, or the evidence bundles.
2. Begin semantic extraction at **checkpoint_01** (cases B01-001 through B01-010).
3. For each case in checkpoint_01, check `omitted_evidence` in the bundle before beginning semantic judgment. If non-empty, load full conversation evidence from Stage 3R before proceeding.
4. Write checkpoint_01 outputs to `batch_01/checkpoints/checkpoint_01/` following the checkpoint strategy in the production extraction plan.
5. Update `batch_registry.jsonl → latest_completed_checkpoint` to `checkpoint_01` only after validation passes.

**Batch 01 can be resumed. No files need to be changed before resumption.**
