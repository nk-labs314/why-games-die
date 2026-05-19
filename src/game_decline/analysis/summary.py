from __future__ import annotations

import pandas as pd


def build_monthly_features(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    features = metrics.copy()
    features["date"] = pd.to_datetime(features["date"], errors="coerce")
    features = features.dropna(subset=["date"]).sort_values(["app_id", "date"])
    features["avg_ccu_change"] = features.groupby("app_id")["avg_ccu"].diff()
    features["avg_ccu_pct_change"] = features.groupby("app_id")["avg_ccu"].pct_change()
    features["peak_ccu_change"] = features.groupby("app_id")["peak_ccu"].diff() if "peak_ccu" in features else pd.NA
    features["date"] = features["date"].dt.strftime("%Y-%m-%d")
    return features.reset_index(drop=True)


def build_decline_summary(metrics: pd.DataFrame, decline_events: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    metrics = metrics.copy()
    metrics["date"] = pd.to_datetime(metrics["date"], errors="coerce")
    summaries: list[dict[str, object]] = []
    for (game, app_id), frame in metrics.groupby(["game", "app_id"], sort=False):
        frame = frame.dropna(subset=["date", "avg_ccu"]).sort_values("date")
        if frame.empty:
            continue
        game_declines = decline_events[decline_events["app_id"] == app_id] if not decline_events.empty else pd.DataFrame()
        peak = float(frame["avg_ccu"].max())
        latest = float(frame.iloc[-1]["avg_ccu"])
        summaries.append(
            {
                "game": game,
                "app_id": int(app_id),
                "first_month": frame.iloc[0]["date"].strftime("%Y-%m-%d"),
                "last_month": frame.iloc[-1]["date"].strftime("%Y-%m-%d"),
                "months_observed": int(len(frame)),
                "peak_avg_ccu": round(peak, 2),
                "latest_avg_ccu": round(latest, 2),
                "latest_vs_peak_percent": round(((latest - peak) / peak) * 100, 2) if peak else None,
                "decline_event_count": int(len(game_declines)),
                "largest_decline_percent": round(float(game_declines["decline_percent"].max()), 2)
                if not game_declines.empty
                else 0.0,
                "avg_monthly_pct_change": round(float(frame["avg_ccu"].pct_change().mean()), 4)
                if len(frame) > 1
                else None,
            }
        )
    return pd.DataFrame(summaries).sort_values(
        ["decline_event_count", "largest_decline_percent"], ascending=[False, False], ignore_index=True
    )
