# Initial Context Database Plan

The future database stays downstream of extraction and consolidation. Stage 5A defines the target structure only.

## Profile layer

The profile record must support:

- goals
- preferences
- constraints
- education
- career direction
- experience
- skills
- recurring responsibilities

## Areas layer

The initial area taxonomy should include at least:

- Career Development
- Education
- Employment
- Freelancing / Client Work
- Software Projects
- Marketing
- Business Ideas
- Personal

## Project and work-entity layer

Each record must support:

- canonical ID
- canonical title
- type
- area
- status
- ownership
- user role
- context brief
- goals
- requirements
- decisions
- tasks
- outputs
- sources
- artifacts
- people
- organizations
- relationships
- timeline
- provenance
- unresolved items

## Proposed filesystem shape

```text
Area/
└── Project/
    ├── project.json
    ├── context.md
    ├── status.md
    ├── decisions.jsonl
    ├── tasks.jsonl
    ├── sources.jsonl
    ├── artifacts.jsonl
    ├── relationships.jsonl
    ├── history.jsonl
    └── prompts/
```

## Generation boundary

Do not generate the final database during Stage 5A. The next dependency is a successful Stage 5B staged extraction followed by consolidation review.
