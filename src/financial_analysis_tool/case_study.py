"""Reproducible finance case-study helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .valuation import DCFResult, dcf_valuation


@dataclass(frozen=True)
class CompanySnapshot:
    revenue: float
    net_income: float
    cash_from_operations: float
    capital_expenditures: float
    cash_and_securities: float
    debt: float
    shares_outstanding: float

    @property
    def free_cash_flow_proxy(self) -> float:
        """Simplified FCF proxy: operating cash flow minus capex."""
        return self.cash_from_operations - self.capital_expenditures

    @property
    def net_debt(self) -> float:
        """Debt minus cash and marketable securities; negative means net cash."""
        return self.debt - self.cash_and_securities


def project_from_growth_path(base_value: float, growth_rates: Iterable[float]) -> list[float]:
    """Project a metric by applying an explicit annual growth path."""
    value = float(base_value)
    projected: list[float] = []
    for growth in growth_rates:
        if growth <= -1:
            raise ValueError("growth rates must be greater than -100%")
        value *= 1.0 + float(growth)
        projected.append(value)
    if not projected:
        raise ValueError("growth_rates must contain at least one rate")
    return projected


def run_dcf_case(
    snapshot: CompanySnapshot,
    growth_rates: Iterable[float],
    wacc: float,
    terminal_growth_rate: float,
) -> DCFResult:
    """Run a simple FCF-based DCF from a company snapshot."""
    projected_fcf = project_from_growth_path(snapshot.free_cash_flow_proxy, growth_rates)
    return dcf_valuation(
        projected_fcf=projected_fcf,
        discount_rate=wacc,
        terminal_growth_rate=terminal_growth_rate,
        net_debt=snapshot.net_debt,
        shares_outstanding=snapshot.shares_outstanding,
    )


def dcf_sensitivity(
    snapshot: CompanySnapshot,
    growth_rates: Iterable[float],
    wacc_values: Iterable[float],
    terminal_growth_values: Iterable[float],
) -> dict[float, dict[float, float]]:
    """Return implied per-share values across WACC and terminal-growth assumptions."""
    result: dict[float, dict[float, float]] = {}
    for wacc in wacc_values:
        row: dict[float, float] = {}
        for terminal_growth in terminal_growth_values:
            valuation = run_dcf_case(snapshot, growth_rates, wacc, terminal_growth)
            if valuation.implied_value_per_share is None:
                raise RuntimeError("shares_outstanding is required for sensitivity output")
            row[terminal_growth] = valuation.implied_value_per_share
        result[wacc] = row
    return result
