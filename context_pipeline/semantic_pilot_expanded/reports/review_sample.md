# Stage 4D — Review Sample

Representative candidates showing how the expanded schema handles blind cases, provenance,
co-authorship, the null-filename policy, the separate status-current axis, and non-project guards.

## 1. Blind active marketing initiative — `ex:cand:e18_ad_campaign`
- **initiative · current_inferred · status_current_confidence=medium · confidence=high · review=true**
- A real owned $200 / 10-day Meta+LinkedIn campaign (Addis Ababa), with copy variations and budget
  decisions. Typed `initiative` (not project) — owned and continuing but lighter on milestones/artifacts.
- Evidence (user): "we're boosting only for the coming 10 days"; "we're starting with facebook".

## 2. Same engagement, later phase — `ex:cand:e19_client_radar_followup`
- **client_engagement · co_authored_flag=true · phase_relationship to ex-06 · review=true**
- The Client Radar work continued with a manager (Lauren) and a high-level summary deliverable.
  Linked `part_of` ex-06; clustered as a phase, not a new engagement. Stays separate from onboarding (3R-P).

## 3. Onboarding workflow, kept separate from the client work — `ex:cand:e22_accenture_onboarding`
- **recurring_responsibility · current_confirmed · status_current_confidence=high**
- Internship task aggregation (M365 + Granola → Todoist). Per 3R-P `do_not_merge` with Client Radar;
  linked to the Accenture employer via `shared_context_only`.

## 4. Null filenames preserved — `ex:cand:b05_fleet_command`
- **project · historical_status_unknown (hr-008) · status_current_confidence=low**
- Attachment overlay: 92 occurrences → 88 unique hashes, **0 populated filenames (preserved null,
  not invented)**, 0 binaries (text only). No GDD/SDD binary inspected.

## 5. Populated filenames used only when present — `ex:cand:e16_csci_project3_submission`
- **assignment · review=true · contradiction recorded**
- Used the 3R-P-populated filenames (Project3.pdf, the report .docx). Flagged that the report author
  ("Naomie Bambara") differs from the primary user — author identity left for human review (HRQ-3).

## 6. Assistant proposal stays a proposal — `ex:cand:b04_exampro_proposal`
- **proposed_decision · assistant_origin=true · implicit_continuation (hr-005)**
- The ExamPro skip is the assistant's proposal; not recorded as an accepted user decision.

## 7. Co-authored content, not blanket-accepted — `ex:cand:b06_client_radar`
- **client_engagement · co_authored_flag=true · mixed origin**
- The audit content is co-authored (3R-P); endorsement is `implicit_continuation`, and
  sentence-level audit authorship is left unresolved rather than treated as user fact.

## 8. Empty case recorded, not substituted — ex-07 / ex-15
- No eligible user evidence in Stage 3R → recorded in `unresolved_items.jsonl` as empty, with no
  manufactured candidate and no replacement case (Part 2 discipline).

## 9. Non-project guards — `ex:cand:e08_chord_homework`, `ex:cand:e11_python_requests_q`
- A homework solve (only assistant content; `assistant_origin=true`) and a one-off Python question —
  both `non_project_interaction`, not projects.

## 10. Separate status-current axis — `ex:cand:e21_ml_group_project`
- **assignment · historical_status_unknown · confidence=high · status_current_confidence=low**
- High confidence it's a real group assignment; low confidence about whether it's still current —
  the two axes diverge deliberately.
