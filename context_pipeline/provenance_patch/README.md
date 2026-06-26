# Stage 3R-P Provenance Patch

This directory contains a narrow metadata overlay for the next semantic pilot. It does not modify Stage 2, Stage 3, Stage 3R, Stage 4A, Stage 4A-R, Stage 4B, Stage 4C, or raw export files.

The patch addresses two things:

- Attachment filename propagation: every Stage 3R attachment occurrence is re-emitted with explicit original and normalized filename fields, source pointers, content hashes, and stage-to-stage trace metadata.
- Confirmed human resolutions: Client Radar is recorded as one user-owned Accenture client engagement with accessibility and repository facets, and AVATAR/BCI is recorded as completed historical work.

The compatibility file `corpus/patched_semantic_evidence_inputs.jsonl` is intended as a small input overlay for the next semantic pilot. It preserves Stage 3R evidence IDs and adds corrected metadata rather than re-extracting semantic entities.

Validation is performed by `scripts/validate_patch.py`.
