from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from economics.unit_economics import calculate_unit_economics
from engines.location_engine import recommend_transfer
from engines.opportunity_engine import (
    ActionType,
    Opportunity,
    Priority,
    evaluate_vehicle,
)
from models.vehicle import Vehicle


@dataclass
class PortfolioSummary:
    vehicles_analysed: int
    total_invested_capital: float
    expected_portfolio_contribution: float

    critical_opportunities: int
    high_opportunities: int
    medium_opportunities: int
    low_opportunities: int

    capital_in_90_plus_day_inventory: float
    capital_in_negative_contribution_vehicles: float
    expected_risk_cost: float

    action_counts: dict[str, int]


@dataclass
class RankedOpportunity:
    rank: int
    vehicle_id: str
    action: ActionType
    priority: Priority
    reason: str
    estimated_impact: float
    confidence: float


PRIORITY_WEIGHT = {
    Priority.CRITICAL: 4,
    Priority.HIGH: 3,
    Priority.MEDIUM: 2,
    Priority.LOW: 1,
}


def calculate_portfolio_summary(
    vehicles: list[Vehicle],
) -> PortfolioSummary:
    total_invested_capital = 0.0
    expected_portfolio_contribution = 0.0

    capital_in_90_plus_day_inventory = 0.0
    capital_in_negative_contribution_vehicles = 0.0
    expected_risk_cost = 0.0

    priority_counter: Counter[Priority] = Counter()
    action_counter: Counter[ActionType] = Counter()

    for vehicle in vehicles:
        economics = calculate_unit_economics(vehicle)

        total_invested_capital += economics.invested_capital
        expected_portfolio_contribution += (
            economics.expected_contribution
        )
        expected_risk_cost += economics.expected_risk_cost

        if vehicle.inventory.days_in_inventory >= 90:
            capital_in_90_plus_day_inventory += (
                economics.invested_capital
            )

        if economics.expected_contribution < 0:
            capital_in_negative_contribution_vehicles += (
                economics.invested_capital
            )

        opportunities = evaluate_vehicle(vehicle)

        for opportunity in opportunities:
            priority_counter[opportunity.priority] += 1
            action_counter[opportunity.action] += 1

    return PortfolioSummary(
        vehicles_analysed=len(vehicles),
        total_invested_capital=round(
            total_invested_capital,
            2,
        ),
        expected_portfolio_contribution=round(
            expected_portfolio_contribution,
            2,
        ),
        critical_opportunities=priority_counter[
            Priority.CRITICAL
        ],
        high_opportunities=priority_counter[
            Priority.HIGH
        ],
        medium_opportunities=priority_counter[
            Priority.MEDIUM
        ],
        low_opportunities=priority_counter[
            Priority.LOW
        ],
        capital_in_90_plus_day_inventory=round(
            capital_in_90_plus_day_inventory,
            2,
        ),
        capital_in_negative_contribution_vehicles=round(
            capital_in_negative_contribution_vehicles,
            2,
        ),
        expected_risk_cost=round(
            expected_risk_cost,
            2,
        ),
        action_counts={
            action.value: count
            for action, count in action_counter.items()
        },
    )


def rank_opportunities(
    vehicles: list[Vehicle],
    limit: int = 10,
) -> list[RankedOpportunity]:
    all_opportunities: list[Opportunity] = []

    for vehicle in vehicles:
        vehicle_opportunities = evaluate_vehicle(vehicle)

        for opportunity in vehicle_opportunities:
            if opportunity.action == ActionType.TRANSFER_REVIEW:
                transfer = recommend_transfer(vehicle)

                if transfer is not None:
                    opportunity = Opportunity(
                        vehicle_id=opportunity.vehicle_id,
                        action=ActionType.TRANSFER_REVIEW,
                        priority=opportunity.priority,
                        reason=(
                            f"Move from "
                            f"{transfer.current_location.value} "
                            f"to "
                            f"{transfer.recommended_location.value}. "
                            f"Estimated {transfer.estimated_days_saved} "
                            f"days saved with "
                            f"{transfer.estimated_net_impact:,.0f} "
                            f"of modeled net impact."
                        ),
                        estimated_impact=round(
                            transfer.estimated_net_impact,
                            2,
                        ),
                        confidence=transfer.confidence,
                    )

            all_opportunities.append(opportunity)

    meaningful = [
        opportunity
        for opportunity in all_opportunities
        if opportunity.action != ActionType.HOLD
    ]

    meaningful.sort(
        key=lambda opportunity: (
            PRIORITY_WEIGHT[opportunity.priority],
            opportunity.estimated_impact,
            opportunity.confidence,
        ),
        reverse=True,
    )

    ranked = []

    for index, opportunity in enumerate(
        meaningful[:limit],
        start=1,
    ):
        ranked.append(
            RankedOpportunity(
                rank=index,
                vehicle_id=opportunity.vehicle_id,
                action=opportunity.action,
                priority=opportunity.priority,
                reason=opportunity.reason,
                estimated_impact=opportunity.estimated_impact,
                confidence=opportunity.confidence,
            )
        )

    return ranked

def action_breakdown(
    vehicles: list[Vehicle],
) -> dict[str, int]:
    counter: Counter[ActionType] = Counter()

    for vehicle in vehicles:
        for opportunity in evaluate_vehicle(vehicle):
            counter[opportunity.action] += 1

    return {
        action.value: count
        for action, count in counter.items()
    }
