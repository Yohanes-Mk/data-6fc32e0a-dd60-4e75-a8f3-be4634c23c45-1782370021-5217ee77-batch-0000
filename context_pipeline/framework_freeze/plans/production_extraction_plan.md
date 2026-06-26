# Production Extraction Plan

## Scope and denominator

The production plan uses the same authoritative Stage 4E evidence universe: **286 conversations**, **36 project documents**, and **2 distinct design chats**. Stage 4E already covered the benchmark set plus the 40 blind calibration cases, leaving:

- **223 remaining conversations**
- **34 remaining project documents**
- **0 remaining design chats**
- **257 remaining Stage 3R/3R-P-bounded extraction targets**

A separate note is required for the raw normalized corpus: `context_pipeline/normalized/conversations.jsonl` contains 292 conversations, but Stage 4E selection operated on the 286-conversation evidence-map universe. The extra 6 normalized conversations stay deferred until the evidence-map boundary is deliberately extended; they must not be mixed into the first frozen-framework extraction run.

## Batch recommendation

Recommended starting batch size: **75 cases per production extraction batch**.

- This stays inside the instructed 50-100 range.
- It is large enough to test scaling without becoming operationally brittle.
- It yields **4 estimated batches** for the 257 remaining in-scope targets: `75 + 75 + 75 + 32`.

## Batch order

1. remaining conversations, ordered by structural complexity bands with date spread preserved
2. remaining project documents interleaved into batches 2-4 to avoid document-only end-loading
3. no design-chat batch is needed because the full design-chat corpus is already represented in the authoritative benchmark set

## Per-batch workflow

1. build frozen evidence bundles from repaired staging inputs
2. run semantic extraction with the frozen ontology, rules, and confirmed resolutions
3. validate schema, ID uniqueness, reference resolution, and provenance fields
4. classify all review items into the 4 frozen review categories
5. checkpoint outputs and metrics before moving to the next batch

## Checkpoint strategy

At the end of every batch, write:

- batch case list
- extraction results
- candidate entities
- candidate relationships
- missing-source impacts
- unresolved/review items
- validation summary
- rules-applied summary
- completion manifest
- quality review memo

Batch N+1 starts only if Batch N completes with:

- schema parse success
- reference resolution success
- no prior-stage file drift
- genuinely unresolved rate still under 10%
- no recurring failure pattern across 3 or more cases

## Subscription-only execution strategy

- keep semantic judgment subscription-only, matching Stage 4E
- allow scripts only for deterministic loading, writing, checksums, counting, validation, comparison, and reporting support
- do not introduce API automation during the first frozen-framework extraction wave
- reconsider API automation only after at least one successful production extraction batch under the frozen framework

## Retry policy

- retry once for transient formatting or serialization defects
- rerun a single case when reference resolution fails due to a packaging defect
- do not rerun an entire batch unless validation shows a systemic error pattern
- if the same semantic defect appears in 3 or more cases, stop and open a framework review rather than pushing ahead

## Stopping conditions

Stop staged extraction if any of the following occurs:

- genuinely unresolved rate exceeds 10% in a batch
- provenance discipline regresses from effectively zero violations
- the same false-project, ownership, or merge error repeats across 3 or more cases
- frozen rules are repeatedly insufficient for a new pattern across 3 or more cases

## Expected outputs

The staged extraction should produce batch-scoped results aligned with Stage 4E outputs plus frozen rule annotations. It should not consolidate the final context database yet; that happens only after cross-batch consolidation review.
