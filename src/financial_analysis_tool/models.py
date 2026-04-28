"""Data models for raw financial statements and derived analysis output.

These dataclasses define the internal financial contracts used across loaders,
metrics, pipelines, reports, charts, and the API service layer. They keep the
core workflow independent of FastAPI and pandas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True, slots=True)
class FinancialStatementRecord:
    """Represents one reporting period from the financial statement CSV.

    Attributes:
        period: Reporting period label in ``YYYY-Qn`` format.
        revenue: Top-line revenue for the period.
        cost_of_revenue: Direct cost associated with revenue.
        operating_expenses: Operating expenses after gross profit.
        net_income: Bottom-line income.
        current_assets: Short-term assets used for liquidity analysis.
        current_liabilities: Short-term liabilities used for liquidity analysis.
        total_assets: Total asset base used for leverage analysis.
        total_liabilities: Total liabilities used for leverage analysis.
    """

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
        """Convert the record to a JSON-serializable dictionary.

        Returns:
            JsonDict: Plain dictionary representation of the record.
        """
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PeriodMetrics:
    """Stores calculated profitability, liquidity, and leverage metrics.

    Attributes:
        period: Reporting period label.
        revenue: Revenue copied from the source record.
        gross_profit: Revenue less cost of revenue.
        operating_income: Gross profit less operating expenses.
        net_income: Net income copied from the source record.
        revenue_growth: Period-over-period revenue growth.
        gross_margin: Gross profit divided by revenue.
        operating_margin: Operating income divided by revenue.
        net_margin: Net income divided by revenue.
        current_ratio: Current assets divided by current liabilities.
        debt_ratio: Total liabilities divided by total assets.
    """

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
        """Convert period metrics to a JSON-serializable dictionary.

        Returns:
            JsonDict: Plain dictionary representation of the metrics.
        """
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AnalysisSummary:
    """Aggregates headline financial outputs for reports, charts, and APIs.

    Attributes:
        company_name: Company label used in presentation surfaces.
        periods: All calculated period metrics.
        latest_period: Most recent period used for current-state review.
        overall_revenue_growth: Growth from first to latest period.
        average_gross_margin: Average gross margin across available periods.
        average_operating_margin: Average operating margin across periods.
        average_net_margin: Average net margin across periods.
        latest_current_ratio: Latest liquidity ratio.
        latest_debt_ratio: Latest leverage ratio.
        best_growth_period: Period with the strongest revenue growth.
        strongest_liquidity_period: Period with the highest current ratio.
        lowest_debt_period: Period with the lowest debt ratio.
    """

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
        """Convert the nested summary to JSON-serializable dictionaries.

        Returns:
            JsonDict: Summary payload used by reporting and API layers.
        """
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
