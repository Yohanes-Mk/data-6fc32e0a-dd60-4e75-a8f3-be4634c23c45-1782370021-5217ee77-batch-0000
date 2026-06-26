# Stage 4E Calibration Report

50-case subscription-only semantic calibration batch (10 benchmark + 40 blind), five checkpointed batches, language-model semantic judgment over Stage 3R + the mandatory 3R-P overlay. Purpose: finalize reusable decision rules and decide framework freeze.

## Headline

- 50/50 cases processed (7 empty recorded, not substituted).

- 63 candidates: work_entity 25 (**5 strict projects**), project_knowledge 18, context_entity 7, non_project 13.

- Confidence {'high': 40, 'medium': 21, 'low': 2}; separate status-current confidence {'high': 20, 'low': 16, 'medium': 27}.

- 22 relationships (all evidence-backed); 7 clusters; 3 possible-duplicate sets; 4 profile-level facts; 3 recurring responsibilities.

- **Benchmarks 16/16 pass.**

- Human-review rate **32% → 10%** after recurring rules; 11 questions auto-resolved by existing rules.

- Review classification: {'case_specific_exception': 2, 'genuinely_unresolved': 1, 'covered_by_existing_rule': 9, 'new_reusable_rule': 1}.

- Missing-source impacts 13 (all do_not_infer); 149 null filenames preserved (0 invented); 0 provenance violations.

- 209 prior-stage files unchanged.


## Strict projects (5)

- Career-mentor / personal context project (scope cleanup & tradeoffs) — drifted/current_confirmed (conf medium)
- AI Aggregator — end-to-end GenAI project (Ebbelaar-tutorial build) — active/current_confirmed (conf high)
- Kibur RAG chatbot / CO-OP build (in progress) — active/current_confirmed (conf medium)
- Personal applied-AI-engineering learning & career roadmap — active/current_confirmed (conf high)
- Fleet Command — Unity hex-grid strategy game (SE: Computer Animation course project) — active/historical_status_unknown (conf high)

## Metrics (Part 14)

- cases completed: 50; empty/no-candidate: 7
- candidates by layer: {'non_project_interaction': 13, 'work_entity': 25, 'project_knowledge': 18, 'context_entity': 7}
- candidates by type: {'generic_question': 6, 'assistant_suggestion': 1, 'assignment': 9, 'exam_preparation': 1, 'artifact': 3, 'task': 6, 'one_off_request': 4, 'tool_execution_trace': 1, 'assistant_explanation': 1, 'project': 5, 'recurring_responsibility': 2, 'source': 4, 'workflow': 2, 'tool': 3, 'job_application': 1, 'standalone_idea': 2, 'initiative': 2, 'person': 2, 'proposed_decision': 1, 'client_engagement': 2, 'employer': 1, 'open_question': 1, 'decision': 1, 'research_effort': 1, 'institution': 1}
- work entities: 25; strict projects: 5; false-project findings: 0
- evidence coverage: 63/63 candidates
- provenance violations: 0
- confidence distribution: {'high': 40, 'medium': 21, 'low': 2}
- status-confidence distribution: {'high': 20, 'low': 16, 'medium': 27}
- endorsement distribution: {'not_applicable': 26, 'no_endorsement': 6, 'explicit_acceptance': 9, 'implicit_continuation': 16, 'modification': 6}
- relationships: 22; duplicate/cluster candidates: 7 clusters / 3 duplicate sets
- human-review cases: 5
- human-review rate before rules: 0.32; after rules: 0.1
- questions resolved by existing rules: 11
- proposed new reusable rules: 1
- case-specific exceptions: 2; genuinely unresolved: 1
- missing-source rate: 13 impacts across 6 cases
- attachment limitation rate: 14 cases had attachments, all binaries unavailable (text used where present)
- repeated systemic failure count: 0
