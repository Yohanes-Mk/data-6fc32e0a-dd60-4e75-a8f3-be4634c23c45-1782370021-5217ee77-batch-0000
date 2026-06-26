# Batch Strategy

## Initial sequencing

- **Batch 01**: 75 conversations, biased toward low/medium complexity to confirm stable throughput under the frozen framework
- **Batch 02**: 60 conversations + 15 project documents
- **Batch 03**: 70 conversations + 5 project documents
- **Batch 04**: 18 conversations + 14 project documents

This preserves complexity diversity while preventing the document tail from accumulating into a final surprise batch.

## Why this order

- early batches validate operational steadiness before the hardest long-tail cases
- midstream document interleaving tests source-vs-artifact and ownership rules under realistic load
- the final batch is intentionally smaller so any late review pressure is containable

## Review thresholds per batch

- target `genuinely_unresolved` <= 10%
- target `new_reusable_rule` = 0 unless a 3-case pattern emerges
- treat isolated anomalies as `case_specific_exception`
- keep `covered_by_existing_rule` as the dominant category for repeated patterns
