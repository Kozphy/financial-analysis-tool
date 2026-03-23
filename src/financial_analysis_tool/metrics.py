from __future__ import annotations

from .models import FinancialRecord, PeriodAnalysis, PerformanceSummary


def analyze_records(records: list[FinancialRecord]) -> list[PeriodAnalysis]:
    if not records:
        raise ValueError("At least one financial record is required for analysis.")

    analyses: list[PeriodAnalysis] = []
    previous_revenue: float | None = None

    for record in records:
        gross_profit = record.revenue - record.cost_of_revenue
        operating_income = gross_profit - record.operating_expenses

        analyses.append(
            PeriodAnalysis(
                period=record.period,
                revenue=record.revenue,
                gross_profit=gross_profit,
                operating_income=operating_income,
                net_income=record.net_income,
                revenue_growth=_calculate_growth(previous_revenue, record.revenue),
                gross_margin=_safe_ratio(gross_profit, record.revenue),
                operating_margin=_safe_ratio(operating_income, record.revenue),
                net_margin=_safe_ratio(record.net_income, record.revenue),
            )
        )
        previous_revenue = record.revenue

    return analyses


def summarize_company_performance(
    analyses: list[PeriodAnalysis],
) -> PerformanceSummary:
    if not analyses:
        raise ValueError("At least one analyzed period is required for summarization.")

    first_period = analyses[0]
    latest_period = analyses[-1]
    growth_periods = [period for period in analyses if period.revenue_growth is not None]

    overall_growth = _calculate_growth(first_period.revenue, latest_period.revenue)
    average_growth = (
        sum(
            period.revenue_growth
            for period in growth_periods
            if period.revenue_growth is not None
        )
        / len(growth_periods)
        if growth_periods
        else None
    )

    return PerformanceSummary(
        periods=analyses,
        latest_period=latest_period,
        overall_revenue_growth=overall_growth,
        average_revenue_growth=average_growth,
        best_growth_period=(
            max(growth_periods, key=lambda period: period.revenue_growth or float("-inf"))
            if growth_periods
            else None
        ),
        highest_net_margin_period=max(analyses, key=lambda period: period.net_margin),
    )


def _calculate_growth(previous_value: float | None, current_value: float) -> float | None:
    if previous_value in (None, 0):
        return None
    return (current_value - previous_value) / previous_value


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
