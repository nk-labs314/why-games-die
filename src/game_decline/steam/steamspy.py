from __future__ import annotations

from pathlib import Path
from typing import Any

from game_decline.raw_store import write_json_snapshot
from game_decline.steam.http import HttpClient


STEAMSPY_API_URL = "https://steamspy.com/api.php"


def fetch_appdetails(app_id: int, client: HttpClient | None = None) -> dict[str, Any]:
    http = client or HttpClient()
    payload = http.get_json(
        STEAMSPY_API_URL,
        params={"request": "appdetails", "appid": app_id},
    )
    if "appid" not in payload and "name" not in payload:
        raise ValueError(f"SteamSpy returned an unexpected payload for app_id={app_id}")
    return payload


def fetch_and_store_appdetails(
    app_id: int,
    raw_root: Path,
    client: HttpClient | None = None,
) -> Path:
    payload = fetch_appdetails(app_id, client)
    return write_json_snapshot(raw_root, "steamspy", app_id, payload)
