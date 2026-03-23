from __future__ import annotations

from datetime import date, datetime, time, timezone
from math import sqrt
from statistics import fmean, stdev


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


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


def annualize_return(equity: float, period_count: int, periods_per_year: int) -> float | None:
    if period_count <= 0:
        return None
    return equity ** (periods_per_year / period_count) - 1


def annualize_volatility(returns: list[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None
    return stdev(returns) * sqrt(periods_per_year)


def sharpe_ratio(returns: list[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None

    volatility = stdev(returns)
    if volatility == 0:
        return None

    return fmean(returns) / volatility * sqrt(periods_per_year)


def max_drawdown(equity_curve: list[float]) -> float:
    peak = 1.0
    largest_drawdown = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        largest_drawdown = max(largest_drawdown, 1 - (equity / peak))
    return largest_drawdown


def rank_score(rank: int, asset_count: int) -> float:
    if asset_count == 1:
        return 1.0
    return (asset_count - rank) / (asset_count - 1)


def to_epoch_milliseconds(value: date, *, end_of_day: bool = False) -> int:
    clock = time.max if end_of_day else time.min
    timestamp = datetime.combine(value, clock, tzinfo=timezone.utc)
    return int(timestamp.timestamp() * 1000)
