#!/usr/bin/env python3
"""Normalize Claude export files into reversible JSONL staging records."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
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
SOURCE_PLATFORM = CONFIG["source_platform"]

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


class WarningLog:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def add(
        self,
        warning_type: str,
        severity: str,
        entity_ref: str | None,
        source_file: str,
        explanation: str,
        blocks_next_stage: bool = False,
    ) -> str:
        warning_id = f"warning:{len(self.records) + 1:06d}"
        self.records.append(
            {
                "warning_id": warning_id,
                "warning_type": warning_type,
                "severity": severity,
                "entity_ref": entity_ref,
                "source_file": source_file,
                "explanation": explanation,
                "blocks_next_stage": blocks_next_stage,
            }
        )
        return warning_id


WARNINGS = WarningLog()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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


def checksum_manifest() -> dict[str, dict[str, Any]]:
    manifest: dict[str, dict[str, Any]] = {}
    for path in raw_files():
        stat = path.stat()
        manifest[rel(path)] = {
            "sha256": sha256_file(path),
            "size_bytes": stat.st_size,
            "modified_time_ns": stat.st_mtime_ns,
        }
    return manifest


def write_json(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        for record in records:
            json.dump(record, fh, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
    os.replace(tmp, path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize_ts(value: Any, source_file: str, entity_ref: str | None) -> str | None:
    if not isinstance(value, str) or not value:
        if value not in (None, ""):
            WARNINGS.add(
                "timestamp_invalid_type",
                "warning",
                entity_ref,
                source_file,
                "Timestamp was present but was not a non-empty string.",
            )
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    except ValueError:
        WARNINGS.add(
            "timestamp_parse_failed",
            "warning",
            entity_ref,
            source_file,
            "Timestamp could not be normalized to UTC.",
        )
        return None


def nid(family: str, entity: str, source_id: str) -> str:
    return f"claude:{family}:{entity}:{source_id}"


def common(
    *,
    normalized_id: str,
    family: str,
    record_type: str,
    source_file: str,
    source_record_id: str | None,
    source_parent_id: str | None,
    source_index: int | None,
    raw_pointer: str,
    created_at: Any = None,
    updated_at: Any = None,
    extraction_eligibility: Any = "conditional",
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "normalized_id": normalized_id,
        "source_platform": SOURCE_PLATFORM,
        "source_export_family": family,
        "source_file": source_file,
        "source_record_id": source_record_id,
        "source_parent_id": source_parent_id,
        "source_index": source_index,
        "original_created_at": created_at,
        "original_updated_at": updated_at,
        "normalized_created_at_utc": normalize_ts(created_at, source_file, normalized_id),
        "normalized_updated_at_utc": normalize_ts(updated_at, source_file, normalized_id),
        "record_type": record_type,
        "provenance": {
            "source_file": source_file,
            "source_record_id": source_record_id,
            "source_parent_id": source_parent_id,
            "source_index": source_index,
            "raw_pointer": raw_pointer,
            "source_export_family": family,
        },
        "extraction_eligibility": extraction_eligibility,
        "warnings": warnings or [],
    }


def sender_semantic(sender: str | None) -> str:
    if sender in ("human", "user"):
        return "user_statement"
    if sender == "assistant":
        return "assistant_output"
    return "export_metadata"


def content_char_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return len(value)
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


def safe_type(value: Any) -> str:
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def local_payload_exists(file_name: str | None, file_uuid: str | None) -> bool:
    if not file_name and not file_uuid:
        return False
    candidates = []
    if file_name:
        candidates.extend(ROOT.glob(f"**/{Path(file_name).name}"))
    if file_uuid:
        candidates.extend(ROOT.glob(f"**/{file_uuid}*"))
    raw_roots = {ROOT / "projects", ROOT / "design_chats"}
    for candidate in candidates:
        if "context_pipeline" in candidate.parts:
            continue
        if candidate.name in {"conversations.json", "users.json", ".DS_Store"}:
            continue
        if any(root in candidate.parents for root in raw_roots):
            continue
        if candidate.is_file():
            return True
    return False


def build_main_conversations(data: list[dict[str, Any]], source_file: str, out: dict[str, list[dict[str, Any]]]) -> Counter:
    counts: Counter = Counter()
    all_tool_use_ids: set[str] = set()

    for conv_index, conv in enumerate(data):
        conv_uuid = conv.get("uuid")
        conv_nid = nid("conversations", "conversation", conv_uuid)
        messages = conv.get("chat_messages") or []
        msg_by_uuid = {m.get("uuid"): m for m in messages if m.get("uuid")}
        children: dict[str, list[str]] = defaultdict(list)
        message_warnings: dict[str, list[str]] = defaultdict(list)
        roots: list[str] = []

        for message in messages:
            msg_uuid = message.get("uuid")
            parent_uuid = message.get("parent_message_uuid")
            if parent_uuid and parent_uuid != ROOT_SENTINEL and parent_uuid in msg_by_uuid:
                children[parent_uuid].append(msg_uuid)
            elif parent_uuid == ROOT_SENTINEL or not parent_uuid:
                roots.append(msg_uuid)
            else:
                warning_id = WARNINGS.add(
                    "missing_parent_reference",
                    "warning",
                    nid("conversations", "message", msg_uuid),
                    source_file,
                    "Message parent UUID was not found in the same conversation.",
                )
                message_warnings[msg_uuid].append(warning_id)
                roots.append(msg_uuid)

        leaves = [m.get("uuid") for m in messages if m.get("uuid") and not children.get(m.get("uuid"))]
        branch_paths: list[list[str]] = []

        def walk(current_uuid: str, path: list[str]) -> None:
            next_path = path + [current_uuid]
            child_ids = children.get(current_uuid) or []
            if not child_ids:
                branch_paths.append(next_path)
                return
            for child_id in child_ids:
                walk(child_id, next_path)

        for root_uuid in roots:
            if root_uuid:
                walk(root_uuid, [])

        branch_count = len(branch_paths)
        title = conv.get("name") or ""
        conv_warnings: list[str] = []
        if not title:
            conv_warnings.append(
                WARNINGS.add(
                    "conversation_title_missing",
                    "info",
                    conv_nid,
                    source_file,
                    "Conversation title is empty.",
                )
            )
        if not messages:
            conv_warnings.append(
                WARNINGS.add(
                    "conversation_empty",
                    "info",
                    conv_nid,
                    source_file,
                    "Conversation has no messages.",
                )
            )

        conv_record = common(
            normalized_id=conv_nid,
            family="conversations",
            record_type="conversation",
            source_file=source_file,
            source_record_id=conv_uuid,
            source_parent_id=conv.get("account", {}).get("uuid"),
            source_index=conv_index,
            raw_pointer=f"/{conv_index}",
            created_at=conv.get("created_at"),
            updated_at=conv.get("updated_at"),
            extraction_eligibility="conditional",
            warnings=conv_warnings,
        )
        conv_record.update(
            {
                "conversation_id": conv_nid,
                "source_conversation_uuid": conv_uuid,
                "title": title,
                "title_missing": not bool(title),
                "summary": conv.get("summary") or "",
                "message_count": len(messages),
                "root_message_count": len(roots),
                "leaf_message_count": len(leaves),
                "branch_count": branch_count,
                "empty_conversation": len(messages) == 0,
                "account_reference": conv.get("account", {}).get("uuid"),
                "message_normalized_ids": [nid("conversations", "message", m.get("uuid")) for m in messages if m.get("uuid")],
                "semantic_provenance": "export_metadata",
            }
        )
        out["conversations"].append(conv_record)
        counts["main_conversations"] += 1

        for msg_index, message in enumerate(messages):
            msg_uuid = message.get("uuid")
            msg_nid = nid("conversations", "message", msg_uuid)
            parent_uuid = message.get("parent_message_uuid")
            parent_nid = None
            root_flag = False
            if parent_uuid and parent_uuid != ROOT_SENTINEL and parent_uuid in msg_by_uuid:
                parent_nid = nid("conversations", "message", parent_uuid)
            else:
                root_flag = True
            direct_text = message.get("text") or ""
            msg_record = common(
                normalized_id=msg_nid,
                family="conversations",
                record_type="message",
                source_file=source_file,
                source_record_id=msg_uuid,
                source_parent_id=parent_uuid,
                source_index=msg_index,
                raw_pointer=f"/{conv_index}/chat_messages/{msg_index}",
                created_at=message.get("created_at"),
                updated_at=message.get("updated_at"),
                extraction_eligibility=True if message.get("sender") == "human" else "conditional",
                warnings=message_warnings.get(msg_uuid, []),
            )
            msg_record.update(
                {
                    "conversation_normalized_id": conv_nid,
                    "message_normalized_id": msg_nid,
                    "source_message_uuid": msg_uuid,
                    "parent_message_normalized_id": parent_nid,
                    "original_parent_uuid": parent_uuid,
                    "message_order_index": msg_index,
                    "sender": message.get("sender"),
                    "role": message.get("sender"),
                    "direct_text": direct_text,
                    "direct_text_char_count": len(direct_text),
                    "content_block_count": len(message.get("content") or []),
                    "attachment_count": len(message.get("attachments") or []),
                    "file_reference_count": len(message.get("files") or []),
                    "root": root_flag,
                    "leaf": not bool(children.get(msg_uuid)),
                    "child_count": len(children.get(msg_uuid) or []),
                    "semantic_provenance": sender_semantic(message.get("sender")),
                }
            )
            out["messages"].append(msg_record)
            counts["main_messages"] += 1
            counts[f"text_chars:{sender_semantic(message.get('sender'))}"] += len(direct_text)

            for block_index, block in enumerate(message.get("content") or []):
                block_type = block.get("type")
                block_id = f"{msg_uuid}:block:{block_index:04d}"
                block_nid = nid("conversations", "content_block", block_id)
                block_record = common(
                    normalized_id=block_nid,
                    family="conversations",
                    record_type="content_block",
                    source_file=source_file,
                    source_record_id=block.get("id") or block_id,
                    source_parent_id=msg_uuid,
                    source_index=block_index,
                    raw_pointer=f"/{conv_index}/chat_messages/{msg_index}/content/{block_index}",
                    created_at=block.get("start_timestamp"),
                    updated_at=block.get("stop_timestamp"),
                    extraction_eligibility="conditional",
                )
                semantic = sender_semantic(message.get("sender"))
                block_record.update(
                    {
                        "conversation_normalized_id": conv_nid,
                        "message_normalized_id": msg_nid,
                        "block_index": block_index,
                        "block_type": block_type,
                        "semantic_provenance": semantic,
                        "content_available": False,
                        "content_char_count": 0,
                        "content_sha256": None,
                        "tool_call_id": block.get("id"),
                        "tool_use_id": block.get("tool_use_id"),
                        "tool_name": block.get("name"),
                        "integration_name": block.get("integration_name"),
                        "integration_is_mcp_app": block.get("is_mcp_app"),
                        "is_error": block.get("is_error"),
                        "truncated": block.get("truncated"),
                        "exclusion_reason": None,
                    }
                )
                if block_type == "text":
                    text = block.get("text") or ""
                    block_record.update(
                        {
                            "content_text": text,
                            "content_available": bool(text),
                            "content_char_count": len(text),
                            "content_sha256": sha256_text(text) if text else None,
                            "extraction_eligibility": True if message.get("sender") == "human" else "conditional",
                        }
                    )
                    counts[f"text_chars:{semantic}"] += len(text)
                elif block_type == "thinking":
                    thinking = block.get("thinking") or ""
                    block_record.update(
                        {
                            "content_available": bool(thinking),
                            "content_char_count": len(thinking),
                            "content_sha256": sha256_text(thinking) if thinking else None,
                            "semantic_provenance": "model_internal_reasoning_excluded",
                            "extraction_eligibility": False,
                            "exclusion_reason": "model_internal_reasoning_not_project_knowledge",
                        }
                    )
                    counts["excluded:model_internal_reasoning_not_project_knowledge"] += 1
                    counts["thinking_blocks"] += 1
                elif block_type == "token_budget":
                    block_record.update(
                        {
                            "content_available": False,
                            "semantic_provenance": "export_metadata",
                            "extraction_eligibility": False,
                            "exclusion_reason": "token_budget_metadata",
                        }
                    )
                    counts["excluded:token_budget_metadata"] += 1
                elif block_type == "tool_use":
                    input_value = block.get("input")
                    all_tool_use_ids.add(block.get("id"))
                    block_record.update(
                        {
                            "semantic_provenance": "tool_input",
                            "extraction_eligibility": "conditional",
                            "input_available": input_value is not None,
                            "input_type": safe_type(input_value),
                            "input_key_count": len(input_value) if isinstance(input_value, dict) else None,
                            "input_sha256": sha256_text(json.dumps(input_value, ensure_ascii=False, sort_keys=True)) if input_value is not None else None,
                        }
                    )
                elif block_type == "tool_result":
                    content = block.get("content")
                    block_record.update(
                        {
                            "semantic_provenance": "tool_output_unverified",
                            "extraction_eligibility": "conditional",
                            "content_available": content is not None,
                            "content_type": safe_type(content),
                            "content_char_count": content_char_count(content),
                            "content_sha256": sha256_text(json.dumps(content, ensure_ascii=False, sort_keys=True)) if content is not None else None,
                        }
                    )
                    counts["text_chars:tool_output_unverified"] += content_char_count(content)
                else:
                    block_record.update({"semantic_provenance": "export_metadata"})
                    WARNINGS.add(
                        "unknown_content_block_type",
                        "warning",
                        block_nid,
                        source_file,
                        "Content block type was not recognized by the Stage 2 normalizer.",
                    )
                out["content_blocks"].append(block_record)
                counts["content_blocks"] += 1

            for att_index, attachment in enumerate(message.get("attachments") or []):
                extracted = attachment.get("extracted_content") or ""
                att_id = f"{msg_uuid}:attachment:{att_index:04d}"
                att_nid = nid("conversations", "attachment", att_id)
                att_record = common(
                    normalized_id=att_nid,
                    family="conversations",
                    record_type="attachment",
                    source_file=source_file,
                    source_record_id=att_id,
                    source_parent_id=msg_uuid,
                    source_index=att_index,
                    raw_pointer=f"/{conv_index}/chat_messages/{msg_index}/attachments/{att_index}",
                    extraction_eligibility=True if extracted else "conditional",
                )
                att_record.update(
                    {
                        "parent_message_normalized_id": msg_nid,
                        "filename": attachment.get("file_name"),
                        "file_type": attachment.get("file_type"),
                        "reported_size": attachment.get("file_size"),
                        "attachment_index": att_index,
                        "extracted_content_available": bool(extracted),
                        "extracted_content_char_count": len(extracted),
                        "extracted_content": extracted,
                        "missing_binary": True,
                        "semantic_provenance": "attachment_text",
                    }
                )
                out["attachments"].append(att_record)
                counts["attachment_entries"] += 1
                counts["text_chars:attachment_text"] += len(extracted)

            for file_index, file_ref in enumerate(message.get("files") or []):
                exists = local_payload_exists(file_ref.get("file_name"), file_ref.get("file_uuid"))
                file_id = f"{msg_uuid}:file_reference:{file_index:04d}"
                file_nid = nid("conversations", "file_reference", file_id)
                file_warnings = []
                if not exists:
                    file_warnings.append(
                        WARNINGS.add(
                            "unresolved_file_reference",
                            "warning",
                            file_nid,
                            source_file,
                            "File reference does not have a matching local payload in this workspace.",
                        )
                    )
                ref_record = common(
                    normalized_id=file_nid,
                    family="conversations",
                    record_type="file_reference",
                    source_file=source_file,
                    source_record_id=file_ref.get("file_uuid") or file_id,
                    source_parent_id=msg_uuid,
                    source_index=file_index,
                    raw_pointer=f"/{conv_index}/chat_messages/{msg_index}/files/{file_index}",
                    extraction_eligibility="conditional",
                    warnings=file_warnings,
                )
                ref_record.update(
                    {
                        "parent_message_normalized_id": msg_nid,
                        "filename": file_ref.get("file_name"),
                        "file_uuid": file_ref.get("file_uuid"),
                        "matching_local_payload_exists": exists,
                        "unresolved_reference": not exists,
                        "semantic_provenance": "export_metadata",
                    }
                )
                out["file_references"].append(ref_record)
                counts["file_reference_entries"] += 1

        branch_edges = [
            [nid("conversations", "message", parent), nid("conversations", "message", child)]
            for parent, child_ids in children.items()
            for child in child_ids
        ]
        for branch_index, path in enumerate(branch_paths):
            branch_id = f"{conv_uuid}:branch:{branch_index:04d}"
            normalized_path = [nid("conversations", "message", msg_uuid) for msg_uuid in path]
            branch_record = common(
                normalized_id=nid("conversations", "conversation_branch", branch_id),
                family="conversations",
                record_type="conversation_branch",
                source_file=source_file,
                source_record_id=branch_id,
                source_parent_id=conv_uuid,
                source_index=branch_index,
                raw_pointer=f"/{conv_index}/chat_messages",
                created_at=conv.get("created_at"),
                updated_at=conv.get("updated_at"),
                extraction_eligibility=False,
            )
            branch_record.update(
                {
                    "conversation_normalized_id": conv_nid,
                    "root_message_normalized_ids": [nid("conversations", "message", r) for r in roots],
                    "leaf_message_normalized_ids": [nid("conversations", "message", leaf) for leaf in leaves],
                    "parent_child_edges": branch_edges,
                    "branch_path_id": nid("conversations", "conversation_branch_path", branch_id),
                    "ordered_message_normalized_ids": normalized_path,
                    "branch_length": len(normalized_path),
                    "branch_root_message_normalized_id": normalized_path[0] if normalized_path else None,
                    "branch_leaf_message_normalized_id": normalized_path[-1] if normalized_path else None,
                    "branches_share_prefix": branch_count > 1,
                    "semantic_provenance": "export_metadata",
                }
            )
            out["conversation_branches"].append(branch_record)
            counts["conversation_branch_paths"] += 1

        if not branch_paths:
            branch_id = f"{conv_uuid}:branch:empty"
            branch_record = common(
                normalized_id=nid("conversations", "conversation_branch", branch_id),
                family="conversations",
                record_type="conversation_branch",
                source_file=source_file,
                source_record_id=branch_id,
                source_parent_id=conv_uuid,
                source_index=0,
                raw_pointer=f"/{conv_index}/chat_messages",
                created_at=conv.get("created_at"),
                updated_at=conv.get("updated_at"),
                extraction_eligibility=False,
                warnings=conv_warnings,
            )
            branch_record.update(
                {
                    "conversation_normalized_id": conv_nid,
                    "root_message_normalized_ids": [],
                    "leaf_message_normalized_ids": [],
                    "parent_child_edges": [],
                    "branch_path_id": None,
                    "ordered_message_normalized_ids": [],
                    "branch_length": 0,
                    "branch_root_message_normalized_id": None,
                    "branch_leaf_message_normalized_id": None,
                    "branches_share_prefix": False,
                    "semantic_provenance": "export_metadata",
                }
            )
            out["conversation_branches"].append(branch_record)
            counts["empty_conversation_branch_records"] += 1

    return counts


def build_users(users: list[dict[str, Any]], conversations: list[dict[str, Any]], projects: list[tuple[Path, dict[str, Any]]], out: dict[str, list[dict[str, Any]]]) -> Counter:
    counts: Counter = Counter()
    conv_links = Counter((c.get("account") or {}).get("uuid") for c in conversations)
    project_links = Counter((p.get("creator") or {}).get("uuid") for _, p in projects)
    source_file = CONFIG["raw_paths"]["users"]
    for index, user in enumerate(users):
        user_uuid = user.get("uuid")
        user_nid = nid("users", "user", user_uuid)
        record = common(
            normalized_id=user_nid,
            family="users",
            record_type="user_redacted",
            source_file=source_file,
            source_record_id=user_uuid,
            source_parent_id=None,
            source_index=index,
            raw_pointer=f"/{index}",
            extraction_eligibility=False,
        )
        record.update(
            {
                "source_user_uuid": user_uuid,
                "display_name": user.get("full_name") or "",
                "has_email": bool(user.get("email_address")),
                "has_phone": bool(user.get("verified_phone_number")),
                "linked_conversation_count": conv_links[user_uuid],
                "linked_project_count": project_links[user_uuid],
                "semantic_provenance": "export_metadata",
            }
        )
        out["users_redacted"].append(record)
        counts["users"] += 1
    return counts


def build_projects(projects: list[tuple[Path, dict[str, Any]]], out: dict[str, list[dict[str, Any]]]) -> Counter:
    counts: Counter = Counter()
    for project_index, (path, project) in enumerate(projects):
        source_file = rel(path)
        project_uuid = project.get("uuid")
        project_nid = nid("projects", "project", project_uuid)
        docs = project.get("docs") or []
        project_record = common(
            normalized_id=project_nid,
            family="projects",
            record_type="project",
            source_file=source_file,
            source_record_id=project_uuid,
            source_parent_id=(project.get("creator") or {}).get("uuid"),
            source_index=project_index,
            raw_pointer="/",
            created_at=project.get("created_at"),
            updated_at=project.get("updated_at"),
            extraction_eligibility="conditional",
        )
        project_record.update(
            {
                "project_uuid": project_uuid,
                "name": project.get("name") or "",
                "description": project.get("description") or "",
                "prompt_template": project.get("prompt_template") or "",
                "is_private": project.get("is_private"),
                "is_starter_project": project.get("is_starter_project"),
                "creator_reference": (project.get("creator") or {}).get("uuid"),
                "document_count": len(docs),
                "semantic_provenance": "export_metadata",
            }
        )
        out["projects"].append(project_record)
        counts["projects"] += 1
        counts["text_chars:export_metadata"] += len(project_record["name"]) + len(project_record["description"]) + len(project_record["prompt_template"])

        for doc_index, doc in enumerate(docs):
            doc_uuid = doc.get("uuid")
            doc_nid = nid("projects", "project_document", doc_uuid)
            content = doc.get("content") or ""
            doc_record = common(
                normalized_id=doc_nid,
                family="projects",
                record_type="project_document",
                source_file=source_file,
                source_record_id=doc_uuid,
                source_parent_id=project_uuid,
                source_index=doc_index,
                raw_pointer=f"/docs/{doc_index}",
                created_at=doc.get("created_at"),
                extraction_eligibility=True,
            )
            doc_record.update(
                {
                    "parent_project_normalized_id": project_nid,
                    "project_uuid": project_uuid,
                    "document_uuid": doc_uuid,
                    "filename": doc.get("filename"),
                    "content": content,
                    "content_char_count": len(content),
                    "semantic_provenance": "project_document",
                }
            )
            out["project_documents"].append(doc_record)
            counts["project_documents"] += 1
            counts["text_chars:project_document"] += len(content)
    return counts


def build_design_chats(design_chats: list[tuple[Path, dict[str, Any]]], project_uuids: set[str], out: dict[str, list[dict[str, Any]]]) -> Counter:
    counts: Counter = Counter()
    for chat_index, (path, chat) in enumerate(design_chats):
        source_file = rel(path)
        chat_uuid = chat.get("uuid")
        chat_nid = nid("design_chats", "design_chat", chat_uuid)
        project = chat.get("project") or {}
        project_uuid = project.get("uuid")
        chat_warnings = []
        if project_uuid not in project_uuids:
            chat_warnings.append(
                WARNINGS.add(
                    "design_project_unmatched",
                    "warning",
                    chat_nid,
                    source_file,
                    "Embedded design-chat project UUID does not match any exported project UUID.",
                )
            )
        messages = chat.get("messages") or []
        message_ids = [nid("design_chats", "message", m.get("uuid")) for m in messages if m.get("uuid")]
        chat_record = common(
            normalized_id=chat_nid,
            family="design_chats",
            record_type="design_chat",
            source_file=source_file,
            source_record_id=chat_uuid,
            source_parent_id=project_uuid,
            source_index=chat_index,
            raw_pointer="/",
            created_at=chat.get("created_at"),
            updated_at=chat.get("updated_at"),
            extraction_eligibility="conditional",
            warnings=chat_warnings,
        )
        chat_record.update(
            {
                "design_chat_uuid": chat_uuid,
                "title": chat.get("title") or "",
                "embedded_project_uuid": project_uuid,
                "embedded_project_name": project.get("name") or "",
                "embedded_project_matches_exported_project": project_uuid in project_uuids,
                "message_count": len(messages),
                "message_normalized_ids": message_ids,
                "semantic_provenance": "export_metadata",
            }
        )
        out["design_chats"].append(chat_record)
        counts["design_chats"] += 1

        for msg_index, message in enumerate(messages):
            msg_uuid = message.get("uuid")
            msg_nid = nid("design_chats", "message", msg_uuid)
            content_obj = message.get("content") or {}
            direct_text = content_obj.get("content") or ""
            content_blocks = content_obj.get("contentBlocks") or []
            attachments = content_obj.get("attachments") or []
            msg_record = common(
                normalized_id=msg_nid,
                family="design_chats",
                record_type="message",
                source_file=source_file,
                source_record_id=msg_uuid,
                source_parent_id=chat_uuid,
                source_index=msg_index,
                raw_pointer=f"/messages/{msg_index}",
                created_at=message.get("created_at"),
                updated_at=content_obj.get("timestamp"),
                extraction_eligibility=True if message.get("role") == "user" else "conditional",
            )
            msg_record.update(
                {
                    "conversation_normalized_id": chat_nid,
                    "message_normalized_id": msg_nid,
                    "source_message_uuid": msg_uuid,
                    "parent_message_normalized_id": None,
                    "original_parent_uuid": None,
                    "message_order_index": msg_index,
                    "sender": message.get("role"),
                    "role": message.get("role"),
                    "direct_text": direct_text,
                    "direct_text_char_count": len(direct_text),
                    "content_block_count": len(content_blocks),
                    "attachment_count": len(attachments),
                    "file_reference_count": 0,
                    "root": msg_index == 0,
                    "leaf": msg_index == len(messages) - 1,
                    "child_count": 1 if msg_index < len(messages) - 1 else 0,
                    "semantic_provenance": sender_semantic(message.get("role")),
                    "design_chat_schema": True,
                }
            )
            out["messages"].append(msg_record)
            counts["design_chat_messages"] += 1
            counts[f"text_chars:{sender_semantic(message.get('role'))}"] += len(direct_text)

            for block_index, block in enumerate(content_blocks):
                block_type = block.get("type")
                block_id = f"{msg_uuid}:block:{block_index:04d}"
                block_nid = nid("design_chats", "content_block", block_id)
                block_record = common(
                    normalized_id=block_nid,
                    family="design_chats",
                    record_type="content_block",
                    source_file=source_file,
                    source_record_id=block_id,
                    source_parent_id=msg_uuid,
                    source_index=block_index,
                    raw_pointer=f"/messages/{msg_index}/content/contentBlocks/{block_index}",
                    extraction_eligibility="conditional",
                )
                semantic = sender_semantic(message.get("role"))
                text = block.get("text") or ""
                block_record.update(
                    {
                        "conversation_normalized_id": chat_nid,
                        "message_normalized_id": msg_nid,
                        "block_index": block_index,
                        "block_type": block_type,
                        "semantic_provenance": semantic,
                        "content_available": bool(text),
                        "content_char_count": len(text),
                        "content_sha256": sha256_text(text) if text else None,
                        "tool_call_id": (block.get("toolCall") or {}).get("id"),
                        "tool_use_id": None,
                        "tool_name": (block.get("toolCall") or {}).get("name"),
                        "integration_name": None,
                        "integration_is_mcp_app": None,
                        "is_error": None,
                        "truncated": None,
                        "exclusion_reason": None,
                    }
                )
                if block_type == "text":
                    block_record["content_text"] = text
                    block_record["extraction_eligibility"] = True if message.get("role") == "user" else "conditional"
                    counts[f"text_chars:{semantic}"] += len(text)
                elif block_type == "thinking":
                    block_record.update(
                        {
                            "semantic_provenance": "model_internal_reasoning_excluded",
                            "extraction_eligibility": False,
                            "exclusion_reason": "model_internal_reasoning_not_project_knowledge",
                        }
                    )
                    counts["excluded:model_internal_reasoning_not_project_knowledge"] += 1
                    counts["thinking_blocks"] += 1
                elif block_type == "tool_call":
                    block_record.update(
                        {
                            "semantic_provenance": "tool_input",
                            "extraction_eligibility": "conditional",
                            "input_available": bool(block.get("toolCall")),
                            "input_type": safe_type(block.get("toolCall")),
                            "input_key_count": len(block.get("toolCall") or {}),
                            "input_sha256": sha256_text(json.dumps(block.get("toolCall"), ensure_ascii=False, sort_keys=True)) if block.get("toolCall") else None,
                        }
                    )
                out["content_blocks"].append(block_record)
                counts["content_blocks"] += 1
    return counts


def build_source_files(before: dict[str, Any], after: dict[str, Any], out: dict[str, list[dict[str, Any]]]) -> Counter:
    counts: Counter = Counter()
    for index, source_file in enumerate(sorted(before)):
        record = common(
            normalized_id=nid("source_files", "source_file", sha256_text(source_file)[:24]),
            family="source_files",
            record_type="source_file",
            source_file=source_file,
            source_record_id=source_file,
            source_parent_id=None,
            source_index=index,
            raw_pointer="/",
            extraction_eligibility=False,
        )
        record.update(
            {
                "size_bytes": before[source_file]["size_bytes"],
                "sha256_before": before[source_file]["sha256"],
                "sha256_after": after[source_file]["sha256"],
                "checksum_unchanged": before[source_file]["sha256"] == after[source_file]["sha256"],
                "semantic_provenance": "export_metadata",
            }
        )
        out["source_files"].append(record)
        counts["source_files"] += 1
    return counts


def warning_summary() -> dict[str, int]:
    return dict(Counter(record["warning_type"] for record in WARNINGS.records))


def write_normalization_report(counts: Counter, checksum_ok: bool) -> None:
    text_volume = {
        key.split(":", 1)[1]: value
        for key, value in sorted(counts.items())
        if key.startswith("text_chars:")
    }
    exclusions = {
        key.split(":", 1)[1]: value
        for key, value in sorted(counts.items())
        if key.startswith("excluded:")
    }
    lines = [
        "# Normalization Report",
        "",
        "## Source Formats Processed",
        "",
        "- `conversations.json`: main Claude conversation export",
        "- `users.json`: user/account export",
        "- `projects/*.json`: Claude project metadata and embedded documents",
        "- `design_chats/*.json`: separate design-chat export family",
        "",
        "## Output Entities Created",
        "",
    ]
    for name, path in JSONL_FILES.items():
        lines.append(f"- `{rel(path)}`")
    lines.extend(
        [
            "",
            "## Final Counts",
            "",
            f"- Main conversations: {counts['main_conversations']}",
            f"- Main messages: {counts['main_messages']}",
            f"- Design chats: {counts['design_chats']}",
            f"- Design-chat messages: {counts['design_chat_messages']}",
            f"- Projects: {counts['projects']}",
            f"- Project documents: {counts['project_documents']}",
            f"- Users redacted: {counts['users']}",
            f"- Content blocks: {counts['content_blocks']}",
            f"- Conversation branch path records: {counts['conversation_branch_paths']}",
            f"- Empty-conversation branch records: {counts['empty_conversation_branch_records']}",
            f"- Attachments: {counts['attachment_entries']}",
            f"- File references: {counts['file_reference_entries']}",
            f"- Source files: {counts['source_files']}",
            "",
            "## Text-Volume Counts By Provenance",
            "",
        ]
    )
    for provenance, chars in text_volume.items():
        lines.append(f"- `{provenance}`: {chars} chars")
    lines.extend(["", "## Excluded Content Counts By Reason", ""])
    for reason, count in exclusions.items():
        lines.append(f"- `{reason}`: {count}")
    if not exclusions:
        lines.append("- None")
    lines.extend(["", "## Warning Summary", ""])
    summary = warning_summary()
    for warning_type, count in sorted(summary.items()):
        lines.append(f"- `{warning_type}`: {count}")
    if not summary:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Memory And Processing Method",
            "",
            "The normalizer uses Python standard-library `json.load` for the approximately 103 MB main export. Outputs are written to temporary files and atomically renamed into place.",
            "",
            "## Unresolved Relationships",
            "",
            "- Design-chat embedded project UUIDs are preserved but not matched to exported project UUIDs.",
            "- File references are preserved as references; missing binary payloads are not invented.",
            "",
            "## Known Limitations",
            "",
            "- No project discovery, semantic extraction, clustering, embeddings, or summarization is performed.",
            "- Tool inputs and tool results are marked with unverified provenance and require later provenance-aware handling.",
            "- Thinking text is intentionally excluded from normalized searchable content.",
            "",
            "## Raw Checksum Verification Result",
            "",
            f"- Raw checksums unchanged after normalization: {checksum_ok}",
            "",
        ]
    )
    tmp = (REPORTS_DIR / "normalization_report.md").with_suffix(".md.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, REPORTS_DIR / "normalization_report.md")


def main() -> None:
    for directory in (NORMALIZED_DIR, REPORTS_DIR, MANIFESTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    before = checksum_manifest()
    write_json(MANIFESTS_DIR / "raw_checksums_before.json", before)

    conversations_path = ROOT / CONFIG["raw_paths"]["conversations"]
    users_path = ROOT / CONFIG["raw_paths"]["users"]
    projects_dir = ROOT / CONFIG["raw_paths"]["projects_dir"]
    design_chats_dir = ROOT / CONFIG["raw_paths"]["design_chats_dir"]

    conversations = load_json(conversations_path)
    users = load_json(users_path)
    projects = [(path, load_json(path)) for path in sorted(projects_dir.glob("*.json"))]
    design_chats = [(path, load_json(path)) for path in sorted(design_chats_dir.glob("*.json"))]

    out: dict[str, list[dict[str, Any]]] = {name: [] for name in JSONL_FILES}
    counts: Counter = Counter()
    counts.update(build_main_conversations(conversations, rel(conversations_path), out))
    counts.update(build_projects(projects, out))
    counts.update(build_design_chats(design_chats, {p.get("uuid") for _, p in projects}, out))
    counts.update(build_users(users, conversations, projects, out))

    after = checksum_manifest()
    counts.update(build_source_files(before, after, out))

    for name, path in JSONL_FILES.items():
        write_jsonl(path, out[name])

    write_jsonl(REPORTS_DIR / "warnings.jsonl", WARNINGS.records)
    write_json(MANIFESTS_DIR / "raw_checksums_after.json", after)
    checksum_ok = before == after
    write_normalization_report(counts, checksum_ok)

    print(json.dumps(
        {
            "status": "ok",
            "counts": {key: counts[key] for key in sorted(counts) if not key.startswith("text_chars:")},
            "warnings": len(WARNINGS.records),
            "raw_checksums_unchanged": checksum_ok,
        },
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
