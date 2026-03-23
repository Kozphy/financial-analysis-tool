from __future__ import annotations

from collections import defaultdict
from datetime import date
from statistics import stdev

from .models import FactorSnapshot, PriceRecord


def compute_factor_snapshots(
    price_records: list[PriceRecord],
    *,
    lookback_periods: int = 3,
    volatility_window: int = 3,
) -> dict[date, list[FactorSnapshot]]:
    if lookback_periods <= 0:
        raise ValueError("lookback_periods must be greater than 0.")
    if volatility_window <= 0:
        raise ValueError("volatility_window must be greater than 0.")
    if not price_records:
        raise ValueError("At least one price record is required for factor calculation.")

    history_by_ticker: dict[str, list[PriceRecord]] = defaultdict(list)
    for record in sorted(price_records, key=lambda item: (item.ticker, item.date)):
        history_by_ticker[record.ticker].append(record)

    minimum_index = max(lookback_periods, volatility_window)
    snapshots_by_date: dict[date, list[FactorSnapshot]] = defaultdict(list)

    for ticker_history in history_by_ticker.values():
        for index in range(minimum_index, len(ticker_history) - 1):
            current_record = ticker_history[index]
            next_record = ticker_history[index + 1]
            anchor_record = ticker_history[index - lookback_periods]
            trailing_returns = [
                _calculate_return(ticker_history[position - 1].close, ticker_history[position].close)
                for position in range(index - volatility_window + 1, index + 1)
            ]

            snapshots_by_date[current_record.date].append(
                FactorSnapshot(
                    date=current_record.date,
                    ticker=current_record.ticker,
                    close=current_record.close,
                    momentum=_calculate_return(anchor_record.close, current_record.close),
                    volatility=_calculate_volatility(trailing_returns),
                    next_date=next_record.date,
                    forward_return=_calculate_return(current_record.close, next_record.close),
                )
            )

    return {
        snapshot_date: sorted(snapshots, key=lambda snapshot: snapshot.ticker)
        for snapshot_date, snapshots in snapshots_by_date.items()
    }


def _calculate_return(start_value: float, end_value: float) -> float:
    if start_value == 0:
        raise ValueError("Price data contains a zero close value, which breaks return calculation.")
    return (end_value - start_value) / start_value


def _calculate_volatility(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    return stdev(returns)
