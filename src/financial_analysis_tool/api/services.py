"""Application services that adapt existing analysis workflows for the API.

This module is the boundary between HTTP routes and the analytics package. It
loads sample CSV artifacts, reuses existing financial and ESG pipelines, converts
pandas/dataclass outputs into JSON-safe dictionaries, and delegates business
rules to the risk signal and decision engines.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from ..config import (
    DEFAULT_COMPANY_NAME,
    DEFAULT_ESG_AUDIENCE,
    DEFAULT_ESG_CLEANED_DATA_OUTPUT,
    DEFAULT_ESG_CORRELATION_CHART,
    DEFAULT_ESG_INPUT_PATH,
    DEFAULT_ESG_REPORT_OUTPUT,
    DEFAULT_ESG_RISK_CHART,
    DEFAULT_ESG_SUMMARY_OUTPUT,
    DEFAULT_ESG_TREND_CHART,
    DEFAULT_FINANCIAL_POSITION_CHART,
    DEFAULT_INPUT_PATH,
    DEFAULT_PROFITABILITY_CHART,
    DEFAULT_REPORT_OUTPUT,
    DEFAULT_SUMMARY_OUTPUT,
    AnalysisConfig,
    EsgAnalysisConfig,
)
from ..decision_engine import map_signals_to_decision
from ..esg_pipeline import EsgAnalysisArtifacts, analyze_esg_dataset, run_esg_analysis_pipeline
from ..pipeline import AnalysisArtifacts, analyze_financial_statements, run_analysis_pipeline
from ..risk_signals import (
    RiskSignal,
    build_esg_risk_signals,
    build_financial_risk_signals,
)


SERVICE_NAME = "Financial ESG Risk Intelligence API"
SERVICE_VERSION = "0.1.0"


class CompanyNotFoundError(ValueError):
    """Raised when the requested company is not present in the sample universe."""


class InvalidPipelineModeError(ValueError):
    """Raised when the pipeline run mode is not supported."""


def get_health() -> dict[str, str]:
    """Return service metadata for health checks."""
    return {"service": SERVICE_NAME, "status": "OK", "version": SERVICE_VERSION}


def list_companies() -> list[str]:
    """Return companies available through the sample data API.

    Returns:
        list[str]: Alphabetized union of the financial sample company and ESG
        sample companies.
    """
    esg_companies = sorted(
        str(company) for company in _esg_artifacts().cleaned_frame["company"].dropna().unique()
    )
    companies = {DEFAULT_COMPANY_NAME, *esg_companies}
    return sorted(companies)


def get_company_features(company: str) -> dict[str, Any]:
    """Return API-ready financial and ESG features for one company.

    The financial sample contains a single named company, while the ESG sample
    contains multiple companies. This service combines whichever feature sets
    are available and returns empty sections instead of leaking internal objects.
    """
    canonical_company = _resolve_company(company)
    financial_artifacts = _financial_artifacts()
    esg_artifacts = _esg_artifacts()

    financial_summary = None
    financial_periods: list[dict[str, Any]] = []
    if canonical_company.casefold() == DEFAULT_COMPANY_NAME.casefold():
        financial_summary = financial_artifacts.summary.to_dict()
        financial_periods = [period.to_dict() for period in financial_artifacts.period_metrics]

    company_frame = _company_esg_frame(canonical_company, esg_artifacts)
    esg_history = _frame_to_records(company_frame) if company_frame is not None else []
    esg_latest = esg_history[-1] if esg_history else None

    return {
        "company": canonical_company,
        "financial_summary": financial_summary,
        "financial_periods": financial_periods,
        "esg_history": esg_history,
        "esg_latest": esg_latest,
    }


def get_company_signals(company: str) -> list[dict[str, Any]]:
    """Return explainable risk signals for one company.

    Args:
        company: Company name, case-insensitive.

    Returns:
        list[dict[str, Any]]: JSON-ready risk signal dictionaries.

    Raises:
        CompanyNotFoundError: If the company is not in the sample universe.
    """
    signals = _build_signals(company)
    return [signal.to_dict() for signal in signals]


def get_company_risk_profile(company: str) -> dict[str, Any]:
    """Return severity counts and supporting risk signals for one company."""
    canonical_company = _resolve_company(company)
    signals = _build_signals(canonical_company)
    severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for signal in signals:
        severity_counts[signal.severity] += 1

    highest_severity = "LOW"
    if severity_counts["HIGH"]:
        highest_severity = "HIGH"
    elif severity_counts["MEDIUM"]:
        highest_severity = "MEDIUM"

    return {
        "company": canonical_company,
        "highest_severity": highest_severity,
        "signal_count": len(signals),
        "severity_counts": severity_counts,
        "signals": [signal.to_dict() for signal in signals],
    }


def get_company_decision(company: str) -> dict[str, Any]:
    """Return the decision-engine recommendation for one company.

    Args:
        company: Company name, case-insensitive.

    Returns:
        dict[str, Any]: JSON-ready decision payload with drivers and rationale.

    Raises:
        CompanyNotFoundError: If the company is not in the sample universe.
    """
    canonical_company = _resolve_company(company)
    signals = _build_signals(canonical_company)
    return map_signals_to_decision(canonical_company, signals).to_dict()


def run_pipeline(mode: str) -> dict[str, Any]:
    """Run existing sample-data pipelines and return written artifact paths.

    Args:
        mode: Pipeline mode: ``all``, ``financial``, or ``esg``.

    Returns:
        dict[str, Any]: Status, selected mode, and generated artifact paths.

    Raises:
        InvalidPipelineModeError: If ``mode`` is not supported.

    Notes:
        This preserves the original CLI-style artifact workflow while exposing
        it through the API as a controlled local operation.
    """
    if mode not in {"all", "financial", "esg"}:
        raise InvalidPipelineModeError(
            "Invalid pipeline mode. Expected one of: all, financial, esg."
        )

    outputs: dict[str, Any] = {}
    if mode in {"all", "financial"}:
        financial_config = AnalysisConfig()
        financial_summary = run_analysis_pipeline(financial_config)
        outputs["financial"] = {
            "company": financial_summary.company_name,
            "summary_output": str(DEFAULT_SUMMARY_OUTPUT),
            "report_output": str(DEFAULT_REPORT_OUTPUT),
            "profitability_chart_output": str(DEFAULT_PROFITABILITY_CHART),
            "financial_position_chart_output": str(DEFAULT_FINANCIAL_POSITION_CHART),
        }

    if mode in {"all", "esg"}:
        esg_config = EsgAnalysisConfig()
        esg_summary = run_esg_analysis_pipeline(esg_config)
        outputs["esg"] = {
            "audience_name": esg_summary.audience_name,
            "summary_output": str(DEFAULT_ESG_SUMMARY_OUTPUT),
            "report_output": str(DEFAULT_ESG_REPORT_OUTPUT),
            "cleaned_data_output": str(DEFAULT_ESG_CLEANED_DATA_OUTPUT),
            "trend_chart_output": str(DEFAULT_ESG_TREND_CHART),
            "correlation_chart_output": str(DEFAULT_ESG_CORRELATION_CHART),
            "risk_chart_output": str(DEFAULT_ESG_RISK_CHART),
        }

    _financial_artifacts.cache_clear()
    _esg_artifacts.cache_clear()
    return {"status": "OK", "mode": mode, "outputs": outputs}


def _build_signals(company: str) -> list[RiskSignal]:
    """Build all financial and ESG signals available for a canonical company."""
    canonical_company = _resolve_company(company)
    signals: list[RiskSignal] = []
    if canonical_company.casefold() == DEFAULT_COMPANY_NAME.casefold():
        signals.extend(
            build_financial_risk_signals(
                canonical_company,
                _financial_artifacts().period_metrics,
            )
        )

    esg_rows = _frame_to_records(_esg_artifacts().cleaned_frame)
    signals.extend(build_esg_risk_signals(canonical_company, esg_rows))
    return signals


def _resolve_company(company: str) -> str:
    """Return the canonical company name or raise when it is not covered."""
    requested = company.casefold()
    for known_company in list_companies():
        if known_company.casefold() == requested:
            return known_company
    raise CompanyNotFoundError(f"Unknown company: {company}")


def _company_esg_frame(company: str, artifacts: EsgAnalysisArtifacts):
    """Return one company's cleaned ESG history sorted by year."""
    frame = artifacts.cleaned_frame
    company_frame = frame.loc[frame["company"].str.casefold() == company.casefold()].copy()
    if company_frame.empty:
        return None
    return company_frame.sort_values("year")


def _frame_to_records(frame) -> list[dict[str, Any]]:
    """Convert a pandas DataFrame into JSON-safe record dictionaries."""
    records = frame.to_dict(orient="records")
    return [_json_safe_record(record) for record in records]


def _json_safe_record(record: dict[str, Any]) -> dict[str, Any]:
    """Convert numpy scalars and NaN values into JSON-friendly values."""
    safe_record: dict[str, Any] = {}
    for key, value in record.items():
        if hasattr(value, "item"):
            value = value.item()
        if value != value:
            value = None
        safe_record[str(key)] = value
    return safe_record


@lru_cache(maxsize=1)
def _financial_artifacts() -> AnalysisArtifacts:
    """Load and cache financial artifacts from the bundled sample CSV."""
    return analyze_financial_statements(
        DEFAULT_INPUT_PATH,
        company_name=DEFAULT_COMPANY_NAME,
    )


@lru_cache(maxsize=1)
def _esg_artifacts() -> EsgAnalysisArtifacts:
    """Load and cache ESG artifacts from the bundled sample CSV."""
    return analyze_esg_dataset(
        DEFAULT_ESG_INPUT_PATH,
        audience_name=DEFAULT_ESG_AUDIENCE,
    )
