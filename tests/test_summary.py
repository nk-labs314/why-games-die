import pandas as pd

from game_decline.analysis.summary import build_decline_summary, build_monthly_features
from game_decline.validation import validate_processed_tables


def test_build_monthly_features_adds_change_columns():
    metrics = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "date": "2026-01-01", "avg_ccu": 100.0, "peak_ccu": 200},
            {"game": "Example", "app_id": 1, "date": "2026-02-01", "avg_ccu": 50.0, "peak_ccu": 100},
        ]
    )

    features = build_monthly_features(metrics)

    second = features.iloc[1].to_dict()
    assert second["avg_ccu_change"] == -50.0
    assert second["avg_ccu_pct_change"] == -0.5


def test_build_decline_summary_aggregates_game_level_risk():
    metrics = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "date": "2026-01-01", "avg_ccu": 100.0},
            {"game": "Example", "app_id": 1, "date": "2026-02-01", "avg_ccu": 50.0},
        ]
    )
    declines = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "decline_percent": 50.0},
            {"game": "Example", "app_id": 1, "decline_percent": 30.0},
        ]
    )

    summary = build_decline_summary(metrics, declines)

    row = summary.iloc[0].to_dict()
    assert row["decline_event_count"] == 2
    assert row["largest_decline_percent"] == 50.0
    assert row["first_month"] == "2026-01-01"
    assert row["last_month"] == "2026-02-01"
    assert row["median_monthly_pct_change"] == -0.5


def test_validate_processed_tables_flags_duplicate_metrics():
    metrics = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "date": "2026-01-01"},
            {"game": "Example", "app_id": 1, "date": "2026-01-01"},
        ]
    )

    errors = validate_processed_tables(metrics, pd.DataFrame(), pd.DataFrame())

    assert any("duplicate" in error for error in errors)
