# Stage 4E Selection Report

Exactly **50 cases** were selected: **10 benchmark/policy cases** (carrying authoritative Stage 4D
and Stage 3R-P extractions) and **40 blind calibration cases** (chosen by deterministic structural
metadata, locked before any semantic content was inspected).

## Selection method
- **Universe:** 286 conversations in the Stage 3R evidence maps, 36 project documents, 30
  design-chat packets (2 distinct design chats).
- **Excluded from blind pool:** the 24 conversation/document/design targets already semantically
  processed in Stage 4D, plus the AVATAR mc-10 conversation carried as benchmark cb-10
  (23 conversations + 1 document + 2 design chats). → 263 available conversations.
- **Complexity tiers:** computed from a purely structural score
  `chars/1000 + units*1.5 + branches*8 + attachments*4 + pasted*2 + tool_log*2 + transcript*1.5 +
  linked_docs*6 + missing_sources*1.5`, then split into rank quartiles (low / medium / high /
  extreme). Within each tier, cases were drawn by even **start-date spread** with deterministic
  tiebreak on conversation id. No semantic content was read during selection.

## Blind composition (40)
| tier | requested | selected | pool size |
|------|-----------|----------|-----------|
| low_complexity | 8 | 9 | 65 |
| medium_complexity | 12 | 12 | 66 |
| high_complexity | 12 | 12 | 65 |
| extreme_complexity | 6 | 6 | 67 |
| project_document | 1 | 1 | 36 docs (AD Campigns briefing, alpha-first unused) |
| design_chat | 1 | 0 (see note) | only 2 design chats, both used in 4D |

**Design-chat note.** The corpus contains only two design chats — *Client Radar Accessibility
Review* and *Trending animation request* — and **both were already used in Stage 4D** (Client Radar
as the cb-06 facet, Trending-animation as ex-24). No blind design chat is available. The
design-chat case type is therefore covered in the **benchmark tier**: cb-06 carries the Client
Radar design chat and cb-08 carries the Trending-animation design chat. To still total 40 blind
cases, the 40th blind slot is an additional low-complexity conversation (a near-empty/low diversity
target the spec explicitly requests). This is a genuine corpus limitation, not a selection gap; it
is recorded in `selection_lock.json`.

## Diversity achieved across the blind sample
Empty/near-empty conversations (bl-01..06, 0 chars), short low-complexity Q&A, medium homework /
career / planning, high-complexity multi-topic and attachment-bearing sessions, extreme cases with
deep branching (bl-34: 12 branches), heavy transcript+attachment material (bl-36: 24 attachments,
57 transcript segments, 48 missing-source refs), missing sources (bl-11/13/28/33/37), early
(2023-11) → recent (2026-06) date span, and one project-document case (bl-40, marketing).

## Lock
- Blind selection lock SHA-256 computed over the 40 blind target ids in id order, **before any
  semantic inspection**: see `selection_lock.json`.
- Difficult, empty, and uninteresting cases are **not** substituted after lock.

## Benchmark cases (10)
1. cb-01 transcript-formatting one-off · 2. cb-02 pesticide assignment · 3. cb-03 mixed
study/career · 4. cb-04 AI learning roadmap · 5. cb-05 Fleet Command · 6. cb-06 Client Radar
(engagement + design chat) · 7. cb-07 CSCI 430/530 Project 3 group assignment · 8. cb-08
Personal/Family Marketing Support (campaign + KB doc + animation design chat) · 9. cb-09 Accenture
onboarding · 10. cb-10 AVATAR/BCI lab.

## Excluded selection candidates
237 conversations recorded in `excluded_selection_candidates.jsonl` (13 already processed in
4D/benchmark, 224 available but not drawn by the tier date-spread).
