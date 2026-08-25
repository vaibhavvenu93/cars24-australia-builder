from __future__ import annotations

from dataclasses import dataclass

from engines.scenario_engine import (
    ScenarioInputs,
    apply_scenario,
)
from models.vehicle import Vehicle


@dataclass
class Initiative:
    name: str
    description: str

    effort_score: float
    implementation_risk: float
    time_to_impact_days: int

    contribution_impact: float
    capital_released: float
    risk_reduction: float

    priority_score: float


def _priority_score(
    contribution_impact: float,
    capital_released: float,
    risk_reduction: float,
    effort_score: float,
    implementation_risk: float,
    time_to_impact_days: int,
) -> float:
    """
    Rank initiatives using non-equivalent business outcomes
    without treating every metric as additive profit.

    Contribution is the primary economic outcome.

    Capital release receives a smaller liquidity weighting.

    Risk reduction is treated as strategic protection rather
    than being counted again as full contribution.
    """

    economic_value = max(
        contribution_impact,
        0,
    )

    liquidity_value = max(
        capital_released,
        0,
    ) * 0.20

    protection_value = max(
        risk_reduction,
        0,
    ) * 0.20

    total_value = (
        economic_value
        + liquidity_value
        + protection_value
    )

    execution_penalty = (
        max(effort_score, 0.1)
        * max(implementation_risk, 0.1)
        * max(time_to_impact_days, 1)
    )

    return total_value / execution_penalty


def _build_initiative(
    vehicles: list[Vehicle],
    name: str,
    description: str,
    inputs: ScenarioInputs,
    effort_score: float,
    implementation_risk: float,
    time_to_impact_days: int,
) -> Initiative:

    result = apply_scenario(
        vehicles,
        inputs,
    )

    priority = _priority_score(
        contribution_impact=(
            result.contribution_improvement
        ),
        capital_released=(
            result.capital_released
        ),
        risk_reduction=(
            result.risk_cost_reduction
        ),
        effort_score=effort_score,
        implementation_risk=implementation_risk,
        time_to_impact_days=time_to_impact_days,
    )

    return Initiative(
        name=name,
        description=description,

        effort_score=effort_score,
        implementation_risk=implementation_risk,
        time_to_impact_days=time_to_impact_days,

        contribution_impact=round(
            result.contribution_improvement,
            2,
        ),
        capital_released=round(
            result.capital_released,
            2,
        ),
        risk_reduction=round(
            result.risk_cost_reduction,
            2,
        ),

        priority_score=round(
            priority,
            4,
        ),
    )


def rank_initiatives(
    vehicles: list[Vehicle],
) -> list[Initiative]:

    initiatives = [

        _build_initiative(
            vehicles=vehicles,
            name="Inventory Velocity Sprint",
            description=(
                "Reduce average vehicle capital cycle "
                "through faster ageing intervention."
            ),
            inputs=ScenarioInputs(
                inventory_days_reduction=7,
            ),
            effort_score=2.0,
            implementation_risk=1.5,
            time_to_impact_days=14,
        ),

        _build_initiative(
            vehicles=vehicles,
            name="Acquisition Discipline",
            description=(
                "Improve vehicle acquisition economics "
                "through tighter buy-side guardrails."
            ),
            inputs=ScenarioInputs(
                acquisition_cost_reduction_pct=2.0,
            ),
            effort_score=3.0,
            implementation_risk=2.0,
            time_to_impact_days=30,
        ),

        _build_initiative(
            vehicles=vehicles,
            name="Refurbishment Efficiency",
            description=(
                "Reduce refurbishment cost while preserving "
                "safety and customer trust."
            ),
            inputs=ScenarioInputs(
                refurbishment_cost_reduction_pct=10.0,
            ),
            effort_score=3.5,
            implementation_risk=2.5,
            time_to_impact_days=45,
        ),

        _build_initiative(
            vehicles=vehicles,
            name="Geographic Inventory Rebalancing",
            description=(
                "Move profitable vehicles toward stronger "
                "modeled demand markets."
            ),
            inputs=ScenarioInputs(
                execute_profitable_transfers=True,
            ),
            effort_score=2.5,
            implementation_risk=2.0,
            time_to_impact_days=21,
        ),

        _build_initiative(
            vehicles=vehicles,
            name="Markdown Risk Reduction",
            description=(
                "Improve pricing intervention to reduce "
                "expected markdown exposure."
            ),
            inputs=ScenarioInputs(
                markdown_risk_reduction_pct=20.0,
            ),
            effort_score=2.5,
            implementation_risk=1.5,
            time_to_impact_days=14,
        ),

        _build_initiative(
            vehicles=vehicles,
            name="Warranty Risk Reduction",
            description=(
                "Use inspection and refurbishment signals "
                "to reduce expected post-sale warranty cost."
            ),
            inputs=ScenarioInputs(
                warranty_risk_reduction_pct=15.0,
            ),
            effort_score=4.0,
            implementation_risk=2.5,
            time_to_impact_days=60,
        ),
    ]

    initiatives.sort(
        key=lambda initiative: (
            initiative.priority_score
        ),
        reverse=True,
    )

    return initiatives
