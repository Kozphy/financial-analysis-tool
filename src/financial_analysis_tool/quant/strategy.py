from __future__ import annotations

from financial_analysis_tool.core.exceptions import InputDataError
from financial_analysis_tool.core.utils import rank_score

from .models import FactorSnapshot, RankedAsset


def rank_assets(
    factor_snapshots: list[FactorSnapshot],
    *,
    momentum_weight: float = 0.8,
    volatility_weight: float = 0.2,
) -> list[RankedAsset]:
    if not factor_snapshots:
        raise InputDataError("At least one factor snapshot is required for ranking.")
    if momentum_weight < 0 or volatility_weight < 0:
        raise InputDataError("Ranking weights must be non-negative.")
    if momentum_weight == 0 and volatility_weight == 0:
        raise InputDataError("At least one ranking weight must be greater than zero.")

    total_weight = momentum_weight + volatility_weight
    normalized_momentum_weight = momentum_weight / total_weight
    normalized_volatility_weight = volatility_weight / total_weight
    asset_count = len(factor_snapshots)

    momentum_ranks = _build_rank_map(
        sorted(
            factor_snapshots,
            key=lambda snapshot: (-snapshot.momentum, snapshot.volatility, snapshot.ticker),
        )
    )
    volatility_ranks = _build_rank_map(
        sorted(
            factor_snapshots,
            key=lambda snapshot: (snapshot.volatility, -snapshot.momentum, snapshot.ticker),
        )
    )

    ranked_assets = [
        RankedAsset(
            date=snapshot.date,
            ticker=snapshot.ticker,
            close=snapshot.close,
            momentum=snapshot.momentum,
            volatility=snapshot.volatility,
            momentum_rank=momentum_ranks[snapshot.ticker],
            volatility_rank=volatility_ranks[snapshot.ticker],
            score=(
                normalized_momentum_weight
                * rank_score(momentum_ranks[snapshot.ticker], asset_count)
                + normalized_volatility_weight
                * rank_score(volatility_ranks[snapshot.ticker], asset_count)
            ),
        )
        for snapshot in factor_snapshots
    ]

    return sorted(
        ranked_assets,
        key=lambda asset: (-asset.score, -asset.momentum, asset.volatility, asset.ticker),
    )


def _build_rank_map(ordered_snapshots: list[FactorSnapshot]) -> dict[str, int]:
    return {
        snapshot.ticker: rank
        for rank, snapshot in enumerate(ordered_snapshots, start=1)
    }
