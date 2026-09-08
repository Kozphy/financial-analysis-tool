"""Tests that lock Apple FY2025 IC memo headline numbers."""

from __future__ import annotations

import pytest

from financial_analysis_tool.case_study import (
    CompanySnapshot,
    dcf_sensitivity,
    project_from_growth_path,
    run_dcf_case,
)
from financial_analysis_tool.valuation import implied_equity_value_from_multiple

# Explicit path used in case_studies/apple_fy2025.md
APPLE_GROWTH_RATES = [0.07, 0.06, 0.05, 0.045, 0.04]


def apple_snapshot() -> CompanySnapshot:
    return CompanySnapshot(
        revenue=416_161.0,
        net_income=112_010.0,
        cash_from_operations=111_482.0,
        capital_expenditures=12_715.0,
        cash_and_securities=132_420.0,
        debt=98_657.0,
        shares_outstanding=14_773.26,
    )


def test_fcf_bridge_matches_ic_memo():
    """FCF proxy = CFO − capex = 98,767."""
    snapshot = apple_snapshot()
    assert snapshot.cash_from_operations - snapshot.capital_expenditures == pytest.approx(
        98_767.0
    )
    assert snapshot.free_cash_flow_proxy == pytest.approx(98_767.0)


def test_net_debt_bridge_matches_ic_memo():
    """Net debt = debt − cash/securities = −33,763 (net cash)."""
    snapshot = apple_snapshot()
    assert snapshot.debt - snapshot.cash_and_securities == pytest.approx(-33_763.0)
    assert snapshot.net_debt == pytest.approx(-33_763.0)


def test_explicit_fcf_growth_path_matches_ic_memo():
    projected = project_from_growth_path(
        apple_snapshot().free_cash_flow_proxy,
        APPLE_GROWTH_RATES,
    )
    assert projected == pytest.approx(
        [105_680.69, 112_021.53, 117_622.61, 122_915.63, 127_832.25],
        rel=1e-6,
    )


def test_base_case_dcf_reproduces_ic_memo():
    result = run_dcf_case(
        apple_snapshot(),
        growth_rates=APPLE_GROWTH_RATES,
        wacc=0.08,
        terminal_growth_rate=0.025,
    )
    assert result.implied_value_per_share == pytest.approx(143.4855, rel=1e-4)
    assert round(result.implied_value_per_share, 2) == 143.49
    # USD millions in model units; memo presents EV as $2,085.99B
    assert result.enterprise_value == pytest.approx(2_085_985.3, rel=1e-4)
    assert round(result.enterprise_value / 1_000, 2) == 2085.99
    assert round(result.equity_value / 1_000, 2) == 2119.75


def test_downside_and_upside_sensitivity_corners_match_ic_memo():
    snapshot = apple_snapshot()
    downside = run_dcf_case(
        snapshot,
        growth_rates=APPLE_GROWTH_RATES,
        wacc=0.09,
        terminal_growth_rate=0.02,
    )
    upside = run_dcf_case(
        snapshot,
        growth_rates=APPLE_GROWTH_RATES,
        wacc=0.07,
        terminal_growth_rate=0.03,
    )
    assert round(downside.implied_value_per_share, 2) == 114.84
    assert round(upside.implied_value_per_share, 2) == 193.47


def test_sensitivity_table_corners_match_ic_memo():
    table = dcf_sensitivity(
        apple_snapshot(),
        growth_rates=APPLE_GROWTH_RATES,
        wacc_values=[0.07, 0.075, 0.08, 0.085, 0.09],
        terminal_growth_values=[0.02, 0.025, 0.03],
    )
    expected = {
        0.07: {0.02: 160.47, 0.025: 175.14, 0.03: 193.47},
        0.075: {0.02: 145.95, 0.025: 157.73, 0.03: 172.13},
        0.08: {0.02: 133.85, 0.025: 143.49, 0.03: 155.05},
        0.085: {0.02: 123.61, 0.025: 131.62, 0.03: 141.08},
        0.09: {0.02: 114.84, 0.025: 121.58, 0.03: 129.44},
    }
    for wacc, row in expected.items():
        for terminal_growth, value in row.items():
            assert round(table[wacc][terminal_growth], 2) == value

    assert table[0.075][0.025] > table[0.08][0.025] > table[0.085][0.025]


def test_illustrative_fcf_comps_placeholder_matches_ic_memo():
    snapshot = apple_snapshot()
    for multiple, expected_ps in ((18.0, 122.62), (22.0, 149.37), (26.0, 176.11)):
        equity = implied_equity_value_from_multiple(
            snapshot.free_cash_flow_proxy,
            multiple,
            snapshot.net_debt,
        )
        assert round(equity / snapshot.shares_outstanding, 2) == expected_ps


def test_empty_growth_path_is_rejected():
    with pytest.raises(ValueError):
        project_from_growth_path(100.0, [])
