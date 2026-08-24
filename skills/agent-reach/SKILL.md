---
name: agent-reach
domain: research
description: Multi-platform internet access — Jina web read, Wikipedia, YouTube, Reddit, optional X/Twitter
allowed_tools: agent_reach, web_search, web_fetch, pinchtab, bash, read, search, github
priority: 85
version: 1.1
---

# Agent Reach

Use the `agent_reach` tool for fast read-only internet access. Prefer it over inventing content.

## Actions
- web_read url=... — any public page as clean text (Jina)
- wikipedia query=... [lang=en|hi] — encyclopedia summary
- youtube url=... or query=... — video meta
- reddit subreddit=... or query=... — threads
- doctor — which backends are available
- x_search_hint — Twitter/X tips

## Rules
1. Never invent page text or titles — only report tool output.
2. Prefer agent_reach.web_read / wikipedia over guessing facts.
3. Interactive pages (click, forms) → pinchtab, not agent_reach.
4. Cite URL + short title in the user answer.
5. Keep outputs compact.
