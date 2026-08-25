from __future__ import annotations

from dataclasses import dataclass

from models.vehicle import (
    DemandLevel,
    Vehicle,
    VehicleLocation,
)


@dataclass
class LocationSignal:
    location: VehicleLocation
    demand_score: float
    supply_pressure: float
    expected_days_to_sale: int
    expected_price_index: float


@dataclass
class TransferRecommendation:
    vehicle_id: str
    current_location: VehicleLocation
    recommended_location: VehicleLocation

    current_score: float
    recommended_score: float

    estimated_transfer_cost: float
    estimated_days_saved: int
    estimated_holding_cost_saved: float
    estimated_price_uplift: float
    estimated_net_impact: float

    reason: str
    confidence: float


DEMAND_SCORE = {
    DemandLevel.VERY_LOW: 20,
    DemandLevel.LOW: 35,
    DemandLevel.MEDIUM: 55,
    DemandLevel.HIGH: 75,
    DemandLevel.VERY_HIGH: 90,
}


LOCATION_PROFILES = {
    VehicleLocation.MELBOURNE: LocationSignal(
        location=VehicleLocation.MELBOURNE,
        demand_score=72,
        supply_pressure=68,
        expected_days_to_sale=31,
        expected_price_index=1.00,
    ),
    VehicleLocation.SYDNEY: LocationSignal(
        location=VehicleLocation.SYDNEY,
        demand_score=80,
        supply_pressure=76,
        expected_days_to_sale=28,
        expected_price_index=1.03,
    ),
    VehicleLocation.BRISBANE: LocationSignal(
        location=VehicleLocation.BRISBANE,
        demand_score=77,
        supply_pressure=58,
        expected_days_to_sale=25,
        expected_price_index=1.02,
    ),
    VehicleLocation.PERTH: LocationSignal(
        location=VehicleLocation.PERTH,
        demand_score=65,
        supply_pressure=48,
        expected_days_to_sale=34,
        expected_price_index=1.01,
    ),
    VehicleLocation.ADELAIDE: LocationSignal(
        location=VehicleLocation.ADELAIDE,
        demand_score=60,
        supply_pressure=46,
        expected_days_to_sale=36,
        expected_price_index=0.98,
    ),
}


TRANSFER_COSTS = {
    (VehicleLocation.MELBOURNE, VehicleLocation.SYDNEY): 650,
    (VehicleLocation.MELBOURNE, VehicleLocation.BRISBANE): 950,
    (VehicleLocation.MELBOURNE, VehicleLocation.ADELAIDE): 600,
    (VehicleLocation.MELBOURNE, VehicleLocation.PERTH): 1500,

    (VehicleLocation.SYDNEY, VehicleLocation.MELBOURNE): 650,
    (VehicleLocation.SYDNEY, VehicleLocation.BRISBANE): 750,
    (VehicleLocation.SYDNEY, VehicleLocation.ADELAIDE): 900,
    (VehicleLocation.SYDNEY, VehicleLocation.PERTH): 1600,

    (VehicleLocation.BRISBANE, VehicleLocation.SYDNEY): 750,
    (VehicleLocation.BRISBANE, VehicleLocation.MELBOURNE): 950,
    (VehicleLocation.BRISBANE, VehicleLocation.ADELAIDE): 1200,
    (VehicleLocation.BRISBANE, VehicleLocation.PERTH): 1800,

    (VehicleLocation.ADELAIDE, VehicleLocation.MELBOURNE): 600,
    (VehicleLocation.ADELAIDE, VehicleLocation.SYDNEY): 900,
    (VehicleLocation.ADELAIDE, VehicleLocation.BRISBANE): 1200,
    (VehicleLocation.ADELAIDE, VehicleLocation.PERTH): 1400,

    (VehicleLocation.PERTH, VehicleLocation.MELBOURNE): 1500,
    (VehicleLocation.PERTH, VehicleLocation.SYDNEY): 1600,
    (VehicleLocation.PERTH, VehicleLocation.BRISBANE): 1800,
    (VehicleLocation.PERTH, VehicleLocation.ADELAIDE): 1400,
}


def market_score(
    signal: LocationSignal,
) -> float:
    return (
        signal.demand_score * 0.65
        + (100 - signal.supply_pressure) * 0.35
    )


def recommend_transfer(
    vehicle: Vehicle,
) -> TransferRecommendation | None:

    current_location = vehicle.inventory.current_location

    current_signal = LOCATION_PROFILES[
        current_location
    ]

    current_score = market_score(
        current_signal
    )

    best_recommendation = None

    for location, signal in LOCATION_PROFILES.items():

        if location == current_location:
            continue

        destination_score = market_score(signal)

        score_improvement = (
            destination_score - current_score
        )

        if score_improvement < 5:
            continue

        transfer_cost = TRANSFER_COSTS.get(
            (current_location, location)
        )

        if transfer_cost is None:
            continue

        days_saved = max(
            0,
            vehicle.demand.estimated_days_to_sale
            - signal.expected_days_to_sale,
        )

        holding_cost_saved = (
            days_saved
            * vehicle.inventory.storage_cost_per_day
        )

        price_uplift = max(
            0,
            vehicle.pricing.current_list_price
            * (
                signal.expected_price_index
                - current_signal.expected_price_index
            ),
        )

        net_impact = (
            holding_cost_saved
            + price_uplift
            - transfer_cost
        )

        if net_impact <= 0:
            continue

        recommendation = TransferRecommendation(
            vehicle_id=vehicle.identity.vehicle_id,
            current_location=current_location,
            recommended_location=location,
            current_score=round(current_score, 2),
            recommended_score=round(
                destination_score,
                2,
            ),
            estimated_transfer_cost=round(
                transfer_cost,
                2,
            ),
            estimated_days_saved=days_saved,
            estimated_holding_cost_saved=round(
                holding_cost_saved,
                2,
            ),
            estimated_price_uplift=round(
                price_uplift,
                2,
            ),
            estimated_net_impact=round(
                net_impact,
                2,
            ),
            reason=(
                f"{location.value} offers stronger modeled "
                f"demand/supply economics than "
                f"{current_location.value}."
            ),
            confidence=0.68,
        )

        if (
            best_recommendation is None
            or recommendation.estimated_net_impact
            > best_recommendation.estimated_net_impact
        ):
            best_recommendation = recommendation

    return best_recommendation
