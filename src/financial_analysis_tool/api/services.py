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
from ..decision_audit import DEFAULT_DECISION_HISTORY_PATH, write_decision_audit_record
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
DECISION_HISTORY_PATH = DEFAULT_DECISION_HISTORY_PATH
SEVERITY_SORT_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
ALERT_LEVEL_BY_SEVERITY = {
    "HIGH": "CRITICAL",
    "MEDIUM": "WATCH",
    "LOW": "NORMAL",
}


class CompanyNotFoundError(ValueError):
    """Raised when the requested company is not present in the sample universe."""


class InvalidPipelineModeError(ValueError):
    """Raised when the pipeline run mode is not supported."""


def get_health() -> dict[str, str]:
    """Return service metadata for health checks.

    Returns:
        dict[str, str]: Service name, ``OK`` status, and semantic version.
    """
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

    Args:
        company: Company name, matched case-insensitively against the sample
            universe.

    Returns:
        dict[str, Any]: JSON-ready payload containing the canonical company
        name, optional financial summary/periods, ESG history, and latest ESG
        row when available.

    Raises:
        CompanyNotFoundError: If the company is not covered by either sample
        dataset.

    Notes:
        The financial sample contains a single named company, while the ESG
        sample contains multiple companies. Missing sections are returned as
        ``None`` or empty lists rather than internal pandas/dataclass objects.
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
    """Return severity counts and supporting risk signals for one company.

    Args:
        company: Company name, matched case-insensitively.

    Returns:
        dict[str, Any]: Canonical company name, highest severity, severity
        counts, total signal count, and full signal payloads.

    Raises:
        CompanyNotFoundError: If the company is not in the sample universe.
    """
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

    Side Effects:
        Appends the returned decision to ``logs/decision_history.jsonl``.
    """
    canonical_company = _resolve_company(company)
    signals = _build_signals(canonical_company)
    decision = map_signals_to_decision(canonical_company, signals).to_dict()
    write_decision_audit_record(decision, output_path=DECISION_HISTORY_PATH)
    return decision


def get_portfolio_ranking() -> dict[str, Any]:
    """Return all companies ranked by risk severity and signal count.

    Returns:
        dict[str, Any]: Portfolio ranking payload with one item per company.

    Notes:
        Ranking uses ``HIGH`` before ``MEDIUM`` before ``LOW``. Ties are sorted
        by signal count descending and then company name for deterministic API
        output. This endpoint does not write decision audit records because it
        is a monitoring view, not a single-company decision request.
    """
    items: list[dict[str, Any]] = []
    for company in list_companies():
        signals = _build_signals(company)
        decision = map_signals_to_decision(company, signals).to_dict()
        items.append(
            {
                "company": company,
                "decision": decision["decision"],
                "highest_severity": decision["highest_severity"],
                "signal_count": decision["signal_count"],
                "top_drivers": decision["key_drivers"],
                "alert_level": ALERT_LEVEL_BY_SEVERITY[decision["highest_severity"]],
            }
        )

    ranked_items = sorted(
        items,
        key=lambda item: (
            SEVERITY_SORT_ORDER[item["highest_severity"]],
            -item["signal_count"],
            item["company"],
        ),
    )
    for rank, item in enumerate(ranked_items, start=1):
        item["rank"] = rank

    return {"companies": ranked_items}


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
    """Build all financial and ESG signals available for a company.

    Args:
        company: Company name to resolve and evaluate.

    Returns:
        list[RiskSignal]: Combined financial and ESG signals. Financial signals
        are only present for the configured financial sample company.

    Raises:
        CompanyNotFoundError: If the company is not covered.
    """
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
    """Resolve a case-insensitive company lookup to its canonical name.

    Args:
        company: User-supplied company name.

    Returns:
        str: Canonical company name as stored in the sample universe.

    Raises:
        CompanyNotFoundError: If no matching company exists.
    """
    requested = company.casefold()
    for known_company in list_companies():
        if known_company.casefold() == requested:
            return known_company
    raise CompanyNotFoundError(f"Unknown company: {company}")


def _company_esg_frame(company: str, artifacts: EsgAnalysisArtifacts):
    """Return one company's cleaned ESG history sorted by year.

    Args:
        company: Canonical company name.
        artifacts: In-memory ESG artifacts containing the cleaned DataFrame.

    Returns:
        pd.DataFrame | None: Company ESG history sorted by year, or ``None``
        when ESG data is not available for the company.
    """
    frame = artifacts.cleaned_frame
    company_frame = frame.loc[frame["company"].str.casefold() == company.casefold()].copy()
    if company_frame.empty:
        return None
    return company_frame.sort_values("year")


def _frame_to_records(frame) -> list[dict[str, Any]]:
    """Convert a pandas DataFrame into JSON-safe record dictionaries.

    Args:
        frame: pandas DataFrame to serialize.

    Returns:
        list[dict[str, Any]]: Row dictionaries with scalar values normalized for
        JSON serialization.
    """
    records = frame.to_dict(orient="records")
    return [_json_safe_record(record) for record in records]


def _json_safe_record(record: dict[str, Any]) -> dict[str, Any]:
    """Convert numpy scalars and NaN values into JSON-compatible values.

    Args:
        record: Row dictionary produced from pandas.

    Returns:
        dict[str, Any]: Row dictionary where numpy scalars are converted to
        Python values and NaN values are converted to ``None``.
    """
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
    """Load and cache financial artifacts from the bundled sample CSV.

    Returns:
        AnalysisArtifacts: In-memory financial records, period metrics, and
        summary reused across API requests.
    """
    return analyze_financial_statements(
        DEFAULT_INPUT_PATH,
        company_name=DEFAULT_COMPANY_NAME,
    )


@lru_cache(maxsize=1)
def _esg_artifacts() -> EsgAnalysisArtifacts:
    """Load and cache ESG artifacts from the bundled sample CSV.

    Returns:
        EsgAnalysisArtifacts: Cleaned ESG frame, helper frames, and summary
        reused across API requests.
    """
    return analyze_esg_dataset(
        DEFAULT_ESG_INPUT_PATH,
        audience_name=DEFAULT_ESG_AUDIENCE,
    )
