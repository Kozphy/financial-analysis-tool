"""Console, Markdown, and JSON reporting helpers for analysis output."""

from __future__ import annotations

import json
from pathlib import Path

from .models import AnalysisSummary


def build_console_summary(summary: AnalysisSummary) -> str:
    """Build a concise text summary for terminal output."""
    latest = summary.latest_period
    lines = [
        "Financial Analysis Summary",
        "==========================",
        f"Company: {summary.company_name}",
        f"Periods analyzed: {len(summary.periods)}",
        f"Latest period: {latest.period}",
        f"Revenue growth since first period: {_format_percent(summary.overall_revenue_growth)}",
        f"Latest gross margin: {_format_percent(latest.gross_margin)}",
        f"Latest operating margin: {_format_percent(latest.operating_margin)}",
        f"Latest net margin: {_format_percent(latest.net_margin)}",
        f"Latest current ratio: {_format_ratio(latest.current_ratio)}",
        f"Latest debt ratio: {_format_percent(latest.debt_ratio)}",
    ]
    return "\n".join(lines)


def build_markdown_report(summary: AnalysisSummary) -> str:
    """Build an executive-summary style Markdown report for portfolio presentation."""
    latest = summary.latest_period
    best_growth_period = summary.best_growth_period.period if summary.best_growth_period else "n/a"
    strongest_liquidity_period = (
        summary.strongest_liquidity_period.period if summary.strongest_liquidity_period else "n/a"
    )
    lowest_debt_period = summary.lowest_debt_period.period if summary.lowest_debt_period else "n/a"

    lines = [
        f"# {summary.company_name} Financial Analysis",
        "",
        "## Executive Summary",
        "",
        f"- Revenue increased {_format_percent(summary.overall_revenue_growth)} from the first period to {latest.period}.",
        f"- Profitability in {latest.period} remained solid, with gross margin at {_format_percent(latest.gross_margin)}, operating margin at {_format_percent(latest.operating_margin)}, and net margin at {_format_percent(latest.net_margin)}.",
        f"- Liquidity and leverage remained controlled, with a current ratio of {_format_ratio(latest.current_ratio)} and a debt ratio of {_format_percent(latest.debt_ratio)} in the latest period.",
        "",
        "## Highlights",
        "",
        f"- Best revenue growth period: `{best_growth_period}`",
        f"- Strongest liquidity period: `{strongest_liquidity_period}`",
        f"- Lowest debt ratio period: `{lowest_debt_period}`",
        "",
        "## Period Metrics",
        "",
        "| Period | Revenue | Rev Growth | Gross Margin | Operating Margin | Net Margin | Current Ratio | Debt Ratio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for period in summary.periods:
        lines.append(
            "| "
            f"{period.period} | "
            f"{_format_currency(period.revenue)} | "
            f"{_format_percent(period.revenue_growth)} | "
            f"{_format_percent(period.gross_margin)} | "
            f"{_format_percent(period.operating_margin)} | "
            f"{_format_percent(period.net_margin)} | "
            f"{_format_ratio(period.current_ratio)} | "
            f"{_format_percent(period.debt_ratio)} |"
        )

    return "\n".join(lines)


def write_summary_json(summary: AnalysisSummary, output_path: str | Path) -> None:
    """Write the structured analysis summary to a JSON file."""
    path = _ensure_parent_directory(output_path)
    path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")


def write_markdown_report(summary: AnalysisSummary, output_path: str | Path) -> None:
    """Write the executive summary report to a Markdown file."""
    path = _ensure_parent_directory(output_path)
    path.write_text(build_markdown_report(summary), encoding="utf-8")


def _ensure_parent_directory(path: str | Path) -> Path:
    """Create the parent directory for an output file when needed."""
    resolved_path = Path(path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def _format_currency(value: float) -> str:
    """Format a raw numeric amount as whole-dollar currency text."""
    return f"${value:,.0f}"


def _format_percent(value: float | None) -> str:
    """Format a decimal ratio as a percentage string."""
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _format_ratio(value: float | None) -> str:
    """Format a ratio value as an x-multiple string."""
    if value is None:
        return "n/a"
    return f"{value:.2f}x"
