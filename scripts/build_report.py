from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT_FOR_IMPORTS / "src"))

from game_decline.config import PROJECT_ROOT
from game_decline.report.build_report import build_markdown_report, write_report
from game_decline.visualization.timelines import build_player_timeline_figures


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() and path.stat().st_size > 1 else pd.DataFrame()


def main() -> int:
    processed_root = PROJECT_ROOT / "data" / "processed"
    reports_root = PROJECT_ROOT / "reports"
    figures_dir = reports_root / "figures"

    metrics = read_csv_or_empty(processed_root / "game_daily_metrics.csv")
    decline_events = read_csv_or_empty(processed_root / "decline_events.csv")
    event_windows = read_csv_or_empty(processed_root / "event_windows.csv")
    game_summary = read_csv_or_empty(processed_root / "game_summary.csv")

    figure_paths = build_player_timeline_figures(metrics, figures_dir)
    markdown = build_markdown_report(metrics, decline_events, event_windows, game_summary, figure_paths)
    write_report(
        markdown,
        reports_root / "steam_decline_analysis.md",
        reports_root / "steam_decline_analysis.html",
    )
    print(f"[OK] figures: {len(figure_paths)}")
    print(f"[OK] report: {reports_root / 'steam_decline_analysis.md'}")
    print(f"[OK] html: {reports_root / 'steam_decline_analysis.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
