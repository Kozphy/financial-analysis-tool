"""Core corporate valuation utilities.

The functions in this module are intentionally dependency-light so they can be
used from notebooks, APIs, or batch pipelines without requiring pandas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DCFResult:
    enterprise_value: float
    equity_value: float
    terminal_value: float
    present_value_terminal: float
    present_value_fcf: float
    implied_value_per_share: float | None


def present_value(cash_flow: float, discount_rate: float, period: int) -> float:
    """Discount a future cash flow to present value."""
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -100%")
    if period < 1:
        raise ValueError("period must be >= 1")
    return cash_flow / ((1.0 + discount_rate) ** period)


def terminal_value_gordon(
    final_year_fcf: float,
    terminal_growth_rate: float,
    discount_rate: float,
) -> float:
    """Calculate terminal value using the Gordon Growth method."""
    if discount_rate <= terminal_growth_rate:
        raise ValueError("discount_rate must be greater than terminal_growth_rate")
    return final_year_fcf * (1.0 + terminal_growth_rate) / (
        discount_rate - terminal_growth_rate
    )


def dcf_valuation(
    projected_fcf: Iterable[float],
    discount_rate: float,
    terminal_growth_rate: float,
    net_debt: float = 0.0,
    shares_outstanding: float | None = None,
) -> DCFResult:
    """Value a company from projected free cash flow.

    Args:
        projected_fcf: Year 1..N unlevered free cash flow values.
        discount_rate: WACC or other appropriate discount rate, expressed as a decimal.
        terminal_growth_rate: Long-run perpetual FCF growth rate.
        net_debt: Debt minus cash. Subtracted from enterprise value.
        shares_outstanding: Optional diluted share count for implied value per share.
    """
    cash_flows = [float(value) for value in projected_fcf]
    if not cash_flows:
        raise ValueError("projected_fcf must contain at least one value")
    if shares_outstanding is not None and shares_outstanding <= 0:
        raise ValueError("shares_outstanding must be positive")

    pv_fcf = sum(
        present_value(cash_flow, discount_rate, period)
        for period, cash_flow in enumerate(cash_flows, start=1)
    )
    terminal = terminal_value_gordon(
        cash_flows[-1], terminal_growth_rate, discount_rate
    )
    pv_terminal = terminal / ((1.0 + discount_rate) ** len(cash_flows))
    enterprise_value = pv_fcf + pv_terminal
    equity_value = enterprise_value - net_debt
    implied_value_per_share = (
        equity_value / shares_outstanding if shares_outstanding is not None else None
    )

    return DCFResult(
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        terminal_value=terminal,
        present_value_terminal=pv_terminal,
        present_value_fcf=pv_fcf,
        implied_value_per_share=implied_value_per_share,
    )


def implied_equity_value_from_multiple(
    metric: float,
    multiple: float,
    net_debt: float = 0.0,
) -> float:
    """Simple comparable-company valuation using an enterprise-value multiple."""
    if multiple < 0:
        raise ValueError("multiple must be non-negative")
    enterprise_value = metric * multiple
    return enterprise_value - net_debt
