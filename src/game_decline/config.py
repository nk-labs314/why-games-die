from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class GameConfig:
    game: str
    app_id: int
    genre: str
    expected_decline_profile: str
    steam_lifecycle_quality: str
    inclusion_status: str
    steam_represents_lifecycle: bool
    notes: str = ""


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_games(config_path: Path | None = None) -> list[GameConfig]:
    path = config_path or PROJECT_ROOT / "config" / "games.yaml"
    data = load_yaml(path)
    games = data.get("games", [])
    if not isinstance(games, list):
        raise ValueError(f"`games` must be a list in {path}")
    return [GameConfig(**game) for game in games]


def filter_games(
    games: list[GameConfig],
    inclusion_status: str | None = None,
    app_ids: set[int] | None = None,
) -> list[GameConfig]:
    selected = games
    if inclusion_status:
        selected = [game for game in selected if game.inclusion_status == inclusion_status]
    if app_ids:
        selected = [game for game in selected if game.app_id in app_ids]
    return selected
