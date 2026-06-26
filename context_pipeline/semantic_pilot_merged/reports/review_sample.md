# Stage 4C — Review Sample

A curated sample showing how the merged schema applies the strict project test, the broader
ontology, status/temporal separation, endorsement discipline, attachment dedup, and missing-source
handling. Each entry cites the candidate id and the grounding evidence.

---

## 1. Strict project (all 9 criteria) — `mc:cand:m04_ai_roadmap`
- **project · work_entity · status=active · temporal=current_confirmed (hr-007) · confidence=high**
- Criteria: all nine. Competing classifications considered: initiative, research_effort.
- Evidence (user): "problem with this plan… we need to research relevancy, market and need";
  "Yes that does make sense… phase A is more important".

## 2. Real assignment, not a project — `mc:cand:m02_pesticide_assignment`
- **assignment · work_entity · status=active · temporal=historical_status_unknown · high**
- Six project signals met, but typed `assignment` (hr-002). Competing: project, exam_preparation, course.
- Evidence: "trying to do this with claude in excel"; worksheet "Matriculation Number".

## 3. Work entity with unresolved status — `mc:cand:m05_fleet_command`
- **project · status=active · temporal=historical_status_unknown (hr-008) · requires_human_review=true**
- Not marked current/completed; completion deliberately left unresolved.
- Attachment discipline: 92 occurrences → 88 unique hashes, binaries unavailable, no GDD/SDD binary present.

## 4. Client engagement across two cases — `mc:cand:m08_client_radar_a11y` + `mc:cand:m09_client_radar_repo`
- **client_engagement** (audit/design-chat) and **client_engagement** (Claude-Code repo session),
  linked `part_of`, clustered `possible_same_project`, flagged for human merge (HRQ-1).
- Evidence: "use Accenture slide colors"; "I have claude code and vs code and the clinet radar repo".

## 5. Source vs artifact — `mc:cand:m07_roadmap_reference_doc`
- **source · context: project document** authored by a third party (Dave Ebbelaar / Datalumina),
  NOT the user's artifact. No verified conversation link (flagged HRQ-4).
- Evidence (document): "I have been working in the field of AI 10+ years… my own AI development company".

## 6. Assistant proposal, not a user decision — `mc:cand:m04_decision_skip_exampro`
- **proposed_decision · assistant_origin=true · endorsement=implicit_continuation · requires_human_review=true (hr-005)**
- Kept out of the user-decision space because no explicit user acceptance is preserved.

## 7. Confirmed employer fact — `mc:cand:m12_employer_accenture`
- **employer · status=active · temporal=current_confirmed (hr-006)** — Technology Summer Analyst,
  start 2026-06-08. Shared context with the Client Radar work but NOT merged with it (cluster `shared_context_only`).

## 8. Mixed-origin discipline — `mc:cand:m10_avatar_lab` + exclusion `mc:excl:m10_github_issue_listing`
- The lab `research_effort` rests on the genuine user description ("BCI lab at Saint Cloud University…
  CSF 400"); the pasted GitHub issue listings are excluded as `tool_execution_trace`, so they don't
  inflate the user's direct involvement. Confidence kept medium (HRQ-3).

## 9. Non-project guard — `mc:cand:m01_transcript_format_request`
- **one_off_request · non_project_interaction · high**; the AI-digest-app narrative is recorded
  separately as `transcript_fragment`. Confirms hr-001.

## 10. Subproject + cross-case cluster — `mc:cand:m11_fleet_card_system`
- **subproject** of Fleet Command (mc-05), `part_of` parent-child cluster `mc:cluster:fleet_command`,
  flagged for human confirmation (HRQ-2). Built via Codex (Feb 2026), earlier than mc-05's Apr–May work.
