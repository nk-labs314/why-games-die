# Steam Game Decline Analysis Project Plan

## Summary

Build a reproducible data science project that analyzes Steam multiplayer games through player-count decline events, review sentiment, update timelines, and external events. The MVP should prove the full pipeline on 3 games before expanding to the full 10-game list.

Current repo state: `C:\Users\2faze\OneDrive\Documents\NANDAN\projects\game analysis` is empty except `.git`, so this plan assumes a fresh Python project scaffold.

Final outcome: a Jupyter-driven analysis repo that produces cleaned datasets, annotated decline-event tables, per-game charts, and a final Markdown/HTML report explaining what public Steam-facing signals appear near major player-count drops.

## Repo Structure

```text
game analysis/
  README.md
  pyproject.toml
  requirements.txt
  .gitignore
  .env.example

  config/
    games.yaml
    analysis.yaml
    event_taxonomy.yaml

  data/
    raw/
      player_counts/
      steamcharts/
      steamspy/
      third_party_datasets/
      steam_reviews/
      steam_announcements/
      external_events/
    interim/
      normalized_player_counts/
      normalized_reviews/
      normalized_events/
    processed/
      game_daily_metrics.csv
      decline_events.csv
      event_windows.csv
      game_summary.csv

  notebooks/
    00_data_availability.ipynb
    01_player_decline_detection.ipynb
    02_review_sentiment_overlay.ipynb
    03_event_annotation_analysis.ipynb
    04_cross_game_comparison.ipynb

  src/
    game_decline/
      __init__.py
      config.py
      schemas.py
      steam/
        __init__.py
        app_lookup.py
        player_counts.py
        reviews.py
        announcements.py
      processing/
        __init__.py
        normalize_players.py
        normalize_reviews.py
        normalize_events.py
        sentiment.py
      analysis/
        __init__.py
        decline_detection.py
        event_windows.py
        correlations.py
        classifications.py
      visualization/
        __init__.py
        timelines.py
        overlays.py
        comparison.py
      report/
        __init__.py
        build_report.py

  reports/
    figures/
    steam_decline_analysis.md
    steam_decline_analysis.html

  tests/
    test_decline_detection.py
    test_event_windows.py
    test_sentiment_aggregation.py
    fixtures/
      sample_player_counts.csv
      sample_reviews.csv
      sample_events.csv

  scripts/
    check_data_availability.py
    fetch_raw_data.py
    build_processed_data.py
    run_analysis.py
    build_report.py
```

## Phases And Steps

### Phase 1: Project Definition And Guardrails

1. Create `README.md` with the project question:
   `Can public Steam-facing signals help explain or anticipate major player-count decline events in multiplayer games?`

2. Define MVP scope:
   - MVP games: `New World`, `H1Z1/Z1 Battle Royale`, `Dota 2`.
   - Expansion games: `PUBG`, `Apex Legends`, `Team Fortress 2`, `Realm of the Mad God`, `Battlefield 2042`, `Star Wars Battlefront II`, `ARK: Survival Evolved`.

3. Define what the project will and will not claim:
   - Allowed claim: signals coincide with or precede decline events.
   - Not allowed claim: proof that one factor caused a decline.
   - Every explanation must allow `unknown / insufficient evidence`.

4. Create `config/analysis.yaml`:
   - player smoothing window: `7 days`
   - major drop threshold: `30%`
   - max drop window: `30 days`
   - launch-decay exclusion window: `14 days after Steam launch`
   - sentiment windows: `30 days before`, `during`, `30 days after`
   - minimum review count per window: `20`

### Phase 2: Data Availability Audit

1. Create `config/games.yaml` with game metadata:
   - game name
   - Steam App ID
   - genre
   - expected decline profile
   - Steam lifecycle quality: `clean`, `partial`, or `distorted`
   - inclusion status: `mvp`, `expansion`, `excluded`, or `needs_review`

2. Implement `scripts/check_data_availability.py`.
   It should output `data/processed/game_summary.csv` with:
   - `game`
   - `app_id`
   - `player_data_available`
   - `review_data_available`
   - `announcement_data_available`
   - `steam_represents_lifecycle`
   - `recommended_action`

3. Exclude or demote games where Steam data does not represent the lifecycle well.
   Examples:
   - Apex Legends: Steam data starts late, so mark as `partial`.
   - Battlefront II: controversy history may predate Steam data, so mark as `distorted`.
   - Dota 2: valid control but Valve-owned, so mark as `special_case`.

4. Stop condition:
   MVP proceeds only when at least 3 games have usable player count data and review data.

### Phase 3: Raw Data Collection

1. Implement Steam player-count ingestion in `src/game_decline/steam/player_counts.py`.
   Preferred source order:
   - SteamCharts monthly tables scraped or manually exported from `steamcharts.com`.
     Use monthly average players and monthly peak concurrent players as the MVP backbone.
   - Kaggle `Steam Player Data` dataset by `jackogozaly`, when it covers the target game and has usable provenance.
   - Mendeley Steam games dataset with player-count history for 2000 top Steam games, when the target game and date window are covered.
   - SteamSpy only for owner estimates, review counts, tags, and metadata; do not use it as the sole source for historical player-count curves.

   Store source-specific raw files under:
   - `data/raw/steamcharts/`
   - `data/raw/third_party_datasets/kaggle/`
   - `data/raw/third_party_datasets/mendeley/`
   - `data/raw/player_counts/` for any already-normalized manual CSV imports.

   The MVP should not require a Steam Web API key for player-count collection.

2. Implement Steam review ingestion in `src/game_decline/steam/reviews.py`.
   Preferred source order:
   - Steam Store review endpoint for review text and timestamps when text sentiment or event-window review changes are needed.
   - SteamSpy review counts when only aggregate context is needed.

   Store raw reviews with:
   - `app_id`
   - `review_id`
   - `created_at`
   - `voted_up`
   - `language`
   - `playtime_at_review`
   - `review_text`

3. Implement SteamSpy metadata ingestion in `src/game_decline/steam/app_lookup.py`.
   Store raw SteamSpy responses with:
   - `app_id`
   - `owners`
   - `positive`
   - `negative`
   - `average_forever`
   - `median_forever`
   - `tags`
   - `genre`
   - `developer`
   - `publisher`

4. Implement Steam announcement ingestion in `src/game_decline/steam/announcements.py`.
   Preferred source order:
   - Public Steam news/community announcement endpoints where available without a project Steam API key.
   - Manual event annotation when announcements are incomplete or unavailable.

   Store raw announcements with:
   - `app_id`
   - `announcement_id`
   - `published_at`
   - `title`
   - `body`
   - `url`

5. Store all untouched source data under `data/raw/`.
   Never overwrite raw files without changing the filename or adding a fetch timestamp.

### Phase 4: Normalization And Daily Metrics

1. Normalize player counts into daily rows:
   - `game`
   - `app_id`
   - `date`
   - `avg_ccu`
   - `peak_ccu`
   - `source`

2. Normalize reviews into daily aggregates:
   - `game`
   - `app_id`
   - `date`
   - `review_count`
   - `positive_count`
   - `negative_count`
   - `positive_ratio`
   - `avg_sentiment_score`

3. Use simple sentiment first:
   - Use Steam `voted_up` as the primary sentiment label.
   - Use VADER only as secondary text sentiment.
   - Do not use transformers in MVP unless VADER clearly fails.

4. Normalize announcements and manual events into one event table:
   - `game`
   - `app_id`
   - `date`
   - `event_type`
   - `event_source`
   - `title`
   - `summary`
   - `url`
   - `confidence`

5. Build `data/processed/game_daily_metrics.csv` by joining player and review metrics by `game`, `app_id`, and `date`.

### Phase 5: Decline Event Detection

1. Implement rule-based decline detection in `src/game_decline/analysis/decline_detection.py`.

2. Use this MVP rule:
   - calculate 7-day rolling average of `avg_ccu`
   - find periods where rolling average drops at least `30%`
   - drop must occur within `30 days`
   - ignore first `14 days` after Steam launch unless labeling as `launch_decay`
   - merge overlapping decline events

3. Output `data/processed/decline_events.csv`:
   - `event_id`
   - `game`
   - `app_id`
   - `decline_start`
   - `decline_end`
   - `start_ccu_rolling`
   - `end_ccu_rolling`
   - `drop_pct`
   - `duration_days`
   - `decline_type`

4. Decline type values:
   - `launch_decay`
   - `sharp_drop`
   - `gradual_decline`
   - `seasonal_cycle`
   - `recovery`
   - `stable_control`

5. Manually inspect each MVP game chart to confirm the detector is not producing nonsense.
   If the detector fails, adjust thresholds only in `config/analysis.yaml`, not inside notebook logic.

### Phase 6: Event Window Analysis

1. Implement `src/game_decline/analysis/event_windows.py`.

2. For every decline event, compute:
   - review metrics 30 days before
   - review metrics during decline
   - review metrics 30 days after
   - announcement count before/during/after
   - days since previous major update
   - nearby manual external events

3. Output `data/processed/event_windows.csv`:
   - `event_id`
   - `game`
   - `pre_positive_ratio`
   - `during_positive_ratio`
   - `post_positive_ratio`
   - `pre_review_count`
   - `during_review_count`
   - `post_review_count`
   - `review_shift`
   - `announcement_count_pre`
   - `announcement_count_during`
   - `days_since_last_update`
   - `nearby_event_types`

4. Classify each decline event with one primary explanation:
   - `launch_quality`
   - `content_drought`
   - `bad_update`
   - `monetization_backlash`
   - `competitor_displacement`
   - `technical_failure`
   - `platform_or_sequel_disruption`
   - `normal_decay`
   - `unknown`

### Phase 7: Visualization

1. Build per-game timeline charts:
   - player count rolling average
   - detected decline events shaded
   - review positivity overlay
   - major events as vertical markers

2. Build cross-game comparison charts:
   - drop percentage by game
   - decline duration by game
   - review sentiment shift around decline events
   - update gap versus decline severity
   - alive/control games versus dead/declined games

3. Save all figures to `reports/figures/`.

4. Every chart must have:
   - title
   - source note
   - date range
   - clear legend
   - no unexplained annotations

### Phase 8: Report And Final Analysis

1. Build `reports/steam_decline_analysis.md`.

2. Required report sections:
   - project question
   - dataset and exclusions
   - methodology
   - decline-event definition
   - per-game analysis
   - cross-game comparison
   - what the data supports
   - what the data does not prove
   - limitations
   - next improvements

3. The final conclusion must be specific and bounded.
   Example acceptable conclusion:
   `In the MVP sample, sharp drops were easier to associate with launch failures or discrete controversy events, while slow declines aligned more with content/update gaps. Review sentiment was more often concurrent with decline than clearly predictive.`

4. The final conclusion must not claim causal proof unless supported by stronger future methods.

## Testing And Validation

1. Unit tests:
   - decline detector finds known synthetic drops
   - decline detector ignores tiny fluctuations
   - event-window code calculates correct before/during/after windows
   - sentiment aggregation handles empty review days
   - event classification allows `unknown`

2. Data validation checks:
   - no duplicate `game + date` daily metric rows
   - no decline event has `decline_end` before `decline_start`
   - all event dates fall inside the game analysis date range
   - all processed tables have required columns
   - missing data is explicit, not silently filled

3. Notebook validation:
   - notebooks run top-to-bottom from a clean kernel
   - notebooks only read from `data/raw`, `data/interim`, or `data/processed`
   - notebooks do not contain hidden manual edits to processed outputs

4. Report validation:
   - every major claim points to a chart, table, or stated limitation
   - every game with distorted Steam data is clearly labeled
   - every causal-sounding sentence is softened unless proven

## Final Outcome

The project is successful when the repo can:

1. Audit candidate Steam games for usable data.
2. Fetch or ingest raw player, review, announcement, and manual event data.
3. Normalize everything into daily metrics.
4. Detect major decline events with a fixed rule.
5. Compare review, update, and external-event signals around each decline.
6. Generate per-game timelines and cross-game comparison charts.
7. Produce a final Markdown/HTML report with bounded, defensible conclusions.

## Assumptions And Defaults

- The MVP uses 3 games first: `New World`, `H1Z1/Z1 Battle Royale`, and `Dota 2`.
- The full candidate list remains available for expansion after the MVP works.
- This is a data science project, not an ML project; rule-based event detection is used for reproducibility.
- Steam `voted_up` is the primary review sentiment signal; text sentiment is secondary.
- Manual event annotation is acceptable for MVP because automated patch-note classification would be a separate project.
- Steam-only analysis is acceptable, but games with major non-Steam populations must be marked as partial or distorted.
- The repo starts from empty, so all files listed above need to be created during implementation.
