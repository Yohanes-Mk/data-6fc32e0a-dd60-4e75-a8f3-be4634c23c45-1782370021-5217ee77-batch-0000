#!/usr/bin/env python3
"""Validate Stage 3 extraction staging outputs."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
STAGING = ROOT / "context_pipeline" / "extraction_staging"
NORMALIZED = ROOT / "context_pipeline" / "normalized"
POLICY_PATH = STAGING / "config" / "extraction_policy.json"

with POLICY_PATH.open("r", encoding="utf-8") as fh:
    POLICY = json.load(fh)

CORPUS = STAGING / "corpus"
REPORTS = STAGING / "reports"
MANIFESTS = STAGING / "manifests"

NORMALIZED_FILES = {
    "attachments": NORMALIZED / "attachments.jsonl",
    "content_blocks": NORMALIZED / "content_blocks.jsonl",
    "conversation_branches": NORMALIZED / "conversation_branches.jsonl",
    "conversations": NORMALIZED / "conversations.jsonl",
    "design_chats": NORMALIZED / "design_chats.jsonl",
    "file_references": NORMALIZED / "file_references.jsonl",
    "messages": NORMALIZED / "messages.jsonl",
    "project_documents": NORMALIZED / "project_documents.jsonl",
    "projects": NORMALIZED / "projects.jsonl",
    "source_files": NORMALIZED / "source_files.jsonl",
    "users_redacted": NORMALIZED / "users_redacted.jsonl",
}

CORPUS_FILES = {
    "source_units": CORPUS / "source_units.jsonl",
    "conversation_paths": CORPUS / "conversation_paths.jsonl",
    "extraction_packets": CORPUS / "extraction_packets.jsonl",
    "conversation_profiles": CORPUS / "conversation_profiles.jsonl",
    "duplicate_groups": CORPUS / "duplicate_groups.jsonl",
    "excluded_units": CORPUS / "excluded_units.jsonl",
    "warnings": REPORTS / "warnings.jsonl",
}

SECRET_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL)),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("api_key", re.compile(r"\b(?:sk|pk|rk|ak|api)[-_]?[A-Za-z0-9]{20,}\b")),
    ("password", re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*([^\s,;]{4,})")),
    ("auth_cookie", re.compile(r"(?i)\b(cookie|set-cookie|authorization)\s*[:=]\s*[^;\n]{8,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)")),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = []
    errors = []
    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append({"file": rel(path), "line": line_number, "error": str(exc)})
    return records, errors


def check(name: str, passed: bool, details: Any = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def all_normalized_records() -> dict[str, dict[str, Any]]:
    by_id = {}
    for path in NORMALIZED_FILES.values():
        records, errors = load_jsonl(path)
        if errors:
            raise RuntimeError(f"Could not parse normalized file {path}")
        for record in records:
            by_id[record["normalized_id"]] = record
    return by_id


def checksum_status() -> dict[str, Any]:
    before = load_json(MANIFESTS / "normalized_checksums_before.json")
    after = load_json(MANIFESTS / "normalized_checksums_after.json")
    current = {
        rel(path): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
            "modified_time_ns": path.stat().st_mtime_ns,
        }
        for path in sorted(NORMALIZED_FILES.values())
    }
    changed_between = [path for path in before if before[path]["sha256"] != after.get(path, {}).get("sha256")]
    changed_since = [path for path in after if after[path]["sha256"] != current.get(path, {}).get("sha256")]
    return {
        "passed": not changed_between and not changed_since and set(before) == set(after) == set(current),
        "changed_between_manifests": changed_between,
        "changed_since_after_manifest": changed_since,
        "before_count": len(before),
        "after_count": len(after),
        "current_count": len(current),
    }


def raw_checksum_status() -> dict[str, Any]:
    manifest_path = ROOT / "context_pipeline" / "manifests" / "raw_checksums_after.json"
    if not manifest_path.exists():
        return {"passed": False, "error": "Stage 2 raw checksum manifest is missing."}
    manifest = load_json(manifest_path)
    changed = []
    missing = []
    for source_file, info in manifest.items():
        path = ROOT / source_file
        if not path.exists():
            missing.append(source_file)
            continue
        current = sha256_file(path)
        if current != info.get("sha256"):
            changed.append(source_file)
    return {
        "passed": not changed and not missing,
        "manifest_count": len(manifest),
        "changed_since_stage2_manifest": changed,
        "missing_raw_files": missing,
    }


def staged_surface(records: dict[str, list[dict[str, Any]]]) -> str:
    parts = []
    for name in ("source_units", "conversation_paths", "extraction_packets", "conversation_profiles", "duplicate_groups", "excluded_units"):
        parts.extend(json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records[name])
    for path in (REPORTS / "extraction_staging_report.md", REPORTS / "review_sample.md", REPORTS / "warnings.jsonl"):
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def staged_text_surface(records: dict[str, list[dict[str, Any]]]) -> str:
    parts = [unit.get("text") or "" for unit in records["source_units"]]
    review = REPORTS / "review_sample.md"
    if review.exists():
        for line in review.read_text(encoding="utf-8").splitlines():
            if " packet `" in line and ": " in line:
                parts.append(line.rsplit(": ", 1)[-1])
            elif line.startswith("- Snippet: "):
                parts.append(line.removeprefix("- Snippet: "))
    return "\n".join(parts)


def users_private_values() -> list[str]:
    values = []
    path = ROOT / "users.json"
    if path.exists():
        for user in load_json(path):
            for key in ("email_address", "verified_phone_number"):
                value = user.get(key)
                if isinstance(value, str) and value:
                    values.append(value)
    return values


def main() -> None:
    records: dict[str, list[dict[str, Any]]] = {}
    parse_errors = []
    for name, path in CORPUS_FILES.items():
        parsed, errors = load_jsonl(path)
        records[name] = parsed
        parse_errors.extend(errors)

    checks: list[dict[str, Any]] = []
    checks.append(check("every_jsonl_line_parses", not parse_errors, parse_errors))

    duplicate_ids = {}
    id_fields = {
        "source_units": "source_unit_id",
        "conversation_paths": "conversation_path_id",
        "extraction_packets": "packet_id",
        "conversation_profiles": "conversation_id",
        "duplicate_groups": "duplicate_group_id",
        "excluded_units": "excluded_unit_id",
    }
    for name, field in id_fields.items():
        ids = [record.get(field) for record in records[name]]
        counts = Counter(ids)
        dupes = sorted([item for item, count in counts.items() if item and count > 1])
        if dupes:
            duplicate_ids[name] = dupes[:50]
    checks.append(check("deterministic_ids_unique_within_entity_type", not duplicate_ids, duplicate_ids))

    normalized_by_id = all_normalized_records()
    unresolved_units = [
        {"source_unit_id": u.get("source_unit_id"), "normalized_entity_id": u.get("normalized_entity_id")}
        for u in records["source_units"]
        if u.get("normalized_entity_id") not in normalized_by_id
    ]
    unresolved_excluded = [
        {"excluded_unit_id": e.get("excluded_unit_id"), "normalized_source_reference": e.get("normalized_source_reference")}
        for e in records["excluded_units"]
        if e.get("normalized_source_reference") not in normalized_by_id
    ]
    checks.append(check("every_source_unit_resolves_to_normalized_record", not unresolved_units, unresolved_units[:50]))
    checks.append(check("every_excluded_unit_resolves_to_normalized_record", not unresolved_excluded, unresolved_excluded[:50]))

    source_unit_ids = {u["source_unit_id"] for u in records["source_units"]}
    packet_ref_errors = []
    for packet in records["extraction_packets"]:
        for unit_id in packet.get("ordered_source_unit_ids") or []:
            if unit_id not in source_unit_ids:
                packet_ref_errors.append({"packet_id": packet.get("packet_id"), "source_unit_id": unit_id})
    checks.append(check("every_packet_source_unit_reference_resolves", not packet_ref_errors, packet_ref_errors[:50]))

    message_ids = {r["normalized_id"] for r in normalized_by_id.values() if r.get("record_type") == "message"}
    path_message_errors = []
    for path in records["conversation_paths"]:
        for message_id in path.get("ordered_message_ids") or []:
            if message_id not in message_ids:
                path_message_errors.append({"conversation_path_id": path.get("conversation_path_id"), "message_id": message_id})
    checks.append(check("every_conversation_path_message_reference_resolves", not path_message_errors, path_message_errors[:50]))

    packet_order_errors = []
    for packet in records["extraction_packets"]:
        if packet.get("start_timestamp") and packet.get("end_timestamp") and packet["start_timestamp"] > packet["end_timestamp"]:
            packet_order_errors.append({"packet_id": packet["packet_id"], "error": "start_after_end"})
    checks.append(check("packet_ordering_follows_timestamps", not packet_order_errors, packet_order_errors[:50]))

    offset_errors = [
        {"source_unit_id": u["source_unit_id"], "offsets": u.get("source_text_offsets")}
        for u in records["source_units"]
        if u.get("parent_source_unit_id")
        and (
            not isinstance(u.get("source_text_offsets"), dict)
            or u["source_text_offsets"].get("start") is None
            or u["source_text_offsets"].get("end") is None
            or u["source_text_offsets"]["start"] >= u["source_text_offsets"]["end"]
        )
    ]
    checks.append(check("oversized_units_have_valid_source_offsets", not offset_errors, offset_errors[:50]))

    thinking_blocks = {r["normalized_id"]: r for r in normalized_by_id.values() if r.get("block_type") == "thinking"}
    thinking_source_units = [u["source_unit_id"] for u in records["source_units"] if u.get("normalized_entity_id") in thinking_blocks]
    excluded_thinking = {e.get("normalized_source_reference") for e in records["excluded_units"] if e.get("exclusion_reason") == "model_internal_reasoning_not_project_knowledge"}
    missing_thinking_exclusions = sorted(set(thinking_blocks) - excluded_thinking)
    checks.append(check("all_thinking_blocks_are_excluded", not thinking_source_units and not missing_thinking_exclusions, {"thinking_source_units": thinking_source_units[:20], "missing_exclusions": missing_thinking_exclusions[:20]}))

    thinking_hashes = {r.get("content_sha256") for r in thinking_blocks.values() if r.get("content_sha256")}
    source_hashes = {u.get("content_hash_sha256") for u in records["source_units"] if u.get("content_hash_sha256")}
    checks.append(check("no_known_thinking_hash_appears_in_corpus", not (thinking_hashes & source_hashes), sorted(thinking_hashes & source_hashes)[:20]))

    surface = staged_surface(records)
    private_leaks = []
    for value in users_private_values():
        if value in surface:
            private_leaks.append(hashlib.sha256(value.encode("utf-8")).hexdigest())
    checks.append(check("email_addresses_and_phone_numbers_from_users_json_absent", not private_leaks, private_leaks))

    text_surface = staged_text_surface(records)
    secret_hits = []
    for category, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text_surface):
            text = match.group(0)
            if "[REDACTED_" in text:
                continue
            secret_hits.append({"category": category, "hash": hashlib.sha256(text.encode("utf-8")).hexdigest()})
            if len(secret_hits) >= 50:
                break
        if len(secret_hits) >= 50:
            break
    checks.append(check("detected_secrets_are_redacted", not secret_hits, secret_hits[:50]))

    eligible_user_messages = [
        r for r in normalized_by_id.values()
        if r.get("record_type") == "message"
        and r.get("role") in ("human", "user")
        and (r.get("direct_text_char_count") or 0) > 0
    ]
    source_unit_entity_ids = {u.get("normalized_entity_id") for u in records["source_units"]}
    excluded_entity_ids = {e.get("normalized_source_reference") for e in records["excluded_units"]}
    disappeared_user_text = [
        r["normalized_id"] for r in eligible_user_messages
        if r["normalized_id"] not in source_unit_entity_ids and r["normalized_id"] not in excluded_entity_ids
    ]
    checks.append(check("no_eligible_user_text_disappears_without_exclusion", not disappeared_user_text, disappeared_user_text[:50]))

    assistant_as_user = [
        u["source_unit_id"] for u in records["source_units"]
        if u.get("author_role") == "assistant" and u.get("semantic_provenance") == "user_statement"
    ]
    checks.append(check("no_assistant_text_labeled_as_user_statement", not assistant_as_user, assistant_as_user[:50]))

    tool_verified = [
        u["source_unit_id"] for u in records["source_units"]
        if u.get("semantic_provenance") == "tool_output_unverified" and u.get("extraction_eligibility") is True
    ]
    checks.append(check("no_tool_result_labeled_as_verified_fact", not tool_verified, tool_verified[:50]))

    duplicate_member_errors = []
    for group in records["duplicate_groups"]:
        for unit_id in group.get("member_source_unit_ids") or []:
            if unit_id not in source_unit_ids:
                duplicate_member_errors.append({"duplicate_group_id": group.get("duplicate_group_id"), "source_unit_id": unit_id})
    checks.append(check("duplicate_groups_preserve_original_source_unit_members", not duplicate_member_errors, duplicate_member_errors[:50]))

    checksum = checksum_status()
    raw_checksum = raw_checksum_status()
    checks.append(check("stage2_normalized_files_remain_unchanged", checksum["passed"], checksum))
    checks.append(check("raw_files_remain_unchanged_since_stage2_manifest", raw_checksum["passed"], raw_checksum))

    output_hashes = {
        rel(path): sha256_file(path)
        for path in sorted(list(CORPUS_FILES.values()) + [REPORTS / "extraction_staging_report.md", REPORTS / "review_sample.md"])
        if path.exists()
    }
    checks.append(check("stable_output_hashes_recorded_for_determinism", True, output_hashes))

    max_tokens = POLICY["packet_limits"]["maximum_estimated_tokens"]
    packet_size_errors = [
        {"packet_id": p["packet_id"], "estimated_token_count": p["estimated_token_count"], "warnings": p.get("packet_warnings")}
        for p in records["extraction_packets"]
        if p["estimated_token_count"] > max_tokens and "contains_oversized_source_subunit" not in (p.get("packet_warnings") or [])
    ]
    checks.append(check("packet_size_limits_respected_except_documented_oversized_cases", not packet_size_errors, packet_size_errors[:50]))

    has_design = any(u.get("source_unit_type", "").startswith("design_chat_") for u in records["source_units"])
    has_project_doc = any(u.get("source_unit_type") == "project_document" for u in records["source_units"])
    checks.append(check("design_chat_and_project_document_content_represented", has_design and has_project_doc, {"has_design_chat": has_design, "has_project_document": has_project_doc}))

    allowed_eligibility = {True, False, "conditional"}
    eligibility_errors = [
        {"source_unit_id": u["source_unit_id"], "extraction_eligibility": u.get("extraction_eligibility")}
        for u in records["source_units"]
        if u.get("extraction_eligibility") not in allowed_eligibility
    ]
    checks.append(check("extraction_eligibility_values_comply_with_policy", not eligibility_errors, eligibility_errors[:50]))

    counts = {
        "source_units": len(records["source_units"]),
        "conversation_paths": len(records["conversation_paths"]),
        "extraction_packets": len(records["extraction_packets"]),
        "conversation_profiles": len(records["conversation_profiles"]),
        "duplicate_groups": len(records["duplicate_groups"]),
        "excluded_units": len(records["excluded_units"]),
        "warnings": len(records["warnings"]),
        "source_units_by_provenance": dict(sorted(Counter(u["semantic_provenance"] for u in records["source_units"]).items())),
        "excluded_units_by_reason": dict(sorted(Counter(e["exclusion_reason"] for e in records["excluded_units"]).items())),
        "duplicate_groups_by_type": dict(sorted(Counter(g["duplicate_type"] for g in records["duplicate_groups"]).items())),
    }
    failed = [item for item in checks if not item["passed"]]
    report = {
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "counts": counts,
        "discrepancies": {},
        "unresolved_references": {
            "source_units": unresolved_units[:100],
            "packet_source_units": packet_ref_errors[:100],
            "path_messages": path_message_errors[:100],
        },
        "checksum_result": {
            "normalized": checksum,
            "raw": raw_checksum,
            "passed": checksum["passed"] and raw_checksum["passed"],
        },
        "redaction_checks": {
            "private_value_leaks": private_leaks,
            "secret_hits": secret_hits[:100],
        },
        "determinism_checks": {
            "output_hashes": output_hashes,
        },
        "packet_size_checks": {
            "maximum_estimated_tokens": max_tokens,
            "violations": packet_size_errors[:100],
        },
        "blocking_issues": [item["name"] for item in failed],
    }

    output = REPORTS / "validation_report.json"
    tmp = output.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(output)

    print(json.dumps({"status": report["status"], "failed_checks": report["blocking_issues"]}, sort_keys=True))


if __name__ == "__main__":
    main()
