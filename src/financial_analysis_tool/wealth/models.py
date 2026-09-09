from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

EvidenceLevel = Literal["E0", "E1", "E2", "E3", "E4", "E5"]
AssetCategory = Literal[
    "cash",
    "bank_deposit",
    "securities",
    "real_estate",
    "insurance",
    "business_interest",
    "digital_asset",
    "private_claim",
    "physical_asset",
    "overseas_asset",
    "other",
]
LiabilityCategory = Literal[
    "mortgage",
    "personal_loan",
    "vehicle_loan",
    "credit_card",
    "margin_debt",
    "private_debt",
    "other",
]

EVIDENCE_WEIGHTS: dict[str, Decimal] = {
    "E0": Decimal("0.10"),
    "E1": Decimal("0.25"),
    "E2": Decimal("0.45"),
    "E3": Decimal("0.70"),
    "E4": Decimal("0.90"),
    "E5": Decimal("1.00"),
}


@dataclass(frozen=True)
class AssetObservation:
    asset_key: str
    category: AssetCategory
    owner_key: str
    gross_value: Decimal
    ownership_pct: Decimal
    valuation_date: date
    source: str
    evidence_level: EvidenceLevel
    currency: str = "TWD"
    notes: str | None = None

    @property
    def owned_value(self) -> Decimal:
        return self.gross_value * self.ownership_pct


@dataclass(frozen=True)
class LiabilityObservation:
    liability_key: str
    owner_key: str
    balance: Decimal
    valuation_date: date
    source: str
    evidence_level: EvidenceLevel
    category: LiabilityCategory = "other"
    linked_asset_key: str | None = None
    currency: str = "TWD"
    notes: str | None = None


@dataclass(frozen=True)
class ReconciliationException:
    code: str
    key: str
    severity: Literal["INFO", "WARN", "HIGH"]
    message: str


@dataclass(frozen=True)
class ReconciledAsset:
    asset_key: str
    category: AssetCategory
    owner_key: str
    canonical_value: Decimal
    ownership_pct: Decimal
    owned_value: Decimal
    evidence_level: EvidenceLevel
    source: str
    valuation_date: date
    confidence: Decimal
    observation_count: int


@dataclass(frozen=True)
class ReconciledLiability:
    liability_key: str
    owner_key: str
    canonical_balance: Decimal
    evidence_level: EvidenceLevel
    source: str
    valuation_date: date
    confidence: Decimal
    linked_asset_key: str | None
    observation_count: int


@dataclass
class ReconciliationReport:
    assets: list[ReconciledAsset] = field(default_factory=list)
    liabilities: list[ReconciledLiability] = field(default_factory=list)
    exceptions: list[ReconciliationException] = field(default_factory=list)
    gross_assets: Decimal = Decimal("0")
    total_liabilities: Decimal = Decimal("0")
    net_worth: Decimal = Decimal("0")
    confidence: Decimal = Decimal("0")
