"""CSV loading and cleaning for ESG portfolio analysis datasets.

This module is the ESG ingestion and data quality layer. It validates the raw
company-year CSV schema, removes duplicate company-year observations, coerces
numeric fields, imputes selected missing sustainability fields, and derives
features used by ESG summaries, risk signals, dashboards, and API responses.
"""

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
    """Load, validate, and clean an ESG dataset from disk.

    Args:
        csv_path: Path to a CSV with one row per company-year observation and
            the columns listed in ``REQUIRED_ESG_COLUMNS``.

    Returns:
        pd.DataFrame: Cleaned ESG frame sorted by company and year, with
        imputation audit columns and derived emissions metrics.

    Raises:
        ValueError: If the file does not exist or required columns are missing.
        SystemExit: If pandas or numpy is not installed.
    """
    pd, np = _require_esg_dependencies()

    path = Path(csv_path)
    if not path.exists():
        raise ValueError(f"Input file does not exist: {path}")

    frame = pd.read_csv(path)
    return _clean_esg_frame(frame, pd=pd, np=np)


def load_and_clean_esg_dataset_from_text(csv_text: str):
    """Load, validate, and clean ESG data from uploaded CSV text.

    Args:
        csv_text: Raw CSV content with the ESG company-year schema.

    Returns:
        pd.DataFrame: Cleaned ESG frame with imputation audit fields and derived
        metrics such as ``carbon_intensity`` and ``esg_score_change``.

    Raises:
        ValueError: If required ESG columns are missing.
        SystemExit: If pandas or numpy is not installed.
    """
    pd, np = _require_esg_dependencies()
    frame = pd.read_csv(StringIO(csv_text))
    return _clean_esg_frame(frame, pd=pd, np=np)


def _clean_esg_frame(frame, *, pd, np):
    """Validate, clean, enrich, and audit an ESG DataFrame.

    Args:
        frame: Raw ESG DataFrame loaded from CSV. Expected grain is one
            company-year row before duplicate removal.
        pd: pandas module injected by the caller.
        np: numpy module injected by the caller.

    Returns:
        pd.DataFrame: Cleaned ESG frame with deduplicated company-year rows,
        numeric ESG fields, imputation source columns, imputation flags, and
        derived fields including ``total_emissions_tco2e``,
        ``carbon_intensity``, ``emissions_change_pct``, and
        ``esg_score_change``.

    Raises:
        ValueError: If one or more required ESG columns are missing.

    Notes:
        Duplicate company-year rows keep the last occurrence. Missing values in
        selected sustainability fields are filled in this order: company
        history, sector median, dataset median. The cleaning audit summary is
        stored in ``frame.attrs["cleaning_summary"]``.
    """
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
    pre_fill_missing = frame[fill_columns].isna().copy()
    for column in fill_columns:
        source_column = f"{column}_imputation_source"
        frame[source_column] = "original"

        company_filled = frame.groupby("company")[column].transform(lambda series: series.ffill().bfill())
        company_fill_mask = frame[column].isna() & company_filled.notna()
        frame[column] = company_filled
        frame.loc[company_fill_mask, source_column] = "company_history"

        sector_filled = frame.groupby("sector")[column].transform(
            lambda series: series.fillna(series.median())
        )
        sector_fill_mask = frame[column].isna() & sector_filled.notna()
        frame[column] = sector_filled
        frame.loc[sector_fill_mask, source_column] = "sector_median"

        dataset_median = frame[column].median()
        dataset_fill_mask = frame[column].isna() & pd.notna(dataset_median)
        frame[column] = frame[column].fillna(dataset_median)
        frame.loc[dataset_fill_mask, source_column] = "dataset_median"

        still_missing_mask = frame[column].isna() & pre_fill_missing[column]
        frame.loc[still_missing_mask, source_column] = "missing"
        frame[f"{column}_imputed"] = pre_fill_missing[column] & frame[column].notna()

    imputation_flag_columns = [f"{column}_imputed" for column in fill_columns]
    frame["imputed_field_count"] = frame[imputation_flag_columns].sum(axis=1).astype(int)
    frame["imputation_applied"] = frame["imputed_field_count"] > 0

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
        "rows_with_imputation": int(frame["imputation_applied"].sum()),
        "imputed_field_total": int(frame["imputed_field_count"].sum()),
        "company_history_imputations": int(
            sum((frame[f"{column}_imputation_source"] == "company_history").sum() for column in fill_columns)
        ),
        "sector_median_imputations": int(
            sum((frame[f"{column}_imputation_source"] == "sector_median").sum() for column in fill_columns)
        ),
        "dataset_median_imputations": int(
            sum((frame[f"{column}_imputation_source"] == "dataset_median").sum() for column in fill_columns)
        ),
    }
    return frame


def _require_esg_dependencies():
    """Load ESG dependencies only when the ESG workflow is used.

    Returns:
        tuple: ``(pd, np)`` modules used for DataFrame cleaning and numeric
        missing-value handling.

    Raises:
        SystemExit: If pandas or numpy is unavailable in the active environment.
    """
    try:
        import numpy as np
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised only when ESG stack missing
        raise SystemExit(
            "ESG analysis requires pandas and numpy. Run: python -m pip install -e .[esg]"
        ) from exc
    return pd, np
