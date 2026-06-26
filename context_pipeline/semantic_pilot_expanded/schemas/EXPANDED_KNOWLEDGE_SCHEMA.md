# Expanded Knowledge Schema (Stage 4D)

Extends the Stage 4C merged schema for the final expanded pilot. Same four knowledge layers,
same strict project test, same provenance discipline, grounded on **Stage 3R + the mandatory
Stage 3R-P overlay** (3R-P wins on patched metadata).

## What is new vs Stage 4C

- `status_current_confidence` — a separate axis from `confidence`: how sure we are that the
  *current* status is right (distinct from how sure we are of the classification).
- `co_authored_flag` — true when the candidate's content is genuinely co-authored by user and
  assistant (e.g. the Client Radar audit per Stage 3R-P), as opposed to purely user- or
  assistant-authored.

## Three independent certainty axes

- `status` (lifecycle): idea…active…completed…historical…unknown.
- `temporal_status` (currency): current_confirmed / current_inferred / historical_confirmed /
  historical_status_unknown / superseded / unknown. **Never inferred from conversation date alone.**
- `confidence` + `status_current_confidence` (calibration of the classification, and separately of
  the current status). Low confidence is used for fragmentary evidence, uncertain origin, ambiguous
  boundaries, attachment/missing-source-central conclusions, assistant-dependent conclusions, or
  conflicting evidence. A pilot with no low-confidence records must justify that in the report.

## Provenance (from Stage 3R / 3R-P)

`transport_author_roles`, `content_origins`, `assertion_relationships`, `assistant_origin`, and
`co_authored_flag` are carried so mixed-origin and co-authored content is represented faithfully.
Pasted assistant text, tool/log output, and transcript material are never treated as direct user
evidence.

## Attachments / filenames (Stage 3R-P policy)

Filenames are used only when populated by 3R-P; otherwise **null is preserved** (never invented).
Occurrence count is reported separately from unique content-hash count; repeated occurrences do not
inflate evidence; unavailable binaries are never described as inspected; extracted text is valid
evidence; a null filename does not make an attachment unusable.

## Missing sources

Material missing sources produce impact records with `do_not_infer: true`; findings/contents/
screenshots/project-document links behind them are never reconstructed.

## Strict project test

`project` requires ≥3 criteria AND a determination that no other work-entity type
(assignment / exam_preparation / job_application / recurring_responsibility / client_engagement /
research_effort / standalone_idea / initiative / subproject / course) is more accurate. Effort
alone (one-off questions, tutoring, isolated writing, a single assignment, one job application, one
calendar request, short research questions, uploaded source docs, unendorsed assistant plans) does
not make a project. Each work entity records criteria satisfied, competing classifications, the
selected classification, and the rationale.

## Relationships & clustering

Typed relationships with evidence, confidence, explicit/inferred, temporal qualification, review
flag, and rationale; no co-occurrence-only links. Cross-case clustering uses
strong_merge_candidate / possible_same_entity / parent_child_candidate / phase_relationship /
shared_context_only / insufficient_evidence, with no automatic merges.

## Profile-level knowledge

Promoted only on recurrence across cases (e.g. the one profile-level voice/tone preference);
one-time statements are not globalized.
