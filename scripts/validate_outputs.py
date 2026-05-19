from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.config import PROJECT_ROOT
from game_decline.validation import validate_processed_tables


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() and path.stat().st_size > 1 else pd.DataFrame()


def main() -> int:
    processed_root = PROJECT_ROOT / "data" / "processed"
    errors = validate_processed_tables(
        read_csv_or_empty(processed_root / "game_daily_metrics.csv"),
        read_csv_or_empty(processed_root / "decline_events.csv"),
        read_csv_or_empty(processed_root / "event_windows.csv"),
    )
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("[OK] processed outputs passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
