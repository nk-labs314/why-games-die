from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def build_comparison_figures(decline_summary: pd.DataFrame, figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    if decline_summary.empty:
        return []
    paths: list[Path] = []
    frame = decline_summary.sort_values("decline_event_count", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(frame["game"], frame["decline_event_count"], color="#4472c4")
    ax.set_title("Detected Major Monthly Decline Events By Game")
    ax.set_xlabel("Decline event count")
    ax.set_ylabel("Game")
    ax.grid(True, axis="x", alpha=0.25)
    path = figures_dir / "decline_event_count_by_game.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)

    fig, ax = plt.subplots(figsize=(10, 5))
    sorted_frame = decline_summary.sort_values("largest_decline_percent", ascending=True)
    ax.barh(sorted_frame["game"], sorted_frame["largest_decline_percent"], color="#c44e52")
    ax.set_title("Largest Month-Over-Month Average CCU Drop")
    ax.set_xlabel("Largest decline percent")
    ax.set_ylabel("Game")
    ax.grid(True, axis="x", alpha=0.25)
    path = figures_dir / "largest_decline_percent_by_game.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    paths.append(path)
    return paths
