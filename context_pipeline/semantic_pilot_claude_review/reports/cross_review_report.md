# Phase 2 — Cross-Review: Claude Blind Extraction vs Codex Repair

Comparison performed only after the Phase-1 blind extraction was written and checksum-locked
(`manifests/blind_extraction_lock.json`).

## Headline metrics

| Metric | Claude (blind) | Codex (repair) |
|---|---|---|
| Candidate entities (knowledge layers) | 43 | 21 |
| Non-knowledge / excluded records | 4 | 22 |
| Relationships | 41 | 12 |
| `project` candidates | **2** | **6** |
| Context entities (person/org/platform/…) | 9 | **0** |
| Distinct knowledge types used | 17 | 4 (project, task, constraint, assistant_suggestion, one_off) |
| Confidence spread | high 39 / med 7 / low 1 | high 7 / med 14 / low 0 |
| Relationship types | part_of 8, associated_with 14, produces 5, informed_by 5, uses 4, created_for 3, supports 1, depends_on 1 | informed_by 6, depends_on 4, supports 2 |
| Candidates flagged for review | 4 | 14 (+12 relationships) |

### Candidate-alignment outcomes (33 aligned items)
exact_agreement 1 · conceptual_agreement 2 · title_only_disagreement 4 ·
type_disagreement 6 · evidence_disagreement 1 · boundary_disagreement 1 ·
claude_only 18 · (codex_only/false-positive 1, in `missing_from_claude.jsonl`).

There were **no exact project-for-project agreements**: the two systems agree a project
exists in b8366901 and e2fc5641, but disagree on title and on the surrounding knowledge.

## Qualitative precision / recall (no ground truth — labelled qualitative)

- **Claude recall** of project knowledge and context is **substantially higher**: it surfaces
  artifacts, decisions, milestones, blockers, research, workflows, and 9 context entities that
  Codex does not represent at all.
- **Claude precision** on the project class is higher: 2 strict projects vs Codex's 6, where
  Codex's 6 include one outright false project (14f3c888) and one over-merge (94f53cfc).
- **Codex precision on noise rejection** is reasonable (22 excluded, sensible discard reasons),
  but it pays for this with severe under-extraction of real knowledge.

## Explicit evaluation of the Codex repair (the 10 required checks)

1. **Under-extracted project knowledge? YES.** Each conversation yields a near-uniform template
   (1 project + ≤1 task + ≤1 constraint + 1 assistant_suggestion). Rich projects (Fleet Command,
   roadmap) get only 1 project + 1 assistant_suggestion — no artifacts, decisions, milestones.
2. **Missed goals/decisions/outputs/milestones/research/direction changes? YES, broadly.** None
   are represented as their specific types; at most a generic "task"/"constraint".
3. **Still created false projects? YES — one.** 14f3c888 (verbatim transcript formatting) is
   emitted as a project. It passes the mechanical ≥3-signal test only because the signals were
   read off the third-party transcript content, not the user's task. Codex flags it for review
   but still emits it.
4. **Overcorrected by discarding useful assistant artifacts? PARTIALLY.** Genuinely useful
   user-endorsed artifacts (HTML roadmap, the study prompts, slides) are not preserved as
   artifacts; assistant content is collapsed into one generic `assistant_suggestion` per
   conversation.
5. **Used `assistant_suggestion` too broadly? YES.** Exactly one per substantive conversation,
   as a catch-all for all assistant output, with truncated raw text as the description.
6. **Classified one-off interactions correctly? YES.** 244ba1ae and 248a80bc are correctly
   non-knowledge one-offs — the clearest Codex success, matching Claude.
7. **Calibrated confidence properly? PARTIALLY.** Skewed to medium (14/21), zero low-confidence,
   and the false project sits at medium rather than low. No fine discrimination.
8. **Applied endorsement correctly? CONSERVATIVELY.** Only not_applicable / no_endorsement are
   used; no explicit_acceptance is ever recorded even where the user clearly says yes (Track-A,
   Tsotsi). Safe but lossy.
9. **Sufficiently specific relationships? TYPE yes, COVERAGE no.** Types are specific
   (informed_by/depends_on/supports) but every link is project→generic-knowledge within one
   conversation; no produces/part_of of real artifacts, no cross-conversation links.
10. **Preserved enough evidence for future reconstruction? NO.** Generic titles/descriptions,
    missing context entities, and assistant/tool text mislabeled as user tasks mean the future
    DB could not faithfully reconstruct the user's projects from the Codex output alone.

**Most serious Codex finding:** the repair appears **template-driven** (one project per
conversation, action-verb→task, boilerplate descriptions, copied-opening titles) rather than the
result of genuine per-item semantic judgment. Its policy/schema are sound; its *execution*
substitutes structure for semantics.

## Codex false positives and omissions (summary)

- **False positive:** 1 project (14f3c888 transcript formatting).
- **Boundary error:** 1 over-merge (94f53cfc → one project instead of five activities).
- **Title rule violations:** all 6 project titles copy message openings.
- **Omissions:** all 9 context entities; all distinct artifacts/outputs/decisions/milestones/
  blockers/research; cross-conversation user identity; the adopted tool workflows (Bezi, Unity AI,
  Claude-in-Excel); correct per-project temporal status (all marked current).

## Explicit evaluation of Claude's own risks

- **Reading Claude-generated content too favorably / preserving the source assistant's framing?**
  Mitigated: assistant artifacts carry `assistant_origin=true` and modification/implicit
  endorsement; the ExamPro "skip" and Accenture role are flagged, not asserted. Residual risk:
  the source export is Claude's, so the assistant's helpful framing could still bias toward
  treating its suggestions as more endorsed than they are.
- **Over-merging conceptually related work?** Low: the chief correction this stage was *splitting*
  94f53cfc. The roadmap/Unity projects are kept whole deliberately.
- **Inferring user intent from assistant text?** The Accenture employer entity is exactly this and
  is therefore low-confidence + flagged.
- **Creating broad projects from weak evidence?** Avoided: only 2 projects, both meeting all 9
  criteria; weaker activities demoted to assignment/job_application/exam_preparation/initiative.
- **Failing to distinguish current vs historical?** Addressed via per-candidate temporal_status;
  this is a place where Claude diverges sharply (and, I argue, correctly) from Codex.
- **New Claude risks introduced:** (a) the `recurring_responsibility` umbrella in 94f53cfc is a
  modelling choice a human may reject; (b) cross-conversation same-user links are inferred. Both
  flagged in `human_review_queue.jsonl`.

## Material human-review questions

See `comparison/human_review_queue.jsonl` (8 items). The highest-impact ones:
1. Whether 14f3c888 should yield a project at all (Codex yes / Claude no).
2. Whether 2838a734 is a real assignment vs false project.
3. Whether 94f53cfc is one project or five.
4. Cross-conversation same-user identity resolution.
5. Whether the ExamPro skip was actually accepted by the user.
6. Whether the Accenture affiliation is real.
7. Per-project current-vs-historical status.
8. GDD/SDD as source vs artifact + the missing attachments.

## Bottom line for this stage

Codex's **policy and schema are the stronger contribution**; Codex's **extraction execution is
the weaker**. Claude's extraction is richer and more semantically faithful but introduces a few
inference/modelling choices that need human confirmation. The two are complementary.
