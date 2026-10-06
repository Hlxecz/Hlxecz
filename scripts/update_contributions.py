"""Refresh the profile heatmap from GitHub's public contribution calendar."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USER = "Hlxecz"
ROOT = Path(__file__).resolve().parents[1]
COLORS = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")


def fetch_days() -> list[dict[str, int | str]]:
    url = f"https://github.com/users/{USER}/contributions"
    response = requests.get(url, headers={"User-Agent": "Hlxecz-profile-readme"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    tooltips = {tip.get("for"): tip.get_text(" ", strip=True) for tip in soup.select("tool-tip[for]")}
    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        day = cell["data-date"]
        tooltip = tooltips.get(cell.get("id"), "")
        if tooltip.lower().startswith("no contributions"):
            count = 0
        else:
            match = re.match(r"([\d,]+) contributions?", tooltip, re.I)
            if not match:
                raise ValueError(f"Cannot read contribution count for {day}: {tooltip!r}")
            count = int(match.group(1).replace(",", ""))
        days.append({"date": day, "count": count, "level": min(int(cell.get("data-level", 0)), 4)})
    days.sort(key=lambda item: item["date"])
    if len(days) < 350 or len({item["date"] for item in days}) != len(days):
        raise ValueError(f"Unexpected contribution calendar: {len(days)} days")
    return days


def streaks(days: list[dict[str, int | str]]) -> tuple[int, int]:
    run = longest = 0
    for item in days:
        run = run + 1 if item["count"] else 0
        longest = max(longest, run)
    current = run
    if not current and days[-1]["date"] == date.today().isoformat():
        for item in reversed(days[:-1]):
            if not item["count"]:
                break
            current += 1
    return current, longest


def render(days: list[dict[str, int | str]]) -> str:
    first = date.fromisoformat(days[0]["date"])
    sunday_offset = (first.weekday() + 1) % 7
    columns = (sunday_offset + len(days) + 6) // 7
    width = 78 + columns * 15 + 18
    height = 218
    total = sum(int(item["count"]) for item in days)
    current, longest = streaks(days)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} GitHub contributions in the last year">',
        '<style>@keyframes reveal{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}.day{animation:reveal .38s ease-out both}@media (prefers-reduced-motion: reduce){.day{animation:none;opacity:1}}</style>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117"/>',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="#30363d"/>',
        f'<path d="M0 30H{width}" stroke="#30363d"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        svg.append(f'<circle cx="{22 + 16 * i}" cy="15" r="5" fill="{color}"/>')
    svg.append(f'<text x="{width / 2}" y="19" text-anchor="middle" fill="#8b949e" font-family="monospace" font-size="12">hlxecz@github: ~/contributions</text>')

    seen_months = set()
    for item in days:
        day = date.fromisoformat(item["date"])
        column = (sunday_offset + (day - first).days) // 7
        row = (day.weekday() + 1) % 7
        x, y = 56 + 15 * column, 54 + 15 * row
        if day.day <= 7 and (day.year, day.month) not in seen_months:
            seen_months.add((day.year, day.month))
            svg.append(f'<text x="{x}" y="45" fill="#8b949e" font-family="monospace" font-size="10">{day.strftime("%b")}</text>')
        color = COLORS[int(item["level"])]
        delay = column * .017 + row * .035
        label = escape(f'{day.isoformat()}: {item["count"]} contributions')
        svg.append(f'<rect class="day" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{color}" style="animation-delay:{delay:.3f}s"><title>{label}</title></rect>')

    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        svg.append(f'<text x="20" y="{63 + 15 * row}" fill="#8b949e" font-family="monospace" font-size="10">{label}</text>')
    svg.extend([
        f'<path d="M18 169H{width - 18}" stroke="#30363d"/>',
        f'<text x="20" y="190" fill="#39d353" font-family="monospace" font-size="13" font-weight="bold">{total:,} contributions</text>',
        f'<text x="{width - 20}" y="190" text-anchor="end" fill="#8b949e" font-family="monospace" font-size="11">{days[0]["date"]} to {days[-1]["date"]}</text>',
        f'<text x="20" y="207" fill="#8b949e" font-family="monospace" font-size="11">current streak <tspan fill="#58a6ff">{current} days</tspan>  ·  longest <tspan fill="#58a6ff">{longest} days</tspan></text>',
        '</svg>',
    ])
    return "\n".join(svg) + "\n"


def main() -> None:
    days = fetch_days()
    data = {"username": USER, "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "days": days}
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "contributions.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "contrib-heatmap.svg").write_text(render(days), encoding="utf-8")
    print(f"Updated {len(days)} days, {sum(int(day['count']) for day in days)} contributions")


if __name__ == "__main__":
    main()
