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
from engines.opportunity_engine import (
    ActionType,
    Priority,
    evaluate_vehicle,
)


def build_base_vehicle() -> Vehicle:
    return Vehicle(
        identity=VehicleIdentity(
            vehicle_id="AU-OPP-001",
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


def actions(vehicle: Vehicle) -> set[ActionType]:
    return {
        opportunity.action
        for opportunity in evaluate_vehicle(vehicle)
    }


def test_healthy_vehicle_does_not_trigger_critical_action():
    vehicle = build_base_vehicle()

    opportunities = evaluate_vehicle(vehicle)

    assert all(
        opportunity.priority != Priority.CRITICAL
        for opportunity in opportunities
    )


def test_ageing_overpriced_vehicle_triggers_reprice():
    vehicle = build_base_vehicle()

    vehicle.inventory.days_in_inventory = 55
    vehicle.inventory.days_since_acquisition = 60
    vehicle.demand.level = DemandLevel.LOW

    vehicle.pricing.current_list_price = 36500
    vehicle.pricing.competitor_median_price = 34500

    assert ActionType.REPRICE in actions(vehicle)


def test_ageing_competitively_priced_vehicle_triggers_transfer_review():
    vehicle = build_base_vehicle()

    vehicle.inventory.days_in_inventory = 60
    vehicle.inventory.days_since_acquisition = 65
    vehicle.demand.level = DemandLevel.LOW

    vehicle.pricing.current_list_price = 34000
    vehicle.pricing.competitor_median_price = 34500

    assert ActionType.TRANSFER_REVIEW in actions(vehicle)


def test_very_old_inventory_triggers_wholesale_review():
    vehicle = build_base_vehicle()

    vehicle.inventory.days_in_inventory = 95
    vehicle.inventory.days_since_acquisition = 100

    assert ActionType.WHOLESALE_REVIEW in actions(vehicle)


def test_high_roi_refurbishment_is_prioritised():
    vehicle = build_base_vehicle()

    vehicle.refurbishment.estimated_cost = 1000
    vehicle.refurbishment.expected_price_uplift = 1800

    assert (
        ActionType.PRIORITISE_REFURBISHMENT
        in actions(vehicle)
    )


def test_low_roi_cosmetic_refurbishment_is_flagged():
    vehicle = build_base_vehicle()

    vehicle.refurbishment.estimated_cost = 1500
    vehicle.refurbishment.expected_price_uplift = 500
    vehicle.refurbishment.safety_work_required = False

    assert (
        ActionType.SKIP_LOW_ROI_REFURBISHMENT
        in actions(vehicle)
    )


def test_safety_work_is_not_skipped_even_if_roi_is_low():
    vehicle = build_base_vehicle()

    vehicle.refurbishment.estimated_cost = 1500
    vehicle.refurbishment.expected_price_uplift = 500
    vehicle.refurbishment.safety_work_required = True

    assert (
        ActionType.SKIP_LOW_ROI_REFURBISHMENT
        not in actions(vehicle)
    )


def test_high_lifecycle_risk_triggers_review():
    vehicle = build_base_vehicle()

    vehicle.condition.mechanical_risk = RiskLevel.HIGH
    vehicle.lifecycle_risk.warranty_probability = 0.35

    assert ActionType.RISK_REVIEW in actions(vehicle)


def test_negative_expected_contribution_triggers_acquisition_review():
    vehicle = build_base_vehicle()

    vehicle.acquisition.acquisition_price = 38000
    vehicle.pricing.current_list_price = 34000
    vehicle.pricing.expected_market_price = 34000

    assert (
        ActionType.ACQUISITION_REVIEW
        in actions(vehicle)
    )


def test_no_trigger_returns_hold():
    vehicle = build_base_vehicle()

    vehicle.refurbishment.estimated_cost = 0
    vehicle.refurbishment.expected_price_uplift = 0

    opportunities = evaluate_vehicle(vehicle)

    assert len(opportunities) == 1
    assert opportunities[0].action == ActionType.HOLD
    assert opportunities[0].priority == Priority.LOW
