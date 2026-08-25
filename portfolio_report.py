from __future__ import annotations

import json
from pathlib import Path

from engines.portfolio_engine import (
    calculate_portfolio_summary,
    rank_opportunities,
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

    summary = calculate_portfolio_summary(
        vehicles
    )

    ranked = rank_opportunities(
        vehicles,
        limit=10,
    )

    print()
    print(
        "CARS24 AUSTRALIA — "
        "SYNTHETIC PORTFOLIO INTELLIGENCE"
    )
    print("=" * 62)

    print()
    print("PORTFOLIO")
    print("-" * 62)
    print(
        f"Vehicles analysed: "
        f"{summary.vehicles_analysed}"
    )
    print(
        f"Capital deployed: "
        f"{money(summary.total_invested_capital)}"
    )
    print(
        "Expected portfolio contribution: "
        f"{money(summary.expected_portfolio_contribution)}"
    )
    print(
        "Expected lifecycle risk cost: "
        f"{money(summary.expected_risk_cost)}"
    )

    print()
    print("INTERVENTIONS")
    print("-" * 62)
    print(
        f"Critical: "
        f"{summary.critical_opportunities}"
    )
    print(
        f"High: "
        f"{summary.high_opportunities}"
    )
    print(
        f"Medium: "
        f"{summary.medium_opportunities}"
    )
    print(
        f"Low: "
        f"{summary.low_opportunities}"
    )

    print()
    print("CAPITAL AT RISK")
    print("-" * 62)
    print(
        "90+ day inventory: "
        f"{money(summary.capital_in_90_plus_day_inventory)}"
    )
    print(
        "Negative contribution vehicles: "
        f"{money(summary.capital_in_negative_contribution_vehicles)}"
    )

    print()
    print("ACTION BREAKDOWN")
    print("-" * 62)

    for action, count in sorted(
        summary.action_counts.items()
    ):
        print(
            f"{action:<32} {count:>5}"
        )

    print()
    print("TOP 10 BUILDER OPPORTUNITIES")
    print("-" * 62)

    for opportunity in ranked:
        print()
        print(
            f"#{opportunity.rank} "
            f"{opportunity.vehicle_id}"
        )
        print(
            f"{opportunity.priority.value} | "
            f"{opportunity.action.value}"
        )
        print(
            f"Impact: "
            f"{money(opportunity.estimated_impact)}"
        )
        print(
            f"Confidence: "
            f"{opportunity.confidence:.0%}"
        )
        print(
            f"Why: {opportunity.reason}"
        )


if __name__ == "__main__":
    main()
