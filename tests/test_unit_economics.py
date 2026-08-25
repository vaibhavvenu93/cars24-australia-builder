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
from economics.unit_economics import (
    calculate_expected_risk_cost,
    calculate_invested_capital,
    calculate_refurbishment_roi,
    calculate_unit_economics,
)


def build_vehicle() -> Vehicle:
    return Vehicle(
        identity=VehicleIdentity(
            vehicle_id="AU-TEST-001",
            make="Toyota",
            model="RAV4",
            variant="GX",
            year=2022,
            kilometres=32000,
            fuel_type="Hybrid",
            transmission="Automatic",
            body_type="SUV",
        ),
        status=VehicleStatus.LISTED,
        acquisition=Acquisition(
            source=AcquisitionSource.DIRECT_SELLER,
            initial_valuation=30000,
            acquisition_price=28500,
            transport_to_hub_cost=400,
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
            estimated_cost=1200,
            expected_price_uplift=1800,
            estimated_hours=8,
            cosmetic_work_required=True,
        ),
        pricing=Pricing(
            expected_market_price=34900,
            initial_list_price=35400,
            current_list_price=34900,
            competitor_median_price=34750,
        ),
        demand=DemandSignals(
            level=DemandLevel.HIGH,
            listing_views_7d=180,
            enquiries_7d=14,
            test_drives_7d=5,
            local_inventory_count=22,
            estimated_days_to_sale=28,
        ),
        inventory=Inventory(
            current_location=VehicleLocation.MELBOURNE,
            days_in_inventory=18,
            days_since_acquisition=23,
            storage_cost_per_day=12,
        ),
        lifecycle_risk=LifecycleRisk(
            warranty_probability=0.08,
            expected_warranty_cost=900,
            return_probability=0.03,
            expected_return_cost=1800,
            markdown_probability=0.20,
            expected_markdown_cost=1200,
        ),
    )


def test_invested_capital():
    vehicle = build_vehicle()

    capital = calculate_invested_capital(vehicle)

    expected = (
        28500
        + 400
        + 1200
        + (23 * 12)
    )

    assert capital == expected


def test_expected_risk_cost():
    vehicle = build_vehicle()

    risk_cost = calculate_expected_risk_cost(vehicle)

    expected = (
        (0.08 * 900)
        + (0.03 * 1800)
        + (0.20 * 1200)
    )

    assert risk_cost == expected


def test_refurbishment_roi():
    vehicle = build_vehicle()

    roi = calculate_refurbishment_roi(vehicle)

    # ($1,800 uplift - $1,200 cost) / $1,200
    assert roi == 0.5


def test_unit_economics_are_positive():
    vehicle = build_vehicle()

    economics = calculate_unit_economics(vehicle)

    assert economics.invested_capital > 0
    assert economics.expected_sale_price == 34900
    assert economics.expected_contribution > 0
    assert economics.capital_days == 23
    assert economics.annualised_inventory_turns > 0


def test_longer_capital_cycle_reduces_efficiency():
    fast_vehicle = build_vehicle()
    slow_vehicle = build_vehicle()

    fast_vehicle.inventory.days_since_acquisition = 20
    slow_vehicle.inventory.days_since_acquisition = 80

    fast = calculate_unit_economics(fast_vehicle)
    slow = calculate_unit_economics(slow_vehicle)

    assert (
        fast.contribution_per_capital_day
        >
        slow.contribution_per_capital_day
    )


def test_higher_risk_reduces_expected_contribution():
    low_risk = build_vehicle()
    high_risk = build_vehicle()

    high_risk.lifecycle_risk.warranty_probability = 0.40
    high_risk.lifecycle_risk.return_probability = 0.15
    high_risk.lifecycle_risk.markdown_probability = 0.50

    low = calculate_unit_economics(low_risk)
    high = calculate_unit_economics(high_risk)

    assert high.expected_risk_cost > low.expected_risk_cost
    assert high.expected_contribution < low.expected_contribution


def test_lower_acquisition_price_improves_contribution():
    expensive_vehicle = build_vehicle()
    cheaper_vehicle = build_vehicle()

    expensive_vehicle.acquisition.acquisition_price = 30000
    cheaper_vehicle.acquisition.acquisition_price = 27000

    expensive = calculate_unit_economics(
        expensive_vehicle
    )
    cheaper = calculate_unit_economics(
        cheaper_vehicle
    )

    assert (
        cheaper.expected_contribution
        >
        expensive.expected_contribution
    )
 
