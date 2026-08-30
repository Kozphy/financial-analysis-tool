from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Iterable, TypeVar

from .models import (
    EVIDENCE_WEIGHTS,
    AssetObservation,
    LiabilityObservation,
    ReconciledAsset,
    ReconciledLiability,
    ReconciliationException,
    ReconciliationReport,
)

T = TypeVar("T", AssetObservation, LiabilityObservation)


def _rank_observation(item: T) -> tuple[Decimal, object]:
    return (EVIDENCE_WEIGHTS[item.evidence_level], item.valuation_date)


def _spread_ratio(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")
    maximum = max(values)
    minimum = min(values)
    denominator = max(abs(maximum), Decimal("1"))
    return abs(maximum - minimum) / denominator


def _weighted_confidence(levels: list[str], agreement_penalty: Decimal) -> Decimal:
    if not levels:
        return Decimal("0")
    base = sum((EVIDENCE_WEIGHTS[level] for level in levels), Decimal("0")) / Decimal(len(levels))
    result = base * agreement_penalty
    return max(Decimal("0"), min(Decimal("1"), result)).quantize(Decimal("0.001"))


def reconcile_wealth(
    assets: Iterable[AssetObservation],
    liabilities: Iterable[LiabilityObservation],
    *,
    value_tolerance: Decimal = Decimal("0.10"),
) -> ReconciliationReport:
    """Reconcile partial observations into an estimated net-worth snapshot.

    The engine is intentionally deterministic and explainable:
    1. Group observations by stable asset/liability key.
    2. Select the canonical observation by evidence strength, then recency.
    3. Emit exceptions when independent values disagree beyond tolerance.
    4. Apply ownership percentage to asset values.
    5. Aggregate assets minus liabilities and attach a confidence estimate.

    It does not discover hidden assets and must only be used with data the user
    is authorized to process.
    """
    asset_groups: dict[str, list[AssetObservation]] = defaultdict(list)
    liability_groups: dict[str, list[LiabilityObservation]] = defaultdict(list)
    exceptions: list[ReconciliationException] = []

    for observation in assets:
        if not Decimal("0") <= observation.ownership_pct <= Decimal("1"):
            raise ValueError(f"ownership_pct must be between 0 and 1: {observation.asset_key}")
        if observation.gross_value < 0:
            raise ValueError(f"gross_value cannot be negative: {observation.asset_key}")
        asset_groups[observation.asset_key].append(observation)

    for observation in liabilities:
        if observation.balance < 0:
            raise ValueError(f"liability balance cannot be negative: {observation.liability_key}")
        liability_groups[observation.liability_key].append(observation)

    reconciled_assets: list[ReconciledAsset] = []
    for key, observations in sorted(asset_groups.items()):
        canonical = max(observations, key=_rank_observation)
        spread = _spread_ratio([item.gross_value for item in observations])
        agreement_penalty = Decimal("0.75") if spread > value_tolerance else Decimal("1")
        if spread > value_tolerance:
            exceptions.append(
                ReconciliationException(
                    code="ASSET_VALUE_MISMATCH",
                    key=key,
                    severity="WARN",
                    message=f"Asset observations differ by {spread:.1%}, above tolerance {value_tolerance:.1%}.",
                )
            )
        if canonical.evidence_level in {"E0", "E1", "E2"}:
            exceptions.append(
                ReconciliationException(
                    code="WEAK_ASSET_EVIDENCE",
                    key=key,
                    severity="WARN",
                    message=f"Canonical asset evidence is only {canonical.evidence_level}.",
                )
            )
        reconciled_assets.append(
            ReconciledAsset(
                asset_key=key,
                category=canonical.category,
                owner_key=canonical.owner_key,
                canonical_value=canonical.gross_value,
                ownership_pct=canonical.ownership_pct,
                owned_value=canonical.owned_value,
                evidence_level=canonical.evidence_level,
                source=canonical.source,
                valuation_date=canonical.valuation_date,
                confidence=_weighted_confidence(
                    [item.evidence_level for item in observations], agreement_penalty
                ),
                observation_count=len(observations),
            )
        )

    reconciled_liabilities: list[ReconciledLiability] = []
    known_asset_keys = set(asset_groups)
    for key, observations in sorted(liability_groups.items()):
        canonical = max(observations, key=_rank_observation)
        spread = _spread_ratio([item.balance for item in observations])
        agreement_penalty = Decimal("0.75") if spread > value_tolerance else Decimal("1")
        if spread > value_tolerance:
            exceptions.append(
                ReconciliationException(
                    code="LIABILITY_VALUE_MISMATCH",
                    key=key,
                    severity="WARN",
                    message=f"Liability observations differ by {spread:.1%}, above tolerance {value_tolerance:.1%}.",
                )
            )
        if canonical.linked_asset_key and canonical.linked_asset_key not in known_asset_keys:
            exceptions.append(
                ReconciliationException(
                    code="ORPHAN_LIABILITY",
                    key=key,
                    severity="HIGH",
                    message=f"Linked asset {canonical.linked_asset_key!r} is not present in the asset population.",
                )
            )
        reconciled_liabilities.append(
            ReconciledLiability(
                liability_key=key,
                owner_key=canonical.owner_key,
                canonical_balance=canonical.balance,
                evidence_level=canonical.evidence_level,
                source=canonical.source,
                valuation_date=canonical.valuation_date,
                confidence=_weighted_confidence(
                    [item.evidence_level for item in observations], agreement_penalty
                ),
                linked_asset_key=canonical.linked_asset_key,
                observation_count=len(observations),
            )
        )

    gross_assets = sum((item.owned_value for item in reconciled_assets), Decimal("0"))
    total_liabilities = sum((item.canonical_balance for item in reconciled_liabilities), Decimal("0"))
    confidence_items = [item.confidence for item in reconciled_assets] + [
        item.confidence for item in reconciled_liabilities
    ]
    confidence = (
        sum(confidence_items, Decimal("0")) / Decimal(len(confidence_items))
        if confidence_items
        else Decimal("0")
    ).quantize(Decimal("0.001"))

    return ReconciliationReport(
        assets=reconciled_assets,
        liabilities=reconciled_liabilities,
        exceptions=exceptions,
        gross_assets=gross_assets,
        total_liabilities=total_liabilities,
        net_worth=gross_assets - total_liabilities,
        confidence=confidence,
    )
