from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def write_text_snapshot(
    raw_root: Path,
    source: str,
    app_id: int,
    suffix: str,
    text: str,
    timestamp: str | None = None,
) -> Path:
    stamp = timestamp or utc_timestamp()
    target_dir = raw_root / source
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{app_id}_{stamp}.{suffix}"
    path.write_text(text, encoding="utf-8")
    return path


def write_json_snapshot(
    raw_root: Path,
    source: str,
    app_id: int,
    payload: dict[str, Any],
    timestamp: str | None = None,
) -> Path:
    stamp = timestamp or utc_timestamp()
    target_dir = raw_root / source
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{app_id}_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
