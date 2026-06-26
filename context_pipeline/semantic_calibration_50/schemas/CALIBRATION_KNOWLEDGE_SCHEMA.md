# Stage 4E Calibration Knowledge Schema

The merged, validated ontology (carried from Stage 4D, frozen for calibration) plus the
Stage 4E additions: per-candidate `applied_decision_rule_ids` and per-review-item
`review_classification`. All semantic decisions are made by language-model judgment, never by
script. Scripts only select, load, write, resolve references, checksum, validate schema, count,
compare, and report.

## Knowledge layers and candidate types

**work_entity** — `project`, `subproject`, `initiative`, `recurring_responsibility`, `course`,
`assignment`, `exam_preparation`, `job_application`, `client_engagement`, `research_effort`,
`standalone_idea`.

**project_knowledge** — `goal`, `motivation`, `requirement`, `constraint`, `preference`,
`decision`, `proposed_decision`, `task`, `open_question`, `milestone`, `direction_change`,
`blocker`, `output`, `artifact`, `research_question`, `research_finding`, `source`, `workflow`,
`status_update`, `next_step`.

**context_entity** — `person`, `organization`, `platform`, `tool`, `employer`, `client`,
`course`, `institution`.

**non_project_interaction** — `one_off_request`, `generic_question`, `assistant_suggestion`,
`assistant_draft`, `assistant_explanation`, `tool_execution_trace`, `attachment_source`,
`transcript_fragment`, `unresolved_fragment`.

## Strict project test
A `project` requires ≥3 of: intended_outcome, continuing_actions, user_ownership_or_responsibility,
tasks_or_milestones, deliverable_or_artifact, resources_or_research, decisions_or_constraints,
repeated_appearance, identifiable_state — AND must beat every competing work-entity type
(assignment, exam_preparation, job_application, client_engagement, recurring_responsibility,
initiative, one_off_request, standalone_idea). Do not force material into `project`.

## Candidate fields (Part 7)
Every candidate records: candidate_id, case_id, candidate_type, knowledge_layer, canonical_title,
description, why_it_matters, ownership_type, user_role, organizational_context, status,
temporal_status, status_current_confidence, first_observed_at, last_observed_at, confidence,
confidence_rationale, explicit_or_inferred, transport_author_roles, content_origins,
assertion_relationships, assistant_origin, co_authored_flag, user_endorsement, evidence_segment_ids,
evidence_message_ids, attachment_ids, document_ids, missing_source_ids, project_test_criteria,
competing_classifications, **applied_decision_rule_ids**, uncertainties, contradictions,
requires_human_review, inclusion_rationale.

## Status (entity) and temporal status
entity: idea, exploring, planned, active, paused, blocked, drifted, completed, abandoned, merged,
historical, unknown. temporal: current_confirmed, current_inferred, historical_confirmed,
historical_status_unknown, superseded, unknown. **Never infer current status from date alone.**
`status_current_confidence` is reported separately from overall `confidence`. On-demand recurring
responsibilities record availability=on_demand, current execution active/inactive, last completed
phase, and reactivation possibility.

## Confidence
high / medium / low. Low is mandatory when evidence is fragmentary, conflicting, missing, or
depends on uncertain identity/authorship.

## Provenance
Distinguish user_authored, co_authored, assistant_generated, pasted_assistant, tool_or_log_output,
transcript_source_material, document, attachment. Pasted assistant content is **not** direct user
evidence. Group ownership is **not** sole ownership. Co-authorship is **not** blanket acceptance of
every assistant-generated claim.

## Relationships and clustering
Relationship types: part_of, supports, depends_on, produces, uses, informed_by, supersedes,
contradicts, evolved_into, created_for, blocked_by, possible_same_project, associated_with — every
relationship requires evidence (no co-occurrence-only links). Cluster outcomes:
strong_merge_candidate, possible_same_entity, parent_child_candidate, phase_relationship,
shared_context_only, insufficient_evidence. No auto-merge unless an authoritative rule or confirmed
human resolution already applies.

## Decision rules and review classification
When a case matches a codified rule (`config/recurring_decision_rules.json`), apply it
automatically, record the rule ID in `applied_decision_rule_ids`, cite the triggering evidence, and
do not queue the case for human review. Every human-review item is classified as
`covered_by_existing_rule`, `new_reusable_rule`, `case_specific_exception`, or `genuinely_unresolved`.
