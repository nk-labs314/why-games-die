import pandas as pd

from game_decline.report.build_report import build_markdown_report


def test_build_markdown_report_states_data_limits_when_no_declines():
    metrics = pd.DataFrame(
        [{"game": "Dota 2", "app_id": 570, "date": "2026-01-01", "avg_ccu": 1000}]
    )
    decline_events = pd.DataFrame()
    event_windows = pd.DataFrame()
    game_summary = pd.DataFrame(
        [
            {
                "game": "Dota 2",
                "app_id": 570,
                "player_data_available": True,
                "review_data_available": False,
            }
        ]
    )

    markdown = build_markdown_report(metrics, decline_events, event_windows, game_summary, [])

    assert "Steam Game Decline Analysis" in markdown
    assert "No major decline events were detected" in markdown
    assert "does not prove causation" in markdown
