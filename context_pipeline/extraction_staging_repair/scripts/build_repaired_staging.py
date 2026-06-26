#!/usr/bin/env python3
"""Build Stage 3R repaired extraction staging and provenance records."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
REPAIR = ROOT / "context_pipeline" / "extraction_staging_repair"
CONFIG = json.loads((REPAIR / "config" / "provenance_repair_policy.json").read_text())
CORPUS = REPAIR / "corpus"
AUDIT = REPAIR / "audit"
REPORTS = REPAIR / "reports"
MANIFESTS = REPAIR / "manifests"

NORMALIZED = ROOT / "context_pipeline" / "normalized"
STAGE3 = ROOT / "context_pipeline" / "extraction_staging" / "corpus"

FLEET_CONV = CONFIG["confirmed_regression_conversations"]["fleet_command"]
TRACK_A_CONV = CONFIG["confirmed_regression_conversations"]["track_a_missing_research"]
TRANSCRIPT_CONV = CONFIG["confirmed_regression_conversations"]["transcript_formatting"]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def immutable_files() -> list[Path]:
    roots = [
        ROOT / "conversations.json",
        ROOT / "users.json",
        ROOT / "projects",
        ROOT / "design_chats",
        ROOT / "context_pipeline" / "normalized",
        ROOT / "context_pipeline" / "extraction_staging",
        ROOT / "context_pipeline" / "semantic_pilot",
        ROOT / "context_pipeline" / "semantic_pilot_repair",
        ROOT / "context_pipeline" / "semantic_pilot_claude_review",
    ]
    files: list[Path] = []
    for item in roots:
        if not item.exists():
            continue
        if item.is_file():
            files.append(item)
        else:
            files.extend(p for p in item.rglob("*") if p.is_file())
    return sorted(files)


def checksum_manifest() -> dict[str, dict[str, Any]]:
    return {
        rel(path): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
            "modified_time_ns": path.stat().st_mtime_ns,
        }
        for path in immutable_files()
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def write_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for row in rows:
            json.dump(row, fh, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
    os.replace(tmp, path)


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / CONFIG["token_estimate"]["characters_per_estimated_token"])


def nid(prefix: str, *parts: str) -> str:
    return f"stage3r:{prefix}:{sha256_text('|'.join(str(p) for p in parts))[:32]}"


def classify_attachment_role(filename: str | None, file_type: str | None, text: str) -> str:
    joined = f"{filename or ''} {file_type or ''} {text[:1000]}".lower()
    if "transcript" in joined:
        return "transcript_source"
    if any(term in joined for term in ["assignment", "exam", "homework", "rubric"]):
        return "assignment_material"
    if any(term in joined for term in ["gdd", "sdd", "fleet", "unity", "design document"]):
        return "project_reference"
    if any(term in joined for term in ["image", "screenshot", ".png", ".jpg", ".jpeg"]):
        return "screenshot_or_image_reference"
    return "attachment_source" if text else "unknown_attachment"


def base_assertion_for_user(text: str) -> str:
    stripped = text.strip().lower()
    if "?" in stripped:
        return "user_question"
    if re.search(r"\b(yes|that works|use that|proceed|continue|accepted|i agree)\b", stripped):
        return "user_endorsement"
    if re.search(r"\b(no|don't|do not|instead|change|actually)\b", stripped):
        return "user_modification"
    if re.search(r"\b(please|can you|create|build|fix|run|make|write|inspect|proceed)\b", stripped):
        return "user_instruction"
    return "direct_user_statement"


def line_classification(line: str, transport: str) -> tuple[str, str, str, str, bool, str]:
    lower = line.lower()
    if transport == "assistant":
        return "assistant_generated", "generated_response", "high", "transport_author_assistant", False, ""
    if transport == "document":
        return "document_content", "source_material", "high", "container_type_document", False, ""
    if transport == "attachment":
        return "attachment_content", "source_material", "high", "container_type_attachment", False, ""
    if re.search(r"^\s*(assistant|claude|chatgpt)\s*:", line, re.I):
        return "assistant_generated", "pasted_for_analysis", "high", "explicit_assistant_label", False, "assistant_label"
    if any(marker in lower for marker in ["here is what claude said", "here is what chatgpt said", "the user is asking"]):
        return "assistant_generated", "pasted_for_analysis", "medium", "assistant_framing_or_agent_summary", True, "pasted_assistant_indicator"
    if re.search(r"^\s*(tool result|console|output|error|traceback)\s*:", line, re.I) or re.search(r"^\s*(npm|python|bash|uv|jq|git)\s+", line):
        return "console_or_log_output", "execution_trace", "high", "console_or_tool_label", False, "tool_log_indicator"
    if re.search(r"^\s*(\[\d{1,2}:\d{2}|\d{1,2}:\d{2}|[A-Z][A-Za-z ]{1,32}:)\s+", line):
        return "transcript_content", "source_material", "medium", "speaker_or_timestamp_pattern", True, "transcript_indicator"
    if any(marker in lower for marker in ["transcript", "console log", "tool output", "pasted below"]):
        return "user_authored", "user_instruction", "medium", "user_framing_for_pasted_material", True, "framing_indicator"
    if transport == "user":
        return "user_authored", base_assertion_for_user(line), "high", "transport_author_user_no_external_indicator", False, ""
    return "unknown", "unknown", "low", "no_confident_origin_signal", True, "unknown_origin"


def split_segments(container: dict[str, Any]) -> list[dict[str, Any]]:
    text = container["text"]
    if text == "":
        return []
    runs = []
    pos = 0
    for match in re.finditer(r".*?(?:\n|$)", text, re.S):
        line = match.group(0)
        if line == "":
            continue
        start, end = match.start(), match.end()
        origin, assertion, conf, method, review, warning = line_classification(line, container["transport_author_role"])
        key = (origin, assertion, conf, method, review, warning)
        if runs and runs[-1]["key"] == key and runs[-1]["end"] == start:
            runs[-1]["end"] = end
        else:
            runs.append({"start": start, "end": end, "key": key})
        pos = end
    if pos < len(text):
        origin, assertion, conf, method, review, warning = line_classification(text[pos:], container["transport_author_role"])
        runs.append({"start": pos, "end": len(text), "key": (origin, assertion, conf, method, review, warning)})
    segments = []
    for idx, run in enumerate(runs):
        origin, assertion, conf, method, review, warning = run["key"]
        seg_text = text[run["start"]:run["end"]]
        warnings = [warning] if warning else []
        if len(runs) > 1:
            warnings.append("container_split_for_multiple_origin_signals")
        segments.append(
            {
                "segment_id": nid("segment", container["container_id"], str(idx), str(run["start"]), str(run["end"])),
                "parent_container_id": container["container_id"],
                "start_char_offset": run["start"],
                "end_char_offset": run["end"],
                "segment_text": seg_text,
                "segment_hash_sha256": sha256_text(seg_text),
                "transport_author_role": container["transport_author_role"],
                "content_origin": origin,
                "assertion_relationship": assertion,
                "origin_confidence": conf,
                "origin_detection_method": method,
                "detection_evidence": warnings,
                "extraction_eligibility": is_eligible_user_evidence(origin, assertion),
                "requires_origin_review": review,
                "warnings": warnings,
                "conversation_id": container.get("conversation_id"),
                "message_id": container.get("message_id"),
                "project_id": container.get("project_id"),
                "document_id": container.get("document_id"),
                "source_file": container.get("source_file"),
                "source_unit_refs": container.get("source_unit_refs", []),
            }
        )
    return segments


def is_eligible_user_evidence(origin: str, assertion: str) -> bool:
    return [origin, assertion] in CONFIG["eligible_user_evidence_pairs"]


def packetize(scope: str, unit_ids: list[str], units_by_id: dict[str, dict[str, Any]], packet_type: str, extra: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    out = []
    current: list[str] = []
    chars = 0
    max_chars = CONFIG["packet_limits"]["maximum_characters"]
    for uid in unit_ids:
        unit = units_by_id[uid]
        u_chars = unit["character_count"]
        if current and chars + u_chars > max_chars:
            out.append(make_packet(scope, packet_type, current, units_by_id, len(out), extra))
            current, chars = [], 0
        current.append(uid)
        chars += u_chars
    if current:
        out.append(make_packet(scope, packet_type, current, units_by_id, len(out), extra))
    return out


def make_packet(scope: str, packet_type: str, unit_ids: list[str], units_by_id: dict[str, dict[str, Any]], index: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    units = [units_by_id[uid] for uid in unit_ids]
    timestamps = [u.get("normalized_timestamp") for u in units if u.get("normalized_timestamp")]
    record = {
        "packet_id": f"stage3r:packet:{sha256_text(scope)[:20]}:{index:05d}",
        "packet_type": packet_type,
        "scope": scope,
        "ordered_repaired_source_unit_ids": unit_ids,
        "primary_user_evidence_unit_ids": [u["repaired_source_unit_id"] for u in units if u["extraction_eligibility"] is True],
        "supporting_unit_ids": [u["repaired_source_unit_id"] for u in units if u["extraction_eligibility"] is not True],
        "character_count": sum(u["character_count"] for u in units),
        "estimated_token_count": sum(u["estimated_token_count"] for u in units),
        "start_timestamp": min(timestamps) if timestamps else None,
        "end_timestamp": max(timestamps) if timestamps else None,
        "provenance_counts": dict(Counter(u["content_origin"] for u in units)),
        "warnings": [],
    }
    if extra:
        record.update(extra)
    return record


def main() -> None:
    for d in [CORPUS, AUDIT, REPORTS, MANIFESTS, REPAIR / "decisions"]:
        d.mkdir(parents=True, exist_ok=True)
    before = checksum_manifest()
    write_json(MANIFESTS / "checksums_before.json", before)

    messages = load_jsonl(NORMALIZED / "messages.jsonl")
    attachments = load_jsonl(NORMALIZED / "attachments.jsonl")
    docs = load_jsonl(NORMALIZED / "project_documents.jsonl")
    projects = load_jsonl(NORMALIZED / "projects.jsonl")
    design_chats = load_jsonl(NORMALIZED / "design_chats.jsonl")
    stage3_units = load_jsonl(STAGE3 / "source_units.jsonl")
    stage3_packets = load_jsonl(STAGE3 / "extraction_packets.jsonl")
    stage3_paths = load_jsonl(STAGE3 / "conversation_paths.jsonl")

    source_units_by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    source_units_by_message: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for u in stage3_units:
        if u.get("normalized_entity_id"):
            source_units_by_entity[u["normalized_entity_id"]].append(u)
        if u.get("message_id"):
            source_units_by_message[u["message_id"]].append(u)

    messages_by_id = {m["normalized_id"]: m for m in messages}
    projects_by_id = {p["normalized_id"]: p for p in projects}
    stage3_packet_by_unit: dict[str, list[str]] = defaultdict(list)
    for p in stage3_packets:
        for uid in p.get("ordered_source_unit_ids", []):
            stage3_packet_by_unit[uid].append(p["packet_id"])

    containers: list[dict[str, Any]] = []
    for m in messages:
        text = m.get("direct_text") or ""
        transport = "user" if m.get("role") in ("human", "user") else "assistant"
        containers.append(
            {
                "container_id": nid("container", m["normalized_id"]),
                "container_type": "message",
                "normalized_entity_id": m["normalized_id"],
                "conversation_id": m.get("conversation_normalized_id"),
                "message_id": m["normalized_id"],
                "project_id": None,
                "document_id": None,
                "text": text,
                "source_unit_refs": [u["source_unit_id"] for u in source_units_by_entity.get(m["normalized_id"], [])],
                "source_file": m.get("source_file"),
                "original_timestamp": m.get("original_created_at"),
                "normalized_timestamp": m.get("normalized_created_at_utc"),
                "original_provenance": m.get("semantic_provenance"),
                "transport_author_role": transport,
                "character_count": len(text),
                "content_hash_sha256": sha256_text(text),
            }
        )

    for a in attachments:
        parent = messages_by_id.get(a.get("parent_message_normalized_id"), {})
        text = a.get("extracted_content") or ""
        containers.append(
            {
                "container_id": nid("container", a["normalized_id"]),
                "container_type": "attachment",
                "normalized_entity_id": a["normalized_id"],
                "conversation_id": parent.get("conversation_normalized_id"),
                "message_id": a.get("parent_message_normalized_id"),
                "project_id": None,
                "document_id": None,
                "text": text,
                "source_unit_refs": [u["source_unit_id"] for u in source_units_by_entity.get(a["normalized_id"], [])],
                "source_file": a.get("source_file"),
                "original_timestamp": a.get("original_created_at"),
                "normalized_timestamp": a.get("normalized_created_at_utc"),
                "original_provenance": "attachment_text",
                "transport_author_role": "attachment",
                "character_count": len(text),
                "content_hash_sha256": sha256_text(text),
                "attachment_normalized_id": a["normalized_id"],
            }
        )

    for d in docs:
        text = d.get("content") or ""
        containers.append(
            {
                "container_id": nid("container", d["normalized_id"]),
                "container_type": "project_document",
                "normalized_entity_id": d["normalized_id"],
                "conversation_id": None,
                "message_id": None,
                "project_id": d.get("parent_project_normalized_id"),
                "document_id": d["normalized_id"],
                "text": text,
                "source_unit_refs": [u["source_unit_id"] for u in source_units_by_entity.get(d["normalized_id"], [])],
                "source_file": d.get("source_file"),
                "original_timestamp": d.get("original_created_at"),
                "normalized_timestamp": d.get("normalized_created_at_utc"),
                "original_provenance": "project_document",
                "transport_author_role": "document",
                "character_count": len(text),
                "content_hash_sha256": sha256_text(text),
            }
        )

    segments: list[dict[str, Any]] = []
    for c in containers:
        segments.extend(split_segments(c))

    repaired_units: list[dict[str, Any]] = []
    for s in segments:
        text = s["segment_text"]
        unit_id = nid("source_unit", s["segment_id"])
        repaired_units.append(
            {
                "repaired_source_unit_id": unit_id,
                "segment_id": s["segment_id"],
                "container_id": s["parent_container_id"],
                "normalized_entity_id": next(c["normalized_entity_id"] for c in containers if c["container_id"] == s["parent_container_id"]),
                "conversation_id": s.get("conversation_id"),
                "message_id": s.get("message_id"),
                "project_id": s.get("project_id"),
                "document_id": s.get("document_id"),
                "transport_author_role": s["transport_author_role"],
                "content_origin": s["content_origin"],
                "assertion_relationship": s["assertion_relationship"],
                "origin_confidence": s["origin_confidence"],
                "origin_detection_method": s["origin_detection_method"],
                "requires_origin_review": s["requires_origin_review"],
                "extraction_eligibility": s["extraction_eligibility"],
                "text": text,
                "character_count": len(text),
                "estimated_token_count": estimate_tokens(text),
                "content_hash_sha256": sha256_text(text),
                "source_file": s.get("source_file"),
                "source_unit_refs": s.get("source_unit_refs", []),
                "normalized_timestamp": next((c["normalized_timestamp"] for c in containers if c["container_id"] == s["parent_container_id"]), None),
                "source_offsets": {"start": s["start_char_offset"], "end": s["end_char_offset"]},
                "warnings": s.get("warnings", []),
            }
        )
    repaired_by_id = {u["repaired_source_unit_id"]: u for u in repaired_units}
    units_by_container: dict[str, list[str]] = defaultdict(list)
    for u in repaired_units:
        units_by_container[u["container_id"]].append(u["repaired_source_unit_id"])

    # Attachment links and dedicated packets.
    attachment_links = []
    missing_sources = []
    attachment_packets = []
    attachment_audit = []
    for a in attachments:
        parent = messages_by_id.get(a.get("parent_message_normalized_id"), {})
        container_id = nid("container", a["normalized_id"])
        unit_ids = units_by_container.get(container_id, [])
        role = classify_attachment_role(a.get("filename"), a.get("file_type"), a.get("extracted_content") or "")
        link_id = nid("attachment_link", a["normalized_id"])
        packet_records = packetize(link_id, unit_ids, repaired_by_id, "attachment_evidence", {"attachment_link_id": link_id}) if unit_ids else []
        attachment_packets.extend(packet_records)
        link = {
            "attachment_link_id": link_id,
            "attachment_normalized_id": a["normalized_id"],
            "parent_message_id": a.get("parent_message_normalized_id"),
            "conversation_id": parent.get("conversation_normalized_id"),
            "attachment_source_unit_ids": [u["source_unit_id"] for u in source_units_by_entity.get(a["normalized_id"], [])],
            "repaired_source_unit_ids": unit_ids,
            "extracted_text_available": bool(a.get("extracted_content")),
            "binary_present": not bool(a.get("missing_binary")),
            "missing_binary": bool(a.get("missing_binary")),
            "filename": a.get("filename"),
            "file_type": a.get("file_type"),
            "reported_size": a.get("reported_size"),
            "attachment_index": a.get("attachment_index"),
            "attachment_role": role,
            "packet_ids": [p["packet_id"] for p in packet_records],
            "warnings": [] if unit_ids else ["no_repaired_source_unit_for_attachment"],
        }
        attachment_links.append(link)
        attachment_audit.append(
            {
                "attachment_normalized_id": a["normalized_id"],
                "conversation_id": link["conversation_id"],
                "linked": bool(unit_ids),
                "extracted_text_available": link["extracted_text_available"],
                "missing_binary": link["missing_binary"],
                "attachment_role": role,
            }
        )
        if a.get("missing_binary"):
            missing_sources.append(
                {
                    "missing_source_id": nid("missing", "binary", a["normalized_id"]),
                    "conversation_id": link["conversation_id"],
                    "project_id": None,
                    "description": "Attachment binary payload is not present in the export workspace.",
                    "evidence_references": [link_id],
                    "expected_source_type": "binary_attachment_payload",
                    "impact": "Only extracted text and metadata are available.",
                    "later_user_upload_could_resolve": True,
                    "do_not_infer": True,
                }
            )

    # Project document links and dedicated packets.
    document_links = []
    doc_packets = []
    for d in docs:
        container_id = nid("container", d["normalized_id"])
        unit_ids = units_by_container.get(container_id, [])
        project = projects_by_id.get(d.get("parent_project_normalized_id"), {})
        link_id = nid("document_link", d["normalized_id"])
        packets = packetize(link_id, unit_ids, repaired_by_id, "project_document_evidence", {"document_link_id": link_id}) if unit_ids else []
        doc_packets.extend(packets)
        document_links.append(
            {
                "document_link_id": link_id,
                "project_id": d.get("parent_project_normalized_id"),
                "exported_project_uuid": d.get("project_uuid"),
                "project_name": project.get("name"),
                "document_id": d["normalized_id"],
                "document_filename": d.get("filename"),
                "created_at": d.get("normalized_created_at_utc"),
                "source_unit_ids": [u["source_unit_id"] for u in source_units_by_entity.get(d["normalized_id"], [])],
                "repaired_source_unit_ids": unit_ids,
                "packet_ids": [p["packet_id"] for p in packets],
                "verified_conversation_links": [],
                "warnings": [],
            }
        )

    # Design-chat packets for every design-chat source unit.
    design_chat_by_id = {d["normalized_id"]: d for d in design_chats}
    design_units = [u for u in repaired_units if str(u.get("conversation_id") or "").startswith("claude:design_chats:design_chat:")]
    design_packets = []
    design_audit = []
    for idx, u in enumerate(sorted(design_units, key=lambda x: x["repaired_source_unit_id"])):
        dc = design_chat_by_id.get(u["conversation_id"], {})
        packet = make_packet(
            u["repaired_source_unit_id"],
            "design_chat_evidence",
            [u["repaired_source_unit_id"]],
            repaired_by_id,
            idx,
            {
                "design_chat_id": u["conversation_id"],
                "embedded_project_uuid": dc.get("embedded_project_uuid"),
                "embedded_project_name": dc.get("embedded_project_name"),
                "embedded_project_matches_exported_project": dc.get("embedded_project_matches_exported_project"),
                "message_id": u.get("message_id"),
                "warnings": ["embedded_project_uuid_unmatched"] if dc and not dc.get("embedded_project_matches_exported_project") else [],
            },
        )
        design_packets.append(packet)
        design_audit.append(
            {
                "design_chat_id": u["conversation_id"],
                "repaired_source_unit_id": u["repaired_source_unit_id"],
                "packet_id": packet["packet_id"],
                "embedded_project_matches_exported_project": dc.get("embedded_project_matches_exported_project"),
            }
        )

    # Conversation evidence maps and repaired conversation packets.
    attachments_by_conversation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for link in attachment_links:
        if link.get("conversation_id"):
            attachments_by_conversation[link["conversation_id"]].append(link)
    paths_by_conversation: dict[str, list[str]] = defaultdict(list)
    for p in stage3_paths:
        paths_by_conversation[p.get("conversation_id")].append(p["conversation_path_id"])
    unit_ids_by_conversation: dict[str, list[str]] = defaultdict(list)
    for u in repaired_units:
        if u.get("conversation_id") and u["conversation_id"].startswith("claude:conversations:conversation:"):
            unit_ids_by_conversation[u["conversation_id"]].append(u["repaired_source_unit_id"])

    conversation_packets = []
    evidence_maps = []
    all_conversation_ids = sorted({m.get("conversation_normalized_id") for m in messages if m.get("source_export_family") == "conversations"})
    for conv_id in all_conversation_ids:
        units = [repaired_by_id[uid] for uid in unit_ids_by_conversation.get(conv_id, [])]
        eligible = [u["repaired_source_unit_id"] for u in units if u["extraction_eligibility"] is True]
        assistant_generated = [u["repaired_source_unit_id"] for u in units if u["content_origin"] == "assistant_generated"]
        pasted_assistant = [u["repaired_source_unit_id"] for u in units if u["content_origin"] == "assistant_generated" and u["transport_author_role"] == "user"]
        tool_log = [u["repaired_source_unit_id"] for u in units if u["content_origin"] in ("tool_generated", "console_or_log_output")]
        transcript = [u["repaired_source_unit_id"] for u in units if u["content_origin"] in ("transcript_content", "quoted_external_source")]
        attachment_ids = [a["attachment_link_id"] for a in attachments_by_conversation.get(conv_id, [])]
        attachment_packet_ids = [pid for a in attachments_by_conversation.get(conv_id, []) for pid in a.get("packet_ids", [])]
        packet_records = packetize(conv_id, [u["repaired_source_unit_id"] for u in units if u["transport_author_role"] in ("user", "assistant")], repaired_by_id, "conversation_evidence", {"conversation_id": conv_id})
        conversation_packets.extend(packet_records)
        evidence_maps.append(
            {
                "conversation_id": conv_id,
                "message_container_ids": [nid("container", m["normalized_id"]) for m in messages if m.get("conversation_normalized_id") == conv_id],
                "eligible_user_evidence_segment_ids": [repaired_by_id[uid]["segment_id"] for uid in eligible],
                "assistant_generated_segment_ids": [repaired_by_id[uid]["segment_id"] for uid in assistant_generated],
                "pasted_assistant_segment_ids": [repaired_by_id[uid]["segment_id"] for uid in pasted_assistant],
                "tool_log_segment_ids": [repaired_by_id[uid]["segment_id"] for uid in tool_log],
                "transcript_source_material_segment_ids": [repaired_by_id[uid]["segment_id"] for uid in transcript],
                "attachment_ids": attachment_ids,
                "attachment_packet_ids": attachment_packet_ids,
                "linked_project_documents": [],
                "design_chat_relationship": None,
                "missing_source_references": [],
                "branch_paths": sorted(paths_by_conversation.get(conv_id, [])),
                "unresolved_provenance_items": [u["repaired_source_unit_id"] for u in units if u["requires_origin_review"]],
                "conversation_packet_ids": [p["packet_id"] for p in packet_records],
            }
        )

    # Missing sources that are known from review or unresolved attachment metadata.
    missing_sources.append(
        {
            "missing_source_id": nid("missing", "track_a_deep_research", TRACK_A_CONV),
            "conversation_id": TRACK_A_CONV,
            "project_id": None,
            "description": "External Track-A deep-research results are referenced by review resolution but are absent from the current export.",
            "evidence_references": [TRACK_A_CONV],
            "expected_source_type": "external_research_results",
            "impact": "Later semantic stages must not reconstruct or infer those findings.",
            "later_user_upload_could_resolve": True,
            "do_not_infer": True,
        }
    )
    fleet_attachment_links = [a for a in attachment_links if a.get("conversation_id") == FLEET_CONV]
    if any(re.search(r"gdd|sdd", (a.get("filename") or ""), re.I) for a in fleet_attachment_links):
        missing_sources.append(
            {
                "missing_source_id": nid("missing", "fleet_gdd_sdd_payloads", FLEET_CONV),
                "conversation_id": FLEET_CONV,
                "project_id": None,
                "description": "GDD/SDD references appear in Fleet attachment metadata; binary payload availability remains unresolved.",
                "evidence_references": [a["attachment_link_id"] for a in fleet_attachment_links if re.search(r"gdd|sdd", (a.get("filename") or ""), re.I)],
                "expected_source_type": "gdd_sdd_source_file",
                "impact": "Treat professor GDD/SDD documents as source/reference documents, not user-authored artifacts.",
                "later_user_upload_could_resolve": True,
                "do_not_infer": True,
            }
        )
    for a in fleet_attachment_links:
        if a["attachment_role"] == "screenshot_or_image_reference" and a["missing_binary"]:
            missing_sources.append(
                {
                    "missing_source_id": nid("missing", "fleet_screenshot", a["attachment_link_id"]),
                    "conversation_id": FLEET_CONV,
                    "project_id": None,
                    "description": "Screenshot or image attachment payload is unavailable.",
                    "evidence_references": [a["attachment_link_id"]],
                    "expected_source_type": "screenshot_or_image",
                    "impact": "Only filename, metadata, and extracted text if any can be used.",
                    "later_user_upload_could_resolve": True,
                    "do_not_infer": True,
                }
            )

    # Add missing refs to maps.
    missing_by_conv: dict[str, list[str]] = defaultdict(list)
    for m in missing_sources:
        if m.get("conversation_id"):
            missing_by_conv[m["conversation_id"]].append(m["missing_source_id"])
    for emap in evidence_maps:
        emap["missing_source_references"] = sorted(missing_by_conv.get(emap["conversation_id"], []))

    all_packets = conversation_packets + attachment_packets + doc_packets + design_packets

    # Excluded units for empty containers and thinking safety.
    excluded = []
    for c in containers:
        if c["text"] == "":
            excluded.append(
                {
                    "excluded_unit_id": nid("excluded", c["container_id"], "empty"),
                    "container_id": c["container_id"],
                    "reason": "empty_container_text",
                    "source_file": c.get("source_file"),
                }
            )

    # Audits.
    provenance_audit = [
        {
            "defect_id": "stage3r-defect-transport-vs-origin",
            "defect": "Transport author and content origin were previously conflated.",
            "repair": "Created source containers and content segments with separate transport_author_role and content_origin fields.",
            "records_created": len(segments),
        },
        {
            "defect_id": "stage3r-defect-user-pasted-generated-content",
            "defect": "User-sent messages may include pasted assistant/tool/log/transcript content.",
            "repair": "Conservative origin detection marks pasted assistant/log/transcript segments as supporting evidence rather than direct user evidence.",
            "requires_review_segments": sum(1 for s in segments if s["requires_origin_review"]),
        },
    ]
    project_doc_audit = [
        {
            "document_id": d["document_id"],
            "project_id": d["project_id"],
            "packet_count": len(d["packet_ids"]),
            "verified_conversation_links": d["verified_conversation_links"],
            "fabricated_conversation_link": False,
        }
        for d in document_links
    ]

    # Confirmed human resolutions.
    resolutions = {
        "resolutions": [
            {"resolution_id": "hr-001", "subject": "conversation 14f3c888-fb33-40af-9039-e8cf89a97bb5", "decision": "one-off transcript-formatting request, not a project", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "later extraction must not classify as project", "unresolved_qualifiers": []},
            {"resolution_id": "hr-002", "subject": "conversation 2838a734-4192-4c0c-93b5-d72976f21da8", "decision": "academic assignment", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "classify as coursework/assignment rather than project by default", "unresolved_qualifiers": []},
            {"resolution_id": "hr-003", "subject": "conversation 94f53cfc-057a-4aa6-a827-4ec3bb332f9a", "decision": "contains multiple distinct activities, not one project", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "do not merge activities automatically", "unresolved_qualifiers": []},
            {"resolution_id": "hr-004", "subject": "2024 and 2026 conversations", "decision": "belong to the same user profile", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "profile continuity allowed", "unresolved_qualifiers": []},
            {"resolution_id": "hr-005", "subject": "ExamPro skip recommendation", "decision": "assistant-origin proposed direction, not confirmed decision", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "requires user endorsement before decision", "unresolved_qualifiers": []},
            {"resolution_id": "hr-006", "subject": "Accenture affiliation", "decision": "confirmed Technology Summer Analyst / Tech Architecture Analyst, starting June 8, 2026", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "may be used as confirmed profile fact with timestamp", "unresolved_qualifiers": []},
            {"resolution_id": "hr-007", "subject": "AI learning roadmap", "decision": "active", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "project status seed for later semantic extraction", "unresolved_qualifiers": []},
            {"resolution_id": "hr-008", "subject": "Fleet Command", "decision": "completion status unresolved", "confidence": "medium", "evidence_basis": "human review resolution", "semantic_stage_applicability": "do not infer completion", "unresolved_qualifiers": ["status unresolved"]},
            {"resolution_id": "hr-009", "subject": "Tsotsi film project", "decision": "completion status unresolved", "confidence": "medium", "evidence_basis": "human review resolution", "semantic_stage_applicability": "do not infer completion", "unresolved_qualifiers": ["status unresolved"]},
            {"resolution_id": "hr-010", "subject": "professor GDD/SDD documents", "decision": "source/reference documents, not user-authored artifacts", "confidence": "high", "evidence_basis": "human review resolution", "semantic_stage_applicability": "document provenance must remain source/reference", "unresolved_qualifiers": []},
        ],
        "project_status": {"AI learning roadmap": "active", "Fleet Command": "unresolved", "Tsotsi film project": "unresolved"},
    }

    # Reports and review samples.
    transport_counts = Counter(c["transport_author_role"] for c in containers)
    origin_counts = Counter(s["content_origin"] for s in segments)
    fleet_links = [a for a in attachment_links if a.get("conversation_id") == FLEET_CONV]
    fleet_unique_names = {a.get("filename") for a in fleet_links}
    report = [
        "# Stage 3R Repair Report",
        "",
        f"- Source containers: {len(containers)}",
        f"- Content segments: {len(segments)}",
        f"- Repaired source units: {len(repaired_units)}",
        f"- Extraction packets: {len(all_packets)}",
        f"- Attachment occurrence count: {len(attachment_links)}",
        f"- Unique attachment filename count: {len({a.get('filename') for a in attachment_links})}",
        f"- Project-document packets: {len(doc_packets)}",
        f"- Design-chat packets: {len(design_packets)}",
        f"- Missing-source references: {len(missing_sources)}",
        "",
        "## Transport Author Counts",
    ]
    for k, v in sorted(transport_counts.items()):
        report.append(f"- `{k}`: {v}")
    report.append("\n## Content Origin Counts")
    for k, v in sorted(origin_counts.items()):
        report.append(f"- `{k}`: {v}")
    report.extend(
        [
            "",
            "## Fleet Command Attachment Results",
            f"- Reported attachment occurrences: {sum(m.get('attachment_count') or 0 for m in messages if m.get('conversation_normalized_id') == FLEET_CONV)}",
            f"- Linked attachment occurrences: {len(fleet_links)}",
            f"- Extracted-text attachment occurrences: {sum(1 for a in fleet_links if a['extracted_text_available'])}",
            f"- Unresolved binary occurrences: {sum(1 for a in fleet_links if a['missing_binary'])}",
            f"- Unique attachment filenames: {len(fleet_unique_names)}",
            f"- GDD/SDD references linked: {sum(1 for a in fleet_links if re.search(r'gdd|sdd', (a.get('filename') or ''), re.I))}",
            f"- Screenshot/image references represented: {sum(1 for a in fleet_links if a['attachment_role'] == 'screenshot_or_image_reference')}",
            "",
            "## Recommendation",
            "Use `conversation_evidence_maps.jsonl` as the next semantic-pilot input boundary. It now surfaces attachment packets, design-chat packets, missing-source records, and content-origin distinctions.",
        ]
    )

    provenance_sample = []
    for label, predicate in [
        ("pure user-authored content", lambda u: u["content_origin"] == "user_authored" and u["assertion_relationship"] in ("direct_user_statement", "user_instruction", "user_question")),
        ("user framing plus pasted assistant output", lambda u: u["content_origin"] == "assistant_generated" and u["transport_author_role"] == "user"),
        ("user framing plus console/log output", lambda u: u["content_origin"] == "console_or_log_output"),
        ("transcript content", lambda u: u["content_origin"] == "transcript_content" or u.get("conversation_id") == TRANSCRIPT_CONV),
        ("assistant proposal", lambda u: u["transport_author_role"] == "assistant" and u["content_origin"] == "assistant_generated"),
        ("explicit user endorsement", lambda u: u["assertion_relationship"] == "user_endorsement"),
        ("uncertain mixed-origin content", lambda u: u["requires_origin_review"]),
    ]:
        match = next((u for u in repaired_units if predicate(u)), None)
        if match:
            provenance_sample.append(
                f"## {label}\n- Unit: `{match['repaired_source_unit_id']}`\n- Offsets: {match['source_offsets']}\n- Origin: `{match['content_origin']}` / `{match['assertion_relationship']}`\n- Confidence: `{match['origin_confidence']}`\n- Eligible: `{match['extraction_eligibility']}`\n"
            )
    attachment_sample = [
        "# Attachment Review Sample",
        "",
        f"- Fleet reported attachment occurrences: {sum(m.get('attachment_count') or 0 for m in messages if m.get('conversation_normalized_id') == FLEET_CONV)}",
        f"- Fleet linked attachment occurrences: {len(fleet_links)}",
        f"- Fleet extracted-text attachment occurrences: {sum(1 for a in fleet_links if a['extracted_text_available'])}",
        f"- Fleet unresolved binary occurrences: {sum(1 for a in fleet_links if a['missing_binary'])}",
        "",
        "## Linked Attachment Examples",
    ]
    for a in fleet_links[:5]:
        attachment_sample.append(f"- `{a['attachment_link_id']}` role `{a['attachment_role']}` packets {a['packet_ids'][:2]} missing_binary `{a['missing_binary']}`")
    if document_links:
        d = document_links[0]
        attachment_sample.append(f"\n## Project Document Example\n- `{d['document_link_id']}` project `{d['project_id']}` packets {d['packet_ids'][:2]} verified conversation links {d['verified_conversation_links']}")
    if design_packets:
        p = design_packets[0]
        attachment_sample.append(f"\n## Design Chat Packet Example\n- `{p['packet_id']}` design chat `{p.get('design_chat_id')}` embedded project match `{p.get('embedded_project_matches_exported_project')}`")
    attachment_sample.append(f"\n## GDD/SDD Linkage\n- GDD/SDD attachment filename references represented: {sum(1 for a in fleet_links if re.search(r'gdd|sdd', (a.get('filename') or ''), re.I))}")

    warnings = []
    if not any(d["verified_conversation_links"] for d in document_links):
        warnings.append({"warning_id": "stage3r-warning-0001", "type": "no_verified_project_document_conversation_links", "severity": "info", "explanation": "Project documents have dedicated packets but no fabricated conversation links.", "blocks_next_stage": False})
    if not design_packets and design_units:
        warnings.append({"warning_id": "stage3r-warning-0002", "type": "design_chat_packets_missing", "severity": "error", "explanation": "Design-chat source units exist but no design-chat packets were created.", "blocks_next_stage": True})

    # Write outputs.
    write_jsonl(CORPUS / "source_containers.jsonl", containers)
    write_jsonl(CORPUS / "content_segments.jsonl", segments)
    write_jsonl(CORPUS / "repaired_source_units.jsonl", repaired_units)
    write_jsonl(CORPUS / "attachment_links.jsonl", attachment_links)
    write_jsonl(CORPUS / "document_links.jsonl", document_links)
    write_jsonl(CORPUS / "design_chat_packets.jsonl", design_packets)
    write_jsonl(CORPUS / "extraction_packets.jsonl", all_packets)
    write_jsonl(CORPUS / "conversation_evidence_maps.jsonl", evidence_maps)
    write_jsonl(CORPUS / "missing_source_references.jsonl", missing_sources)
    write_jsonl(CORPUS / "excluded_units.jsonl", excluded)
    write_jsonl(AUDIT / "provenance_defect_audit.jsonl", provenance_audit)
    write_jsonl(AUDIT / "attachment_linkage_audit.jsonl", attachment_audit)
    write_jsonl(AUDIT / "design_chat_packet_audit.jsonl", design_audit)
    write_jsonl(AUDIT / "project_document_linkage_audit.jsonl", project_doc_audit)
    write_json(REPAIR / "decisions" / "confirmed_human_resolutions.json", resolutions)
    (REPORTS / "repair_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (REPORTS / "provenance_review_sample.md").write_text("# Provenance Review Sample\n\n" + "\n".join(provenance_sample), encoding="utf-8")
    (REPORTS / "attachment_review_sample.md").write_text("\n".join(attachment_sample) + "\n", encoding="utf-8")
    write_jsonl(REPORTS / "warnings.jsonl", warnings)
    after = checksum_manifest()
    write_json(MANIFESTS / "checksums_after.json", after)

    print(
        json.dumps(
            {
                "status": "ok",
                "source_containers": len(containers),
                "content_segments": len(segments),
                "repaired_source_units": len(repaired_units),
                "attachment_links": len(attachment_links),
                "design_chat_packets": len(design_packets),
                "project_document_packets": len(doc_packets),
                "missing_sources": len(missing_sources),
                "existing_files_changed": sum(1 for p in before if before[p]["sha256"] != after.get(p, {}).get("sha256")),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
