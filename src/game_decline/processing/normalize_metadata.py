from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from game_decline.config import GameConfig


SNAPSHOT_RE = re.compile(r"(?P<app_id>\d+)_(?P<timestamp>\d{8}T\d{6}Z)\.json$")


def latest_json_snapshots(source_dir: Path) -> dict[int, Path]:
    snapshots: dict[int, tuple[str, Path]] = {}
    for path in source_dir.glob("*.json"):
        match = SNAPSHOT_RE.match(path.name)
        if not match:
            continue
        app_id = int(match.group("app_id"))
        timestamp = match.group("timestamp")
        if app_id not in snapshots or timestamp > snapshots[app_id][0]:
            snapshots[app_id] = (timestamp, path)
    return {app_id: path for app_id, (_, path) in snapshots.items()}


def normalize_steamspy_snapshots(raw_root: Path, games: list[GameConfig]) -> pd.DataFrame:
    game_by_app = {game.app_id: game for game in games}
    rows: list[dict[str, object]] = []
    for app_id, path in latest_json_snapshots(raw_root / "steamspy").items():
        if app_id not in game_by_app:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        tags = payload.get("tags") or {}
        rows.append(
            {
                "game": game_by_app[app_id].game,
                "app_id": app_id,
                "owners": payload.get("owners", ""),
                "positive_reviews": int(payload.get("positive") or 0),
                "negative_reviews": int(payload.get("negative") or 0),
                "review_total": int(payload.get("positive") or 0) + int(payload.get("negative") or 0),
                "review_positive_ratio": _ratio(payload.get("positive"), payload.get("negative")),
                "average_playtime_forever": payload.get("average_forever"),
                "median_playtime_forever": payload.get("median_forever"),
                "developer": payload.get("developer", ""),
                "publisher": payload.get("publisher", ""),
                "steamspy_genre": payload.get("genre", ""),
                "top_tags": ";".join(list(tags.keys())[:5]) if isinstance(tags, dict) else "",
                "source_file": path.name,
            }
        )
    return pd.DataFrame(rows).sort_values(["game"], ignore_index=True) if rows else pd.DataFrame()


def _ratio(positive: object, negative: object) -> float | None:
    positive_count = int(positive or 0)
    negative_count = int(negative or 0)
    total = positive_count + negative_count
    if total == 0:
        return None
    return round(positive_count / total, 4)
