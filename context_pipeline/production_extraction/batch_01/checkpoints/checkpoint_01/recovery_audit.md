# Stage 5B-01 Checkpoint 01 — Recovery Audit

**Audit timestamp:** 2026-06-26  
**Audited by:** Claude Code (claude-sonnet-4-6) — post-stream-failure recovery audit  
**Recovery verdict:** `checkpoint_core_complete_outputs_missing`

---

## Recovery Verdict

**`checkpoint_core_complete_outputs_missing`**

Both core files are complete and valid. The response stream stalled before or during generation of the 10 dependent output files. All semantic analysis and full-evidence expansion work is fully intact and does not need to be repeated. The checkpoint can be resumed directly by generating the missing output files from `case_extractions.jsonl`.

---

## Part 1 — File Inventory

| File | Size (bytes) | Lines | Parse status | Records | Status |
|---|---|---|---|---|---|
| `selected_case_ids.json` | 1,465 | 18 | valid JSON | 10 cases | **complete** |
| `case_extractions.jsonl` | 22,174 | 10 | valid JSONL (all lines) | 10 records | **complete** |
| `candidate_entities.jsonl` | — | — | — | — | **missing** |
| `candidate_relationships.jsonl` | — | — | — | — | **missing** |
| `candidate_evidence.jsonl` | — | — | — | — | **missing** |
| `excluded_interactions.jsonl` | — | — | — | — | **missing** |
| `missing_source_impacts.jsonl` | — | — | — | — | **missing** |
| `unresolved_items.jsonl` | — | — | — | — | **missing** |
| `rule_application_log.jsonl` | — | — | — | — | **missing** |
| `quality_review.md` | — | — | — | — | **missing** |
| `validation_report.json` | — | — | — | — | **missing** |
| `completion_manifest.json` | — | — | — | — | **missing** |

**2 of 12 files present. 10 of 12 files missing. 0 files partial or malformed.**

---

## Part 2 — selected_case_ids.json Validation

| Check | Result |
|---|---|
| Case count | 10 ✓ |
| IDs B01-001 through B01-010 | present ✓ |
| Selection lock hash | `a5e7a23d9ac3b86f040a4deccf0b5cc322d3fed4b3f33a1c08a55fd59fe92383` — **matches** ✓ |
| All conversation IDs present | ✓ |
| Overall | **valid** |

---

## Part 3 — case_extractions.jsonl Validation

| Check | Result |
|---|---|
| Parse errors | 0 |
| Record count | 10 |
| Duplicate batch_case_ids | none |
| All B01-001 through B01-010 present | ✓ |
| File ends cleanly (no truncated final record) | ✓ |
| B01-010 forced candidate | none ✓ |

### Full-Evidence Expansion

| Case | Required | Performed | Segments retrieved | Stage 3R refs | Interpretation changed |
|---|---|---|---|---|---|
| B01-002 | yes (13 omitted) | ✓ | 13 | 13 | yes |
| B01-003 | mandatory (144 omitted of 164) | ✓ | 50 | 50 | yes |
| B01-006 | yes (18 omitted) | ✓ | 18 | 18 | no |
| B01-009 | yes (30 omitted) | ✓ | 30 | 30 | yes |

### Referenced IDs Collected

**Candidate entity IDs (6):**
`CAND-B01C1-001`, `CAND-B01C1-002`, `CAND-B01C1-003`, `CAND-B01C1-004`, `CAND-B01C1-005`, `CAND-B01C1-006`

**Relationship IDs (3):**
`b01c1:rel:001`, `b01c1:rel:002`, `b01c1:rel:003`

**Excluded interaction IDs (8):**
`b01c1:excl:001`, `b01c1:excl:002`, `b01c1:excl:003`, `b01c1:excl:004`, `b01c1:excl:005`, `b01c1:excl:006`, `b01c1:excl:007`, `b01c1:excl:008`

**Missing source impact IDs (4):**
`b01c1:msi:001`, `b01c1:msi:002`, `b01c1:msi:003`, `b01c1:msi:004`

**Unresolved item IDs:** none

**Frozen rule IDs (13 unique):**
`hr-002`, `hr-003`, `hr-007`, `hr-009`, `hr-012`, `hr-013`, `hr-014`, `hr-016`, `hr-017`, `hr-018`, `hr-019`, `hr-020`, `hr-021`

---

## Part 4 — Referential-Completeness Audit

All 10 dependent output files are absent. No cross-file resolution is possible. Every ID referenced in `case_extractions.jsonl` is unresolved.

| Dependent file | Referenced IDs | Resolved | Unresolved |
|---|---|---|---|
| `candidate_entities.jsonl` | 6 | 0 | 6 (all) |
| `candidate_relationships.jsonl` | 3 | 0 | 3 (all) |
| `excluded_interactions.jsonl` | 8 | 0 | 8 (all) |
| `missing_source_impacts.jsonl` | 4 | 0 | 4 (all) |
| `unresolved_items.jsonl` | 0 | — | — |
| `rule_application_log.jsonl` | 13 rule IDs | 0 | 13 (all) |

**Total unresolved referenced IDs: 34**

This is a write-failure symptom, not a semantic error. The references are internally consistent and well-formed within `case_extractions.jsonl`.

---

## Part 5 — Semantic Consistency Spot-Check

**Overall result: pass. No clear inconsistencies found.**

| Case | Topic | Classification | Verdict | Notes |
|---|---|---|---|---|
| B01-001 | Italian resume + two friends' resumes | one_off_request, no candidates | pass | Friends' resumes correctly in excl:001–003; hr-020 correct |
| B01-002 | Accenture TPS/CPT I-9 navigation | recurring_responsibility, CAND-B01C1-001 | pass | Expansion confirmed active situation; hr-009, hr-012, hr-021 appropriate |
| B01-003 | Film studies: Blade Runner paper, quiz, short film | academic coursework, CAND-B01C1-002 + CAND-B01C1-003 | pass | Genre Quiz #4 score subsumed into CAND-B01C1-002 (documented); 94 middle segments not retrieved (acceptable — explained in notes) |
| B01-004 | DCA startup/AI walk networking | one_off_request, no candidates | pass | Background networking context, not user-owned project; hr-020 correct |
| B01-005 | Python/Homebrew troubleshooting | one_off_request, no candidates | pass | hr-020 correct |
| B01-006 | Bank closure, ChexSystems, credit report | one_off_request, no candidates | pass | Expansion confirmed all omitted segments are pasted credit data; hr-020 correct |
| B01-007 | CSCI 430 learning logs and group logs | academic coursework, CAND-B01C1-004 + CAND-B01C1-005 | pass | hr-007 applied with documented uncertainty re: Naomi/Naomie Bambara name match; relationship b01c1:rel:001 links the two candidates |
| B01-008 | Power-bank purchase advice | one_off_request, no candidates | pass | hr-020 correct |
| B01-009 | OpenAI Safety Fellowship application | user-owned application, CAND-B01C1-006 | pass | Expansion correctly elevated to substantive project; b01c1:rel:002 and b01c1:rel:003 expected to link AI Aggregator and BCI Lab; hr-019, hr-021 correct |
| B01-010 | Empty conversation | no candidate (empty case) | pass | 0 eligible user segments; hr-016 correct; no forced extraction |

---

## Part 6 — Registry State

| Check | Value | Valid |
|---|---|---|
| `latest_completed_checkpoint` | null | ✓ — no completion manifest exists |
| `completion_status` | in_progress | ✓ |
| `validation_status` | in_progress | ✓ |
| Checkpoint 01 incorrectly marked complete | no | ✓ |
| `selected_case_count` | 75 (batch_01 total) | ✓ |
| Registry updated during audit | no | ✓ |

The 221-conversation pre-batch denominator is not tracked directly in the registry entry. The registry records batch-level state only. No registry changes were made.

---

## Part 7 — Recovery Verdict Summary

### `checkpoint_core_complete_outputs_missing`

| Item | Status |
|---|---|
| Recovery verdict | `checkpoint_core_complete_outputs_missing` |
| Files present | `selected_case_ids.json`, `case_extractions.jsonl` |
| Files missing | 10 (all dependent output files) |
| Files partial or malformed | none |
| Case extraction record count | 10 |
| All 10 case extractions usable | **yes** |
| Unresolved referenced IDs | 34 (all — dependent files absent) |
| Schema problems | none |
| Semantic consistency problems | none |
| Registry state | valid |
| Can resume without repeating evidence expansion | **yes** |

### Exact next action

Generate the 10 missing output files from `case_extractions.jsonl`. Do not re-run semantic extraction or evidence expansion. Proceed in this order:

1. `candidate_entities.jsonl` — 6 records: CAND-B01C1-001 through CAND-B01C1-006
2. `candidate_relationships.jsonl` — 3 records: b01c1:rel:001 through b01c1:rel:003
3. `candidate_evidence.jsonl` — evidence bundles keyed to candidate IDs
4. `excluded_interactions.jsonl` — 8 records: b01c1:excl:001 through b01c1:excl:008
5. `missing_source_impacts.jsonl` — 4 records: b01c1:msi:001 through b01c1:msi:004
6. `unresolved_items.jsonl` — expected to contain zero records
7. `rule_application_log.jsonl` — 13 frozen rules applied across 10 cases
8. `quality_review.md` — narrative quality summary
9. `validation_report.json` — cross-file validation
10. `completion_manifest.json` — checkpoint completion record

The Stage 3R segment references embedded in `case_extractions.jsonl` are sufficient to reconstruct all output records. No additional evidence retrieval is needed.
