from __future__ import annotations

import pandas as pd


WINDOW_COLUMNS = [
    "event_id",
    "game",
    "app_id",
    "pre_positive_ratio",
    "during_positive_ratio",
    "post_positive_ratio",
    "nearby_event_count",
    "nearby_event_types",
    "classification",
]


def build_event_windows(
    decline_events: pd.DataFrame,
    reviews: pd.DataFrame,
    manual_events: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    if decline_events.empty:
        return pd.DataFrame(columns=WINDOW_COLUMNS)

    reviews = reviews.copy()
    manual_events = manual_events.copy()
    if not reviews.empty:
        reviews["date"] = pd.to_datetime(reviews["date"], errors="coerce")
    if not manual_events.empty:
        manual_events["date"] = pd.to_datetime(manual_events["date"], errors="coerce")

    rows: list[dict[str, object]] = []
    for _, event in decline_events.iterrows():
        start = pd.to_datetime(event["decline_start"])
        end = pd.to_datetime(event["decline_end"])
        game_reviews = reviews[
            (reviews.get("app_id") == event["app_id"]) if not reviews.empty else []
        ] if not reviews.empty else pd.DataFrame()
        game_events = manual_events[
            (manual_events.get("app_id") == event["app_id"]) if not manual_events.empty else []
        ] if not manual_events.empty else pd.DataFrame()

        nearby = _between(game_events, start - pd.Timedelta(days=window_days), end + pd.Timedelta(days=window_days))
        event_types = ""
        if not nearby.empty and "event_type" in nearby.columns:
            event_types = ";".join(sorted(set(nearby["event_type"].dropna().astype(str))))

        rows.append(
            {
                "event_id": event["event_id"],
                "game": event["game"],
                "app_id": int(event["app_id"]),
                "pre_positive_ratio": _weighted_positive_ratio(
                    _between(game_reviews, start - pd.Timedelta(days=window_days), start - pd.Timedelta(days=1))
                ),
                "during_positive_ratio": _weighted_positive_ratio(_between(game_reviews, start, end)),
                "post_positive_ratio": _weighted_positive_ratio(
                    _between(game_reviews, end + pd.Timedelta(days=1), end + pd.Timedelta(days=window_days))
                ),
                "nearby_event_count": int(len(nearby)),
                "nearby_event_types": event_types,
                "classification": "unknown",
            }
        )
    return pd.DataFrame(rows, columns=WINDOW_COLUMNS)


def _between(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if frame.empty or "date" not in frame.columns:
        return pd.DataFrame()
    return frame[(frame["date"] >= start) & (frame["date"] <= end)]


def _weighted_positive_ratio(frame: pd.DataFrame) -> float | None:
    if frame.empty or "positive_ratio" not in frame.columns:
        return None
    weights = frame.get("review_count")
    if weights is None or weights.isna().all() or weights.sum() == 0:
        return round(float(frame["positive_ratio"].mean()), 4)
    return round(float((frame["positive_ratio"] * weights).sum() / weights.sum()), 4)
