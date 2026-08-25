from __future__ import annotations

from dataclasses import dataclass

from engines.initiative_engine import rank_initiatives
from engines.portfolio_engine import (
    calculate_portfolio_summary,
    rank_opportunities,
)
from models.vehicle import Vehicle


@dataclass
class BriefingItem:
    rank: int
    headline: str
    detail: str
    modeled_impact: float
    confidence: float


@dataclass
class BuilderBriefing:
    vehicles_analysed: int

    capital_deployed: float
    expected_contribution: float
    capital_at_risk: float

    critical_interventions: int
    high_interventions: int

    top_initiative: str
    top_initiative_reason: str

    priority_actions: list[BriefingItem]


def build_briefing(
    vehicles: list[Vehicle],
    action_limit: int = 5,
) -> BuilderBriefing:

    summary = calculate_portfolio_summary(
        vehicles
    )

    opportunities = rank_opportunities(
        vehicles,
        limit=action_limit,
    )

    initiatives = rank_initiatives(
        vehicles
    )

    top_initiative = initiatives[0]

    priority_actions = []

    for opportunity in opportunities:
        priority_actions.append(
            BriefingItem(
                rank=opportunity.rank,
                headline=(
                    f"{opportunity.action.value} — "
                    f"{opportunity.vehicle_id}"
                ),
                detail=opportunity.reason,
                modeled_impact=opportunity.estimated_impact,
                confidence=opportunity.confidence,
            )
        )

    return BuilderBriefing(
        vehicles_analysed=summary.vehicles_analysed,

        capital_deployed=(
            summary.total_invested_capital
        ),

        expected_contribution=(
            summary.expected_portfolio_contribution
        ),

        capital_at_risk=(
            summary.capital_in_90_plus_day_inventory
            + summary.capital_in_negative_contribution_vehicles
        ),

        critical_interventions=(
            summary.critical_opportunities
        ),

        high_interventions=(
            summary.high_opportunities
        ),

        top_initiative=top_initiative.name,

        top_initiative_reason=(
            f"{top_initiative.description} "
            f"Modeled contribution impact: "
            f"A${top_initiative.contribution_impact:,.0f}. "
            f"Time to impact: "
            f"{top_initiative.time_to_impact_days} days."
        ),

        priority_actions=priority_actions,
    )
