"""CSV loading and cleaning for ESG portfolio analysis datasets."""

from __future__ import annotations

from io import StringIO
from pathlib import Path


REQUIRED_ESG_COLUMNS = (
    "company",
    "sector",
    "year",
    "revenue_musd",
    "scope1_emissions_tco2e",
    "scope2_emissions_tco2e",
    "esg_score",
    "environment_score",
    "social_score",
    "governance_score",
    "renewable_energy_pct",
    "green_capex_pct",
    "board_independence_pct",
    "women_board_pct",
    "safety_incidents",
    "controversy_count",
)


def load_and_clean_esg_dataset(csv_path: str | Path):
    """Load, validate, and clean an ESG dataset for downstream analysis."""
    pd, np = _require_esg_dependencies()

    path = Path(csv_path)
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")

    frame = pd.read_csv(path)
    return _clean_esg_frame(frame, pd=pd, np=np)


def load_and_clean_esg_dataset_from_text(csv_text: str):
    """Load, validate, and clean an ESG dataset from uploaded CSV text."""
    pd, np = _require_esg_dependencies()
    frame = pd.read_csv(StringIO(csv_text))
    return _clean_esg_frame(frame, pd=pd, np=np)


def _clean_esg_frame(frame, *, pd, np):
    """Apply schema validation, cleaning, and derived field creation to an ESG DataFrame."""
    frame.columns = [str(column).strip().lower() for column in frame.columns]

    missing_columns = [column for column in REQUIRED_ESG_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(
            f"Input CSV is missing required ESG columns: {', '.join(missing_columns)}"
        )

    original_row_count = int(len(frame))
    frame = frame.drop_duplicates(subset=["company", "year"], keep="last").copy()
    duplicates_removed = original_row_count - int(len(frame))

    numeric_columns = [
        "year",
        "revenue_musd",
        "scope1_emissions_tco2e",
        "scope2_emissions_tco2e",
        "esg_score",
        "environment_score",
        "social_score",
        "governance_score",
        "renewable_energy_pct",
        "green_capex_pct",
        "board_independence_pct",
        "women_board_pct",
        "safety_incidents",
        "controversy_count",
    ]

    initial_missing_values = int(frame[numeric_columns].isna().sum().sum())
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    non_negative_columns = [
        "revenue_musd",
        "scope1_emissions_tco2e",
        "scope2_emissions_tco2e",
        "esg_score",
        "environment_score",
        "social_score",
        "governance_score",
        "renewable_energy_pct",
        "green_capex_pct",
        "board_independence_pct",
        "women_board_pct",
        "safety_incidents",
        "controversy_count",
    ]
    for column in non_negative_columns:
        frame.loc[frame[column] < 0, column] = np.nan

    frame = frame.sort_values(["company", "year"]).reset_index(drop=True)

    fill_columns = [
        "renewable_energy_pct",
        "green_capex_pct",
        "board_independence_pct",
        "women_board_pct",
        "safety_incidents",
        "controversy_count",
    ]
    for column in fill_columns:
        frame[column] = frame.groupby("company")[column].transform(lambda series: series.ffill().bfill())
        frame[column] = frame.groupby("sector")[column].transform(
            lambda series: series.fillna(series.median())
        )
        frame[column] = frame[column].fillna(frame[column].median())

    frame["total_emissions_tco2e"] = (
        frame["scope1_emissions_tco2e"] + frame["scope2_emissions_tco2e"]
    )
    frame["carbon_intensity"] = frame["total_emissions_tco2e"] / frame["revenue_musd"].replace(0, np.nan)
    frame["emissions_change_pct"] = frame.groupby("company")["total_emissions_tco2e"].pct_change()
    frame["esg_score_change"] = frame.groupby("company")["esg_score"].diff()

    remaining_missing_values = int(frame[numeric_columns].isna().sum().sum())
    frame.attrs["cleaning_summary"] = {
        "original_rows": original_row_count,
        "cleaned_rows": int(len(frame)),
        "duplicates_removed": duplicates_removed,
        "initial_missing_values": initial_missing_values,
        "remaining_missing_values": remaining_missing_values,
    }
    return frame


def _require_esg_dependencies():
    """Load pandas and numpy lazily so the base financial workflow stays lightweight."""
    try:
        import numpy as np
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised only when ESG stack missing
        raise SystemExit(
            "ESG analysis requires pandas and numpy. Run: python -m pip install -e .[esg]"
        ) from exc
    return pd, np
