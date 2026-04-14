"""Data models for raw financial statements and derived analysis output."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True, slots=True)
class FinancialStatementRecord:
    """Represents one reporting period from the input financial statement CSV."""

    period: str
    revenue: float
    cost_of_revenue: float
    operating_expenses: float
    net_income: float
    current_assets: float
    current_liabilities: float
    total_assets: float
    total_liabilities: float

    def to_dict(self) -> JsonDict:
        """Return the record in JSON-serializable dictionary form."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PeriodMetrics:
    """Stores calculated profitability, liquidity, and leverage metrics for one period."""

    period: str
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    revenue_growth: float | None
    gross_margin: float | None
    operating_margin: float | None
    net_margin: float | None
    current_ratio: float | None
    debt_ratio: float | None
    current_assets: float
    current_liabilities: float
    total_assets: float
    total_liabilities: float

    def to_dict(self) -> JsonDict:
        """Return the calculated period metrics in dictionary form."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AnalysisSummary:
    """Aggregates the headline outputs used by reports, charts, and UI surfaces."""

    company_name: str
    periods: list[PeriodMetrics]
    latest_period: PeriodMetrics
    overall_revenue_growth: float | None
    average_gross_margin: float | None
    average_operating_margin: float | None
    average_net_margin: float | None
    latest_current_ratio: float | None
    latest_debt_ratio: float | None
    best_growth_period: PeriodMetrics | None
    strongest_liquidity_period: PeriodMetrics | None
    lowest_debt_period: PeriodMetrics | None

    def to_dict(self) -> JsonDict:
        """Return the analysis summary and nested metrics as plain dictionaries."""
        return {
            "company_name": self.company_name,
            "latest_period": self.latest_period.to_dict(),
            "overall_revenue_growth": self.overall_revenue_growth,
            "average_gross_margin": self.average_gross_margin,
            "average_operating_margin": self.average_operating_margin,
            "average_net_margin": self.average_net_margin,
            "latest_current_ratio": self.latest_current_ratio,
            "latest_debt_ratio": self.latest_debt_ratio,
            "best_growth_period": (
                self.best_growth_period.to_dict() if self.best_growth_period else None
            ),
            "strongest_liquidity_period": (
                self.strongest_liquidity_period.to_dict() if self.strongest_liquidity_period else None
            ),
            "lowest_debt_period": (
                self.lowest_debt_period.to_dict() if self.lowest_debt_period else None
            ),
            "periods": [period.to_dict() for period in self.periods],
        }
