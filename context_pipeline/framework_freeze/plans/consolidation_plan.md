# Cross-Conversation Consolidation Plan

Consolidation happens only after per-batch extraction is complete and validated. The default is conservative linking, not aggressive merge.

## Allowed consolidation outcomes

- `same_project`
- `subproject`
- `project_phase`
- `recurring_responsibility`
- `shared_employer_or_client_context`
- `shared_organization_only`
- `possible_duplicate`
- `unrelated`

## Evidence required for stronger consolidation

Use multiple evidence classes before declaring `same_project` or `subproject`:

- matching project names or canonical aliases
- shared repositories, files, or deliverables
- same client, employer, or organization in the same workstream
- overlapping people and responsibilities
- compatible dates and continuing tasks
- explicit user confirmation
- frozen rules or confirmed resolutions already tying the records together

## Automatic non-merge rules

Do **not** merge solely because two records share:

- the same folder name
- the same topic
- the same tool
- the same employer
- the same course
- the same person

`hr-008a` is binding here: label collision alone yields at most `shared_context_only`.

## Decision ladder

1. same named deliverable/client/workstream with matching artifacts and dates -> `same_project`
2. same core project with narrower scoped deliverable or child outcome -> `subproject`
3. same project identity but clearly earlier/later milestone -> `project_phase`
4. repeated on-demand support without one continuous deliverable -> `recurring_responsibility`
5. shared employer/client but distinct activity -> `shared_employer_or_client_context`
6. same organization label only -> `shared_organization_only`
7. thin overlap with unresolved identity -> `possible_duplicate`
8. otherwise -> `unrelated`
