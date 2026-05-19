from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.analysis.decline_detection import detect_decline_events
from game_decline.analysis.event_windows import build_event_windows
from game_decline.config import PROJECT_ROOT, load_yaml


def main() -> int:
    processed_root = PROJECT_ROOT / "data" / "processed"
    interim_root = PROJECT_ROOT / "data" / "interim"
    config = load_yaml(PROJECT_ROOT / "config" / "analysis.yaml")
    threshold = float(config.get("player", {}).get("major_drop_threshold", 0.30))
    window_days = int(config.get("events", {}).get("nearby_window_days", 30))

    metrics = pd.read_csv(processed_root / "game_daily_metrics.csv")
    reviews_path = interim_root / "normalized_reviews" / "steam_reviews_daily.csv"
    events_path = interim_root / "normalized_events" / "events.csv"
    reviews = pd.read_csv(reviews_path) if reviews_path.exists() else pd.DataFrame()
    events = pd.read_csv(events_path) if events_path.exists() else pd.DataFrame()

    decline_events = detect_decline_events(metrics, major_drop_threshold=threshold)
    event_windows = build_event_windows(decline_events, reviews, events, window_days=window_days)

    decline_events.to_csv(processed_root / "decline_events.csv", index=False)
    event_windows.to_csv(processed_root / "event_windows.csv", index=False)
    print(f"[OK] decline_events: {len(decline_events)} rows")
    print(f"[OK] event_windows: {len(event_windows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
