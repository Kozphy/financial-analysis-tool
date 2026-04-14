"""Metric calculations for profitability, liquidity, and leverage analysis."""

from __future__ import annotations

from .models import AnalysisSummary, FinancialStatementRecord, PeriodMetrics


def calculate_period_metrics(records: list[FinancialStatementRecord]) -> list[PeriodMetrics]:
    """Calculate per-period financial metrics from validated statement records."""
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
    """Build the headline summary used by reports and portfolio outputs."""
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
    """Safely calculate a ratio and return None when the denominator is zero."""
    if denominator == 0:
        return None
    return numerator / denominator


def _growth(previous_value: float | None, current_value: float) -> float | None:
    """Calculate period-over-period growth relative to the prior value."""
    if previous_value in (None, 0):
        return None
    return (current_value - previous_value) / previous_value


def _average(values: list[float | None]) -> float | None:
    """Calculate the average across non-null metric values."""
    filtered_values = [value for value in values if value is not None]
    if not filtered_values:
        return None
    return sum(filtered_values) / len(filtered_values)
