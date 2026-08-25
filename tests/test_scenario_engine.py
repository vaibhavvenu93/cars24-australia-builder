from engines.scenario_engine import (
    ScenarioInputs,
    apply_scenario,
)
from models.vehicle import Vehicle


def make_vehicle(
    acquisition_price: float = 20000,
    refurbishment_cost: float = 1000,
    days_in_inventory: int = 60,
    markdown_probability: float = 0.10,
    warranty_probability: float = 0.05,
) -> Vehicle:
    return Vehicle.model_validate(
        {
            "vehicle_id": "TEST-001",
            "make": "Toyota",
            "model": "Corolla",
            "year": 2021,
            "odometer_km": 50000,

            "acquisition": {
                "acquisition_price": acquisition_price,
                "auction_fees": 500,
                "transport_to_hub_cost": 300,
            },

            "refurbishment": {
                "estimated_cost": refurbishment_cost,
                "actual_cost": refurbishment_cost,
                "safety_cost": 300,
                "cosmetic_cost": 700,
                "estimated_days": 5,
                "actual_days": 5,
            },

            "pricing": {
                "current_list_price": 25000,
                "market_price_estimate": 25000,
                "original_list_price": 25000,
            },

            "inventory": {
                "current_location": "Sydney",
                "days_in_inventory": days_in_inventory,
                "days_since_acquisition": days_in_inventory + 5,
            },

            "demand": {
                "local_demand_score": 0.8,
                "estimated_days_to_sale": 20,
            },

            "lifecycle_risk": {
                "markdown_probability": markdown_probability,
                "expected_markdown_amount": 1000,
                "warranty_probability": warranty_probability,
                "expected_warranty_cost": 1500,
            },
        }
    )


def test_acquisition_improvement_releases_capital():
    vehicle = make_vehicle()

    result = apply_scenario(
        [vehicle],
        ScenarioInputs(
            acquisition_cost_reduction_pct=5,
        ),
    )

    assert result.capital_released > 0


def test_refurbishment_improvement_increases_contribution():
    vehicle = make_vehicle()

    result = apply_scenario(
        [vehicle],
        ScenarioInputs(
            refurbishment_cost_reduction_pct=20,
        ),
    )

    assert result.contribution_improvement > 0


def test_risk_reduction_reduces_expected_risk_cost():
    vehicle = make_vehicle()

    result = apply_scenario(
        [vehicle],
        ScenarioInputs(
            markdown_risk_reduction_pct=50,
            warranty_risk_reduction_pct=50,
        ),
    )

    assert (
        result.scenario_risk_cost
        < result.baseline_risk_cost
    )


def test_no_changes_produce_no_economic_change():
    vehicle = make_vehicle()

    result = apply_scenario(
        [vehicle],
        ScenarioInputs(),
    )

    assert result.capital_released == 0
    assert result.contribution_improvement == 0
    assert result.risk_cost_reduction == 0


def test_inventory_improvement_reduces_aged_capital():
    vehicle = make_vehicle(
        days_in_inventory=95,
    )

    result = apply_scenario(
        [vehicle],
        ScenarioInputs(
            inventory_days_reduction=10,
        ),
    )

    assert (
        result.scenario_90_plus_day_capital
        < result.baseline_90_plus_day_capital
    )
