"""Portfolio risk metrics for interview-facing finance analytics."""

from __future__ import annotations

from math import sqrt
from statistics import mean, pstdev
from typing import Iterable


def simple_returns(prices: Iterable[float]) -> list[float]:
    values = [float(v) for v in prices]
    if len(values) < 2:
        return []
    if any(v <= 0 for v in values):
        raise ValueError("prices must be positive")
    return [(current / previous) - 1.0 for previous, current in zip(values, values[1:])]


def annualized_volatility(returns: Iterable[float], periods_per_year: int = 252) -> float:
    values = [float(v) for v in returns]
    if not values:
        raise ValueError("returns must not be empty")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    return pstdev(values) * sqrt(periods_per_year)


def sharpe_ratio(
    returns: Iterable[float],
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    values = [float(v) for v in returns]
    if not values:
        raise ValueError("returns must not be empty")
    volatility = pstdev(values)
    if volatility == 0:
        raise ValueError("Sharpe ratio is undefined for zero-volatility returns")
    periodic_rf = risk_free_rate / periods_per_year
    return ((mean(values) - periodic_rf) / volatility) * sqrt(periods_per_year)


def historical_var(returns: Iterable[float], confidence: float = 0.95) -> float:
    """Return positive historical Value at Risk as a fraction of portfolio value."""
    values = sorted(float(v) for v in returns)
    if not values:
        raise ValueError("returns must not be empty")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    tail_probability = 1.0 - confidence
    index = max(0, min(len(values) - 1, int(tail_probability * len(values))))
    return max(0.0, -values[index])


def expected_shortfall(returns: Iterable[float], confidence: float = 0.95) -> float:
    """Return positive historical Expected Shortfall as a fraction of portfolio value."""
    values = sorted(float(v) for v in returns)
    if not values:
        raise ValueError("returns must not be empty")
    var = historical_var(values, confidence)
    tail = [r for r in values if r <= -var]
    if not tail:
        return var
    return max(0.0, -mean(tail))


def max_drawdown(prices: Iterable[float]) -> float:
    values = [float(v) for v in prices]
    if not values:
        raise ValueError("prices must not be empty")
    if any(v <= 0 for v in values):
        raise ValueError("prices must be positive")

    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = (value / peak) - 1.0
        worst = min(worst, drawdown)
    return abs(worst)
