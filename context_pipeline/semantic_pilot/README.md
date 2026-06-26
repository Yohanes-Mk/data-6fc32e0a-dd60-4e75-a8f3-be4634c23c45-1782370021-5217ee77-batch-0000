# Stage 4A Semantic Extraction Pilot

This derived workspace contains a controlled, provenance-aware semantic extraction pilot over exactly 24 Stage 3 extraction packets. It does not process the full corpus, call external APIs, or construct the final knowledge graph.

Inputs are read-only: raw exports, `context_pipeline/normalized/`, and `context_pipeline/extraction_staging/corpus/`. Stage 3 corpus checksums are recorded before and after the pilot.

Outputs include selected packets, candidate extractions, candidate entities, relationships, unresolved items, extraction failures, validation/report files, and review samples. Candidate wording is intentionally conservative and keeps assistant-origin material separate from user-authored evidence.
