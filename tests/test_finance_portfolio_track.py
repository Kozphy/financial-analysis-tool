import math

import pytest

from financial_analysis_tool.forecasting import (
    cagr,
    forecast_by_growth,
    scenario_forecast,
)
from financial_analysis_tool.portfolio_risk import (
    max_drawdown,
    simple_returns,
)
from financial_analysis_tool.valuation import (
    dcf_valuation,
    terminal_value_gordon,
)


def test_cagr():
    assert cagr(100, 121, 2) == pytest.approx(0.10)


def test_growth_forecast():
    points = forecast_by_growth(100, 0.10, 2)
    assert [p.value for p in points] == pytest.approx([110, 121])


def test_scenario_forecast_has_three_paths():
    result = scenario_forecast(100, 0.05, 0.10, -0.05, 3)
    assert set(result) == {"base", "bull", "bear"}
    assert len(result["base"]) == 3


def test_terminal_value_requires_spread():
    with pytest.raises(ValueError):
        terminal_value_gordon(100, 0.05, 0.05)


def test_dcf_returns_enterprise_and_equity_value():
    result = dcf_valuation(
        projected_fcf=[100, 110, 120],
        discount_rate=0.10,
        terminal_growth_rate=0.03,
        net_debt=200,
        shares_outstanding=100,
    )
    assert result.enterprise_value > result.equity_value
    assert result.implied_value_per_share == pytest.approx(result.equity_value / 100)


def test_simple_returns_and_drawdown():
    returns = simple_returns([100, 110, 99])
    assert returns == pytest.approx([0.10, -0.10])
    assert max_drawdown([100, 120, 90]) == pytest.approx(0.25)
