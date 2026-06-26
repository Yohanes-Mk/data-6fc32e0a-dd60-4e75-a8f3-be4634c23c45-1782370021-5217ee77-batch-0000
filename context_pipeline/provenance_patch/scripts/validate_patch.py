#!/usr/bin/env python3
"""Validate Stage 3R-P provenance patch artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PATCH = ROOT / "context_pipeline" / "provenance_patch"
FLEET_CONVERSATION_ID = "claude:conversations:conversation:e2fc5641-6bd8-41c3-80d2-1e1e71b1e491"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: {exc}") from exc
    return records


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_file_digests() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): digest_file(path)
        for path in sorted(PATCH.rglob("*"))
        if path.is_file() and path.name != "validation_report.json"
    }


def validate_unique(records: list[dict[str, Any]], key: str, issues: list[str]) -> None:
    values = [r.get(key) for r in records]
    missing = sum(1 for value in values if not value)
    duplicates = [value for value, count in Counter(values).items() if value and count > 1]
    if missing:
        issues.append(f"{key}: {missing} missing ids")
    if duplicates:
        issues.append(f"{key}: duplicate ids {duplicates[:5]}")


def normalize_filename(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def main() -> None:
    issues: list[str] = []
    warnings: list[str] = []

    required_files = [
        PATCH / "config" / "patch_policy.json",
        PATCH / "decisions" / "confirmed_resolutions.json",
        PATCH / "audit" / "attachment_filename_trace.jsonl",
        PATCH / "audit" / "client_radar_authorship_trace.jsonl",
        PATCH / "audit" / "avatar_status_trace.jsonl",
        PATCH / "corpus" / "patched_attachment_links.jsonl",
        PATCH / "corpus" / "patched_conversation_evidence_maps.jsonl",
        PATCH / "corpus" / "patched_semantic_evidence_inputs.jsonl",
        PATCH / "manifests" / "checksums_before.json",
        PATCH / "manifests" / "checksums_after.json",
    ]
    for path in required_files:
        if not path.exists():
            issues.append(f"missing required file: {path.relative_to(ROOT)}")

    if issues:
        report = build_report(issues, warnings, {}, {}, {}, False)
        write_json(PATCH / "reports" / "validation_report.json", report)
        print(json.dumps({k: report[k] for k in ("structural_validation_status", "metadata_quality_status")}, sort_keys=True))
        sys.exit(1)

    policy = read_json(PATCH / "config" / "patch_policy.json")
    resolutions = read_json(PATCH / "decisions" / "confirmed_resolutions.json")
    attachment_traces = read_jsonl(PATCH / "audit" / "attachment_filename_trace.jsonl")
    client_trace = read_jsonl(PATCH / "audit" / "client_radar_authorship_trace.jsonl")
    avatar_trace = read_jsonl(PATCH / "audit" / "avatar_status_trace.jsonl")
    patched_attachments = read_jsonl(PATCH / "corpus" / "patched_attachment_links.jsonl")
    patched_maps = read_jsonl(PATCH / "corpus" / "patched_conversation_evidence_maps.jsonl")
    semantic_inputs = read_jsonl(PATCH / "corpus" / "patched_semantic_evidence_inputs.jsonl")

    validate_unique(patched_attachments, "patched_attachment_link_id", issues)
    validate_unique(patched_attachments, "attachment_occurrence_id", issues)
    validate_unique(patched_maps, "patched_evidence_map_id", issues)
    validate_unique(semantic_inputs, "semantic_input_id", issues)
    validate_unique(attachment_traces, "trace_id", issues)

    stage3r_links = {
        r.get("attachment_link_id"): r
        for r in read_jsonl(ROOT / "context_pipeline" / "extraction_staging_repair" / "corpus" / "attachment_links.jsonl")
    }
    normalized_attachments = {
        r.get("normalized_id"): r
        for r in read_jsonl(ROOT / "context_pipeline" / "normalized" / "attachments.jsonl")
    }
    merged_bundles = read_jsonl(
        ROOT / "context_pipeline" / "semantic_pilot_merged" / "evidence_bundles" / "semantic_evidence_bundles.jsonl"
    )

    for record in patched_attachments:
        occurrence_id = record.get("attachment_occurrence_id")
        if occurrence_id not in stage3r_links:
            issues.append(f"unresolved Stage 3R attachment link: {occurrence_id}")
        attachment_id = record.get("attachment_normalized_id")
        if attachment_id not in normalized_attachments:
            issues.append(f"unresolved normalized attachment: {attachment_id}")
        upstream_filename = normalize_filename(normalized_attachments.get(attachment_id, {}).get("filename"))
        if upstream_filename and not record.get("filename_populated"):
            issues.append(f"upstream filename lost in patched attachment: {occurrence_id}")
        if record.get("original_filename") and record.get("original_filename") != upstream_filename:
            issues.append(f"invented or altered original filename: {occurrence_id}")
        if record.get("normalized_filename") and upstream_filename and record.get("normalized_filename") != upstream_filename:
            issues.append(f"normalized filename diverges from upstream filename: {occurrence_id}")
        if record.get("normalized_filename") and not upstream_filename:
            link_filename = normalize_filename(stage3r_links.get(occurrence_id, {}).get("filename"))
            if record.get("normalized_filename") != link_filename:
                issues.append(f"filename appears invented without upstream value: {occurrence_id}")

    fleet = [a for a in patched_attachments if a.get("conversation_id") == FLEET_CONVERSATION_ID]
    fleet_names = [a.get("normalized_filename") for a in fleet if a.get("normalized_filename")]
    fleet_hashes = [a.get("content_hash") for a in fleet if a.get("content_hash")]
    fleet_input = next(
        (r for r in semantic_inputs if r.get("semantic_input_id") == "stage3rp:semantic_input:fleet_attachment_filename_overlay"),
        None,
    )
    if len(fleet) != 92:
        issues.append(f"Fleet attachment count expected 92, got {len(fleet)}")
    if len(fleet_names) != 0:
        warnings.append("Fleet has populated filenames; verify this still reflects upstream data.")
    if not fleet_input:
        issues.append("missing Fleet semantic evidence filename overlay")
    elif len(fleet_input.get("attachment_filename_metadata", [])) != len(fleet):
        issues.append("Fleet semantic evidence overlay count does not reconcile")

    if not all(a.get("missing_binary") for a in fleet):
        warnings.append("At least one Fleet attachment is no longer unresolved binary; verify upstream export state.")

    client = client_trace[0] if client_trace else {}
    authorship = client.get("content_authorship", {})
    facets = client.get("facets", [])
    if client.get("project_owner") != "user":
        issues.append("Client Radar project_owner is not user")
    if client.get("organizational_context") != "Accenture":
        issues.append("Client Radar organizational_context is not Accenture")
    if client.get("engagement_type") != "client_engagement":
        issues.append("Client Radar engagement_type is not client_engagement")
    if len(facets) != 2:
        issues.append("Client Radar does not have exactly two facets")
    if authorship.get("authorship_classification") != "co_authored":
        issues.append("Client Radar audit authorship is not co_authored")
    if not authorship.get("user_contribution") or not authorship.get("assistant_contribution"):
        issues.append("Client Radar authorship does not include both user and assistant contribution")
    do_not_merge = set(client.get("not_merged_with", []))
    if "Accenture interview preparation" not in do_not_merge:
        issues.append("Client Radar lacks interview-prep non-merge guard")

    avatar = avatar_trace[0] if avatar_trace else {}
    if avatar.get("status") != "completed":
        issues.append("AVATAR status is not completed")
    if avatar.get("temporal_status") != "historical_confirmed":
        issues.append("AVATAR temporal_status is not historical_confirmed")
    if avatar.get("current_activity") is not False:
        issues.append("AVATAR current_activity is not false")

    before = read_json(PATCH / "manifests" / "checksums_before.json")
    after = read_json(PATCH / "manifests" / "checksums_after.json")
    changed_existing_files = [path for path, digest in before.items() if after.get(path) != digest]
    if changed_existing_files:
        issues.append(f"prior files changed: {changed_existing_files[:5]}")

    repeat_stable = check_repeat_stability()
    if not repeat_stable:
        issues.append("rerunning build_patched_evidence.py did not produce stable outputs")

    loss_counts = Counter(t.get("filename_loss_classification") for t in attachment_traces)
    merged_fleet_bundle = [
        b for b in merged_bundles
        if b.get("conversation_id") == FLEET_CONVERSATION_ID
    ]
    stage4c_has_per_occurrence_filenames = any("attachment_filename_metadata" in b for b in merged_fleet_bundle)

    counts = {
        "patched_attachment_links": len(patched_attachments),
        "patched_conversation_evidence_maps": len(patched_maps),
        "patched_semantic_evidence_inputs": len(semantic_inputs),
        "attachment_filename_traces": len(attachment_traces),
        "filename_populated_occurrences": sum(1 for a in patched_attachments if a.get("filename_populated")),
        "fleet": {
            "total_attachment_occurrences": len(fleet),
            "filename_populated_occurrences": len(fleet_names),
            "unique_filenames": len(set(fleet_names)),
            "unique_content_hashes": len(set(fleet_hashes)),
            "missing_filenames": sum(1 for a in fleet if not a.get("normalized_filename")),
            "unresolved_binaries": sum(1 for a in fleet if a.get("missing_binary")),
            "patched_semantic_input_preserves_filename_metadata": bool(fleet_input),
        },
        "loss_classification_counts": dict(sorted(loss_counts.items())),
    }

    metadata = {
        "policy_stage": policy.get("stage"),
        "stage4c_has_per_occurrence_filenames": stage4c_has_per_occurrence_filenames,
        "filename_loss_location": "Stage 3R extraction packets omit filename fields, and merged semantic evidence bundles carry only aggregate filename counts/samples rather than the per-occurrence attachment filename table.",
        "changed_existing_files": changed_existing_files,
    }

    report = build_report(issues, warnings, counts, metadata, resolutions, repeat_stable)
    write_json(PATCH / "reports" / "validation_report.json", report)
    print(
        json.dumps(
            {
                "structural_validation_status": report["structural_validation_status"],
                "metadata_quality_status": report["metadata_quality_status"],
                "blocking_issues": report["blocking_issues"],
            },
            sort_keys=True,
        )
    )
    if issues:
        sys.exit(1)


def check_repeat_stability() -> bool:
    before = patch_file_digests()
    result = subprocess.run(
        [sys.executable, str(PATCH / "scripts" / "build_patched_evidence.py")],
        cwd=ROOT,
        env={"PYTHONDONTWRITEBYTECODE": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    after = patch_file_digests()
    if result.returncode != 0:
        return False
    return before == after


def build_report(
    issues: list[str],
    warnings: list[str],
    counts: dict[str, Any],
    metadata: dict[str, Any],
    resolutions: dict[str, Any],
    repeat_stable: bool,
) -> dict[str, Any]:
    structural_status = "pass" if not issues else "fail"
    metadata_status = "pass" if not issues else "fail"
    return {
        "structural_validation_status": structural_status,
        "metadata_quality_status": metadata_status,
        "blocking_issues": issues,
        "warnings": warnings,
        "counts": counts,
        "metadata": metadata,
        "confirmed_resolution_count": len(resolutions.get("resolutions", [])) if isinstance(resolutions, dict) else 0,
        "checksum_status": {
            "passed": not metadata.get("changed_existing_files"),
            "changed_existing_files": metadata.get("changed_existing_files", []),
        },
        "rerun_stability_status": "pass" if repeat_stable else "fail",
    }


if __name__ == "__main__":
    main()
