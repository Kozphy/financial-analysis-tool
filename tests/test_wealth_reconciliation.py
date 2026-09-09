from datetime import date
from decimal import Decimal

import pytest

from financial_analysis_tool.wealth import (
    AssetObservation,
    LiabilityObservation,
    reconcile_wealth,
)


def test_reconcile_wealth_applies_ownership_and_liabilities():
    assets = [
        AssetObservation(
            asset_key="home",
            category="real_estate",
            owner_key="person-a",
            gross_value=Decimal("20000000"),
            ownership_pct=Decimal("0.5"),
            valuation_date=date(2026, 8, 31),
            source="land-registry-plus-valuation",
            evidence_level="E5",
        ),
        AssetObservation(
            asset_key="bank-a",
            category="bank_deposit",
            owner_key="person-a",
            gross_value=Decimal("500000"),
            ownership_pct=Decimal("1"),
            valuation_date=date(2026, 8, 31),
            source="bank-statement",
            evidence_level="E4",
        ),
    ]
    liabilities = [
        LiabilityObservation(
            liability_key="mortgage-a",
            category="mortgage",
            owner_key="person-a",
            balance=Decimal("3000000"),
            valuation_date=date(2026, 8, 31),
            source="loan-statement",
            evidence_level="E4",
            linked_asset_key="home",
        )
    ]

    report = reconcile_wealth(assets, liabilities)

    assert report.gross_assets == Decimal("10500000.0")
    assert report.total_liabilities == Decimal("3000000")
    assert report.net_worth == Decimal("7500000.0")
    assert report.exceptions == []
    assert report.confidence > Decimal("0.8")


def test_reconciliation_prefers_stronger_evidence_and_flags_mismatch():
    assets = [
        AssetObservation(
            asset_key="broker-a",
            category="securities",
            owner_key="person-a",
            gross_value=Decimal("800000"),
            ownership_pct=Decimal("1"),
            valuation_date=date(2026, 8, 30),
            source="screenshot",
            evidence_level="E2",
        ),
        AssetObservation(
            asset_key="broker-a",
            category="securities",
            owner_key="person-a",
            gross_value=Decimal("1000000"),
            ownership_pct=Decimal("1"),
            valuation_date=date(2026, 8, 29),
            source="broker-statement",
            evidence_level="E4",
        ),
    ]

    report = reconcile_wealth(assets, [])

    assert report.assets[0].canonical_value == Decimal("1000000")
    assert any(item.code == "ASSET_VALUE_MISMATCH" for item in report.exceptions)


def test_orphan_linked_liability_is_high_severity_exception():
    liabilities = [
        LiabilityObservation(
            liability_key="mortgage-a",
            category="mortgage",
            owner_key="person-a",
            balance=Decimal("1000000"),
            valuation_date=date(2026, 8, 31),
            source="loan-statement",
            evidence_level="E4",
            linked_asset_key="missing-home",
        )
    ]

    report = reconcile_wealth([], liabilities)

    assert any(
        item.code == "ORPHAN_LIABILITY" and item.severity == "HIGH"
        for item in report.exceptions
    )


def test_invalid_ownership_is_rejected():
    assets = [
        AssetObservation(
            asset_key="bad",
            category="other",
            owner_key="person-a",
            gross_value=Decimal("1"),
            ownership_pct=Decimal("1.1"),
            valuation_date=date(2026, 8, 31),
            source="manual",
            evidence_level="E1",
        )
    ]

    with pytest.raises(ValueError, match="ownership_pct"):
        reconcile_wealth(assets, [])
