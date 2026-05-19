import pandas as pd

from game_decline.analysis.decline_detection import detect_decline_events
from game_decline.analysis.event_windows import build_event_windows


def test_detect_decline_events_finds_major_monthly_drop():
    metrics = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "date": "2026-01-01", "avg_ccu": 1000},
            {"game": "Example", "app_id": 1, "date": "2026-02-01", "avg_ccu": 650},
            {"game": "Example", "app_id": 1, "date": "2026-03-01", "avg_ccu": 640},
        ]
    )

    events = detect_decline_events(metrics, major_drop_threshold=0.30)

    assert events.to_dict("records") == [
        {
            "event_id": "1-2026-02-01",
            "game": "Example",
            "app_id": 1,
            "decline_start": "2026-01-01",
            "decline_end": "2026-02-01",
            "baseline_avg_ccu": 1000.0,
            "trough_avg_ccu": 650.0,
            "decline_fraction": 0.35,
            "decline_percent": 35.0,
            "source": "steamcharts_monthly",
        }
    ]


def test_build_event_windows_summarizes_reviews_and_nearby_events():
    decline_events = pd.DataFrame(
        [
            {
                "event_id": "1-2026-02-01",
                "game": "Example",
                "app_id": 1,
                "decline_start": "2026-01-01",
                "decline_end": "2026-02-01",
            }
        ]
    )
    reviews = pd.DataFrame(
        [
            {"game": "Example", "app_id": 1, "date": "2025-12-20", "positive_ratio": 0.8, "review_count": 10},
            {"game": "Example", "app_id": 1, "date": "2026-01-15", "positive_ratio": 0.4, "review_count": 20},
            {"game": "Example", "app_id": 1, "date": "2026-02-10", "positive_ratio": 0.5, "review_count": 10},
        ]
    )
    manual_events = pd.DataFrame(
        [
            {
                "game": "Example",
                "app_id": 1,
                "date": "2026-01-20",
                "event_type": "technical_failure",
                "title": "Server outage",
            }
        ]
    )

    windows = build_event_windows(decline_events, reviews, manual_events, window_days=30)
    row = windows.iloc[0].to_dict()

    assert row["pre_positive_ratio"] == 0.8
    assert row["during_positive_ratio"] == 0.4
    assert row["post_positive_ratio"] == 0.5
    assert row["nearby_event_count"] == 1
    assert row["nearby_event_types"] == "technical_failure"
