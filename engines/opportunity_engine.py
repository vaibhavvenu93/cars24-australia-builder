from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from economics.unit_economics import (
    UnitEconomics,
    calculate_unit_economics,
)
from models.vehicle import DemandLevel, RiskLevel, Vehicle


class ActionType(str, Enum):
    HOLD = "HOLD"
    REPRICE = "REPRICE"
    PROMOTE = "PROMOTE"
    TRANSFER_REVIEW = "TRANSFER_REVIEW"
    WHOLESALE_REVIEW = "WHOLESALE_REVIEW"
    PRIORITISE_REFURBISHMENT = "PRIORITISE_REFURBISHMENT"
    SKIP_LOW_ROI_REFURBISHMENT = "SKIP_LOW_ROI_REFURBISHMENT"
    ACQUISITION_REVIEW = "ACQUISITION_REVIEW"
    RISK_REVIEW = "RISK_REVIEW"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Opportunity:
    vehicle_id: str
    action: ActionType
    priority: Priority
    reason: str
    estimated_impact: float
    confidence: float


def _price_gap(vehicle: Vehicle) -> float:
    """
    Positive value means the vehicle is listed above
    the local competitor median.
    """
    current_price = vehicle.pricing.current_list_price
    competitor_price = vehicle.pricing.competitor_median_price

    if current_price is None or competitor_price is None:
        return 0.0

    return current_price - competitor_price


def _high_lifecycle_risk(vehicle: Vehicle) -> bool:
    return (
        vehicle.condition.mechanical_risk
        in {RiskLevel.HIGH, RiskLevel.VERY_HIGH}
        or vehicle.lifecycle_risk.warranty_probability >= 0.25
        or vehicle.lifecycle_risk.return_probability >= 0.10
    )


def evaluate_vehicle(vehicle: Vehicle) -> list[Opportunity]:
    """
    Produce explainable intervention opportunities for one vehicle.

    This is deliberately rules-based for the first prototype.

    The goal is to make the decision logic:
    - inspectable
    - testable
    - easy to challenge
    - easy to replace with learned models later
    """

    economics: UnitEconomics = calculate_unit_economics(vehicle)

    opportunities: list[Opportunity] = []

    price_gap = _price_gap(vehicle)

    # 1. Ageing + weak demand + overpriced
    if (
        vehicle.inventory.days_in_inventory >= 45
        and vehicle.demand.level
        in {DemandLevel.LOW, DemandLevel.VERY_LOW}
        and price_gap > 0
    ):
        estimated_impact = min(
            price_gap,
            vehicle.lifecycle_risk.expected_markdown_cost,
        )

        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.REPRICE,
                priority=Priority.HIGH,
                reason=(
                    "Vehicle is ageing, demand is weak, and the "
                    "current list price is above the competitor median."
                ),
                estimated_impact=round(estimated_impact, 2),
                confidence=0.86,
            )
        )

    # 2. Ageing vehicle where price is already competitive
    if (
        vehicle.inventory.days_in_inventory >= 45
        and vehicle.demand.level
        in {DemandLevel.LOW, DemandLevel.VERY_LOW}
        and price_gap <= 0
    ):
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.TRANSFER_REVIEW,
                priority=Priority.HIGH,
                reason=(
                    "Vehicle is ageing despite competitive pricing. "
                    "Review whether another location has stronger demand."
                ),
                estimated_impact=round(
                    vehicle.inventory.storage_cost_per_day * 20,
                    2,
                ),
                confidence=0.72,
            )
        )

    # 3. Very old inventory becomes a capital-release problem
    if vehicle.inventory.days_in_inventory >= 90:
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.WHOLESALE_REVIEW,
                priority=Priority.CRITICAL,
                reason=(
                    "Vehicle has exceeded 90 inventory days. "
                    "Compare expected retail upside with immediate "
                    "capital release through wholesale."
                ),
                estimated_impact=round(
                    economics.invested_capital,
                    2,
                ),
                confidence=0.91,
            )
        )

    # 4. Attractive refurbishment
    if (
        vehicle.refurbishment.estimated_cost > 0
        and economics.refurbishment_roi >= 0.50
    ):
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.PRIORITISE_REFURBISHMENT,
                priority=Priority.MEDIUM,
                reason=(
                    "Expected refurbishment uplift materially "
                    "exceeds estimated refurbishment cost."
                ),
                estimated_impact=round(
                    vehicle.refurbishment.expected_price_uplift
                    - vehicle.refurbishment.estimated_cost,
                    2,
                ),
                confidence=0.75,
            )
        )

    # 5. Poor refurbishment economics
    if (
        vehicle.refurbishment.estimated_cost > 0
        and economics.refurbishment_roi < 0
        and not vehicle.refurbishment.safety_work_required
    ):
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.SKIP_LOW_ROI_REFURBISHMENT,
                priority=Priority.MEDIUM,
                reason=(
                    "Non-safety refurbishment is expected to destroy "
                    "economic value."
                ),
                estimated_impact=round(
                    vehicle.refurbishment.estimated_cost
                    - vehicle.refurbishment.expected_price_uplift,
                    2,
                ),
                confidence=0.82,
            )
        )

    # 6. Lifecycle risk
    if _high_lifecycle_risk(vehicle):
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.RISK_REVIEW,
                priority=Priority.HIGH,
                reason=(
                    "Mechanical, warranty, or return risk exceeds "
                    "prototype thresholds."
                ),
                estimated_impact=round(
                    economics.expected_risk_cost,
                    2,
                ),
                confidence=0.79,
            )
        )

    # 7. Acquisition economics
    if economics.expected_contribution < 0:
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.ACQUISITION_REVIEW,
                priority=Priority.CRITICAL,
                reason=(
                    "Expected lifecycle contribution is negative. "
                    "Review acquisition economics and exit options."
                ),
                estimated_impact=round(
                    abs(economics.expected_contribution),
                    2,
                ),
                confidence=0.94,
            )
        )

    # No intervention detected
    if not opportunities:
        opportunities.append(
            Opportunity(
                vehicle_id=vehicle.identity.vehicle_id,
                action=ActionType.HOLD,
                priority=Priority.LOW,
                reason=(
                    "No material intervention threshold has "
                    "been triggered."
                ),
                estimated_impact=0.0,
                confidence=0.70,
            )
        )

    return opportunities
