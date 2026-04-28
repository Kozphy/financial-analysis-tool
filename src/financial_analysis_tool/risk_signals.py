"""Explainable risk signal generation for financial and ESG analysis outputs.

The functions in this module are pure business logic: they receive calculated
financial metrics or cleaned ESG rows and return deterministic, user-facing
signals. Keeping these rules outside FastAPI makes them easy to test and easy
to explain in interviews.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Literal

from .models import PeriodMetrics


Severity = Literal["LOW", "MEDIUM", "HIGH"]


@dataclass(frozen=True, slots=True)
class RiskSignal:
    """Explainable monitoring signal for a company and reporting period.

    Attributes:
        company: Company the signal applies to.
        year: ESG year or financial period label.
        signal_type: Stable machine-readable signal name.
        severity: Business severity used by risk profiles and decisions.
        reason: Human-readable explanation of why the rule fired.
        metric_value: Numeric value that triggered or contextualized the signal.
        recommendation: Suggested analyst or portfolio-monitoring action.
    """

    company: str
    year: int | str
    signal_type: str
    severity: Severity
    reason: str
    metric_value: float
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the signal to a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: Plain dictionary payload for API and report layers.
        """
        return asdict(self)


def build_financial_risk_signals(
    company: str,
    period_metrics: list[PeriodMetrics],
) -> list[RiskSignal]:
    """Build explainable financial risk signals from period metrics.

    Args:
        company: Company name attached to emitted signals.
        period_metrics: Chronologically sorted financial metrics. The latest
            period is evaluated, and the prior period is used for margin-change
            comparison when available.

    Returns:
        list[RiskSignal]: Financial monitoring signals. Returns an empty list
        when no metrics are provided or no thresholds are breached.

    Notes:
        Rules are intentionally transparent: revenue decline and margin pressure
        indicate financial deterioration, debt ratio captures leverage risk, and
        current ratio captures liquidity stress.
    """
    if not period_metrics:
        return []

    signals: list[RiskSignal] = []
    latest = period_metrics[-1]
    previous = period_metrics[-2] if len(period_metrics) > 1 else None

    if latest.revenue_growth is not None and latest.revenue_growth < 0:
        severity: Severity = "HIGH" if latest.revenue_growth <= -0.10 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest.period,
                signal_type="FINANCIAL_DETERIORATION",
                severity=severity,
                reason="Latest period revenue declined versus the prior period.",
                metric_value=round(latest.revenue_growth, 4),
                recommendation="Review revenue drivers and validate whether the decline is temporary or structural.",
            )
        )

    if previous and latest.net_margin is not None and previous.net_margin is not None:
        margin_change = latest.net_margin - previous.net_margin
        if margin_change <= -0.03:
            severity = "HIGH" if margin_change <= -0.07 else "MEDIUM"
            signals.append(
                RiskSignal(
                    company=company,
                    year=latest.period,
                    signal_type="FINANCIAL_DETERIORATION",
                    severity=severity,
                    reason="Latest net margin weakened materially versus the prior period.",
                    metric_value=round(margin_change, 4),
                    recommendation="Investigate cost pressure, pricing power, and operating expense discipline.",
                )
            )

    if latest.debt_ratio is not None and latest.debt_ratio >= 0.50:
        severity = "HIGH" if latest.debt_ratio >= 0.65 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest.period,
                signal_type="HIGH_LEVERAGE",
                severity=severity,
                reason="Latest debt ratio is above the portfolio monitoring threshold.",
                metric_value=round(latest.debt_ratio, 4),
                recommendation="Review refinancing risk, covenant headroom, and debt reduction plans.",
            )
        )

    if latest.current_ratio is not None and latest.current_ratio < 1.50:
        severity = "HIGH" if latest.current_ratio < 1.00 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest.period,
                signal_type="LIQUIDITY_STRESS",
                severity=severity,
                reason="Latest current ratio is below the liquidity monitoring threshold.",
                metric_value=round(latest.current_ratio, 4),
                recommendation="Assess working capital needs, short-term liabilities, and available liquidity.",
            )
        )

    return signals


def build_esg_risk_signals(
    company: str,
    rows: Iterable[dict[str, Any]],
) -> list[RiskSignal]:
    """Build explainable ESG and transition-risk signals for one company.

    Args:
        company: Company name to evaluate, matched case-insensitively.
        rows: Cleaned ESG records containing company-year observations and
            derived fields such as ``carbon_intensity`` and ``esg_score_change``.

    Returns:
        list[RiskSignal]: ESG and transition monitoring signals for the latest
        company year. Returns an empty list when the company is absent.

    Notes:
        Carbon intensity is assessed relative to the latest-year sample
        universe. Governance, controversy, renewable energy, and green capex
        use fixed thresholds for deterministic behavior. ``ESG_IMPROVEMENT`` is
        a positive monitoring signal, not a risk breach.
    """
    normalized_rows = [_normalize_row(row) for row in rows]
    company_rows = [
        row for row in normalized_rows if row.get("company", "").casefold() == company.casefold()
    ]
    if not company_rows:
        return []

    company_rows = sorted(company_rows, key=lambda row: int(row["year"]))
    latest = company_rows[-1]
    latest_year = int(latest["year"])
    latest_year_rows = [row for row in normalized_rows if int(row["year"]) == latest_year]
    carbon_values = [float(row["carbon_intensity"]) for row in latest_year_rows]
    carbon_watch_threshold = _percentile(carbon_values, 0.75)
    signals: list[RiskSignal] = []

    carbon_intensity = float(latest["carbon_intensity"])
    if carbon_intensity >= carbon_watch_threshold:
        severity: Severity = "HIGH" if carbon_intensity >= carbon_watch_threshold * 1.20 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest_year,
                signal_type="HIGH_CARBON_INTENSITY",
                severity=severity,
                reason=(
                    "Latest carbon intensity is above the latest-year portfolio watchlist threshold "
                    f"of {carbon_watch_threshold:.2f}."
                ),
                metric_value=round(carbon_intensity, 4),
                recommendation="Prioritize transition-plan review and compare emissions intensity against sector peers.",
            )
        )

    governance_score = float(latest["governance_score"])
    if governance_score < 65:
        severity = "HIGH" if governance_score < 55 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest_year,
                signal_type="WEAK_GOVERNANCE",
                severity=severity,
                reason="Latest governance score is below the governance quality threshold.",
                metric_value=round(governance_score, 4),
                recommendation="Request governance remediation plan and monitor board oversight indicators.",
            )
        )

    controversy_count = float(latest["controversy_count"])
    if controversy_count >= 1:
        severity = "HIGH" if controversy_count >= 3 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest_year,
                signal_type="ELEVATED_CONTROVERSY_RISK",
                severity=severity,
                reason="Latest controversy count indicates unresolved reputational or conduct risk.",
                metric_value=round(controversy_count, 4),
                recommendation="Escalate for controversy review and document management response.",
            )
        )

    renewable_energy_pct = float(latest["renewable_energy_pct"])
    green_capex_pct = float(latest["green_capex_pct"])
    if carbon_intensity >= carbon_watch_threshold and (renewable_energy_pct < 30 or green_capex_pct < 10):
        severity = "HIGH" if renewable_energy_pct < 20 or green_capex_pct < 6 else "MEDIUM"
        signals.append(
            RiskSignal(
                company=company,
                year=latest_year,
                signal_type="TRANSITION_RISK_WATCHLIST",
                severity=severity,
                reason=(
                    "Company combines elevated carbon intensity with limited renewable energy "
                    "or green capex indicators."
                ),
                metric_value=round(min(renewable_energy_pct, green_capex_pct), 4),
                recommendation="Engage management on transition investment plans and interim decarbonization milestones.",
            )
        )

    esg_score_change = latest.get("esg_score_change")
    if esg_score_change is not None and float(esg_score_change) > 0:
        signals.append(
            RiskSignal(
                company=company,
                year=latest_year,
                signal_type="ESG_IMPROVEMENT",
                severity="LOW",
                reason="Latest ESG score improved versus the prior year.",
                metric_value=round(float(esg_score_change), 4),
                recommendation="Maintain monitoring and use the improvement trend as context for engagement priorities.",
            )
        )

    return signals


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert pandas and numpy scalar values into plain Python values.

    Args:
        row: Record dictionary that may contain pandas or numpy scalar objects.

    Returns:
        dict[str, Any]: Normalized row suitable for deterministic comparisons.
    """
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if hasattr(value, "item"):
            value = value.item()
        normalized[str(key)] = value
    return normalized


def _percentile(values: list[float], percentile: float) -> float:
    """Calculate a deterministic nearest-rank percentile without numpy.

    Args:
        values: Numeric values to rank.
        percentile: Percentile in the inclusive range ``0.0`` to ``1.0``.

    Returns:
        float: Nearest ranked value, or ``0.0`` when no values are provided.

    Notes:
        The implementation avoids numpy so signal generation remains pure Python
        and easy to unit test.
    """
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * percentile))))
    return sorted_values[index]
