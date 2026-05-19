from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.config import PROJECT_ROOT, filter_games, load_games
from game_decline.steam.announcements import fetch_and_store_announcements
from game_decline.steam.reviews import fetch_and_store_reviews
from game_decline.steam.steamcharts import fetch_and_store_steamcharts
from game_decline.steam.steamspy import fetch_and_store_appdetails


@dataclass(frozen=True)
class FetchResult:
    game: str
    app_id: int
    source: str
    ok: bool
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch raw Steam-facing source data.")
    parser.add_argument(
        "--scope",
        default="mvp",
        choices=["mvp", "expansion", "all"],
        help="Which games from config/games.yaml to fetch.",
    )
    parser.add_argument(
        "--app-id",
        type=int,
        action="append",
        default=[],
        help="Fetch specific Steam app id. Can be passed multiple times.",
    )
    parser.add_argument(
        "--steamcharts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Fetch SteamCharts monthly player tables.",
    )
    parser.add_argument(
        "--steamspy",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Fetch SteamSpy app metadata.",
    )
    parser.add_argument(
        "--reviews",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Fetch recent Steam Store review snapshots.",
    )
    parser.add_argument(
        "--announcements",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Fetch public Steam news/announcement snapshots.",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Directory where untouched source snapshots are written.",
    )
    return parser.parse_args()


def selected_games(args: argparse.Namespace):
    games = load_games()
    scope = None if args.scope == "all" else args.scope
    app_ids = set(args.app_id) if args.app_id else None
    return filter_games(games, inclusion_status=scope, app_ids=app_ids)


def fetch_game_sources(
    game,
    raw_root: Path,
    use_steamcharts: bool,
    use_steamspy: bool,
    use_reviews: bool,
    use_announcements: bool,
) -> list[FetchResult]:
    results: list[FetchResult] = []

    if use_steamcharts:
        try:
            html_path, csv_path, row_count = fetch_and_store_steamcharts(game.app_id, raw_root)
            results.append(
                FetchResult(
                    game.game,
                    game.app_id,
                    "steamcharts",
                    True,
                    f"{row_count} monthly rows -> {html_path.name}, {csv_path.name}",
                )
            )
        except Exception as exc:
            results.append(FetchResult(game.game, game.app_id, "steamcharts", False, str(exc)))

    if use_steamspy:
        try:
            json_path = fetch_and_store_appdetails(game.app_id, raw_root)
            results.append(
                FetchResult(
                    game.game,
                    game.app_id,
                    "steamspy",
                    True,
                    json_path.name,
                )
            )
        except Exception as exc:
            results.append(FetchResult(game.game, game.app_id, "steamspy", False, str(exc)))

    if use_reviews:
        try:
            json_path = fetch_and_store_reviews(game.app_id, raw_root)
            results.append(FetchResult(game.game, game.app_id, "reviews", True, json_path.name))
        except Exception as exc:
            results.append(FetchResult(game.game, game.app_id, "reviews", False, str(exc)))

    if use_announcements:
        try:
            json_path = fetch_and_store_announcements(game.app_id, raw_root)
            results.append(FetchResult(game.game, game.app_id, "announcements", True, json_path.name))
        except Exception as exc:
            results.append(FetchResult(game.game, game.app_id, "announcements", False, str(exc)))

    return results


def main() -> int:
    args = parse_args()
    games = selected_games(args)
    if not games:
        print("No games matched the requested filters.")
        return 2

    all_results: list[FetchResult] = []
    for game in games:
        all_results.extend(
            fetch_game_sources(
                game,
                args.raw_root,
                args.steamcharts,
                args.steamspy,
                args.reviews,
                args.announcements,
            )
        )

    for result in all_results:
        status = "OK" if result.ok else "FAIL"
        print(f"[{status}] {result.game} ({result.app_id}) {result.source}: {result.message}")

    return 0 if all(result.ok for result in all_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
