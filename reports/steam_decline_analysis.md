# Steam Game Decline Analysis

## Project Question

Can public Steam-facing signals help explain or anticipate major player-count decline events in multiplayer games?

## Dataset And Exclusions

| game | app_id | player_data_available | review_data_available | recommended_action |
| --- | --- | --- | --- | --- |
| New World | 1063730 | False | False | include |
| Z1 Battle Royale | 433850 | False | False | include |
| Dota 2 | 570 | True | False | include |
| PUBG: BATTLEGROUNDS | 578080 | False | False | expansion |
| Apex Legends | 1172470 | False | False | expansion |
| Team Fortress 2 | 440 | False | False | expansion |
| Realm of the Mad God Exalt | 200210 | False | False | expansion |
| Battlefield 2042 | 1517290 | False | False | expansion |
| STAR WARS Battlefront II | 1237950 | False | False | expansion |
| ARK: Survival Evolved | 346110 | False | False | expansion |

Player-count data currently comes from SteamCharts monthly average and peak concurrent-player tables. SteamSpy is treated as metadata/context, not proof of historical player-count changes.

## Methodology

The MVP detects major monthly decline events using a fixed percentage drop in average concurrent players. Review and event signals are summarized around detected windows when those raw sources are available.

## Decline-Event Definition

A major decline is currently defined as a month-over-month average-player drop at or above the configured threshold. The default threshold is 30%.

## Detected Declines

No major decline events were detected in the currently processed dataset.

## Event Windows

No event-window rows are available yet.

## Figures

![dota_2_player_timeline](figures/dota_2_player_timeline.png)

## What The Data Supports

- The pipeline can show player-count trend changes and whether public signals appear near those changes.
- It can compare games using the same decline rule once enough source data is collected.

## What The Data Does Not Prove

- This analysis does not prove causation.
- Steam-only data can miss non-Steam populations, console audiences, and off-platform context.
- Monthly SteamCharts data cannot support precise daily event timing.

## Next Improvements

- Collect all MVP SteamCharts histories, not just one app.
- Add Steam review snapshots for the decline windows.
- Fill manual event annotations for major updates, controversies, and competitor releases.
