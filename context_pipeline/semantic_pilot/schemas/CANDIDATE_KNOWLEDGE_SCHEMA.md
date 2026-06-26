# Candidate Knowledge Schema

Stage 4A candidate records are strict JSON objects validated against `candidate_knowledge.schema.json`. Every substantive candidate must reference evidence source units and message IDs where applicable. Assistant-origin candidates remain conditional unless user evidence endorses them. Tool-output-only candidates remain unverified.

Candidate types include project, subproject, standalone idea, goal, motivation, research question, source, research finding, decision, proposed decision, constraint, requirement, preference, task, open question, output, file or artifact, prompt, workflow, milestone, direction change, abandoned thread, unresolved reference, person, organization, and tool or platform.

Status values are idea, exploring, planned, active, paused, drifted, blocked, completed, abandoned, merged, and unknown. Endorsement values are explicit acceptance, explicit rejection, modification, implicit continuation, no endorsement, and unclear.
