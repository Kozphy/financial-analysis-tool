from __future__ import annotations

from financial_analysis_tool.core.io import write_json
from financial_analysis_tool.core.utils import format_percent, format_ratio

from .models import BacktestResult


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
        f"{', '.join(position.ticker for position in latest_period.positions)}",
        "",
        "Rebalance Timeline",
        "------------------",
        f"{'Date':<12} {'Next':<12} {'Selected':<18} {'Strategy':>10} {'Benchmark':>10} {'Equity':>10}",
    ]

    for period in result.periods:
        selected_tickers = ",".join(position.ticker for position in period.positions)
        lines.append(
            f"{period.rebalance_date.isoformat():<12} "
            f"{period.next_date.isoformat():<12} "
            f"{selected_tickers:<18} "
            f"{format_percent(period.strategy_return, short=True):>10} "
            f"{format_percent(period.benchmark_return, short=True):>10} "
            f"{period.strategy_equity:>10.3f}"
        )

    return "\n".join(lines)


def write_backtest_json(result: BacktestResult, output_path: str) -> None:
    write_json(result.to_dict(), output_path)
