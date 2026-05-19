from __future__ import annotations

from pathlib import Path
from typing import Any

from game_decline.raw_store import write_json_snapshot
from game_decline.steam.http import HttpClient


STEAM_NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"


def fetch_announcements(
    app_id: int,
    client: HttpClient | None = None,
    count: int = 100,
) -> dict[str, Any]:
    http = client or HttpClient()
    return http.get_json(
        STEAM_NEWS_URL,
        params={"appid": app_id, "count": count, "format": "json"},
    )


def fetch_and_store_announcements(
    app_id: int,
    raw_root: Path,
    client: HttpClient | None = None,
) -> Path:
    payload = fetch_announcements(app_id, client)
    return write_json_snapshot(raw_root, "steam_announcements", app_id, payload)
