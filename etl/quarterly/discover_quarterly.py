"""Read-only discovery of BA quarterly Germany Employed Excel files.

Usage (from repository root):
    python etl/quarterly/discover_quarterly.py
    python etl/quarterly/discover_quarterly.py --pages 6

This script does not download Excel files or write to the project.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[2]
PARQUET = REPO / "data" / "employed_people_full_kldb.parquet"
START_URL = (
    "https://statistik.arbeitsagentur.de/"
    "SiteGlobals/Forms/Suche/Einzelheftsuche_Formular.html"
    "?topic_f=beschaeftigung-sozbe-bo-heft"
)
FILE_PATTERN = re.compile(r"bo-heft-d-0-(\d{6})-xlsx\.xlsx", re.IGNORECASE)


def parse_page(html: str, response_url: str) -> tuple[dict[str, str], dict[int, str]]:
    """Extract Germany Excel URLs and actual pagination links from BA HTML."""
    soup = BeautifulSoup(html, "html.parser")
    excel_urls: dict[str, str] = {}
    page_urls: dict[int, str] = {}

    for link in soup.select("a[href]"):
        href = link["href"].strip()
        full_url = urljoin(response_url, href)
        filename = urlparse(full_url).path.rsplit("/", 1)[-1]
        match = FILE_PATTERN.fullmatch(filename)
        if match:
            excel_urls[match.group(1)] = full_url

        # BA changes its internal list identifier; follow its own links.
        label = link.get_text(" ", strip=True)
        if label.isdecimal() and "gtp=" in href:
            page_urls[int(label)] = full_url

    return excel_urls, page_urls


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only BA quarterly discovery")
    parser.add_argument("--pages", type=int, default=3, help="Max catalogue pages (default: 3)")
    args = parser.parse_args()
    if not 1 <= args.pages <= 100:
        parser.error("--pages must be between 1 and 100")

    if not PARQUET.is_file():
        raise FileNotFoundError(f"Existing Parquet not found: {PARQUET}")
    dates = pd.to_datetime(pd.read_parquet(PARQUET, columns=["report_date"])["report_date"])
    if dates.empty or dates.isna().any():
        raise ValueError("Existing Parquet has empty or missing report dates")
    latest_existing = dates.max().strftime("%Y%m")
    existing_periods = set(dates.dt.strftime("%Y%m"))
    print(f"Existing Parquet: {PARQUET.name}")
    print(f"Existing quarters: {len(existing_periods)}, latest: {latest_existing}")

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CareerCompass-ETL/1.0)"})
    pending: dict[int, str] = {1: START_URL}
    visited: set[int] = set()
    found: dict[str, str] = {}

    while pending and len(visited) < args.pages:
        number = min(pending)
        url = pending.pop(number)
        if number in visited:
            continue
        response = session.get(url, timeout=30)
        response.raise_for_status()
        on_page, pagination = parse_page(response.text, response.url)
        print(f"Page {number}: HTTP {response.status_code}, Germany Excel: {', '.join(sorted(on_page, reverse=True)) or '(none)'}")
        found.update(on_page)
        visited.add(number)
        for next_num, next_url in pagination.items():
            if next_num not in visited and next_num not in pending:
                pending[next_num] = next_url
        if number == 1 and not on_page:
            raise RuntimeError("No Germany Excel files found on the first page; check BA markup")

    new_periods = sorted(set(found) - existing_periods)
    print(f"\nPages checked: {', '.join(map(str, sorted(visited)))}")
    print(f"Germany quarterly files discovered: {len(found)}")
    if new_periods:
        print("Missing from existing Parquet:")
        for period in new_periods:
            print(f"  {period}: {urlparse(found[period]).path.rsplit('/', 1)[-1]}")
    else:
        print("No missing quarters found on the checked pages.")
    if pending:
        print(f"Note: additional catalogue pages were not checked (limit --pages {args.pages}).")
    print("READ-ONLY: no files downloaded or modified.")


if __name__ == "__main__":
    main()
