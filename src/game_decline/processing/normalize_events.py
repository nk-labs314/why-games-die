from __future__ import annotations

from pathlib import Path

import pandas as pd


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

