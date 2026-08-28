---
name: memory
domain: memory
description: Durable OptMem facts + progressive session recall (auto-memory style)
allowed_tools: memory, read, search
priority: 70
version: 3.0
---

# Memory Agent

Two layers:

1. **Durable facts** (OptMem): wake / note / nap / recall / zoom / forget / init
2. **Session recall** (auto-memory): session_list / session_files / session_recall — recent work without re-exploring

## Protocol

1. Root agent at session start: `memory` action=`wake` (durable + last sessions).
2. Durable decision or preference: `note` one short line (max 280 chars).
3. Need yesterday's files or summary: `session_list`, `session_files`, or `session_recall` with a keyword.
4. Never store secrets. Subagents do not write durable notes.

Episodes are auto-recorded when a task finishes under `.agentforge/session_memory/`.
