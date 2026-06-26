# Stage 4C — Semantic Quality Review

Every candidate and relationship was reviewed against the Part-13 defect checklist. Real
defects and how they were resolved are recorded below (this is separate from structural
validation; it does not report "zero defects because the schema validates").

## Defects found and resolved

| # | Defect class | Where | Resolution |
|---|---|---|---|
| D1 | Wrong work-entity granularity (risk) | mc-08 / mc-09 Client Radar | Both are the same engagement seen from two sides. Resolved by typing both `client_engagement`, linking mc-09 `part_of` mc-08, and flagging the merge in a cluster + human-review queue rather than emitting one or three entities. |
| D2 | Over-merge risk | mc-11 ↔ mc-05 Fleet Command | Same project across two conversations/time. Resolved as `subproject` + `part_of` parent-child cluster, NOT collapsed into one candidate, and flagged for review. |
| D3 | Assistant-origin confusion | mc-09 architecture finding; mc-04 ExamPro skip; mc-11 null-DeckManager decision | All set `assistant_origin=true`, endorsement `implicit_continuation`, and (ExamPro) typed `proposed_decision` per hr-005 — never user decisions/facts. |
| D4 | Mixed-origin "user evidence" | mc-10 (GitHub issue listings) ; mc-11 (Codex plan) ; mc-09 (pasted console error) | The pasted listings/plans/errors were excluded as `tool_execution_trace` / `assistant_draft`; candidates rest only on genuine user authorship. mc-10's lab effort kept at medium confidence because direct user evidence is thin. |
| D5 | Source vs artifact | mc-07 roadmap doc; mc-05 GDD/SDD | mc-07 typed `source` (third-party authored by Dave Ebbelaar), not artifact; GDD/SDD typed `source` per hr-010. |
| D6 | Incorrect temporal status (risk) | mc-05 Fleet Command, mc-06 Tsotsi | Both set `historical_status_unknown` per hr-008/hr-009; not marked current. Only the roadmap (mc-04) is `current_confirmed` (hr-007). |
| D7 | Repeated-attachment inflation | mc-05 (92 occurrences) | Occurrences (92) reported separately from unique content (88 hashes); evidence weight uses unique content; binaries marked unavailable; no GDD/SDD binary directly present. |
| D8 | Missing-source overreach | all attachment-heavy cases | 9 impact records with `do_not_infer:true`; no research findings reconstructed (e.g. mc-04 deep-research results left unrecovered). |
| D9 | Unsupported claim (employer) | Accenture | Now grounded in hr-006 (confirmed Technology Summer Analyst, start 2026-06-08) rather than inferred; the Stage-4B low-confidence inference is superseded by the confirmed resolution. |
| D10 | Possible over-fragmentation | mc-03 (5 activities) vs hr-003 | hr-003 explicitly says do-not-merge, so keeping five separate work entities is correct, not over-fragmentation. The shared user is linked via `associated_with` only. |
| D11 | Design-chat authorship uncertainty | mc-08 | The audit body is labeled `user_authored` but reads like a co-authored report; flagged in `unresolved_items.jsonl` and `human_review_queue.md`; endorsement kept conservative (`implicit_continuation`). |
| D12 | Vague relationship risk | cross-case Accenture / roadmap-doc | Used `associated_with` / `shared_context_only` (not `part_of`/`same_project`) for the employer-context and doc links, each with evidence and a review flag, to avoid asserting unproven unity. |

## Checked, no defect

- **False project classification:** none. Only 2 `project` candidates, both with all 9 criteria; the
  transcript one-off, the two Q&A-like items, the assignments, job applications, exam-prep, lab, and
  client work were all typed at their correct (non-project) granularity.
- **Fragmentary titles:** none; all titles describe the underlying work (validator enforces the banned list).
- **Duplicate candidate:** none within a case; cross-case near-duplicates are surfaced as clusters/possible-duplicates, not merged.
- **Missing goal/task/decision/output/direction change:** captured across cases (decisions×5, tasks, artifacts×2, milestone, blocker, next_step, research_question/finding, etc.).

## Residual risks (carried to human review)

1. mc-08 design-chat authorship (D11).
2. mc-08↔mc-09 merge into one engagement (D1).
3. mc-05↔mc-11 parent-child (D2).
4. mc-10 lab involvement depth (D4).
5. mc-07 document-to-conversation link (D5).

Quality-review issue count: **12 defect classes addressed; 5 residual risks flagged.**
Semantic quality status: **conditional_pass** (clean classification + provenance discipline; the
material residual decisions are merges/links that need human confirmation, not extraction errors).
