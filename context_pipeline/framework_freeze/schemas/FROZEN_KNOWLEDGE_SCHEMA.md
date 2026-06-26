# Frozen Knowledge Schema

Stage 5A freezes the Stage 4E ontology, review policy, provenance rules, and recurring decision rules for production extraction. No semantic redesign is introduced here; only authoritative carry-forward plus the newly authoritative `hr-008a`.

## Frozen ontology

**work_entity**: `project`, `subproject`, `initiative`, `recurring_responsibility`, `course`, `assignment`, `exam_preparation`, `job_application`, `client_engagement`, `research_effort`, `standalone_idea`

**project_knowledge**: `goal`, `motivation`, `requirement`, `constraint`, `preference`, `decision`, `proposed_decision`, `task`, `open_question`, `milestone`, `direction_change`, `blocker`, `output`, `artifact`, `research_question`, `research_finding`, `source`, `workflow`, `status_update`, `next_step`

**context_entity**: `person`, `organization`, `platform`, `tool`, `employer`, `client`, `course`, `institution`

**non_project_interaction**: `one_off_request`, `generic_question`, `assistant_suggestion`, `assistant_draft`, `assistant_explanation`, `tool_execution_trace`, `attachment_source`, `transcript_fragment`, `unresolved_fragment`

## Frozen tests and policies

- Strict project test remains `>=3` criteria plus "must beat alternatives".
- Status is split into entity status, temporal status, and separate `status_current_confidence`.
- Ownership and provenance remain independent. Group participation is not sole authorship.
- Attachments keep null filenames, repeated occurrences do not multiply evidence, and missing binaries cannot be reconstructed.
- Relationship types and clustering outcomes are frozen from Stage 4E.
- Profile-level promotion still requires recurrence across contexts or a clearly general statement.

## Review categories

Every future review item must land in exactly one frozen category:

- `covered_by_existing_rule`
- `new_reusable_rule`
- `case_specific_exception`
- `genuinely_unresolved`

## Auto-resolution behavior

When a frozen rule matches, the extractor must:

1. apply the rule automatically
2. record the rule ID
3. cite the triggering evidence
4. skip user review unless evidence conflicts with the frozen rule

## New authoritative addition

`hr-008a` is now frozen and authoritative: shared labels or folders do not imply umbrella membership or project identity. Ownership, client, organization, deliverable, workstream, and explicit evidence outrank labels.
