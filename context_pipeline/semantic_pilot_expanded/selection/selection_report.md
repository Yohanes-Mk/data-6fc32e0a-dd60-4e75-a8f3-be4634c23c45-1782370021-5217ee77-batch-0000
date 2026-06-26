# Stage 4D — Expanded Pilot: Case Selection Report

24 distinct cases: 6 benchmark + 18 blind. The 18 blind cases were selected **deterministically
from structural metadata only** and locked (`selection/selection_lock.json`,
sha256 `9c2411cf…`) before any semantic content was inspected.

## Benchmark cases (6)

| Case | Target | Why |
|---|---|---|
| ex-01 | 14f3c888 | Transcript-formatting one-off (not a project) |
| ex-02 | 2838a734 | Pesticide academic assignment |
| ex-03 | 94f53cfc | Mixed study/career (not one broad project) |
| ex-04 | b8366901 | AI learning roadmap (active project) |
| ex-05 | e2fc5641 | Fleet Command / Unity (real project, status unresolved); attachment-heavy |
| ex-06 | Client Radar (design-chat a5eb06ca + conv f04cc5a5) | ONE Accenture client_engagement, two facets (audit/design + repo implementation), co-authored audit content (Stage 3R-P) |

## Blind cases (18) — deterministic structural selection

**Complexity score** (structural only): `packets×2 + user_evidence×0.05 + branches×1.5 +
attachment_occurrences/10 + missing×0.3 + tool_log×0.5 + pasted×1.0`. Tiers by score quartiles of
the eligible pool (276 conversations, after excluding the 10 Stage 4C conversations):
low ≤3.5, medium ≤3.8, high ≤11.8, extreme >11.8. Within each tier, cases were picked by an
even spread across date and rank (no semantic inspection).

| Case | Conv/Doc/DC | Tier | Score | pk | ue | br | att | miss | span |
|---|---|---|---|---|---|---|---|---|---|
| ex-07 | 19b86969 | low | 1.5 | 0 | 0 | 1 | 0 | 0 | (empty) |
| ex-08 | 1f2a6b9a | low | 3.5 | 1 | 0 | 1 | 0 | 0 | 2025-03-12 |
| ex-09 | 3357cec5 | low | 3.55 | 1 | 1 | 1 | 0 | 0 | 2026-06-25 |
| ex-10 | 37aabbd3 | medium | 3.8 | 1 | 6 | 1 | 0 | 0 | 2024-11-02 |
| ex-11 | e612528d | medium | 3.6 | 1 | 2 | 1 | 0 | 0 | 2026-03-03 |
| ex-12 | f4e5df2e | medium | 3.6 | 1 | 2 | 1 | 0 | 0 | 2026-03-24 |
| ex-13 | acf6687a | medium | 3.7 | 1 | 4 | 1 | 0 | 0 | 2026-04-27 |
| ex-14 | 3aa7c40a | medium | 3.75 | 1 | 5 | 1 | 0 | 0 | 2026-06-18 |
| ex-15 | 681bad4a | high | 4.5 | 0 | 0 | 3 | 0 | 0 | (empty/branched) |
| ex-16 | 925a6676 | high | 4.7 | 1 | 8 | 1 | 2 | 2 | 2025-12-08 |
| ex-17 | dd1aabd1 | high | 3.85 | 1 | 7 | 1 | 0 | 0 | 2026-03-17 |
| ex-18 | 965b21a5 | high | 10.75 | 3 | 35 | 2 | 0 | 0 | 2026-04-16..30 |
| ex-19 | 6cf988f8 | high | 10.75 | 3 | 25 | 1 | 5 | 5 | 2026-06-24 |
| ex-20 | ab705905 | extreme | 109.45 | 2 | 69 | 68 | 0 | 0 | 2023-10-29..31 |
| ex-21 | ba42f9ff | extreme | 20.85 | 4 | 149 | 2 | 6 | 6 | 2026-04-11..29 |
| ex-22 | 8cdf0ae5 | extreme | 17.55 | 3 | 51 | 6 | 0 | 0 | 2026-06-16..23 |
| ex-23 | AD Campigns doc `digital_marketing_knowledge_base.html` | project_document | — | — | — | — | — | — | — |
| ex-24 | design chat `Trending animation request` | design_chat | — | — | — | — | — | — | — |

### Diversity coverage achieved (structural)
- **Dates:** 2023 (ex-20), 2024 (ex-10), 2025 (ex-08, ex-16), 2026 across all quarters.
- **Branched:** ex-20 (68 branches), ex-15 (3), ex-22 (6).
- **Attachment/missing-source:** ex-16, ex-19, ex-21.
- **Multi-day continuing:** ex-18, ex-21, ex-22.
- **Near-empty / no-real-project candidates:** ex-07, ex-15 (retained, not substituted).
- **Document / design-chat:** ex-23, ex-24.
- Tier counts: low 3, medium 5, high 5, extreme 3 (+1 document +1 design-chat) = 18.

Semantic-content diversity (academic / career / technical / business / research / no-project) is a
*goal*; it can only be confirmed after inspection and is reported in `pilot_report.md`. No case was
swapped after inspection. Empty/unusable cases are recorded as such rather than replaced.

## Anti-bias procedure (Part 2)
1. Blind cases selected from structural metadata only.
2. `selected_cases.jsonl` written.
3. `selection_lock.json` sha256 recorded over the 18 blind selections.
4. Only then was semantic content inspected.
5. No difficult/uninteresting case was replaced post-inspection.
6. Genuinely empty cases (ex-07, ex-15) retained and reported.

See `excluded_selection_candidates.jsonl` for notable non-selections (e.g. 5bf2f2cd, the
single-day 58-packet conversation deprioritized in favor of multi-day continuing-work spans).
