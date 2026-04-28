"""Metric calculations for profitability, liquidity, and leverage analysis.

This module is the financial feature layer for the project. It converts
validated statement records into period-level ratios and headline summary
metrics that feed reporting, visualization, the dashboard, and API risk
signals.
"""

from __future__ import annotations

from .models import AnalysisSummary, FinancialStatementRecord, PeriodMetrics


def calculate_period_metrics(records: list[FinancialStatementRecord]) -> list[PeriodMetrics]:
    """Calculate per-period profitability, liquidity, and leverage metrics.

    Args:
        records: Chronologically sorted financial statement records.

    Returns:
        list[PeriodMetrics]: Derived metrics for each reporting period.

    Raises:
        ValueError: If no financial statement records are provided.

    Notes:
        Revenue growth is calculated against the prior period. Margin, current
        ratio, and debt ratio values are returned as decimal ratios.
    """
    if not records:
        raise ValueError("At least one financial statement record is required.")

    metrics: list[PeriodMetrics] = []
    previous_revenue: float | None = None

    for record in records:
        gross_profit = record.revenue - record.cost_of_revenue
        operating_income = gross_profit - record.operating_expenses

        metrics.append(
            PeriodMetrics(
                period=record.period,
                revenue=record.revenue,
                gross_profit=gross_profit,
                operating_income=operating_income,
                net_income=record.net_income,
                revenue_growth=_growth(previous_revenue, record.revenue),
                gross_margin=_ratio(gross_profit, record.revenue),
                operating_margin=_ratio(operating_income, record.revenue),
                net_margin=_ratio(record.net_income, record.revenue),
                current_ratio=_ratio(record.current_assets, record.current_liabilities),
                debt_ratio=_ratio(record.total_liabilities, record.total_assets),
                current_assets=record.current_assets,
                current_liabilities=record.current_liabilities,
                total_assets=record.total_assets,
                total_liabilities=record.total_liabilities,
            )
        )
        previous_revenue = record.revenue

    return metrics


def build_analysis_summary(period_metrics: list[PeriodMetrics], *, company_name: str) -> AnalysisSummary:
    """Build headline financial indicators used by reports and API responses.

    Args:
        period_metrics: Calculated metrics for each reporting period.
        company_name: Company label attached to downstream outputs.

    Returns:
        AnalysisSummary: Aggregated summary including latest-period metrics,
        overall growth, average margins, and best/worst monitoring periods.

    Raises:
        ValueError: If no period metrics are provided.
    """
    if not period_metrics:
        raise ValueError("At least one calculated period metric is required.")

    latest_period = period_metrics[-1]
    growth_periods = [period for period in period_metrics if period.revenue_growth is not None]
    liquidity_periods = [period for period in period_metrics if period.current_ratio is not None]
    debt_periods = [period for period in period_metrics if period.debt_ratio is not None]

    return AnalysisSummary(
        company_name=company_name,
        periods=period_metrics,
        latest_period=latest_period,
        overall_revenue_growth=_growth(period_metrics[0].revenue, latest_period.revenue),
        average_gross_margin=_average([period.gross_margin for period in period_metrics]),
        average_operating_margin=_average([period.operating_margin for period in period_metrics]),
        average_net_margin=_average([period.net_margin for period in period_metrics]),
        latest_current_ratio=latest_period.current_ratio,
        latest_debt_ratio=latest_period.debt_ratio,
        best_growth_period=(
            max(growth_periods, key=lambda period: period.revenue_growth or float("-inf"))
            if growth_periods
            else None
        ),
        strongest_liquidity_period=(
            max(liquidity_periods, key=lambda period: period.current_ratio or float("-inf"))
            if liquidity_periods
            else None
        ),
        lowest_debt_period=(
            min(debt_periods, key=lambda period: period.debt_ratio or float("inf"))
            if debt_periods
            else None
        ),
    )


def _ratio(numerator: float, denominator: float) -> float | None:
    """Safely calculate a ratio.

    Args:
        numerator: Top value in the ratio.
        denominator: Bottom value in the ratio.

    Returns:
        float | None: Ratio value, or ``None`` when the denominator is zero.
    """
    if denominator == 0:
        return None
    return numerator / denominator


def _growth(previous_value: float | None, current_value: float) -> float | None:
    """Calculate period-over-period growth.

    Args:
        previous_value: Prior period value used as the baseline.
        current_value: Current period value.

    Returns:
        float | None: Growth as a decimal ratio, or ``None`` when a baseline
        is unavailable or zero.
    """
    if previous_value in (None, 0):
        return None
    return (current_value - previous_value) / previous_value


def _average(values: list[float | None]) -> float | None:
    """Calculate an average while ignoring missing metric values.

    Args:
        values: Optional numeric values to aggregate.

    Returns:
        float | None: Average of available values, or ``None`` when every value
        is missing.
    """
    filtered_values = [value for value in values if value is not None]
    if not filtered_values:
        return None
    return sum(filtered_values) / len(filtered_values)
