from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from datetime import date, timedelta
from statistics import stdev

from financial_analysis_tool.core.exceptions import InputDataError

from .models import FactorSnapshot, PriceRecord


def compute_factor_snapshots(
    price_records: list[PriceRecord],
    *,
    momentum_lookback_days: int = 90,
    volatility_lookback_days: int = 90,
) -> dict[date, list[FactorSnapshot]]:
    if momentum_lookback_days <= 0:
        raise InputDataError("momentum_lookback_days must be greater than 0.")
    if volatility_lookback_days <= 0:
        raise InputDataError("volatility_lookback_days must be greater than 0.")
    if not price_records:
        raise InputDataError("At least one price record is required for factor calculation.")

    history_by_ticker: dict[str, list[PriceRecord]] = defaultdict(list)
    for record in sorted(price_records, key=lambda item: (item.ticker, item.date)):
        history_by_ticker[record.ticker].append(record)

    snapshots_by_date: dict[date, list[FactorSnapshot]] = defaultdict(list)
    for ticker_history in history_by_ticker.values():
        history_dates = [record.date for record in ticker_history]
        for index, current_record in enumerate(ticker_history):
            if index == 0:
                continue

            anchor_index = _find_anchor_index(
                history_dates,
                current_record.date,
                lookback_days=momentum_lookback_days,
            )
            if anchor_index is None or anchor_index >= index:
                continue

            trailing_returns = _collect_trailing_returns(
                ticker_history,
                current_index=index,
                window_days=volatility_lookback_days,
            )
            if len(trailing_returns) < 2:
                continue

            snapshots_by_date[current_record.date].append(
                FactorSnapshot(
                    date=current_record.date,
                    ticker=current_record.ticker,
                    close=current_record.close,
                    momentum=_calculate_return(
                        ticker_history[anchor_index].close,
                        current_record.close,
                    ),
                    volatility=_calculate_volatility(trailing_returns),
                )
            )

    return {
        snapshot_date: sorted(snapshots, key=lambda snapshot: snapshot.ticker)
        for snapshot_date, snapshots in snapshots_by_date.items()
    }


def _find_anchor_index(
    history_dates: list[date],
    current_date: date,
    *,
    lookback_days: int,
) -> int | None:
    window_start = current_date - timedelta(days=lookback_days)
    anchor_index = bisect_left(history_dates, window_start)
    if anchor_index >= len(history_dates):
        return None
    return anchor_index


def _collect_trailing_returns(
    ticker_history: list[PriceRecord],
    *,
    current_index: int,
    window_days: int,
) -> list[float]:
    current_date = ticker_history[current_index].date
    window_start = current_date - timedelta(days=window_days)
    trailing_returns: list[float] = []
    for position in range(1, current_index + 1):
        start_record = ticker_history[position - 1]
        end_record = ticker_history[position]
        if start_record.date < window_start or end_record.date > current_date:
            continue
        trailing_returns.append(
            _calculate_return(
                start_record.close,
                end_record.close,
            )
        )
    return trailing_returns


def _calculate_return(start_value: float, end_value: float) -> float:
    if start_value == 0:
        raise InputDataError("Price data contains a zero close value, which breaks return calculation.")
    return (end_value - start_value) / start_value


def _calculate_volatility(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    return stdev(returns)
