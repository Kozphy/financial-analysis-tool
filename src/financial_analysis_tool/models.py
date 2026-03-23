from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class FinancialRecord:
    period: str
    revenue: float
    cost_of_revenue: float
    operating_expenses: float
    net_income: float


@dataclass(frozen=True, slots=True)
class PeriodAnalysis:
    period: str
    revenue: float
    gross_profit: float
    operating_income: float
    net_income: float
    revenue_growth: float | None
    gross_margin: float
    operating_margin: float
    net_margin: float

    def to_dict(self) -> dict[str, float | str | None]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerformanceSummary:
    periods: list[PeriodAnalysis]
    latest_period: PeriodAnalysis
    overall_revenue_growth: float | None
    average_revenue_growth: float | None
    best_growth_period: PeriodAnalysis | None
    highest_net_margin_period: PeriodAnalysis | None

    def to_dict(self) -> dict[str, object]:
        return {
            "latest_period": self.latest_period.to_dict(),
            "overall_revenue_growth": self.overall_revenue_growth,
            "average_revenue_growth": self.average_revenue_growth,
            "best_growth_period": (
                self.best_growth_period.to_dict() if self.best_growth_period else None
            ),
            "highest_net_margin_period": (
                self.highest_net_margin_period.to_dict()
                if self.highest_net_margin_period
                else None
            ),
            "periods": [period.to_dict() for period in self.periods],
        }
