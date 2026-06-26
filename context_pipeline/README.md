# Claude Export Normalization Pipeline

This Stage 2 pipeline converts the mixed Claude export files in the workspace into reversible JSONL staging records. It does not perform project discovery, summarization, clustering, embeddings, semantic classification, knowledge extraction, or final folder-framework design.

## Raw And Immutable Inputs

The following paths are treated as raw source data and must not be edited by this pipeline:

- `conversations.json`
- `users.json`
- `projects/`
- `design_chats/`

The normalizer computes SHA-256 checksums before processing and again after writing derived outputs. The validator confirms the checksums are unchanged.

## How To Run

From the workspace root:

```bash
python3 context_pipeline/scripts/normalize.py
python3 context_pipeline/scripts/validate.py
```

The scripts use only the Python 3 standard library.

## Output Structure

Derived output is written under `context_pipeline/`:

- `normalized/*.jsonl`: normalized staging entities
- `reports/normalization_report.md`: human-readable normalization summary
- `reports/validation_report.json`: machine-readable validation results
- `reports/warnings.jsonl`: structured warnings
- `manifests/raw_checksums_before.json`: raw source checksums before normalization
- `manifests/raw_checksums_after.json`: raw source checksums after normalization

## Provenance Rules

Every normalized record carries source provenance, including the source file, source record ID, source index where applicable, parent source ID where applicable, and a raw JSON pointer. Deterministic normalized IDs use the pattern:

```text
claude:<export_family>:<entity_type>:<source_identifier>
```

Entities without native UUIDs use deterministic suffixes such as message UUID plus block, attachment, or file-reference index.

## Text Provenance

The pipeline marks text-bearing entities with explicit `semantic_provenance` values:

- `user_statement`
- `assistant_output`
- `tool_input`
- `tool_output_unverified`
- `attachment_text`
- `project_document`
- `export_metadata`
- `model_internal_reasoning_excluded`

Normalization preserves provenance. It does not decide whether any content is true.

## Thinking-Block Exclusion

Claude thinking blocks remain preserved in the immutable raw export, but their thinking text is not copied into normalized searchable content. Normalized thinking block records store only structural metadata, character count, a SHA-256 hash of the original thinking text, truncation metadata, timestamps, provenance, and:

```json
{
  "extraction_eligibility": false,
  "exclusion_reason": "model_internal_reasoning_not_project_knowledge"
}
```

## Processing Method

`conversations.json` is about 103 MB. This implementation uses Python's standard-library `json.load` for the root JSON arrays and objects. That is acceptable for this local dataset and keeps the adapter readable, but it is not a fully streaming parser. If a future export is substantially larger, the conversation adapter should be replaced with a streaming root-array reader while preserving the same normalized schemas.

All JSONL outputs are written to temporary files and then atomically renamed into place. A failure should leave either the previous complete file or no final file, rather than a silently partial final output.

## Limitations

- `design_chats/*.json` contain embedded project UUIDs that do not match UUIDs in `projects/*.json`; the relationship is preserved as unresolved.
- File references are normalized as references only. No missing binary payloads are invented.
- Tool inputs and tool results are preserved as structural, unverified provenance and must not be interpreted later as user beliefs or verified facts without further review.
- This stage intentionally does not classify conversations into projects or topics.

## Future ChatGPT Adapter Boundary

A future ChatGPT export can be added as another adapter that emits the same normalized entity types with `source_platform = "chatgpt"` and a distinct `source_export_family`. The adapter should map ChatGPT conversations, messages, content parts, attachments, and tool records into the existing JSONL schemas without changing already-normalized Claude record shapes.
