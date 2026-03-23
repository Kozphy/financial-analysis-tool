from __future__ import annotations

import json
from pathlib import Path

from .models import BacktestResult, PerformanceSummary


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


def write_summary_json(summary: PerformanceSummary, output_path: str | Path) -> None:
    _write_json_payload(summary.to_dict(), output_path)


def build_backtest_report(result: BacktestResult) -> str:
    latest_period = result.periods[-1]
    lines = [
        "Quant Backtest Summary",
        "======================",
        f"Rebalance periods: {len(result.periods)}",
        f"Benchmark: {result.benchmark_label}",
        f"Lookback periods: {result.lookback_periods}",
        f"Volatility window: {result.volatility_window}",
        f"Top N holdings: {result.top_n}",
        f"Strategy total return: {format_percent(result.total_return)}",
        f"Benchmark total return: {format_percent(result.benchmark_total_return)}",
        f"Strategy annualized return: {format_percent(result.annualized_return)}",
        f"Benchmark annualized return: {format_percent(result.benchmark_annualized_return)}",
        f"Strategy annualized volatility: {format_percent(result.annualized_volatility)}",
        f"Benchmark annualized volatility: {format_percent(result.benchmark_annualized_volatility)}",
        f"Strategy Sharpe ratio: {format_ratio(result.sharpe_ratio)}",
        f"Benchmark Sharpe ratio: {format_ratio(result.benchmark_sharpe_ratio)}",
        f"Strategy max drawdown: {format_percent(result.max_drawdown)}",
        f"Benchmark max drawdown: {format_percent(result.benchmark_max_drawdown)}",
        f"Positive-period rate: {format_percent(result.positive_period_rate)}",
        f"Outperformance rate: {format_percent(result.outperformance_rate)}",
        f"Latest selection ({latest_period.rebalance_date.isoformat()}): "
        f"{', '.join(asset.ticker for asset in latest_period.selected_assets)}",
        "",
        "Rebalance Timeline",
        "------------------",
        f"{'Date':<12} {'Next':<12} {'Selected':<18} {'Strategy':>10} {'Benchmark':>10} {'Equity':>10}",
    ]

    for period in result.periods:
        selected_tickers = ",".join(asset.ticker for asset in period.selected_assets)
        lines.append(
            f"{period.rebalance_date.isoformat():<12} "
            f"{period.next_date.isoformat():<12} "
            f"{selected_tickers:<18} "
            f"{format_percent(period.strategy_return, short=True):>10} "
            f"{format_percent(period.benchmark_return, short=True):>10} "
            f"{period.strategy_equity:>10.3f}"
        )

    return "\n".join(lines)


def write_backtest_json(result: BacktestResult, output_path: str | Path) -> None:
    _write_json_payload(result.to_dict(), output_path)


def format_currency(value: float, *, compact: bool = False) -> str:
    if compact:
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def format_percent(value: float | None, *, short: bool = False) -> str:
    if value is None:
        return "n/a"
    precision = 1 if short else 2
    return f"{value * 100:.{precision}f}%"


def format_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _format_optional_period(label: str, period, *, use_margin: bool = False) -> str:
    if period is None:
        return f"{label}: n/a"

    metric = period.net_margin if use_margin else period.revenue_growth
    return f"{label}: {period.period} ({format_percent(metric)})"


def _write_json_payload(payload: dict[str, object], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
