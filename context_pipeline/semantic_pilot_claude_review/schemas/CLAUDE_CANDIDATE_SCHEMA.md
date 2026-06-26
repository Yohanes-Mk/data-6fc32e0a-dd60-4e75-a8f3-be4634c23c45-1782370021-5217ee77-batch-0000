# Claude Cross-Review Candidate Schema

This schema governs the blind independent extraction produced in Phase 1 of the
Stage 4B Claude semantic cross-review. It is intentionally close in spirit to the
Stage 4A-R repaired schema so that candidates can be aligned, but it is authored
independently and does not copy the repaired field set verbatim.

## Knowledge layers

Every candidate is assigned exactly one `knowledge_layer`:

- `work_entity` — projects, subprojects, courses, assignments, job applications, etc.
- `project_knowledge` — goals, decisions, tasks, outputs, constraints, research, etc.
- `context_entity` — people, organizations, platforms, employers, institutions.
- `non_knowledge` — one-off requests, generic questions, assistant suggestions/drafts,
  tool traces, attachments, transcript fragments. These never enter the project graph
  automatically.

## Field reference

| Field | Meaning |
|---|---|
| `claude_candidate_id` | Stable id, form `claude:cand:<slug>`. |
| `conversation_id` | Source conversation. |
| `candidate_type` | One of the enumerated types (A–D groups in the brief). |
| `canonical_title` | Describes the underlying activity, not a copied message opening. |
| `description` | What the candidate is, grounded in evidence. |
| `why_it_matters` | Why this is worth storing for reconstruction. |
| `knowledge_layer` | See above. |
| `temporal_status` | current / historical / future_intended / point_in_time / unknown. |
| `status` | active / completed / abandoned / proposed / in_progress / one_time / unknown. |
| `confidence` | high / medium / low — calibrated, not defaulted to medium. |
| `confidence_rationale` | Why that confidence level. |
| `explicit_or_inferred` | Whether grounded in explicit user text or inferred. |
| `semantic_provenance` | user_statement / assistant_output / tool_trace / attachment / mixed. |
| `assistant_origin` | true if the candidate originates from assistant content. |
| `user_endorsement` | Endorsement policy value; explicit_* requires user-authored evidence. |
| `evidence_source_unit_ids` | Stage 3 source-unit ids supporting the candidate. |
| `evidence_message_ids` | Message ids supporting the candidate. |
| `project_test_criteria` | For work entities claiming project status: which strict criteria are met. |
| `related_candidate_ids` | Linked Claude candidate ids. |
| `uncertainties` | Open questions about the candidate. |
| `contradictions` | Conflicting evidence. |
| `requires_human_review` | true when a human decision materially affects the DB. |
| `inclusion_rationale` | Why this candidate was emitted (or why kept as non-knowledge). |

## Strict project test

A `work_entity` is labelled `project` only when at least three criteria are
satisfied and listed in `project_test_criteria`:
intended_outcome, more_than_one_continuing_action, explicit_user_ownership,
tasks_or_milestones, deliverable_or_artifact, resources_or_research,
decisions_or_constraints, repeated_appearance_over_time, identifiable_state.

Lesser work entities (`assignment`, `exam_preparation`, `job_application`,
`recurring_responsibility`, `standalone_idea`) are used when the activity is real
but does not meet the full project bar, or is better described by a more specific type.
