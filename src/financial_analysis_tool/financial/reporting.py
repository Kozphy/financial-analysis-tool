from __future__ import annotations

from financial_analysis_tool.core.io import write_json
from financial_analysis_tool.core.utils import format_currency, format_percent

from .models import PerformanceSummary


def build_console_report(summary: PerformanceSummary) -> str:
    lines = [
        "Financial Performance Summary",
        "=============================",
        f"Periods analyzed: {len(summary.periods)}",
        f"Latest period: {summary.latest_period.period}",
        f"Latest revenue: {format_currency(summary.latest_period.revenue)}",
        f"Latest gross margin: {format_percent(summary.latest_period.gross_margin)}",
        f"Latest operating margin: {format_percent(summary.latest_period.operating_margin)}",
        f"Latest net margin: {format_percent(summary.latest_period.net_margin)}",
        f"Overall revenue growth: {format_percent(summary.overall_revenue_growth)}",
        f"Average period revenue growth: {format_percent(summary.average_revenue_growth)}",
        _format_optional_period("Best revenue growth period", summary.best_growth_period),
        _format_optional_period(
            "Highest net margin period", summary.highest_net_margin_period, use_margin=True
        ),
        "",
        "Per-Period Metrics",
        "------------------",
        f"{'Period':<10} {'Revenue':>14} {'Growth':>10} {'Gross Mgn':>12} {'Op Mgn':>10} {'Net Mgn':>10}",
    ]

    for period in summary.periods:
        lines.append(
            f"{period.period:<10} "
            f"{format_currency(period.revenue, compact=True):>14} "
            f"{format_percent(period.revenue_growth, short=True):>10} "
            f"{format_percent(period.gross_margin, short=True):>12} "
            f"{format_percent(period.operating_margin, short=True):>10} "
            f"{format_percent(period.net_margin, short=True):>10}"
        )

    return "\n".join(lines)


def write_summary_json(summary: PerformanceSummary, output_path: str) -> None:
    write_json(summary.to_dict(), output_path)


def _format_optional_period(label: str, period, *, use_margin: bool = False) -> str:
    if period is None:
        return f"{label}: n/a"

    metric = period.net_margin if use_margin else period.revenue_growth
    return f"{label}: {period.period} ({format_percent(metric)})"
