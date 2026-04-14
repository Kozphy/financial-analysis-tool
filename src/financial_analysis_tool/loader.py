"""CSV loading and validation for structured financial statement input."""

from __future__ import annotations

import csv
import re
from io import StringIO
from pathlib import Path
from typing import TextIO

from .models import FinancialStatementRecord


REQUIRED_COLUMNS = (
    "period",
    "revenue",
    "cost_of_revenue",
    "operating_expenses",
    "net_income",
    "current_assets",
    "current_liabilities",
    "total_assets",
    "total_liabilities",
)


def load_financial_statements(csv_path: str | Path) -> list[FinancialStatementRecord]:
    """Load validated financial statement records from a CSV file path."""
    path = Path(csv_path)
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return _load_from_handle(handle)


def load_financial_statements_from_text(csv_text: str) -> list[FinancialStatementRecord]:
    """Load validated financial statement records from uploaded CSV text."""
    return _load_from_handle(StringIO(csv_text))


def _load_from_handle(handle: TextIO) -> list[FinancialStatementRecord]:
    """Parse CSV rows from an open text handle and return sorted records."""
    reader = csv.DictReader(handle)
    if reader.fieldnames is None:
        raise ValueError("Input CSV is missing a header row.")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
    if missing_columns:
        raise ValueError(f"Input CSV is missing required columns: {', '.join(missing_columns)}")

    records: list[FinancialStatementRecord] = []
    for row_number, row in enumerate(reader, start=2):
        period = (row.get("period") or "").strip()
        if not period:
            raise ValueError(f"Row {row_number} is missing a period value.")

        records.append(
            FinancialStatementRecord(
                period=period,
                revenue=_parse_float(row, "revenue", row_number),
                cost_of_revenue=_parse_float(row, "cost_of_revenue", row_number),
                operating_expenses=_parse_float(row, "operating_expenses", row_number),
                net_income=_parse_float(row, "net_income", row_number),
                current_assets=_parse_float(row, "current_assets", row_number),
                current_liabilities=_parse_float(row, "current_liabilities", row_number),
                total_assets=_parse_float(row, "total_assets", row_number),
                total_liabilities=_parse_float(row, "total_liabilities", row_number),
            )
        )

    if not records:
        raise ValueError("Input CSV does not contain any financial statement rows.")

    return sorted(records, key=lambda record: _period_sort_key(record.period))


def _parse_float(row: dict[str, str], column: str, row_number: int) -> float:
    """Parse one numeric field from a CSV row and raise a row-aware error on failure."""
    raw_value = (row.get(column) or "").replace(",", "").strip()
    if raw_value == "":
        raise ValueError(f"Row {row_number} is missing a value for {column}.")

    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"Row {row_number} has an invalid numeric value for {column}: {raw_value}") from exc


def _period_sort_key(period: str) -> tuple[int, int]:
    """Convert a period label such as 2025-Q4 into a sortable year-quarter key."""
    match = re.fullmatch(r"(\d{4})-Q([1-4])", period)
    if not match:
        raise ValueError(f"Unsupported period format: {period}. Expected values such as 2025-Q4.")
    return int(match.group(1)), int(match.group(2))
