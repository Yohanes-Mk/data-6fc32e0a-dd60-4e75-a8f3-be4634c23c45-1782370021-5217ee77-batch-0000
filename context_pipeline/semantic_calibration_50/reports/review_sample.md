# Stage 4E Review Sample (representative cases)

## cb-01 (conversation_benchmark)
- **one_off_request** — One-off request to reformat a pasted video transcript verbatim
  - status one_time/point_in_time · conf high · scc high · ownership user_owned
  - rules ['hr-001'] · review False
  - rationale: User's words frame verbatim formatting; hr-001.

## cb-06 (benchmark_client_radar_engagement)
- **client_engagement** — Client Radar accessibility & repository-implementation engagement (Accenture, user-owned)
  - status active/current_confirmed · conf high · scc high · ownership user_owned
  - rules ['hr-006'] · review False (covered_by_existing_rule)
  - rationale: Stage 3R-P resolution stage3rp:resolution:client_radar; user owns the engagement, audit co-authored.
- **tool** — Claude Code (used on the Client Radar repo)
  - status active/current_inferred · conf high · scc medium · ownership user_owned
  - rules [] · review False
  - rationale: User explicitly uses Claude Code with the repo.
- **employer** — Accenture (confirmed employer; client context for Client Radar)
  - status active/current_confirmed · conf high · scc high · ownership user_owned
  - rules ['hr-009', 'hr-012'] · review False
  - rationale: hr-006 confirmed; brand context in the engagement.
- **client_engagement** — Client Radar accessibility engagement — manager sync, high-level summary deliverable
  - status active/current_confirmed · conf high · scc high · ownership user_owned
  - rules ['hr-006', 'hr-011'] · review False (covered_by_existing_rule)
  - rationale: Explicit project ownership ('my project'), manager named, deliverable described; same engagement as ex-06.
- **person** — Lauren (Client Radar engagement manager at Accenture)
  - status active/current_confirmed · conf high · scc medium · ownership user_owned
  - rules [] · review False
  - rationale: Explicitly named as manager.
- **open_question** — Open question: ask the manager how she uses AI / frameworks (Claude Code & general)
  - status active/current_confirmed · conf medium · scc low · ownership user_owned
  - rules [] · review False
  - rationale: Explicit user intent to ask; outcome unknown.

## cb-07 (benchmark_group_assignment)
- **assignment** — CSCI 430-530 Project 3 submission document (Part 2)
  - status completed/historical_confirmed · conf medium · scc low · ownership group_owned
  - rules ['hr-007', 'hr-013'] · review False (covered_by_existing_rule)
  - rationale: Explicit user requests to build/format the submission; attachments name a different person.

## cb-08 (benchmark_marketing_umbrella)
- **initiative** — Social-media ad-boosting campaign (Meta/LinkedIn, Addis Ababa, 10-day push)
  - status completed/historical_confirmed · conf high · scc medium · ownership user_owned
  - rules ['hr-008', 'hr-022'] · review False (covered_by_existing_rule)
  - rationale: Explicit ownership, budget, multi-platform, copy iterations over days.
- **decision** — Decision: run the boost on a continuous daily budget, Addis Ababa focus
  - status completed/current_inferred · conf medium · scc medium · ownership user_owned
  - rules [] · review False
  - rationale: Explicit user choices about budget/geo.
- **source** — Digital Marketing Knowledge Base (2025–2026) project document
  - status active/unknown · conf medium · scc low · ownership user_owned
  - rules ['hr-008', 'hr-014'] · review False (covered_by_existing_rule)
  - rationale: Document content is a marketing knowledge base; authorship/role inferred.
- **standalone_idea** — Trending-animation design request (matcha kinetic-type short)
  - status exploring/historical_confirmed · conf medium · scc low · ownership user_owned
  - rules ['hr-008'] · review False
  - rationale: User gives a loose brief; mostly assistant-driven scoping.

## cb-10 (benchmark_avatar_bci_lab)
- **research_effort** — AVATAR lab (BCI) work at St. Cloud State University
  - status completed/historical_confirmed · conf high · scc high · ownership user_owned
  - rules ['hr-010'] · review False
  - rationale: Genuine user description of the lab role is explicit; most other segments are pasted GitHub issue listings (tool/log), so depth of current involvement is uncertain.
- **institution** — St. Cloud State University — AVATAR lab / CSF 400
  - status active/historical_status_unknown · conf high · scc medium · ownership user_owned
  - rules [] · review False
  - rationale: Explicitly named by the user ('BCI lab at Saint Cloud University... CSF 400').
- **task** — Task: add console logging to the AVATAR 'Artificial Intelligence' tab
  - status active/historical_status_unknown · conf medium · scc medium · ownership user_owned
  - rules [] · review False
  - rationale: Short explicit user instruction; surrounding context is pasted logs.

## bl-01 (blind_conversation_low_complexity)
- EMPTY: recorded empty (hr-016), no candidate, not substituted.

## bl-13 (blind_conversation_medium_complexity)
- **artifact** — Individual contribution statement — CSCI 440 Project 2 (German Credit Risk)
  - status completed/historical_confirmed · conf high · scc medium · ownership group_owned
  - rules ['hr-013', 'hr-018', 'hr-002', 'hr-017'] · review False
  - rationale: User (Yohannes Nigusse) supplies a contribution statement describing sections 5-7 he owned in a group ML project, and asks for a PDF. The statement is a user-authored output artifact. Group project ->

## bl-29 (blind_conversation_high_complexity)
- **project** — Career-mentor / personal context project (scope cleanup & tradeoffs)
  - status drifted/current_confirmed · conf medium · scc medium · ownership user_owned
  - rules ['hr-011', 'hr-021'] · review True (case_specific_exception)
  - rationale: User explicitly owns a 'career mentor project' that has accumulated ~18 files and 'diverged'; asks to clean up, make tradeoffs, and plan. Satisfies intended_outcome, continuing_actions, user_ownership

## bl-36 (blind_conversation_extreme_complexity)
- **project** — AI Aggregator — end-to-end GenAI project (Ebbelaar-tutorial build)
  - status active/current_confirmed · conf high · scc medium · ownership user_owned
  - rules ['hr-018', 'hr-017', 'hr-011', 'hr-014'] · review True (covered_by_existing_rule)
  - rationale: Largest blind case (565 segments, 313 user). User owns and builds an AI Aggregator GenAI project on a dated multi-day plan (Mar 9-12), following the Dave Ebbelaar tutorial, with code, attachments, and
- **source** — Dave Ebbelaar 'Build a Complete End-to-End GenAI Project in 3 Hours' tutorial (external)
  - status active/current_confirmed · conf high · scc medium · ownership third_party
  - rules ['hr-014'] · review False
  - rationale: External YouTube tutorial the user follows; clearly third-party source material, not a user artifact. hr-014.
- **workflow** — Standing rule: user writes code first, AI reviews (never AI-writes-first)
  - status active/current_confirmed · conf high · scc medium · ownership user_owned
  - rules ['hr-015'] · review False
  - rationale: Explicit, repeated user workflow constraint governing how Claude assists. Appears as a standing rule; candidate for profile-level promotion if it recurs across cases (hr-015).

## bl-38 (blind_conversation_extreme_complexity)
- **job_application** — Summer 2026 internship pipeline (CPT) — active job search
  - status active/current_confirmed · conf high · scc high · ownership user_owned
  - rules ['hr-012', 'hr-021'] · review False
  - rationale: User has a live Plan-A internship pipeline (Morgan Stanley screening done, Bentley in progress, 12+ applications out, 5 due this week) via CPT. Explicit, ongoing, user-owned career search -> job_appli
- **standalone_idea** — Plan B: freelance/contract AI work (undefined fallback)
  - status idea/current_inferred · conf medium · scc medium · ownership user_owned
  - rules ['hr-020'] · review False
  - rationale: Freelance is explicitly a mentioned-but-undeveloped fallback ('never concretely scoped'). Typed standalone_idea, status idea -> NOT a project (fails continuing-actions/tasks). hr-020.
- **project** — Kibur RAG chatbot / CO-OP build (in progress)
  - status active/current_confirmed · conf medium · scc medium · ownership user_owned
  - rules ['hr-011', 'hr-021', 'hr-005'] · review True (case_specific_exception)
  - rationale: User is 'actively building' a RAG chatbot tied to Kibur work ('chatbot that knows our stuff'); resume thread (bl-33) shows its status is in flux (architecture designed vs deployed). Meets >=3 project 

## bl-40 (blind_project_document)
- **source** — AABS 2026 Connect Conference campaign briefing (Kibur College, prepared by conference marketing team)
  - status completed/historical_confirmed · conf medium · scc medium · ownership unknown
  - rules ['hr-014', 'hr-008'] · review True (new_reusable_rule)
  - rationale: Project-document 'AABS_2026_Campaign_Briefing.docx' in the 'AD Campigns' project. It is a professional/CLIENT conference-marketing briefing prepared by the AABS conference marketing team — authorship 

## bl-34 (blind_conversation_extreme_complexity)
- **task** — Code review help: VS Code webview reset.css / index.js (DOM highlighter)
  - status completed/historical_status_unknown · conf low · scc low · ownership unknown
  - rules ['hr-018', 'hr-017', 'hr-011', 'hr-014'] · review True (genuinely_unresolved)
  - rationale: User submits JS/CSS in chunks for review across a deeply branched session (12 branches) with several null-filename attachments (binaries not inspected). The codebase ownership is unclear (could be cou

