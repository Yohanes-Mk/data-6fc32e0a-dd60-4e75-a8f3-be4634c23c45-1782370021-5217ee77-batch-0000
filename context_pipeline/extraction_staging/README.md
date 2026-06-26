# Stage 3 Extraction Staging

This derived workspace prepares the Stage 2 normalized Claude records for a later semantic extraction stage. It preserves eligible content as provenance-rich source units, creates reference-based conversation paths, builds extraction packets, records duplicate groups, and logs exclusions.

## Inputs

Read-only inputs:

- `conversations.json`
- `users.json`
- `projects/`
- `design_chats/`
- `context_pipeline/normalized/`
- `context_pipeline/manifests/`
- existing Stage 2 reports and scripts

The builder computes SHA-256 checksums for every file under `context_pipeline/normalized/` before and after Stage 3. The validator checks that those files remain unchanged.

## How To Run

```bash
python3 context_pipeline/extraction_staging/scripts/build_extraction_staging.py
python3 context_pipeline/extraction_staging/scripts/validate_extraction_staging.py
```

The scripts use only the Python 3 standard library.

## Outputs

- `corpus/source_units.jsonl`: extraction-ready content units
- `corpus/conversation_paths.jsonl`: branch/path references without repeated message text
- `corpus/extraction_packets.jsonl`: packetized source-unit references for later LLM processing
- `corpus/conversation_profiles.jsonl`: deterministic conversation metadata and complexity flags
- `corpus/duplicate_groups.jsonl`: exact and near-exact duplicate groups
- `corpus/excluded_units.jsonl`: excluded content and reasons
- `reports/*.md|json|jsonl`: human and machine-readable reports
- `manifests/*.json`: before/after Stage 2 normalized checksums

## Eligibility And Provenance

User-authored content is eligible. Assistant output, tool input, tool output, and attachment text are conditional. Project documents and project metadata are eligible as document evidence. Conversation metadata is conditional. Thinking blocks, token-budget blocks, empty text, private contact data, and structural-only records are excluded.

Assistant output is preserved as generated content. It must not later be promoted automatically into user facts, user decisions, completed actions, verified research, or confirmed preferences.

Tool output is preserved only when text is available and is always marked `tool_output_unverified`. Stage 2 stores most tool output structurally, so unavailable tool bodies become exclusion records rather than invented text.

Attachments and project documents remain distinct from conversation text.

## Direct Text Reconciliation

For each message, direct message text is compared with the combined eligible text blocks using Unicode NFC normalization, normalized line endings, and trimming. Exact matches produce one primary source unit from direct text plus references to the matching text blocks. Differing values are preserved as separate units with warnings. Empty representations are excluded.

## Branch Handling

Conversation paths are built from Stage 2 branch records. Path records store ordered message IDs and ordered source-unit references. Message text is not duplicated inside path records.

## Packet Construction

Packets are ordered source-unit references. Target size is 6,000 estimated tokens, maximum size is 8,000 estimated tokens, with about 500 estimated tokens of overlap where practical. Estimated tokens are computed deterministically as `ceil(character_count / 4)`.

Oversized source units are split into deterministic subunits using paragraph-aware boundaries when possible. Subunits retain the original source-unit reference and character offset ranges.

## Duplicate Detection

Exact duplicates use conservative normalized text hashing: Unicode NFC, normalized line endings, trimming, and repeated-whitespace collapse. Near-exact duplicate candidates are bucketed by line fingerprints, then compared with `difflib.SequenceMatcher` only within those buckets.

Duplicate detection never deletes or merges source units.

## Redaction

The builder detects obvious emails, phone numbers, bearer tokens, API-key-like values, private keys, labeled passwords, and authentication cookies. Staged text replaces detected values with typed redaction markers. Counts and source-unit references are reported; detected values are not printed.

## Limitations

- Stage 3 does not identify projects, classify topics, summarize conversations, cluster content, design a final database, or call an LLM/API.
- Tool input/output bodies that Stage 2 did not preserve as text cannot be reconstructed here.
- Near-duplicate detection is intentionally conservative and may miss loose paraphrases.
- A future ChatGPT-normalized adapter can emit the same source-unit, path, packet, duplicate, and exclusion records with `source_platform = "chatgpt"` and a distinct export family.
