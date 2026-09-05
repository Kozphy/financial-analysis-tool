import pytest

from financial_analysis_tool.case_study import (
    CompanySnapshot,
    dcf_sensitivity,
    project_from_growth_path,
    run_dcf_case,
)


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


def test_snapshot_finance_bridges():
    snapshot = apple_snapshot()
    assert snapshot.free_cash_flow_proxy == pytest.approx(98_767.0)
    assert snapshot.net_debt == pytest.approx(-33_763.0)


def test_project_growth_path():
    result = project_from_growth_path(100.0, [0.10, 0.05])
    assert result == pytest.approx([110.0, 115.5])


def test_base_case_dcf_reproduces_case_study():
    result = run_dcf_case(
        apple_snapshot(),
        growth_rates=[0.07, 0.06, 0.05, 0.045, 0.04],
        wacc=0.08,
        terminal_growth_rate=0.025,
    )
    assert result.implied_value_per_share == pytest.approx(143.4855, rel=1e-4)
    assert result.enterprise_value == pytest.approx(2_085.9853, rel=1e-4)


def test_sensitivity_is_ordered_for_discount_rate():
    table = dcf_sensitivity(
        apple_snapshot(),
        growth_rates=[0.07, 0.06, 0.05, 0.045, 0.04],
        wacc_values=[0.075, 0.08, 0.085],
        terminal_growth_values=[0.025],
    )
    assert table[0.075][0.025] > table[0.08][0.025] > table[0.085][0.025]


def test_empty_growth_path_is_rejected():
    with pytest.raises(ValueError):
        project_from_growth_path(100.0, [])
