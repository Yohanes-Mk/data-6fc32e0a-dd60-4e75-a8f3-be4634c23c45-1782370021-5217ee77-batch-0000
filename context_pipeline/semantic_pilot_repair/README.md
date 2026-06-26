# Stage 4A-R Semantic Pilot Repair

This repair preserves Stage 4A unchanged as a baseline and creates a stricter semantic pilot repair under `context_pipeline/semantic_pilot_repair/`. It audits all 62 original candidates, selects 8 Stage 4A-sampled conversations, builds conversation-level evidence bundles, and emits repaired candidates with stricter project, assistant, tool, attachment, endorsement, confidence, and relationship policies. No Claude cross-review or full-corpus extraction is performed.
