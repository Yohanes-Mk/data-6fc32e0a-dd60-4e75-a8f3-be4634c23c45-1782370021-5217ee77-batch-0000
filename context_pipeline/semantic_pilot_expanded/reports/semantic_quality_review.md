# Stage 4D — Semantic Quality Review

Every candidate and relationship was reviewed against the Part-15 defect checklist. Defects and
their resolutions are documented (separate from structural validation).

## Defects found and resolved

| # | Defect class | Where | Resolution |
|---|---|---|---|
| D1 | Co-authorship confusion (risk) | ex-06 / ex-19 Client Radar | Audit content marked `co_authored_flag=true` per 3R-P; endorsement kept `implicit_continuation`/`modification`, not blanket acceptance; sentence-level authorship left unresolved. |
| D2 | Over-merge risk (multi-session engagement) | ex-06 ↔ ex-19 | Modeled as a `phase_relationship` cluster (later manager-facing phase), `part_of` link with review flag — not collapsed and not split into unrelated entities. |
| D3 | Wrong umbrella merge | Accenture (ex-06/09/19/22) | `shared_context_only` cluster: one employer entity referenced by distinct activities (client engagement, onboarding workflow, summary task). Per 3R-P, Client Radar is NOT merged with interview prep/onboarding. |
| D4 | Content-origin confusion | ex-08, ex-16, ex-21, ex-22 | Pasted console errors, notebook run-logs, and assistant task-dumps excluded as tool/assistant content; ex-08 flagged assistant_origin (only assistant content present). |
| D5 | Attachment inflation | ex-05 (92 occ) | Occurrences (92) vs unique hashes (88) reported separately; 0 filenames preserved null (not invented); binaries marked unavailable/not inspected. |
| D6 | Filename invention (risk) | ex-16, ex-19 | Only the 3R-P-populated filenames (Project3.pdf, a11y_issues.md, etc.) were used; null filenames in ex-21/ex-05 kept null. |
| D7 | Incorrect temporal status | ex-05, ex-21, ex-02 | Set `historical_status_unknown` with `status_current_confidence=low` (no current inference from date); only ex-04 roadmap is `current_confirmed` (hr-007). AVATAR referenced in ex-17 fixed to historical_confirmed. |
| D8 | False project (risk) | ex-08/10/11/12/13/14/16/20/21 | None classified as project; typed as one-off / exam_prep / assignment / standalone_idea as appropriate. Only 2 strict projects total. |
| D9 | Identity/profile confusion | ex-16 (Naomie Bambara) | Recorded the assignment with a `contradiction` flag and an unresolved item; profile not asserted; flagged for human review. |
| D10 | Missing-source overreach | ex-05/06/16/19/21/04 | 6 impact records, all `do_not_infer:true`; no findings/contents/screenshots reconstructed. |
| D11 | Vague relationship risk | marketing (ex-18/23/24), profile preference | Used `associated_with`/`informed_by` with low confidence + review flags and an `insufficient_evidence` cluster rather than asserting one entity. |
| D12 | Empty-case handling | ex-07, ex-15 | Recorded as `unresolved_items` (empty), not substituted, not forced into a candidate. |
| D13 | Over-promotion to profile level | voice preference, AI tooling | Promoted only on cross-case recurrence (ex-02/06/17 for voice; ex-05/06/21/22 for tooling); one-time statements not globalized. |

## Checked, no defect
- **Fragmentary titles:** none (validator enforces banned list).
- **Irrelevant context entities:** context entities (Accenture employer, SCSU institution, Lauren,
  Claude Code/Todoist tools) are all engagement-relevant.
- **Duplicate candidates:** none within a case; cross-case near-duplicates surfaced as clusters.
- **Over-fragmentation:** the six academic assignments are genuinely distinct courses/terms, not a split of one.

## Confidence calibration note (Part 7)
`confidence`: high 24 / medium 10 / low 1. The separate `status_current_confidence` axis is
distributed high 8 / medium 19 / low 8 — low is used wherever current status is genuinely
unresolved (Fleet Command, pesticide, group project, Client Radar). The single `confidence=low`
candidate (ex-12 ambiguous fragment) plus the eight low `status_current_confidence` values satisfy
the requirement that low confidence not be absent; it is applied only where evidence/status truly
warrant it.

## Residual risks (to human review)
ex-06/ex-19 phase merge; Accenture shared-context separation; ex-16 author identity; ex-18 marketing
cluster; ex-23 document authorship/link. All flagged in `human_review_queue.md`.

**Semantic quality status: conditional_pass.**
