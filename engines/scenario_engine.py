from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from economics.unit_economics import calculate_unit_economics
from engines.location_engine import recommend_transfer
from models.vehicle import Vehicle


@dataclass
class ScenarioInputs:
    acquisition_cost_reduction_pct: float = 0.0
    refurbishment_cost_reduction_pct: float = 0.0
    inventory_days_reduction: int = 0
    markdown_risk_reduction_pct: float = 0.0
    warranty_risk_reduction_pct: float = 0.0
    execute_profitable_transfers: bool = False


@dataclass
class ScenarioResult:
    vehicles_analysed: int

    baseline_capital: float
    scenario_capital: float
    capital_released: float

    baseline_contribution: float
    scenario_contribution: float
    contribution_improvement: float

    baseline_risk_cost: float
    scenario_risk_cost: float
    risk_cost_reduction: float

    baseline_90_plus_day_capital: float
    scenario_90_plus_day_capital: float

    vehicles_transferred: int
    modeled_transfer_impact: float

    annualised_contribution_improvement: float


def _portfolio_metrics(
    vehicles: list[Vehicle],
) -> tuple[float, float, float, float]:
    capital = 0.0
    contribution = 0.0
    risk = 0.0
    aged_capital = 0.0

    for vehicle in vehicles:
        economics = calculate_unit_economics(vehicle)

        capital += economics.invested_capital
        contribution += economics.expected_contribution
        risk += economics.expected_risk_cost

        if vehicle.inventory.days_in_inventory >= 90:
            aged_capital += economics.invested_capital

    return (
        capital,
        contribution,
        risk,
        aged_capital,
    )


def apply_scenario(
    vehicles: list[Vehicle],
    inputs: ScenarioInputs,
) -> ScenarioResult:
    """
    Apply synthetic operating improvements to a copy of the
    portfolio and compare baseline vs scenario economics.

    This is a decision-support model, not a forecast of actual
    CARS24 financial performance.
    """

    scenario_vehicles = deepcopy(vehicles)

    baseline = _portfolio_metrics(vehicles)

    vehicles_transferred = 0
    transfer_impact = 0.0

    for vehicle in scenario_vehicles:

        # 1. Acquisition efficiency
        if inputs.acquisition_cost_reduction_pct > 0:
            reduction = (
                vehicle.acquisition.acquisition_price
                * inputs.acquisition_cost_reduction_pct
                / 100
            )

            vehicle.acquisition.acquisition_price -= reduction

        # 2. Refurbishment efficiency
        if inputs.refurbishment_cost_reduction_pct > 0:
            reduction_factor = (
                1
                - inputs.refurbishment_cost_reduction_pct / 100
            )

            vehicle.refurbishment.estimated_cost *= (
                reduction_factor
            )

            if vehicle.refurbishment.actual_cost is not None:
                vehicle.refurbishment.actual_cost *= (
                    reduction_factor
                )

        # 3. Inventory velocity
        if inputs.inventory_days_reduction > 0:
            vehicle.inventory.days_in_inventory = max(
                0,
                vehicle.inventory.days_in_inventory
                - inputs.inventory_days_reduction,
            )

            vehicle.inventory.days_since_acquisition = max(
                1,
                vehicle.inventory.days_since_acquisition
                - inputs.inventory_days_reduction,
            )

            vehicle.demand.estimated_days_to_sale = max(
                1,
                vehicle.demand.estimated_days_to_sale
                - inputs.inventory_days_reduction,
            )

        # 4. Markdown-risk improvement
        if inputs.markdown_risk_reduction_pct > 0:
            vehicle.lifecycle_risk.markdown_probability *= (
                1
                - inputs.markdown_risk_reduction_pct / 100
            )

        # 5. Warranty-risk improvement
        if inputs.warranty_risk_reduction_pct > 0:
            vehicle.lifecycle_risk.warranty_probability *= (
                1
                - inputs.warranty_risk_reduction_pct / 100
            )

        # 6. Geographic optimisation
        if inputs.execute_profitable_transfers:
            recommendation = recommend_transfer(vehicle)

            if recommendation is not None:
                vehicle.inventory.current_location = (
                    recommendation.recommended_location
                )

        

                vehicle.demand.estimated_days_to_sale = max(
                    1,
                    vehicle.demand.estimated_days_to_sale
                    - recommendation.estimated_days_saved,
                )

                if vehicle.pricing.current_list_price is not None:
                    vehicle.pricing.current_list_price += (
                        recommendation.estimated_price_uplift
                    )

                vehicles_transferred += 1
                transfer_impact += (
                    recommendation.estimated_net_impact
                )

    scenario = _portfolio_metrics(scenario_vehicles)

    baseline_capital = baseline[0]
    baseline_contribution = baseline[1]
    baseline_risk = baseline[2]
    baseline_aged = baseline[3]

    scenario_capital = scenario[0]
    scenario_contribution = scenario[1]
    scenario_risk = scenario[2]
    scenario_aged = scenario[3]

    contribution_improvement = (
        scenario_contribution
        - baseline_contribution
    )

    return ScenarioResult(
        vehicles_analysed=len(vehicles),

        baseline_capital=round(baseline_capital, 2),
        scenario_capital=round(scenario_capital, 2),
        capital_released=round(
            baseline_capital - scenario_capital,
            2,
        ),

        baseline_contribution=round(
            baseline_contribution,
            2,
        ),
        scenario_contribution=round(
            scenario_contribution,
            2,
        ),
        contribution_improvement=round(
            contribution_improvement,
            2,
        ),

        baseline_risk_cost=round(
            baseline_risk,
            2,
        ),
        scenario_risk_cost=round(
            scenario_risk,
            2,
        ),
        risk_cost_reduction=round(
            baseline_risk - scenario_risk,
            2,
        ),

        baseline_90_plus_day_capital=round(
            baseline_aged,
            2,
        ),
        scenario_90_plus_day_capital=round(
            scenario_aged,
            2,
        ),

        vehicles_transferred=vehicles_transferred,
        modeled_transfer_impact=round(
            transfer_impact,
            2,
        ),

        annualised_contribution_improvement=round(
            contribution_improvement * 12,
            2,
        ),
    )
