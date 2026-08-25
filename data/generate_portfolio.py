from __future__ import annotations

import json
import random
from pathlib import Path

from models.vehicle import (
    Acquisition,
    AcquisitionSource,
    Condition,
    ConditionGrade,
    DemandLevel,
    DemandSignals,
    Inventory,
    LifecycleRisk,
    Pricing,
    Refurbishment,
    RiskLevel,
    Vehicle,
    VehicleIdentity,
    VehicleLocation,
    VehicleStatus,
)


SEED = 24
PORTFOLIO_SIZE = 150

random.seed(SEED)


VEHICLES = [
    ("Toyota", "RAV4", "SUV", 38000),
    ("Toyota", "Corolla", "Hatchback", 26000),
    ("Toyota", "Camry", "Sedan", 32000),
    ("Mazda", "CX-5", "SUV", 34000),
    ("Mazda", "Mazda3", "Hatchback", 26000),
    ("Hyundai", "Tucson", "SUV", 33000),
    ("Hyundai", "i30", "Hatchback", 24000),
    ("Kia", "Sportage", "SUV", 35000),
    ("Kia", "Cerato", "Sedan", 24000),
    ("Ford", "Ranger", "Ute", 47000),
    ("Mitsubishi", "Outlander", "SUV", 35000),
    ("Nissan", "X-Trail", "SUV", 33000),
    ("Honda", "CR-V", "SUV", 36000),
    ("Subaru", "Forester", "SUV", 36000),
    ("Volkswagen", "Golf", "Hatchback", 29000),
]

LOCATIONS = list(VehicleLocation)

ACQUISITION_SOURCES = [
    AcquisitionSource.DIRECT_SELLER,
    AcquisitionSource.DIRECT_SELLER,
    AcquisitionSource.DIRECT_SELLER,
    AcquisitionSource.DEALER,
    AcquisitionSource.AUCTION,
    AcquisitionSource.TRADE_IN,
]

DEMAND_LEVELS = [
    DemandLevel.VERY_HIGH,
    DemandLevel.HIGH,
    DemandLevel.HIGH,
    DemandLevel.MEDIUM,
    DemandLevel.MEDIUM,
    DemandLevel.LOW,
    DemandLevel.VERY_LOW,
]


def choose_risk() -> RiskLevel:
    return random.choices(
        [
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.VERY_HIGH,
        ],
        weights=[55, 30, 12, 3],
    )[0]


def build_vehicle(index: int) -> Vehicle:
    make, model, body_type, base_market_price = random.choice(
        VEHICLES
    )

    year = random.randint(2018, 2025)

    age_discount = (2026 - year) * random.randint(900, 1700)

    expected_market_price = max(
        12000,
        base_market_price - age_discount,
    )

    kilometres = random.randint(12000, 145000)

    acquisition_ratio = random.uniform(0.72, 0.91)

    acquisition_price = (
        expected_market_price * acquisition_ratio
    )

    # Deliberately create some poor acquisitions.
    if random.random() < 0.10:
        acquisition_price = (
            expected_market_price
            * random.uniform(0.94, 1.05)
        )

    estimated_refurbishment = random.choice(
        [0, 300, 500, 800, 1200, 1800, 2500, 3500]
    )

    expected_refurbishment_uplift = (
        estimated_refurbishment
        * random.uniform(0.4, 1.8)
    )

    days_in_inventory = random.randint(3, 115)

    demand_level = random.choice(DEMAND_LEVELS)

    competitor_median = (
        expected_market_price
        * random.uniform(0.96, 1.04)
    )

    current_list_price = (
        expected_market_price
        * random.uniform(0.96, 1.08)
    )

    mechanical_risk = choose_risk()
    cosmetic_risk = choose_risk()

    inspection_score = random.uniform(55, 98)

    warranty_probability = random.uniform(0.02, 0.18)

    if mechanical_risk in {
        RiskLevel.HIGH,
        RiskLevel.VERY_HIGH,
    }:
        warranty_probability = random.uniform(0.25, 0.48)

    return Vehicle(
        identity=VehicleIdentity(
            vehicle_id=f"AU-{index:04d}",
            make=make,
            model=model,
            year=year,
            kilometres=kilometres,
            fuel_type=random.choice(
                [
                    "Petrol",
                    "Petrol",
                    "Diesel",
                    "Hybrid",
                ]
            ),
            transmission="Automatic",
            body_type=body_type,
        ),
        status=VehicleStatus.LISTED,
        acquisition=Acquisition(
            source=random.choice(ACQUISITION_SOURCES),
            initial_valuation=round(
                expected_market_price * 0.82,
                2,
            ),
            acquisition_price=round(
                acquisition_price,
                2,
            ),
            transport_to_hub_cost=random.choice(
                [150, 250, 350, 450, 650]
            ),
        ),
        condition=Condition(
            grade=random.choice(
                [
                    ConditionGrade.EXCELLENT,
                    ConditionGrade.GOOD,
                    ConditionGrade.GOOD,
                    ConditionGrade.FAIR,
                    ConditionGrade.POOR,
                ]
            ),
            inspection_score=round(inspection_score, 2),
            mechanical_risk=mechanical_risk,
            cosmetic_risk=cosmetic_risk,
            service_history_complete=(
                random.random() > 0.20
            ),
            ppsr_clear=(random.random() > 0.03),
        ),
        refurbishment=Refurbishment(
            estimated_cost=estimated_refurbishment,
            expected_price_uplift=round(
                expected_refurbishment_uplift,
                2,
            ),
            estimated_hours=round(
                estimated_refurbishment / 150,
                1,
            ),
            safety_work_required=(
                mechanical_risk
                in {
                    RiskLevel.HIGH,
                    RiskLevel.VERY_HIGH,
                }
            ),
            cosmetic_work_required=(
                estimated_refurbishment > 0
            ),
        ),
        pricing=Pricing(
            expected_market_price=round(
                expected_market_price,
                2,
            ),
            initial_list_price=round(
                expected_market_price * 1.05,
                2,
            ),
            current_list_price=round(
                current_list_price,
                2,
            ),
            competitor_median_price=round(
                competitor_median,
                2,
            ),
            price_changes=random.randint(0, 4),
        ),
        demand=DemandSignals(
            level=demand_level,
            listing_views_7d=random.randint(20, 400),
            enquiries_7d=random.randint(0, 25),
            test_drives_7d=random.randint(0, 8),
            local_inventory_count=random.randint(5, 60),
            estimated_days_to_sale=random.randint(15, 75),
        ),
        inventory=Inventory(
            current_location=random.choice(LOCATIONS),
            days_in_inventory=days_in_inventory,
            days_since_acquisition=(
                days_in_inventory + random.randint(3, 15)
            ),
            storage_cost_per_day=random.uniform(8, 18),
        ),
        lifecycle_risk=LifecycleRisk(
            warranty_probability=round(
                warranty_probability,
                3,
            ),
            expected_warranty_cost=random.randint(
                500,
                3500,
            ),
            return_probability=round(
                random.uniform(0.01, 0.14),
                3,
            ),
            expected_return_cost=random.randint(
                800,
                3000,
            ),
            markdown_probability=round(
                min(
                    0.70,
                    0.08 + days_in_inventory / 200,
                ),
                3,
            ),
            expected_markdown_cost=random.randint(
                500,
                3500,
            ),
        ),
    )


def generate_portfolio(
    size: int = PORTFOLIO_SIZE,
) -> list[Vehicle]:
    return [
        build_vehicle(index)
        for index in range(1, size + 1)
    ]


def save_portfolio(
    vehicles: list[Vehicle],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = [
        vehicle.model_dump(mode="json")
        for vehicle in vehicles
    ]

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        )
    )


if __name__ == "__main__":
    portfolio = generate_portfolio()

    output = Path(
        "data/synthetic_vehicle_portfolio.json"
    )

    save_portfolio(
        portfolio,
        output,
    )

    print(
        f"Generated {len(portfolio)} synthetic vehicles "
        f"at {output}"
    )
