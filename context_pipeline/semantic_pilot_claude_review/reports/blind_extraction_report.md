# Phase 1 — Blind Independent Extraction Report

**Stage 4B, Claude Code semantic cross-review.** This report documents the blind
independent extraction performed *before* reading any Codex repair results, audit, or
reports. Inputs used: the selected-conversation list and the conversation context
bundles only. The extraction (every type, project decision, confidence, and endorsement)
was made by the language model reading the eight bundles; scripts only wrote, resolved
references, and validated.

## Totals

- Candidate entities (work / knowledge / context): **43**
- Excluded / non-knowledge records: **4**
- Relationships: **41**
- Conversations processed: **8 / 8**

## Candidate counts by type (entities + excluded = 47)

| Type | Count |
|---|---|
| decision | 5 |
| artifact | 5 |
| platform | 4 |
| assignment | 3 |
| preference | 3 |
| person | 3 |
| project | 2 |
| workflow | 2 |
| constraint | 2 |
| source | 2 |
| one_off_request | 2 |
| initiative | 1 |
| recurring_responsibility | 1 |
| job_application | 1 |
| standalone_idea | 1 |
| exam_preparation | 1 |
| direction_change | 1 |
| task | 1 |
| research_question | 1 |
| blocker | 1 |
| milestone | 1 |
| organization | 1 |
| employer | 1 |
| transcript_fragment | 1 |
| generic_question | 1 |

By knowledge layer: work_entity 10, project_knowledge 24, context_entity 9, non_knowledge 4.

## Confidence distribution

- high: 39
- medium: 7
- low: 1

The single low-confidence candidate is the assistant-inferred Accenture affiliation
(`claude:cand:a_context_accenture_inferred`) — recorded precisely because it is an
unconfirmed assistant inference. Confidence was not defaulted to medium; most candidates
rest on direct, repeated user statements and are high.

## Endorsement distribution

- not_applicable: 29
- modification: 8
- implicit_continuation: 5
- explicit_acceptance: 4
- unclear: 1

Every `explicit_acceptance` / `modification` cites user-authored evidence. Assistant
recommendations the user did not explicitly accept (e.g. skipping the ExamPro course)
are recorded as `implicit_continuation` with `assistant_origin=true`, never as user
decisions.

## Per-conversation findings (project shape)

| Conv | Title | Selection label | Claude's finding |
|---|---|---|---|
| 14f3c888 | Transcript formatting request | false_project | **No project.** Verbatim transcript-formatting one-off; the AI-digest-app content is third-party transcript material. Confirms false_project. |
| 2838a734 | Getting started with Claude in Excel | false_project | **One real assignment.** A graded pesticide groundwater risk-assessment assignment (E_1/E_2/E_3, matriculation number) + an adopted Claude-in-Excel workflow. **Disputes false_project.** |
| 94f53cfc | Efficient Lecture Comprehension Assistance | plausible_real_project | **Multiple distinct activities (5).** Lecture-study system, OS lab, Amazon resume, YouTube policy, linear algebra exam prep. **Over-merge risk** in the single-project framing. |
| b8366901 | Roadmap kitchen | plausible_real_project | **One strong project** — applied-AI-engineering learning/career roadmap. Confirms plausible_real_project (meets all 9 criteria). |
| e2fc5641 | Fleet Command (Unity) | attachment_heavy | **One major project** — multi-week Unity strategy game. But **attachments empty despite attachment_heavy label** (material omission). |
| c69f5e03 | Final project planning and execution | assistant_tool_heavy | **One real assignment** — Tsotsi film-analysis final project (paper + slides + presentation). |
| 244ba1ae | Defending weak interview questions about Accenture | project_document_linked_proxy | **No project.** One-off advice; Accenture role is assistant-inferred, not user-confirmed. Proxy selection is documented, not a real document link. |
| 248a80bc | DC overtime pay requirements | deterministic_fill | **No project.** One-off factual legal Q&A. |

## The strict project test (applied)

Only two candidates were labelled `project`; both list all nine criteria:

- `claude:cand:r_aiengineer_roadmap` (AI-engineering roadmap) — outcome, continuing
  actions, ownership, milestones/tasks, deliverable (HTML), research, decisions/constraints,
  repeated over multiple days, identifiable state.
- `claude:cand:u_fleet_command` (Unity Fleet Command) — same nine, over multiple weeks.

Real but lesser work entities were deliberately *not* called projects:
- `assignment`: pesticide risk-assessment, OS lab, Tsotsi film project.
- `job_application`: Amazon SDE internship.
- `exam_preparation`: linear algebra.
- `initiative`: lecture-study system.
- `standalone_idea`: YouTube policy-reviewer prompt.
- `recurring_responsibility`: the study-helper umbrella thread.

## Evidence, provenance, and tool discipline

- Generic tool calls (web_search/view/console logs) were **not** turned into platform or
  workflow candidates. `platform`/`workflow` candidates (Claude-in-Excel, Bezi, Unity AI,
  the multi-AI orchestration) exist only because the user is *evaluating, adopting, or
  repeatedly building with* those tools.
- Assistant-generated artifacts (prompts, HTML roadmap, slides) are recorded as artifacts
  with `assistant_origin=true` and endorsement `modification`/`implicit_continuation`,
  never as user-authored facts.

## Material omissions observed

1. **e2fc5641** is selected as attachment_heavy (attachment_count=92) yet its
   `attachment_or_document_references` array is empty — the GDD/SDD and screenshots the
   user repeatedly references are not surfaced. (See `unresolved_items.jsonl`.)
2. Across the tool-heavy conversations, many `user_authored_source_units` actually contain
   pasted Bezi / Claude-Code / Unity-console output mislabeled `user_statement`. Candidates
   were based only on genuine user authorship.
3. Large pasted numeric blocks in 2838a734 are iteration *data*, not new user statements.
4. Deep-research results in b8366901 are not preserved.

See `unresolved_items.jsonl` for the four unresolved references and their impact.
