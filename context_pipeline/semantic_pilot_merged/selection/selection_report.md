# Stage 4C — Merged-Schema Pilot: Case Selection Report

Twelve evidence cases selected deterministically over the Stage 3R corpus
(`extraction_staging_repair/corpus/`). Six are fixed prior-benchmark conversations; six are
chosen by deterministic structural rules over Stage 3R metadata (no semantic judgment used
in selection).

## Benchmark cases (6, fixed)

| Case | Conversation | Why |
|---|---|---|
| mc-01 | 14f3c888 | Transcript-formatting one-off (hr-001: not a project) |
| mc-02 | 2838a734 | Academic pesticide risk-assessment (hr-002: assignment) |
| mc-03 | 94f53cfc | Mixed study/career activities (hr-003: do not merge) |
| mc-04 | b8366901 | AI learning roadmap (hr-007: active project) |
| mc-05 | e2fc5641 | Fleet Command / Unity (hr-008: real entity, status unresolved); attachment-heavy |
| mc-06 | c69f5e03 | Tsotsi film work (hr-009: status unresolved) |

## Additional cases (6, deterministic)

| Case | Type | Target | Deterministic rule |
|---|---|---|---|
| mc-07 | project_document | `ai-engineer-2026.md` (project "AI Engineer Roadmap") | The project-document whose `project_name` matches a benchmark project (mc-04), so a conversation can be paired with a real document. Stage 3R `verified_conversation_links` is empty — no invented join. |
| mc-08 | design_chat | "Client Radar Accessibility Review" (`a5eb06ca6b67`) | Design chat with the most packets (25) carrying user-authored evidence; `embedded_project_matches_exported_project=False`. |
| mc-09 | pasted_assistant | conversation f04cc5a5 | The **only** non-benchmark conversation with `pasted_assistant_segment_ids` (1) plus substantial user evidence (14). |
| mc-10 | tool_log | conversation c2701642 | **Highest** non-benchmark `tool_log_segment_ids` count (21). |
| mc-11 | missing_source | conversation 85fc6dee | High non-benchmark `missing_source_references` count (23), distinct from the log case; chosen for missing-source impact testing. |
| mc-12 | structural_project_candidate | conversation c9b827d9 | New likely-continuing project by structure only: 43 packets, 12 branch paths, 9 attachments, one-month span (2026-04-18..2026-05-15) — strongest **multi-day** continuing-work signal among non-benchmark conversations (5bf2f2cd had more packets but all on a single day, so it reads as one long session, not continuing work). |

## Notes and overlaps (documented, not hidden)

- **mc-07 pairs with mc-04** (same project name) — the explicitly-allowed conversation+document pairing. The document turned out to be a **third-party reference** (authored by Dave Ebbelaar / Datalumina), which is itself a useful source-vs-artifact test.
- **mc-08 and mc-09** both concern **Client Radar** (an Accenture client deliverable): mc-08 is the design-chat write-up, mc-09 is the Claude-Code repo session that produced the findings. This was not engineered — they surfaced independently from the design-chat and pasted-assistant rules — and gives a genuine cross-case relationship to test.
- **mc-11 is Fleet Command** card-system work (path `SP 26/SE- Computer Animation/.../Fleet Command`), an earlier (2026-02-19) session than mc-05's April–May work — a real cross-case clustering signal with mc-05.
- **mc-12 ties to the confirmed Accenture affiliation** (hr-006), and a "water/clean-water" phrase appears in both mc-12 (Accenture interview scenario) and mc-10 (SCSU AVATAR lab "water project"); these are **different** activities and must not be merged.

All twelve case targets were verified to resolve against the Stage 3R corpus before bundling.
