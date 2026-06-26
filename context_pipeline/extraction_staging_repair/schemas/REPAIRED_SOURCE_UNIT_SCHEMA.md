# Repaired Source Unit Schema

Stage 3R separates message transport authorship from the origin of content inside that message.

Every repaired source unit and content segment carries:

- `transport_author_role`
- `content_origin`
- `assertion_relationship`
- `origin_confidence`
- `origin_detection_method`
- `requires_origin_review`

Only segments with `content_origin = user_authored` and an eligible user assertion relationship may act as primary user evidence in later semantic stages.

Attachments, project documents, design chats, pasted assistant text, logs, transcripts, and missing sources are preserved as evidence or references without being silently promoted to user facts, user decisions, or projects.

## Source Containers

`source_containers.jsonl` stores intact retained text for original messages, attachments, project documents, and design-chat records. Containers preserve source-unit references, normalized IDs, message/conversation/project/document IDs, source file, timestamps, character count, and hash.

## Content Segments

`content_segments.jsonl` stores offset-based content-origin slices for each container. Segments cover the retained text without overlaps. Containers are split only when conservative evidence identifies multiple origins.

## Repaired Source Units

`repaired_source_units.jsonl` points to content segments and carries extraction eligibility. Eligible direct-user-evidence units are explicitly separated from supporting source material.
