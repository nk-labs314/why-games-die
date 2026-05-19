from __future__ import annotations

import pandas as pd


def validate_processed_tables(
    metrics: pd.DataFrame,
    decline_events: pd.DataFrame,
    event_windows: pd.DataFrame,
) -> list[str]:
    errors: list[str] = []
    if not metrics.empty:
        duplicate_mask = metrics.duplicated(subset=["game", "app_id", "date"], keep=False)
        if duplicate_mask.any():
            errors.append("game_daily_metrics has duplicate game + app_id + date rows")
        if "avg_ccu" in metrics.columns and (metrics["avg_ccu"].dropna() < 0).any():
            errors.append("game_daily_metrics has negative avg_ccu values")
    if not decline_events.empty:
        starts = pd.to_datetime(decline_events["decline_start"], errors="coerce")
        ends = pd.to_datetime(decline_events["decline_end"], errors="coerce")
        if (ends < starts).any():
            errors.append("decline_events contains a decline_end before decline_start")
        if decline_events["event_id"].duplicated().any():
            errors.append("decline_events has duplicate event_id values")
    if not event_windows.empty and not decline_events.empty:
        missing = set(event_windows["event_id"]) - set(decline_events["event_id"])
        if missing:
            errors.append("event_windows references event_id values missing from decline_events")
    return errors
