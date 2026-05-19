from __future__ import annotations

from pathlib import Path

import json
import pandas as pd

from game_decline.config import GameConfig
from game_decline.processing.normalize_metadata import latest_json_snapshots


EVENT_COLUMNS = [
    "game",
    "app_id",
    "date",
    "event_type",
    "event_source",
    "title",
    "summary",
    "url",
    "confidence",
]


def normalize_manual_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=EVENT_COLUMNS)
    events = pd.read_csv(path)
    for column in EVENT_COLUMNS:
        if column not in events.columns:
            events[column] = ""
    events = events[EVENT_COLUMNS].copy()
    events["date"] = pd.to_datetime(events["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    events = events.dropna(subset=["date"])
    return events.sort_values(["game", "date", "event_type"], ignore_index=True)


def normalize_steam_announcements(raw_root: Path, games: list[GameConfig]) -> pd.DataFrame:
    game_by_app = {game.app_id: game.game for game in games}
    rows: list[dict[str, object]] = []
    for app_id, path in latest_json_snapshots(raw_root / "steam_announcements").items():
        if app_id not in game_by_app:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for item in payload.get("appnews", {}).get("newsitems", []):
            published = pd.to_datetime(item.get("date"), unit="s", errors="coerce")
            if pd.isna(published):
                continue
            rows.append(
                {
                    "game": game_by_app[app_id],
                    "app_id": app_id,
                    "date": published.strftime("%Y-%m-%d"),
                    "event_type": "steam_announcement",
                    "event_source": "steam_announcements",
                    "title": item.get("title", ""),
                    "summary": _clip(item.get("contents", "")),
                    "url": item.get("url", ""),
                    "confidence": "medium",
                }
            )
    return pd.DataFrame(rows, columns=EVENT_COLUMNS).sort_values(["game", "date"], ignore_index=True)


def combine_event_sources(manual_events: pd.DataFrame, steam_announcements: pd.DataFrame) -> pd.DataFrame:
    frames = [frame for frame in [manual_events, steam_announcements] if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=EVENT_COLUMNS)
    return pd.concat(frames, ignore_index=True)[EVENT_COLUMNS].sort_values(
        ["game", "date", "event_type"], ignore_index=True
    )


def _clip(text: str, limit: int = 240) -> str:
    clean = " ".join(str(text).split())
    return clean if len(clean) <= limit else clean[: limit - 3] + "..."
