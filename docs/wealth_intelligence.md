# Wealth Intelligence: Evidence-Based Reconciliation

This module estimates a person's net-worth snapshot from authorized, partial financial observations. It is designed for self-owned data or data the operator is legally authorized to process.

## Core flow

```text
Authorized data sources
  -> asset/liability observations
  -> evidence scoring (E0-E5)
  -> ownership application
  -> canonical observation selection
  -> mismatch/orphan exception detection
  -> reconciliation
  -> gross assets - liabilities
  -> estimated net worth + confidence
```

## Evidence levels

- E0: rumor or unsupported guess
- E1: self-reported statement
- E2: screenshot or informal record
- E3: third-party or financial institution document
- E4: official registration or formal evidence
- E5: multiple independent sources reconciled

The engine ranks observations primarily by evidence strength and secondarily by valuation date. Conflicting values above the configured tolerance reduce confidence and create an exception instead of being silently averaged.

## Database model

`db/wealth_schema.sql` separates:

- `person`
- `asset`
- `liability`
- `evidence_source`
- `asset_observation`
- `liability_observation`
- `reconciliation_run`
- `reconciliation_exception`

This preserves raw evidence separately from canonical reconciled outputs, which is important for auditability.

## Design principles

1. **Observed wealth is not true wealth.** The system estimates only from supplied evidence and does not claim hidden assets are known.
2. **Ownership before valuation.** An asset's gross market value is not automatically the owner's economic value.
3. **Liabilities are first-class records.** Net worth is not gross assets.
4. **Do not hide disagreement.** Material source differences become reconciliation exceptions.
5. **Deterministic rules first.** The initial implementation avoids opaque ML so every result is explainable and testable.
6. **Authorization is required.** This is not a tool for bypassing privacy, banking, tax, or legal-access controls.

## Python example

```python
from datetime import date
from decimal import Decimal

from financial_analysis_tool.wealth import AssetObservation, LiabilityObservation, reconcile_wealth

assets = [
    AssetObservation(
        asset_key="home",
        category="real_estate",
        owner_key="person-a",
        gross_value=Decimal("20000000"),
        ownership_pct=Decimal("0.5"),
        valuation_date=date(2026, 8, 31),
        source="formal-valuation",
        evidence_level="E4",
    )
]

liabilities = [
    LiabilityObservation(
        liability_key="mortgage",
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
print(report.net_worth)
print(report.confidence)
print(report.exceptions)
```

## Next engineering steps

- Persist reconciliation runs to SQLite/PostgreSQL.
- Add currency normalization with explicit FX snapshots.
- Add valuation-policy adapters by asset class.
- Add duplicate/entity resolution for imported statements.
- Add FastAPI endpoints for ingest, reconcile, exceptions, and snapshots.
- Add an immutable audit event stream.
- Add scenario analysis without overwriting historical evidence.
