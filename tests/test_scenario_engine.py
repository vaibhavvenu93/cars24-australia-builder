from engines.scenario_engine import (
    ScenarioInputs,
    apply_scenario,
)
from models.vehicle import (
    Acquisition,
    AcquisitionSource,
    Condition,
    ConditionGrade,
    DemandLevel,
    DemandSignals,
    Inventory,
    LifecycleRisk,
    Pricing,
    Refurbishment,
    RiskLevel,
    Vehicle,
    VehicleIdentity,
    VehicleLocation,
    VehicleStatus,
)


def make_vehicle(
    acquisition_price: float = 20000,
    refurbishment_cost: float = 1000,
    days_in_inventory: int = 60,
    markdown_probability: float = 0.10,
    warranty_probability: float = 0.05,
) -> Vehicle:
    return Vehicle(
        identity=VehicleIdentity(
            vehicle_id="TEST-001",
            make="Toyota",
            model="Corolla",
            variant="Ascent Sport",
            year=2021,
            kilometres=50000,
            fuel_type="Petrol",
            transmission="Automatic",
            body_type="Hatchback",
        ),
        status=VehicleStatus.LISTED,
        acquisition=Acquisition(
            source=AcquisitionSource.DIRECT_SELLER,
            initial_valuation=22000,
            acquisition_price=acquisition_price,
            transport_to_hub_cost=300,
        ),
        condition=Condition(
            grade=ConditionGrade.GOOD,
            inspection_score=88,
            mechanical_risk=RiskLevel.LOW,
            cosmetic_risk=RiskLevel.MEDIUM,
            service_history_complete=True,
            ppsr_clear=True,
        ),
        refurbishment=Refurbishment(
            estimated_cost=refurbishment_cost,
            actual_cost=refurbishment_cost,
            estimated_hours=6,
            actual_hours=6,
            expected_price_uplift=1500,
            safety_work_required=False,
            cosmetic_work_required=True,
        ),
        pricing=Pricing(
            expected_market_price=25000,
            initial_list_price=25500,
            current_list_price=25000,
            competitor_median_price=24800,
        ),
        demand=DemandSignals(
            level=DemandLevel.MEDIUM,
            listing_views_7d=100,
            enquiries_7d=8,
            test_drives_7d=2,
            local_inventory_count=20,
            estimated_days_to_sale=20,
        ),
        inventory=Inventory(
            current_location=VehicleLocation.SYDNEY,
            days_in_inventory=days_in_inventory,
            days_since_acquisition=days_in_inventory + 5,
            storage_cost_per_day=10,
        ),
        lifecycle_risk=LifecycleRisk(
            markdown_probability=markdown_probability,
            expected_markdown_cost=1000,
            warranty_probability=warranty_probability,
            expected_warranty_cost=1500,
            return_probability=0.03,
            expected_return_cost=1200,
        ),
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
