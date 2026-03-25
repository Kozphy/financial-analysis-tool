from __future__ import annotations

from datetime import date
from statistics import fmean

from financial_analysis_tool.core.exceptions import DataAlignmentError, InputDataError
from financial_analysis_tool.core.utils import (
    annualize_return,
    annualize_volatility,
    max_drawdown,
    sharpe_ratio,
)

from .factors import compute_factor_snapshots
from .models import BacktestPeriod, BacktestResult, PriceRecord
from .portfolio import build_equal_weight_portfolio
from .strategy import rank_assets


VALID_REBALANCE_FREQUENCIES = {"daily", "weekly", "monthly", "quarterly"}
VALID_BENCHMARK_ALIGNMENT = {"strict", "intersect"}


def run_backtest(
    price_records: list[PriceRecord],
    *,
    momentum_lookback_days: int = 90,
    volatility_lookback_days: int = 90,
    rebalance_frequency: str = "monthly",
    top_n: int = 2,
    periods_per_year: int = 12,
    benchmark_ticker: str | None = None,
    benchmark_alignment: str = "strict",
    momentum_weight: float = 0.8,
    volatility_weight: float = 0.2,
) -> BacktestResult:
    if top_n <= 0:
        raise InputDataError("top_n must be greater than 0.")
    if periods_per_year <= 0:
        raise InputDataError("periods_per_year must be greater than 0.")
    if rebalance_frequency not in VALID_REBALANCE_FREQUENCIES:
        raise InputDataError(
            f"rebalance_frequency must be one of: {', '.join(sorted(VALID_REBALANCE_FREQUENCIES))}."
        )
    if benchmark_alignment not in VALID_BENCHMARK_ALIGNMENT:
        raise InputDataError(
            f"benchmark_alignment must be one of: {', '.join(sorted(VALID_BENCHMARK_ALIGNMENT))}."
        )

    benchmark_symbol = benchmark_ticker.strip().upper() if benchmark_ticker else None
    snapshots_by_date = compute_factor_snapshots(
        price_records,
        momentum_lookback_days=momentum_lookback_days,
        volatility_lookback_days=volatility_lookback_days,
    )
    if not snapshots_by_date:
        raise InputDataError("Not enough price history is available to run the backtest.")

    rebalance_dates = _select_rebalance_dates(
        sorted(snapshots_by_date),
        frequency=rebalance_frequency,
    )
    benchmark_dates = {
        record.date
        for record in price_records
        if benchmark_symbol and record.ticker == benchmark_symbol
    }
    if benchmark_symbol:
        rebalance_dates = _align_rebalance_dates(
            rebalance_dates,
            benchmark_dates=benchmark_dates,
            benchmark_symbol=benchmark_symbol,
            benchmark_alignment=benchmark_alignment,
        )

    if len(rebalance_dates) < 2:
        raise InputDataError(
            "At least two rebalance dates are required after applying the selected rebalance frequency."
        )

    close_lookup = {
        (record.ticker, record.date): record.close
        for record in price_records
    }
    periods: list[BacktestPeriod] = []
    strategy_equity = 1.0
    benchmark_equity = 1.0

    for rebalance_date, next_date in zip(rebalance_dates, rebalance_dates[1:]):
        universe = snapshots_by_date[rebalance_date]
        eligible_snapshots = [
            snapshot
            for snapshot in universe
            if (snapshot.ticker, next_date) in close_lookup
        ]
        if not eligible_snapshots:
            continue

        ranked_assets = rank_assets(
            eligible_snapshots,
            momentum_weight=momentum_weight,
            volatility_weight=volatility_weight,
        )
        exit_prices = {
            asset.ticker: close_lookup[(asset.ticker, next_date)]
            for asset in ranked_assets
            if (asset.ticker, next_date) in close_lookup
        }
        positions = build_equal_weight_portfolio(
            ranked_assets,
            top_n,
            exit_date=next_date,
            exit_prices=exit_prices,
        )
        strategy_return = sum(position.weight * position.forward_return for position in positions)

        if benchmark_symbol:
            benchmark_entry_close = close_lookup[(benchmark_symbol, rebalance_date)]
            benchmark_exit_close = close_lookup[(benchmark_symbol, next_date)]
            benchmark_return = _calculate_return(benchmark_entry_close, benchmark_exit_close)
        else:
            benchmark_return = fmean(
                _calculate_return(snapshot.close, close_lookup[(snapshot.ticker, next_date)])
                for snapshot in eligible_snapshots
            )

        strategy_equity *= 1 + strategy_return
        benchmark_equity *= 1 + benchmark_return

        periods.append(
            BacktestPeriod(
                rebalance_date=rebalance_date,
                next_date=next_date,
                positions=positions,
                universe_size=len(eligible_snapshots),
                strategy_return=strategy_return,
                benchmark_return=benchmark_return,
                strategy_equity=strategy_equity,
                benchmark_equity=benchmark_equity,
            )
        )

    if not periods:
        raise InputDataError(
            "The backtest produced no rebalance periods. Check the price history and benchmark selection."
        )

    strategy_returns = [period.strategy_return for period in periods]
    benchmark_returns = [period.benchmark_return for period in periods]
    start_date = periods[0].rebalance_date
    end_date = periods[-1].next_date

    return BacktestResult(
        periods=periods,
        benchmark_label=benchmark_symbol or "Equal-Weight Universe",
        momentum_lookback_days=momentum_lookback_days,
        volatility_lookback_days=volatility_lookback_days,
        rebalance_frequency=rebalance_frequency,
        benchmark_alignment=benchmark_alignment,
        top_n=top_n,
        periods_per_year=periods_per_year,
        total_return=periods[-1].strategy_equity - 1,
        benchmark_total_return=periods[-1].benchmark_equity - 1,
        annualized_return=_annualize_equity_over_days(
            periods[-1].strategy_equity,
            start_date,
            end_date,
        ),
        benchmark_annualized_return=_annualize_equity_over_days(
            periods[-1].benchmark_equity,
            start_date,
            end_date,
        ),
        annualized_volatility=annualize_volatility(strategy_returns, periods_per_year),
        benchmark_annualized_volatility=annualize_volatility(
            benchmark_returns,
            periods_per_year,
        ),
        sharpe_ratio=sharpe_ratio(strategy_returns, periods_per_year),
        benchmark_sharpe_ratio=sharpe_ratio(benchmark_returns, periods_per_year),
        max_drawdown=max_drawdown([period.strategy_equity for period in periods]),
        benchmark_max_drawdown=max_drawdown(
            [period.benchmark_equity for period in periods]
        ),
        positive_period_rate=sum(1 for value in strategy_returns if value > 0) / len(strategy_returns),
        outperformance_rate=sum(
            1
            for strategy_return, benchmark_return in zip(strategy_returns, benchmark_returns)
            if strategy_return > benchmark_return
        )
        / len(periods),
    )


def _align_rebalance_dates(
    rebalance_dates: list[date],
    *,
    benchmark_dates: set[date],
    benchmark_symbol: str,
    benchmark_alignment: str,
) -> list[date]:
    if benchmark_alignment == "strict":
        for rebalance_date in rebalance_dates:
            if rebalance_date not in benchmark_dates:
                raise DataAlignmentError(
                    f"Benchmark '{benchmark_symbol}' is missing price data for {rebalance_date.isoformat()}."
                )
        return rebalance_dates

    return [
        rebalance_date
        for rebalance_date in rebalance_dates
        if rebalance_date in benchmark_dates
    ]


def _select_rebalance_dates(
    candidate_dates: list,
    *,
    frequency: str,
) -> list:
    grouped_dates: dict[tuple[int, int], list] = {}
    if frequency == "daily":
        return list(candidate_dates)

    for candidate_date in candidate_dates:
        key = _rebalance_group_key(candidate_date, frequency=frequency)
        grouped_dates.setdefault(key, []).append(candidate_date)

    return [max(group) for _, group in sorted(grouped_dates.items())]


def _rebalance_group_key(candidate_date, *, frequency: str) -> tuple[int, int]:
    if frequency == "weekly":
        iso_year, iso_week, _ = candidate_date.isocalendar()
        return iso_year, iso_week
    if frequency == "monthly":
        return candidate_date.year, candidate_date.month
    if frequency == "quarterly":
        return candidate_date.year, ((candidate_date.month - 1) // 3) + 1
    raise InputDataError(f"Unsupported rebalance frequency: {frequency}")


def _calculate_return(start_value: float, end_value: float) -> float:
    if start_value == 0:
        raise InputDataError("Price data contains a zero close value, which breaks return calculation.")
    return (end_value - start_value) / start_value


def _annualize_equity_over_days(
    equity: float,
    start_date: date,
    end_date: date,
) -> float | None:
    elapsed_days = (end_date - start_date).days
    if elapsed_days <= 0:
        return None
    return annualize_return(equity, elapsed_days, 365)
