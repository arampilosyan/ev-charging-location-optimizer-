import pytest
from src.finance import calculate_financials


def test_financial_calculation():
    result = calculate_financials(
        charger_type="AC",
        sessions_per_day=3,
        kwh_per_session=20,
        selling_price=120,
        electricity_cost=60,
        monthly_fixed_cost=150_000,
        installation_cost=500_000,
    )
    assert result["hardware_cost_amd"] == 650_000
    assert result["initial_investment_amd"] == 1_150_000
    assert result["monthly_energy_kwh"] == 1800
    assert result["monthly_revenue_amd"] == 216_000
    assert result["monthly_energy_cost_amd"] == 108_000
    assert result["monthly_profit_amd"] == -42_000
    assert result["payback_months"] is None


def test_unknown_charger_type_is_rejected():
    with pytest.raises(ValueError):
        calculate_financials("XYZ", 3, 20, 120, 60, 150_000, 500_000)
