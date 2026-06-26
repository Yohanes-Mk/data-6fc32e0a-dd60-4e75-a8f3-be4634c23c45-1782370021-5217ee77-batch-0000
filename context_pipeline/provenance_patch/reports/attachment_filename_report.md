# Attachment Filename Report

{
  "all_attachments": {
    "filename_populated_occurrences": 61,
    "missing_filename_occurrences": 278,
    "total_attachment_occurrences": 339,
    "unique_filenames": 43
  },
  "fleet_command": {
    "conversation_id": "claude:conversations:conversation:e2fc5641-6bd8-41c3-80d2-1e1e71b1e491",
    "filename_information_preserved_in_patched_semantic_evidence_input": true,
    "filename_populated_occurrences": 0,
    "missing_filenames": 92,
    "repeated_filenames": [],
    "source_limitation": "Fleet attachment filename fields are blank in Stage 2 normalized attachments and Stage 3R attachment links; null is preserved rather than invented.",
    "total_attachment_occurrences": 92,
    "unique_content_hashes": 88,
    "unique_filenames": 0,
    "unresolved_binaries": 92
  },
  "loss_classification_counts": {
    "absent_upstream_raw_or_normalized": 278,
    "lost_between_stage3r_attachment_link_and_stage3r_extraction_packet": 61
  },
  "stage4c_loss_location": "Per-attachment filename metadata was not present in Stage 3R extraction packets and was not carried into merged semantic evidence bundles, which expose only aggregate attachment filename counts/samples."
}
