from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from game_decline.config import GameConfig


SNAPSHOT_RE = re.compile(r"(?P<app_id>\d+)_(?P<timestamp>\d{8}T\d{6}Z)\.csv$")


def latest_snapshots(source_dir: Path) -> dict[int, Path]:
    snapshots: dict[int, tuple[str, Path]] = {}
    for path in source_dir.glob("*.csv"):
        match = SNAPSHOT_RE.match(path.name)
        if not match:
            continue
        app_id = int(match.group("app_id"))
        timestamp = match.group("timestamp")
        if app_id not in snapshots or timestamp > snapshots[app_id][0]:
            snapshots[app_id] = (timestamp, path)
    return {app_id: path for app_id, (_, path) in snapshots.items()}


def normalize_steamcharts_monthly(raw_root: Path, games: list[GameConfig]) -> pd.DataFrame:
    game_by_app = {game.app_id: game.game for game in games}
    rows: list[dict[str, object]] = []
    for app_id, path in latest_snapshots(raw_root / "steamcharts").items():
        if app_id not in game_by_app:
            continue
        source = pd.read_csv(path)
        for _, row in source.iterrows():
            date = pd.to_datetime(row.get("month"), format="%B %Y", errors="coerce")
            if pd.isna(date):
                continue
            rows.append(
                {
                    "game": game_by_app[app_id],
                    "app_id": app_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "avg_ccu": float(row["avg_players"]) if pd.notna(row.get("avg_players")) else None,
                    "peak_ccu": int(row["peak_players"]) if pd.notna(row.get("peak_players")) else None,
                    "source": "steamcharts",
                    "source_file": path.name,
                }
            )
    return pd.DataFrame(
        rows,
        columns=["game", "app_id", "date", "avg_ccu", "peak_ccu", "source", "source_file"],
    ).sort_values(["game", "date"], ignore_index=True)

