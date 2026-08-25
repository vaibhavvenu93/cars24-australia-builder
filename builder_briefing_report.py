from __future__ import annotations

import json
from pathlib import Path

from agents.builder_briefing import (
    build_briefing,
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

    briefing = build_briefing(
        vehicles,
        action_limit=5,
    )

    print()
    print(
        "CARS24 AUSTRALIA — "
        "BUILDER MORNING BRIEF"
    )
    print("=" * 68)

    print()
    print("PORTFOLIO PULSE")
    print("-" * 68)

    print(
        f"Vehicles analysed: "
        f"{briefing.vehicles_analysed}"
    )

    print(
        "Capital deployed: "
        f"{money(briefing.capital_deployed)}"
    )

    print(
        "Expected contribution: "
        f"{money(briefing.expected_contribution)}"
    )

    print(
        "Capital requiring attention: "
        f"{money(briefing.capital_at_risk)}"
    )

    print(
        "Critical interventions: "
        f"{briefing.critical_interventions}"
    )

    print(
        "High interventions: "
        f"{briefing.high_interventions}"
    )

    print()
    print("WHAT SHOULD WE ATTACK FIRST?")
    print("-" * 68)

    print(
        briefing.top_initiative
    )

    print(
        briefing.top_initiative_reason
    )

    print()
    print("TOP 5 ACTIONS TODAY")
    print("-" * 68)

    for action in briefing.priority_actions:
        print()

        print(
            f"#{action.rank} "
            f"{action.headline}"
        )

        print(
            f"Modeled impact: "
            f"{money(action.modeled_impact)}"
        )

        print(
            f"Confidence: "
            f"{action.confidence:.0%}"
        )

        print(
            f"Why: {action.detail}"
        )

    print()
    print("BUILDER QUESTION")
    print("-" * 68)

    print(
        "What changed since yesterday, "
        "what is economically important, "
        "and which intervention deserves "
        "management attention first?"
    )

    print()
    print(
        "NOTE: All operating data is synthetic."
    )


if __name__ == "__main__":
    main()
