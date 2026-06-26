#!/usr/bin/env python3
"""Build Stage 3 extraction staging records from Stage 2 normalized JSONL."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
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
}


class WarningLog:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def add(self, warning_type: str, severity: str, entity: str | None, explanation: str, blocks: bool = False) -> str:
        warning_id = f"stage3-warning:{len(self.records) + 1:06d}"
        self.records.append(
            {
                "warning_id": warning_id,
                "type": warning_type,
                "severity": severity,
                "affected_entity": entity,
                "explanation": explanation,
                "blocks_semantic_extraction": blocks,
            }
        )
        return warning_id


WARNINGS = WarningLog()
REDACTION_COUNTS: Counter = Counter()
RECONCILIATION_COUNTS: Counter = Counter()


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


def checksum_manifest() -> dict[str, dict[str, Any]]:
    return {
        rel(path): {
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
            "modified_time_ns": path.stat().st_mtime_ns,
        }
        for path in sorted(NORMALIZED_FILES.values())
    }


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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def estimate_tokens(text_or_chars: str | int) -> int:
    chars = text_or_chars if isinstance(text_or_chars, int) else len(text_or_chars)
    return math.ceil(chars / POLICY["token_estimate"]["characters_per_estimated_token"])


def canonical_text(text: str, collapse_ws: bool = False) -> str:
    normalized = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n").strip()
    if collapse_ws:
        normalized = re.sub(r"\s+", " ", normalized)
    return normalized


SECRET_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL)),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("api_key", re.compile(r"\b(?:sk|pk|rk|ak|api)[-_]?[A-Za-z0-9]{20,}\b")),
    ("password", re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*([^\s,;]{4,})")),
    ("auth_cookie", re.compile(r"(?i)\b(cookie|set-cookie|authorization)\s*[:=]\s*[^;\n]{8,}")),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone", re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}(?!\d)")),
]


def redact_text(text: str) -> tuple[str, dict[str, int]]:
    redacted = text
    counts: Counter = Counter()
    markers = POLICY["redaction"]["markers"]
    for category, pattern in SECRET_PATTERNS:
        marker = markers[category]
        redacted, count = pattern.subn(marker, redacted)
        if count:
            counts[category] += count
            REDACTION_COUNTS[category] += count
    return redacted, dict(counts)


def source_unit_id(entity_id: str, label: str) -> str:
    return f"stage3:source_unit:{sha256_text(entity_id + ':' + label)[:32]}"


def excluded_unit_id(entity_id: str, label: str) -> str:
    return f"stage3:excluded_unit:{sha256_text(entity_id + ':' + label)[:32]}"


def packet_id(scope: str, index: int) -> str:
    return f"stage3:packet:{sha256_text(scope)[:20]}:{index:05d}"


def duplicate_group_id(kind: str, key: str) -> str:
    return f"stage3:duplicate_group:{kind}:{sha256_text(key)[:24]}"


def policy_for_provenance(provenance: str) -> Any:
    return POLICY["eligibility_policy"].get(provenance, "conditional")


def make_source_unit(
    *,
    entity: dict[str, Any],
    label: str,
    text: str,
    unit_type: str,
    semantic_provenance: str,
    author_role: str | None = None,
    conversation_id: str | None = None,
    message_id: str | None = None,
    project_id: str | None = None,
    document_id: str | None = None,
    related_normalized_entity_ids: list[str] | None = None,
    warnings: list[str] | None = None,
    original_source_unit_id: str | None = None,
    offsets: dict[str, int] | None = None,
) -> dict[str, Any]:
    redacted_text, redactions = redact_text(text)
    unit_warnings = list(warnings or [])
    if redactions:
        unit_warnings.append(
            WARNINGS.add(
                "text_redacted",
                "warning",
                entity.get("normalized_id"),
                "Detected private or secret-like text was replaced with typed redaction markers.",
            )
        )
    return {
        "source_unit_id": source_unit_id(entity.get("normalized_id", ""), label),
        "normalized_entity_id": entity.get("normalized_id"),
        "related_normalized_entity_ids": related_normalized_entity_ids or [],
        "conversation_id": conversation_id,
        "message_id": message_id,
        "project_id": project_id,
        "document_id": document_id,
        "source_platform": entity.get("source_platform", "claude"),
        "source_export_family": entity.get("source_export_family"),
        "source_unit_type": unit_type,
        "semantic_provenance": semantic_provenance,
        "author_role": author_role,
        "text": redacted_text,
        "character_count": len(redacted_text),
        "estimated_token_count": estimate_tokens(redacted_text),
        "content_hash_sha256": sha256_text(canonical_text(redacted_text, collapse_ws=True)),
        "original_timestamp": entity.get("original_created_at") or entity.get("original_timestamp"),
        "normalized_timestamp": entity.get("normalized_created_at_utc") or entity.get("normalized_timestamp"),
        "source_file": entity.get("source_file"),
        "source_record_pointer": (entity.get("provenance") or {}).get("raw_pointer"),
        "branch_membership_refs": [],
        "extraction_eligibility": policy_for_provenance(semantic_provenance),
        "extraction_policy": POLICY["policy_name"],
        "warnings": unit_warnings,
        "redactions": redactions,
        "parent_source_unit_id": original_source_unit_id,
        "source_text_offsets": offsets,
    }


def make_excluded(
    *,
    entity: dict[str, Any],
    label: str,
    unit_type: str,
    reason: str,
    character_count: int = 0,
    content_hash: str | None = None,
    policy_dependent: bool = True,
    scope: str = "policy",
    related_normalized_entity_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "excluded_unit_id": excluded_unit_id(entity.get("normalized_id", ""), label),
        "normalized_source_reference": entity.get("normalized_id"),
        "related_normalized_entity_ids": related_normalized_entity_ids or [],
        "unit_type": unit_type,
        "exclusion_reason": reason,
        "character_count": character_count,
        "content_hash_sha256": content_hash,
        "source_file": entity.get("source_file"),
        "source_record_pointer": (entity.get("provenance") or {}).get("raw_pointer"),
        "exclusion_scope": scope,
        "policy_dependent": policy_dependent,
    }


def remove_thinking_hash_collisions(
    source_units: list[dict[str, Any]],
    excluded: list[dict[str, Any]],
    thinking_hashes: set[str],
    units_by_message: dict[str, list[str]],
    project_units: dict[str, list[str]],
    conversation_title_units: dict[str, list[str]],
) -> list[dict[str, Any]]:
    if not thinking_hashes:
        return source_units
    keep = []
    removed_ids = set()
    for unit in source_units:
        if unit.get("content_hash_sha256") in thinking_hashes:
            removed_ids.add(unit["source_unit_id"])
            excluded.append(
                {
                    "excluded_unit_id": excluded_unit_id(unit["normalized_entity_id"], f"thinking_hash_collision:{unit['source_unit_id']}"),
                    "normalized_source_reference": unit["normalized_entity_id"],
                    "related_normalized_entity_ids": unit.get("related_normalized_entity_ids") or [],
                    "unit_type": unit["source_unit_type"],
                    "exclusion_reason": "model_internal_reasoning_not_project_knowledge",
                    "character_count": unit["character_count"],
                    "content_hash_sha256": unit["content_hash_sha256"],
                    "source_file": unit["source_file"],
                    "source_record_pointer": unit["source_record_pointer"],
                    "exclusion_scope": "permanent",
                    "policy_dependent": False,
                }
            )
        else:
            keep.append(unit)
    if removed_ids:
        WARNINGS.add(
            "thinking_hash_collision_excluded",
            "warning",
            None,
            "One or more candidate source units matched a known thinking-block content hash and were excluded conservatively.",
        )
    for mapping in (units_by_message, project_units, conversation_title_units):
        for key, unit_ids in list(mapping.items()):
            mapping[key] = [unit_id for unit_id in unit_ids if unit_id not in removed_ids]
    return keep


def message_unit_type(message: dict[str, Any]) -> str:
    role = message.get("role")
    family = message.get("source_export_family")
    if family == "design_chats":
        return "design_chat_user_text" if role == "user" else "design_chat_assistant_text"
    return "user_message_text" if role in ("human", "user") else "assistant_message_text"


def block_unit_type(block: dict[str, Any], role: str | None) -> str:
    if block.get("block_type") == "text":
        return "user_message_text" if role in ("human", "user") else "assistant_text_block"
    if block.get("block_type") in ("tool_use", "tool_call"):
        return "tool_input"
    if block.get("block_type") == "tool_result":
        return "tool_output"
    return "structural_metadata"


def source_units_from_messages(
    messages: list[dict[str, Any]],
    blocks_by_message: dict[str, list[dict[str, Any]]],
    source_units: list[dict[str, Any]],
    excluded: list[dict[str, Any]],
) -> dict[str, list[str]]:
    units_by_message: dict[str, list[str]] = defaultdict(list)
    for message in messages:
        msg_id = message["normalized_id"]
        text_blocks = [b for b in blocks_by_message.get(msg_id, []) if b.get("block_type") == "text"]
        block_texts = [b.get("content_text") or "" for b in text_blocks if b.get("content_text")]
        direct_text = message.get("direct_text") or ""
        combined_blocks = "\n\n".join(block_texts)
        direct_norm = canonical_text(direct_text)
        blocks_norm = canonical_text(combined_blocks)
        related_block_ids = [b["normalized_id"] for b in text_blocks]
        role = message.get("role")
        semantic = "user_statement" if role in ("human", "user") else "assistant_output"

        if direct_norm and blocks_norm and direct_norm == blocks_norm:
            RECONCILIATION_COUNTS["exact_match"] += 1
            unit = make_source_unit(
                entity=message,
                label="message_text",
                text=direct_text,
                unit_type=message_unit_type(message),
                semantic_provenance=semantic,
                author_role=role,
                conversation_id=message.get("conversation_normalized_id"),
                message_id=msg_id,
                related_normalized_entity_ids=related_block_ids,
            )
            source_units.append(unit)
            units_by_message[msg_id].append(unit["source_unit_id"])
            for block in text_blocks:
                excluded.append(
                    make_excluded(
                        entity=block,
                        label="redundant_text_block",
                        unit_type=block_unit_type(block, role),
                        reason="exact_redundant_representation",
                        character_count=block.get("content_char_count") or 0,
                        content_hash=block.get("content_sha256"),
                        related_normalized_entity_ids=[msg_id],
                    )
                )
        elif direct_norm and blocks_norm:
            ratio = SequenceMatcher(None, direct_norm, blocks_norm).ratio()
            warning_type = "direct_text_content_block_partial_match" if ratio >= POLICY["direct_text_reconciliation"]["partial_match_threshold"] else "direct_text_content_block_mismatch"
            RECONCILIATION_COUNTS["partial_match" if ratio >= POLICY["direct_text_reconciliation"]["partial_match_threshold"] else "mismatch"] += 1
            warning_id = WARNINGS.add(
                warning_type,
                "warning",
                msg_id,
                "Direct message text and combined text-block content differ; both representations were preserved.",
            )
            direct_unit = make_source_unit(
                entity=message,
                label="message_text",
                text=direct_text,
                unit_type=message_unit_type(message),
                semantic_provenance=semantic,
                author_role=role,
                conversation_id=message.get("conversation_normalized_id"),
                message_id=msg_id,
                related_normalized_entity_ids=related_block_ids,
                warnings=[warning_id],
            )
            source_units.append(direct_unit)
            units_by_message[msg_id].append(direct_unit["source_unit_id"])
            for block in text_blocks:
                block_unit = make_source_unit(
                    entity=block,
                    label=f"text_block_{block.get('block_index')}",
                    text=block.get("content_text") or "",
                    unit_type=block_unit_type(block, role),
                    semantic_provenance=semantic,
                    author_role=role,
                    conversation_id=message.get("conversation_normalized_id"),
                    message_id=msg_id,
                    related_normalized_entity_ids=[msg_id],
                    warnings=[warning_id],
                )
                source_units.append(block_unit)
                units_by_message[msg_id].append(block_unit["source_unit_id"])
        elif direct_norm:
            RECONCILIATION_COUNTS["direct_text_only"] += 1
            unit = make_source_unit(
                entity=message,
                label="message_text",
                text=direct_text,
                unit_type=message_unit_type(message),
                semantic_provenance=semantic,
                author_role=role,
                conversation_id=message.get("conversation_normalized_id"),
                message_id=msg_id,
            )
            source_units.append(unit)
            units_by_message[msg_id].append(unit["source_unit_id"])
        elif blocks_norm:
            RECONCILIATION_COUNTS["content_block_text_only"] += 1
            for block in text_blocks:
                block_unit = make_source_unit(
                    entity=block,
                    label=f"text_block_{block.get('block_index')}",
                    text=block.get("content_text") or "",
                    unit_type=block_unit_type(block, role),
                    semantic_provenance=semantic,
                    author_role=role,
                    conversation_id=message.get("conversation_normalized_id"),
                    message_id=msg_id,
                    related_normalized_entity_ids=[msg_id],
                )
                source_units.append(block_unit)
                units_by_message[msg_id].append(block_unit["source_unit_id"])
        else:
            excluded.append(
                make_excluded(
                    entity=message,
                    label="empty_message_text",
                    unit_type=message_unit_type(message),
                    reason="empty_content",
                    policy_dependent=False,
                    scope="permanent",
                )
            )

        for block in blocks_by_message.get(msg_id, []):
            block_type = block.get("block_type")
            if block_type == "thinking":
                excluded.append(
                    make_excluded(
                        entity=block,
                        label=f"thinking_{block.get('block_index')}",
                        unit_type="thinking_block",
                        reason="model_internal_reasoning_not_project_knowledge",
                        character_count=block.get("content_char_count") or 0,
                        content_hash=block.get("content_sha256"),
                        policy_dependent=False,
                        scope="permanent",
                    )
                )
            elif block_type == "token_budget":
                excluded.append(
                    make_excluded(
                        entity=block,
                        label=f"token_budget_{block.get('block_index')}",
                        unit_type="token_budget",
                        reason="token_budget_metadata",
                        policy_dependent=False,
                        scope="permanent",
                    )
                )
            elif block_type in ("tool_use", "tool_call"):
                tool_text = ""
                if block.get("tool_name") or block.get("input_type"):
                    tool_text = f"tool_name={block.get('tool_name') or ''}\ninput_type={block.get('input_type') or 'unknown'}\ninput_key_count={block.get('input_key_count') if block.get('input_key_count') is not None else ''}"
                if tool_text.strip():
                    unit = make_source_unit(
                        entity=block,
                        label=f"tool_input_{block.get('block_index')}",
                        text=tool_text,
                        unit_type="tool_input",
                        semantic_provenance="tool_input",
                        author_role="assistant",
                        conversation_id=message.get("conversation_normalized_id"),
                        message_id=msg_id,
                        related_normalized_entity_ids=[msg_id],
                    )
                    source_units.append(unit)
                    units_by_message[msg_id].append(unit["source_unit_id"])
                else:
                    excluded.append(
                        make_excluded(
                            entity=block,
                            label=f"tool_input_{block.get('block_index')}",
                            unit_type="tool_input",
                            reason="structural_only",
                        )
                    )
            elif block_type == "tool_result":
                excluded.append(
                    make_excluded(
                        entity=block,
                        label=f"tool_result_{block.get('block_index')}",
                        unit_type="tool_output",
                        reason="unsupported_content_type",
                        character_count=block.get("content_char_count") or 0,
                        content_hash=block.get("content_sha256"),
                    )
                )
    return units_by_message


def add_project_units(projects: list[dict[str, Any]], docs: list[dict[str, Any]], source_units: list[dict[str, Any]], excluded: list[dict[str, Any]]) -> dict[str, list[str]]:
    units_by_project: dict[str, list[str]] = defaultdict(list)
    for project in projects:
        project_id = project["normalized_id"]
        for field, unit_type in (("name", "project_title"), ("description", "project_description"), ("prompt_template", "project_prompt_template")):
            text = project.get(field) or ""
            if text.strip():
                unit = make_source_unit(
                    entity=project,
                    label=field,
                    text=text,
                    unit_type=unit_type,
                    semantic_provenance="project_metadata",
                    author_role=None,
                    project_id=project_id,
                )
                source_units.append(unit)
                units_by_project[project_id].append(unit["source_unit_id"])
            else:
                excluded.append(
                    make_excluded(
                        entity=project,
                        label=f"empty_{field}",
                        unit_type=unit_type,
                        reason="empty_content",
                        policy_dependent=False,
                        scope="permanent",
                    )
                )
    for doc in docs:
        text = doc.get("content") or ""
        if text.strip():
            project_id = doc.get("parent_project_normalized_id")
            unit = make_source_unit(
                entity=doc,
                label="document_content",
                text=text,
                unit_type="project_document",
                semantic_provenance="project_document",
                author_role=None,
                project_id=project_id,
                document_id=doc.get("normalized_id"),
            )
            source_units.append(unit)
            units_by_project[project_id].append(unit["source_unit_id"])
        else:
            excluded.append(
                make_excluded(
                    entity=doc,
                    label="empty_document",
                    unit_type="project_document",
                    reason="empty_content",
                    policy_dependent=False,
                    scope="permanent",
                )
            )
    return units_by_project


def add_attachment_units(attachments: list[dict[str, Any]], source_units: list[dict[str, Any]], excluded: list[dict[str, Any]]) -> dict[str, list[str]]:
    units_by_message: dict[str, list[str]] = defaultdict(list)
    for attachment in attachments:
        text = attachment.get("extracted_content") or ""
        msg_id = attachment.get("parent_message_normalized_id")
        if text.strip():
            unit = make_source_unit(
                entity=attachment,
                label="attachment_text",
                text=text,
                unit_type="attachment_extracted_text",
                semantic_provenance="attachment_text",
                author_role=None,
                message_id=msg_id,
                conversation_id=None,
            )
            source_units.append(unit)
            units_by_message[msg_id].append(unit["source_unit_id"])
        else:
            excluded.append(
                make_excluded(
                    entity=attachment,
                    label="empty_attachment_text",
                    unit_type="attachment_extracted_text",
                    reason="empty_content",
                    policy_dependent=False,
                    scope="permanent",
                )
            )
    return units_by_message


def add_conversation_title_units(conversations: list[dict[str, Any]], source_units: list[dict[str, Any]], excluded: list[dict[str, Any]]) -> dict[str, list[str]]:
    units_by_conversation: dict[str, list[str]] = defaultdict(list)
    for conversation in conversations:
        title = conversation.get("title") or ""
        if title.strip():
            unit = make_source_unit(
                entity=conversation,
                label="conversation_title",
                text=title,
                unit_type="conversation_title",
                semantic_provenance="conversation_metadata",
                author_role=None,
                conversation_id=conversation.get("normalized_id"),
            )
            source_units.append(unit)
            units_by_conversation[conversation.get("normalized_id")].append(unit["source_unit_id"])
        else:
            excluded.append(
                make_excluded(
                    entity=conversation,
                    label="empty_title",
                    unit_type="conversation_title",
                    reason="empty_content",
                    policy_dependent=False,
                    scope="permanent",
                )
            )
    return units_by_conversation


def common_prefix_length(paths: list[list[str]], path: list[str]) -> int:
    if len(paths) <= 1 or not path:
        return 0
    max_prefix = 0
    for other in paths:
        if other == path:
            continue
        prefix = 0
        for left, right in zip(path, other):
            if left != right:
                break
            prefix += 1
        max_prefix = max(max_prefix, prefix)
    return max_prefix


def build_paths(branches: list[dict[str, Any]], units_by_message: dict[str, list[str]], messages_by_id: dict[str, dict[str, Any]], source_units_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    branches_by_conversation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for branch in branches:
        branches_by_conversation[branch.get("conversation_normalized_id")].append(branch)

    paths: list[dict[str, Any]] = []
    for conversation_id, conversation_branches in sorted(branches_by_conversation.items()):
        message_paths = [b.get("ordered_message_normalized_ids") or [] for b in conversation_branches]
        for index, branch in enumerate(sorted(conversation_branches, key=lambda b: b.get("normalized_id") or "")):
            ordered_messages = branch.get("ordered_message_normalized_ids") or []
            ordered_units: list[str] = []
            timestamps = []
            for msg_id in ordered_messages:
                ordered_units.extend(units_by_message.get(msg_id, []))
                ts = messages_by_id.get(msg_id, {}).get("normalized_created_at_utc")
                if ts:
                    timestamps.append(ts)
            path_id = f"stage3:conversation_path:{sha256_text((branch.get('normalized_id') or '') + ':' + str(index))[:32]}"
            shared_prefix_len = common_prefix_length(message_paths, ordered_messages)
            path_record = {
                "conversation_path_id": path_id,
                "source_branch_id": branch.get("normalized_id"),
                "conversation_id": conversation_id,
                "root_message_id": ordered_messages[0] if ordered_messages else None,
                "leaf_message_id": ordered_messages[-1] if ordered_messages else None,
                "ordered_message_ids": ordered_messages,
                "ordered_source_unit_ids": ordered_units,
                "shared_prefix_length": shared_prefix_len,
                "shared_prefix_reference": ordered_messages[:shared_prefix_len] if shared_prefix_len else [],
                "path_length": len(ordered_messages),
                "start_timestamp": min(timestamps) if timestamps else None,
                "end_timestamp": max(timestamps) if timestamps else None,
                "branch_warnings": branch.get("warnings") or [],
            }
            paths.append(path_record)
            for unit_id in ordered_units:
                if unit_id in source_units_by_id:
                    source_units_by_id[unit_id]["branch_membership_refs"].append(path_id)
    return paths


def classify_complexity(profile: dict[str, Any]) -> tuple[str, list[str]]:
    cfg = POLICY["conversation_complexity"]
    reasons = []
    level = "low"
    if profile["message_count"] >= cfg["large_message_threshold"]:
        level = "medium"
        reasons.append("message_count_large")
    if profile["branch_count"] >= cfg["medium_branch_threshold"]:
        level = max(level, "medium", key=["low", "medium", "high", "extreme"].index)
        reasons.append("branched_conversation")
    if profile["tool_call_count"] >= cfg["tool_heavy_threshold"]:
        level = "high"
        reasons.append("tool_heavy")
    if profile["message_count"] >= cfg["extreme_message_threshold"] or profile["branch_count"] >= cfg["high_branch_threshold"] or profile["eligible_character_count_total"] >= cfg["large_character_threshold"]:
        level = "high"
        reasons.append("high_volume_or_branching")
    if profile["branch_count"] >= cfg["extreme_branch_threshold"] or profile["eligible_character_count_total"] >= cfg["extreme_character_threshold"]:
        level = "extreme"
        reasons.append("extreme_volume_or_branching")
    if not reasons:
        reasons.append("below_complexity_thresholds")
    return level, sorted(set(reasons))


def build_profiles(conversations: list[dict[str, Any]], messages: list[dict[str, Any]], blocks: list[dict[str, Any]], source_units: list[dict[str, Any]], paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    messages_by_conversation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for message in messages:
        if message.get("source_export_family") == "conversations":
            messages_by_conversation[message.get("conversation_normalized_id")].append(message)
    blocks_by_conversation = Counter(b.get("conversation_normalized_id") for b in blocks if b.get("block_type") in ("tool_use", "tool_call"))
    units_by_conversation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in source_units:
        if unit.get("conversation_id"):
            units_by_conversation[unit["conversation_id"]].append(unit)
    paths_by_conversation = Counter(p.get("conversation_id") for p in paths)
    profiles = []
    for conv in conversations:
        conv_id = conv["normalized_id"]
        conv_messages = messages_by_conversation.get(conv_id, [])
        prov_chars: Counter = Counter()
        for unit in units_by_conversation.get(conv_id, []):
            if unit.get("extraction_eligibility") in (True, "conditional"):
                prov_chars[unit["semantic_provenance"]] += unit["character_count"]
        profile = {
            "conversation_id": conv_id,
            "title": conv.get("title") or "",
            "title_missing": conv.get("title_missing"),
            "source_export_family": conv.get("source_export_family"),
            "created_at": conv.get("normalized_created_at_utc"),
            "updated_at": conv.get("normalized_updated_at_utc"),
            "message_count": conv.get("message_count") or len(conv_messages),
            "user_message_count": sum(1 for m in conv_messages if m.get("role") in ("human", "user")),
            "assistant_message_count": sum(1 for m in conv_messages if m.get("role") == "assistant"),
            "tool_call_count": blocks_by_conversation[conv_id],
            "attachment_count": sum(m.get("attachment_count") or 0 for m in conv_messages),
            "source_unit_count": len(units_by_conversation.get(conv_id, [])),
            "eligible_character_count_by_provenance": dict(sorted(prov_chars.items())),
            "eligible_character_count_total": sum(prov_chars.values()),
            "branch_count": paths_by_conversation[conv_id],
            "root_count": conv.get("root_message_count"),
            "leaf_count": conv.get("leaf_message_count"),
            "empty": conv.get("empty_conversation"),
            "large_conversation": (conv.get("message_count") or 0) >= POLICY["conversation_complexity"]["large_message_threshold"],
        }
        complexity, reasons = classify_complexity(profile)
        profile["candidate_extraction_complexity"] = complexity
        profile["complexity_reasons"] = reasons
        profiles.append(profile)
    return profiles


def line_fingerprints(text: str) -> set[str]:
    lines = [canonical_text(line, collapse_ws=True) for line in text.splitlines()]
    return {sha256_text(line)[:16] for line in lines if len(line) >= 40}


def build_duplicates(source_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    exact_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in source_units:
        key = sha256_text(canonical_text(unit["text"], collapse_ws=True))
        exact_buckets[key].append(unit)

    groups: list[dict[str, Any]] = []
    exact_members: set[str] = set()
    for key, members in sorted(exact_buckets.items()):
        if len(members) < 2:
            continue
        member_ids = sorted(m["source_unit_id"] for m in members)
        exact_members.update(member_ids)
        prov = Counter(m["semantic_provenance"] for m in members)
        convs = {m.get("conversation_id") for m in members if m.get("conversation_id")}
        groups.append(
            {
                "duplicate_group_id": duplicate_group_id("exact", key),
                "duplicate_type": "exact",
                "member_source_unit_ids": member_ids,
                "canonical_source_unit_id": member_ids[0],
                "similarity_score": 1.0,
                "provenance_distribution": dict(sorted(prov.items())),
                "crosses_conversations": len(convs) > 1,
                "crosses_provenance_types": len(prov) > 1,
                "recommended_later_handling": "Preserve all occurrences; consider one canonical text with occurrence-level provenance during semantic extraction.",
            }
        )

    fp_buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    max_compare_chars = POLICY["duplicate_detection"]["near_exact_max_compare_characters"]
    max_bucket_size = POLICY["duplicate_detection"]["near_exact_max_bucket_size"]
    for unit in source_units:
        if (
            unit["source_unit_id"] in exact_members
            or unit["character_count"] < POLICY["duplicate_detection"]["near_exact_min_characters"]
            or unit["character_count"] > max_compare_chars
        ):
            continue
        for fp in sorted(line_fingerprints(unit["text"]))[:10]:
            fp_buckets[fp].append(unit)

    seen_pairs: set[tuple[str, str]] = set()
    near_edges: dict[str, set[str]] = defaultdict(set)
    scores: dict[tuple[str, str], float] = {}
    min_similarity = POLICY["duplicate_detection"]["near_exact_min_similarity"]
    max_ratio = POLICY["duplicate_detection"]["near_exact_max_length_ratio"]
    for bucket in fp_buckets.values():
        if len(bucket) < 2 or len(bucket) > max_bucket_size:
            continue
        sorted_bucket = sorted(bucket, key=lambda u: u["source_unit_id"])
        for i, left in enumerate(sorted_bucket):
            for right in sorted_bucket[i + 1 :]:
                pair = (left["source_unit_id"], right["source_unit_id"])
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                l_len = max(left["character_count"], 1)
                r_len = max(right["character_count"], 1)
                if max(l_len, r_len) / min(l_len, r_len) > max_ratio:
                    continue
                left_text = canonical_text(left["text"], collapse_ws=True)
                right_text = canonical_text(right["text"], collapse_ws=True)
                matcher = SequenceMatcher(None, left_text, right_text)
                if matcher.quick_ratio() < min_similarity:
                    continue
                similarity = matcher.ratio()
                if similarity >= min_similarity and left["content_hash_sha256"] != right["content_hash_sha256"]:
                    near_edges[left["source_unit_id"]].add(right["source_unit_id"])
                    near_edges[right["source_unit_id"]].add(left["source_unit_id"])
                    scores[pair] = similarity

    visited: set[str] = set()
    units_by_id = {u["source_unit_id"]: u for u in source_units}
    for unit_id in sorted(near_edges):
        if unit_id in visited:
            continue
        stack = [unit_id]
        component = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(near_edges[current] - visited))
        if len(component) < 2:
            continue
        members = [units_by_id[mid] for mid in sorted(component)]
        prov = Counter(m["semantic_provenance"] for m in members)
        convs = {m.get("conversation_id") for m in members if m.get("conversation_id")}
        component_scores = [score for pair, score in scores.items() if pair[0] in component and pair[1] in component]
        groups.append(
            {
                "duplicate_group_id": duplicate_group_id("near_exact", "|".join(sorted(component))),
                "duplicate_type": "near_exact",
                "member_source_unit_ids": sorted(component),
                "canonical_source_unit_id": sorted(component)[0],
                "similarity_score": round(min(component_scores), 4) if component_scores else None,
                "provenance_distribution": dict(sorted(prov.items())),
                "crosses_conversations": len(convs) > 1,
                "crosses_provenance_types": len(prov) > 1,
                "recommended_later_handling": "Review before consolidation; near-exact text may include quoted context or revised drafts.",
            }
        )
    return sorted(groups, key=lambda g: g["duplicate_group_id"])


def split_oversized_unit(unit: dict[str, Any]) -> list[dict[str, Any]]:
    max_chars = POLICY["packet_limits"]["maximum_characters"]
    if unit["character_count"] <= max_chars:
        return [unit]
    text = unit["text"]
    parts: list[tuple[int, int, str]] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            window = text[start:end]
            split = window.rfind("\n\n")
            if split > max_chars // 2:
                end = start + split + 2
        part_text = text[start:end]
        parts.append((start, end, part_text))
        start = end
    subunits = []
    for index, (start, end, part_text) in enumerate(parts):
        entity = {
            "normalized_id": unit["normalized_entity_id"],
            "source_platform": unit["source_platform"],
            "source_export_family": unit["source_export_family"],
            "source_file": unit["source_file"],
            "provenance": {"raw_pointer": unit["source_record_pointer"]},
            "original_created_at": unit["original_timestamp"],
            "normalized_created_at_utc": unit["normalized_timestamp"],
        }
        subunit = make_source_unit(
            entity=entity,
            label=f"{unit['source_unit_id']}:subunit:{index:04d}",
            text=part_text,
            unit_type=unit["source_unit_type"],
            semantic_provenance=unit["semantic_provenance"],
            author_role=unit["author_role"],
            conversation_id=unit["conversation_id"],
            message_id=unit["message_id"],
            project_id=unit["project_id"],
            document_id=unit["document_id"],
            related_normalized_entity_ids=unit.get("related_normalized_entity_ids") or [],
            warnings=unit.get("warnings") or [],
            original_source_unit_id=unit["source_unit_id"],
            offsets={"start": start, "end": end},
        )
        subunit["branch_membership_refs"] = list(unit.get("branch_membership_refs") or [])
        subunits.append(subunit)
    return subunits


def packetize_units(scope: str, units: list[dict[str, Any]], conversation_path_id: str | None = None, conversation_id: str | None = None, project_id: str | None = None) -> list[dict[str, Any]]:
    max_tokens = POLICY["packet_limits"]["maximum_estimated_tokens"]
    target_tokens = POLICY["packet_limits"]["target_estimated_tokens"]
    packets: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_tokens = 0

    def flush() -> None:
        nonlocal current, current_tokens
        if not current:
            return
        index = len(packets)
        unit_ids = [u["source_unit_id"] for u in current]
        prov = Counter(u["semantic_provenance"] for u in current)
        timestamps = [u["normalized_timestamp"] for u in current if u.get("normalized_timestamp")]
        warnings = []
        if any(u.get("parent_source_unit_id") for u in current):
            warnings.append("contains_oversized_source_subunit")
        packets.append(
            {
                "packet_id": packet_id(scope, index),
                "conversation_id": conversation_id,
                "project_id": project_id,
                "conversation_path_id": conversation_path_id,
                "ordered_source_unit_ids": unit_ids,
                "primary_eligible_source_unit_ids": [u["source_unit_id"] for u in current if u.get("extraction_eligibility") is True],
                "supporting_context_source_unit_ids": [u["source_unit_id"] for u in current if u.get("extraction_eligibility") == "conditional"],
                "provenance_counts": dict(sorted(prov.items())),
                "character_count": sum(u["character_count"] for u in current),
                "estimated_token_count": sum(u["estimated_token_count"] for u in current),
                "start_timestamp": min(timestamps) if timestamps else None,
                "end_timestamp": max(timestamps) if timestamps else None,
                "overlap_reference": None,
                "previous_packet_id": None,
                "next_packet_id": None,
                "packet_warnings": warnings,
                "extraction_priority": "primary" if any(u.get("extraction_eligibility") is True for u in current) else "supporting",
            }
        )
        current = []
        current_tokens = 0

    for unit in units:
        unit_tokens = unit["estimated_token_count"]
        if current and current_tokens + unit_tokens > target_tokens:
            flush()
        current.append(unit)
        current_tokens += unit_tokens
        if current_tokens >= max_tokens:
            flush()
    flush()
    for index, packet in enumerate(packets):
        if index:
            packet["previous_packet_id"] = packets[index - 1]["packet_id"]
            packet["overlap_reference"] = {
                "type": "previous_packet_tail_reference",
                "packet_id": packets[index - 1]["packet_id"],
                "approximate_overlap_tokens": POLICY["packet_limits"]["context_overlap_estimated_tokens"],
            }
        if index + 1 < len(packets):
            packet["next_packet_id"] = packets[index + 1]["packet_id"]
    return packets


def build_packets(source_units: list[dict[str, Any]], paths: list[dict[str, Any]], project_units: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    units_by_id = {u["source_unit_id"]: u for u in source_units}
    packet_units_by_id: dict[str, dict[str, Any]] = dict(units_by_id)
    packets: list[dict[str, Any]] = []

    for path in paths:
        expanded: list[dict[str, Any]] = []
        for unit_id in path["ordered_source_unit_ids"]:
            unit = units_by_id.get(unit_id)
            if not unit:
                continue
            split_units = split_oversized_unit(unit)
            for split_unit in split_units:
                packet_units_by_id[split_unit["source_unit_id"]] = split_unit
            expanded.extend(split_units)
        packets.extend(
            packetize_units(
                scope=path["conversation_path_id"],
                units=expanded,
                conversation_path_id=path["conversation_path_id"],
                conversation_id=path["conversation_id"],
            )
        )

    for project_id, unit_ids in sorted(project_units.items()):
        expanded = []
        for unit_id in unit_ids:
            unit = units_by_id.get(unit_id)
            if not unit:
                continue
            split_units = split_oversized_unit(unit)
            for split_unit in split_units:
                packet_units_by_id[split_unit["source_unit_id"]] = split_unit
            expanded.extend(split_units)
        packets.extend(packetize_units(scope=project_id, units=expanded, project_id=project_id))

    packet_source_units = sorted(packet_units_by_id.values(), key=lambda u: u["source_unit_id"])
    return packets, packet_source_units


def safe_snippet(text: str, limit: int = 120) -> str:
    snippet = text.replace("\n", " ")
    snippet = re.sub(r"\s+", " ", snippet).strip()
    if len(snippet) > limit:
        return snippet[:limit] + "..."
    return snippet


def build_review_sample(profiles: list[dict[str, Any]], source_units: list[dict[str, Any]], packets: list[dict[str, Any]], duplicates: list[dict[str, Any]]) -> str:
    units_by_conv: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for unit in source_units:
        if unit.get("conversation_id"):
            units_by_conv[unit["conversation_id"]].append(unit)
    packet_by_unit = {}
    for packet in packets:
        for unit_id in packet["ordered_source_unit_ids"]:
            packet_by_unit.setdefault(unit_id, packet["packet_id"])

    selected: list[tuple[str, dict[str, Any]]] = []
    sorted_profiles = sorted(profiles, key=lambda p: (p["message_count"], p["conversation_id"]))
    if sorted_profiles:
        selected.append(("small conversation", sorted_profiles[0]))
        selected.append(("medium conversation", sorted_profiles[len(sorted_profiles) // 2]))
        selected.append(("large conversation", sorted_profiles[-1]))
    branched = [p for p in profiles if p["branch_count"] > 1]
    attached = [p for p in profiles if p["attachment_count"] > 0]
    tool_heavy = [p for p in profiles if p["tool_call_count"] > 0]
    missing_title = [p for p in profiles if p["title_missing"]]
    for label, candidates in (("branched conversation", branched), ("conversation with attachments", attached), ("tool-heavy conversation", tool_heavy), ("missing-title conversation", missing_title)):
        if candidates:
            selected.append((label, sorted(candidates, key=lambda p: p["conversation_id"])[0]))

    lines = ["# Review Sample", ""]
    seen = set()
    for label, profile in selected:
        key = (label, profile["conversation_id"])
        if key in seen:
            continue
        seen.add(key)
        units = units_by_conv.get(profile["conversation_id"], [])[:3]
        lines.extend(
            [
                f"## {label}",
                "",
                f"- Conversation ID: `{profile['conversation_id']}`",
                f"- Messages: {profile['message_count']}",
                f"- Complexity: {profile['candidate_extraction_complexity']}",
                f"- Source units shown: {len(units)}",
            ]
        )
        for unit in units:
            lines.append(f"- `{unit['source_unit_id']}` `{unit['semantic_provenance']}` packet `{packet_by_unit.get(unit['source_unit_id'])}`: {safe_snippet(unit['text'])}")
        lines.append("")

    project_doc = next((u for u in source_units if u["source_unit_type"] == "project_document"), None)
    if project_doc:
        lines.extend(["## project document", "", f"- Source unit: `{project_doc['source_unit_id']}`", f"- Project: `{project_doc['project_id']}`", f"- Snippet: {safe_snippet(project_doc['text'])}", ""])
    design = next((u for u in source_units if u["source_unit_type"].startswith("design_chat_")), None)
    if design:
        lines.extend(["## design chat", "", f"- Source unit: `{design['source_unit_id']}`", f"- Provenance: `{design['semantic_provenance']}`", f"- Snippet: {safe_snippet(design['text'])}", ""])
    if duplicates:
        dup = duplicates[0]
        lines.extend(["## duplicate group", "", f"- Group: `{dup['duplicate_group_id']}`", f"- Type: `{dup['duplicate_type']}`", f"- Members shown: {', '.join('`' + m + '`' for m in dup['member_source_unit_ids'][:5])}", ""])
    return "\n".join(lines)


def write_report(source_units: list[dict[str, Any]], paths: list[dict[str, Any]], packets: list[dict[str, Any]], duplicates: list[dict[str, Any]], excluded: list[dict[str, Any]], checksum_ok: bool) -> None:
    by_type = Counter(u["source_unit_type"] for u in source_units)
    by_prov = Counter(u["semantic_provenance"] for u in source_units)
    elig = Counter(str(u["extraction_eligibility"]) for u in source_units)
    chars_by_prov = Counter()
    tokens_by_prov = Counter()
    for unit in source_units:
        chars_by_prov[unit["semantic_provenance"]] += unit["character_count"]
        tokens_by_prov[unit["semantic_provenance"]] += unit["estimated_token_count"]
    packet_sizes = [p["estimated_token_count"] for p in packets]
    duplicate_counts = Counter(d["duplicate_type"] for d in duplicates)
    excluded_counts = Counter(e["exclusion_reason"] for e in excluded)
    warning_counts = Counter(w["type"] for w in WARNINGS.records)
    oversized = [u for u in source_units if u.get("parent_source_unit_id")]

    lines = [
        "# Extraction Staging Report",
        "",
        f"- Total source units: {len(source_units)}",
        f"- Conversation paths: {len(paths)}",
        f"- Extraction packets: {len(packets)}",
        f"- Checksum result: {checksum_ok}",
        "",
        "## Source Units By Type",
        "",
    ]
    for key, value in sorted(by_type.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Source Units By Provenance", ""])
    for key, value in sorted(by_prov.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Eligibility Counts", ""])
    for key, value in sorted(elig.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Characters And Estimated Tokens By Provenance", ""])
    for key in sorted(chars_by_prov):
        lines.append(f"- `{key}`: {chars_by_prov[key]} chars, {tokens_by_prov[key]} estimated tokens")
    lines.extend(["", "## Packet Size Statistics", ""])
    if packet_sizes:
        lines.extend(
            [
                f"- Min estimated tokens: {min(packet_sizes)}",
                f"- Max estimated tokens: {max(packet_sizes)}",
                f"- Average estimated tokens: {round(sum(packet_sizes) / len(packet_sizes), 2)}",
            ]
        )
    else:
        lines.append("- No packets")
    lines.extend(["", "## Oversized Units", "", f"- Subunits created: {len(oversized)}", "", "## Direct Text / Content Block Reconciliation", ""])
    for key, value in sorted(RECONCILIATION_COUNTS.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Duplicate Groups", ""])
    lines.append(f"- Exact duplicate groups: {duplicate_counts['exact']}")
    lines.append(f"- Near-exact duplicate groups: {duplicate_counts['near_exact']}")
    lines.extend(["", "## Redaction Counts", ""])
    for key, value in sorted(REDACTION_COUNTS.items()):
        lines.append(f"- `{key}`: {value}")
    if not REDACTION_COUNTS:
        lines.append("- None")
    lines.extend(["", "## Excluded Content Counts", ""])
    for key, value in sorted(excluded_counts.items()):
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Warnings", ""])
    for key, value in sorted(warning_counts.items()):
        lines.append(f"- `{key}`: {value}")
    if not warning_counts:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Known Limitations",
            "",
            "- Tool result bodies that were not copied into Stage 2 normalized text cannot be reconstructed in Stage 3.",
            "- Near-duplicate detection is conservative and intentionally avoids broad semantic paraphrase detection.",
            "- This stage does not infer topics, projects, decisions, or final database structure.",
            "",
            "## Recommendation For The Next Stage",
            "",
            "Use the source units and packets as the only extraction input, applying provenance-specific rules so user statements, assistant output, project documents, attachments, and tool records remain separate evidence streams.",
            "",
        ]
    )
    tmp = (REPORTS / "extraction_staging_report.md").with_suffix(".md.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, REPORTS / "extraction_staging_report.md")


def main() -> None:
    for directory in (CORPUS, REPORTS, MANIFESTS):
        directory.mkdir(parents=True, exist_ok=True)

    before = checksum_manifest()
    write_json(MANIFESTS / "normalized_checksums_before.json", before)

    data = {name: load_jsonl(path) for name, path in NORMALIZED_FILES.items()}
    messages = data["messages"]
    blocks = data["content_blocks"]
    blocks_by_message: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in blocks:
        blocks_by_message[block.get("message_normalized_id")].append(block)

    source_units: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    units_by_message = source_units_from_messages(messages, blocks_by_message, source_units, excluded)
    attachment_units = add_attachment_units(data["attachments"], source_units, excluded)
    for msg_id, unit_ids in attachment_units.items():
        units_by_message[msg_id].extend(unit_ids)
    project_units = add_project_units(data["projects"], data["project_documents"], source_units, excluded)
    conversation_title_units = add_conversation_title_units(data["conversations"], source_units, excluded)
    thinking_hashes = {block.get("content_sha256") for block in blocks if block.get("block_type") == "thinking" and block.get("content_sha256")}
    source_units = remove_thinking_hash_collisions(source_units, excluded, thinking_hashes, units_by_message, project_units, conversation_title_units)

    source_units_by_id = {unit["source_unit_id"]: unit for unit in source_units}
    messages_by_id = {message["normalized_id"]: message for message in messages}
    paths = build_paths(data["conversation_branches"], units_by_message, messages_by_id, source_units_by_id)
    for conv_id, unit_ids in conversation_title_units.items():
        for unit_id in unit_ids:
            if unit_id in source_units_by_id:
                source_units_by_id[unit_id]["branch_membership_refs"] = [p["conversation_path_id"] for p in paths if p["conversation_id"] == conv_id]

    profiles = build_profiles(data["conversations"], messages, blocks, list(source_units_by_id.values()), paths)
    duplicates = build_duplicates(list(source_units_by_id.values()))
    packets, packet_source_units = build_packets(list(source_units_by_id.values()), paths, project_units)
    # Packet subunits are extraction corpus units too.
    source_units = packet_source_units
    duplicates = build_duplicates(source_units)

    after = checksum_manifest()
    checksum_ok = before == after

    write_jsonl(CORPUS_FILES["source_units"], sorted(source_units, key=lambda u: u["source_unit_id"]))
    write_jsonl(CORPUS_FILES["conversation_paths"], sorted(paths, key=lambda p: p["conversation_path_id"]))
    write_jsonl(CORPUS_FILES["extraction_packets"], sorted(packets, key=lambda p: p["packet_id"]))
    write_jsonl(CORPUS_FILES["conversation_profiles"], sorted(profiles, key=lambda p: p["conversation_id"]))
    write_jsonl(CORPUS_FILES["duplicate_groups"], duplicates)
    write_jsonl(CORPUS_FILES["excluded_units"], sorted(excluded, key=lambda e: e["excluded_unit_id"]))
    write_jsonl(REPORTS / "warnings.jsonl", WARNINGS.records)
    write_json(MANIFESTS / "normalized_checksums_after.json", after)
    write_report(source_units, paths, packets, duplicates, excluded, checksum_ok)
    review = build_review_sample(profiles, source_units, packets, duplicates)
    tmp = (REPORTS / "review_sample.md").with_suffix(".md.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(review)
        fh.write("\n")
    os.replace(tmp, REPORTS / "review_sample.md")

    print(
        json.dumps(
            {
                "status": "ok",
                "source_units": len(source_units),
                "conversation_paths": len(paths),
                "packets": len(packets),
                "duplicate_groups": len(duplicates),
                "excluded_units": len(excluded),
                "warnings": len(WARNINGS.records),
                "normalized_checksums_unchanged": checksum_ok,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
