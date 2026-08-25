from __future__ import annotations

import json
from pathlib import Path

from engines.initiative_engine import (
    rank_initiatives,
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

    initiatives = rank_initiatives(
        vehicles
    )

    print()
    print(
        "CARS24 AUSTRALIA — "
        "BUILDER INITIATIVE PRIORITISATION"
    )
    print("=" * 68)

    print()
    print(
        "Question: What should the Australia "
        "Business Builder attack first?"
    )

    print()

    for rank, initiative in enumerate(
        initiatives,
        start=1,
    ):
        print(
            f"#{rank} — {initiative.name}"
        )
        print("-" * 68)

        print(
            initiative.description
        )

        print(
            "Modeled contribution impact: "
            f"{money(initiative.contribution_impact)}"
        )

        print(
            "Capital released: "
            f"{money(initiative.capital_released)}"
        )

        print(
            "Risk reduction: "
            f"{money(initiative.risk_reduction)}"
        )

        print(
            "Time to impact: "
            f"{initiative.time_to_impact_days} days"
        )

        print(
            "Effort score: "
            f"{initiative.effort_score}"
        )

        print(
            "Implementation risk: "
            f"{initiative.implementation_risk}"
        )

        print(
            "Priority score: "
            f"{initiative.priority_score}"
        )

        print()

    print(
        "NOTE: All economics are synthetic and "
        "demonstrate prioritisation logic only."
    )


if __name__ == "__main__":
    main()
