# Stage 3R Extraction Staging And Provenance Repair

This derived workspace repairs upstream provenance defects found after semantic pilot review. It does not perform semantic project extraction and does not modify raw exports, Stage 2 outputs, Stage 3 outputs, Stage 4A outputs, or repair review outputs.

The repair creates intact source containers, offset-based content segments, repaired source units, attachment links, project-document links, design-chat packets, repaired extraction packets, conversation evidence maps, missing-source references, and validation reports.

Run from the workspace root:

```bash
python3 context_pipeline/extraction_staging_repair/scripts/build_repaired_staging.py
python3 context_pipeline/extraction_staging_repair/scripts/validate_repaired_staging.py
```

The scripts use only the Python standard library.
