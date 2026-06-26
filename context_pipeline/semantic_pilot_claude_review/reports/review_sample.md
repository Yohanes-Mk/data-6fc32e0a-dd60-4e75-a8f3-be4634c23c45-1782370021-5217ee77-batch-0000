# Review Sample — Representative Claude Blind Candidates

A curated sample illustrating how the strict project test, endorsement policy,
assistant-origin handling, and confidence calibration were applied. Each shows the
candidate's classification and the user-authored (or assistant-origin) evidence behind it.

---

## 1. A true project (all nine criteria) — `claude:cand:r_aiengineer_roadmap`
- **type:** project · **layer:** work_entity · **confidence:** high · **status:** active/current
- **endorsement:** modification (user iterated the roadmap repeatedly)
- **project_test_criteria:** all nine satisfied
- **Why it qualifies:** explicit ownership, multi-day continuing actions, decisions
  (Track-A-first), constraints (avoid rabbit-hole), research questions, an HTML deliverable
  iterated over feedback, repeated appearance, identifiable current state.
- **Evidence (user):** "the path you made is solely based on the >2 minute research… we need
  to research relevancy, market and need"; "Yes that does make sense… phase A is more
  important"; "make it an HTML and frictionless, something I could just start tomorrow".

## 2. A real assignment recovered from a `false_project` label — `claude:cand:x_pesticide_risk_assignment`
- **type:** assignment · **layer:** work_entity · **confidence:** high
- **Why not a project:** it is better described as a graded course assignment; still meets six
  strict criteria, so it is a genuine work entity (disputes the false_project selection).
- **Evidence (user):** "trying to do this with claude in excel, give me the exact steps";
  the worksheet carries a "Matriculation Number" and structured exercises E_1/E_2/E_3 with
  "Expected answer" sections.

## 3. A job application, not a project — `claude:cand:l_amazon_internship`
- **type:** job_application · **layer:** work_entity · **confidence:** high
- **Why this type:** real owned activity with a deliverable (tailored resume) but lacks the
  continuing-action/milestone density for full project status.
- **Evidence (user):** "I am going to apply to amazon internship… tailor my resume"; "software
  development engineering… sophomore 2nd semester, computer science, no previous experience".

## 4. A user-authored project decision — `claude:cand:u_decision_make_it_playable`
- **type:** decision · **layer:** project_knowledge · **confidence:** high · assistant_origin: false
- **Evidence (user):** "before moving to step 9 we need to make sure the game works… I can't
  even play it properly"; "take this as crucial need to do rather than a sprint".

## 5. An assistant recommendation kept out of the user-decision space — `claude:cand:r_decision_skip_exampro`
- **type:** decision · **status:** proposed · **assistant_origin:** TRUE · **endorsement:** implicit_continuation · **confidence:** medium · **requires_human_review:** true
- **Why handled this way:** the "skip ExamPro" call is the assistant's; the user never wrote an
  explicit yes. Recorded as a proposed/assistant-origin direction with only implicit
  continuation — not a confirmed user decision.

## 6. An assistant-inferred fact, flagged not asserted — `claude:cand:a_context_accenture_inferred`
- **type:** employer · **confidence:** low · **assistant_origin:** TRUE · **explicit_or_inferred:** inferred · **requires_human_review:** true
- **Contradiction recorded:** the assistant calls the user "a Tech Analyst candidate" with an
  internship "before July", but the user never states this. Kept low-confidence so it cannot
  enter the graph as a confirmed employer fact.

## 7. A non-knowledge one-off (false-project guard) — `claude:cand:c14_transcript_format_request`
- **type:** one_off_request · **layer:** non_knowledge · **confidence:** high
- **Evidence (user):** "I will be asking you transcripts from format this time to this time
  your job is to give it back to me as it is". The rich AI-digest-app narrative in the reply is
  third-party transcript content, recorded separately as a `transcript_fragment`.
