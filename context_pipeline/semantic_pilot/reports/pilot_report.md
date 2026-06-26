# Stage 4A Pilot Report

- Selected packets: 24
- Packet completion rate: 24/24
- Candidate count: 62
- Relationship count: 14
- Source-unit coverage: 56/591 referenced as direct evidence
- Schema-validation rate: calculated in `validation_report.json`
- Assistant-origin candidates: 31
- Project/subproject candidates: 10
- Low-confidence candidates: 0
- Requires-review candidates: 37

## Candidates By Type

- `constraint`: 4
- `file_or_artifact`: 5
- `open_question`: 2
- `output`: 3
- `project`: 10
- `proposed_decision`: 8
- `standalone_idea`: 9
- `tool_or_platform`: 13
- `workflow`: 8

## Endorsement Distribution

- `explicit_acceptance`: 25
- `no_endorsement`: 31
- `unclear`: 6

## Relationship Counts

- `related_to`: 14

## Observed Strengths

- The schema preserved packet, source-unit, message, and provenance references for all substantive candidates.
- Assistant-origin candidates are separated from user-authored evidence.
- The pilot exposed a Stage 3 gap: design-chat source units are present but not packetized.

## Observed Weaknesses

- Candidate wording is conservative and may under-extract nuanced project relationships.
- Some project candidates require review because the pilot avoids merging across packets.
- Attachment-heavy packets can dominate size while providing limited direct user intent.

## Readiness

- Ready for independent Claude Code cross-review: yes, as a pilot artifact.
- Ready for full-corpus extraction: not yet; first review schema behavior, design-chat packetization, and candidate granularity.
