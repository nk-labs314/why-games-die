# Steam Game Decline Analysis

Can public Steam-facing signals help explain or anticipate major player-count decline events in multiplayer games?

This project analyzes Steam multiplayer games through player-count decline events, review sentiment, update timelines, and external events. The MVP proves the full workflow on three games before expanding to the full candidate list.

## Guardrails

- The project can claim that signals coincide with or precede decline events.
- The project cannot claim that one factor caused a decline without stronger causal evidence.
- Every decline event can be classified as `unknown` when the evidence is weak.
- Steam-only data is a project constraint, not a complete picture of every game.

## MVP Scope

MVP games:

- New World
- Z1 Battle Royale / H1Z1
- Dota 2

Expansion candidates:

- PUBG: BATTLEGROUNDS
- Apex Legends
- Team Fortress 2
- Realm of the Mad God Exalt
- Battlefield 2042
- STAR WARS Battlefront II
- ARK: Survival Evolved

## Workflow

1. Audit data availability.
2. Ingest raw player-count, Steam review, Steam announcement, and manual event data.
3. Normalize source data into daily metrics.
4. Detect decline events with a fixed rule.
5. Compare review, update, and external-event signals around each decline.
6. Generate per-game timelines and cross-game comparison charts.
7. Produce a bounded Markdown/HTML report.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pytest
```

Run the pipeline:

```powershell
python scripts/check_data_availability.py
python scripts/fetch_raw_data.py --reviews --announcements
python scripts/build_processed_data.py
python scripts/run_analysis.py
python scripts/validate_outputs.py
python scripts/build_report.py
```

Player-count history should be added manually under `data/raw/player_counts/` as CSV files when using SteamDB or SteamCharts exports. The normalizer accepts common date/count column names and preserves the source filename.

Current MVP source strategy:

- SteamCharts monthly average and peak concurrent-player tables are the player-count backbone.
- SteamSpy provides owner ranges, review totals, tags, and metadata context.
- Steam announcements and manual events are treated as contextual signals, not causal proof.
- Kaggle/Mendeley datasets can be added under `data/raw/third_party_datasets/` as expansion sources.

## Main Outputs

- `data/processed/game_summary.csv`
- `data/processed/game_daily_metrics.csv`
- `data/processed/monthly_features.csv`
- `data/processed/decline_events.csv`
- `data/processed/decline_summary.csv`
- `data/processed/event_windows.csv`
- `reports/figures/`
- `reports/steam_decline_analysis.md`
- `reports/steam_decline_analysis.html`

## Notebooks

The notebooks mirror the CLI pipeline:

- `notebooks/00_data_availability.ipynb`
- `notebooks/01_player_decline_detection.ipynb`
- `notebooks/02_review_sentiment_overlay.ipynb`
- `notebooks/03_event_annotation_analysis.ipynb`
- `notebooks/04_cross_game_comparison.ipynb`
