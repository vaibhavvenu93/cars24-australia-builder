from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

LOCATIONS = [
    "Sydney",
    "Melbourne",
    "Brisbane",
    "Perth",
    "Adelaide",
]

SEGMENTS = [
    "SUV",
    "Sedan",
    "Hatchback",
    "Ute",
]

MAKES = [
    "Toyota",
    "Mazda",
    "Hyundai",
    "Kia",
    "Ford",
    "Mitsubishi",
    "Subaru",
    "Volkswagen",
]


# ==========================================================
# DATA CLASSES
# ==========================================================

@dataclass
class InventoryDecision:
    priority: str
    vehicle_id: str
    make: str
    model: str
    location: str
    segment: str
    decision: str
    reason: str
    expected_impact: float
    capital_at_risk: float
    confidence: float


# ==========================================================
# SYNTHETIC VEHICLE DATA
# ==========================================================

def load_inventory_data() -> pd.DataFrame:
    """
    Build deterministic synthetic vehicle-level inventory data.

    Each row represents one vehicle as a capital and operating
    decision object.

    No real CARS24 data is used.
    """

    rows: List[dict] = []

    models_by_make = {
        "Toyota": [
            ("RAV4", "SUV"),
            ("Corolla", "Sedan"),
            ("Yaris", "Hatchback"),
            ("Hilux", "Ute"),
        ],
        "Mazda": [
            ("CX-5", "SUV"),
            ("Mazda3", "Sedan"),
            ("Mazda2", "Hatchback"),
            ("BT-50", "Ute"),
        ],
        "Hyundai": [
            ("Tucson", "SUV"),
            ("i30 Sedan", "Sedan"),
            ("i30", "Hatchback"),
            ("Santa Cruz", "Ute"),
        ],
        "Kia": [
            ("Sportage", "SUV"),
            ("Cerato", "Sedan"),
            ("Picanto", "Hatchback"),
            ("Tasman", "Ute"),
        ],
        "Ford": [
            ("Everest", "SUV"),
            ("Focus", "Sedan"),
            ("Fiesta", "Hatchback"),
            ("Ranger", "Ute"),
        ],
        "Mitsubishi": [
            ("Outlander", "SUV"),
            ("Lancer", "Sedan"),
            ("Mirage", "Hatchback"),
            ("Triton", "Ute"),
        ],
        "Subaru": [
            ("Forester", "SUV"),
            ("Liberty", "Sedan"),
            ("Impreza", "Hatchback"),
            ("Brumby", "Ute"),
        ],
        "Volkswagen": [
            ("Tiguan", "SUV"),
            ("Passat", "Sedan"),
            ("Golf", "Hatchback"),
            ("Amarok", "Ute"),
        ],
    }

    base_prices: Dict[str, float] = {
        "SUV": 33500,
        "Sedan": 27000,
        "Hatchback": 20500,
        "Ute": 36500,
    }

    demand_by_location: Dict[str, float] = {
        "Sydney": 82,
        "Melbourne": 68,
        "Brisbane": 88,
        "Perth": 73,
        "Adelaide": 64,
    }

    vehicle_index = 1

    for location_index, location in enumerate(
        LOCATIONS
    ):
        for make_index, make in enumerate(
            MAKES
        ):
            model_options = models_by_make[make]

            for model_index, (
                model,
                segment,
            ) in enumerate(model_options):

                if vehicle_index > 160:
                    break

                seed = (
                    location_index * 31
                    + make_index * 17
                    + model_index * 11
                    + vehicle_index
                )

                acquisition_price = (
                    base_prices[segment]
                    * (
                        0.76
                        + (seed % 9) * 0.012
                    )
                )

                recon_cost = (
                    650
                    + (seed % 8) * 145
                )

                logistics_cost = (
                    260
                    + (seed % 5) * 90
                )

                age_days = (
                    12
                    + (seed * 7) % 67
                )

                holding_cost_per_day = (
                    16
                    + (seed % 5) * 2.5
                )

                holding_cost = (
                    age_days
                    * holding_cost_per_day
                )

                landed_cost = (
                    acquisition_price
                    + recon_cost
                    + logistics_cost
                    + holding_cost
                )

                market_price = (
                    base_prices[segment]
                    * (
                        1.01
                        + (seed % 7) * 0.018
                    )
                )

                listing_price = (
                    market_price
                    * (
                        0.985
                        + (seed % 5) * 0.009
                    )
                )

                demand_index = (
                    demand_by_location[location]
                    + (seed % 15)
                    - 7
                )

                if segment == "SUV":
                    demand_index += 5

                if (
                    location == "Brisbane"
                    and segment == "SUV"
                ):
                    demand_index += 8

                if (
                    location == "Melbourne"
                    and segment == "SUV"
                ):
                    demand_index -= 4

                expected_sale_price = min(
                    listing_price,
                    market_price * 1.01,
                )

                expected_contribution = (
                    expected_sale_price
                    - landed_cost
                )

                expected_margin_pct = (
                    expected_contribution
                    / expected_sale_price
                    if expected_sale_price
                    else 0.0
                )

                price_position = (
                    listing_price
                    / market_price
                )

                sale_probability = (
                    0.72
                    + (demand_index - 70) * 0.004
                    - max(
                        age_days - 35,
                        0,
                    )
                    * 0.005
                    - max(
                        price_position - 1.0,
                        0,
                    )
                    * 0.6
                )

                sale_probability = max(
                    0.18,
                    min(
                        sale_probability,
                        0.92,
                    ),
                )

                expected_days_to_sale = (
                    11
                    + max(
                        80 - demand_index,
                        0,
                    )
                    * 0.35
                    + max(
                        price_position - 1.0,
                        0,
                    )
                    * 90
                )

                capital_at_risk = (
                    landed_cost
                    if age_days >= 60
                    else (
                        landed_cost * 0.65
                        if age_days >= 45
                        else (
                            landed_cost * 0.25
                            if age_days >= 30
                            else 0.0
                        )
                    )
                )

                age_bucket = (
                    "0-20"
                    if age_days <= 20
                    else (
                        "21-40"
                        if age_days <= 40
                        else (
                            "41-60"
                            if age_days <= 60
                            else "60+"
                        )
                    )
                )

                status = (
                    "Critical"
                    if age_days >= 60
                    else (
                        "Ageing"
                        if age_days >= 45
                        else (
                            "Watch"
                            if age_days >= 30
                            else "Healthy"
                        )
                    )
                )

                rows.append(
                    {
                        "vehicle_id": (
                            f"AU-VH-{vehicle_index:04d}"
                        ),
                        "make": make,
                        "model": model,
                        "segment": segment,
                        "location": location,
                        "year": (
                            2021
                            + seed % 5
                        ),
                        "mileage_km": (
                            22000
                            + (seed * 1700) % 78000
                        ),
                        "acquisition_price": round(
                            acquisition_price,
                            2,
                        ),
                        "recon_cost": round(
                            recon_cost,
                            2,
                        ),
                        "logistics_cost": round(
                            logistics_cost,
                            2,
                        ),
                        "holding_cost": round(
                            holding_cost,
                            2,
                        ),
                        "holding_cost_per_day": round(
                            holding_cost_per_day,
                            2,
                        ),
                        "landed_cost": round(
                            landed_cost,
                            2,
                        ),
                        "market_price": round(
                            market_price,
                            2,
                        ),
                        "listing_price": round(
                            listing_price,
                            2,
                        ),
                        "expected_sale_price": round(
                            expected_sale_price,
                            2,
                        ),
                        "expected_contribution": round(
                            expected_contribution,
                            2,
                        ),
                        "expected_margin_pct": round(
                            expected_margin_pct,
                            4,
                        ),
                        "age_days": age_days,
                        "age_bucket": age_bucket,
                        "status": status,
                        "demand_index": round(
                            demand_index,
                            1,
                        ),
                        "price_position": round(
                            price_position,
                            3,
                        ),
                        "sale_probability": round(
                            sale_probability,
                            4,
                        ),
                        "expected_days_to_sale": round(
                            expected_days_to_sale,
                            1,
                        ),
                        "capital_at_risk": round(
                            capital_at_risk,
                            2,
                        ),
                    }
                )

                vehicle_index += 1

    return pd.DataFrame(rows)


# ==========================================================
# FILTERING
# ==========================================================

def filter_inventory_data(
    dataframe: pd.DataFrame,
    locations: Optional[List[str]] = None,
    segments: Optional[List[str]] = None,
    makes: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
) -> pd.DataFrame:
    df = dataframe.copy()

    if locations:
        df = df[
            df["location"].isin(
                locations
            )
        ]

    if segments:
        df = df[
            df["segment"].isin(
                segments
            )
        ]

    if makes:
        df = df[
            df["make"].isin(
                makes
            )
        ]

    if statuses:
        df = df[
            df["status"].isin(
                statuses
            )
        ]

    return df


# ==========================================================
# PORTFOLIO KPIs
# ==========================================================

def inventory_kpis(
    dataframe: pd.DataFrame,
) -> Dict[str, float]:
    """
    Executive inventory and capital metrics.
    """

    vehicles = len(
        dataframe
    )

    capital_deployed = float(
        dataframe[
            "landed_cost"
        ].sum()
    )

    expected_revenue = float(
        dataframe[
            "expected_sale_price"
        ].sum()
    )

    expected_contribution = float(
        dataframe[
            "expected_contribution"
        ].sum()
    )

    capital_at_risk = float(
        dataframe[
            "capital_at_risk"
        ].sum()
    )

    average_age = float(
        dataframe[
            "age_days"
        ].mean()
    )

    average_margin = float(
        dataframe[
            "expected_margin_pct"
        ].mean()
    )

    average_sale_probability = float(
        dataframe[
            "sale_probability"
        ].mean()
    )

    critical_count = int(
        (
            dataframe[
                "status"
            ]
            == "Critical"
        ).sum()
    )

    ageing_count = int(
        (
            dataframe[
                "status"
            ]
            == "Ageing"
        ).sum()
    )

    return {
        "vehicles": vehicles,
        "capital_deployed": (
            capital_deployed
        ),
        "expected_revenue": (
            expected_revenue
        ),
        "expected_contribution": (
            expected_contribution
        ),
        "capital_at_risk": (
            capital_at_risk
        ),
        "average_age_days": (
            average_age
        ),
        "average_margin_pct": (
            average_margin
        ),
        "average_sale_probability": (
            average_sale_probability
        ),
        "critical_count": (
            critical_count
        ),
        "ageing_count": (
            ageing_count
        ),
    }


# ==========================================================
# AGEING ANALYSIS
# ==========================================================

def ageing_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarise capital by age bucket.
    """

    bucket_order = [
        "0-20",
        "21-40",
        "41-60",
        "60+",
    ]

    grouped = (
        dataframe
        .groupby(
            "age_bucket",
            as_index=False,
        )
        .agg(
            vehicles=(
                "vehicle_id",
                "count",
            ),
            capital=(
                "landed_cost",
                "sum",
            ),
            expected_contribution=(
                "expected_contribution",
                "sum",
            ),
            capital_at_risk=(
                "capital_at_risk",
                "sum",
            ),
        )
    )

    grouped[
        "age_bucket"
    ] = pd.Categorical(
        grouped[
            "age_bucket"
        ],
        categories=bucket_order,
        ordered=True,
    )

    return grouped.sort_values(
        "age_bucket"
    )


# ==========================================================
# LOCATION INVENTORY
# ==========================================================

def location_inventory_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    grouped = (
        dataframe
        .groupby(
            "location",
            as_index=False,
        )
        .agg(
            vehicles=(
                "vehicle_id",
                "count",
            ),
            capital=(
                "landed_cost",
                "sum",
            ),
            expected_revenue=(
                "expected_sale_price",
                "sum",
            ),
            expected_contribution=(
                "expected_contribution",
                "sum",
            ),
            average_age_days=(
                "age_days",
                "mean",
            ),
            average_margin_pct=(
                "expected_margin_pct",
                "mean",
            ),
            demand_index=(
                "demand_index",
                "mean",
            ),
            capital_at_risk=(
                "capital_at_risk",
                "sum",
            ),
        )
    )

    return grouped.sort_values(
        "expected_contribution",
        ascending=False,
    )


# ==========================================================
# MAKE / MODEL INTELLIGENCE
# ==========================================================

def model_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    grouped = (
        dataframe
        .groupby(
            [
                "make",
                "model",
                "segment",
            ],
            as_index=False,
        )
        .agg(
            vehicles=(
                "vehicle_id",
                "count",
            ),
            average_age_days=(
                "age_days",
                "mean",
            ),
            average_margin_pct=(
                "expected_margin_pct",
                "mean",
            ),
            average_demand_index=(
                "demand_index",
                "mean",
            ),
            average_sale_probability=(
                "sale_probability",
                "mean",
            ),
            expected_contribution=(
                "expected_contribution",
                "sum",
            ),
        )
    )

    return grouped.sort_values(
        [
            "average_demand_index",
            "average_margin_pct",
        ],
        ascending=[
            False,
            False,
        ],
    )


# ==========================================================
# DECISION ENGINE
# ==========================================================

def detect_inventory_decisions(
    dataframe: pd.DataFrame,
) -> List[InventoryDecision]:
    """
    Rank vehicle-level inventory interventions.

    The logic is deterministic and inspectable.
    """

    decisions: List[
        InventoryDecision
    ] = []

    for _, row in dataframe.iterrows():

        age_days = int(
            row["age_days"]
        )

        demand_index = float(
            row["demand_index"]
        )

        price_position = float(
            row["price_position"]
        )

        contribution = float(
            row[
                "expected_contribution"
            ]
        )

        capital_at_risk = float(
            row[
                "capital_at_risk"
            ]
        )

        sale_probability = float(
            row[
                "sale_probability"
            ]
        )

        holding_cost_per_day = float(
            row[
                "holding_cost_per_day"
            ]
        )

        # --------------------------------------------------
        # WHOLESALE / EXIT
        # --------------------------------------------------

        if (
            age_days >= 65
            and sale_probability < 0.45
        ):

            expected_impact = (
                capital_at_risk
                * 0.08
                + holding_cost_per_day
                * 18
            )

            decisions.append(
                InventoryDecision(
                    priority="P0",
                    vehicle_id=str(
                        row[
                            "vehicle_id"
                        ]
                    ),
                    make=str(
                        row["make"]
                    ),
                    model=str(
                        row["model"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    decision=(
                        "Wholesale / Exit Review"
                    ),
                    reason=(
                        f"Vehicle has aged {age_days} days "
                        f"with only {sale_probability:.0%} "
                        "estimated sale probability."
                    ),
                    expected_impact=round(
                        expected_impact,
                        2,
                    ),
                    capital_at_risk=round(
                        capital_at_risk,
                        2,
                    ),
                    confidence=0.91,
                )
            )

            continue

        # --------------------------------------------------
        # REPRICE
        # --------------------------------------------------

        if (
            age_days >= 45
            and price_position >= 1.025
        ):

            expected_impact = (
                holding_cost_per_day
                * 14
                + max(
                    contribution,
                    0,
                )
                * 0.035
            )

            decisions.append(
                InventoryDecision(
                    priority="P0",
                    vehicle_id=str(
                        row[
                            "vehicle_id"
                        ]
                    ),
                    make=str(
                        row["make"]
                    ),
                    model=str(
                        row["model"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    decision=(
                        "Reprice"
                    ),
                    reason=(
                        f"Vehicle is {age_days} days old "
                        f"and priced {price_position:.1%} "
                        "of market benchmark."
                    ),
                    expected_impact=round(
                        expected_impact,
                        2,
                    ),
                    capital_at_risk=round(
                        capital_at_risk,
                        2,
                    ),
                    confidence=0.90,
                )
            )

            continue

        # --------------------------------------------------
        # TRANSFER
        # --------------------------------------------------

        if (
            age_days >= 40
            and demand_index < 70
            and row["segment"] == "SUV"
        ):

            expected_impact = (
                holding_cost_per_day
                * 11
                + max(
                    contribution,
                    0,
                )
                * 0.045
            )

            decisions.append(
                InventoryDecision(
                    priority="P1",
                    vehicle_id=str(
                        row[
                            "vehicle_id"
                        ]
                    ),
                    make=str(
                        row["make"]
                    ),
                    model=str(
                        row["model"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    decision=(
                        "Transfer Review"
                    ),
                    reason=(
                        f"Local demand index is only "
                        f"{demand_index:.0f} while vehicle "
                        f"has aged {age_days} days."
                    ),
                    expected_impact=round(
                        expected_impact,
                        2,
                    ),
                    capital_at_risk=round(
                        capital_at_risk,
                        2,
                    ),
                    confidence=0.84,
                )
            )

            continue

        # --------------------------------------------------
        # HOLD / PROTECT MARGIN
        # --------------------------------------------------

        if (
            demand_index >= 82
            and sale_probability >= 0.70
            and contribution > 2500
        ):

            expected_impact = (
                contribution
                * 0.025
            )

            decisions.append(
                InventoryDecision(
                    priority="P2",
                    vehicle_id=str(
                        row[
                            "vehicle_id"
                        ]
                    ),
                    make=str(
                        row["make"]
                    ),
                    model=str(
                        row["model"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    decision=(
                        "Hold Price / Protect Margin"
                    ),
                    reason=(
                        f"Demand index is {demand_index:.0f} "
                        f"with {sale_probability:.0%} "
                        "estimated sale probability."
                    ),
                    expected_impact=round(
                        expected_impact,
                        2,
                    ),
                    capital_at_risk=round(
                        capital_at_risk,
                        2,
                    ),
                    confidence=0.87,
                )
            )

    decisions.sort(
        key=lambda item: (
            item.priority,
            -item.expected_impact,
        )
    )

    return decisions


# ==========================================================
# CAPITAL INTELLIGENCE
# ==========================================================

def capital_intelligence(
    dataframe: pd.DataFrame,
) -> Dict[str, float]:
    """
    Capital productivity summary.
    """

    productive = dataframe[
        dataframe[
            "age_days"
        ] <= 30
    ]

    ageing = dataframe[
        (
            dataframe[
                "age_days"
            ] > 30
        )
        & (
            dataframe[
                "age_days"
            ] <= 60
        )
    ]

    critical = dataframe[
        dataframe[
            "age_days"
        ] > 60
    ]

    productive_capital = float(
        productive[
            "landed_cost"
        ].sum()
    )

    ageing_capital = float(
        ageing[
            "landed_cost"
        ].sum()
    )

    critical_capital = float(
        critical[
            "landed_cost"
        ].sum()
    )

    daily_holding_burn = float(
        dataframe[
            "holding_cost_per_day"
        ].sum()
    )

    decisions = (
        detect_inventory_decisions(
            dataframe
        )
    )

    modeled_release = sum(
        min(
            decision.capital_at_risk
            * 0.20,
            decision.expected_impact
            * 4,
        )
        for decision in decisions
        if decision.priority
        in {
            "P0",
            "P1",
        }
    )

    return {
        "productive_capital": round(
            productive_capital,
            2,
        ),
        "ageing_capital": round(
            ageing_capital,
            2,
        ),
        "critical_capital": round(
            critical_capital,
            2,
        ),
        "daily_holding_burn": round(
            daily_holding_burn,
            2,
        ),
        "modeled_capital_release": round(
            modeled_release,
            2,
        ),
    }


# ==========================================================
# VEHICLE 360
# ==========================================================

def get_vehicle(
    dataframe: pd.DataFrame,
    vehicle_id: str,
) -> Dict[str, object]:
    matches = dataframe[
        dataframe[
            "vehicle_id"
        ]
        == vehicle_id
    ]

    if matches.empty:
        raise ValueError(
            f"Vehicle not found: {vehicle_id}"
        )

    return matches.iloc[
        0
    ].to_dict()


def vehicle_decisions(
    dataframe: pd.DataFrame,
    vehicle_id: str,
) -> List[InventoryDecision]:
    return [
        decision
        for decision
        in detect_inventory_decisions(
            dataframe
        )
        if decision.vehicle_id
        == vehicle_id
    ]
