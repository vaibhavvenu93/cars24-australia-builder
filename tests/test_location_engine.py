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
from engines.location_engine import (
    recommend_transfer,
)


def build_vehicle() -> Vehicle:
    return Vehicle(
        identity=VehicleIdentity(
            vehicle_id="AU-LOC-001",
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
            level=DemandLevel.LOW,
            listing_views_7d=60,
            enquiries_7d=3,
            test_drives_7d=1,
            local_inventory_count=35,
            estimated_days_to_sale=55,
        ),
        inventory=Inventory(
            current_location=VehicleLocation.MELBOURNE,
            days_in_inventory=52,
            days_since_acquisition=58,
            storage_cost_per_day=14,
        ),
        lifecycle_risk=LifecycleRisk(
            warranty_probability=0.08,
            expected_warranty_cost=900,
            return_probability=0.03,
            expected_return_cost=1800,
            markdown_probability=0.25,
            expected_markdown_cost=1500,
        ),
    )


def test_transfer_recommendation_can_be_generated():
    vehicle = build_vehicle()

    recommendation = recommend_transfer(vehicle)

    assert recommendation is not None
    assert (
        recommendation.current_location
        == VehicleLocation.MELBOURNE
    )
    assert (
        recommendation.recommended_location
        != VehicleLocation.MELBOURNE
    )


def test_transfer_must_create_positive_net_impact():
    vehicle = build_vehicle()

    recommendation = recommend_transfer(vehicle)

    assert recommendation is not None
    assert recommendation.estimated_net_impact > 0


def test_transfer_should_save_days():
    vehicle = build_vehicle()

    recommendation = recommend_transfer(vehicle)

    assert recommendation is not None
    assert recommendation.estimated_days_saved > 0


def test_transfer_reason_is_explainable():
    vehicle = build_vehicle()

    recommendation = recommend_transfer(vehicle)

    assert recommendation is not None
    assert recommendation.reason
    assert len(recommendation.reason) > 20
