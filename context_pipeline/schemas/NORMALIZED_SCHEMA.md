# Normalized Schema

All records are JSON objects written as JSONL. Every record includes common provenance fields where applicable:

- `normalized_id`
- `source_platform`
- `source_export_family`
- `source_file`
- `source_record_id`
- `source_parent_id`
- `source_index`
- `original_created_at`
- `original_updated_at`
- `normalized_created_at_utc`
- `normalized_updated_at_utc`
- `record_type`
- `provenance`
- `extraction_eligibility`
- `warnings`

## Common Provenance Object

`provenance` contains:

- `source_file`
- `source_record_id`
- `source_parent_id`
- `source_index`
- `raw_pointer`
- `source_export_family`

## Entity Files

`conversations.jsonl` stores one main Claude conversation per line. It contains title metadata, counts, branch statistics, account references, timestamps, and flags, but not full message bodies.

`messages.jsonl` stores messages from both the main Claude conversation export and the design-chat export. It preserves direct text where present, role or sender, parent references, order, branching flags, and content/attachment/file counts.

`content_blocks.jsonl` stores block-level content metadata and eligible text. Thinking blocks exclude thinking text and retain only count/hash/structural metadata.

`conversation_branches.jsonl` stores root-to-leaf branch paths for each conversation without duplicating message text.

`attachments.jsonl` stores attachment metadata and extracted attachment text with attachment-specific provenance.

`file_references.jsonl` stores message file references and whether a matching local payload exists.

`projects.jsonl` stores Claude project metadata and creator references. It does not assume project-to-conversation links.

`project_documents.jsonl` stores embedded project documents and their content with project-document provenance.

`design_chats.jsonl` stores top-level design-chat records and their embedded project references.

`users_redacted.jsonl` stores redacted user metadata only. Email addresses and phone numbers are represented as booleans.

`source_files.jsonl` stores raw file metadata and before/after SHA-256 checksums.

## Extraction Eligibility

`extraction_eligibility` values are:

- `true`: eligible for later extraction with provenance-aware handling
- `false`: excluded from later extraction
- `conditional`: may be used later only with special handling

## Thinking Blocks

Thinking blocks must not include `text`, `content_text`, `thinking`, or any equivalent searchable copy of the original thinking text. They include:

- `block_type`
- `content_char_count`
- `content_sha256`
- `truncated`
- timestamps
- `extraction_eligibility: false`
- `exclusion_reason: "model_internal_reasoning_not_project_knowledge"`
- `semantic_provenance: "model_internal_reasoning_excluded"`
