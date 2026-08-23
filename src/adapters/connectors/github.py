from __future__ import annotations

from typing import Any
import httpx


class GitHubConnector:
    def __init__(self, token: str | None = None, base_url: str = "https://api.github.com"):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_repo(self, owner: str, repo: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def list_issues(self, owner: str, repo: str, state: str = "open") -> list[dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self._headers(),
                params={"state": state, "per_page": 30},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_file(self, owner: str, repo: str, path: str, ref: str = "main") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(),
                params={"ref": ref},
            )
            resp.raise_for_status()
            return resp.json()

    async def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues",
                headers=self._headers(),
                json={"title": title, "body": body},
            )
            resp.raise_for_status()
            return resp.json()
