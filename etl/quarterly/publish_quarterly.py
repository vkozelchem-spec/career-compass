"""Safely inspect or publish a quarterly BA Employed staging Parquet.

Default is READ-ONLY (real production paths):
    python etl/quarterly/publish_quarterly.py
    python etl/quarterly/publish_quarterly.py --dry-run

Sandbox (prepare *copies* in ba_quarterly_test/publish_sandbox/{data,processed}):
    python etl/quarterly/publish_quarterly.py --sandbox --dry-run
    python etl/quarterly/publish_quarterly.py --sandbox --publish --confirm SANDBOX

REAL publication (only after successful sandbox testing and separate approval):
    python etl/quarterly/publish_quarterly.py --publish --confirm PUBLISH

A confirmed publication creates a SHA256-verified, timestamped backup next to
its target, copies the verified candidate to a same-directory temporary file,
then performs os.replace. If post-replacement verification fails, an automatic
rollback is attempted without consuming the backup. This script never changes
app.py, any Excel, or other datasets. Do not run concurrently with another
process writing the production file. OneDrive synchronization can interfere
with file operations; do not run publication while a file is changing.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REAL_PRODUCTION = ROOT / "data" / "employed_people_full_kldb.parquet"
REAL_STAGING = ROOT / "ba_quarterly_test" / "processed"
SANDBOX = ROOT / "ba_quarterly_test" / "publish_sandbox"
SANDBOX_PRODUCTION = SANDBOX / "data" / REAL_PRODUCTION.name
SANDBOX_STAGING = SANDBOX / "processed"

KEY = ["report_date", "occupation_level", "occupation_code", "qualification"]
COLUMNS = [
    "report_date", "occupation_level", "occupation_code", "occupation_name",
    "qualification", "employed",
]
FILE_PATTERN = re.compile(r"^employed_full_through_(\d{6})\.parquet$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frame(frame: pd.DataFrame, label: str) -> pd.PeriodIndex:
    if frame.empty:
        raise ValueError(f"{label}: empty dataset")
    if frame.columns.tolist() != COLUMNS:
        raise ValueError(f"{label}: unexpected column order or names")
    if frame[KEY].isna().any().any():
        raise ValueError(f"{label}: null business keys")
    if frame.duplicated(subset=KEY).any():
        raise ValueError(f"{label}: duplicate business keys")
    dates = frame["report_date"]
    if not pd.api.types.is_datetime64_any_dtype(dates.dtype):
        raise ValueError(f"{label}: report_date must be datetime")
    if (dates.isna().any() or not dates.dt.day.eq(1).all()
            or not dates.dt.month.isin((3, 6, 9, 12)).all()):
        raise ValueError(f"{label}: invalid quarterly reporting dates")
    unique_dates = pd.DatetimeIndex(dates.unique()).sort_values()
    periods = pd.PeriodIndex(unique_dates.to_period("Q"))
    if periods.has_duplicates:
        raise ValueError(f"{label}: multiple report dates map to one quarter")
    expected = pd.period_range(periods.min(), periods.max(), freq="Q")
    if not periods.equals(expected):
        raise ValueError(f"{label}: gaps in quarterly timeline")
    return periods


def paths(sandbox: bool) -> tuple[Path, Path]:
    if not sandbox:
        return REAL_PRODUCTION, REAL_STAGING
    # Sandbox is an explicit tree, never an alias to the real data directory.
    expected = ROOT / "ba_quarterly_test" / "publish_sandbox"
    if SANDBOX != expected:
        raise RuntimeError("Sandbox directory does not match its fixed location")
    for p in (SANDBOX, SANDBOX / "data", SANDBOX_STAGING,
              SANDBOX_PRODUCTION):
        if p.is_symlink():
            raise RuntimeError(f"Sandbox path must not be a symlink: {p}")
    if SANDBOX_PRODUCTION.resolve() == REAL_PRODUCTION.resolve():
        raise RuntimeError("Sandbox target resolves to real production")
    if SANDBOX_STAGING.resolve() == REAL_STAGING.resolve():
        raise RuntimeError("Sandbox staging resolves to real staging")
    return SANDBOX_PRODUCTION, SANDBOX_STAGING


def preflight(production: Path, staging_dir: Path):
    if not production.is_file():
        raise FileNotFoundError(f"Production file not found: {production}")
    if not staging_dir.is_dir():
        raise FileNotFoundError(f"Staging directory not found: {staging_dir}")

    history = pd.read_parquet(production)
    historical_quarters = check_frame(history, "Production")
    print(f"Production: {len(history):,} rows / {len(historical_quarters)} quarters"
          f" / latest {historical_quarters.max()}")

    candidates = {}
    for path in staging_dir.glob("employed_full_through_*.parquet"):
        match = FILE_PATTERN.fullmatch(path.name)
        if not match:
            raise ValueError(f"Unexpected candidate filename: {path.name}")
        if path.is_symlink():
            raise ValueError(f"Candidate must not be symlink: {path}")
        period = pd.Period(match.group(1), freq="M")
        if period.month not in (3, 6, 9, 12):
            raise ValueError(f"Candidate not a quarterly reporting month: {path.name}")
        if period in candidates:
            raise ValueError(f"Duplicate candidate reporting month: {period}")
        candidates[period] = path
    if not candidates:
        raise FileNotFoundError(f"No combined quarterly candidates in {staging_dir}")
    filename_month = max(candidates)
    candidate_path = candidates[filename_month]
    candidate = pd.read_parquet(candidate_path)
    candidate_quarters = check_frame(candidate, "Staging")
    if not history.dtypes.equals(candidate.dtypes):
        raise ValueError("Production and candidate dtypes differ")
    if candidate_quarters.min() != historical_quarters.min():
        raise ValueError("Candidate historical starting quarter differs")
    if candidate_quarters.max() != filename_month.asfreq("Q"):
        raise ValueError("Candidate final reporting quarter does not match filename")
    if candidate_quarters.max() <= historical_quarters.max():
        raise ValueError("Candidate has no newer quarters than production")

    existing = candidate.loc[candidate["report_date"] <= history["report_date"].max()]
    pd.testing.assert_frame_equal(
        existing.reset_index(drop=True), history.reset_index(drop=True),
        check_exact=True, check_dtype=True,
    )
    additional = candidate.loc[candidate["report_date"] > history["report_date"].max()]
    if additional.empty or len(candidate) != len(history) + len(additional):
        raise ValueError("Staging size mismatch or no new rows")
    added = pd.PeriodIndex(additional["report_date"].dt.to_period("Q").unique()).sort_values()
    if not added.equals(pd.period_range(historical_quarters.max() + 1, candidate_quarters.max(), freq="Q")):
        raise ValueError("New quarters are not contiguous immediately after production")
    production_hash, candidate_hash = sha256(production), sha256(candidate_path)
    print(f"Candidate: {candidate_path.name} / {len(candidate):,} rows / "
          f"{len(candidate_quarters)} quarters")
    print(f"Added quarters: {', '.join(map(str, added))} / {len(additional):,} rows")
    print("PASS: keys, schema, dtypes, reporting dates, continuous quarters")
    print("PASS: every production row preserved exactly, in its original order")
    print(f"Production SHA256: {production_hash}")
    print(f"Candidate SHA256:  {candidate_hash}")
    return candidate_path, production_hash, candidate_hash, len(candidate)


def make_temp(parent: Path, prefix: str) -> Path:
    fd, name = tempfile.mkstemp(prefix=prefix, suffix=".parquet.tmp", dir=parent)
    os.close(fd)
    return Path(name)


def copy_verified(source: Path, target: Path, expected_hash: str) -> None:
    # Caller must supply a new, private target; never copy over a production file.
    with source.open("rb") as inp, target.open("wb") as out:
        shutil.copyfileobj(inp, out, length=1024 * 1024)
        out.flush()
        os.fsync(out.fileno())
    if sha256(target) != expected_hash:
        raise ValueError(f"SHA256 verification failed after copying to {target}")


def publish(production: Path, candidate: Path, original_hash: str,
            candidate_hash: str, expected_rows: int) -> None:
    lock = production.with_name(production.name + ".publish.lock")
    lock_owned = False
    target_temp = None
    rollback_temp = None
    replaced = False
    backup = None
    try:
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise RuntimeError(f"Publication lock already exists: {lock}") from exc
        lock_owned = True
        with os.fdopen(fd, "w") as out:
            out.write(f"pid={os.getpid()}\n")
        if sha256(production) != original_hash or sha256(candidate) != candidate_hash:
            raise RuntimeError("Input changed since preflight: publication aborted")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = production.with_name(
            f"{production.stem}.backup_{timestamp}_{original_hash[:8]}.parquet"
        )
        # Exclusive creation: never overwrite an older backup.
        with backup.open("xb") as out, production.open("rb") as inp:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        if sha256(backup) != original_hash:
            raise RuntimeError(f"Backup verification failed: {backup}")
        print(f"Verified backup: {backup}")

        target_temp = make_temp(production.parent, ".quarterly_publish_")
        copy_verified(candidate, target_temp, candidate_hash)
        if len(pd.read_parquet(target_temp)) != expected_rows:
            raise RuntimeError("Candidate temporary copy row count changed")
        if sha256(production) != original_hash:
            raise RuntimeError("Production changed while preparing publication")
        os.replace(target_temp, production)
        replaced = True
        target_temp = None
        if sha256(production) != candidate_hash:
            raise RuntimeError("Post-replacement SHA256 check failed")
        resulting = pd.read_parquet(production)
        check_frame(resulting, "Published")
        if len(resulting) != expected_rows:
            raise RuntimeError("Post-replacement row count mismatch")
        print(f"PUBLISHED: {production}")
        print(f"Rows: {len(resulting):,} | SHA256: {candidate_hash}")
        print(f"Backup retained: {backup}")
    except BaseException as exc:
        if replaced and backup is not None:
            try:
                rollback_temp = make_temp(production.parent, ".quarterly_rollback_")
                copy_verified(backup, rollback_temp, original_hash)
                os.replace(rollback_temp, production)
                rollback_temp = None
                if sha256(production) != original_hash:
                    raise RuntimeError("Rollback hash mismatch")
                print("AUTOMATIC ROLLBACK: PASS; original production restored")
                print(f"Backup retained: {backup}")
            except Exception as rollback_exc:
                print(f"CRITICAL: automatic rollback FAILED: {rollback_exc}")
                print(f"Verified backup should be available at: {backup}")
        raise
    finally:
        if target_temp is not None:
            target_temp.unlink(missing_ok=True)
        if rollback_temp is not None:
            rollback_temp.unlink(missing_ok=True)
        if lock_owned:
            lock.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quarterly BA Employed publication (dry-run by default)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Check without writing (default)")
    group.add_argument("--publish", action="store_true", help="Publish (requires --confirm)")
    parser.add_argument("--sandbox", action="store_true", help="Use test-only sandbox copies")
    parser.add_argument("--confirm", default="", help="SANDBOX or PUBLISH confirmation token")
    args = parser.parse_args()
    expected_confirm = "SANDBOX" if args.sandbox else "PUBLISH"
    if args.publish and args.confirm != expected_confirm:
        parser.error(f"--publish requires --confirm {expected_confirm}")
    if not args.publish and args.confirm:
        parser.error("--confirm is valid only with --publish")

    production, staging_dir = paths(args.sandbox)
    print("TARGET: SANDBOX COPIES ONLY" if args.sandbox else "TARGET: REAL PRODUCTION PATH")
    print("MODE: EXPLICIT PUBLICATION" if args.publish else "MODE: READ-ONLY DRY-RUN")
    candidate, old_hash, new_hash, expected_rows = preflight(production, staging_dir)
    if not args.publish:
        print("DRY-RUN PASSED. Nothing downloaded, copied, or modified.")
        print("Potential publication would make a verified timestamped backup "
              "and replace the target atomically.")
        return
    # Recheck sandbox location just before writing.
    if args.sandbox:
        paths(True)
    publish(production, candidate, old_hash, new_hash, expected_rows)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(f"PUBLICATION STOPPED: {type(exc).__name__}: {exc}") from exc
