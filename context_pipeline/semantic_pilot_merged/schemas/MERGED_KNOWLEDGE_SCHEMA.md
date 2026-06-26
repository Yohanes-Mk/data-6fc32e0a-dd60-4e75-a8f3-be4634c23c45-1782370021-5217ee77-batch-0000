# Merged Knowledge Schema (Stage 4C)

This schema merges Codex's conservative project-admission discipline (Stage 4A-R) with
Claude's broader work-entity and project-knowledge ontology (Stage 4B), grounded on Stage 3R's
corrected provenance, attachment, document, design-chat, and missing-source records.

## Knowledge layers

- **work_entity** — project / subproject / initiative / recurring_responsibility / course /
  assignment / exam_preparation / job_application / client_engagement / research_effort /
  standalone_idea.
- **project_knowledge** — goal, motivation, requirement, constraint, preference, decision,
  proposed_decision, task, open_question, milestone, direction_change, blocker, output, artifact,
  research_question, research_finding, source, workflow, status_update, next_step.
- **context_entity** — person, organization, platform, tool, employer, client, course_context,
  institution.
- **non_project_interaction** — one_off_request, generic_question, assistant_suggestion,
  assistant_draft, assistant_explanation, tool_execution_trace, attachment_source,
  transcript_fragment, unresolved_fragment. Searchable but never auto-enter the project landscape.

## Strict project test

A `project` requires ≥3 of: intended_outcome, continuing_actions,
user_ownership_or_responsibility, tasks_or_milestones, deliverable_or_artifact,
resources_or_research, decisions_or_constraints, repeated_appearance, identifiable_state —
**and** must be better represented as a project than as assignment / exam_preparation /
job_application / recurring_responsibility / client_engagement / one_off_request /
standalone_idea. Record `project_test_criteria` and `competing_classifications` for every work entity.

## Provenance fields (from Stage 3R)

`transport_author_roles`, `content_origins`, `assertion_relationships` are carried from the
Stage 3R segments/units backing each candidate, so mixed-origin messages are represented
faithfully (a user message containing pasted assistant output is not treated as user authorship).

## Status vs temporal vs confidence

Three independent axes:
- `status` (entity lifecycle: idea…active…completed…unknown),
- `temporal_status` (evidence recency / currency: current_confirmed … historical_status_unknown … superseded),
- `confidence` (high/medium/low that the classification + status are right, with rationale).

Confirmed human resolutions (Stage 3R decisions) seed status: roadmap=active;
Fleet Command & Tsotsi = status unresolved (historical_status_unknown, do not infer completion);
Accenture affiliation = confirmed; professor GDD/SDD = source (not artifact);
ExamPro skip = assistant proposal (proposed_decision, not accepted).

## Attachments

`attachment_ids` record occurrences; evidence weight uses **unique** content (by hash/filename).
Unavailable binaries are never described as inspected; an attachment is `artifact` only if its
role supports it (otherwise `source` / `attachment_source`).

## Missing sources

Every missing source yields an impact record (`results/missing_source_impacts.jsonl`) with
`do_not_infer:true`; findings behind missing sources are never reconstructed.

## Canonical titles

Must describe the underlying work. Banned: "Quick question", "Perfect", "Yes, that is clear",
"Mark the statement true or false", "Let me verify", "The user wants", and any copied message opening.

## Relationships

Typed (`merged_relationship.schema.json`), each with evidence, confidence, explicit/inferred,
temporal qualification, and review flag. No co-occurrence-only links. Cross-case clustering uses
`possible_same_project` / `possible_parent_child` / `possible_evolution` / `shared_context_only`.
