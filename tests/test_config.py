from pathlib import Path

from game_decline.config import filter_games, load_games


def test_load_games_reads_project_config():
    games = load_games(Path("config/games.yaml"))

    assert len(games) >= 3
    assert {game.game for game in filter_games(games, inclusion_status="mvp")} == {
        "New World",
        "Z1 Battle Royale",
        "Dota 2",
    }
