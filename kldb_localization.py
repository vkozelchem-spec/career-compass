"""Official German/English KldB occupation labels (2020 classification).

The classification labels are for presentation only. Filtering must use
original source columns/codes; a translated occupation name never becomes
a join or filter key for statistics.
"""

import csv
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=2)
def load_kldb_labels(csv_path: str | Path) -> dict[str, dict[str, str]]:
    """Load official EN/DE names, preserving leading zeros in KldB codes."""
    labels: dict[str, dict[str, str]] = {}
    with Path(csv_path).open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        expected = {"occupation_code", "name_de", "name_en"}
        if not expected.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"Expected CSV columns: {sorted(expected)}")
        for row in reader:
            code = str(row["occupation_code"]).strip()
            de = (row["name_de"] or "").strip()
            en = (row["name_en"] or "").strip()
            if not code or not de or not en:
                raise ValueError(f"Missing KldB code or translation: {row!r}")
            if code in labels:
                raise ValueError(f"Duplicate KldB code: {code}")
            labels[code] = {"De": de, "En": en}
    if not labels:
        raise ValueError("The KldB translation CSV is empty")
    return labels


def compact_english_occupation(name: str) -> str:
    """Short UI label for official KldB English names.

    The CSV retains the complete BA wording. Only the predictable leading
    phrase is removed in presentation, without changing the classification.
    """
    prefix = "Occupations in "
    if name.startswith(prefix):
        subject = name[len(prefix):]
        if subject.startswith("the "):
            subject = subject[4:]
        return subject[:1].upper() + subject[1:]
    return name


def occupation_label(
    code: str,
    language: str,
    fallback: str,
    catalog: dict[str, dict[str, str]],
    *,
    compact: bool = False,
) -> str:
    """Present KldB name by stable code; never alter dataset filter values."""
    result = catalog.get(str(code), {}).get(language, fallback)
    return compact_english_occupation(result) if compact and language == "En" else result
