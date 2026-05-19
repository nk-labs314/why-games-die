from game_decline.config import GameConfig
from game_decline.processing.normalize_events import normalize_manual_events
from game_decline.processing.normalize_metadata import normalize_steamspy_snapshots
from game_decline.processing.normalize_players import normalize_steamcharts_monthly
from game_decline.processing.normalize_reviews import normalize_review_snapshots


FIXTURE_ROOT = __import__("pathlib").Path(__file__).parent / "fixtures" / "normalize"


def test_normalize_steamcharts_monthly_uses_latest_snapshot():
    raw_root = FIXTURE_ROOT / "raw"

    games = [
        GameConfig(
            game="Dota 2",
            app_id=570,
            genre="MOBA",
            expected_decline_profile="alive_control",
            steam_lifecycle_quality="special_case",
            inclusion_status="mvp",
            steam_represents_lifecycle=True,
        )
    ]

    normalized = normalize_steamcharts_monthly(raw_root, games)

    assert normalized.to_dict("records") == [
        {
            "game": "Dota 2",
            "app_id": 570,
            "date": "2026-02-01",
            "avg_ccu": 800.0,
            "peak_ccu": 1800,
            "source": "steamcharts",
            "source_file": "570_20260201T000000Z.csv",
        }
    ]


def test_normalize_manual_events_keeps_required_columns():
    normalized = normalize_manual_events(FIXTURE_ROOT / "manual_events.csv")

    assert normalized.to_dict("records")[0]["event_type"] == "major_update"
    assert normalized.to_dict("records")[0]["date"] == "2026-02-15"


def test_normalize_steam_announcements_adds_public_news_events():
    from game_decline.processing.normalize_events import normalize_steam_announcements

    normalized = normalize_steam_announcements(FIXTURE_ROOT / "raw", [GameConfig("Dota 2", 570, "MOBA", "control", "special_case", "mvp", True)])

    assert normalized.to_dict("records")[0]["event_source"] == "steam_announcements"
    assert normalized.to_dict("records")[0]["title"] == "Gameplay Update"


def test_normalize_review_snapshots_aggregates_daily_rows():
    raw_root = FIXTURE_ROOT / "raw"
    games = [
        GameConfig("Dota 2", 570, "MOBA", "control", "special_case", "mvp", True)
    ]

    normalized = normalize_review_snapshots(raw_root, games)

    row = normalized.iloc[0].to_dict()
    assert row["game"] == "Dota 2"
    assert row["review_count"] == 2
    assert row["positive_count"] == 1
    assert row["negative_count"] == 1
    assert row["positive_ratio"] == 0.5


def test_normalize_steamspy_snapshots_extracts_context_metadata():
    games = [
        GameConfig("Dota 2", 570, "MOBA", "control", "special_case", "mvp", True)
    ]

    metadata = normalize_steamspy_snapshots(FIXTURE_ROOT / "raw", games)

    row = metadata.iloc[0].to_dict()
    assert row["game"] == "Dota 2"
    assert row["owners"] == "100,000,000 .. 200,000,000"
    assert row["positive_reviews"] == 100
    assert row["negative_reviews"] == 20
