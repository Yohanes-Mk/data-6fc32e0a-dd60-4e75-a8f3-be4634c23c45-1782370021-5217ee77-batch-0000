# Stage 3R Repair Report

- Source containers: 8207
- Content segments: 21927
- Repaired source units: 21927
- Extraction packets: 987
- Attachment occurrence count: 339
- Unique attachment filename count: 44
- Project-document packets: 36
- Design-chat packets: 30
- Missing-source references: 341

## Transport Author Counts
- `assistant`: 3911
- `attachment`: 339
- `document`: 36
- `user`: 3921

## Content Origin Counts
- `assistant_generated`: 3730
- `attachment_content`: 339
- `console_or_log_output`: 35
- `document_content`: 36
- `transcript_content`: 5620
- `user_authored`: 12167

## Fleet Command Attachment Results
- Reported attachment occurrences: 92
- Linked attachment occurrences: 92
- Extracted-text attachment occurrences: 92
- Unresolved binary occurrences: 92
- Unique attachment filenames: 1
- GDD/SDD references linked: 0
- Screenshot/image references represented: 1

## Recommendation
Use `conversation_evidence_maps.jsonl` as the next semantic-pilot input boundary. It now surfaces attachment packets, design-chat packets, missing-source records, and content-origin distinctions.
