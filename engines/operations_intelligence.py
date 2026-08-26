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

VENDORS = [
    "AutoFix Network",
    "Metro Recon",
    "Rapid Motor Works",
    "Precision Auto",
    "Prime Bodyworks",
    "DriveReady Services",
]

SEGMENTS = [
    "SUV",
    "Sedan",
    "Hatchback",
    "Ute",
]


# ==========================================================
# DATA CLASSES
# ==========================================================


@dataclass
class OperationsAction:
    priority: str
    action_type: str
    entity: str
    location: str
    issue: str
    evidence: str
    recommended_action: str
    expected_impact: float
    confidence: float


@dataclass
class TransferRecommendation:
    vehicle_id: str
    make_model: str
    segment: str
    origin: str
    destination: str
    origin_demand: float
    destination_demand: float
    transfer_cost: float
    modeled_margin_gain: float
    days_saved: float
    confidence: float


# ==========================================================
# SYNTHETIC RECON DATA
# ==========================================================


def load_recon_data() -> pd.DataFrame:
    """
    Deterministic synthetic recon and vendor dataset.

    No real CARS24 data is used.
    """

    rows: List[dict] = []

    job_index = 1

    for location_index, location in enumerate(
        LOCATIONS
    ):
        for vendor_index, vendor in enumerate(
            VENDORS
        ):
            for job_number in range(12):

                seed = (
                    location_index * 37
                    + vendor_index * 19
                    + job_number * 13
                )

                quoted_cost = (
                    720
                    + (seed % 9) * 135
                )

                cost_variance = (
                    -0.05
                    + (seed % 8) * 0.025
                )

                actual_cost = (
                    quoted_cost
                    * (
                        1
                        + cost_variance
                    )
                )

                turnaround_days = (
                    2.4
                    + (seed % 7) * 0.55
                )

                rework = (
                    seed % 11 == 0
                )

                parts_delay_days = (
                    0
                    if seed % 5
                    else (
                        1
                        + seed % 4
                    )
                )

                sla_days = 4.0

                # ------------------------------------------
                # CONTROLLED OPERATING STORIES
                # ------------------------------------------

                if (
                    location == "Melbourne"
                    and vendor
                    == "Metro Recon"
                ):
                    turnaround_days += 2.1
                    actual_cost *= 1.12

                    if job_number % 4 == 0:
                        rework = True

                if (
                    location == "Sydney"
                    and vendor
                    == "Rapid Motor Works"
                ):
                    turnaround_days -= 0.5
                    actual_cost *= 0.97

                if (
                    location == "Brisbane"
                    and vendor
                    == "AutoFix Network"
                ):
                    turnaround_days -= 0.4

                defect_category = [
                    "Mechanical",
                    "Cosmetic",
                    "Tyres",
                    "Electrical",
                    "Body",
                ][seed % 5]

                rows.append(
                    {
                        "job_id": (
                            f"RC-{job_index:04d}"
                        ),
                        "location": location,
                        "vendor": vendor,
                        "vehicle_id": (
                            f"AU-VH-{((job_index - 1) % 160) + 1:04d}"
                        ),
                        "quoted_cost": round(
                            quoted_cost,
                            2,
                        ),
                        "actual_cost": round(
                            actual_cost,
                            2,
                        ),
                        "turnaround_days": round(
                            max(
                                turnaround_days,
                                1.0,
                            ),
                            1,
                        ),
                        "sla_days": sla_days,
                        "rework_required": (
                            rework
                        ),
                        "parts_delay_days": (
                            parts_delay_days
                        ),
                        "defect_category": (
                            defect_category
                        ),
                    }
                )

                job_index += 1

    df = pd.DataFrame(rows)

    df["cost_variance"] = (
        df["actual_cost"]
        - df["quoted_cost"]
    )

    df["cost_variance_pct"] = (
        df["cost_variance"]
        / df["quoted_cost"]
    )

    df["sla_breach"] = (
        df["turnaround_days"]
        > df["sla_days"]
    )

    return df


# ==========================================================
# SYNTHETIC LOCATION DATA
# ==========================================================


def load_location_operations() -> pd.DataFrame:
    """
    Synthetic operating performance by location.
    """

    rows = [
        {
            "location": "Sydney",
            "vehicles": 410,
            "sales": 142,
            "avg_inventory_age": 37.2,
            "recon_days": 3.2,
            "lead_response_minutes": 11,
            "conversion_rate": 0.205,
            "gross_profit": 418000,
            "operating_cost": 188000,
        },
        {
            "location": "Melbourne",
            "vehicles": 386,
            "sales": 116,
            "avg_inventory_age": 49.1,
            "recon_days": 5.7,
            "lead_response_minutes": 31,
            "conversion_rate": 0.167,
            "gross_profit": 344000,
            "operating_cost": 204000,
        },
        {
            "location": "Brisbane",
            "vehicles": 302,
            "sales": 109,
            "avg_inventory_age": 31.8,
            "recon_days": 3.0,
            "lead_response_minutes": 10,
            "conversion_rate": 0.221,
            "gross_profit": 338000,
            "operating_cost": 147000,
        },
        {
            "location": "Perth",
            "vehicles": 214,
            "sales": 67,
            "avg_inventory_age": 42.0,
            "recon_days": 4.1,
            "lead_response_minutes": 17,
            "conversion_rate": 0.187,
            "gross_profit": 201000,
            "operating_cost": 111000,
        },
        {
            "location": "Adelaide",
            "vehicles": 174,
            "sales": 51,
            "avg_inventory_age": 40.4,
            "recon_days": 3.8,
            "lead_response_minutes": 16,
            "conversion_rate": 0.181,
            "gross_profit": 156000,
            "operating_cost": 92000,
        },
    ]

    df = pd.DataFrame(rows)

    df["operating_contribution"] = (
        df["gross_profit"]
        - df["operating_cost"]
    )

    df["sales_per_100_vehicles"] = (
        df["sales"]
        / df["vehicles"]
        * 100
    )

    return df


# ==========================================================
# SYNTHETIC LOGISTICS / TRANSFER DATA
# ==========================================================


def load_transfer_candidates() -> pd.DataFrame:
    """
    Synthetic vehicle transfer candidates.

    Represents inventory that may perform better
    in another Australian market.
    """

    rows: List[dict] = []

    origin_demand = {
        "Sydney": 82,
        "Melbourne": 66,
        "Brisbane": 91,
        "Perth": 72,
        "Adelaide": 63,
    }

    vehicle_models = [
        ("Toyota RAV4", "SUV"),
        ("Mazda CX-5", "SUV"),
        ("Ford Ranger", "Ute"),
        ("Mitsubishi Outlander", "SUV"),
        ("Toyota Corolla", "Sedan"),
        ("Hyundai Tucson", "SUV"),
        ("Volkswagen Golf", "Hatchback"),
        ("Subaru Forester", "SUV"),
    ]

    vehicle_index = 1

    for origin_index, origin in enumerate(
        LOCATIONS
    ):
        for model_index, (
            model,
            segment,
        ) in enumerate(
            vehicle_models
        ):

            destination = (
                "Brisbane"
                if (
                    segment == "SUV"
                    and origin != "Brisbane"
                )
                else (
                    "Sydney"
                    if origin != "Sydney"
                    else "Perth"
                )
            )

            seed = (
                origin_index * 17
                + model_index * 11
            )

            transfer_cost = (
                420
                + seed % 6 * 115
            )

            current_demand = (
                origin_demand[
                    origin
                ]
            )

            destination_demand = (
                origin_demand[
                    destination
                ]
            )

            age_days = (
                34
                + seed % 39
            )

            landed_cost = (
                24500
                + seed % 8 * 1750
            )

            margin_gain = (
                max(
                    destination_demand
                    - current_demand,
                    0,
                )
                * 115
                + max(
                    age_days - 40,
                    0,
                )
                * 26
                - transfer_cost
            )

            days_saved = (
                max(
                    destination_demand
                    - current_demand,
                    0,
                )
                * 0.18
            )

            rows.append(
                {
                    "vehicle_id": (
                        f"AU-VH-{vehicle_index:04d}"
                    ),
                    "make_model": model,
                    "segment": segment,
                    "origin": origin,
                    "destination": destination,
                    "origin_demand": (
                        current_demand
                    ),
                    "destination_demand": (
                        destination_demand
                    ),
                    "age_days": age_days,
                    "landed_cost": landed_cost,
                    "transfer_cost": (
                        transfer_cost
                    ),
                    "modeled_margin_gain": round(
                        margin_gain,
                        2,
                    ),
                    "days_saved": round(
                        days_saved,
                        1,
                    ),
                }
            )

            vehicle_index += 1

    return pd.DataFrame(rows)


# ==========================================================
# FILTERING
# ==========================================================


def filter_recon_data(
    dataframe: pd.DataFrame,
    locations: Optional[List[str]] = None,
    vendors: Optional[List[str]] = None,
) -> pd.DataFrame:

    df = dataframe.copy()

    if locations:
        df = df[
            df["location"].isin(
                locations
            )
        ]

    if vendors:
        df = df[
            df["vendor"].isin(
                vendors
            )
        ]

    return df


# ==========================================================
# VENDOR PERFORMANCE
# ==========================================================


def vendor_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    grouped = (
        dataframe
        .groupby(
            "vendor",
            as_index=False,
        )
        .agg(
            jobs=(
                "job_id",
                "count",
            ),
            quoted_cost=(
                "quoted_cost",
                "sum",
            ),
            actual_cost=(
                "actual_cost",
                "sum",
            ),
            avg_turnaround_days=(
                "turnaround_days",
                "mean",
            ),
            rework_rate=(
                "rework_required",
                "mean",
            ),
            sla_breach_rate=(
                "sla_breach",
                "mean",
            ),
            avg_parts_delay=(
                "parts_delay_days",
                "mean",
            ),
        )
    )

    grouped["cost_overrun"] = (
        grouped["actual_cost"]
        - grouped["quoted_cost"]
    )

    grouped[
        "cost_overrun_pct"
    ] = (
        grouped["cost_overrun"]
        / grouped["quoted_cost"]
    )

    # Explainable vendor score
    grouped[
        "vendor_score"
    ] = (
        100
        - grouped[
            "sla_breach_rate"
        ]
        * 35
        - grouped[
            "rework_rate"
        ]
        * 30
        - grouped[
            "cost_overrun_pct"
        ].clip(
            lower=0
        )
        * 100
        * 0.25
        - grouped[
            "avg_parts_delay"
        ]
        * 2
    )

    grouped[
        "vendor_score"
    ] = grouped[
        "vendor_score"
    ].clip(
        lower=0,
        upper=100,
    )

    return grouped.sort_values(
        "vendor_score",
        ascending=False,
    )


# ==========================================================
# LOCATION PERFORMANCE
# ==========================================================


def location_performance() -> pd.DataFrame:

    df = load_location_operations()

    max_contribution = df[
        "operating_contribution"
    ].max()

    max_velocity = df[
        "sales_per_100_vehicles"
    ].max()

    df[
        "operating_score"
    ] = (
        (
            df[
                "operating_contribution"
            ]
            / max_contribution
        )
        * 35
        + (
            df[
                "sales_per_100_vehicles"
            ]
            / max_velocity
        )
        * 30
        + (
            1
            - (
                df[
                    "avg_inventory_age"
                ]
                / df[
                    "avg_inventory_age"
                ].max()
            )
        )
        * 15
        + (
            1
            - (
                df[
                    "recon_days"
                ]
                / df[
                    "recon_days"
                ].max()
            )
        )
        * 10
        + (
            1
            - (
                df[
                    "lead_response_minutes"
                ]
                / df[
                    "lead_response_minutes"
                ].max()
            )
        )
        * 10
    )

    return df.sort_values(
        "operating_score",
        ascending=False,
    )


# ==========================================================
# TRANSFER INTELLIGENCE
# ==========================================================


def transfer_recommendations(
    dataframe: Optional[
        pd.DataFrame
    ] = None,
) -> List[TransferRecommendation]:

    if dataframe is None:
        dataframe = (
            load_transfer_candidates()
        )

    recommendations: List[
        TransferRecommendation
    ] = []

    for _, row in (
        dataframe.iterrows()
    ):

        demand_gap = (
            float(
                row[
                    "destination_demand"
                ]
            )
            - float(
                row[
                    "origin_demand"
                ]
            )
        )

        margin_gain = float(
            row[
                "modeled_margin_gain"
            ]
        )

        if (
            demand_gap >= 8
            and margin_gain > 250
        ):

            confidence = (
                0.88
                if demand_gap >= 18
                else 0.81
            )

            recommendations.append(
                TransferRecommendation(
                    vehicle_id=str(
                        row[
                            "vehicle_id"
                        ]
                    ),
                    make_model=str(
                        row[
                            "make_model"
                        ]
                    ),
                    segment=str(
                        row[
                            "segment"
                        ]
                    ),
                    origin=str(
                        row[
                            "origin"
                        ]
                    ),
                    destination=str(
                        row[
                            "destination"
                        ]
                    ),
                    origin_demand=float(
                        row[
                            "origin_demand"
                        ]
                    ),
                    destination_demand=float(
                        row[
                            "destination_demand"
                        ]
                    ),
                    transfer_cost=float(
                        row[
                            "transfer_cost"
                        ]
                    ),
                    modeled_margin_gain=(
                        margin_gain
                    ),
                    days_saved=float(
                        row[
                            "days_saved"
                        ]
                    ),
                    confidence=confidence,
                )
            )

    recommendations.sort(
        key=lambda item: (
            -item.modeled_margin_gain
        )
    )

    return recommendations


# ==========================================================
# OPERATIONS ACTION ENGINE
# ==========================================================


def detect_operations_actions() -> List[
    OperationsAction
]:
    """
    Combine location, vendor and transfer signals
    into one operating action queue.
    """

    actions: List[
        OperationsAction
    ] = []

    # ------------------------------------------------------
    # LOCATION SIGNALS
    # ------------------------------------------------------

    locations = (
        load_location_operations()
    )

    national_conversion = float(
        locations[
            "conversion_rate"
        ].mean()
    )

    national_recon = float(
        locations[
            "recon_days"
        ].mean()
    )

    for _, row in (
        locations.iterrows()
    ):

        if (
            float(
                row[
                    "conversion_rate"
                ]
            )
            < national_conversion
            - 0.02
        ):

            revenue_opportunity = (
                float(
                    row["sales"]
                )
                * 3200
                * 0.12
            )

            actions.append(
                OperationsAction(
                    priority="P0",
                    action_type=(
                        "Location Intervention"
                    ),
                    entity=str(
                        row["location"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    issue=(
                        "Conversion materially below "
                        "national operating benchmark."
                    ),
                    evidence=(
                        f"Conversion is "
                        f"{row['conversion_rate']:.1%} "
                        f"versus "
                        f"{national_conversion:.1%} "
                        "network benchmark."
                    ),
                    recommended_action=(
                        "Run a location-level operating review "
                        "across response time, recon throughput "
                        "and inventory mix."
                    ),
                    expected_impact=round(
                        revenue_opportunity,
                        2,
                    ),
                    confidence=0.91,
                )
            )

        if (
            float(
                row[
                    "recon_days"
                ]
            )
            > national_recon
            + 1
        ):

            actions.append(
                OperationsAction(
                    priority="P0",
                    action_type=(
                        "Recon Bottleneck"
                    ),
                    entity=str(
                        row["location"]
                    ),
                    location=str(
                        row["location"]
                    ),
                    issue=(
                        "Recon turnaround is materially "
                        "slower than network benchmark."
                    ),
                    evidence=(
                        f"{row['location']} recon averages "
                        f"{row['recon_days']:.1f} days "
                        f"versus {national_recon:.1f} days."
                    ),
                    recommended_action=(
                        "Review vendor mix, parts delays "
                        "and workshop capacity."
                    ),
                    expected_impact=round(
                        float(
                            row[
                                "vehicles"
                            ]
                        )
                        * 18
                        * 1.2,
                        2,
                    ),
                    confidence=0.94,
                )
            )

    # ------------------------------------------------------
    # VENDOR SIGNALS
    # ------------------------------------------------------

    vendor_df = vendor_performance(
        load_recon_data()
    )

    for _, row in (
        vendor_df.iterrows()
    ):

        if (
            float(
                row[
                    "vendor_score"
                ]
            )
            < 78
        ):

            impact = (
                max(
                    float(
                        row[
                            "cost_overrun"
                        ]
                    ),
                    0,
                )
                + float(
                    row[
                        "jobs"
                    ]
                )
                * float(
                    row[
                        "sla_breach_rate"
                    ]
                )
                * 75
            )

            actions.append(
                OperationsAction(
                    priority="P1",
                    action_type=(
                        "Vendor Review"
                    ),
                    entity=str(
                        row[
                            "vendor"
                        ]
                    ),
                    location="Network",
                    issue=(
                        "Vendor economics or SLA "
                        "performance is below target."
                    ),
                    evidence=(
                        f"Vendor score "
                        f"{row['vendor_score']:.0f}/100; "
                        f"SLA breach rate "
                        f"{row['sla_breach_rate']:.0%}; "
                        f"rework "
                        f"{row['rework_rate']:.0%}."
                    ),
                    recommended_action=(
                        "Review allocation volume, "
                        "commercial terms and SLA root causes."
                    ),
                    expected_impact=round(
                        impact,
                        2,
                    ),
                    confidence=0.86,
                )
            )

    # ------------------------------------------------------
    # TRANSFER SIGNALS
    # ------------------------------------------------------

    for transfer in (
        transfer_recommendations()
    )[:8]:

        actions.append(
            OperationsAction(
                priority="P1",
                action_type=(
                    "Inventory Transfer"
                ),
                entity=(
                    transfer.vehicle_id
                ),
                location=(
                    transfer.origin
                ),
                issue=(
                    "Vehicle appears better matched "
                    "to demand in another market."
                ),
                evidence=(
                    f"{transfer.origin} demand "
                    f"{transfer.origin_demand:.0f} → "
                    f"{transfer.destination} demand "
                    f"{transfer.destination_demand:.0f}."
                ),
                recommended_action=(
                    f"Evaluate transfer to "
                    f"{transfer.destination}."
                ),
                expected_impact=(
                    transfer
                    .modeled_margin_gain
                ),
                confidence=(
                    transfer.confidence
                ),
            )
        )

    actions.sort(
        key=lambda item: (
            item.priority,
            -item.expected_impact,
        )
    )

    return actions


# ==========================================================
# OPERATIONS SUMMARY
# ==========================================================


def operations_summary() -> Dict[
    str,
    float
]:

    recon = load_recon_data()

    vendor = vendor_performance(
        recon
    )

    transfers = (
        transfer_recommendations()
    )

    actions = (
        detect_operations_actions()
    )

    return {
        "recon_jobs": float(
            len(recon)
        ),
        "average_recon_days": float(
            recon[
                "turnaround_days"
            ].mean()
        ),
        "sla_breach_rate": float(
            recon[
                "sla_breach"
            ].mean()
        ),
        "rework_rate": float(
            recon[
                "rework_required"
            ].mean()
        ),
        "average_vendor_score": float(
            vendor[
                "vendor_score"
            ].mean()
        ),
        "transfer_opportunities": float(
            len(
                transfers
            )
        ),
        "transfer_margin_upside": float(
            sum(
                item
                .modeled_margin_gain
                for item
                in transfers
            )
        ),
        "open_actions": float(
            len(
                actions
            )
        ),
    }
