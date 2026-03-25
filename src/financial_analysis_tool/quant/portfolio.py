from __future__ import annotations

from datetime import date

from financial_analysis_tool.core.exceptions import InputDataError

from .models import PortfolioPosition, RankedAsset


def build_equal_weight_portfolio(
    ranked_assets: list[RankedAsset],
    top_n: int,
    *,
    exit_date: date | None = None,
    exit_prices: dict[str, float] | None = None,
) -> list[PortfolioPosition]:
    if top_n <= 0:
        raise InputDataError("top_n must be greater than 0.")

    selected_assets = ranked_assets[: min(top_n, len(ranked_assets))]
    if not selected_assets:
        raise InputDataError("No ranked assets are available to build a portfolio.")

    weight = 1 / len(selected_assets)
    return [
        PortfolioPosition(
            ticker=asset.ticker,
            weight=weight,
            asset=asset,
            entry_date=asset.date,
            exit_date=exit_date or asset.date,
            entry_close=asset.close,
            exit_close=(exit_prices or {}).get(asset.ticker, asset.close),
            forward_return=_calculate_forward_return(
                asset.close,
                (exit_prices or {}).get(asset.ticker, asset.close),
            ),
        )
        for asset in selected_assets
    ]


def _calculate_forward_return(entry_close: float, exit_close: float) -> float:
    if entry_close == 0:
        raise InputDataError("Price data contains a zero close value, which breaks return calculation.")
    return (exit_close - entry_close) / entry_close
