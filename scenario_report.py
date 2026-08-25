from __future__ import annotations

import json
from pathlib import Path

from engines.scenario_engine import (
    ScenarioInputs,
    apply_scenario,
)
from models.vehicle import Vehicle


def load_portfolio() -> list[Vehicle]:
    path = Path(
        "data/synthetic_vehicle_portfolio.json"
    )

    payload = json.loads(
        path.read_text()
    )

    return [
        Vehicle.model_validate(item)
        for item in payload
    ]


def money(value: float) -> str:
    return f"A${value:,.0f}"


def main() -> None:
    vehicles = load_portfolio()

    inputs = ScenarioInputs(
        acquisition_cost_reduction_pct=2.0,
        refurbishment_cost_reduction_pct=10.0,
        inventory_days_reduction=7,
        markdown_risk_reduction_pct=15.0,
        warranty_risk_reduction_pct=10.0,
        execute_profitable_transfers=True,
    )

    result = apply_scenario(
        vehicles,
        inputs,
    )

    print()
    print(
        "CARS24 AUSTRALIA — "
        "SYNTHETIC BUILDER SCENARIO"
    )
    print("=" * 64)

    print()
    print("SCENARIO")
    print("-" * 64)
    print("Acquisition cost improvement: 2%")
    print("Refurbishment cost improvement: 10%")
    print("Inventory cycle improvement: 7 days")
    print("Markdown risk reduction: 15%")
    print("Warranty risk reduction: 10%")
    print("Profitable transfers: ON")

    print()
    print("CURRENT → PROJECTED")
    print("-" * 64)

    print(
        "Capital deployed: "
        f"{money(result.baseline_capital)} "
        "→ "
        f"{money(result.scenario_capital)}"
    )

    print(
        "Expected contribution: "
        f"{money(result.baseline_contribution)} "
        "→ "
        f"{money(result.scenario_contribution)}"
    )

    print(
        "Expected lifecycle risk: "
        f"{money(result.baseline_risk_cost)} "
        "→ "
        f"{money(result.scenario_risk_cost)}"
    )

    print()
    print("MODELED IMPACT")
    print("-" * 64)

    print(
        "Capital released: "
        f"{money(result.capital_released)}"
    )

    print(
        "Contribution improvement: "
        f"{money(result.contribution_improvement)}"
    )

    print(
        "Risk cost reduction: "
        f"{money(result.risk_cost_reduction)}"
    )

    print(
        "90+ day inventory capital: "
        f"{money(result.baseline_90_plus_day_capital)} "
        "→ "
        f"{money(result.scenario_90_plus_day_capital)}"
    )

    print(
        "Vehicles transferred: "
        f"{result.vehicles_transferred}"
    )

    print(
        "Modeled transfer impact: "
        f"{money(result.modeled_transfer_impact)}"
    )

    print()
    print(
        "ILLUSTRATIVE ANNUALISED CONTRIBUTION IMPROVEMENT"
    )
    print("-" * 64)

    print(
        money(
            result.annualised_contribution_improvement
        )
    )

    print()
    print(
        "NOTE: All operating data and scenario assumptions "
        "are synthetic and demonstrate decision architecture only."
    )


if __name__ == "__main__":
    main()
