from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from financial_analysis_tool.core.types import JsonDict


@dataclass(frozen=True, slots=True)
class PriceRecord:
    date: date
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self) -> JsonDict:
        return {
            "date": self.date.isoformat(),
            "ticker": self.ticker,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


@dataclass(frozen=True, slots=True)
class FactorSnapshot:
    date: date
    ticker: str
    close: float
    momentum: float
    volatility: float
    next_date: date
    forward_return: float

    def to_dict(self) -> JsonDict:
        return {
            "date": self.date.isoformat(),
            "ticker": self.ticker,
            "close": self.close,
            "momentum": self.momentum,
            "volatility": self.volatility,
            "next_date": self.next_date.isoformat(),
            "forward_return": self.forward_return,
        }


@dataclass(frozen=True, slots=True)
class RankedAsset:
    date: date
    ticker: str
    close: float
    momentum: float
    volatility: float
    momentum_rank: int
    volatility_rank: int
    score: float
    next_date: date
    forward_return: float

    def to_dict(self) -> JsonDict:
        return {
            "date": self.date.isoformat(),
            "ticker": self.ticker,
            "close": self.close,
            "momentum": self.momentum,
            "volatility": self.volatility,
            "momentum_rank": self.momentum_rank,
            "volatility_rank": self.volatility_rank,
            "score": self.score,
            "next_date": self.next_date.isoformat(),
            "forward_return": self.forward_return,
        }


@dataclass(frozen=True, slots=True)
class PortfolioPosition:
    ticker: str
    weight: float
    asset: RankedAsset

    def to_dict(self) -> JsonDict:
        return {
            "ticker": self.ticker,
            "weight": self.weight,
            "asset": self.asset.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class BacktestPeriod:
    rebalance_date: date
    next_date: date
    positions: list[PortfolioPosition]
    universe_size: int
    strategy_return: float
    benchmark_return: float
    strategy_equity: float
    benchmark_equity: float

    def to_dict(self) -> JsonDict:
        return {
            "rebalance_date": self.rebalance_date.isoformat(),
            "next_date": self.next_date.isoformat(),
            "positions": [position.to_dict() for position in self.positions],
            "universe_size": self.universe_size,
            "strategy_return": self.strategy_return,
            "benchmark_return": self.benchmark_return,
            "strategy_equity": self.strategy_equity,
            "benchmark_equity": self.benchmark_equity,
        }


@dataclass(frozen=True, slots=True)
class BacktestResult:
    periods: list[BacktestPeriod]
    benchmark_label: str
    lookback_periods: int
    volatility_window: int
    top_n: int
    periods_per_year: int
    total_return: float
    benchmark_total_return: float
    annualized_return: float | None
    benchmark_annualized_return: float | None
    annualized_volatility: float | None
    benchmark_annualized_volatility: float | None
    sharpe_ratio: float | None
    benchmark_sharpe_ratio: float | None
    max_drawdown: float
    benchmark_max_drawdown: float
    positive_period_rate: float
    outperformance_rate: float

    def to_dict(self) -> JsonDict:
        return {
            "benchmark_label": self.benchmark_label,
            "lookback_periods": self.lookback_periods,
            "volatility_window": self.volatility_window,
            "top_n": self.top_n,
            "periods_per_year": self.periods_per_year,
            "total_return": self.total_return,
            "benchmark_total_return": self.benchmark_total_return,
            "annualized_return": self.annualized_return,
            "benchmark_annualized_return": self.benchmark_annualized_return,
            "annualized_volatility": self.annualized_volatility,
            "benchmark_annualized_volatility": self.benchmark_annualized_volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "benchmark_sharpe_ratio": self.benchmark_sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "benchmark_max_drawdown": self.benchmark_max_drawdown,
            "positive_period_rate": self.positive_period_rate,
            "outperformance_rate": self.outperformance_rate,
            "periods": [period.to_dict() for period in self.periods],
        }
