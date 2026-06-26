# Stage 4E Semantic Quality Review

Per-case language-model semantic judgment; no scripts/keywords/templates decided type, status, ownership, boundary, title, confidence, endorsement, relationship, or merge.

## No template behavior

The 40 blind cases produced genuinely varied outputs: empty records, tech-support one-offs, homework assignments (SVD/PCA/calculus/DB/C++/Python), exam-prep authoring, group contribution statements, learning logs, career-content tasks (NSBE pitch/LinkedIn), Accenture training tasks, tool retrieval traces, a barista skill-building responsibility, three real software/career projects (AI Aggregator, career-mentor, Kibur RAG), an internship job-application pipeline, an undeveloped freelance idea, and one client/professional marketing source document. Type variety: {'generic_question': 6, 'assistant_suggestion': 1, 'assignment': 9, 'exam_preparation': 1, 'artifact': 3, 'task': 6, 'one_off_request': 4, 'tool_execution_trace': 1, 'assistant_explanation': 1, 'project': 5, 'recurring_responsibility': 2, 'source': 4, 'workflow': 2, 'tool': 3, 'job_application': 1, 'standalone_idea': 2, 'initiative': 2, 'person': 2, 'proposed_decision': 1, 'client_engagement': 2, 'employer': 1, 'open_question': 1, 'decision': 1, 'research_effort': 1, 'institution': 1}.

## Confidence and status discipline

- Low confidence used where evidence is fragmentary or identity uncertain (bl-34 webview, bl-35 garbled chat).

- status_current_confidence reported on a separate axis: 16 low (Fleet Command, CSCI group, most homework completion).

- No current status inferred from recency alone; historical/completed only with confirmation or resolution.

## Provenance

- Pasted transcript/tutorial content typed as source (bl-36 Ebbelaar tutorial), tool retrieval as tool_execution_trace (bl-21 Granola), not as user facts.

- Co-authored material flagged (co_authored_flag) without treating assistant claims as user-accepted.

- Group work kept group_owned (cb-07, bl-13); not represented as sole authorship.

## Boundary discriminations that worked

- AABS conference briefing (bl-40) kept OUT of the Personal/Family Marketing umbrella (client/professional source).

- 'Project 3' name collision resolved as two distinct courses (bl-37 ML regression vs cb-07 CSCI 430/530).

- Accenture activities linked by one employer context, not collapsed.

## Residual semantic uncertainties (flagged, not errors)

- [case_specific_exception] bl-29: Boundary: is the 'career mentor project' the same entity as the per-project context-DB idea (ex-14) and/or the AI Aggregator (bl-36)? Needs human confirmation of identity/merge.
- [genuinely_unresolved] bl-34: Ownership/identity of the reviewed VS Code webview codebase is unclear (user project vs third-party vs coursework). Recommended default: keep as task, ownership unknown, low confidence, until the user clarifies.
- [covered_by_existing_rule] bl-36: Possible part_of the AI learning roadmap (cb-04) and possible_same_entity with the career-mentor/context-DB work (bl-29/ex-14). Clustering handled by hr-011; relationship emitted, no human review forced.
- [case_specific_exception] bl-38: Is Kibur RAG/CO-OP a user-owned personal project, a client engagement, or coursework? And is it the same Kibur entity as the AABS conference marketing (bl-40)? Recommended default: keep as user-owned project, medium confidence, shared_context_only with the AABS doc.
- [new_reusable_rule] bl-40: Source-vs-artifact + umbrella boundary: a document sharing the 'AD Campigns' project label is professional/client (Kibur/AABS), not personal/family marketing. Propose generalized rule hr-008a (label-collision does not imply umbrella membership).
