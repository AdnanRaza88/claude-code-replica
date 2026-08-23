from __future__ import annotations

from typing import Any, Callable, Optional
from pydantic import BaseModel, Field

from .base import Tool, ToolResult
from src.adapters.connectors.github import GitHubConnector


class GitHubInput(BaseModel):
    action: str = Field(
        description="One of: list_repos, get_user, get_repo, list_issues, get_file, search_repos"
    )
    owner: str | None = None
    repo: str | None = None
    path: str | None = None
    ref: str = "main"
    state: str = "open"
    query: str | None = None
    username: str | None = None
    per_page: int = 30


class GitHubTool(Tool):
    name = "github"
    description = (
        "Interact with the authenticated GitHub account. "
        "Use when the user asks about their repos, profile, bio, issues, or repository contents. "
        "Requires a GitHub token set in Connectors. "
        "Actions: list_repos, get_user, get_repo, list_issues, get_file, search_repos."
    )
    risk = "low"
    input_schema = GitHubInput

    def __init__(self, get_token: Optional[Callable[[], Optional[str]]] = None):
        self.get_token = get_token or (lambda: None)

    def _connector(self, runtime: Any = None) -> GitHubConnector | None:
        token = None
        if self.get_token:
            token = self.get_token()
        if not token and runtime is not None and hasattr(runtime, "get_credential"):
            token = runtime.get_credential("github")
        if not token:
            return None
        return GitHubConnector(token=token)

    async def execute(self, input_data: dict[str, Any], runtime: Any = None) -> ToolResult:
        try:
            data = GitHubInput(**input_data)
            connector = self._connector(runtime)
            if connector is None:
                return ToolResult(
                    success=False,
                    error="GitHub token not configured. Add it under Connectors → GitHub token in the sidebar.",
                )

            action = data.action.strip().lower()

            if action == "list_repos":
                return await self._list_repos(connector, data)
            if action == "get_user":
                return await self._get_user(connector, data)
            if action == "get_repo":
                if not data.owner or not data.repo:
                    return ToolResult(success=False, error="owner and repo required")
                result = await connector.get_repo(data.owner, data.repo)
                return ToolResult(success=True, output=self._fmt_repo(result), data=result)
            if action == "list_issues":
                if not data.owner or not data.repo:
                    return ToolResult(success=False, error="owner and repo required")
                issues = await connector.list_issues(data.owner, data.repo, state=data.state)
                lines = [f"- #{i.get('number')}: {i.get('title')} [{i.get('state')}]" for i in issues[:40]]
                return ToolResult(
                    success=True,
                    output=f"{len(issues)} issues ({data.state}):\n" + "\n".join(lines),
                    data={"count": len(issues), "issues": issues[:40]},
                )
            if action == "get_file":
                if not data.owner or not data.repo or not data.path:
                    return ToolResult(success=False, error="owner, repo and path required")
                result = await connector.get_file(data.owner, data.repo, data.path, ref=data.ref)
                return ToolResult(success=True, output=str(result)[:8000], data=result)
            if action == "search_repos":
                return await self._search_repos(connector, data)

            return ToolResult(
                success=False,
                error=f"unknown action '{data.action}'. Use: list_repos, get_user, get_repo, list_issues, get_file, search_repos",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e)[:500])

    async def _list_repos(self, connector: GitHubConnector, data: GitHubInput) -> ToolResult:
        import httpx
        async with httpx.AsyncClient(timeout=connector.timeout) as client:
            resp = await client.get(
                f"{connector.base_url}/user/repos",
                headers=connector._headers(),
                params={"per_page": min(data.per_page, 100), "sort": "updated", "affiliation": "owner,collaborator"},
            )
            resp.raise_for_status()
            repos = resp.json()
        lines = []
        for r in repos:
            priv = "private" if r.get("private") else "public"
            lines.append(f"- {r.get('full_name')} ({priv}) — {r.get('description') or 'no description'}")
        return ToolResult(
            success=True,
            output=f"Found {len(repos)} repositories:\n" + "\n".join(lines),
            data={"count": len(repos), "repos": [{"full_name": r.get("full_name"), "private": r.get("private"), "description": r.get("description")} for r in repos]},
        )

    async def _get_user(self, connector: GitHubConnector, data: GitHubInput) -> ToolResult:
        import httpx
        url = f"{connector.base_url}/user"
        if data.username:
            url = f"{connector.base_url}/users/{data.username}"
        async with httpx.AsyncClient(timeout=connector.timeout) as client:
            resp = await client.get(url, headers=connector._headers())
            resp.raise_for_status()
            user = resp.json()
        bio = user.get("bio") or "(no bio set)"
        summary = (
            f"Login: {user.get('login')}\n"
            f"Name: {user.get('name') or '(not set)'}\n"
            f"Bio: {bio}\n"
            f"Public repos: {user.get('public_repos')}\n"
            f"Followers: {user.get('followers')} | Following: {user.get('following')}\n"
            f"Location: {user.get('location') or '(not set)'}\n"
            f"Company: {user.get('company') or '(not set)'}\n"
            f"Blog: {user.get('blog') or '(not set)'}\n"
            f"Profile: {user.get('html_url')}"
        )
        return ToolResult(success=True, output=summary, data=user)

    async def _search_repos(self, connector: GitHubConnector, data: GitHubInput) -> ToolResult:
        import httpx
        q = data.query or ""
        if not q:
            return ToolResult(success=False, error="query required for search_repos")
        async with httpx.AsyncClient(timeout=connector.timeout) as client:
            resp = await client.get(
                f"{connector.base_url}/search/repositories",
                headers=connector._headers(),
                params={"q": q, "per_page": min(data.per_page, 30)},
            )
            resp.raise_for_status()
            payload = resp.json()
        items = payload.get("items", [])
        lines = [f"- {i.get('full_name')} ★{i.get('stargazers_count')} — {i.get('description') or ''}" for i in items]
        return ToolResult(
            success=True,
            output=f"Search '{q}': {payload.get('total_count', 0)} total, showing {len(items)}\n" + "\n".join(lines),
            data=payload,
        )

    def _fmt_repo(self, r: dict) -> str:
        return (
            f"{r.get('full_name')}\n"
            f"Description: {r.get('description') or '(none)'}\n"
            f"Visibility: {'private' if r.get('private') else 'public'}\n"
            f"Stars: {r.get('stargazers_count')} | Forks: {r.get('forks_count')}\n"
            f"Language: {r.get('language')}\n"
            f"Default branch: {r.get('default_branch')}\n"
            f"URL: {r.get('html_url')}"
        )
