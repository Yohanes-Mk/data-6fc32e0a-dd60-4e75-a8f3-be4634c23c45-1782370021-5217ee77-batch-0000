#!/usr/bin/env python3
"""Self-contained structural validator for Stage 4C (no external packages).
Structural only; semantic quality is judged separately in the reports."""
import json, os, sys
ROOT=os.path.dirname(os.path.abspath(__file__))
PIPE=os.path.dirname(ROOT)
SR=os.path.join(PIPE,"extraction_staging_repair")
def L(p):
    return [json.loads(l) for l in open(p) if l.strip()]

def main():
    errors=[]; warnings=[]
    # Stage 3R reference universe
    segs=set(); units=set(); convs=set(); docs=set(); dcs=set(); msids=set()
    for s in L(os.path.join(SR,"corpus/content_segments.jsonl")): segs.add(s["segment_id"])
    for u in L(os.path.join(SR,"corpus/repaired_source_units.jsonl")): units.add(u["repaired_source_unit_id"])
    for m in L(os.path.join(SR,"corpus/conversation_evidence_maps.jsonl")):
        if m.get("conversation_id"): convs.add(m["conversation_id"])
    for d in L(os.path.join(SR,"corpus/document_links.jsonl")): docs.add(d["document_id"])
    for d in L(os.path.join(SR,"corpus/design_chat_packets.jsonl")): dcs.add(d["design_chat_id"])
    for x in L(os.path.join(SR,"corpus/missing_source_references.jsonl")): msids.add(x["missing_source_id"])
    evidence_universe=segs|units

    sel=L(os.path.join(ROOT,"selection/selected_cases.jsonl"))
    cands=L(os.path.join(ROOT,"results/candidate_entities.jsonl"))
    rels=L(os.path.join(ROOT,"results/candidate_relationships.jsonl"))
    excl=L(os.path.join(ROOT,"results/excluded_interactions.jsonl"))
    miss=L(os.path.join(ROOT,"results/missing_source_impacts.jsonl"))
    ce=L(os.path.join(ROOT,"results/case_extractions.jsonl"))
    ev=L(os.path.join(ROOT,"results/candidate_evidence.jsonl"))

    # 1 parse already done by load. 2 unique ids
    cids=[c["candidate_id"] for c in cands]
    for i in set(cids):
        if cids.count(i)>1: errors.append(f"dup candidate_id {i}")
    rids=[r["relationship_id"] for r in rels]
    for i in set(rids):
        if rids.count(i)>1: errors.append(f"dup relationship_id {i}")
    idset=set(cids)

    BANNED=["quick question","perfect","yes, that is clear","mark the statement true or false","let me verify","the user wants"]
    PROJECT_MIN=3
    for c in cands:
        # 3 evidence refs resolve
        for s in c.get("evidence_segment_ids",[]):
            if s not in evidence_universe: errors.append(f"{c['candidate_id']}: unresolved evidence {s}")
        for d in c.get("document_ids",[]):
            if d not in docs: warnings.append(f"{c['candidate_id']}: document id not in document_links ({d})")
        for ms in c.get("missing_source_ids",[]):
            if ms not in msids and not ms.startswith("stage3r:document"): warnings.append(f"{c['candidate_id']}: missing_source id unresolved {ms}")
        # 6 project test
        if c["candidate_type"]=="project":
            if len(c.get("project_test_criteria") or [])<PROJECT_MIN:
                errors.append(f"{c['candidate_id']}: project lacks >=3 project_test_criteria")
        # 9 explicit endorsement needs user evidence (not assistant-only)
        if c.get("user_endorsement") in ("explicit_acceptance","explicit_rejection","modification"):
            if c.get("assistant_origin") and c.get("content_origins")==["assistant_generated"]:
                errors.append(f"{c['candidate_id']}: explicit endorsement on assistant-only content")
        # 7/8 pasted assistant / tool-log not direct user evidence: any candidate whose content_origins is purely pasted/tool and explicit_or_inferred=explicit user fact
        co=set(c.get("content_origins") or [])
        if c["knowledge_layer"] in ("work_entity","project_knowledge") and co and co.issubset({"pasted_assistant","tool_log","tool_output"}) and not c.get("assistant_origin"):
            warnings.append(f"{c['candidate_id']}: built only on pasted/tool content but not flagged assistant_origin")
        # 14 titles descriptive
        t=(c.get("canonical_title") or "").strip().lower()
        if any(t==b or t.startswith(b) for b in BANNED) or len(t)<4:
            errors.append(f"{c['candidate_id']}: banned/fragmentary title {c.get('canonical_title')!r}")
        # 15 temporal justified (rationale present)
        if not c.get("confidence_rationale"): errors.append(f"{c['candidate_id']}: missing confidence_rationale")
        # related/competing sanity
    # relationships: 13 evidence present
    for r in rels:
        if r["source_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad source")
        if r["target_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad target")
        if not r.get("evidence_segment_ids"): errors.append(f"rel {r['relationship_id']}: no evidence")
        for s in r.get("evidence_segment_ids",[]):
            if s not in evidence_universe: errors.append(f"rel {r['relationship_id']}: unresolved evidence {s}")
    # 4 all 12 cases processed
    if len(ce)!=12: errors.append(f"case_extractions has {len(ce)} not 12")
    case_ids={c["case_id"] for c in ce}
    if case_ids!={f"mc-{i:02d}" for i in range(1,13)}: errors.append("case_extractions do not cover mc-01..mc-12")
    # selection has 12 unique cases that resolve
    selids=[s["case_id"] for s in sel]
    if len(set(selids))!=12: errors.append("selected_cases not 12 unique")
    for s in sel:
        tgt=s.get("conversation_id") or s.get("document_id") or s.get("design_chat_id")
        if s.get("conversation_id") and s["conversation_id"] not in convs: errors.append(f"{s['case_id']}: conversation not in 3R")
        if s.get("document_id") and s["document_id"] not in docs: errors.append(f"{s['case_id']}: document not in 3R")
        if s.get("design_chat_id") and s["design_chat_id"] not in dcs: errors.append(f"{s['case_id']}: design_chat not in 3R")
    # 10 attachment dedup discipline: candidates referencing attachments should have occurrence!=unique recorded in bundle (checked in report). here ensure missing impacts have do_not_infer
    for m in miss:
        if not m.get("do_not_infer"): errors.append(f"missing impact {m.get('missing_source_impact_id')} not do_not_infer")
    # 11 unavailable binaries not inspected: no candidate description claims 'screenshot shows' etc with missing binaries — heuristic check
    for c in cands:
        d=(c.get("description") or "").lower()
        if ("the screenshot shows" in d or "as seen in the image" in d) and c.get("missing_source_ids"):
            warnings.append(f"{c['candidate_id']}: description may claim inspection of unavailable binary")

    # candidate_evidence integrity
    for e in ev:
        if e["candidate_id"] not in idset: errors.append(f"candidate_evidence references unknown candidate {e['candidate_id']}")
        if e["segment_id"] not in evidence_universe: errors.append(f"candidate_evidence unresolved segment {e['segment_id']}")

    out={
      "selected_cases":len(sel),"candidates":len(cands),"relationships":len(rels),
      "excluded":len(excl),"missing_impacts":len(miss),"case_extractions":len(ce),
      "errors":errors,"warnings":warnings,
      "structural_validation_status":"pass" if not errors else "fail",
    }
    print(json.dumps(out,indent=2))
    return 0 if not errors else 1

if __name__=="__main__":
    sys.exit(main())
