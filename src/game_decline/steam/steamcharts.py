from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup

from game_decline.raw_store import write_text_snapshot
from game_decline.steam.http import HttpClient


STEAMCHARTS_APP_URL = "https://steamcharts.com/app/{app_id}"


@dataclass(frozen=True)
class SteamChartsMonthlyRow:
    app_id: int
    month: str
    avg_players: float | None
    gain: float | None
    percent_gain: float | None
    peak_players: int | None


def parse_number(value: str) -> float | None:
    cleaned = value.strip().replace(",", "").replace("+", "")
    if not cleaned or cleaned == "-":
        return None
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    parsed = parse_number(value)
    if parsed is None:
        return None
    return int(round(parsed))


def parse_monthly_table(app_id: int, html: str) -> list[SteamChartsMonthlyRow]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="common-table")
    if table is None:
        raise ValueError(f"Could not find SteamCharts history table for app_id={app_id}")

    rows: list[SteamChartsMonthlyRow] = []
    for table_row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in table_row.find_all("td")]
        if len(cells) < 5:
            continue
        rows.append(
            SteamChartsMonthlyRow(
                app_id=app_id,
                month=cells[0],
                avg_players=parse_number(cells[1]),
                gain=parse_number(cells[2]),
                percent_gain=parse_number(cells[3]),
                peak_players=parse_int(cells[4]),
            )
        )
    if not rows:
        raise ValueError(f"SteamCharts table had no monthly rows for app_id={app_id}")
    return rows


def rows_to_csv(rows: Iterable[SteamChartsMonthlyRow]) -> str:
    header = "app_id,month,avg_players,gain,percent_gain,peak_players"
    lines = [header]
    for row in rows:
        values = asdict(row)
        lines.append(",".join(_csv_value(values[key]) for key in header.split(",")))
    return "\n".join(lines) + "\n"


def _csv_value(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    if any(char in text for char in [",", '"', "\n"]):
        return '"' + text.replace('"', '""') + '"'
    return text


def fetch_steamcharts_html(app_id: int, client: HttpClient | None = None) -> str:
    http = client or HttpClient()
    return http.get_text(STEAMCHARTS_APP_URL.format(app_id=app_id))


def fetch_and_store_steamcharts(
    app_id: int,
    raw_root: Path,
    client: HttpClient | None = None,
) -> tuple[Path, Path, int]:
    html = fetch_steamcharts_html(app_id, client)
    rows = parse_monthly_table(app_id, html)
    html_path = write_text_snapshot(raw_root, "steamcharts", app_id, "html", html)
    csv_path = write_text_snapshot(raw_root, "steamcharts", app_id, "csv", rows_to_csv(rows))
    return html_path, csv_path, len(rows)
