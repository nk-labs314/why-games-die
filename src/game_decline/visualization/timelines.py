from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def build_player_timeline_figures(metrics: pd.DataFrame, figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    if metrics.empty:
        return []

    paths: list[Path] = []
    metrics = metrics.copy()
    metrics["date"] = pd.to_datetime(metrics["date"], errors="coerce")
    metrics = metrics.dropna(subset=["date", "avg_ccu"])
    for game, frame in metrics.groupby("game"):
        frame = frame.sort_values("date")
        if frame.empty:
            continue
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(frame["date"], frame["avg_ccu"], marker="o", linewidth=2, label="Avg CCU")
        if "peak_ccu" in frame.columns and frame["peak_ccu"].notna().any():
            ax.plot(frame["date"], frame["peak_ccu"], marker="o", linewidth=1.5, label="Peak CCU")
        ax.set_title(f"{game} SteamCharts Monthly Player Counts")
        ax.set_xlabel("Month")
        ax.set_ylabel("Players")
        ax.legend()
        ax.grid(True, alpha=0.25)
        fig.autofmt_xdate()
        safe_name = "".join(char.lower() if char.isalnum() else "_" for char in game).strip("_")
        path = figures_dir / f"{safe_name}_player_timeline.png"
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)
    return paths

