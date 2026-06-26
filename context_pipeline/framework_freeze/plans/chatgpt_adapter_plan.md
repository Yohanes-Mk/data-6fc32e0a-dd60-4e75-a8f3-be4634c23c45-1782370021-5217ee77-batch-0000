# ChatGPT Adapter Plan

The adapter is a contract, not an implementation, in Stage 5A.

## Target pipeline

```text
Provider export
-> provider-specific adapter
-> common normalized schema
-> frozen provenance layer
-> frozen semantic extractor
-> common context database
```

## Required ChatGPT adapter outputs

The adapter must emit, at minimum:

- conversation IDs
- message IDs
- authors
- timestamps
- branches
- attachments
- tool calls
- projects or GPT contexts when available
- content blocks
- source references
- provenance fields

## Adapter obligations

- preserve branching and parent-child message relationships
- preserve null filenames instead of inventing them
- separate pasted assistant text from direct user-authored evidence
- record tool execution traces distinctly from user assertions
- normalize attachment occurrences and content hashes when available
- surface missing-source references explicitly

## Reuse goal

If the adapter satisfies the source adapter contract, it should be able to reuse the Claude frozen semantic pipeline unchanged above the adapter layer.
