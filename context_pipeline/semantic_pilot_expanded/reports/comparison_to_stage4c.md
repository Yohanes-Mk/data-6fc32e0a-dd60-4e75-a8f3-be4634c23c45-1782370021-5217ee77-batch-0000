# Stage 4D vs Stage 4C

| Dimension | Stage 4C (merged) | Stage 4D (expanded) |
|---|---|---|
| Cases | 12 (6 benchmark + 6 additional) | **24** (6 benchmark + **18 blind**, lock-hashed before inspection) |
| Evidence boundary | Stage 3R | **Stage 3R + mandatory Stage 3R-P overlay** |
| Candidate entities | 48 | 35 |
| Work entities / projects | 13 / 2 | 16 / **2** |
| Context entities | 10 | 7 |
| Confidence | high 38 / med 10 / low 0 | high 24 / med 10 / **low 1** + separate `status_current_confidence` (high 8 / med 19 / **low 8**) |
| Endorsement | conservative | conservative (4 modification, 6 modification/impl., 0 unjustified explicit) |
| Relationships | 39 | 20 |
| New schema fields | — | `status_current_confidence`, `co_authored_flag` |
| Attachment policy | occurrence-vs-unique | + **filenames preserved null (3R-P), never invented**; Fleet 92→88, 0 filenames, 0 binaries |
| Co-authorship | not modeled explicitly | **Client Radar audit `co_authored_flag=true`** (3R-P) |
| Cross-case synthesis | 6 clusters, 5 dup | 6 clusters, 4 dup, **4 profile-level knowledge records** |
| Benchmarks | 9/9 | **11/11** |
| Blind generalization | n/a (cases curated) | **18 mostly-unseen cases; no template behavior** |

## What 4D adds / tests beyond 4C

1. **Scale & blindness:** 18 deterministically-selected, mostly-unseen cases (locked before
   inspection) — the key generalization test. The framework held: correct project boundaries
   (only 2 projects), correct non-project handling (homework, one-offs, empty cases), and
   genuine per-case variation rather than a repeated template.
2. **3R-P overlay:** filename nulls preserved, co-authorship represented, AVATAR fixed to
   historical, Client Radar as one two-facet engagement — all applied.
3. **New blind work entities discovered:** a social-media ad campaign (ex-18), an Accenture
   onboarding workflow (ex-22), a group ML assignment (ex-21), a 2023 CMSC assignment (ex-20),
   a cover letter (ex-17), and the later Client Radar phase (ex-19) — none seen in 4C.
4. **Separate status-current-confidence axis** now distinguishes "sure of classification" from
   "sure it's still current," used heavily for the status-unresolved entities.
5. **Profile-level knowledge** (voice preference, Accenture employment, SCSU identity, AI-tooling
   habit) promoted only on cross-case recurrence.

## Consistency with 4C and prior resolutions

The six benchmarks reproduce their 4C/3R-P resolutions (transcript one-off; pesticide assignment;
mixed-2024 not merged; roadmap active; Fleet Command status-unresolved; Client Radar one
co-authored two-facet engagement). The candidate count is lower than 4C (35 vs 48) mainly because
8 blind cases are thin/empty/one-off and correctly yield few or no candidates — a feature, not a
regression: the pipeline did not manufacture structure where none exists.

## Net
4D demonstrates the merged+3R-P framework **generalizes** to a broader, blind sample while holding
provenance and boundary discipline. The open items are recurring **boundary/merge/identity**
decisions (not extraction errors), which is exactly what must be codified before scaling.
