# Stage 5B-01 Checkpoint 01 — Quality Review

**Review timestamp:** 2026-06-26  
**Reviewed by:** Claude Code (claude-sonnet-4-6) — post-recovery checkpoint completion  
**Source of semantic decisions:** `case_extractions.jsonl` (authoritative, not re-derived)  
**Review scope:** Focused quality review of persisted outputs. Semantic extraction is not redone.

---

## Review Mandate

This review checks for the following failure modes across all 10 cases and 6 candidates:

- False-project classification
- Assignment promoted to project
- One-off request promoted to work entity
- Unsupported ownership claim
- Unsupported current status
- Assistant proposal treated as user decision
- External pasted content treated as user-authored fact
- Endorsement error
- Weak title (e.g., first user message used verbatim)
- Missing-source overreach (conclusions drawn from unavailable sources)
- Attachment inflation (duplicate occurrences counted multiple times)
- Unsupported relationship
- Over-merging (distinct activities collapsed into one candidate)
- Over-fragmentation (one activity split into too many candidates)
- Profile-level over-promotion (case-specific preference elevated to general profile)

---

## Findings Table

| Case ID | Reviewed Record | Issue Checked | Finding | Correction Made | Evidence Reference |
|---|---|---|---|---|---|
| B01-001 | b01c1:excl:001, excl:002, excl:003 | One-off request promoted to work entity | **No issue.** All three formatting requests correctly classified as one_off_request per hr-020. Friends' resumes correctly excluded as third-party content. No candidate created. | None required. | B01-BUNDLE-0206a1dc |
| B01-001 | (no candidate) | False-project classification | **No issue.** No project created from resume formatting requests. | None required. | hr-020 |
| B01-002 | CAND-B01C1-001 | Unsupported ownership (user_owned) | **No issue.** User directly states Accenture employment and personal I-9/TPS situation. Ownership is clearly user_owned (their own compliance obligation). | None required. | stage3r:segment:685d5c5418ee9bbeddccfb6c53f31007 |
| B01-002 | CAND-B01C1-001 | Unsupported current status | **No issue.** Status current_inferred (not current_confirmed) per hr-021. Expansion segments document active navigation steps without confirmed resolution. Temporal_status current_inferred is appropriate. | None required. | stage3r:segment:baf4cfc4b120c1fefcee716b43299177 |
| B01-002 | CAND-B01C1-001 | Candidate type check (recurring_responsibility vs. task) | **Borderline — acceptable.** The I-9/TPS compliance could be typed as a one-time task rather than a recurring_responsibility. However, immigration/work authorization compliance is structurally recurring (requires monitoring TPS status, periodic I-9 renewals). The expansion confirms ongoing monitoring intent. Classification as recurring_responsibility is defensible. | None required. Note recorded. | stage3r:segment:71138be6bfc6487f0e9cbc118a62c6da |
| B01-003 | CAND-B01C1-002 | Assignment promoted to project | **No issue.** Blade Runner reflection paper is correctly typed as assignment per hr-002. AI-detection incident does not create a project. | None required. | stage3r:segment:3743b68124371e3d107638b5d20e6747 |
| B01-003 | CAND-B01C1-002 | Weak title check | **No issue.** Title "Film Genre Course — Blade Runner Reflection Paper and AI-Detection Rewrite" accurately describes the assignment without copying the first user message verbatim. | None required. | — |
| B01-003 | CAND-B01C1-003 | Assignment promoted to project | **No issue.** Genre Movie Assignment is correctly typed as assignment per hr-002. The short film deliverable is an individual user-authored work for a graded course, not a project. | None required. | stage3r:segment:bfac9c12af276d93dae63317dffd6ba3 |
| B01-003 | CAND-B01C1-002, CAND-B01C1-003 | Over-merging (should be one candidate) | **No issue.** The two film assignments are correctly separated per hr-003. Different assignment types (reflective paper vs. short film), different date ranges (March 4/16 vs. March 26-30), and different content domains. Over-merging them would lose provenance fidelity. | None required. | hr-003 |
| B01-003 | CAND-B01C1-002, CAND-B01C1-003 | Over-fragmentation (Genre Quiz #4 as separate candidate) | **No issue.** Genre Quiz #4 (46/50) correctly subsumed into CAND-B01C1-002 rather than created as a third candidate. Quiz score is a supporting assessment within the same session and does not independently meet work-entity criteria. | None required. | recovery_audit.json Part 5 |
| B01-003 | b01c1:excl:004 | External pasted content (course transcript) treated as user-authored fact | **No issue.** Course transcript material (Film Noir, Sci-Fi, RomCom genre conventions) correctly classified as external_source_material per hr-001. Not treated as user-authored content. | None required. | hr-001 |
| B01-004 | b01c1:excl:005 | One-off request promoted to work entity | **No issue.** DCA networking request correctly classified as one_off_request per hr-020. DCA walks attendance background context correctly not elevated to a networking project. | None required. | B01-BUNDLE-07deebd3 |
| B01-005 | b01c1:excl:006 | One-off request promoted to work entity | **No issue.** Python/Homebrew troubleshooting correctly classified as one_off_request (simple_technical_troubleshooting) per hr-020. | None required. | B01-BUNDLE-0c7085d8 |
| B01-006 | b01c1:excl:007 | External pasted content (credit report data) treated as user-authored fact | **No issue.** TransUnion credit report inquiry data (SyncB/Google, Klarna, Liberty Mutual, Upgrade, Apple Card) correctly classified as external_pasted_content in excluded_interactions and evidence records. Not treated as user-authored financial activity. | None required. | stage3r:segment:797a5885d6d6b85c08c961e08ceccfd9 |
| B01-006 | b01c1:excl:007 | One-off request promoted to work entity | **No issue.** Full expansion confirmed reactive advisory assistance. No ongoing financial management initiative exists in the conversation. Correctly excluded per hr-020. | None required. | B01-BUNDLE-10a1f086 |
| B01-007 | CAND-B01C1-004 | Over-fragmentation (three Learning Logs as separate candidates) | **No issue.** Three weekly Learning Logs (Weeks 6, 7, 8) merged into one candidate (CAND-B01C1-004). All three are the same deliverable type, same course, same session. Merging is appropriate. | None required. | — |
| B01-007 | CAND-B01C1-005 | Unsupported ownership (group_owned) | **No issue.** Group composition explicitly evidenced by user statements (Owen, Naomi, Yohannes). Naomi's submitted Group Log used as source material. Group ownership is directly supported. | None required. | B01-BUNDLE-1116ed38 |
| B01-007 | CAND-B01C1-004, CAND-B01C1-005 | Attachment inflation (null-filename attachments counted multiple times) | **No issue.** Three null-filename attachments correctly treated as three source material occurrences (one each: Naomi's Group Log templates). Not counted multiple times as evidence. hr-018 applied. | None required. | hr-018, b01c1:msi:003 |
| B01-007 | CAND-B01C1-004, CAND-B01C1-005 | Missing-source overreach (conclusions drawn from null-filename attachments) | **No issue.** Null-filename attachments classified as external source material (Naomi's templates) only from user's direct statement that they are examples. No conclusions drawn from binary content (unavailable). hr-017 and hr-014 applied correctly. | None required. | hr-014, hr-017 |
| B01-007 | CAND-B01C1-005 | hr-007 trigger precision (Naomi vs. Naomie Bambara) | **Documented borderline — acceptable.** hr-007 trigger requires "Naomie Bambara appears." In B01-007 the name used is "Naomi," not "Naomie Bambara." hr-007 was applied analogously given the same course (CSCI 430), same professor (Ramnath), and same group structure as the hr-007 rule origin (cb-07). This is explicitly documented in the candidate provenance notes and rule application log (b01c1:rule:012 validation_status: conditional_pass). | None required — documented appropriately. | b01c1:rule:012 |
| B01-008 | b01c1:excl:008 | One-off request promoted to work entity | **No issue.** Power bank purchasing advice correctly classified as one_off_request (purchasing_advice) per hr-020. | None required. | B01-BUNDLE-14ab51d9 |
| B01-009 | CAND-B01C1-006 | Assistant proposal treated as user decision (Astra Fellowship, essay structure) | **No issue.** The Astra Fellowship alternative is acknowledged as a user-raised or assistant-suggested backup option and not created as a separate candidate. Essay structure suggestions and resume formatting recommendations by the assistant are typed as assistant_suggestion/assistant_draft and not promoted to user decisions per hr-019. | None required. | stage3r:segment:93fceaf3633374abed47f6636fa51d7a, hr-019 |
| B01-009 | CAND-B01C1-006 | Unsupported current status (current_inferred) | **No issue.** Status current_inferred is supported by: (1) active application preparation steps in expansion segments, (2) known future deadline (offers expected July 25, 2026), (3) essays not yet written at conversation end. All three criteria from hr-021 for current_inferred are met. | None required. | stage3r:segment:f5d0f1127fe964ea9dd9cf48b744c8eb, hr-021 |
| B01-009 | CAND-B01C1-006 | Portfolio URLs treated as facts | **No issue.** Portfolio site (https://yohanes-os.vercel.app/) and GitHub handle (Yohanes-Mk) are preserved as stated by the user. These are direct user statements, not assistant-generated content. URLs not verified against live web sources (not required); preserved as user-reported evidence. | None required. | stage3r:segment:3bf2088c138737939c831f0191156f30 |
| B01-009 | b01c1:rel:002, b01c1:rel:003 | Unsupported relationship | **No issue.** b01c1:rel:002 (CAND-B01C1-006 uses AI Aggregator) and b01c1:rel:003 (CAND-B01C1-006 informed_by BCI Lab) are both based on explicit user statements in expansion segments. AI Aggregator is confirmed as a named portfolio repo; BCI Lab supervisor is confirmed as a named reference. Relationships are not created from thematic similarity alone. | None required. | stage3r:segment:f125c291946d21b09e95ac1a4ce38d3b |
| B01-010 | (no candidate) | Forced candidate from empty conversation | **No issue.** B01-010 has 0 eligible user segments and 1 assistant segment. No candidate was created. hr-016 applied correctly. No substitution of a new case after selection lock. | None required. | B01-BUNDLE-1f4044fa, hr-016 |

---

## Summary of Corrections

**No corrections required.** All semantic decisions in `case_extractions.jsonl` were applied correctly in the output files. Two borderline notes were documented (CAND-B01C1-001 type choice, b01c1:rule:012 name-match precision) but neither requires correction — both are within frozen rule bounds and are explicitly documented in provenance.

---

## B01-006 Expansion Verification Result

**Verified: PASS.**

The actual B01-006 record in `case_extractions.jsonl` contains all required expansion fields:

| Field | Required | Actual Value | Verdict |
|---|---|---|---|
| `full_evidence_expansion_performed` | `true` | `true` | ✓ |
| `eligible_user_segments_total` | 38 | 38 | ✓ |
| `segments_in_bundle` | 20 | 20 | ✓ |
| `segments_retrieved_in_expansion` | 18 | 18 | ✓ |
| `stage3r_evidence_references_used` | 18 Stage 3R refs | 18 refs listed | ✓ |

The recovery audit prose (`recovery_audit.md` Part 3 table) also documents the B01-006 expansion correctly:

> "B01-006 | yes (18 omitted) | ✓ | 18 | 18 | no"

**No prose omission found.** The recovery-audit summary correctly includes B01-006. The instruction noted a "possible reporting omission" but inspection confirms the omission did not occur.

---

## Chronological Skew in Batch 01 Selection

### Known skew

Batch 01 (75 cases selected from 221 conversations) contains a known selection-date skew: the 10 cases in Checkpoint 01 span conversations from October 2025 through June 2026. The selection algorithm applied to a conversation corpus ordered by conversation ID (not by date), which produces a sample biased toward earlier conversation IDs regardless of actual date.

Specific observation in Checkpoint 01:
- B01-002 and B01-009 are from June 2026 (near the extraction date)
- B01-007 is from October 2025
- B01-003 is from March 2026
- B01-008 is from January 2026
- B01-005 is from February 2026
- Other cases span March–April 2026

This is not a uniform chronological sample of the user's activity.

### Does skew invalidate this checkpoint?

**No.** The chronological skew does not invalidate Checkpoint 01 for the following reasons:

1. **The selection is locked.** `selected_case_ids.json` contains a verified selection lock hash (`a5e7a23d9ac3b86f040a4deccf0b5cc322d3fed4b3f33a1c08a55fd59fe92383`). The selection was made before extraction. It cannot be revised mid-extraction.

2. **Semantic extraction is per-case.** Each case was independently extracted. The skew affects the *representativeness* of the batch but not the correctness of individual case extractions.

3. **Status discipline handles it.** Per hr-021 (current status discipline), status is not inferred from recency alone. A March 2026 assignment is correctly assigned `historical_status_unknown`, not `completed`, even if the extraction occurs in June 2026.

4. **Checkpoint 01 is a sample, not a census.** Batch 01's 75 cases are drawn from 221 conversations; Checkpoint 01 processes 10 of 75. Representativeness across the full corpus is a concern for the batch summary, not for individual checkpoint validity.

5. **No frozen rule requires uniform chronological coverage.** No frozen framework rule or confirmed resolution mandates that a checkpoint sample be temporally balanced.

### Authoritative pre-batch denominator

The authoritative count of conversations before Batch 01 selection is **221 conversations**. This is established by Stage 4 output and is not tracked in the Batch 01 registry entry directly. The registry records `selected_case_count: 75` for Batch 01. The 221-conversation denominator must be preserved when computing coverage metrics at the batch and corpus levels. It does not affect Checkpoint 01 operations.

---

## Quality Review Overall Verdict

**PASS.** No corrections required. Two borderline notes documented and filed in provenance. Checkpoint 01 output files are consistent with the semantic decisions in `case_extractions.jsonl` and compliant with the frozen framework.
