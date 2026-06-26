# Repair Report

- Original Stage 4A candidates audited: 62
- Repaired selected conversations: 8
- Repaired candidates: 21
- Repaired relationships: 12
- Excluded content records: 22
- Semantic quality issues: 27

## Repaired Candidates By Type
- `assistant_suggestion`: 7
- `constraint`: 2
- `one_off_request`: 2
- `project`: 6
- `task`: 4

## Confidence Distribution
- `high`: 7
- `medium`: 14

## Endorsement Distribution
- `no_endorsement`: 7
- `not_applicable`: 14

## Relationship Counts
- `depends_on`: 4
- `informed_by`: 6
- `supports`: 2

## Selection Note

A project-document-linked proxy conversation is labeled explicitly because Stage 4A project-document packets do not carry conversation IDs. The repair records this as a limitation rather than inferring a join.

## Recommendation

The repaired pilot is suitable for independent Claude Code cross-review as a semantic repair artifact, but not yet for full-corpus extraction until reviewer feedback confirms ontology granularity, project-test behavior, and project-document linkage handling.
