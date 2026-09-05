"""Simple finance-oriented forecasting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class ForecastPoint:
    period: int
    value: float


def growth_rates(values: Iterable[float]) -> list[float]:
    series = [float(v) for v in values]
    if len(series) < 2:
        return []

    rates: list[float] = []
    for previous, current in zip(series, series[1:]):
        if previous == 0:
            raise ValueError("cannot calculate growth rate from a zero base")
        rates.append((current / previous) - 1.0)
    return rates


def cagr(start_value: float, end_value: float, periods: int) -> float:
    if start_value <= 0 or end_value < 0:
        raise ValueError("CAGR requires a positive start value and non-negative end value")
    if periods <= 0:
        raise ValueError("periods must be positive")
    return (end_value / start_value) ** (1.0 / periods) - 1.0


def forecast_by_growth(
    latest_value: float,
    annual_growth_rate: float,
    periods: int,
) -> list[ForecastPoint]:
    if periods < 1:
        raise ValueError("periods must be >= 1")
    return [
        ForecastPoint(period=i, value=latest_value * ((1 + annual_growth_rate) ** i))
        for i in range(1, periods + 1)
    ]


def forecast_using_average_historical_growth(
    historical_values: Iterable[float],
    periods: int,
    lookback: int | None = None,
) -> list[ForecastPoint]:
    values = [float(v) for v in historical_values]
    if len(values) < 2:
        raise ValueError("at least two historical observations are required")

    rates = growth_rates(values)
    if lookback is not None:
        if lookback < 1:
            raise ValueError("lookback must be >= 1")
        rates = rates[-lookback:]

    return forecast_by_growth(values[-1], mean(rates), periods)


def scenario_forecast(
    latest_value: float,
    base_growth: float,
    bull_growth: float,
    bear_growth: float,
    periods: int,
) -> dict[str, list[ForecastPoint]]:
    """Generate base, bull, and bear forecast paths."""
    return {
        "base": forecast_by_growth(latest_value, base_growth, periods),
        "bull": forecast_by_growth(latest_value, bull_growth, periods),
        "bear": forecast_by_growth(latest_value, bear_growth, periods),
    }
