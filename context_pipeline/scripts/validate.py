#!/usr/bin/env python3
"""Validate Stage 2 normalized Claude export records."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "context_pipeline"
CONFIG_PATH = PIPELINE / "config.json"

with CONFIG_PATH.open("r", encoding="utf-8") as fh:
    CONFIG = json.load(fh)

NORMALIZED_DIR = ROOT / CONFIG["output_paths"]["normalized_dir"]
REPORTS_DIR = ROOT / CONFIG["output_paths"]["reports_dir"]
MANIFESTS_DIR = ROOT / CONFIG["output_paths"]["manifests_dir"]
ROOT_SENTINEL = CONFIG["root_parent_sentinel_uuid"]

JSONL_FILES = {
    "conversations": NORMALIZED_DIR / "conversations.jsonl",
    "messages": NORMALIZED_DIR / "messages.jsonl",
    "content_blocks": NORMALIZED_DIR / "content_blocks.jsonl",
    "conversation_branches": NORMALIZED_DIR / "conversation_branches.jsonl",
    "attachments": NORMALIZED_DIR / "attachments.jsonl",
    "file_references": NORMALIZED_DIR / "file_references.jsonl",
    "projects": NORMALIZED_DIR / "projects.jsonl",
    "project_documents": NORMALIZED_DIR / "project_documents.jsonl",
    "design_chats": NORMALIZED_DIR / "design_chats.jsonl",
    "users_redacted": NORMALIZED_DIR / "users_redacted.jsonl",
    "source_files": NORMALIZED_DIR / "source_files.jsonl",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_files() -> list[Path]:
    files = [
        ROOT / CONFIG["raw_paths"]["conversations"],
        ROOT / CONFIG["raw_paths"]["users"],
    ]
    files.extend(sorted((ROOT / CONFIG["raw_paths"]["projects_dir"]).glob("*.json")))
    files.extend(sorted((ROOT / CONFIG["raw_paths"]["design_chats_dir"]).glob("*.json")))
    return files


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                errors.append({"file": rel(path), "line": line_number, "error": str(exc)})
    return records, errors


def parse_utc(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def check(name: str, passed: bool, details: Any = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "details": details}


def raw_counts() -> dict[str, int]:
    conversations = load_json(ROOT / CONFIG["raw_paths"]["conversations"])
    users = load_json(ROOT / CONFIG["raw_paths"]["users"])
    projects = [load_json(path) for path in sorted((ROOT / CONFIG["raw_paths"]["projects_dir"]).glob("*.json"))]
    design_chats = [load_json(path) for path in sorted((ROOT / CONFIG["raw_paths"]["design_chats_dir"]).glob("*.json"))]
    return {
        "main_conversations": len(conversations),
        "main_messages": sum(len(c.get("chat_messages") or []) for c in conversations),
        "design_chats": len(design_chats),
        "design_chat_messages": sum(len(c.get("messages") or []) for c in design_chats),
        "projects": len(projects),
        "project_documents": sum(len(p.get("docs") or []) for p in projects),
        "users": len(users),
        "attachment_entries": sum(len(m.get("attachments") or []) for c in conversations for m in c.get("chat_messages") or []),
        "file_reference_entries": sum(len(m.get("files") or []) for c in conversations for m in c.get("chat_messages") or []),
    }


def observed_counts(records: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    main_messages = [r for r in records["messages"] if r.get("source_export_family") == "conversations"]
    design_messages = [r for r in records["messages"] if r.get("source_export_family") == "design_chats"]
    return {
        "main_conversations": len(records["conversations"]),
        "main_messages": len(main_messages),
        "design_chats": len(records["design_chats"]),
        "design_chat_messages": len(design_messages),
        "projects": len(records["projects"]),
        "project_documents": len(records["project_documents"]),
        "users": len(records["users_redacted"]),
        "attachment_entries": len(records["attachments"]),
        "file_reference_entries": len(records["file_references"]),
        "content_blocks": len(records["content_blocks"]),
        "conversation_branch_records": len(records["conversation_branches"]),
        "source_files": len(records["source_files"]),
    }


def checksum_status() -> dict[str, Any]:
    before = load_json(MANIFESTS_DIR / "raw_checksums_before.json")
    after = load_json(MANIFESTS_DIR / "raw_checksums_after.json")
    current = {
        rel(path): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
            "modified_time_ns": path.stat().st_mtime_ns,
        }
        for path in raw_files()
    }
    changed_between_manifests = [
        path for path in before if before[path]["sha256"] != after.get(path, {}).get("sha256")
    ]
    changed_since_after = [
        path for path in after if after[path]["sha256"] != current.get(path, {}).get("sha256")
    ]
    return {
        "before_manifest_count": len(before),
        "after_manifest_count": len(after),
        "current_raw_file_count": len(current),
        "changed_between_manifests": changed_between_manifests,
        "changed_since_after_manifest": changed_since_after,
        "passed": not changed_between_manifests and not changed_since_after and set(before) == set(after) == set(current),
    }


def privacy_status(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    users = load_json(ROOT / CONFIG["raw_paths"]["users"])
    secrets = []
    for user in users:
        for key in ("email_address", "verified_phone_number"):
            value = user.get(key)
            if isinstance(value, str) and value:
                secrets.append(value)
    surfaces = {
        "users_redacted.jsonl": "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in records["users_redacted"]),
        "normalization_report.md": (REPORTS_DIR / "normalization_report.md").read_text(encoding="utf-8"),
        "validation_report.json": "",
        "warnings.jsonl": (REPORTS_DIR / "warnings.jsonl").read_text(encoding="utf-8"),
    }
    leaks = []
    for secret in secrets:
        for surface_name, surface in surfaces.items():
            if secret and secret in surface:
                leaks.append({"surface": surface_name, "secret_sha256": hashlib.sha256(secret.encode("utf-8")).hexdigest()})
    return {"checked_secret_count": len(secrets), "leaks": leaks, "passed": not leaks}


def main() -> None:
    checks: list[dict[str, Any]] = []
    records: dict[str, list[dict[str, Any]]] = {}
    parse_errors: list[dict[str, Any]] = []

    for name, path in JSONL_FILES.items():
        parsed, errors = load_jsonl(path)
        records[name] = parsed
        parse_errors.extend(errors)
    checks.append(check("all_jsonl_lines_parse", not parse_errors, parse_errors))

    duplicate_ids: dict[str, list[str]] = {}
    id_pattern_failures: dict[str, list[str]] = {}
    id_pattern = re.compile(r"^claude:[a-z_]+:[a-z_]+:.+")
    for name, parsed in records.items():
        ids = [r.get("normalized_id") for r in parsed if r.get("normalized_id")]
        counts = Counter(ids)
        dups = sorted([normalized_id for normalized_id, count in counts.items() if count > 1])
        if dups:
            duplicate_ids[name] = dups
        failures = [normalized_id for normalized_id in ids if not id_pattern.match(normalized_id)]
        if failures:
            id_pattern_failures[name] = failures[:20]
    checks.append(check("normalized_ids_unique_within_each_entity_type", not duplicate_ids, duplicate_ids))
    checks.append(check("deterministic_id_pattern", not id_pattern_failures, id_pattern_failures))

    expected = CONFIG["expected_stage1_counts"]
    raw = raw_counts()
    observed = observed_counts(records)
    raw_discrepancies = {key: {"stage1": expected[key], "raw": raw[key]} for key in expected if expected[key] != raw[key]}
    observed_discrepancies = {key: {"raw": raw[key], "observed": observed[key]} for key in raw if raw[key] != observed[key]}
    checks.append(check("stage1_counts_reconcile_with_raw_export", not raw_discrepancies, raw_discrepancies))
    checks.append(check("normalized_counts_reconcile_with_raw_export", not observed_discrepancies, observed_discrepancies))

    checks.append(check("conversation_counts_reconcile", observed["main_conversations"] == raw["main_conversations"], {"raw": raw["main_conversations"], "observed": observed["main_conversations"]}))
    checks.append(check("message_counts_reconcile", observed["main_messages"] == raw["main_messages"], {"raw": raw["main_messages"], "observed": observed["main_messages"]}))
    checks.append(check("project_counts_reconcile", observed["projects"] == raw["projects"], {"raw": raw["projects"], "observed": observed["projects"]}))
    checks.append(check("project_document_counts_reconcile", observed["project_documents"] == raw["project_documents"], {"raw": raw["project_documents"], "observed": observed["project_documents"]}))
    checks.append(check("design_chat_counts_reconcile", observed["design_chats"] == raw["design_chats"] and observed["design_chat_messages"] == raw["design_chat_messages"], {"raw": raw, "observed": observed}))
    checks.append(check("attachment_and_file_reference_counts_reconcile", observed["attachment_entries"] == raw["attachment_entries"] and observed["file_reference_entries"] == raw["file_reference_entries"], {"raw": raw, "observed": observed}))

    message_ids = {r["normalized_id"] for r in records["messages"]}
    unresolved_parents = [
        {
            "message": r.get("normalized_id"),
            "parent": r.get("parent_message_normalized_id"),
        }
        for r in records["messages"]
        if r.get("parent_message_normalized_id") and r.get("parent_message_normalized_id") not in message_ids
    ]
    checks.append(check("normalized_parent_references_resolve_when_expected", not unresolved_parents, unresolved_parents[:50]))

    tool_use_ids = {
        r.get("tool_call_id")
        for r in records["content_blocks"]
        if r.get("block_type") in ("tool_use", "tool_call") and r.get("tool_call_id")
    }
    unresolved_tool_results = [
        {
            "content_block": r.get("normalized_id"),
            "tool_use_id": r.get("tool_use_id"),
        }
        for r in records["content_blocks"]
        if r.get("block_type") == "tool_result" and r.get("tool_use_id") and r.get("tool_use_id") not in tool_use_ids
    ]
    checks.append(check("tool_result_tool_use_ids_resolve_when_possible", not unresolved_tool_results, unresolved_tool_results[:50]))

    branch_errors = []
    child_counts: dict[str, int] = defaultdict(int)
    roots_by_conversation: dict[str, set[str]] = defaultdict(set)
    leaves_by_conversation: dict[str, set[str]] = defaultdict(set)
    for message in records["messages"]:
        if message.get("source_export_family") != "conversations":
            continue
        conv_id = message.get("conversation_normalized_id")
        msg_id = message.get("normalized_id")
        if message.get("root"):
            roots_by_conversation[conv_id].add(msg_id)
        if message.get("leaf"):
            leaves_by_conversation[conv_id].add(msg_id)
        parent = message.get("parent_message_normalized_id")
        if parent:
            child_counts[parent] += 1
    for branch in records["conversation_branches"]:
        conv_id = branch.get("conversation_normalized_id")
        path = branch.get("ordered_message_normalized_ids") or []
        if path:
            if path[0] not in roots_by_conversation[conv_id]:
                branch_errors.append({"branch": branch.get("normalized_id"), "error": "path_root_not_marked_root"})
            if path[-1] not in leaves_by_conversation[conv_id]:
                branch_errors.append({"branch": branch.get("normalized_id"), "error": "path_leaf_not_marked_leaf"})
            for msg_id in path:
                if msg_id not in message_ids:
                    branch_errors.append({"branch": branch.get("normalized_id"), "error": "path_message_missing", "message": msg_id})
        else:
            if roots_by_conversation.get(conv_id) or leaves_by_conversation.get(conv_id):
                branch_errors.append({"branch": branch.get("normalized_id"), "error": "empty_branch_for_nonempty_conversation"})
    checks.append(check("branch_roots_and_leaves_internally_consistent", not branch_errors, branch_errors[:50]))

    checksum = checksum_status()
    checks.append(check("raw_source_checksums_unchanged", checksum["passed"], checksum))

    timestamp_errors = []
    for name, parsed in records.items():
        for record in parsed:
            for field in ("normalized_created_at_utc", "normalized_updated_at_utc"):
                if not parse_utc(record.get(field)):
                    timestamp_errors.append({"file": name, "record": record.get("normalized_id"), "field": field, "value": record.get(field)})
    checks.append(check("timestamps_valid_or_absent", not timestamp_errors, timestamp_errors[:50]))

    privacy = privacy_status(records)
    checks.append(check("users_redacted_and_reports_do_not_contain_user_email_or_phone", privacy["passed"], privacy))

    thinking_errors = []
    for record in records["content_blocks"]:
        if record.get("block_type") == "thinking":
            forbidden_fields = [field for field in ("text", "content_text", "thinking") if field in record and record.get(field)]
            if forbidden_fields:
                thinking_errors.append({"record": record.get("normalized_id"), "forbidden_fields": forbidden_fields})
            if record.get("extraction_eligibility") is not False:
                thinking_errors.append({"record": record.get("normalized_id"), "error": "thinking_block_not_excluded"})
    checks.append(check("thinking_text_not_duplicated_into_normalized_searchable_content", not thinking_errors, thinking_errors[:50]))

    stable_count_details = {
        "raw_counts": raw,
        "observed_counts": observed,
        "counts_match_raw": not observed_discrepancies,
    }
    checks.append(check("rerun_stable_record_counts_supported_by_raw_reconciliation", not observed_discrepancies, stable_count_details))

    status = "pass" if all(item["passed"] for item in checks) else "fail"
    report = {
        "status": status,
        "checks_performed": checks,
        "expected_counts": expected,
        "raw_counts": raw,
        "observed_counts": observed,
        "discrepancies": {
            "stage1_vs_raw": raw_discrepancies,
            "raw_vs_normalized": observed_discrepancies,
        },
        "unresolved_references": {
            "parents": unresolved_parents[:100],
            "tool_results": unresolved_tool_results[:100],
        },
        "checksum_status": checksum,
        "timestamp_warnings": timestamp_errors[:100],
        "privacy_checks": privacy,
        "deterministic_id_checks": {
            "duplicate_ids": duplicate_ids,
            "id_pattern_failures": id_pattern_failures,
        },
    }
    output = REPORTS_DIR / "validation_report.json"
    tmp = output.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(output)

    print(json.dumps({"status": status, "failed_checks": [c["name"] for c in checks if not c["passed"]]}, sort_keys=True))


if __name__ == "__main__":
    main()
