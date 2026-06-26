# Normalization Report

## Source Formats Processed

- `conversations.json`: main Claude conversation export
- `users.json`: user/account export
- `projects/*.json`: Claude project metadata and embedded documents
- `design_chats/*.json`: separate design-chat export family

## Output Entities Created

- `context_pipeline/normalized/conversations.jsonl`
- `context_pipeline/normalized/messages.jsonl`
- `context_pipeline/normalized/content_blocks.jsonl`
- `context_pipeline/normalized/conversation_branches.jsonl`
- `context_pipeline/normalized/attachments.jsonl`
- `context_pipeline/normalized/file_references.jsonl`
- `context_pipeline/normalized/projects.jsonl`
- `context_pipeline/normalized/project_documents.jsonl`
- `context_pipeline/normalized/design_chats.jsonl`
- `context_pipeline/normalized/users_redacted.jsonl`
- `context_pipeline/normalized/source_files.jsonl`

## Final Counts

- Main conversations: 292
- Main messages: 7826
- Design chats: 2
- Design-chat messages: 6
- Projects: 17
- Project documents: 36
- Users redacted: 1
- Content blocks: 20241
- Conversation branch path records: 490
- Empty-conversation branch records: 6
- Attachments: 339
- File references: 1763
- Source files: 21

## Text-Volume Counts By Provenance

- `assistant_output`: 14695326 chars
- `attachment_text`: 18571897 chars
- `export_metadata`: 5687 chars
- `project_document`: 1240382 chars
- `tool_output_unverified`: 18753432 chars
- `user_statement`: 9176915 chars

## Excluded Content Counts By Reason

- `model_internal_reasoning_not_project_knowledge`: 2662
- `token_budget_metadata`: 472

## Warning Summary

- `conversation_empty`: 6
- `conversation_title_missing`: 48
- `design_project_unmatched`: 2
- `unresolved_file_reference`: 1763

## Memory And Processing Method

The normalizer uses Python standard-library `json.load` for the approximately 103 MB main export. Outputs are written to temporary files and atomically renamed into place.

## Unresolved Relationships

- Design-chat embedded project UUIDs are preserved but not matched to exported project UUIDs.
- File references are preserved as references; missing binary payloads are not invented.

## Known Limitations

- No project discovery, semantic extraction, clustering, embeddings, or summarization is performed.
- Tool inputs and tool results are marked with unverified provenance and require later provenance-aware handling.
- Thinking text is intentionally excluded from normalized searchable content.

## Raw Checksum Verification Result

- Raw checksums unchanged after normalization: True
