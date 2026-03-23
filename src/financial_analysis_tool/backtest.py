from __future__ import annotations

from math import sqrt
from statistics import fmean, stdev

from .factors import compute_factor_snapshots
from .models import BacktestPeriod, BacktestResult, PriceRecord
from .strategy import rank_assets, select_top_ranked_assets


def run_backtest(
    price_records: list[PriceRecord],
    *,
    lookback_periods: int = 3,
    volatility_window: int = 3,
    top_n: int = 2,
    periods_per_year: int = 12,
    benchmark_ticker: str | None = None,
    momentum_weight: float = 0.8,
    volatility_weight: float = 0.2,
) -> BacktestResult:
    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be greater than 0.")

    benchmark_symbol = benchmark_ticker.strip().upper() if benchmark_ticker else None
    snapshots_by_date = compute_factor_snapshots(
        price_records,
        lookback_periods=lookback_periods,
        volatility_window=volatility_window,
    )
    if not snapshots_by_date:
        raise ValueError("Not enough price history is available to run the backtest.")

    periods: list[BacktestPeriod] = []
    strategy_equity = 1.0
    benchmark_equity = 1.0

    for rebalance_date in sorted(snapshots_by_date):
        universe = snapshots_by_date[rebalance_date]
        benchmark_snapshot = None
        if benchmark_symbol:
            benchmark_snapshot = next(
                (snapshot for snapshot in universe if snapshot.ticker == benchmark_symbol),
                None,
            )
            if benchmark_snapshot is None:
                continue

        ranked_assets = rank_assets(
            universe,
            momentum_weight=momentum_weight,
            volatility_weight=volatility_weight,
        )
        selected_assets = select_top_ranked_assets(ranked_assets, top_n)
        if not selected_assets:
            continue

        strategy_return = fmean(asset.forward_return for asset in selected_assets)
        benchmark_return = (
            benchmark_snapshot.forward_return
            if benchmark_snapshot
            else fmean(snapshot.forward_return for snapshot in universe)
        )

        strategy_equity *= 1 + strategy_return
        benchmark_equity *= 1 + benchmark_return

        next_dates = {asset.next_date for asset in selected_assets}
        if benchmark_snapshot:
            next_dates.add(benchmark_snapshot.next_date)

        periods.append(
            BacktestPeriod(
                rebalance_date=rebalance_date,
                next_date=max(next_dates),
                selected_assets=selected_assets,
                universe_size=len(universe),
                strategy_return=strategy_return,
                benchmark_return=benchmark_return,
                strategy_equity=strategy_equity,
                benchmark_equity=benchmark_equity,
            )
        )

    if not periods:
        raise ValueError(
            "The backtest produced no rebalance periods. Check the price history and benchmark selection."
        )

    strategy_returns = [period.strategy_return for period in periods]
    benchmark_returns = [period.benchmark_return for period in periods]

    return BacktestResult(
        periods=periods,
        benchmark_label=benchmark_symbol or "Equal-Weight Universe",
        lookback_periods=lookback_periods,
        volatility_window=volatility_window,
        top_n=top_n,
        periods_per_year=periods_per_year,
        total_return=periods[-1].strategy_equity - 1,
        benchmark_total_return=periods[-1].benchmark_equity - 1,
        annualized_return=_annualize_return(periods[-1].strategy_equity, len(periods), periods_per_year),
        benchmark_annualized_return=_annualize_return(
            periods[-1].benchmark_equity,
            len(periods),
            periods_per_year,
        ),
        annualized_volatility=_annualize_volatility(strategy_returns, periods_per_year),
        benchmark_annualized_volatility=_annualize_volatility(
            benchmark_returns,
            periods_per_year,
        ),
        sharpe_ratio=_calculate_sharpe_ratio(strategy_returns, periods_per_year),
        benchmark_sharpe_ratio=_calculate_sharpe_ratio(
            benchmark_returns,
            periods_per_year,
        ),
        max_drawdown=_calculate_max_drawdown([period.strategy_equity for period in periods]),
        benchmark_max_drawdown=_calculate_max_drawdown(
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


def _annualize_return(equity: float, period_count: int, periods_per_year: int) -> float | None:
    if period_count <= 0:
        return None
    return equity ** (periods_per_year / period_count) - 1


def _annualize_volatility(returns: list[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None
    return stdev(returns) * sqrt(periods_per_year)


def _calculate_sharpe_ratio(returns: list[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None

    volatility = stdev(returns)
    if volatility == 0:
        return None

    return fmean(returns) / volatility * sqrt(periods_per_year)


def _calculate_max_drawdown(equity_curve: list[float]) -> float:
    peak = 1.0
    max_drawdown = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        drawdown = 1 - (equity / peak)
        max_drawdown = max(max_drawdown, drawdown)
    return max_drawdown
