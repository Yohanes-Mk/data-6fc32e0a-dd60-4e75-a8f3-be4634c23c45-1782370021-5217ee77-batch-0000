# Remaining Risks

- The Stage 4E readiness assessment still flags mixed-origin segmentation in some `user_authored` spans; this is manageable under frozen provenance rules but can increase review load.
- Attachment filenames remain frequently null, so cross-case attachment identity will continue to rely on content hashes and occurrence-level provenance.
- The 6 normalized conversations outside the Stage 4E evidence-map universe must stay out of the first production run unless the evidence boundary is explicitly extended.
- Full context-database generation still depends on later consolidation quality, not just extraction quality.
