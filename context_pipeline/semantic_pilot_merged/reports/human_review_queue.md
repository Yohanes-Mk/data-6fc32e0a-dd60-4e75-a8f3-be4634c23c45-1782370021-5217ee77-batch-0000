# Stage 4C — Human Review Queue

Only decisions that materially affect the future database structure. Trivial wording is excluded.

---

### HRQ-1 — Are mc-08 and mc-09 one Client Radar engagement?
- **Affected:** `mc:cand:m08_client_radar_a11y`, `mc:cand:m09_client_radar_repo` (cluster `mc:cluster:client_radar`)
- **Evidence:** Same Client Radar PPTX accessibility work; mc-08 is the audit/design-chat write-up, mc-09 the Claude-Code repo session referencing the same TypeScript files and the same accessibility Word doc.
- **Recommended default:** Merge into one `client_engagement` with two facets (audit + implementation).
- **Consequence:** Merge → one coherent engagement; keep separate → two entities that look like distinct work.
- **Confidence:** high.

### HRQ-2 — Is mc-11 a subproject of the mc-05 Fleet Command project?
- **Affected:** `mc:cand:m11_fleet_card_system`, `mc:cand:m05_fleet_command` (cluster `mc:cluster:fleet_command`)
- **Evidence:** Identical project file paths; mc-11 (Feb 2026 card system, via Codex) predates mc-05 (Apr–May 2026, via Bezi/Claude Code).
- **Recommended default:** Parent-child link; keep both candidates.
- **Consequence:** Determines whether Fleet Command is one project with phases or two separate items.
- **Confidence:** high.

### HRQ-3 — Is the AVATAR/BCI lab (mc-10) a current responsibility or historical?
- **Affected:** `mc:cand:m10_avatar_lab`
- **Evidence:** Genuine user description of the lab role, but most segments are pasted GitHub issue listings; no clear current-involvement statement.
- **Recommended default:** Keep `historical_status_unknown`; do not mark current.
- **Consequence:** Affects whether the lab appears as active work in the user's current landscape.
- **Confidence:** medium.

### HRQ-4 — Was the AI Engineer Roadmap document (mc-07) used in the roadmap conversation (mc-04)?
- **Affected:** `mc:cand:m07_roadmap_reference_doc`, `mc:cand:m04_ai_roadmap`
- **Evidence:** Shared project name "AI Engineer Roadmap"; document is third-party authored (Dave Ebbelaar); Stage 3R `verified_conversation_links` is empty.
- **Recommended default:** Keep as external source, `associated_with` only; do not assert a hard link or treat it as the project's artifact.
- **Consequence:** Avoids inventing a document→conversation join and avoids misattributing third-party content to the user.
- **Confidence:** high (on the caution); low (on any actual link).

### HRQ-5 — Who authored the mc-08 design-chat audit body?
- **Affected:** `mc:cand:m08_client_radar_a11y`
- **Evidence:** Segments labeled `content_origin=user_authored`, but the audit text reads like a formal (possibly assistant-generated/co-authored) report.
- **Recommended default:** Treat the audit body as co-authored; rely on the clearly user-authored instructions for endorsement.
- **Consequence:** Affects whether the audit findings are stored as user facts or assistant drafts.
- **Confidence:** medium.

### HRQ-6 — Model mc-12 as a job_application or as part of a broader "Accenture onboarding" entity?
- **Affected:** `mc:cand:m12_accenture_interview_prep`, `mc:cand:m12_employer_accenture`
- **Evidence:** Interview prep leads to the confirmed role (hr-006, start 2026-06-08); same employer as the client work (mc-08/09).
- **Recommended default:** Keep as a `job_application` (interview prep); link to the Accenture employer context; do NOT merge with the Client Radar engagement.
- **Consequence:** Determines whether interview prep, the confirmed role, and the client work collapse into one Accenture umbrella or stay distinct.
- **Confidence:** medium.

### HRQ-7 — Is the recurring voice/tone preference one entity across conversations?
- **Affected:** `mc:cand:m02_pref_user_tone`, `mc:cand:m06_pref_voice`
- **Evidence:** The same preference appears in mc-02 (Excel expected-answers) and mc-06 (film paper).
- **Recommended default:** Merge into one stable user preference.
- **Consequence:** One profile-level preference vs. two conversation-scoped ones.
- **Confidence:** medium.
