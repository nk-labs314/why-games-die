from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


DEFAULT_USER_AGENT = (
    "game-decline-analysis/0.1 "
    "(educational data science project; contact: local research script)"
)


@dataclass(frozen=True)
class HttpClient:
    timeout_seconds: int = 30
    user_agent: str = DEFAULT_USER_AGENT

    def get_text(self, url: str, params: dict[str, Any] | None = None) -> str:
        response = requests.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()
        return response.text

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
            headers={"User-Agent": self.user_agent},
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object from {response.url}")
        return payload
