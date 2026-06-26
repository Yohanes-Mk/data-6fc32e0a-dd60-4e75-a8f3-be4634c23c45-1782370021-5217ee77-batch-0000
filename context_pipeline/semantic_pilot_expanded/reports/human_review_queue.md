# Stage 4D — Human Review Queue

Only decisions that materially affect entity boundaries, merges, current status, accepted
proposals, source-vs-artifact, ownership, or profile promotion.

### HRQ-1 — Merge ex-06 and ex-19 as one Client Radar engagement with phases?
- **Affected:** `ex:cand:b06_client_radar`, `ex:cand:e19_client_radar_followup`
- **Evidence:** Same engagement one day apart (June 23/24, 2026); ex-19 adds the manager (Lauren) and the high-level summary deliverable.
- **Recommended default:** Merge as one engagement with an audit/design phase, a repo-implementation phase, and a manager-summary phase.
- **Consequence:** One coherent engagement vs. two entities. Per 3R-P this engagement stays separate from interview prep/onboarding.
- **Confidence:** high.

### HRQ-2 — Keep Accenture activities separate under a shared employer?
- **Affected:** `ex:cand:b06_client_radar`, `ex:cand:e22_accenture_onboarding`, `ex:cand:e09_internship_summary_request`, `ex:cand:b06_employer_accenture`
- **Evidence:** All reference the Accenture internship (hr-006); 3R-P says do-not-merge Client Radar with interview prep/onboarding.
- **Recommended default:** One Accenture employer entity; keep client engagement, onboarding workflow, and summary task as distinct activities linked to it.
- **Consequence:** Prevents collapsing distinct work into one "Accenture" blob.
- **Confidence:** high.

### HRQ-3 — Whose work is ex-16 (CSCI 430-530 Project 3)?
- **Affected:** `ex:cand:e16_csci_project3_submission`
- **Evidence:** Attached files name "Naomie Bambara"; the primary user is Yohannes Nigusse.
- **Recommended default:** Do not assign to the primary user's profile until confirmed (peer help, group work, or different user).
- **Consequence:** Affects profile/ownership attribution and whether this assignment enters the user's landscape.
- **Confidence:** medium.

### HRQ-4 — Is there one marketing effort across ex-18 / ex-23 / ex-24?
- **Affected:** `ex:cand:e18_ad_campaign`, `ex:cand:e23_marketing_kb_doc`, `ex:cand:e24_animation_request`
- **Evidence:** A paid social campaign, a marketing knowledge-base document, and a trending-animation request — plausibly one effort, no verified links.
- **Recommended default:** Keep separate (insufficient_evidence); link as inferred associations only.
- **Consequence:** Avoids inventing a marketing project from unlinked pieces.
- **Confidence:** low.

### HRQ-5 — Is the ex-23 marketing knowledge base a source or a user artifact?
- **Affected:** `ex:cand:e23_marketing_kb_doc`
- **Evidence:** A saved HTML knowledge base under "AD Campigns"; authorship and any conversation link are unverified.
- **Recommended default:** Treat as a source until a verified link/authorship proves otherwise.
- **Consequence:** Source-vs-artifact classification and campaign linkage.
- **Confidence:** medium.

### HRQ-6 — Promote the voice/tone preference to profile level?
- **Affected:** `ex:cand:e17_pref_voice` → `ex:profile:voice_tone_pref`
- **Evidence:** Recurs in ex-02 (expected answers), the Client Radar/film-era writing, and ex-17 (cover letter).
- **Recommended default:** Promote to one profile-level preference (per 3R-P guidance).
- **Consequence:** One durable preference vs. repeated per-case ones.
- **Confidence:** medium.

### HRQ-7 — Confirm current status of the active non-project work
- **Affected:** `ex:cand:e18_ad_campaign`, `ex:cand:e22_accenture_onboarding`, `ex:cand:e19_client_radar_followup`
- **Evidence:** All inferred current from June-2026 activity; no explicit "still ongoing" confirmation.
- **Recommended default:** Keep `current_inferred`/`current_confirmed` with `status_current_confidence` medium; confirm before treating as definitely live.
- **Consequence:** Accuracy of "what is the user doing now".
- **Confidence:** medium.
