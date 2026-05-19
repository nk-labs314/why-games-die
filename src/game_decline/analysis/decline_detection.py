from __future__ import annotations

import pandas as pd


DECLINE_COLUMNS = [
    "event_id",
    "game",
    "app_id",
    "decline_start",
    "decline_end",
    "baseline_avg_ccu",
    "trough_avg_ccu",
    "decline_fraction",
    "decline_percent",
    "source",
]


def detect_decline_events(
    metrics: pd.DataFrame,
    major_drop_threshold: float = 0.30,
) -> pd.DataFrame:
    if metrics.empty or "avg_ccu" not in metrics.columns:
        return pd.DataFrame(columns=DECLINE_COLUMNS)

    rows: list[dict[str, object]] = []
    metrics = metrics.dropna(subset=["avg_ccu"]).copy()
    metrics["date"] = pd.to_datetime(metrics["date"], errors="coerce")
    metrics = metrics.dropna(subset=["date"]).sort_values(["app_id", "date"])

    for (_, app_id), frame in metrics.groupby(["game", "app_id"], sort=False):
        frame = frame.sort_values("date").reset_index(drop=True)
        for index in range(1, len(frame)):
            previous = frame.iloc[index - 1]
            current = frame.iloc[index]
            baseline = float(previous["avg_ccu"])
            trough = float(current["avg_ccu"])
            if baseline <= 0:
                continue
            decline_fraction = (baseline - trough) / baseline
            if decline_fraction >= major_drop_threshold:
                decline_end = current["date"].strftime("%Y-%m-%d")
                rows.append(
                    {
                        "event_id": f"{int(app_id)}-{decline_end}",
                        "game": current["game"],
                        "app_id": int(app_id),
                        "decline_start": previous["date"].strftime("%Y-%m-%d"),
                        "decline_end": decline_end,
                        "baseline_avg_ccu": baseline,
                        "trough_avg_ccu": trough,
                        "decline_fraction": round(decline_fraction, 4),
                        "decline_percent": round(decline_fraction * 100, 2),
                        "source": "steamcharts_monthly",
                    }
                )
    return pd.DataFrame(rows, columns=DECLINE_COLUMNS)

