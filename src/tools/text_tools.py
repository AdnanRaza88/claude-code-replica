from __future__ import annotations

import html as html_lib
import re
from typing import Any

from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class DefuddleInput(BaseModel):
    html: str = Field(default="", description="Raw HTML or noisy web text")
    text: str = Field(default="", description="Alternate plain text if html is empty")
    max_chars: int = 8000
    url: str = Field(default="", description="Optional source URL for citation")


class HumanizeInput(BaseModel):
    text: str = Field(description="Draft to rewrite in a human voice")
    keep_code: bool = True


_SCRIPT_RE = re.compile(r"(?is)<(script|style|noscript|svg|iframe)[^>]*>.*?</\1>")
_TAG_RE = re.compile(r"(?is)<[^>]+>")
_HEADING_RE = re.compile(r"(?is)<h([1-6])[^>]*>(.*?)</h\1>")
_LINK_RE = re.compile(r'(?is)<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>')
_LI_RE = re.compile(r"(?is)<li[^>]*>(.*?)</li>")
_BR_RE = re.compile(r"(?is)<br\s*/?>")
_P_RE = re.compile(r"(?is)</p>")
_WS_RE = re.compile(r"\n{3,}")
_SPACE_RE = re.compile(r"[ \t]{2,}")

_AI_PHRASES = (
    (r"(?i)\bdelve into\b", "look at"),
    (r"(?i)\bin today's (?:fast-paced|ever-evolving) (?:world|landscape)\b", "today"),
    (r"(?i)\bit's important to note that\b", ""),
    (r"(?i)\bit is important to note that\b", ""),
    (r"(?i)\bin conclusion,\s*", ""),
    (r"(?i)\bfurthermore,\s*", ""),
    (r"(?i)\bmoreover,\s*", ""),
    (r"(?i)\bleverage\b", "use"),
    (r"(?i)\butilize\b", "use"),
    (r"(?i)\brobust\b", "solid"),
    (r"(?i)\bcutting-edge\b", "new"),
    (r"(?i)\bunlock(?:s|ing)? the potential\b", "help"),
    (r"(?i)\bembark on\b", "start"),
    (r"(?i)\ba testament to\b", "shows"),
    (r"(?i)\bmultifaceted\b", "varied"),
    (r"(?i)\bpivotal\b", "important"),
    (r"(?i)\bunderscore(?:s|d)?\b", "show"),
    (r"(?i)\brealm of\b", ""),
    (r"(?i)\btapestry of\b", ""),
    (r"(?i)\bfoster(?:s|ing)?\b", "support"),
    (r"(?i)\belevate\b", "improve"),
    (r"(?i)\bas an ai(?: language model)?[^.]*\.\s*", ""),
    (r"(?i)\bi hope this helps!?\s*", ""),
    (r"(?i)\blet me know if you (?:need|have)[^.]*\.\s*", ""),
)


def defuddle_html(raw: str, max_chars: int = 8000) -> str:
    text = raw or ""
    text = _SCRIPT_RE.sub("", text)
    text = _HEADING_RE.sub(lambda m: "\n" + ("#" * min(int(m.group(1)), 6)) + " " + m.group(2) + "\n", text)
    text = _LINK_RE.sub(lambda m: f"[{m.group(2)}]({m.group(1)})", text)
    text = _LI_RE.sub(lambda m: "- " + m.group(1) + "\n", text)
    text = _BR_RE.sub("\n", text)
    text = _P_RE.sub("\n\n", text)
    text = _TAG_RE.sub(" ", text)
    text = html_lib.unescape(text)
    text = _SPACE_RE.sub(" ", text)
    text = _WS_RE.sub("\n\n", text)
    return text.strip()[:max_chars]


def humanize_text(text: str, keep_code: bool = True) -> str:
    if not text:
        return ""
    blocks: list[tuple[str, str]] = []
    work = text
    if keep_code:
        parts = re.split(r"(```[\s\S]*?```|`[^`]+`)", work)
        rebuilt: list[str] = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                rebuilt.append(part)
            else:
                rebuilt.append(_rewrite(part))
        return "".join(rebuilt).strip()
    return _rewrite(work).strip()


def _rewrite(chunk: str) -> str:
    out = chunk
    for pattern, repl in _AI_PHRASES:
        out = re.sub(pattern, repl, out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    out = re.sub(r" {2,}", " ", out)
    return out


class DefuddleTool(Tool):
    name = "defuddle"
    description = (
        "Convert noisy HTML or scraped web text into compact readable markdown. "
        "Use after web_fetch when the page is cluttered."
    )
    risk = "low"
    input_schema = DefuddleInput

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        data = DefuddleInput(**input_data)
        raw = data.html or data.text
        if not raw.strip():
            return ToolResult(success=False, error="html or text required")
        cleaned = defuddle_html(raw, data.max_chars)
        return ToolResult(
            success=True,
            output=cleaned,
            data={"chars": len(cleaned), "url": data.url, "sources": [{"title": "defuddle", "url": data.url}] if data.url else []},
        )


class HumanizeTool(Tool):
    name = "humanize"
    description = (
        "Rewrite prose to strip common AI-writing tells. Leaves fenced code and inline code alone."
    )
    risk = "low"
    input_schema = HumanizeInput

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        data = HumanizeInput(**input_data)
        if not data.text.strip():
            return ToolResult(success=False, error="text required")
        out = humanize_text(data.text, data.keep_code)
        return ToolResult(success=True, output=out, data={"chars": len(out)})
