# Stage 4E Human-Review Queue

After applying the 22 codified recurring rules, **5 of 50 cases** (rate 0.1) remain flagged. Before rules, 16 cases touched a review concern (rate 0.32); 11 were auto-resolved.

## Only the four reviewable categories are queued

- covered_by_existing_rule (auto-applied, removed from queue): 9

- new_reusable_rule (proposed, not yet authoritative): 1

- case_specific_exception (case-level only): 2

- genuinely_unresolved (one focused question each): 1


## Genuinely unresolved (needs a user decision)

- **bl-34 bl34_vscode_webview_review** — Ownership/identity of the reviewed VS Code webview codebase is unclear (user project vs third-party vs coursework). Recommended default: keep as task, ownership unknown, low confidence, until the user clarifies.
  - DB consequence: ownership/identity left as recorded default until confirmed.
  - Recommended default: keep as extracted (task, ownership unknown, low confidence).

## Case-specific exceptions (retained, not redesign triggers)

- bl-29: Boundary: is the 'career mentor project' the same entity as the per-project context-DB idea (ex-14) and/or the AI Aggregator (bl-36)? Needs human confirmation of identity/merge.
- bl-38: Is Kibur RAG/CO-OP a user-owned personal project, a client engagement, or coursework? And is it the same Kibur entity as the AABS conference marketing (bl-40)? Recommended default: keep as user-owned project, medium confidence, shared_context_only with the AABS doc.

## New reusable rule proposed

- **hr-008a** Project-label collision does not imply marketing-umbrella membership — seen in ['bl-40']; Do NOT pull it into the Personal/Family Marketing Support umbrella; classify by actual ownership/context (client/professional). Default to shared_context_only.
