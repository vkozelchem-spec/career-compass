"""Read-only trial of the Colab employment transformation for one BA quarter.

Usage from the Career Compass project root:
    python etl/quarterly/transform_quarterly.py --period 202603

This script reads the local BA workbook and the existing KldB-1 label source,
then validates a single-quarter DataFrame in memory. It does NOT write files.
It never changes production Parquet, the Streamlit app, or source Excel.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "ba_quarterly_test" / "raw"
LABELS_PATH = ROOT / "data" / "german_labour_market.parquet"
OUTPUT_COLUMNS = [
    "report_date",
    "occupation_level",
    "occupation_code",
    "occupation_name",
    "qualification",
    "employed",
]
QUALIFICATIONS = {
    "employed_total": "Gesamt",
    "employed_helper": "Helfer",
    "employed_skilled": "Fachkraft",
    "employed_specialist": "Spezialist",
    "employed_expert": "Experte",
}
BUSINESS_KEY = [
    "report_date", "occupation_level", "occupation_code", "qualification"
]


def parse_period(value: str) -> str:
    if not re.fullmatch(r"\d{6}", value):
        raise argparse.ArgumentTypeError("Expected YYYYMM (for example 202603)")
    year, month = int(value[:4]), int(value[4:])
    if year < 2000 or month not in (3, 6, 9, 12):
        raise argparse.ArgumentTypeError("Expected a quarterly month: 03, 06, 09 or 12")
    return value


def parse_workbook(path: Path, period: str) -> pd.DataFrame:
    # This follows the parser in Final Project6_Employed (7).ipynb, cell 13.
    raw = pd.read_excel(path, sheet_name="SVB - Tabelle II", header=None)
    if raw.shape[1] < 8:
        raise ValueError(f"Excel layout changed: {raw.shape[1]} columns (need A:H)")

    occupation = raw.iloc[:, 0].astype("string").str.strip()
    total_mask = occupation.eq("Insgesamt").fillna(False)
    if int(total_mask.sum()) != 1:
        raise ValueError(f"Expected one 'Insgesamt' row, found {int(total_mask.sum())}")

    source_cols = [0, 1, 4, 5, 6, 7]  # A, B, E, F, G, H
    metric_cols = [
        "employed_total", "employed_helper", "employed_skilled",
        "employed_specialist", "employed_expert",
    ]

    total = raw.loc[total_mask, source_cols].copy()
    total.columns = ["occupation", *metric_cols]
    total["occupation_code"] = "DE"
    total["occupation_level"] = 0
    total["occupation_name"] = "Germany"
    total = total.drop(columns="occupation")

    codes = occupation.str.extract(r"^(\d{1,4})\s+")[0]
    mask = codes.notna()
    parsed = raw.loc[mask, source_cols].copy()
    parsed.columns = ["occupation", *metric_cols]
    parsed["occupation_code"] = codes.loc[mask].to_numpy()
    parsed["occupation_level"] = parsed["occupation_code"].str.len().astype(int)
    parsed["occupation_name"] = (
        parsed["occupation"].str.replace(r"^\d{1,4}\s+", "", regex=True).str.strip()
    )
    parsed = parsed.drop(columns="occupation")
    parsed = pd.concat([total, parsed], ignore_index=True)

    parsed[metric_cols] = (
        parsed[metric_cols].apply(pd.to_numeric, errors="coerce").astype("Float64")
    )
    parsed = parsed.melt(
        id_vars=["occupation_code", "occupation_level", "occupation_name"],
        value_vars=metric_cols,
        var_name="qualification",
        value_name="employed",
    )
    parsed["qualification"] = parsed["qualification"].map(QUALIFICATIONS)
    parsed["report_date"] = pd.to_datetime(period, format="%Y%m")
    return parsed[OUTPUT_COLUMNS].reset_index(drop=True)


def add_level_one(frame: pd.DataFrame, labels_path: Path) -> pd.DataFrame:
    # Follows Colab cells 17-20: aggregate level-2 to level-1 and join labels.
    level_one = frame.loc[frame["occupation_level"] == 2].copy()
    level_one["occupation_code"] = level_one["occupation_code"].astype(str).str[0]
    level_one = (
        level_one.groupby(
            ["report_date", "occupation_code", "qualification"], as_index=False
        )["employed"].sum(min_count=1)
    )
    level_one["occupation_level"] = 1

    labels = pd.read_parquet(labels_path, columns=[
        "occupation_level", "occupation_code", "occupation_name"
    ])
    labels = (
        labels.loc[labels["occupation_level"] == 1, ["occupation_code", "occupation_name"]]
        .drop_duplicates()
    )
    if labels["occupation_code"].duplicated().any():
        raise ValueError("Ambiguous level-1 names in german_labour_market.parquet")
    level_one = level_one.merge(
        labels, on="occupation_code", how="left", validate="many_to_one"
    )
    if level_one["occupation_name"].isna().any():
        missing = sorted(level_one.loc[
            level_one["occupation_name"].isna(), "occupation_code"
        ].unique().tolist())
        raise ValueError(f"Missing level-1 names for codes: {missing}")
    return pd.concat([frame, level_one[OUTPUT_COLUMNS]], ignore_index=True)


def validate(frame: pd.DataFrame, period: str) -> None:
    if frame.empty or frame.columns.tolist() != OUTPUT_COLUMNS:
        raise ValueError("Empty data or unexpected output columns")
    if frame[BUSINESS_KEY].isna().any().any():
        raise ValueError("Null values in business key")
    duplicates = int(frame.duplicated(subset=BUSINESS_KEY).sum())
    if duplicates:
        raise ValueError(f"Duplicate business keys: {duplicates}")
    if not frame["report_date"].eq(pd.to_datetime(period, format="%Y%m")).all():
        raise ValueError("Unexpected report date")
    if sorted(frame["qualification"].unique().tolist()) != sorted(QUALIFICATIONS.values()):
        raise ValueError("Unexpected qualification labels")
    if not set(frame["occupation_level"].unique()) == {0, 1, 2, 3, 4}:
        raise ValueError("Unexpected KldB levels")
    counts = frame.groupby(
        ["occupation_level", "occupation_code"]
    )["qualification"].nunique()
    if not counts.eq(5).all():
        raise ValueError("Some occupation codes do not have all five qualifications")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only BA quarterly transformation test")
    parser.add_argument("--period", required=True, type=parse_period)
    args = parser.parse_args()
    path = RAW_DIR / f"bo-heft-d-0-{args.period}-xlsx.xlsx"
    for file in (path, LABELS_PATH):
        if not file.is_file():
            raise FileNotFoundError(f"Required input not found: {file}")

    print("Source Excel:", path.name)
    frame = parse_workbook(path, args.period)
    print("Parsed rows before level-1 aggregation:", len(frame))
    final = add_level_one(frame, LABELS_PATH)
    validate(final, args.period)
    print("Validated rows including level 1:", len(final))
    print("Report date:", final["report_date"].iloc[0].date())
    print("Rows by KldB level:", final["occupation_level"].value_counts().sort_index().to_dict())
    print("Employed missing values:", int(final["employed"].isna().sum()))
    print("Duplicate business keys: 0")
    print("READ-ONLY: no Parquet, Excel, or application files changed.")


if __name__ == "__main__":
    main()
