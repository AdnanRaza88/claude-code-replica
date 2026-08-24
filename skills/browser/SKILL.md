---
name: browser
domain: browser
description: Browser automation via PinchTab; agent_reach for static reads
allowed_tools: pinchtab, agent_reach, bash, read, search, web_search, web_fetch
priority: 80
version: 1.2
---

# Browser Agent (PinchTab + Agent Reach)

Interactive Chrome via `pinchtab`. Static reads via `agent_reach`.

## Interactive (pinchtab)
1. health → confirm server (default http://127.0.0.1:9867)
2. navigate url=...
3. snapshot filter=interactive → refs e0, e1
4. action kind=click|type|fill|press ref=...
5. text — readable content

## Read-only (agent_reach)
- web_read / wikipedia / youtube / reddit — no browser server needed

## Rules
1. Use snapshot refs for actions; never invent selectors.
2. Never invent page content.
3. If PinchTab unreachable, fall back to agent_reach / web_search / web_fetch.
4. Prefer agent_reach for static articles (cheaper).
