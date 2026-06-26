#!/usr/bin/env python3
"""Stage 4D self-contained structural validator (no external packages). Structural only."""
import json, os, sys
ROOT=os.path.dirname(os.path.abspath(__file__)); PIPE=os.path.dirname(ROOT)
SR=os.path.join(PIPE,"extraction_staging_repair"); PP=os.path.join(PIPE,"provenance_patch")
def L(p): return [json.loads(l) for l in open(p) if l.strip()]
def main():
    errors=[]; warnings=[]
    segs={s["segment_id"] for s in L(f"{SR}/corpus/content_segments.jsonl")}
    units={u["repaired_source_unit_id"] for u in L(f"{SR}/corpus/repaired_source_units.jsonl")}
    convs={m["conversation_id"] for m in L(f"{SR}/corpus/conversation_evidence_maps.jsonl") if m.get("conversation_id")}
    docs={d["document_id"] for d in L(f"{SR}/corpus/document_links.jsonl")}
    dcs={d["design_chat_id"] for d in L(f"{SR}/corpus/design_chat_packets.jsonl")}
    occ={a["attachment_occurrence_id"] for a in L(f"{PP}/corpus/patched_attachment_links.jsonl")}
    msids={x["missing_source_id"] for x in L(f"{SR}/corpus/missing_source_references.jsonl")}
    universe=segs|units
    cands=L(f"{ROOT}/results/candidate_entities.jsonl"); rels=L(f"{ROOT}/results/candidate_relationships.jsonl")
    ce=L(f"{ROOT}/results/case_extractions.jsonl"); ev=L(f"{ROOT}/results/candidate_evidence.jsonl")
    excl=L(f"{ROOT}/results/excluded_interactions.jsonl"); miss=L(f"{ROOT}/results/missing_source_impacts.jsonl")
    sel=L(f"{ROOT}/selection/selected_cases.jsonl"); lock=json.load(open(f"{ROOT}/selection/selection_lock.json"))
    BANNED=["quick question","perfect","yes, that is clear","mark the statement true or false","let me verify","the user wants"]
    cids=[c["candidate_id"] for c in cands]
    for i in set(cids):
        if cids.count(i)>1: errors.append(f"dup cand {i}")
    idset=set(cids)
    for c in cands:
        for s in c.get("evidence_segment_ids",[]):
            if s not in universe: errors.append(f"{c['candidate_id']}: unresolved evidence {s}")
        for a in c.get("attachment_ids",[]):
            if a not in occ: warnings.append(f"{c['candidate_id']}: attachment occ id not found {a}")
        for ms in c.get("missing_source_ids",[]):
            if ms not in msids: warnings.append(f"{c['candidate_id']}: missing-source id not found {ms}")
        if c["candidate_type"]=="project" and len(c.get("project_test_criteria") or [])<3:
            errors.append(f"{c['candidate_id']}: project <3 criteria")
        if c.get("user_endorsement") in ("explicit_acceptance","explicit_rejection","modification"):
            if c.get("assistant_origin") and c.get("content_origins")==["assistant_generated"]:
                errors.append(f"{c['candidate_id']}: explicit endorsement on assistant-only content")
        t=(c.get("canonical_title") or "").strip().lower()
        if any(t==b or t.startswith(b) for b in BANNED) or len(t)<4:
            errors.append(f"{c['candidate_id']}: banned/fragmentary title")
        if not c.get("confidence_rationale"): errors.append(f"{c['candidate_id']}: no confidence_rationale")
        if c.get("temporal_status") and "_status_unknown" not in str(c.get("temporal_status")) and not c.get("confidence_rationale"):
            errors.append(f"{c['candidate_id']}: temporal w/o rationale")
    for r in rels:
        if r["source_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad source")
        if r["target_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad target")
        if not r.get("evidence_segment_ids"): errors.append(f"rel {r['relationship_id']}: no evidence")
        for s in r.get("evidence_segment_ids",[]):
            if s not in universe: errors.append(f"rel {r['relationship_id']}: unresolved evidence")
    if len(ce)!=24: errors.append(f"case_extractions {len(ce)} != 24")
    if {c["case_id"] for c in ce}!={f"ex-{i:02d}" for i in range(1,25)}: errors.append("case_extractions not ex-01..ex-24")
    if len({s["case_id"] for s in sel})!=24: errors.append("selected_cases not 24 unique")
    for s in sel:
        if s.get("conversation_id") and s["conversation_id"] not in convs: errors.append(f"{s['case_id']} conv not in 3R")
        if s.get("document_id") and s["document_id"] not in docs: errors.append(f"{s['case_id']} doc not in 3R")
        if s.get("design_chat_id") and s["design_chat_id"] not in dcs: errors.append(f"{s['case_id']} dc not in 3R")
    # lock present
    if not lock.get("selection_lock_sha256"): errors.append("missing selection lock hash")
    if lock.get("blind_case_count")!=18: errors.append("blind lock count != 18")
    for m in miss:
        if not m.get("do_not_infer"): errors.append(f"missing impact {m.get('missing_source_impact_id')} not do_not_infer")
    for e in ev:
        if e["candidate_id"] not in idset: errors.append("candidate_evidence unknown candidate")
        if e["segment_id"] not in universe: errors.append("candidate_evidence unresolved segment")
    out={"selected_cases":len(sel),"candidates":len(cands),"relationships":len(rels),"excluded":len(excl),
         "missing_impacts":len(miss),"case_extractions":len(ce),"errors":errors,"warnings":warnings,
         "structural_validation_status":"pass" if not errors else "fail"}
    print(json.dumps(out,indent=2))
    return 0 if not errors else 1
if __name__=="__main__": sys.exit(main())
