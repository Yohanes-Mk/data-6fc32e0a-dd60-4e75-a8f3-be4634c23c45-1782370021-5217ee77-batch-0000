#!/usr/bin/env python3
"""Build Stage 3R-P provenance metadata patch artifacts."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PATCH = ROOT / "context_pipeline" / "provenance_patch"
FLEET_CONVERSATION_ID = "claude:conversations:conversation:e2fc5641-6bd8-41c3-80d2-1e1e71b1e491"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def normalize_filename(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "|".join("" if p is None else str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:32]}"


def all_non_patch_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[:2] == ("context_pipeline", "provenance_patch"):
            continue
        files.append(path)
    return sorted(files)


def checksums() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in all_non_patch_files():
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def load_stage_indexes() -> dict[str, Any]:
    normalized = ROOT / "context_pipeline" / "normalized"
    stage3r = ROOT / "context_pipeline" / "extraction_staging_repair"
    merged = ROOT / "context_pipeline" / "semantic_pilot_merged"

    messages = read_jsonl(normalized / "messages.jsonl")
    attachments = read_jsonl(normalized / "attachments.jsonl")
    attachment_links = read_jsonl(stage3r / "corpus" / "attachment_links.jsonl")
    source_containers = read_jsonl(stage3r / "corpus" / "source_containers.jsonl")
    packets = read_jsonl(stage3r / "corpus" / "extraction_packets.jsonl")
    evidence_maps = read_jsonl(stage3r / "corpus" / "conversation_evidence_maps.jsonl")
    merged_bundles = read_jsonl(merged / "evidence_bundles" / "semantic_evidence_bundles.jsonl")
    candidates = read_jsonl(merged / "results" / "candidate_entities.jsonl")
    candidate_evidence = read_jsonl(merged / "results" / "candidate_evidence.jsonl")
    case_extractions = read_jsonl(merged / "results" / "case_extractions.jsonl")

    return {
        "messages_by_id": {m.get("normalized_id"): m for m in messages},
        "attachments_by_id": {a.get("normalized_id"): a for a in attachments},
        "attachment_links": attachment_links,
        "containers_by_entity_id": {
            c.get("normalized_entity_id"): c
            for c in source_containers
            if c.get("container_type") == "attachment"
        },
        "attachment_packets_by_link_id": {
            p.get("attachment_link_id"): p
            for p in packets
            if p.get("packet_type") == "attachment_evidence"
        },
        "evidence_maps": evidence_maps,
        "merged_bundles": merged_bundles,
        "candidates_by_id": {c.get("candidate_id"): c for c in candidates},
        "candidate_evidence_by_id": group_by(candidate_evidence, "candidate_id"),
        "case_extractions_by_id": {c.get("case_id"): c for c in case_extractions},
    }


def group_by(records: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get(key))].append(record)
    return grouped


def build_confirmed_resolutions(indexes: dict[str, Any]) -> dict[str, Any]:
    candidate_evidence = indexes["candidate_evidence_by_id"]
    candidates = indexes["candidates_by_id"]
    cases = indexes["case_extractions_by_id"]

    client_evidence_refs = []
    for candidate_id in ("mc:cand:m08_client_radar_a11y", "mc:cand:m09_client_radar_repo"):
        client_evidence_refs.extend(candidate_evidence.get(candidate_id, []))

    return {
        "resolution_set_id": "stage3rp:confirmed_resolutions:001",
        "source": "direct_human_resolution_stage3rp",
        "resolutions": [
            {
                "resolution_id": "stage3rp:resolution:client_radar",
                "related_candidate_ids": [
                    "mc:cand:m08_client_radar_a11y",
                    "mc:cand:m09_client_radar_repo",
                ],
                "canonical_entity_id": "stage3rp:entity:client_radar_accenture_engagement",
                "canonical_title": "Client Radar accessibility and repository implementation engagement",
                "project_owner": "user",
                "organizational_context": "Accenture",
                "engagement_type": "client_engagement",
                "status": "active",
                "facets": [
                    {
                        "facet_id": "stage3rp:facet:client_radar_accessibility_audit_design",
                        "label": "accessibility audit/design",
                        "source_candidate_id": "mc:cand:m08_client_radar_a11y",
                    },
                    {
                        "facet_id": "stage3rp:facet:client_radar_repository_implementation",
                        "label": "repository implementation",
                        "source_candidate_id": "mc:cand:m09_client_radar_repo",
                    },
                ],
                "content_authorship": {
                    "user_contribution": True,
                    "assistant_contribution": True,
                    "authorship_classification": "co_authored",
                    "note": "The engagement is user-owned, while the accessibility audit/report content was collaboratively developed with Claude.",
                },
                "transport_author": {
                    "m08": candidates.get("mc:cand:m08_client_radar_a11y", {}).get("transport_author_roles", []),
                    "m09": candidates.get("mc:cand:m09_client_radar_repo", {}).get("transport_author_roles", []),
                },
                "content_origin": {
                    "m08_prior": candidates.get("mc:cand:m08_client_radar_a11y", {}).get("content_origins", []),
                    "m09_prior": candidates.get("mc:cand:m09_client_radar_repo", {}).get("content_origins", []),
                    "patched": "mixed_origin_co_authored",
                },
                "assertion_relationship": {
                    "m08_prior": candidates.get("mc:cand:m08_client_radar_a11y", {}).get("assertion_relationships", []),
                    "m09_prior": candidates.get("mc:cand:m09_client_radar_repo", {}).get("assertion_relationships", []),
                },
                "evidence_references": client_evidence_refs,
                "source_cases": [
                    cases.get("mc-08"),
                    cases.get("mc-09"),
                ],
                "confidence": "high",
                "unresolved_sections": [
                    "Exact sentence-level authorship inside the audit report remains unresolved; treat report assertions as mixed-origin unless directly tied to user-authored evidence."
                ],
                "do_not_merge_with": [
                    "Accenture interview preparation",
                    "Accenture onboarding",
                ],
            },
            {
                "resolution_id": "stage3rp:resolution:avatar_bci",
                "related_candidate_ids": ["mc:cand:m10_avatar_lab"],
                "canonical_entity_id": "stage3rp:entity:avatar_bci_lab_work",
                "entity": "AVATAR/BCI lab work",
                "status": "completed",
                "temporal_status": "historical_confirmed",
                "current_activity": False,
                "evidence_basis": "direct human resolution",
                "evidence_references": candidate_evidence.get("mc:cand:m10_avatar_lab", []),
                "source_case": cases.get("mc-10"),
                "confidence": "high",
                "do_not_delete_historical_entity": True,
            },
        ],
    }


def build_attachment_records(indexes: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attachments_by_id = indexes["attachments_by_id"]
    containers_by_entity_id = indexes["containers_by_entity_id"]
    packets_by_link_id = indexes["attachment_packets_by_link_id"]
    messages_by_id = indexes["messages_by_id"]

    patched: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []

    for link in sorted(indexes["attachment_links"], key=lambda r: r.get("attachment_link_id") or ""):
        attachment_id = link.get("attachment_normalized_id")
        source = attachments_by_id.get(attachment_id, {})
        container = containers_by_entity_id.get(attachment_id, {})
        packet = packets_by_link_id.get(link.get("attachment_link_id"), {})
        parent_message = messages_by_id.get(link.get("parent_message_id"), {})

        original_filename = normalize_filename(source.get("filename"))
        stage3r_filename = normalize_filename(link.get("filename"))
        normalized_filename = original_filename if original_filename is not None else stage3r_filename
        content_hash = container.get("content_hash_sha256")

        trace = {
            "trace_id": stable_id("stage3rp:attachment_filename_trace", link.get("attachment_link_id")),
            "attachment_occurrence_id": link.get("attachment_link_id"),
            "attachment_normalized_id": attachment_id,
            "conversation_id": link.get("conversation_id") or parent_message.get("conversation_normalized_id"),
            "parent_message_id": link.get("parent_message_id"),
            "attachment_index": link.get("attachment_index"),
            "stage2": {
                "filename": original_filename,
                "filename_populated": original_filename is not None,
                "source_record_pointer": source.get("provenance", {}).get("raw_pointer"),
                "normalized_id": source.get("normalized_id"),
            },
            "stage3r_attachment_link": {
                "filename": stage3r_filename,
                "filename_populated": stage3r_filename is not None,
                "attachment_link_id": link.get("attachment_link_id"),
            },
            "stage3r_extraction_packet": {
                "packet_id": packet.get("packet_id"),
                "contains_filename_field": "filename" in packet or "attachment_filename" in packet,
                "filename": normalize_filename(packet.get("filename") or packet.get("attachment_filename")),
            },
            "stage3r_conversation_evidence_map": {
                "available_attachment_reference": True,
                "per_occurrence_filename_available": False,
                "note": "Stage 3R conversation maps retain attachment IDs and aggregate filename counts, not per-occurrence filename metadata.",
            },
            "stage4c_semantic_evidence_bundle": {
                "per_occurrence_filename_available": False,
                "note": "Merged semantic evidence bundles retain aggregate filename counts/samples, not the attachment occurrence filename table.",
            },
            "filename_loss_classification": loss_classification(original_filename, stage3r_filename, packet),
        }
        traces.append(trace)

        patched.append(
            {
                "patched_attachment_link_id": stable_id("stage3rp:attachment_link", link.get("attachment_link_id")),
                "attachment_occurrence_id": link.get("attachment_link_id"),
                "conversation_id": trace["conversation_id"],
                "parent_message_id": link.get("parent_message_id"),
                "attachment_index": link.get("attachment_index"),
                "original_filename": original_filename,
                "normalized_filename": normalized_filename,
                "filename_populated": normalized_filename is not None,
                "file_uuid": source.get("file_uuid") or source.get("uuid"),
                "attachment_normalized_id": attachment_id,
                "mime_or_file_type": source.get("file_type") or link.get("file_type"),
                "reported_size": source.get("reported_size") or link.get("reported_size"),
                "extracted_text_available": bool(source.get("extracted_content_available") or link.get("extracted_text_available")),
                "content_hash": content_hash,
                "binary_present": bool(link.get("binary_present")),
                "missing_binary": bool(link.get("missing_binary")),
                "source_record_pointer": {
                    "normalized_attachment": source.get("provenance", {}).get("raw_pointer"),
                    "stage3r_attachment_link": link.get("attachment_link_id"),
                    "stage3r_packet": packet.get("packet_id"),
                    "stage3r_source_container": container.get("container_id"),
                },
                "stage3r_packet_ids": link.get("packet_ids") or ([packet.get("packet_id")] if packet.get("packet_id") else []),
                "stage3r_repaired_source_unit_ids": link.get("repaired_source_unit_ids", []),
                "provenance_path": [
                    "context_pipeline/normalized/attachments.jsonl",
                    "context_pipeline/extraction_staging_repair/corpus/attachment_links.jsonl",
                    "context_pipeline/extraction_staging_repair/corpus/extraction_packets.jsonl",
                    "context_pipeline/extraction_staging_repair/corpus/conversation_evidence_maps.jsonl",
                    "context_pipeline/provenance_patch/corpus/patched_semantic_evidence_inputs.jsonl",
                ],
            }
        )

    return patched, traces


def loss_classification(original_filename: str | None, stage3r_filename: str | None, packet: dict[str, Any]) -> str:
    packet_has_filename = normalize_filename(packet.get("filename") or packet.get("attachment_filename")) is not None
    if original_filename is None and stage3r_filename is None:
        return "absent_upstream_raw_or_normalized"
    if original_filename is not None and stage3r_filename is None:
        return "lost_between_stage2_and_stage3r_attachment_link"
    if stage3r_filename is not None and not packet_has_filename:
        return "lost_between_stage3r_attachment_link_and_stage3r_extraction_packet"
    return "preserved_to_available_packet_metadata"


def build_patched_conversation_maps(
    indexes: dict[str, Any], patched_attachments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    attachments_by_conversation = group_by(patched_attachments, "conversation_id")
    records: list[dict[str, Any]] = []
    for evidence_map in sorted(indexes["evidence_maps"], key=lambda r: r.get("conversation_id") or ""):
        conversation_id = evidence_map.get("conversation_id")
        attachments = attachments_by_conversation.get(str(conversation_id), [])
        records.append(
            {
                "patched_evidence_map_id": stable_id("stage3rp:conversation_evidence_map", conversation_id),
                "conversation_id": conversation_id,
                "source_stage3r_map": "context_pipeline/extraction_staging_repair/corpus/conversation_evidence_maps.jsonl",
                "stage3r_attachment_ids": evidence_map.get("attachment_ids", []),
                "stage3r_attachment_occurrence_count": evidence_map.get("attachment_occurrence_count", 0),
                "patched_attachment_occurrence_count": len(attachments),
                "filename_populated_occurrences": sum(1 for a in attachments if a["filename_populated"]),
                "attachment_filename_metadata": [
                    {
                        "attachment_occurrence_id": a["attachment_occurrence_id"],
                        "attachment_normalized_id": a["attachment_normalized_id"],
                        "attachment_index": a["attachment_index"],
                        "original_filename": a["original_filename"],
                        "normalized_filename": a["normalized_filename"],
                        "filename_populated": a["filename_populated"],
                        "content_hash": a["content_hash"],
                    }
                    for a in attachments
                ],
                "metadata_patch_note": "Conversation-level overlay only; full Stage 3R evidence map remains immutable source of truth.",
            }
        )
    return records


def build_semantic_inputs(
    patched_attachments: list[dict[str, Any]],
    patched_maps: list[dict[str, Any]],
    resolutions: dict[str, Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for attachment in patched_attachments:
        records.append(
            {
                "semantic_input_id": stable_id("stage3rp:semantic_input:attachment", attachment["attachment_occurrence_id"]),
                "input_type": "attachment_filename_metadata",
                "stage3r_evidence_ids": {
                    "attachment_occurrence_id": attachment["attachment_occurrence_id"],
                    "packet_ids": attachment["stage3r_packet_ids"],
                    "repaired_source_unit_ids": attachment["stage3r_repaired_source_unit_ids"],
                },
                "conversation_id": attachment["conversation_id"],
                "filename_metadata": {
                    "original_filename": attachment["original_filename"],
                    "normalized_filename": attachment["normalized_filename"],
                    "filename_populated": attachment["filename_populated"],
                    "content_hash": attachment["content_hash"],
                    "mime_or_file_type": attachment["mime_or_file_type"],
                    "reported_size": attachment["reported_size"],
                    "binary_present": attachment["binary_present"],
                    "extracted_text_available": attachment["extracted_text_available"],
                },
                "do_not_invent_filename": True,
            }
        )

    fleet_map = next((m for m in patched_maps if m["conversation_id"] == FLEET_CONVERSATION_ID), None)
    if fleet_map:
        records.append(
            {
                "semantic_input_id": "stage3rp:semantic_input:fleet_attachment_filename_overlay",
                "input_type": "conversation_attachment_filename_overlay",
                "conversation_id": FLEET_CONVERSATION_ID,
                "stage3r_evidence_ids": {
                    "attachment_occurrence_ids": [a["attachment_occurrence_id"] for a in fleet_map["attachment_filename_metadata"]],
                },
                "attachment_filename_metadata": fleet_map["attachment_filename_metadata"],
                "do_not_invent_filename": True,
            }
        )

    for resolution in resolutions["resolutions"]:
        records.append(
            {
                "semantic_input_id": stable_id("stage3rp:semantic_input:resolution", resolution["resolution_id"]),
                "input_type": "confirmed_human_resolution",
                "resolution": resolution,
            }
        )
    return records


def attachment_reports(
    patched_attachments: list[dict[str, Any]], traces: list[dict[str, Any]], semantic_inputs: list[dict[str, Any]]
) -> dict[str, Any]:
    fleet = [a for a in patched_attachments if a["conversation_id"] == FLEET_CONVERSATION_ID]
    filenames = [a["normalized_filename"] for a in fleet if a["normalized_filename"]]
    filename_counts = Counter(filenames)
    content_hashes = [a["content_hash"] for a in fleet if a["content_hash"]]
    fleet_input = next(
        (r for r in semantic_inputs if r["semantic_input_id"] == "stage3rp:semantic_input:fleet_attachment_filename_overlay"),
        None,
    )
    loss_counts = Counter(t["filename_loss_classification"] for t in traces)
    return {
        "all_attachments": {
            "total_attachment_occurrences": len(patched_attachments),
            "filename_populated_occurrences": sum(1 for a in patched_attachments if a["filename_populated"]),
            "missing_filename_occurrences": sum(1 for a in patched_attachments if not a["filename_populated"]),
            "unique_filenames": len(set(a["normalized_filename"] for a in patched_attachments if a["normalized_filename"])),
        },
        "fleet_command": {
            "conversation_id": FLEET_CONVERSATION_ID,
            "total_attachment_occurrences": len(fleet),
            "filename_populated_occurrences": len(filenames),
            "unique_filenames": len(set(filenames)),
            "unique_content_hashes": len(set(content_hashes)),
            "missing_filenames": sum(1 for a in fleet if not a["normalized_filename"]),
            "repeated_filenames": [
                {"filename": name, "count": count}
                for name, count in sorted(filename_counts.items())
                if count > 1
            ],
            "unresolved_binaries": sum(1 for a in fleet if a["missing_binary"]),
            "filename_information_preserved_in_patched_semantic_evidence_input": bool(fleet_input),
            "source_limitation": "Fleet attachment filename fields are blank in Stage 2 normalized attachments and Stage 3R attachment links; null is preserved rather than invented.",
        },
        "loss_classification_counts": dict(sorted(loss_counts.items())),
        "stage4c_loss_location": "Per-attachment filename metadata was not present in Stage 3R extraction packets and was not carried into merged semantic evidence bundles, which expose only aggregate attachment filename counts/samples.",
    }


def write_reports(report: dict[str, Any], resolutions: dict[str, Any]) -> None:
    write_json(PATCH / "reports" / "validation_report.json", report["validation_placeholder"])
    attachment = report["attachment"]
    patch_lines = [
        "# Stage 3R-P Patch Report",
        "",
        "This patch adds a metadata compatibility overlay only. It does not rerun semantic extraction and does not modify earlier stage outputs.",
        "",
        f"- Attachment occurrences patched: {attachment['all_attachments']['total_attachment_occurrences']}",
        f"- Filename-populated occurrences: {attachment['all_attachments']['filename_populated_occurrences']}",
        f"- Fleet attachment occurrences: {attachment['fleet_command']['total_attachment_occurrences']}",
        f"- Fleet populated filenames: {attachment['fleet_command']['filename_populated_occurrences']}",
        "- Client Radar resolution: one user-owned Accenture client engagement with accessibility and repository facets; audit content marked co-authored.",
        "- AVATAR/BCI resolution: completed historical work, not current activity.",
    ]
    (PATCH / "reports" / "patch_report.md").write_text("\n".join(patch_lines) + "\n", encoding="utf-8")

    filename_lines = [
        "# Attachment Filename Report",
        "",
        json.dumps(attachment, indent=2, sort_keys=True),
    ]
    (PATCH / "reports" / "attachment_filename_report.md").write_text("\n".join(filename_lines) + "\n", encoding="utf-8")

    resolution_lines = [
        "# Resolution Application Report",
        "",
        "Confirmed human resolutions applied:",
        "",
        "- Client Radar: one Accenture client engagement, user-owned, with accessibility audit/design and repository implementation facets. Audit/report authorship is co-authored or mixed-origin.",
        "- AVATAR/BCI: completed and historical; current_activity=false.",
        "",
        "Resolution IDs:",
    ]
    for resolution in resolutions["resolutions"]:
        resolution_lines.append(f"- {resolution['resolution_id']}")
    (PATCH / "reports" / "resolution_application_report.md").write_text(
        "\n".join(resolution_lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    before = checksums()
    write_json(PATCH / "manifests" / "checksums_before.json", before)

    indexes = load_stage_indexes()
    resolutions = build_confirmed_resolutions(indexes)
    patched_attachments, traces = build_attachment_records(indexes)
    patched_maps = build_patched_conversation_maps(indexes, patched_attachments)
    semantic_inputs = build_semantic_inputs(patched_attachments, patched_maps, resolutions)
    attachment_report = attachment_reports(patched_attachments, traces, semantic_inputs)

    write_json(PATCH / "decisions" / "confirmed_resolutions.json", resolutions)
    write_jsonl(PATCH / "corpus" / "patched_attachment_links.jsonl", patched_attachments)
    write_jsonl(PATCH / "corpus" / "patched_conversation_evidence_maps.jsonl", patched_maps)
    write_jsonl(PATCH / "corpus" / "patched_semantic_evidence_inputs.jsonl", semantic_inputs)
    write_jsonl(PATCH / "audit" / "attachment_filename_trace.jsonl", traces)

    client_resolution = resolutions["resolutions"][0]
    avatar_resolution = resolutions["resolutions"][1]
    write_jsonl(
        PATCH / "audit" / "client_radar_authorship_trace.jsonl",
        [
            {
                "trace_id": "stage3rp:trace:client_radar_authorship",
                "related_candidate_ids": client_resolution["related_candidate_ids"],
                "project_owner": client_resolution["project_owner"],
                "organizational_context": client_resolution["organizational_context"],
                "engagement_type": client_resolution["engagement_type"],
                "facets": client_resolution["facets"],
                "content_authorship": client_resolution["content_authorship"],
                "evidence_references": client_resolution["evidence_references"],
                "not_merged_with": client_resolution["do_not_merge_with"],
            }
        ],
    )
    write_jsonl(
        PATCH / "audit" / "avatar_status_trace.jsonl",
        [
            {
                "trace_id": "stage3rp:trace:avatar_bci_status",
                "related_candidate_ids": avatar_resolution["related_candidate_ids"],
                "entity": avatar_resolution["entity"],
                "status": avatar_resolution["status"],
                "temporal_status": avatar_resolution["temporal_status"],
                "current_activity": avatar_resolution["current_activity"],
                "evidence_basis": avatar_resolution["evidence_basis"],
                "confidence": avatar_resolution["confidence"],
            }
        ],
    )

    after = checksums()
    write_json(PATCH / "manifests" / "checksums_after.json", after)

    changed_existing_files = [
        path for path, digest in before.items() if after.get(path) != digest
    ]
    report = {
        "validation_placeholder": {
            "status": "not_validated",
            "note": "Run scripts/validate_patch.py to validate this patch.",
        },
        "attachment": attachment_report,
        "checksum_status": {
            "changed_existing_files": changed_existing_files,
            "passed": not changed_existing_files,
        },
        "counts": {
            "patched_attachment_links": len(patched_attachments),
            "patched_conversation_evidence_maps": len(patched_maps),
            "patched_semantic_evidence_inputs": len(semantic_inputs),
            "attachment_filename_traces": len(traces),
        },
    }
    write_reports(report, resolutions)
    print(
        json.dumps(
            {
                "status": "ok",
                "patched_attachment_links": len(patched_attachments),
                "patched_semantic_evidence_inputs": len(semantic_inputs),
                "changed_existing_files": len(changed_existing_files),
                "fleet_attachment_occurrences": attachment_report["fleet_command"]["total_attachment_occurrences"],
                "fleet_filename_populated": attachment_report["fleet_command"]["filename_populated_occurrences"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
