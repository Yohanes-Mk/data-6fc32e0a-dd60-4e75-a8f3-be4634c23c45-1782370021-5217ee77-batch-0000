# Stage 4C — Merged-Schema Semantic Pilot Report

A controlled 12-case pilot combining Codex's conservative project-admission rules, Claude's
broader work-entity / project-knowledge ontology, and Stage 3R's corrected provenance,
attachment, document, design-chat, and missing-source records. Extraction was performed by
language-model semantic judgment; scripts only loaded, resolved references, wrote, validated,
counted, and checksummed.

## 1. Selected 12 cases

Benchmark (6): mc-01 transcript one-off (14f3c888), mc-02 pesticide assignment (2838a734),
mc-03 mixed study/career (94f53cfc), mc-04 AI roadmap (b8366901), mc-05 Fleet Command (e2fc5641),
mc-06 Tsotsi film (c69f5e03).
Additional (6, deterministic): mc-07 AI Engineer Roadmap **project document** (ai-engineer-2026.md),
mc-08 **design chat** (Client Radar Accessibility Review), mc-09 **pasted-assistant** conversation
(f04cc5a5, Client Radar repo via Claude Code), mc-10 **tool/log** conversation (c2701642, SCSU
AVATAR/BCI lab), mc-11 **missing-source** conversation (85fc6dee, Fleet Command card system),
mc-12 **structural project candidate** (c9b827d9, Accenture final-round interview prep).

## 2. Candidate counts

- 48 candidates: **work_entity 13, project_knowledge 23, context_entity 10, non_project_interaction 2** (+5 excluded).
- Work-entity types: project 2, assignment 3, job_application 2, client_engagement 2, initiative 1,
  exam_preparation 1, research_effort 1, subproject 1.
- **2 projects** (AI roadmap; Fleet Command). Everything else is typed at its correct, lower granularity.

## 3. Confidence / endorsement / relationships

- Confidence: high 38, medium 10, low 0.
- Endorsement: not_applicable 28, implicit_continuation 10, modification 6, explicit_acceptance 4.
  Every explicit endorsement cites user-authored evidence; assistant proposals (ExamPro skip,
  mc-09 finding, mc-11 decision) are implicit_continuation with assistant_origin=true.
- Relationships: 39 — part_of 12, associated_with 12, uses 4, created_for 4, informed_by 3,
  supports 2, produces 2. No co-occurrence-only links.

## 4. Evidence coverage

48/48 candidates carry resolved evidence (segments/units, plus attachment/document/missing-source
ids where relevant). 47/48 rest on at least some user-origin content; the single supporting-only
candidate (mc-09 architecture finding) is explicitly assistant_origin.

## 5. Attachment deduplication (Fleet Command, mc-05)

92 occurrences → **88 unique content hashes**; filenames not populated in Stage 3R; **0 binaries
present** (all 92 are text-extracted); **no GDD/SDD binary directly present**. Occurrences do not
multiply evidence weight; image/screenshot binaries were not inspected.

## 6. Missing-source impacts

9 impact records covering 143 missing references (mostly unavailable attachment binaries plus the
mc-04 deep-research results and the mc-07 document link). All carry `do_not_infer: true`; no
findings were reconstructed.

## 7. Benchmark results

**9/9 pass** (see `validation_report.json`), honoring all confirmed human resolutions hr-001…hr-010.

## 8. Cross-case synthesis

6 clusters (Fleet Command parent-child; Client Radar same-engagement; Accenture shared-context;
user-profile continuity; AI-roadmap-doc reference-only; voice preference) and 5 possible-duplicate
records. No automatic merges; merges are recommendations flagged for review. The
`pilot_project_landscape.json` shows a small, reviewable landscape: 13 work entities, **1 active
project**, Fleet Command and Tsotsi correctly status-unresolved.

## 9. Quality defects

12 defect classes reviewed and resolved (see `semantic_quality_review.md`); 5 residual risks are
merge/link/authorship decisions carried to the human-review queue, not extraction errors.

## 10. Statuses

- **structural_validation_status: pass** (0 errors, 0 warnings).
- **semantic_quality_status: conditional_pass.**
- **checksums:** 130 tracked files unchanged; no existing file modified.

## 11. Did the pilot meet its objectives?

Yes, on all nine: it distinguished projects from one-offs; recovered project knowledge without
under-extracting; preserved context entities and sources; identified cross-entity relationships;
handled mixed-origin messages via Stage 3R provenance; used attachments/documents without
overstating availability; represented missing sources explicitly; produced descriptive titles and
justified temporal states; and produced a small reviewable landscape rather than chat fragments.

## 12. Final recommendation

**Run one more small pilot, then a larger subscription-only batch — not full-corpus yet, and not
API automation yet.**

- **Ready for another pilot:** yes — ideally a slightly larger subscription-only batch (~25–40
  cases) drawn deterministically across more conversation shapes, to test the merged schema at
  modest scale and exercise the clustering pass on more cross-case overlap.
- **Ready for a larger subscription-only batch:** yes, conditionally — after the seven
  human-review questions (esp. the merge/parent-child rules HRQ-1/HRQ-2 and the design-chat
  authorship HRQ-5) are answered, since those decisions are recurring patterns that will repeat
  at scale.
- **Full-corpus subscription extraction:** **not yet.** Two systemic issues must be addressed
  first: (a) mixed-origin "user_authored" segments that actually contain pasted assistant/tool
  content (mc-10/mc-11) need a provenance refinement upstream; (b) attachment filenames are not
  populated in Stage 3R, so dedup currently relies on hashes only.
- **Later batch API automation:** **not yet** — defer until the merged schema is stable across the
  larger subscription batch and the human-review decision rules are codified, so automation
  inherits settled conventions rather than open questions.

Structural validation passing is necessary but not sufficient; the recommendation is gated on the
semantic_quality_status (conditional_pass) and the open human-review decisions, not on structure.
