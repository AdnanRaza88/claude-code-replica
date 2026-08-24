from __future__ import annotations

import json
import re
from typing import Any, Awaitable, Callable, Optional

from src.harness.sandbox import AgentSandbox
from src.harness.types import Phase
from src.models.provider import Message, ToolSpec
from src.models.events import EventType


ToolInvoker = Callable[[str, dict], Awaitable[Any]]
EventEmitter = Callable[..., None]
ProviderInvoker = Callable[..., Awaitable[Any]]


class CognitiveLoop:
    """
    Compact multi-step harness loop for one agent sandbox.

    Design goals (DeepSeek-inspired, Python-native, Streamlit-safe):
    - Per-agent isolation only (uses AgentSandbox)
    - Structured phases: THINK → REASON → ACT → OBSERVE → (optional VERIFY) → DONE
    - Visible intermediate steps via events
    - Hard step budget so context stays small
    - Falls back gracefully if model ignores structured format
    """

    def __init__(
        self,
        sandbox: AgentSandbox,
        invoke_provider: ProviderInvoker,
        invoke_tool: ToolInvoker,
        emit: EventEmitter,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        tool_specs: Optional[list[ToolSpec]] = None,
        system_prompt: str = "",
    ):
        self.sb = sandbox
        self.invoke_provider = invoke_provider
        self.invoke_tool = invoke_tool
        self.emit = emit
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tool_specs = tool_specs or []
        self.system_prompt = system_prompt

    async def run(self) -> dict[str, Any]:
        sb = self.sb
        if not sb.budget_ok():
            sb.fail("sandbox budget exceeded before start")
            return self._result("failed", sb.error or "budget")

        think_prompt = self._build_think_prompt()
        self.emit(
            EventType.THINKING,
            message=f"[{sb.domain}] thinking about objective",
            payload={"phase": "think", "sandbox_id": sb.sandbox_id},
        )
        think_text = await self._ask(think_prompt, expect_json=False)
        sb.think(think_text or "considering approach")
        self.emit(
            EventType.THINKING,
            message=(think_text or "")[:240],
            payload={"phase": "think", "content": (think_text or "")[:800]},
        )

        if not sb.budget_ok() or sb.cancelled:
            return self._abort()

        reason_prompt = self._build_reason_prompt()
        self.emit(
            EventType.REASONING,
            message=f"[{sb.domain}] reasoning next action",
            payload={"phase": "reason"},
        )
        reason_raw = await self._ask(reason_prompt, expect_json=True)
        plan = self._parse_plan(reason_raw)
        sb.reason(plan.get("reasoning") or reason_raw or "proceed")
        self.emit(
            EventType.REASONING,
            message=(plan.get("reasoning") or reason_raw or "")[:240],
            payload={"phase": "reason", "plan": plan},
        )

        sources: list[dict] = []
        tool_summaries: list[str] = []

        actions = plan.get("actions") or []
        if not actions and plan.get("tool"):
            actions = [{"tool": plan["tool"], "input": plan.get("input") or {}}]

        for action in actions[: max(0, sb.max_steps - len(sb.trace.steps) - 1)]:
            if not sb.budget_ok() or sb.cancelled:
                break
            tool_name = (action.get("tool") or "").strip()
            tool_input = action.get("input") or {}
            if not tool_name:
                continue
            if sb.allowed_tools and tool_name not in sb.allowed_tools:
                sb.observe(tool_name, f"tool not allowed for this agent: {tool_name}", False)
                continue

            sb.act_tool(tool_name, tool_input)
            self.emit(
                EventType.REASONING,
                message=f"[{sb.domain}] calling {tool_name}",
                payload={"tool": tool_name, "input": tool_input},
            )
            self.emit(
                EventType.TOOL_STARTED,
                message=f"tool {tool_name}",
                payload={"tool": tool_name},
            )

            try:
                result = await self.invoke_tool(tool_name, tool_input)
            except Exception as e:
                result = type("R", (), {"success": False, "output": "", "error": str(e), "data": {}})()

            success = bool(getattr(result, "success", False))
            output = getattr(result, "output", None) or getattr(result, "error", "") or ""
            data = getattr(result, "data", None) or {}
            sb.observe(tool_name, str(output), success)
            tool_summaries.append(f"{tool_name}: {str(output)[:400]}")
            self.emit(
                EventType.TOOL_FINISHED,
                message=f"{tool_name} {'ok' if success else 'fail'}",
                payload={"tool": tool_name, "success": success},
            )
            for src in (data.get("sources") or []):
                sources.append(src)
                self.emit(
                    EventType.SOURCE_FOUND,
                    message=src.get("title") or src.get("url") or "source",
                    payload=src,
                )

        if not sb.budget_ok() or sb.cancelled:
            return self._abort()

        final_prompt = self._build_final_prompt(tool_summaries)
        final_text = await self._ask(final_prompt, expect_json=False)
        summary = (final_text or "").strip() or "\n".join(tool_summaries) or sb.recent_context(4)

        if sb.enable_verify and summary:
            conf = 0.7 if tool_summaries else 0.55
            sb.verify("checked coherence of final answer against objective", confidence=conf)

        if sources:
            cite = []
            for s in sources[:8]:
                title = s.get("title") or "Source"
                url = s.get("url") or ""
                cite.append(f"- [{title}]({url})" if url else f"- {title}")
            summary = summary.rstrip() + "\n\n**Sources**\n" + "\n".join(cite)

        sb.finalize(summary, sources=sources)
        return self._result("success", summary, sources=sources)

    def _build_think_prompt(self) -> list[Message]:
        sys = self.system_prompt + (
            "\n\nYou are inside an isolated agent sandbox. "
            "First think briefly about the objective, constraints, and best approach. "
            "Reply with 2-5 short sentences of thinking only. No tools yet."
        )
        user = (
            f"Objective: {self.sb.objective}\n"
            f"Domain: {self.sb.domain}\n"
            f"Allowed tools: {', '.join(self.sb.allowed_tools) or 'none'}\n"
        )
        return [Message(role="system", content=sys), Message(role="user", content=user)]

    def _build_reason_prompt(self) -> list[Message]:
        sys = (
            self.system_prompt
            + "\n\nYou are still in the isolated sandbox. "
            "Given your previous thinking, decide the next actions. "
            "Reply with a single JSON object only:\n"
            '{"reasoning":"<short>","actions":[{"tool":"<name>","input":{...}}],"done":false}\n'
            "If no tool is needed, use empty actions and set done=true."
        )
        user = (
            f"Objective: {self.sb.objective}\n"
            f"Recent sandbox steps:\n{self.sb.recent_context(6)}\n"
            f"Allowed tools: {', '.join(self.sb.allowed_tools) or 'none'}\n"
        )
        return [Message(role="system", content=sys), Message(role="user", content=user)]

    def _build_final_prompt(self, tool_summaries: list[str]) -> list[Message]:
        sys = (
            self.system_prompt
            + "\n\nProduce the final answer for this agent only. "
            "Be concise, accurate, and grounded in the tool results and prior steps. "
            "Do not invent facts."
        )
        tools_block = "\n".join(tool_summaries) if tool_summaries else "(no tools used)"
        user = (
            f"Objective: {self.sb.objective}\n"
            f"Sandbox steps:\n{self.sb.recent_context(8)}\n"
            f"Tool results:\n{tools_block}\n\n"
            "Write the final response for the user."
        )
        return [Message(role="system", content=sys), Message(role="user", content=user)]

    async def _ask(self, messages: list[Message], expect_json: bool = False) -> str:
        try:
            resp = await self.invoke_provider(
                messages,
                model=self.model,
                tools=None,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            content = (getattr(resp, "content", None) or "") or ""
            if expect_json:
                return content
            return content.strip()
        except Exception as e:
            self.sb.fail(str(e))
            return ""

    def _parse_plan(self, raw: str) -> dict[str, Any]:
        if not raw:
            return {"reasoning": "", "actions": [], "done": True}
        text = raw.strip()
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            text = m.group(0)
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
        return {"reasoning": raw[:600], "actions": [], "done": True}

    def _result(
        self,
        status: str,
        summary: str,
        sources: Optional[list] = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "summary": summary,
            "artifacts": [],
            "findings": [],
            "open_questions": list(self.sb.trace.open_questions) if self.sb.trace else [],
            "verification": {
                "confidence": self.sb.trace.confidence if self.sb.trace else 0.0,
                "steps": len(self.sb.trace.steps) if self.sb.trace else 0,
            },
            "sources": sources or (self.sb.trace.sources if self.sb.trace else []),
            "reasoning": self.sb.recent_context(8),
            "active_domain": self.sb.domain,
            "sandbox_id": self.sb.sandbox_id,
            "harness": "cognitive_loop_v1",
        }

    def _abort(self) -> dict[str, Any]:
        msg = self.sb.error or "cancelled or budget exceeded"
        if self.sb.trace and not self.sb.trace.final_summary:
            self.sb.fail(msg)
        return self._result("failed" if self.sb.error else "partial", msg)
