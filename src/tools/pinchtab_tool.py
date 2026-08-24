from __future__ import annotations

from typing import Any, Callable, Optional
from pydantic import BaseModel, Field
import httpx
import json

from .base import Tool, ToolResult


DEFAULT_BASE = "http://127.0.0.1:9867"


class PinchTabInput(BaseModel):
    action: str = Field(
        description=(
            "One of: health, navigate, snapshot, text, action, tabs, back, reload. "
            "navigate requires url. snapshot/text optional tab_id and filter. "
            "action requires kind (click|type|fill|press|hover|scroll|select) and usually ref."
        )
    )
    url: str | None = Field(default=None, description="URL for navigate")
    tab_id: str | None = Field(default=None, description="Existing tab id when targeting a specific tab")
    filter: str = Field(default="interactive", description="snapshot filter: interactive | all")
    format: str = Field(default="compact", description="snapshot format: json | compact | text")
    kind: str | None = Field(default=None, description="action kind: click, type, fill, press, hover, scroll, select")
    ref: str | None = Field(default=None, description="accessibility ref from snapshot e.g. e0, e3")
    text: str | None = Field(default=None, description="text to type/fill when kind is type or fill")
    key: str | None = Field(default=None, description="key name when kind is press e.g. Enter, Tab")
    value: str | None = Field(default=None, description="value for select")
    max_chars: int = Field(default=12000, description="max characters to return for text extraction")
    new_tab: bool = Field(default=False, description="open navigate in a new tab")


class PinchTabTool(Tool):
    name = "pinchtab"
    description = (
        "Control a real Chrome browser via PinchTab HTTP API (accessibility tree). "
        "Use for accurate page navigation, interactive element inspection (refs e0/e1), "
        "clicking, typing, and text extraction without hallucinating URLs or content. "
        "Requires PinchTab server running (default http://127.0.0.1:9867). "
        "Typical flow: health -> navigate(url) -> snapshot(filter=interactive) -> action(kind, ref). "
        "Prefer snapshot refs over CSS selectors. Falls back gracefully if server is down."
    )
    risk = "medium"
    input_schema = PinchTabInput

    def __init__(
        self,
        base_url: str | None = None,
        get_base_url: Optional[Callable[[], Optional[str]]] = None,
        get_token: Optional[Callable[[], Optional[str]]] = None,
        timeout: float = 45.0,
    ):
        self._base_url = (base_url or DEFAULT_BASE).rstrip("/")
        self.get_base_url = get_base_url
        self.get_token = get_token
        self.timeout = timeout

    def _resolve_base(self, runtime: Any = None) -> str:
        if self.get_base_url:
            u = self.get_base_url()
            if u:
                return u.rstrip("/")
        if runtime is not None and hasattr(runtime, "get_credential"):
            u = runtime.get_credential("pinchtab_url")
            if u:
                return str(u).rstrip("/")
        return self._base_url

    def _headers(self, runtime: Any = None) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        token = None
        if self.get_token:
            token = self.get_token()
        if not token and runtime is not None and hasattr(runtime, "get_credential"):
            token = runtime.get_credential("pinchtab_token")
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = PinchTabInput(**input_data)
            action = data.action.strip().lower()
            base = self._resolve_base(runtime)
            headers = self._headers(runtime)

            if action == "health":
                return await self._health(base, headers)
            if action == "navigate":
                if not data.url:
                    return ToolResult(success=False, error="url required for navigate")
                return await self._navigate(base, headers, data)
            if action == "snapshot":
                return await self._snapshot(base, headers, data)
            if action == "text":
                return await self._text(base, headers, data)
            if action == "action":
                if not data.kind:
                    return ToolResult(success=False, error="kind required for action (click|type|fill|press|hover|scroll|select)")
                return await self._action(base, headers, data)
            if action == "tabs":
                return await self._tabs(base, headers)
            if action == "back":
                return await self._simple_post(base, headers, "/back", data.tab_id)
            if action == "reload":
                return await self._simple_post(base, headers, "/reload", data.tab_id)
            return ToolResult(
                success=False,
                error=f"unknown action '{action}'. Use: health, navigate, snapshot, text, action, tabs, back, reload",
            )
        except httpx.ConnectError:
            return ToolResult(
                success=False,
                error=(
                    "PinchTab server not reachable. Start it with: pinchtab server "
                    "(or pinchtab daemon install). Default URL http://127.0.0.1:9867"
                ),
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:500])

    async def _request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        json_body: dict | None = None,
        params: dict | None = None,
    ) -> tuple[int, Any]:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            resp = await client.request(method, url, headers=headers, json=json_body, params=params)
            try:
                body = resp.json()
            except Exception:
                body = {"raw": resp.text[:4000]}
            return resp.status_code, body

    async def _health(self, base: str, headers: dict[str, str]) -> ToolResult:
        status, body = await self._request("GET", f"{base}/health", headers)
        ok = status == 200
        return ToolResult(
            success=ok,
            output=json.dumps(body, indent=2) if isinstance(body, dict) else str(body),
            data=body if isinstance(body, dict) else {"body": body},
            error=None if ok else f"health returned {status}",
        )

    async def _navigate(self, base: str, headers: dict[str, str], data: PinchTabInput) -> ToolResult:
        payload: dict[str, Any] = {"url": data.url}
        if data.tab_id:
            payload["tabId"] = data.tab_id
        if data.new_tab:
            payload["newTab"] = True
        path = f"/tabs/{data.tab_id}/navigate" if data.tab_id else "/navigate"
        status, body = await self._request("POST", f"{base}{path}", headers, json_body=payload)
        if status >= 400:
            return ToolResult(success=False, error=f"navigate failed ({status}): {body}", data=body if isinstance(body, dict) else {})
        tab_id = ""
        title = ""
        url = data.url or ""
        if isinstance(body, dict):
            tab_id = str(body.get("tabId") or body.get("id") or body.get("tab_id") or "")
            title = str(body.get("title") or "")
            url = str(body.get("url") or url)
        out = f"Navigated to {url}"
        if title:
            out += f" — {title}"
        if tab_id:
            out += f"\ntab_id: {tab_id}"
        return ToolResult(
            success=True,
            output=out,
            data={"tab_id": tab_id, "url": url, "title": title, "raw": body if isinstance(body, dict) else {}},
        )

    async def _snapshot(self, base: str, headers: dict[str, str], data: PinchTabInput) -> ToolResult:
        params = {"filter": data.filter or "interactive", "format": data.format or "compact"}
        if data.tab_id:
            path = f"/tabs/{data.tab_id}/snapshot"
        else:
            path = "/snapshot"
            if data.tab_id:
                params["tabId"] = data.tab_id
        status, body = await self._request("GET", f"{base}{path}", headers, params=params)
        if status >= 400:
            return ToolResult(success=False, error=f"snapshot failed ({status}): {body}", data=body if isinstance(body, dict) else {})

        nodes = []
        url = title = ""
        if isinstance(body, dict):
            nodes = body.get("nodes") or body.get("elements") or []
            url = str(body.get("url") or "")
            title = str(body.get("title") or "")
        elif isinstance(body, list):
            nodes = body

        lines = []
        if title or url:
            lines.append(f"Page: {title} ({url})".strip())
        for n in nodes[:80]:
            if not isinstance(n, dict):
                continue
            ref = n.get("ref") or n.get("id") or ""
            role = n.get("role") or n.get("type") or ""
            name = n.get("name") or n.get("label") or n.get("text") or ""
            value = n.get("value")
            extra = f" value={value!r}" if value not in (None, "") else ""
            lines.append(f"  [{ref}] {role}: {name}{extra}".strip())
        if not lines:
            lines.append(json.dumps(body, indent=2)[:6000] if body else "(empty snapshot)")

        return ToolResult(
            success=True,
            output="\n".join(lines),
            data={
                "url": url,
                "title": title,
                "nodes": nodes[:80] if isinstance(nodes, list) else [],
                "count": len(nodes) if isinstance(nodes, list) else 0,
                "tab_id": data.tab_id,
            },
        )

    async def _text(self, base: str, headers: dict[str, str], data: PinchTabInput) -> ToolResult:
        params: dict[str, Any] = {}
        if data.tab_id:
            path = f"/tabs/{data.tab_id}/text"
        else:
            path = "/text"
            if data.tab_id:
                params["tabId"] = data.tab_id
        status, body = await self._request("GET", f"{base}{path}", headers, params=params or None)
        if status >= 400:
            return ToolResult(success=False, error=f"text failed ({status}): {body}", data=body if isinstance(body, dict) else {})

        text = ""
        url = ""
        if isinstance(body, dict):
            text = str(body.get("text") or body.get("content") or body.get("body") or "")
            url = str(body.get("url") or "")
            if not text and "raw" in body:
                text = str(body["raw"])
        elif isinstance(body, str):
            text = body
        else:
            text = json.dumps(body)

        truncated = text[: data.max_chars]
        if len(text) > data.max_chars:
            truncated += "\n...[truncated]..."
        header = f"Text from {url}\n\n" if url else "Page text:\n\n"
        return ToolResult(
            success=True,
            output=header + truncated,
            data={"url": url, "chars": len(text), "tab_id": data.tab_id, "sources": [{"title": url or "page", "url": url}] if url else []},
        )

    async def _action(self, base: str, headers: dict[str, str], data: PinchTabInput) -> ToolResult:
        payload: dict[str, Any] = {"kind": data.kind}
        if data.ref:
            payload["ref"] = data.ref
        if data.text is not None:
            payload["text"] = data.text
        if data.key:
            payload["key"] = data.key
        if data.value is not None:
            payload["value"] = data.value
        if data.tab_id:
            payload["tabId"] = data.tab_id
            path = f"/tabs/{data.tab_id}/action"
        else:
            path = "/action"
        status, body = await self._request("POST", f"{base}{path}", headers, json_body=payload)
        if status >= 400:
            return ToolResult(success=False, error=f"action failed ({status}): {body}", data=body if isinstance(body, dict) else {})
        ok = True
        if isinstance(body, dict) and body.get("success") is False:
            ok = False
        summary = f"action {data.kind}"
        if data.ref:
            summary += f" ref={data.ref}"
        if data.text:
            summary += f" text={data.text[:40]!r}"
        out = summary + (" OK" if ok else " FAILED")
        if isinstance(body, dict):
            out += "\n" + json.dumps(body, indent=2)[:2000]
        return ToolResult(success=ok, output=out, data=body if isinstance(body, dict) else {"body": body})

    async def _tabs(self, base: str, headers: dict[str, str]) -> ToolResult:
        status, body = await self._request("GET", f"{base}/tabs", headers)
        if status >= 400:
            return ToolResult(success=False, error=f"tabs failed ({status}): {body}")
        lines = []
        items = body if isinstance(body, list) else (body.get("tabs") if isinstance(body, dict) else [])
        if not isinstance(items, list):
            items = []
        for t in items[:30]:
            if isinstance(t, dict):
                tid = t.get("id") or t.get("tabId") or ""
                title = t.get("title") or ""
                url = t.get("url") or ""
                lines.append(f"- {tid}: {title} ({url})")
        if not lines:
            lines.append(json.dumps(body, indent=2)[:3000])
        return ToolResult(success=True, output="Open tabs:\n" + "\n".join(lines), data={"tabs": items})

    async def _simple_post(self, base: str, headers: dict[str, str], path: str, tab_id: str | None) -> ToolResult:
        payload: dict[str, Any] = {}
        if tab_id:
            payload["tabId"] = tab_id
            path = f"/tabs/{tab_id}{path}" if not path.startswith("/tabs/") else path
        status, body = await self._request("POST", f"{base}{path}", headers, json_body=payload or None)
        if status >= 400:
            return ToolResult(success=False, error=f"{path} failed ({status}): {body}")
        return ToolResult(
            success=True,
            output=json.dumps(body, indent=2) if isinstance(body, dict) else str(body),
            data=body if isinstance(body, dict) else {},
        )
