from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.config import PROJECT_ROOT, load_games


def has_snapshot(raw_root: Path, source: str, app_id: int, suffixes: tuple[str, ...]) -> bool:
    source_dir = raw_root / source
    if not source_dir.exists():
        return False
    return any(path.name.startswith(f"{app_id}_") and path.suffix in suffixes for path in source_dir.iterdir())


def main() -> int:
    raw_root = PROJECT_ROOT / "data" / "raw"
    rows: list[dict[str, object]] = []
    for game in load_games():
        player_available = has_snapshot(raw_root, "steamcharts", game.app_id, (".csv",))
        review_available = has_snapshot(raw_root, "steam_reviews", game.app_id, (".json",))
        announcement_available = has_snapshot(raw_root, "steam_announcements", game.app_id, (".json",))
        rows.append(
            {
                "game": game.game,
                "app_id": game.app_id,
                "player_data_available": player_available,
                "review_data_available": review_available,
                "announcement_data_available": announcement_available,
                "steam_represents_lifecycle": game.steam_represents_lifecycle,
                "recommended_action": "include" if game.inclusion_status == "mvp" else game.inclusion_status,
            }
        )
    output_path = PROJECT_ROOT / "data" / "processed" / "game_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    print(f"[OK] game_summary: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
