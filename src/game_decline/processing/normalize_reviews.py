from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from game_decline.config import GameConfig


SNAPSHOT_RE = re.compile(r"(?P<app_id>\d+)_(?P<timestamp>\d{8}T\d{6}Z)\.json$")


def _latest_review_snapshots(source_dir: Path) -> dict[int, Path]:
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


def normalize_review_snapshots(raw_root: Path, games: list[GameConfig]) -> pd.DataFrame:
    game_by_app = {game.app_id: game.game for game in games}
    rows: list[dict[str, object]] = []
    for app_id, path in _latest_review_snapshots(raw_root / "steam_reviews").items():
        if app_id not in game_by_app:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for review in payload.get("reviews", []):
            created_at = pd.to_datetime(review.get("timestamp_created"), unit="s", errors="coerce")
            if pd.isna(created_at):
                continue
            rows.append(
                {
                    "game": game_by_app[app_id],
                    "app_id": app_id,
                    "date": created_at.strftime("%Y-%m-%d"),
                    "voted_up": bool(review.get("voted_up")),
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "game",
                "app_id",
                "date",
                "review_count",
                "positive_count",
                "negative_count",
                "positive_ratio",
                "avg_sentiment_score",
            ]
        )

    reviews = pd.DataFrame(rows)
    grouped = reviews.groupby(["game", "app_id", "date"], as_index=False).agg(
        review_count=("voted_up", "size"),
        positive_count=("voted_up", "sum"),
    )
    grouped["negative_count"] = grouped["review_count"] - grouped["positive_count"]
    grouped["positive_ratio"] = grouped["positive_count"] / grouped["review_count"]
    grouped["avg_sentiment_score"] = grouped["positive_ratio"].mul(2).sub(1)
    return grouped.sort_values(["game", "date"], ignore_index=True)
