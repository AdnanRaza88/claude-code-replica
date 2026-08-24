from __future__ import annotations

import asyncio
import json
import shutil
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class AgentReachInput(BaseModel):
    action: str = Field(
        description=(
            "One of: doctor, web_read, youtube, reddit, wikipedia, x_search_hint. "
            "web_read requires url. youtube requires url or query. "
            "reddit requires subreddit or query. wikipedia requires query."
        )
    )
    url: str | None = Field(default=None, description="URL for web_read or youtube")
    query: str | None = Field(default=None, description="Search query")
    subreddit: str | None = Field(default=None, description="Subreddit name without r/")
    max_chars: int = Field(default=12000, description="Max characters for text content")
    limit: int = Field(default=8, description="Max items for list endpoints")
    lang: str = Field(default="en", description="Wikipedia language code e.g. en, hi")


class AgentReachTool(Tool):
    name = "agent_reach"
    description = (
        "Multi-platform internet reach (Agent-Reach style): read any URL via Jina Reader, "
        "YouTube metadata (yt-dlp if installed), Reddit public JSON, Wikipedia summaries, doctor. "
        "Use for research when you need page text, encyclopedia facts, video info, or social threads. "
        "For interactive click/type use pinchtab instead. Zero paid APIs. No LangChain required."
    )
    risk = "low"
    input_schema = AgentReachInput

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = AgentReachInput(**input_data)
            action = (data.action or "").strip().lower()
            if action == "doctor":
                return await self._doctor()
            if action == "web_read":
                if not data.url:
                    return ToolResult(success=False, error="url required for web_read")
                return await self._web_read(data.url, data.max_chars)
            if action == "youtube":
                return await self._youtube(data)
            if action == "reddit":
                return await self._reddit(data)
            if action == "wikipedia":
                if not data.query:
                    return ToolResult(success=False, error="query required for wikipedia")
                return await self._wikipedia(data.query, data.lang, data.max_chars, data.limit)
            if action in ("x_search_hint", "twitter_hint", "x_hint"):
                return self._x_hint()
            return ToolResult(
                success=False,
                error="unknown action. Use: doctor, web_read, youtube, reddit, wikipedia, x_search_hint",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:500])

    async def _doctor(self) -> ToolResult:
        checks: dict[str, str] = {}
        checks["jina_reader"] = "ok (httpx → r.jina.ai)"
        checks["wikipedia"] = "ok (MediaWiki API)"
        checks["reddit"] = "ok (public JSON; may 403 on some IPs)"
        checks["yt_dlp"] = "available" if shutil.which("yt-dlp") else "missing (optional: pip install yt-dlp)"
        checks["gh"] = "available" if shutil.which("gh") else "missing (use github tool)"
        checks["xreach"] = "available" if shutil.which("xreach") else "missing (optional Twitter CLI)"
        lines = ["Agent-Reach doctor:"]
        for k, v in checks.items():
            lines.append(f"  - {k}: {v}")
        lines.append(
            "\nAlways works: web_read, wikipedia. Reddit usually works. "
            "YouTube full meta needs yt-dlp. Interactive UI → pinchtab."
        )
        return ToolResult(success=True, output="\n".join(lines), data=checks)

    async def _web_read(self, url: str, max_chars: int) -> ToolResult:
        url = url.strip()
        if not url.startswith("http"):
            url = "https://" + url
        jina = f"https://r.jina.ai/{url}"
        async with httpx.AsyncClient(timeout=40.0, follow_redirects=True) as client:
            resp = await client.get(
                jina,
                headers={"User-Agent": "ClaudeCodeReplica-AgentReach/1.0", "Accept": "text/plain"},
            )
            if resp.status_code >= 400:
                return ToolResult(
                    success=False,
                    error=f"Jina Reader failed ({resp.status_code}) for {url}",
                    data={"url": url, "status": resp.status_code},
                )
            text = (resp.text or "").strip()
            if len(text) > max_chars:
                text = text[:max_chars] + "\n...[truncated]"
            return ToolResult(
                success=True,
                output=f"Source: {url}\n\n{text}",
                data={"url": url, "chars": len(text), "source": "jina"},
            )

    async def _wikipedia(self, query: str, lang: str, max_chars: int, limit: int) -> ToolResult:
        lang = (lang or "en").strip()[:8] or "en"
        api = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": min(max(limit, 1), 10),
            "format": "json",
        }
        headers = {"User-Agent": "ClaudeCodeReplica-AgentReach/1.0"}
        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
            r = await client.get(api, params=params, headers=headers)
            if r.status_code >= 400:
                return ToolResult(success=False, error=f"Wikipedia search failed ({r.status_code})")
            hits = ((r.json().get("query") or {}).get("search")) or []
            if not hits:
                return ToolResult(success=True, output=f"No Wikipedia results for: {query}", data={"items": []})

            lines = []
            items = []
            for h in hits[: min(limit, 5)]:
                title = h.get("title") or ""
                page_url = f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                # extract summary
                sum_params = {
                    "action": "query",
                    "prop": "extracts",
                    "exintro": 1,
                    "explaintext": 1,
                    "titles": title,
                    "format": "json",
                }
                sr = await client.get(api, params=sum_params, headers=headers)
                extract = ""
                if sr.status_code < 400:
                    pages = ((sr.json().get("query") or {}).get("pages")) or {}
                    for p in pages.values():
                        extract = (p.get("extract") or "")[: max_chars // max(len(hits), 1)]
                        break
                block = f"## {title}\n{page_url}\n{extract}".strip()
                lines.append(block)
                items.append({"title": title, "url": page_url, "extract": extract[:500]})

            body = f"Wikipedia ({lang}): {query}\n\n" + "\n\n---\n\n".join(lines)
            if len(body) > max_chars:
                body = body[:max_chars] + "\n...[truncated]"
            return ToolResult(success=True, output=body, data={"items": items, "query": query, "lang": lang})

    async def _youtube(self, data: AgentReachInput) -> ToolResult:
        target = (data.url or data.query or "").strip()
        if not target:
            return ToolResult(success=False, error="url or query required for youtube")

        if not shutil.which("yt-dlp"):
            if target.startswith("http"):
                oembed = f"https://www.youtube.com/oembed?url={quote(target, safe='')}&format=json"
                try:
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        r = await client.get(oembed)
                        if r.status_code == 200:
                            meta = r.json()
                            out = (
                                f"YouTube (oEmbed — install yt-dlp for richer meta):\n"
                                f"Title: {meta.get('title')}\n"
                                f"Author: {meta.get('author_name')}\n"
                                f"URL: {target}\n"
                            )
                            return ToolResult(success=True, output=out, data=meta)
                except Exception:
                    pass
            return ToolResult(
                success=False,
                error="yt-dlp not installed. Optional: pip install yt-dlp",
            )

        if target.startswith("http"):
            cmd = ["yt-dlp", "--dump-json", "--skip-download", target]
        else:
            cmd = ["yt-dlp", "--dump-json", "--skip-download", f"ytsearch{min(data.limit, 5)}:{target}"]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
            raw = (stdout or b"").decode("utf-8", errors="replace").strip()
            if proc.returncode != 0 and not raw:
                err = (stderr or b"").decode("utf-8", errors="replace")[:400]
                return ToolResult(success=False, error=f"yt-dlp failed: {err}")

            entries = []
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            if not entries:
                return ToolResult(success=False, error="yt-dlp returned no JSON")

            lines = []
            for e in entries[: data.limit]:
                title = e.get("title") or ""
                vid = e.get("id") or ""
                uploader = e.get("uploader") or e.get("channel") or ""
                dur = e.get("duration")
                desc = (e.get("description") or "")[:400]
                webpage = e.get("webpage_url") or (f"https://www.youtube.com/watch?v={vid}" if vid else "")
                lines.append(
                    f"Title: {title}\nUploader: {uploader}\nDuration: {dur}s\nURL: {webpage}\nDesc: {desc}\n"
                )
            return ToolResult(
                success=True,
                output="\n---\n".join(lines),
                data={"count": len(entries), "ids": [e.get("id") for e in entries[: data.limit]]},
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, error="yt-dlp timed out")
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:400])

    async def _reddit(self, data: AgentReachInput) -> ToolResult:
        limit = max(1, min(data.limit, 25))
        headers = {"User-Agent": "ClaudeCodeReplica-AgentReach/1.0"}
        if data.subreddit:
            api = f"https://www.reddit.com/r/{data.subreddit.strip('/')}/hot.json?limit={limit}"
        elif data.query:
            api = f"https://www.reddit.com/search.json?q={quote(data.query)}&limit={limit}"
        else:
            return ToolResult(success=False, error="subreddit or query required for reddit")

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(api, headers=headers)
            if resp.status_code == 403:
                return ToolResult(
                    success=False,
                    error="Reddit blocked this IP (403). Use web_search or pinchtab instead.",
                )
            if resp.status_code >= 400:
                return ToolResult(success=False, error=f"Reddit API {resp.status_code}")
            payload = resp.json()

        children = (payload.get("data") or {}).get("children") or []
        lines = []
        items = []
        for c in children[:limit]:
            d = c.get("data") or {}
            title = d.get("title") or ""
            score = d.get("score")
            sub = d.get("subreddit")
            permalink = d.get("permalink") or ""
            url = f"https://www.reddit.com{permalink}" if permalink else (d.get("url") or "")
            selftext = (d.get("selftext") or "")[:300]
            lines.append(f"[{score}] r/{sub}: {title}\n{url}\n{selftext}".strip())
            items.append({"title": title, "url": url, "score": score, "subreddit": sub})
        if not lines:
            return ToolResult(success=True, output="No Reddit results.", data={"items": []})
        return ToolResult(success=True, output="\n\n".join(lines), data={"items": items})

    def _x_hint(self) -> ToolResult:
        msg = (
            "Twitter/X full search needs xreach CLI + cookies.\n"
            "If installed: xreach search \"query\" -n 10 --json\n"
            "Else use web_search / web_fetch / pinchtab for public tweets."
        )
        return ToolResult(success=True, output=msg, data={"backend": "xreach_optional"})
