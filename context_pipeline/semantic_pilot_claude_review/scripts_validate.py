#!/usr/bin/env python3
"""Self-contained structural validator for the Claude cross-review outputs.
No external packages. Validates JSONL parse, schema basics, id uniqueness,
evidence resolution, and relationship integrity. Semantic judgement is NOT done here."""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(ROOT)
BUNDLES = os.path.join(PIPE, "semantic_pilot_repair/context_bundles/conversation_context_bundles.jsonl")
BE = os.path.join(ROOT, "blind_extraction")
CMP = os.path.join(ROOT, "comparison")

REQUIRED = ["claude_candidate_id","conversation_id","candidate_type","canonical_title",
  "description","why_it_matters","knowledge_layer","temporal_status","status","confidence",
  "confidence_rationale","explicit_or_inferred","semantic_provenance","assistant_origin",
  "user_endorsement","evidence_source_unit_ids","evidence_message_ids","related_candidate_ids",
  "uncertainties","contradictions","requires_human_review","inclusion_rationale"]
CONF={"high","medium","low"}
LAYERS={"work_entity","project_knowledge","context_entity","non_knowledge"}
ENDORSE={"explicit_acceptance","explicit_rejection","modification","implicit_continuation",
  "no_endorsement","unclear","not_applicable"}

def load(p):
    rows=[]
    for i,l in enumerate(open(p)):
        l=l.strip()
        if not l: continue
        rows.append(json.loads(l))  # raises on bad json
    return rows

def main():
    errors=[]; warnings=[]
    # valid source units
    valid_su=set(); valid_conv=set()
    for l in open(BUNDLES):
        b=json.loads(l); valid_conv.add(b["conversation_id"])
        for g in ("user_authored_source_units","connected_assistant_source_units","acceptance_rejection_or_modification_units"):
            for u in b.get(g,[]): valid_su.add(u["source_unit_id"])

    ent=load(os.path.join(BE,"candidate_entities.jsonl"))
    exc=load(os.path.join(BE,"excluded_content.jsonl"))
    allc=ent+exc
    ids=[c["claude_candidate_id"] for c in allc]
    for i in set(ids):
        if ids.count(i)>1: errors.append(f"dup candidate id {i}")
    idset=set(ids)
    PROJECT_CRIT_MIN=3
    for c in allc:
        for f in REQUIRED:
            if f not in c: errors.append(f"{c.get('claude_candidate_id')}: missing {f}")
        if c.get("confidence") not in CONF: errors.append(f"{c['claude_candidate_id']}: bad confidence")
        if c.get("knowledge_layer") not in LAYERS: errors.append(f"{c['claude_candidate_id']}: bad layer")
        if c.get("user_endorsement") not in ENDORSE: errors.append(f"{c['claude_candidate_id']}: bad endorsement")
        if c.get("conversation_id") not in valid_conv: errors.append(f"{c['claude_candidate_id']}: unknown conversation")
        for s in c.get("evidence_source_unit_ids",[]):
            if s not in valid_su: errors.append(f"{c['claude_candidate_id']}: unresolved source unit {s}")
        if c.get("evidence_source_unit_ids") and not c.get("evidence_message_ids"):
            errors.append(f"{c['claude_candidate_id']}: has source units but no message ids")
        # project test documented for any project candidate
        if c.get("candidate_type")=="project":
            crit=c.get("project_test_criteria") or []
            if len(crit)<PROJECT_CRIT_MIN:
                errors.append(f"{c['claude_candidate_id']}: project lacks >=3 project_test_criteria")
        # explicit endorsement requires user-authored evidence
        if c.get("user_endorsement") in ("explicit_acceptance","explicit_rejection","modification"):
            if c.get("assistant_origin") and c.get("semantic_provenance")=="assistant_output":
                warnings.append(f"{c['claude_candidate_id']}: explicit endorsement on assistant-origin candidate (check user evidence)")
        # assistant-only content not a confirmed user fact
        if c.get("assistant_origin") and c.get("candidate_type") in ("project","decision","preference") and c.get("explicit_or_inferred")=="explicit" and c.get("semantic_provenance")=="assistant_output":
            warnings.append(f"{c['claude_candidate_id']}: assistant-origin treated as explicit user fact?")
        # generic tool ops should not be platform/workflow without justification (heuristic warn only)
        for rc in c.get("related_candidate_ids",[]):
            if rc not in idset: warnings.append(f"{c['claude_candidate_id']}: related id {rc} not found (forward link)")

    # relationships
    rels=load(os.path.join(BE,"candidate_relationships.jsonl"))
    rids=[r["relationship_id"] for r in rels]
    for i in set(rids):
        if rids.count(i)>1: errors.append(f"dup relationship id {i}")
    for r in rels:
        if r["source_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad source")
        if r["target_candidate_id"] not in idset: errors.append(f"rel {r['relationship_id']}: bad target")
        if not r.get("evidence_source_unit_ids"): errors.append(f"rel {r['relationship_id']}: no evidence")
        if r.get("confidence") not in CONF: errors.append(f"rel {r['relationship_id']}: bad confidence")

    # conversation completeness: all 8 processed
    ce=load(os.path.join(BE,"conversation_extractions.jsonl"))
    if len(ce)!=8: errors.append(f"conversation_extractions has {len(ce)} not 8")
    covered={c["conversation_id"] for c in ce}
    if covered!=valid_conv: errors.append("conversation_extractions do not cover all 8 selected conversations")

    # comparison files (optional in phase1, required after phase2)
    cmp_status={}
    for fn in ["candidate_alignment.jsonl","relationship_alignment.jsonl","missing_from_codex.jsonl",
               "missing_from_claude.jsonl","disputed_classifications.jsonl","human_review_queue.jsonl"]:
        p=os.path.join(CMP,fn)
        if os.path.exists(p):
            try: cmp_status[fn]=len(load(p))
            except Exception as e: errors.append(f"{fn}: parse error {e}")
    print(json.dumps({
        "candidate_entities": len(ent),
        "excluded_content": len(exc),
        "relationships": len(rels),
        "conversation_extractions": len(ce),
        "comparison_files": cmp_status,
        "errors": errors,
        "warnings": warnings,
        "structural_validation_status": "pass" if not errors else "fail",
    }, indent=2))
    return 0 if not errors else 1

if __name__=="__main__":
    sys.exit(main())
