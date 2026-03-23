from __future__ import annotations

from financial_analysis_tool.core.exceptions import InputDataError

from .models import PortfolioPosition, RankedAsset


def build_equal_weight_portfolio(
    ranked_assets: list[RankedAsset],
    top_n: int,
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
        )
        for asset in selected_assets
    ]
