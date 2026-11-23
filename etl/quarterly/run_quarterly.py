"""Orchestrate BA Germany quarterly Employed ETL; never publish production.

From the repository root:
    python etl/quarterly/run_quarterly.py              # discovery / plan ONLY
    python etl/quarterly/run_quarterly.py --prepare    # prepare staging ONLY

Default is read-only: it does not download or write files. --prepare may
write XLSX and Parquet files ONLY under ba_quarterly_test/{raw,processed}.
Production publication must be run separately using publish_quarterly.py.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

from discover_quarterly import REPO, START_URL, parse_page
from download_quarterly import RAW
from publish_quarterly import REAL_PRODUCTION, REAL_STAGING, check_frame, sha256
from transform_quarterly import (
    LABELS_PATH, add_level_one, parse_workbook, validate,
)


def inspect_xlsx(path: Path) -> None:
    """Verify the downloaded (or reused) XLSX is structurally valid."""
    if path.is_symlink():
        raise RuntimeError(f"Refusing symlinked Excel: {path}")
    if not path.is_file() or path.stat().st_size == 0 or not zipfile.is_zipfile(path):
        raise ValueError(f"Missing, empty, or invalid XLSX: {path}")
    with zipfile.ZipFile(path) as archive:
        if "xl/workbook.xml" not in archive.namelist() or archive.testzip() is not None:
            raise ValueError(f"Corrupt XLSX: {path}")


def existing_dates() -> tuple[pd.DataFrame, str, set[str]]:
    if not REAL_PRODUCTION.is_file() or REAL_PRODUCTION.is_symlink():
        raise FileNotFoundError(f"Safe production Parquet not found: {REAL_PRODUCTION}")
    history = pd.read_parquet(REAL_PRODUCTION)
    periods = check_frame(history, "Production")
    latest = periods.max().end_time.strftime("%Y%m")
    # The reporting date is the 1st of each quarter's final month (03/06/09/12).
    present = set(history["report_date"].dt.strftime("%Y%m"))
    if latest != max(present):
        raise ValueError("Latest period calculation disagrees with source dates")
    return history, latest, present


def discover_until_boundary(latest: str, max_pages: int) -> tuple[dict[str, str], list[int]]:
    """Read BA catalogue until the latest production quarter has been seen.

    This avoids hard-coding BA's changing pagination identifiers and avoids
    interpreting a truncated catalogue scan as evidence that no files exist.
    """
    pending: dict[int, str] = {1: START_URL}
    visited: set[int] = set()
    found: dict[str, str] = {}
    reached_boundary = False
    with requests.Session() as session:
        session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CareerCompass-ETL/1.0)"})
        while pending and len(visited) < max_pages:
            number = min(pending)
            url = pending.pop(number)
            if number in visited:
                continue
            response = session.get(url, timeout=30)
            response.raise_for_status()
            on_page, pagination = parse_page(response.text, response.url)
            print(f"Page {number}: HTTP {response.status_code}, Germany Excel: "
                  f"{', '.join(sorted(on_page, reverse=True)) or '(none)'}")
            if number == 1 and not on_page:
                raise RuntimeError("No Germany Excel on first BA page; check catalogue structure")
            for period, file_url in on_page.items():
                if period in found and found[period] != file_url:
                    raise RuntimeError(f"Conflicting BA links for {period}")
                found[period] = file_url
            visited.add(number)
            if latest in on_page:
                reached_boundary = True
                break
            for next_number, next_url in pagination.items():
                if next_number not in visited and next_number not in pending:
                    pending[next_number] = next_url
    if not reached_boundary:
        raise RuntimeError(
            f"Stopped after {len(visited)} page(s) without finding existing "
            f"latest quarter {latest}. Catalogue may be incomplete or BA changed "
            "its format. No preparation will run. Try --pages with a higher limit."
        )
    return found, sorted(visited)


def next_reporting_month(period: str) -> str:
    month = pd.Period(period, freq="M")
    if month.month not in (3, 6, 9, 12):
        raise ValueError(f"Not a quarterly reporting month: {period}")
    return (month + 3).strftime("%Y%m")


def missing_periods(found: dict[str, str], latest: str) -> list[str]:
    missing = sorted(period for period in found if period > latest)
    if missing:
        expected = next_reporting_month(latest)
        for period in missing:
            if period != expected:
                raise RuntimeError(
                    f"Gap in discovered quarters: expected {expected}, got {period}; "
                    "not preparing a partial dataset"
                )
            expected = next_reporting_month(period)
    return missing


def staging_write(frame: pd.DataFrame, target: Path) -> str:
    """Never overwrite staging. Reuse only if exactly identical."""
    if target.is_symlink():
        raise RuntimeError(f"Refusing symlinked staging file: {target}")
    if target.exists():
        pd.testing.assert_frame_equal(pd.read_parquet(target), frame, check_exact=True)
        return f"REUSED (verified): {target}"
    # Exclusive creation; no replacing an existing staging file.
    with target.open("xb") as handle:
        frame.to_parquet(handle, index=False)
    pd.testing.assert_frame_equal(pd.read_parquet(target), frame, check_exact=True)
    return f"CREATED (read-back PASS): {target}"


def verify_stage_locations() -> None:
    test_root = REPO / "ba_quarterly_test"
    for path in (test_root, RAW, REAL_STAGING):
        if path.is_symlink():
            raise RuntimeError(f"Refusing symlinked staging directory: {path}")
    if RAW.resolve() == REAL_PRODUCTION.parent.resolve() or REAL_STAGING.resolve() == REAL_PRODUCTION.parent.resolve():
        raise RuntimeError("Staging cannot coincide with production directory")


def prepare(history: pd.DataFrame, new: list[str], pages: int) -> None:
    verify_stage_locations()
    original_hash = sha256(REAL_PRODUCTION)
    source_frames: list[tuple[str, pd.DataFrame]] = []
    for period in new:
        excel = RAW / f"bo-heft-d-0-{period}-xlsx.xlsx"
        if excel.exists():
            inspect_xlsx(excel)
            print(f"REUSED source XLSX: {excel}")
        else:
            # Delegate download safety to the tested download_quarterly.py.
            # It refuses overwrite and validates the XLSX ZIP before saving.
            import subprocess
            command = [sys.executable, str(REPO / "etl" / "quarterly" / "download_quarterly.py"),
                       "--period", period, "--pages", str(pages)]
            subprocess.run(command, cwd=REPO, check=True)
            inspect_xlsx(excel)

        frame = add_level_one(parse_workbook(excel, period), LABELS_PATH)
        validate(frame, period)
        frame["report_date"] = frame["report_date"].astype(history["report_date"].dtype)
        if frame.columns.tolist() != history.columns.tolist():
            raise ValueError(f"Column mismatch in quarter {period}")
        if not frame.dtypes.equals(history.dtypes):
            raise ValueError(f"Dtype mismatch in quarter {period}")
        source_frames.append((period, frame))
        print(f"TRANSFORM PASS: {period} / {len(frame):,} rows")
    combined = pd.concat([history, *(frame for _, frame in source_frames)], ignore_index=True)
    check_frame(combined, "Combined staging")
    if len(combined) != len(history) + sum(len(frame) for _, frame in source_frames):
        raise ValueError("Combined row count mismatch")
    pd.testing.assert_frame_equal(combined.iloc[:len(history)].reset_index(drop=True),
                                  history.reset_index(drop=True), check_exact=True)
    if sha256(REAL_PRODUCTION) != original_hash:
        raise RuntimeError("Production changed during preparation; refusing staging writes")

    verify_stage_locations()
    REAL_STAGING.mkdir(parents=True, exist_ok=True)
    # Reuse/verify existing quarter staging; all writes restricted to ba_quarterly_test.
    for period, frame in source_frames:
        path = REAL_STAGING / f"employed_{period}_full_kldb.parquet"
        print(staging_write(frame, path))
    final_path = REAL_STAGING / f"employed_full_through_{new[-1]}.parquet"
    print(staging_write(combined, final_path))
    if sha256(REAL_PRODUCTION) != original_hash:
        raise RuntimeError("Production changed during staging; STOP and investigate")
    print(f"STAGING READY: {len(combined):,} rows, through {new[-1]}")
    print("Production unchanged: SHA256 PASS")
    print("NOT PUBLISHED: publication requires a separate explicit command")


def main() -> None:
    parser = argparse.ArgumentParser(description="BA quarterly Employed: safe orchestration")
    parser.add_argument("--pages", type=int, default=10,
                        help="Maximum catalogue pages (default: 10); stop when newest existing quarter is found")
    parser.add_argument("--prepare", action="store_true",
                        help="Download/transform into ba_quarterly_test only; NEVER publish")
    args = parser.parse_args()
    if not 1 <= args.pages <= 100:
        parser.error("--pages must be between 1 and 100")
    print("MODE:", "PREPARE STAGING ONLY" if args.prepare else "READ-ONLY DISCOVERY / PLAN")
    history, latest, _ = existing_dates()
    print(f"Production: {len(history):,} rows, latest {latest}")
    found, checked = discover_until_boundary(latest, args.pages)
    print("Pages checked:", checked)
    new = missing_periods(found, latest)
    if not new:
        print("NO NEW QUARTERS: nothing to prepare")
        print("Production untouched; no files downloaded or modified")
        return
    print("Missing quarters:", ", ".join(new))
    if not args.prepare:
        print("READ-ONLY: nothing downloaded or modified. Use --prepare to stage the update.")
        return
    prepare(history, new, args.pages)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"QUARTERLY ETL STOPPED: {type(exc).__name__}: {exc}") from exc
