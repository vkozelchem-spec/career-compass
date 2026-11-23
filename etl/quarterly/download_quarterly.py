"""Download one missing BA Germany quarterly Excel to isolated test storage.

From repository root:
    python etl/quarterly/download_quarterly.py --period 202603

This script never writes to data/, app.py, or existing Parquet files.
It refuses to overwrite an existing raw Excel.
"""

from __future__ import annotations

import argparse
import os
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

from discover_quarterly import PARQUET, REPO, START_URL, parse_page

RAW = REPO / "ba_quarterly_test" / "raw"
MAX_BYTES = 100 * 1024 * 1024


def find_source(session: requests.Session, period: str, max_pages: int) -> tuple[str, list[int]]:
    pending: dict[int, str] = {1: START_URL}
    visited: set[int] = set()
    while pending and len(visited) < max_pages:
        number = min(pending)
        url = pending.pop(number)
        if number in visited:
            continue
        response = session.get(url, timeout=30)
        response.raise_for_status()
        files, pages = parse_page(response.text, response.url)
        print(f"Catalogue page {number}: HTTP {response.status_code}, {len(files)} Germany file(s)")
        visited.add(number)
        if period in files:
            return files[period], sorted(visited)
        for next_number, next_url in pages.items():
            if next_number not in visited and next_number not in pending:
                pending[next_number] = next_url
    raise RuntimeError(f"Quarter {period} not found within {max_pages} catalogue pages")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download one missing BA quarterly Excel to staging")
    parser.add_argument("--period", required=True, help="Quarter YYYYMM, e.g. 202603")
    parser.add_argument("--pages", type=int, default=3, help="Max catalogue pages to check")
    args = parser.parse_args()
    period = args.period
    if len(period) != 6 or not period.isdigit() or period[4:] not in {"03", "06", "09", "12"}:
        parser.error("--period must be YYYY03, YYYY06, YYYY09, or YYYY12")
    if not 1 <= args.pages <= 100:
        parser.error("--pages must be between 1 and 100")

    dates = pd.to_datetime(pd.read_parquet(PARQUET, columns=["report_date"])["report_date"])
    if period in set(dates.dt.strftime("%Y%m")):
        raise SystemExit(f"SKIPPED: quarter {period} is already present in {PARQUET.name}")

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CareerCompass-ETL/1.0)"})
    url, pages = find_source(session, period, args.pages)
    filename = urlparse(url).path.rsplit("/", 1)[-1]
    expected_name = f"bo-heft-d-0-{period}-xlsx.xlsx"
    if filename.lower() != expected_name:
        raise RuntimeError(f"Unexpected source filename: {filename}")

    # Deliberately restrict all writes to independent staging storage.
    RAW.mkdir(parents=True, exist_ok=True)
    target = RAW / expected_name
    if target.exists():
        raise SystemExit(f"SKIPPED: target already exists (will not overwrite): {target}")

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=RAW, prefix=f".{period}_", suffix=".part", delete=False) as temp:
            temp_path = Path(temp.name)
            count = 0
            with session.get(url, stream=True, timeout=(15, 90)) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        count += len(chunk)
                        if count > MAX_BYTES:
                            raise ValueError("Excel exceeds 100 MB safety limit")
                        temp.write(chunk)
            temp.flush()
            os.fsync(temp.fileno())

        if count == 0 or not zipfile.is_zipfile(temp_path):
            raise ValueError("Download is empty or is not an XLSX/ZIP file")
        with zipfile.ZipFile(temp_path) as workbook:
            if "xl/workbook.xml" not in workbook.namelist() or workbook.testzip() is not None:
                raise ValueError("Downloaded XLSX is missing workbook metadata or is corrupted")
        if target.exists():
            raise RuntimeError(f"Target appeared during download; refusing overwrite: {target}")
        # Exclusive target creation: never replace a pre-existing file.
        with target.open("xb") as out, temp_path.open("rb") as inp:
            while block := inp.read(1024 * 1024):
                out.write(block)
        print(f"Downloaded quarter: {period}")
        print(f"Catalogue pages checked: {pages}")
        print(f"Saved to: {target}")
        print(f"Size: {count:,} bytes; XLSX ZIP integrity: PASS")
        print("STAGING ONLY: production Parquet and application were not modified.")
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
