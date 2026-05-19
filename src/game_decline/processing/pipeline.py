from __future__ import annotations

from pathlib import Path

import pandas as pd

from game_decline.config import GameConfig
from game_decline.processing.normalize_events import normalize_manual_events
from game_decline.processing.normalize_players import normalize_steamcharts_monthly
from game_decline.processing.normalize_reviews import normalize_review_snapshots


def build_game_daily_metrics(raw_root: Path, games: list[GameConfig]) -> pd.DataFrame:
    players = normalize_steamcharts_monthly(raw_root, games)
    reviews = normalize_review_snapshots(raw_root, games)
    if players.empty:
        return pd.DataFrame(
            columns=[
                "game",
                "app_id",
                "date",
                "avg_ccu",
                "peak_ccu",
                "source",
                "review_count",
                "positive_count",
                "negative_count",
                "positive_ratio",
                "avg_sentiment_score",
            ]
        )

    if reviews.empty:
        metrics = players.copy()
        for column in [
            "review_count",
            "positive_count",
            "negative_count",
            "positive_ratio",
            "avg_sentiment_score",
        ]:
            metrics[column] = pd.NA
        return metrics.drop(columns=["source_file"], errors="ignore")

    metrics = players.merge(reviews, on=["game", "app_id", "date"], how="left")
    return metrics.drop(columns=["source_file"], errors="ignore").sort_values(
        ["game", "date"], ignore_index=True
    )


def build_game_summary(metrics: pd.DataFrame, games: list[GameConfig]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    by_app = {app_id: frame for app_id, frame in metrics.groupby("app_id")} if not metrics.empty else {}
    for game in games:
        frame = by_app.get(game.app_id, pd.DataFrame())
        rows.append(
            {
                "game": game.game,
                "app_id": game.app_id,
                "player_data_available": not frame.empty and frame["avg_ccu"].notna().any(),
                "review_data_available": not frame.empty and frame.get("review_count", pd.Series(dtype=float)).notna().any(),
                "announcement_data_available": False,
                "steam_represents_lifecycle": game.steam_represents_lifecycle,
                "recommended_action": "include" if game.inclusion_status == "mvp" else game.inclusion_status,
            }
        )
    return pd.DataFrame(rows)


def write_processed_tables(
    raw_root: Path,
    processed_root: Path,
    interim_root: Path,
    games: list[GameConfig],
) -> dict[str, Path]:
    processed_root.mkdir(parents=True, exist_ok=True)
    interim_root.mkdir(parents=True, exist_ok=True)

    players = normalize_steamcharts_monthly(raw_root, games)
    reviews = normalize_review_snapshots(raw_root, games)
    events = normalize_manual_events(raw_root / "external_events" / "manual_events.csv")
    metrics = build_game_daily_metrics(raw_root, games)
    summary = build_game_summary(metrics, games)

    paths = {
        "normalized_player_counts": interim_root / "normalized_player_counts" / "steamcharts_monthly.csv",
        "normalized_reviews": interim_root / "normalized_reviews" / "steam_reviews_daily.csv",
        "normalized_events": interim_root / "normalized_events" / "events.csv",
        "game_daily_metrics": processed_root / "game_daily_metrics.csv",
        "game_summary": processed_root / "game_summary.csv",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    players.to_csv(paths["normalized_player_counts"], index=False)
    reviews.to_csv(paths["normalized_reviews"], index=False)
    events.to_csv(paths["normalized_events"], index=False)
    metrics.to_csv(paths["game_daily_metrics"], index=False)
    summary.to_csv(paths["game_summary"], index=False)
    return paths
