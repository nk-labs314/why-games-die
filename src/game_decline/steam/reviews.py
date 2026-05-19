from __future__ import annotations

from pathlib import Path
from typing import Any

from game_decline.raw_store import write_json_snapshot
from game_decline.steam.http import HttpClient


STEAM_REVIEWS_URL = "https://store.steampowered.com/appreviews/{app_id}"


def fetch_reviews(
    app_id: int,
    client: HttpClient | None = None,
    num_per_page: int = 100,
    language: str = "english",
) -> dict[str, Any]:
    http = client or HttpClient()
    return http.get_json(
        STEAM_REVIEWS_URL.format(app_id=app_id),
        params={
            "json": 1,
            "filter": "recent",
            "language": language,
            "purchase_type": "all",
            "num_per_page": num_per_page,
        },
    )


def fetch_and_store_reviews(
    app_id: int,
    raw_root: Path,
    client: HttpClient | None = None,
) -> Path:
    payload = fetch_reviews(app_id, client)
    return write_json_snapshot(raw_root, "steam_reviews", app_id, payload)
