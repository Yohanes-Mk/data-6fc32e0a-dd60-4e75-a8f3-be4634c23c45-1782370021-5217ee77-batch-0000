# Runtime Context Retrieval Plan

Stage 5A defines desired retrieval behavior for a future assistant, without building it yet.

## Retrieval flow

```text
User request
-> retrieve profile context
-> retrieve relevant areas/projects
-> determine existing project vs new project vs one-off
-> answer using context
-> propose or perform database update
```

## Routing outcomes

- `existing_project`
- `new_project`
- `subproject_or_phase`
- `recurring_responsibility`
- `profile_question`
- `one_off_request`
- `ambiguous_review`

## Create a new project only when

- the request passes the strict project test
- no strong existing-project match exists
- the work appears meaningfully continuing
- ownership is clear
- the outcome or state is identifiable

## Update an existing project when

- identity match is strong
- client/employer/course/repository/deliverable matches
- surrounding project context matches
- the new request is clearly a continuing task, phase, or update

## Conservative default

When identity is thin or the only overlap is a label, route to `ambiguous_review` or `shared_context_only` rather than creating a bad merge.
