from __future__ import annotations

import html
from pathlib import Path

import pandas as pd


def build_markdown_report(
    metrics: pd.DataFrame,
    decline_events: pd.DataFrame,
    event_windows: pd.DataFrame,
    game_summary: pd.DataFrame,
    figure_paths: list[Path],
    decline_summary: pd.DataFrame | None = None,
) -> str:
    decline_summary = decline_summary if decline_summary is not None else pd.DataFrame()
    lines = [
        "# Steam Game Decline Analysis",
        "",
        "## Project Question",
        "",
        "Can public Steam-facing signals help explain or anticipate major player-count decline events in multiplayer games?",
        "",
        "## Dataset And Exclusions",
        "",
        _summary_table(game_summary),
        "",
        "Player-count data currently comes from SteamCharts monthly average and peak concurrent-player tables. SteamSpy is treated as metadata/context, not proof of historical player-count changes.",
        "",
        "## Methodology",
        "",
        "The MVP detects major monthly decline events using a fixed percentage drop in average concurrent players. Review and event signals are summarized around detected windows when those raw sources are available.",
        "",
        "## Decline-Event Definition",
        "",
        "A major decline is currently defined as a month-over-month average-player drop at or above the configured threshold. The default threshold is 30%.",
        "",
        "## Detected Declines",
        "",
    ]

    if not decline_summary.empty:
        lines.extend(["## Cross-Game Summary", "", _dataframe_table(decline_summary), ""])

    if decline_events.empty:
        lines.extend(
            [
                "No major decline events were detected in the currently processed dataset.",
                "",
            ]
        )
    else:
        lines.extend([_dataframe_table(decline_events), ""])

    lines.extend(
        [
            "## Event Windows",
            "",
            _dataframe_table(event_windows) if not event_windows.empty else "No event-window rows are available yet.",
            "",
            "## Figures",
            "",
        ]
    )
    if figure_paths:
        for path in figure_paths:
            lines.append(f"![{path.stem}](figures/{path.name})")
            lines.append("")
    else:
        lines.append("No figures were generated because no player-count metrics were available.")
        lines.append("")

    lines.extend(
        [
            "## What The Data Supports",
            "",
            "- The pipeline can show player-count trend changes and whether public signals appear near those changes.",
            "- It can compare games using the same decline rule once enough source data is collected.",
            "",
            "## What The Data Does Not Prove",
            "",
            "- This analysis does not prove causation.",
            "- Steam-only data can miss non-Steam populations, console audiences, and off-platform context.",
            "- Monthly SteamCharts data cannot support precise daily event timing.",
            "",
            "## Next Improvements",
            "",
            "- Collect all MVP SteamCharts histories, not just one app.",
            "- Add Steam review snapshots for the decline windows.",
            "- Fill manual event annotations for major updates, controversies, and competitor releases.",
            "- Treat low-player-count late-life games carefully; percentage drops can look dramatic even when absolute movement is small.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(markdown: str, markdown_path: Path, html_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")
    body = html.escape(markdown)
    html_path.write_text(
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>Steam Game Decline Analysis</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:980px;margin:40px auto;line-height:1.5}"
        "pre{white-space:pre-wrap}</style></head><body><pre>"
        + body
        + "</pre></body></html>",
        encoding="utf-8",
    )


def _summary_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No game summary is available yet."
    columns = [
        column
        for column in ["game", "app_id", "player_data_available", "review_data_available", "recommended_action"]
        if column in frame.columns
    ]
    return _dataframe_table(frame[columns])


def _dataframe_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return ""
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        values = [str(row[column]) if pd.notna(row[column]) else "" for column in frame.columns]
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines)
