# Extraction Staging Report

- Total source units: 16371
- Conversation paths: 496
- Extraction packets: 3551
- Checksum result: True

## Source Units By Type

- `assistant_message_text`: 3731
- `assistant_text_block`: 4008
- `attachment_extracted_text`: 860
- `conversation_title`: 244
- `design_chat_assistant_text`: 3
- `design_chat_user_text`: 3
- `project_description`: 2
- `project_document`: 73
- `project_prompt_template`: 2
- `project_title`: 17
- `tool_input`: 3886
- `user_message_text`: 3542

## Source Units By Provenance

- `assistant_output`: 7742
- `attachment_text`: 860
- `conversation_metadata`: 244
- `project_document`: 73
- `project_metadata`: 21
- `tool_input`: 3886
- `user_statement`: 3545

## Eligibility Counts

- `True`: 3639
- `conditional`: 12732

## Characters And Estimated Tokens By Provenance

- `assistant_output`: 11651939 chars, 2916107 estimated tokens
- `attachment_text`: 34174778 chars, 8543943 estimated tokens
- `conversation_metadata`: 9321 chars, 2428 estimated tokens
- `project_document`: 2171859 chars, 542986 estimated tokens
- `project_metadata`: 5687 chars, 1432 estimated tokens
- `tool_input`: 218707 chars, 56211 estimated tokens
- `user_statement`: 7583979 chars, 1897305 estimated tokens

## Packet Size Statistics

- Min estimated tokens: 2
- Max estimated tokens: 8000
- Average estimated tokens: 5394.43

## Oversized Units

- Subunits created: 663

## Direct Text / Content Block Reconciliation

- `direct_text_only`: 23
- `exact_match`: 5031
- `mismatch`: 1108
- `partial_match`: 1017

## Duplicate Groups

- Exact duplicate groups: 270
- Near-exact duplicate groups: 448

## Redaction Counts

- `api_key`: 27
- `auth_cookie`: 8
- `email`: 387
- `password`: 5
- `phone`: 1495

## Excluded Content Counts

- `empty_content`: 732
- `exact_redundant_representation`: 5031
- `model_internal_reasoning_not_project_knowledge`: 2667
- `token_budget_metadata`: 472
- `unsupported_content_type`: 3852

## Warnings

- `direct_text_content_block_mismatch`: 1108
- `direct_text_content_block_partial_match`: 1017
- `text_redacted`: 314
- `thinking_hash_collision_excluded`: 1

## Known Limitations

- Tool result bodies that were not copied into Stage 2 normalized text cannot be reconstructed in Stage 3.
- Near-duplicate detection is conservative and intentionally avoids broad semantic paraphrase detection.
- This stage does not infer topics, projects, decisions, or final database structure.

## Recommendation For The Next Stage

Use the source units and packets as the only extraction input, applying provenance-specific rules so user statements, assistant output, project documents, attachments, and tool records remain separate evidence streams.
