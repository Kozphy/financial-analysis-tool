from __future__ import annotations

from .models import FactorSnapshot, RankedAsset


def rank_assets(
    factor_snapshots: list[FactorSnapshot],
    *,
    momentum_weight: float = 0.8,
    volatility_weight: float = 0.2,
) -> list[RankedAsset]:
    if not factor_snapshots:
        raise ValueError("At least one factor snapshot is required for ranking.")
    if momentum_weight < 0 or volatility_weight < 0:
        raise ValueError("Ranking weights must be non-negative.")
    if momentum_weight == 0 and volatility_weight == 0:
        raise ValueError("At least one ranking weight must be greater than zero.")

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
                * _score_from_rank(momentum_ranks[snapshot.ticker], asset_count)
                + normalized_volatility_weight
                * _score_from_rank(volatility_ranks[snapshot.ticker], asset_count)
            ),
            next_date=snapshot.next_date,
            forward_return=snapshot.forward_return,
        )
        for snapshot in factor_snapshots
    ]

    return sorted(
        ranked_assets,
        key=lambda asset: (-asset.score, -asset.momentum, asset.volatility, asset.ticker),
    )


def select_top_ranked_assets(
    ranked_assets: list[RankedAsset],
    top_n: int,
) -> list[RankedAsset]:
    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")
    return ranked_assets[: min(top_n, len(ranked_assets))]


def _build_rank_map(ordered_snapshots: list[FactorSnapshot]) -> dict[str, int]:
    return {
        snapshot.ticker: rank
        for rank, snapshot in enumerate(ordered_snapshots, start=1)
    }


def _score_from_rank(rank: int, asset_count: int) -> float:
    if asset_count == 1:
        return 1.0
    return (asset_count - rank) / (asset_count - 1)
