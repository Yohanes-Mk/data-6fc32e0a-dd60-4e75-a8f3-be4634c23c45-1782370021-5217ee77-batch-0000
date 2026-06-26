# Extraction Staging Schema

All corpus files are JSONL, one JSON object per line.

## `source_units.jsonl`

Each record represents one extraction-ready content occurrence or deterministic subunit.

Required fields include:

- `source_unit_id`
- `normalized_entity_id`
- `conversation_id`
- `message_id`
- `project_id`
- `document_id`
- `source_platform`
- `source_export_family`
- `source_unit_type`
- `semantic_provenance`
- `author_role`
- `text`
- `character_count`
- `estimated_token_count`
- `content_hash_sha256`
- `original_timestamp`
- `normalized_timestamp`
- `source_file`
- `source_record_pointer`
- `branch_membership_refs`
- `extraction_eligibility`
- `extraction_policy`
- `warnings`

Subunits include `parent_source_unit_id` and `source_text_offsets`.

## `conversation_paths.jsonl`

Path records preserve branch structure without text duplication:

- `conversation_path_id`
- `conversation_id`
- `root_message_id`
- `leaf_message_id`
- `ordered_message_ids`
- `ordered_source_unit_ids`
- `shared_prefix_length`
- `shared_prefix_reference`
- `path_length`
- `start_timestamp`
- `end_timestamp`
- `branch_warnings`

## `conversation_profiles.jsonl`

Profiles contain deterministic metadata only: message counts, role counts, tool and attachment counts, branch counts, source-unit counts, eligible character counts by provenance, and complexity classification.

## `extraction_packets.jsonl`

Packets are ordered references to source units:

- `packet_id`
- `conversation_id` or `project_id`
- `conversation_path_id` when applicable
- `ordered_source_unit_ids`
- `primary_eligible_source_unit_ids`
- `supporting_context_source_unit_ids`
- `provenance_counts`
- `character_count`
- `estimated_token_count`
- `start_timestamp`
- `end_timestamp`
- `overlap_reference`
- `previous_packet_id`
- `next_packet_id`
- `packet_warnings`
- `extraction_priority`

## `duplicate_groups.jsonl`

Duplicate groups retain all members:

- `duplicate_group_id`
- `duplicate_type`
- `member_source_unit_ids`
- `canonical_source_unit_id`
- `similarity_score`
- `provenance_distribution`
- `crosses_conversations`
- `crosses_provenance_types`
- `recommended_later_handling`

## `excluded_units.jsonl`

Excluded records preserve why content did not enter the corpus:

- `excluded_unit_id`
- `normalized_source_reference`
- `unit_type`
- `exclusion_reason`
- `character_count`
- `content_hash_sha256`
- `source_file`
- `exclusion_scope`
- `policy_dependent`
