"""Simple configurable charging-station financial scenario model."""
HARDWARE_COSTS_AMD = {
    # Illustrative defaults only. Replace with written supplier quotations.
    "AC": 650_000,
    "DC": 4_200_000,
}


def calculate_financials(
    charger_type,
    sessions_per_day,
    kwh_per_session,
    selling_price,
    electricity_cost,
    monthly_fixed_cost,
    installation_cost,
):
    """Calculate simple monthly operating estimate and initial investment."""
    if charger_type not in HARDWARE_COSTS_AMD:
        raise ValueError("charger_type must be 'AC' or 'DC'")
    numeric_values = {
        "sessions_per_day": sessions_per_day,
        "kwh_per_session": kwh_per_session,
        "selling_price": selling_price,
        "electricity_cost": electricity_cost,
        "monthly_fixed_cost": monthly_fixed_cost,
        "installation_cost": installation_cost,
    }
    if any(float(value) < 0 for value in numeric_values.values()):
        raise ValueError("Financial inputs must be non-negative")
    if float(kwh_per_session) <= 0:
        raise ValueError("kwh_per_session must be greater than zero")

    hardware_cost = HARDWARE_COSTS_AMD[charger_type]
    investment = hardware_cost + float(installation_cost)
    monthly_energy = float(sessions_per_day) * float(kwh_per_session) * 30
    revenue = monthly_energy * float(selling_price)
    energy_cost = monthly_energy * float(electricity_cost)
    profit = revenue - energy_cost - float(monthly_fixed_cost)
    payback = investment / profit if profit > 0 else None

    return {
        "hardware_cost_amd": hardware_cost,
        "initial_investment_amd": investment,
        "monthly_energy_kwh": monthly_energy,
        "monthly_revenue_amd": revenue,
        "monthly_energy_cost_amd": energy_cost,
        "monthly_profit_amd": profit,
        "payback_months": payback,
    }
