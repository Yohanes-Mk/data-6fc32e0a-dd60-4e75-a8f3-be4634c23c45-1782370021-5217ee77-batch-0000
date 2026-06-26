# Phase 1 — Blind Semantic Self-Review of Claude Candidates

Performed before reading the Codex repair. Each candidate set was reviewed against the
issue checklist in the brief. Issues found and their resolutions are recorded below.

## Issue-by-issue findings

### False project classification
- **Checked, none emitted.** Only two `project` candidates exist; both satisfy all nine
  strict criteria. Every weaker activity was demoted to assignment / job_application /
  exam_preparation / initiative / standalone_idea / recurring_responsibility.
- The transcript-formatting (14f3c888) and the two Q&A conversations (244ba1ae, 248a80bc)
  were explicitly kept as non-knowledge rather than projects.

### Missing real project
- **Two real projects could have been under-extracted under the selection labels:**
  - 2838a734 was labelled false_project; Claude finds a real *assignment* and recovers it.
  - The 94f53cfc "single project" label hides five real activities; all five were recovered
    as separate work entities.

### Fragmentary / message-opening titles
- **Resolved.** No `canonical_title` copies a raw message opening. Titles describe the
  underlying activity (e.g. "Pesticide groundwater exposure & risk-assessment coursework",
  not "trying to do this with claude in excel").

### Unsupported claim
- The Accenture role (`a_context_accenture_inferred`) is the main risk: it is asserted only
  by the assistant. **Resolved** by marking it `assistant_origin=true`, `confidence=low`,
  `explicit_or_inferred=inferred`, and `requires_human_review=true`, with a contradiction
  noting the user never confirmed it.

### Assistant-origin confusion
- The ExamPro "skip" recommendation and the HTML artifacts originate from the assistant.
  **Resolved** by setting `assistant_origin=true` and using endorsement
  `implicit_continuation` / `modification`, not user decision/acceptance.

### Wrong endorsement
- **Re-audited every explicit endorsement.** `explicit_acceptance` is used only where the
  user wrote a clear yes ("Yes that does make sense and also I agree phase A is more
  important"; "let us go with Tsotsi"; "ask it to fill them instead"). Requests alone were
  not treated as acceptance.

### Overconfident classification / missing low-confidence
- Confidence is spread (39 high / 7 medium / 1 low), not defaulted to medium. Low/medium
  applied where evidence is inferred or generalization is uncertain (Accenture role; tone
  preference generalization; Unity-AI adoption outcome; YouTube channel status).

### Duplicate candidate
- **None.** All 47 ids unique (validator confirms). The voice/tone preference appears in two
  conversations and is intentionally kept as two conversation-scoped preferences linked by an
  `associated_with` relationship rather than merged into one cross-conversation fact.

### Over-fragmentation
- The roadmap and Fleet Command projects were kept as single projects with attached knowledge
  rather than split per debugging session, to avoid fragmenting one project into many.

### Over-merging
- **Primary correction this stage.** 94f53cfc was *not* merged into one project; it was split
  into five activities plus an explicit `recurring_responsibility` umbrella flagged
  `requires_human_review=true`.

### Missing goal / decision / task / output / direction change
- Captured: goal change (lecture exam→understanding), decisions (Track-A-first, choose Tsotsi,
  orchestrate-Excel, make-it-playable), tasks (expected-answer), outputs/artifacts (prompts,
  HTML roadmap, paper, slides, phase tracker), direction changes, a blocker, and a milestone.

### Generic relationship
- No relationship was created purely from co-occurrence. The five sub-activities in 94f53cfc
  are linked to the umbrella only with `associated_with` (explicitly *not* `part_of`) and
  flagged for review, precisely to avoid asserting they are one project.

### Missing temporal context
- Every candidate carries `temporal_status` and `status`. Historical projects (2024 study
  helper; the spring-2026 Unity and film projects) are marked historical/completed; the
  roadmap is current/active.

## Net self-review outcome

No false projects, no fragmentary titles, no unsupported user facts left unflagged. The two
substantive risks in *Claude's own* extraction are:
1. The `recurring_responsibility` umbrella in 94f53cfc is a modelling choice that a human may
   prefer to drop entirely (flagged for review).
2. The cross-conversation "same user / same preference" links are inferred and flagged.

Both are surfaced rather than asserted. Phase-1 self-review status: **pass**.
