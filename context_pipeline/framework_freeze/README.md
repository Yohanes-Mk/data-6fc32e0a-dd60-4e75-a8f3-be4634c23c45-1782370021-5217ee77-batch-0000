# Stage 5A Framework Freeze

This directory freezes the validated Stage 4E semantic framework and records the production extraction plan for the remaining Claude corpus. It does **not** begin Stage 5B extraction.

## What is frozen

- ontology and candidate typing
- strict project test
- status, temporal-status, ownership, user-role, confidence, and endorsement models
- provenance, attachment, and missing-source discipline
- relationship and clustering semantics
- review categories and escalation thresholds
- profile-promotion rules
- 23 authoritative recurring decision rules (22 from Stage 4E + `hr-008a`)
- final direct human resolutions from Stage 5A

## What this package adds

- frozen config copies for policy, rules, confirmed resolutions, and review thresholds
- future-facing schemas for frozen candidates, relationships, project records, and profile records
- production, consolidation, database, ChatGPT adapter, and runtime retrieval plans
- validation and checksum manifests proving prior-stage files remained unchanged

## Execution boundary

- Do not run another pilot.
- Do not process additional conversations inside Stage 5A.
- Do not start full-corpus extraction yet.
- The exact next step is **Stage 5B staged extraction under the frozen framework**.
