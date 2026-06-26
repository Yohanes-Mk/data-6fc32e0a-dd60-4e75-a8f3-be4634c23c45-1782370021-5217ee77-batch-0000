#!/usr/bin/env python3
"""Validate Stage 3R repaired extraction staging outputs."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REPAIR = ROOT / "context_pipeline" / "extraction_staging_repair"
CORPUS = REPAIR / "corpus"
AUDIT = REPAIR / "audit"
REPORTS = REPAIR / "reports"
MANIFESTS = REPAIR / "manifests"
CONFIG = json.loads((REPAIR / "config" / "provenance_repair_policy.json").read_text())
FLEET_CONV = CONFIG["confirmed_regression_conversations"]["fleet_command"]
TRACK_A_CONV = CONFIG["confirmed_regression_conversations"]["track_a_missing_research"]
TRANSCRIPT_CONV = CONFIG["confirmed_regression_conversations"]["transcript_formatting"]


JSONL_FILES = {
    "source_containers": CORPUS / "source_containers.jsonl",
    "content_segments": CORPUS / "content_segments.jsonl",
    "repaired_source_units": CORPUS / "repaired_source_units.jsonl",
    "attachment_links": CORPUS / "attachment_links.jsonl",
    "document_links": CORPUS / "document_links.jsonl",
    "design_chat_packets": CORPUS / "design_chat_packets.jsonl",
    "extraction_packets": CORPUS / "extraction_packets.jsonl",
    "conversation_evidence_maps": CORPUS / "conversation_evidence_maps.jsonl",
    "missing_source_references": CORPUS / "missing_source_references.jsonl",
    "excluded_units": CORPUS / "excluded_units.jsonl",
    "provenance_defect_audit": AUDIT / "provenance_defect_audit.jsonl",
    "attachment_linkage_audit": AUDIT / "attachment_linkage_audit.jsonl",
    "design_chat_packet_audit": AUDIT / "design_chat_packet_audit.jsonl",
    "project_document_linkage_audit": AUDIT / "project_document_linkage_audit.jsonl",
    "warnings": REPORTS / "warnings.jsonl",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows, errors = [], []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append({"file": str(path), "line": line_no, "error": str(exc)})
    return rows, errors


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check(name: str, passed: bool, details: Any = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def main() -> None:
    records: dict[str, list[dict[str, Any]]] = {}
    parse_errors = []
    for name, path in JSONL_FILES.items():
        parsed, errors = load_jsonl(path)
        records[name] = parsed
        parse_errors.extend(errors)

    checks = [check("all_jsonl_parses", not parse_errors, parse_errors)]

    id_fields = {
        "source_containers": "container_id",
        "content_segments": "segment_id",
        "repaired_source_units": "repaired_source_unit_id",
        "attachment_links": "attachment_link_id",
        "document_links": "document_link_id",
        "design_chat_packets": "packet_id",
        "extraction_packets": "packet_id",
        "conversation_evidence_maps": "conversation_id",
        "missing_source_references": "missing_source_id",
        "excluded_units": "excluded_unit_id",
    }
    duplicate_ids = {}
    for name, field in id_fields.items():
        ids = [r.get(field) for r in records[name]]
        dupes = [item for item, count in Counter(ids).items() if item and count > 1]
        if dupes:
            duplicate_ids[name] = dupes[:50]
    checks.append(check("all_ids_unique", not duplicate_ids, duplicate_ids))

    containers = {r["container_id"]: r for r in records["source_containers"]}
    segments_by_container: dict[str, list[dict[str, Any]]] = {}
    for seg in records["content_segments"]:
        segments_by_container.setdefault(seg["parent_container_id"], []).append(seg)
    unresolved_parent_segments = [s["segment_id"] for s in records["content_segments"] if s["parent_container_id"] not in containers]
    checks.append(check("all_segment_parent_references_resolve", not unresolved_parent_segments, unresolved_parent_segments[:50]))

    offset_errors = []
    coverage_errors = []
    for cid, container in containers.items():
        segs = sorted(segments_by_container.get(cid, []), key=lambda s: s["start_char_offset"])
        last = 0
        for seg in segs:
            if seg["start_char_offset"] < 0 or seg["end_char_offset"] > container["character_count"] or seg["start_char_offset"] >= seg["end_char_offset"]:
                offset_errors.append(seg["segment_id"])
            if seg["start_char_offset"] != last:
                coverage_errors.append({"container_id": cid, "expected_start": last, "actual_start": seg["start_char_offset"]})
            last = seg["end_char_offset"]
        if container["character_count"] and last != container["character_count"]:
            coverage_errors.append({"container_id": cid, "expected_end": container["character_count"], "actual_end": last})
    checks.append(check("segment_offsets_are_valid", not offset_errors, offset_errors[:50]))
    checks.append(check("retained_segments_cover_container_text_without_gaps_or_overlaps", not coverage_errors, coverage_errors[:50]))

    field_errors = [
        r["repaired_source_unit_id"]
        for r in records["repaired_source_units"]
        if not all(k in r for k in ("transport_author_role", "content_origin", "assertion_relationship"))
    ]
    checks.append(check("transport_author_and_content_origin_are_separate_fields", not field_errors, field_errors[:50]))

    bad_pasted = [
        r["repaired_source_unit_id"]
        for r in records["repaired_source_units"]
        if r["transport_author_role"] == "user" and r["content_origin"] == "assistant_generated" and r["extraction_eligibility"] is True
    ]
    checks.append(check("pasted_assistant_content_not_direct_user_evidence", not bad_pasted, bad_pasted[:50]))

    bad_logs = [
        r["repaired_source_unit_id"]
        for r in records["repaired_source_units"]
        if r["content_origin"] in ("tool_generated", "console_or_log_output") and r["extraction_eligibility"] is True
    ]
    checks.append(check("tool_or_log_output_not_direct_user_evidence", not bad_logs, bad_logs[:50]))

    bad_eligible = [
        r["repaired_source_unit_id"]
        for r in records["repaired_source_units"]
        if r["extraction_eligibility"] is True and [r["content_origin"], r["assertion_relationship"]] not in CONFIG["eligible_user_evidence_pairs"]
    ]
    checks.append(check("eligible_user_evidence_has_valid_user_authored_origin", not bad_eligible, bad_eligible[:50]))

    attachment_links = records["attachment_links"]
    normalized_messages, _ = load_jsonl(ROOT / "context_pipeline" / "normalized" / "messages.jsonl")
    normalized_attachment_count = sum(1 for _ in open(ROOT / "context_pipeline" / "normalized" / "attachments.jsonl", encoding="utf-8"))
    checks.append(check("every_attachment_occurrence_has_link", len(attachment_links) == normalized_attachment_count, {"links": len(attachment_links), "normalized": normalized_attachment_count}))

    fleet_links = [a for a in attachment_links if a.get("conversation_id") == FLEET_CONV]
    fleet_map = next((m for m in records["conversation_evidence_maps"] if m["conversation_id"] == FLEET_CONV), None)
    checks.append(check("attachment_heavy_conversation_surfaces_attachments", bool(fleet_map and fleet_map["attachment_ids"] and len(fleet_links) == len(fleet_map["attachment_ids"])), {"fleet_links": len(fleet_links), "map_attachment_ids": len(fleet_map["attachment_ids"]) if fleet_map else 0}))

    doc_links = records["document_links"]
    project_doc_packets = [p for p in records["extraction_packets"] if p.get("packet_type") == "project_document_evidence"]
    checks.append(check("project_documents_have_dedicated_packets", bool(doc_links) and all(d.get("packet_ids") for d in doc_links), {"document_links": len(doc_links), "project_document_packets": len(project_doc_packets)}))

    fabricated_links = [d["document_link_id"] for d in doc_links if d.get("verified_conversation_links")]
    checks.append(check("no_unverified_conversation_document_link_fabricated", not fabricated_links, fabricated_links))

    design_source_units = [r for r in records["repaired_source_units"] if str(r.get("conversation_id", "")).startswith("claude:design_chats:design_chat:")]
    checks.append(check("all_design_chats_have_packets", bool(records["design_chat_packets"]) and len(records["design_chat_packets"]) == len(design_source_units), {"design_source_units": len(design_source_units), "design_chat_packets": len(records["design_chat_packets"])}))

    missing = records["missing_source_references"]
    track_a = [m for m in missing if m.get("conversation_id") == TRACK_A_CONV and m.get("expected_source_type") == "external_research_results"]
    unresolved_binaries = [m for m in missing if m.get("expected_source_type") == "binary_attachment_payload"]
    checks.append(check("missing_sources_are_explicitly_represented", bool(track_a) and bool(unresolved_binaries), {"track_a": len(track_a), "unresolved_binaries": len(unresolved_binaries)}))

    thinking = [r["repaired_source_unit_id"] for r in records["repaired_source_units"] if r.get("content_origin") == "model_internal_reasoning_excluded" or "thinking" in " ".join(r.get("warnings", [])).lower()]
    checks.append(check("no_thinking_content_enters_repaired_staging", not thinking, thinking[:50]))

    before = load_json(MANIFESTS / "checksums_before.json")
    after = load_json(MANIFESTS / "checksums_after.json")
    changed = [path for path in before if before[path]["sha256"] != after.get(path, {}).get("sha256")]
    checks.append(check("previous_files_remain_unchanged", not changed, changed[:50]))

    # Targeted regression tests.
    regressions = []
    def reg(name: str, passed: bool, details: Any = None) -> None:
        regressions.append({"name": name, "passed": bool(passed), "details": details})

    reg("user_framing_plus_pasted_assistant_output", any(r["transport_author_role"] == "user" and r["content_origin"] == "assistant_generated" and r["extraction_eligibility"] is not True for r in records["repaired_source_units"]))
    reg("unity_or_terminal_logs_not_user_evidence", not bad_logs)
    transcript_map = next((m for m in records["conversation_evidence_maps"] if m["conversation_id"] == TRANSCRIPT_CONV), None)
    reg("transcript_formatting_request_not_user_project", bool(transcript_map and transcript_map["transcript_source_material_segment_ids"] or transcript_map))
    reg("fleet_attachment_heavy_conversation", bool(fleet_links and fleet_map and fleet_map["attachment_packet_ids"]))
    reg("project_document_without_verified_conversation_link", bool(doc_links) and not fabricated_links)
    reg("design_chat_packet", bool(records["design_chat_packets"]))
    reg("pure_user_authored_message", any(r["content_origin"] == "user_authored" and r["extraction_eligibility"] is True for r in records["repaired_source_units"]))
    reg("assistant_proposal_later_explicitly_accepted", any(r["assertion_relationship"] == "user_endorsement" for r in records["repaired_source_units"]))
    reg("assistant_proposal_without_user_endorsement", any(r["transport_author_role"] == "assistant" and r["extraction_eligibility"] is not True for r in records["repaired_source_units"]))
    reg("missing_external_research_source", bool(track_a))
    checks.append(check("targeted_regression_tests_pass", all(r["passed"] for r in regressions), regressions))

    packet_hashes = {p["packet_id"]: hashlib.sha256(json.dumps(p, sort_keys=True).encode("utf-8")).hexdigest() for p in records["extraction_packets"]}
    provenance_quality_status = "pass" if all(c["passed"] for c in checks) else "fail"
    status = "pass" if all(c["passed"] for c in checks) else "fail"
    counts = {
        "source_containers": len(records["source_containers"]),
        "content_segments": len(records["content_segments"]),
        "repaired_source_units": len(records["repaired_source_units"]),
        "transport_author_counts": dict(Counter(r["transport_author_role"] for r in records["source_containers"])),
        "content_origin_counts": dict(Counter(r["content_origin"] for r in records["content_segments"])),
        "eligible_direct_user_evidence_count": sum(1 for r in records["repaired_source_units"] if r["extraction_eligibility"] is True),
        "pasted_assistant_segments": sum(1 for r in records["repaired_source_units"] if r["transport_author_role"] == "user" and r["content_origin"] == "assistant_generated"),
        "tool_log_segments": sum(1 for r in records["repaired_source_units"] if r["content_origin"] in ("tool_generated", "console_or_log_output")),
        "attachment_occurrences": len(attachment_links),
        "unique_attachment_filenames": len({a.get("filename") for a in attachment_links}),
        "linked_attachment_count": len([a for a in attachment_links if a.get("repaired_source_unit_ids")]),
        "unresolved_attachment_binary_count": len([a for a in attachment_links if a.get("missing_binary")]),
        "fleet": {
            "reported_attachment_count": sum(m.get("attachment_count") or 0 for m in normalized_messages if m.get("conversation_normalized_id") == FLEET_CONV),
            "linked_attachment_count": len(fleet_links),
            "extracted_text_attachment_count": sum(1 for a in fleet_links if a.get("extracted_text_available")),
            "unresolved_binary_count": sum(1 for a in fleet_links if a.get("missing_binary")),
            "gdd_sdd_reference_count": sum(1 for a in fleet_links if __import__("re").search(r"gdd|sdd", (a.get("filename") or ""), __import__("re").I)),
            "screenshot_or_image_reference_count": sum(1 for a in fleet_links if a.get("attachment_role") == "screenshot_or_image_reference"),
        },
        "project_document_packet_count": len(project_doc_packets),
        "design_chat_packet_count": len(records["design_chat_packets"]),
        "missing_source_count": len(missing),
    }

    report = {
        "status": status,
        "provenance_quality_status": provenance_quality_status,
        "checks": checks,
        "targeted_regression_tests": regressions,
        "counts": counts,
        "checksum_status": {"changed_existing_files": changed, "passed": not changed},
        "determinism": {"packet_hash_count": len(packet_hashes), "packet_hash_sample": dict(list(sorted(packet_hashes.items()))[:10])},
        "blocking_issues": [c["name"] for c in checks if not c["passed"]],
    }
    out = REPORTS / "validation_report.json"
    tmp = out.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, out)
    print(json.dumps({"status": status, "provenance_quality_status": provenance_quality_status, "blocking_issues": report["blocking_issues"]}, sort_keys=True))


if __name__ == "__main__":
    main()
