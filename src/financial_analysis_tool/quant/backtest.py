from __future__ import annotations

from statistics import fmean

from financial_analysis_tool.core.exceptions import InputDataError
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
        raise InputDataError("top_n must be greater than 0.")
    if periods_per_year <= 0:
        raise InputDataError("periods_per_year must be greater than 0.")

    benchmark_symbol = benchmark_ticker.strip().upper() if benchmark_ticker else None
    snapshots_by_date = compute_factor_snapshots(
        price_records,
        lookback_periods=lookback_periods,
        volatility_window=volatility_window,
    )
    if not snapshots_by_date:
        raise InputDataError("Not enough price history is available to run the backtest.")

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
        positions = build_equal_weight_portfolio(ranked_assets, top_n)
        strategy_return = sum(
            position.weight * position.asset.forward_return for position in positions
        )
        benchmark_return = (
            benchmark_snapshot.forward_return
            if benchmark_snapshot
            else fmean(snapshot.forward_return for snapshot in universe)
        )

        strategy_equity *= 1 + strategy_return
        benchmark_equity *= 1 + benchmark_return

        next_dates = {position.asset.next_date for position in positions}
        if benchmark_snapshot:
            next_dates.add(benchmark_snapshot.next_date)

        periods.append(
            BacktestPeriod(
                rebalance_date=rebalance_date,
                next_date=max(next_dates),
                positions=positions,
                universe_size=len(universe),
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

    return BacktestResult(
        periods=periods,
        benchmark_label=benchmark_symbol or "Equal-Weight Universe",
        lookback_periods=lookback_periods,
        volatility_window=volatility_window,
        top_n=top_n,
        periods_per_year=periods_per_year,
        total_return=periods[-1].strategy_equity - 1,
        benchmark_total_return=periods[-1].benchmark_equity - 1,
        annualized_return=annualize_return(
            periods[-1].strategy_equity,
            len(periods),
            periods_per_year,
        ),
        benchmark_annualized_return=annualize_return(
            periods[-1].benchmark_equity,
            len(periods),
            periods_per_year,
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
