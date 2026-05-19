from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.config import PROJECT_ROOT, load_games
from game_decline.processing.pipeline import write_processed_tables


def main() -> int:
    paths = write_processed_tables(
        raw_root=PROJECT_ROOT / "data" / "raw",
        processed_root=PROJECT_ROOT / "data" / "processed",
        interim_root=PROJECT_ROOT / "data" / "interim",
        games=load_games(),
    )
    for name, path in paths.items():
        print(f"[OK] {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
