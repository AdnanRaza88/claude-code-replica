from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
import httpx

from .base import Tool, ToolResult


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = 5


class WebFetchInput(BaseModel):
    url: str = Field(description="URL to fetch")
    max_chars: int = 8000


class WebSearchTool(Tool):
    name = "web_search"
    description = (
        "Search the public web for current information. "
        "Use when the user needs facts, docs, news, or anything that might be outdated in training data. "
        "Returns titles, links, and snippets. Cite these sources in your answer."
    )
    risk = "low"
    input_schema = WebSearchInput

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = WebSearchInput(**input_data)
            q = data.query.strip()
            if not q:
                return ToolResult(success=False, error="query required")

            results = await self._ddg_search(q, data.max_results)
            if not results:
                return ToolResult(
                    success=True,
                    output=f"No web results for: {q}",
                    data={"query": q, "results": [], "sources": []},
                )

            lines = []
            sources = []
            for i, r in enumerate(results, 1):
                title = r.get("title") or "Untitled"
                url = r.get("url") or ""
                snippet = (r.get("snippet") or "")[:240]
                lines.append(f"{i}. {title}\n   {url}\n   {snippet}")
                sources.append({"title": title, "url": url, "snippet": snippet})

            body = f"Web search: {q}\n\n" + "\n\n".join(lines)
            return ToolResult(
                success=True,
                output=body,
                data={"query": q, "results": results, "sources": sources},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:400])

    async def _ddg_search(self, query: str, max_results: int) -> list[dict]:
        url = "https://html.duckduckgo.com/html/"
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.post(
                url,
                data={"q": query},
                headers={"User-Agent": "ClaudeCodeReplica/1.0"},
            )
            resp.raise_for_status()
            html = resp.text

        results: list[dict] = []
        import re
        pattern = re.compile(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</(?:a|td|div)',
            re.DOTALL | re.IGNORECASE,
        )
        for m in pattern.finditer(html):
            href = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            snippet = re.sub(r"<[^>]+>", "", m.group(3)).strip()
            if "uddg=" in href:
                from urllib.parse import unquote, parse_qs, urlparse
                qs = parse_qs(urlparse(href).query)
                href = unquote(qs.get("uddg", [href])[0])
            if href and title:
                results.append({"title": title, "url": href, "snippet": snippet})
            if len(results) >= max_results:
                break

        if not results:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r2 = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                if r2.status_code == 200:
                    payload = r2.json()
                    if payload.get("AbstractText"):
                        results.append({
                            "title": payload.get("Heading") or query,
                            "url": payload.get("AbstractURL") or "",
                            "snippet": payload.get("AbstractText", "")[:300],
                        })
                    for t in (payload.get("RelatedTopics") or [])[:max_results]:
                        if isinstance(t, dict) and t.get("Text"):
                            results.append({
                                "title": t.get("Text", "")[:80],
                                "url": t.get("FirstURL") or "",
                                "snippet": t.get("Text", "")[:240],
                            })
        return results[:max_results]


class WebFetchTool(Tool):
    name = "web_fetch"
    description = (
        "Fetch the text content of a public URL. "
        "Use after web_search when you need the full page body. Cite the URL in your answer."
    )
    risk = "low"
    input_schema = WebFetchInput

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = WebFetchInput(**input_data)
            url = data.url.strip()
            if not url.startswith(("http://", "https://")):
                return ToolResult(success=False, error="url must start with http:// or https://")

            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                resp = await client.get(
                    url,
                    headers={"User-Agent": "ClaudeCodeReplica/1.0"},
                )
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")
                text = resp.text

            if "html" in content_type.lower() or text.lstrip().startswith("<"):
                import re
                text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", text)
                text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
                text = re.sub(r"(?is)<[^>]+", " ", text)
                text = re.sub(r"\s+", " ", text).strip()

            truncated = text[: data.max_chars]
            if len(text) > data.max_chars:
                truncated += "\n...[truncated]..."

            return ToolResult(
                success=True,
                output=f"Fetched {url}\n\n{truncated}",
                data={"url": url, "chars": len(text), "sources": [{"title": url, "url": url}]},
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:400])
