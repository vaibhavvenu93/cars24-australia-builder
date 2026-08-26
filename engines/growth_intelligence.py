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

MONTHS = [
    "2026-06",
    "2026-07",
    "2026-08",
]


LOCATION_BASE_ENQUIRIES: Dict[str, int] = {
    "Sydney": 760,
    "Melbourne": 690,
    "Brisbane": 520,
    "Perth": 360,
    "Adelaide": 280,
}


SEGMENT_SHARE: Dict[str, float] = {
    "SUV": 0.43,
    "Sedan": 0.23,
    "Hatchback": 0.18,
    "Ute": 0.16,
}


MONTH_MULTIPLIER: Dict[str, float] = {
    "2026-06": 0.91,
    "2026-07": 0.97,
    "2026-08": 1.00,
}


AVERAGE_SALE_PRICE: Dict[str, float] = {
    "SUV": 38900,
    "Sedan": 31800,
    "Hatchback": 24400,
    "Ute": 42100,
}


BASE_TEST_DRIVE_RATE: Dict[str, float] = {
    "Sydney": 0.47,
    "Melbourne": 0.42,
    "Brisbane": 0.49,
    "Perth": 0.44,
    "Adelaide": 0.45,
}


BASE_OFFER_RATE: Dict[str, float] = {
    "Sydney": 0.61,
    "Melbourne": 0.57,
    "Brisbane": 0.64,
    "Perth": 0.59,
    "Adelaide": 0.60,
}


BASE_CLOSE_RATE: Dict[str, float] = {
    "Sydney": 0.73,
    "Melbourne": 0.68,
    "Brisbane": 0.76,
    "Perth": 0.71,
    "Adelaide": 0.72,
}


BASE_RESPONSE_MINUTES: Dict[str, float] = {
    "Sydney": 13.0,
    "Melbourne": 27.0,
    "Brisbane": 11.0,
    "Perth": 17.0,
    "Adelaide": 16.0,
}


BASE_INVENTORY_AGE: Dict[str, float] = {
    "Sydney": 38.0,
    "Melbourne": 47.0,
    "Brisbane": 32.0,
    "Perth": 41.0,
    "Adelaide": 39.0,
}


LOCATION_PRICE_INDEX: Dict[str, float] = {
    "Sydney": 1.01,
    "Melbourne": 1.035,
    "Brisbane": 0.995,
    "Perth": 1.015,
    "Adelaide": 1.00,
}


SEGMENT_TEST_DRIVE_MODIFIER: Dict[str, float] = {
    "SUV": 1.00,
    "Sedan": 0.96,
    "Hatchback": 1.02,
    "Ute": 0.94,
}


SEGMENT_CLOSE_MODIFIER: Dict[str, float] = {
    "SUV": 1.02,
    "Sedan": 0.98,
    "Hatchback": 1.00,
    "Ute": 0.97,
}


# ==========================================================
# DATA CLASSES
# ==========================================================

@dataclass
class GrowthOpportunity:
    priority: str
    location: str
    segment: str
    issue: str
    evidence: str
    modeled_monthly_revenue_upside: float
    current_value: float
    benchmark_value: float
    recommended_action: str
    confidence: float


# ==========================================================
# SYNTHETIC DATASET
# ==========================================================

def load_growth_data() -> pd.DataFrame:
    """
    Create deterministic synthetic growth data for the
    CARS24 Australia Intelligence OS.

    The dataset represents:

    enquiry
        ↓
    test drive
        ↓
    offer
        ↓
    sale

    alongside revenue and diagnostic operating signals.

    No real CARS24 data is used.
    """

    rows: List[dict] = []

    for month in MONTHS:

        month_multiplier = MONTH_MULTIPLIER[month]

        for location in LOCATIONS:

            for segment in SEGMENTS:

                enquiries = round(
                    LOCATION_BASE_ENQUIRIES[location]
                    * SEGMENT_SHARE[segment]
                    * month_multiplier
                )

                test_drive_rate = (
                    BASE_TEST_DRIVE_RATE[location]
                    * SEGMENT_TEST_DRIVE_MODIFIER[segment]
                )

                offer_rate = BASE_OFFER_RATE[location]

                close_rate = (
                    BASE_CLOSE_RATE[location]
                    * SEGMENT_CLOSE_MODIFIER[segment]
                )

                response_minutes = (
                    BASE_RESPONSE_MINUTES[location]
                )

                inventory_age = (
                    BASE_INVENTORY_AGE[location]
                )

                price_index = (
                    LOCATION_PRICE_INDEX[location]
                )

                # ------------------------------------------
                # CONTROLLED OPERATING STORIES
                # ------------------------------------------

                if month == "2026-08":

                    # Melbourne SUV problem:
                    # enough demand exists, but customers are
                    # not progressing to test drives.
                    if (
                        location == "Melbourne"
                        and segment == "SUV"
                    ):
                        test_drive_rate = 0.31
                        response_minutes = 42.0
                        inventory_age = 53.0
                        price_index = 1.055

                    # Brisbane SUV opportunity:
                    # strong demand and healthy conversion.
                    if (
                        location == "Brisbane"
                        and segment == "SUV"
                    ):
                        enquiries = round(
                            enquiries * 1.18
                        )
                        test_drive_rate = 0.54
                        close_rate = 0.79
                        inventory_age = 27.0
                        price_index = 0.99

                    # Sydney gets operationally stronger.
                    if location == "Sydney":
                        response_minutes *= 0.82

                    # Perth Ute opportunity.
                    if (
                        location == "Perth"
                        and segment == "Ute"
                    ):
                        enquiries = round(
                            enquiries * 1.12
                        )
                        close_rate = 0.76

                if month == "2026-07":

                    if (
                        location == "Melbourne"
                        and segment == "SUV"
                    ):
                        test_drive_rate = 0.37
                        response_minutes = 34.0
                        inventory_age = 49.0
                        price_index = 1.045

                test_drives = round(
                    enquiries * test_drive_rate
                )

                offers = round(
                    test_drives * offer_rate
                )

                sales = round(
                    offers * close_rate
                )

                average_sale_price = (
                    AVERAGE_SALE_PRICE[segment]
                    * price_index
                )

                revenue = (
                    sales
                    * average_sale_price
                )

                rows.append(
                    {
                        "month": month,
                        "location": location,
                        "segment": segment,
                        "enquiries": enquiries,
                        "test_drives": test_drives,
                        "offers": offers,
                        "sales": sales,
                        "revenue": round(
                            revenue,
                            2,
                        ),
                        "average_sale_price": round(
                            average_sale_price,
                            2,
                        ),
                        "response_minutes": round(
                            response_minutes,
                            1,
                        ),
                        "inventory_age_days": round(
                            inventory_age,
                            1,
                        ),
                        "price_index": round(
                            price_index,
                            3,
                        ),
                    }
                )

    dataframe = pd.DataFrame(rows)

    return add_funnel_metrics(dataframe)


# ==========================================================
# DERIVED METRICS
# ==========================================================

def add_funnel_metrics(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add funnel conversion metrics to the dataset.
    """

    df = dataframe.copy()

    df["enquiry_to_test_drive"] = (
        df["test_drives"]
        / df["enquiries"]
    )

    df["test_drive_to_offer"] = (
        df["offers"]
        / df["test_drives"]
    )

    df["offer_to_sale"] = (
        df["sales"]
        / df["offers"]
    )

    df["enquiry_to_sale"] = (
        df["sales"]
        / df["enquiries"]
    )

    return df


# ==========================================================
# FILTERING
# ==========================================================

def filter_growth_data(
    dataframe: pd.DataFrame,
    month: Optional[str] = None,
    locations: Optional[List[str]] = None,
    segments: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Apply user-selected Growth Intelligence filters.
    """

    df = dataframe.copy()

    if month:
        df = df[
            df["month"] == month
        ]

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

    return df


# ==========================================================
# KPI SUMMARY
# ==========================================================

def growth_kpis(
    dataframe: pd.DataFrame,
) -> Dict[str, float]:
    """
    Calculate executive growth KPIs.
    """

    enquiries = float(
        dataframe["enquiries"].sum()
    )

    test_drives = float(
        dataframe["test_drives"].sum()
    )

    offers = float(
        dataframe["offers"].sum()
    )

    sales = float(
        dataframe["sales"].sum()
    )

    revenue = float(
        dataframe["revenue"].sum()
    )

    average_response = float(
        dataframe["response_minutes"]
        .mean()
    )

    return {
        "enquiries": enquiries,
        "test_drives": test_drives,
        "offers": offers,
        "sales": sales,
        "revenue": revenue,
        "enquiry_to_test_drive": (
            test_drives / enquiries
            if enquiries
            else 0.0
        ),
        "test_drive_to_offer": (
            offers / test_drives
            if test_drives
            else 0.0
        ),
        "offer_to_sale": (
            sales / offers
            if offers
            else 0.0
        ),
        "enquiry_to_sale": (
            sales / enquiries
            if enquiries
            else 0.0
        ),
        "average_response_minutes": (
            average_response
        ),
    }


# ==========================================================
# FUNNEL SUMMARY
# ==========================================================

def funnel_summary(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return the full commercial funnel.
    """

    kpis = growth_kpis(
        dataframe
    )

    stages = [
        {
            "stage": "Enquiries",
            "volume": int(
                kpis["enquiries"]
            ),
            "conversion_from_previous": 1.0,
        },
        {
            "stage": "Test Drives",
            "volume": int(
                kpis["test_drives"]
            ),
            "conversion_from_previous": (
                kpis[
                    "enquiry_to_test_drive"
                ]
            ),
        },
        {
            "stage": "Offers",
            "volume": int(
                kpis["offers"]
            ),
            "conversion_from_previous": (
                kpis[
                    "test_drive_to_offer"
                ]
            ),
        },
        {
            "stage": "Sales",
            "volume": int(
                kpis["sales"]
            ),
            "conversion_from_previous": (
                kpis[
                    "offer_to_sale"
                ]
            ),
        },
    ]

    return pd.DataFrame(stages)


# ==========================================================
# LOCATION PERFORMANCE
# ==========================================================

def location_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate funnel and revenue performance by location.
    """

    grouped = (
        dataframe
        .groupby(
            "location",
            as_index=False,
        )
        .agg(
            enquiries=(
                "enquiries",
                "sum",
            ),
            test_drives=(
                "test_drives",
                "sum",
            ),
            offers=(
                "offers",
                "sum",
            ),
            sales=(
                "sales",
                "sum",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
            response_minutes=(
                "response_minutes",
                "mean",
            ),
            inventory_age_days=(
                "inventory_age_days",
                "mean",
            ),
            price_index=(
                "price_index",
                "mean",
            ),
        )
    )

    grouped[
        "enquiry_to_test_drive"
    ] = (
        grouped["test_drives"]
        / grouped["enquiries"]
    )

    grouped[
        "enquiry_to_sale"
    ] = (
        grouped["sales"]
        / grouped["enquiries"]
    )

    return grouped.sort_values(
        "revenue",
        ascending=False,
    )


# ==========================================================
# SEGMENT PERFORMANCE
# ==========================================================

def segment_performance(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate commercial performance by vehicle segment.
    """

    grouped = (
        dataframe
        .groupby(
            "segment",
            as_index=False,
        )
        .agg(
            enquiries=(
                "enquiries",
                "sum",
            ),
            test_drives=(
                "test_drives",
                "sum",
            ),
            offers=(
                "offers",
                "sum",
            ),
            sales=(
                "sales",
                "sum",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
        )
    )

    grouped[
        "enquiry_to_test_drive"
    ] = (
        grouped["test_drives"]
        / grouped["enquiries"]
    )

    grouped[
        "enquiry_to_sale"
    ] = (
        grouped["sales"]
        / grouped["enquiries"]
    )

    return grouped.sort_values(
        "revenue",
        ascending=False,
    )


# ==========================================================
# REVENUE TREND
# ==========================================================

def monthly_growth_trend(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate revenue and funnel outcomes by month.
    """

    grouped = (
        dataframe
        .groupby(
            "month",
            as_index=False,
        )
        .agg(
            enquiries=(
                "enquiries",
                "sum",
            ),
            test_drives=(
                "test_drives",
                "sum",
            ),
            offers=(
                "offers",
                "sum",
            ),
            sales=(
                "sales",
                "sum",
            ),
            revenue=(
                "revenue",
                "sum",
            ),
        )
    )

    grouped[
        "enquiry_to_test_drive"
    ] = (
        grouped["test_drives"]
        / grouped["enquiries"]
    )

    grouped[
        "enquiry_to_sale"
    ] = (
        grouped["sales"]
        / grouped["enquiries"]
    )

    return grouped.sort_values(
        "month"
    )


# ==========================================================
# BENCHMARKS
# ==========================================================

def national_benchmarks(
    dataframe: pd.DataFrame,
) -> Dict[str, float]:
    """
    Calculate weighted national conversion benchmarks.
    """

    kpis = growth_kpis(
        dataframe
    )

    return {
        "enquiry_to_test_drive": (
            kpis[
                "enquiry_to_test_drive"
            ]
        ),
        "test_drive_to_offer": (
            kpis[
                "test_drive_to_offer"
            ]
        ),
        "offer_to_sale": (
            kpis[
                "offer_to_sale"
            ]
        ),
        "enquiry_to_sale": (
            kpis[
                "enquiry_to_sale"
            ]
        ),
    }


# ==========================================================
# OPPORTUNITY DETECTION
# ==========================================================

def detect_growth_opportunities(
    dataframe: pd.DataFrame,
) -> List[GrowthOpportunity]:
    """
    Detect meaningful conversion leakage and commercial
    opportunities.

    This engine is intentionally deterministic so the reasoning
    behind an opportunity is inspectable.
    """

    opportunities: List[
        GrowthOpportunity
    ] = []

    benchmarks = national_benchmarks(
        dataframe
    )

    benchmark_test_drive = benchmarks[
        "enquiry_to_test_drive"
    ]

    benchmark_sale = benchmarks[
        "enquiry_to_sale"
    ]

    for _, row in dataframe.iterrows():

        current_test_drive = float(
            row[
                "enquiry_to_test_drive"
            ]
        )

        current_sale = float(
            row[
                "enquiry_to_sale"
            ]
        )

        enquiries = float(
            row["enquiries"]
        )

        average_sale_price = float(
            row["average_sale_price"]
        )

        # ------------------------------------------
        # TEST DRIVE CONVERSION LEAKAGE
        # ------------------------------------------

        test_drive_gap = (
            benchmark_test_drive
            - current_test_drive
        )

        if test_drive_gap >= 0.08:

            additional_test_drives = (
                enquiries
                * test_drive_gap
            )

            downstream_conversion = (
                float(
                    row[
                        "test_drive_to_offer"
                    ]
                )
                * float(
                    row[
                        "offer_to_sale"
                    ]
                )
            )

            additional_sales = (
                additional_test_drives
                * downstream_conversion
            )

            revenue_upside = (
                additional_sales
                * average_sale_price
            )

            issue = (
                "Enquiry → test-drive conversion "
                "is materially below benchmark."
            )

            evidence = (
                f"{row['location']} "
                f"{row['segment']} converts "
                f"{current_test_drive:.0%} of enquiries "
                f"to test drives versus "
                f"{benchmark_test_drive:.0%} benchmark."
            )

            confidence = 0.88

            if (
                float(
                    row["response_minutes"]
                )
                >= 30
            ):
                evidence += (
                    f" Median response time is "
                    f"{row['response_minutes']:.0f} minutes."
                )

                confidence = 0.93

            opportunities.append(
                GrowthOpportunity(
                    priority="P0",
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    issue=issue,
                    evidence=evidence,
                    modeled_monthly_revenue_upside=round(
                        revenue_upside,
                        2,
                    ),
                    current_value=current_test_drive,
                    benchmark_value=benchmark_test_drive,
                    recommended_action=(
                        "Run a conversion intervention on "
                        "response time, vehicle pricing and "
                        "test-drive scheduling for this cohort."
                    ),
                    confidence=confidence,
                )
            )

        # ------------------------------------------
        # HIGH DEMAND / STRONG CONVERSION
        # ------------------------------------------

        if (
            current_sale
            >= benchmark_sale + 0.025
            and enquiries >= 100
        ):

            expansion_sales = (
                enquiries
                * 0.10
                * current_sale
            )

            revenue_upside = (
                expansion_sales
                * average_sale_price
            )

            opportunities.append(
                GrowthOpportunity(
                    priority="P1",
                    location=str(
                        row["location"]
                    ),
                    segment=str(
                        row["segment"]
                    ),
                    issue=(
                        "High demand and above-benchmark "
                        "conversion suggest inventory expansion."
                    ),
                    evidence=(
                        f"{row['location']} "
                        f"{row['segment']} enquiry-to-sale "
                        f"conversion is {current_sale:.1%} "
                        f"versus {benchmark_sale:.1%} benchmark."
                    ),
                    modeled_monthly_revenue_upside=round(
                        revenue_upside,
                        2,
                    ),
                    current_value=current_sale,
                    benchmark_value=benchmark_sale,
                    recommended_action=(
                        "Evaluate increasing acquisition "
                        "and inventory allocation for this cohort."
                    ),
                    confidence=0.84,
                )
            )

    opportunities.sort(
        key=lambda item: (
            item.priority,
            -item.modeled_monthly_revenue_upside,
        )
    )

    return opportunities


# ==========================================================
# LARGEST LEAKAGE
# ==========================================================

def largest_conversion_leakage(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Rank location / segment cohorts by the largest
    enquiry-to-test-drive gap versus national benchmark.
    """

    benchmark = national_benchmarks(
        dataframe
    )[
        "enquiry_to_test_drive"
    ]

    result = dataframe[
        [
            "location",
            "segment",
            "enquiries",
            "test_drives",
            "sales",
            "revenue",
            "response_minutes",
            "inventory_age_days",
            "price_index",
            "enquiry_to_test_drive",
            "enquiry_to_sale",
        ]
    ].copy()

    result[
        "benchmark_test_drive"
    ] = benchmark

    result[
        "conversion_gap"
    ] = (
        result[
            "enquiry_to_test_drive"
        ]
        - benchmark
    )

    return result.sort_values(
        "conversion_gap"
    )


# ==========================================================
# GROWTH EXECUTIVE SUMMARY
# ==========================================================

def growth_executive_summary(
    dataframe: pd.DataFrame,
) -> Dict[str, object]:
    """
    Produce a compact executive summary used by the UI.
    """

    kpis = growth_kpis(
        dataframe
    )

    opportunities = (
        detect_growth_opportunities(
            dataframe
        )
    )

    total_upside = sum(
        opportunity.modeled_monthly_revenue_upside
        for opportunity
        in opportunities
    )

    p0_count = sum(
        1
        for opportunity
        in opportunities
        if opportunity.priority == "P0"
    )

    p1_count = sum(
        1
        for opportunity
        in opportunities
        if opportunity.priority == "P1"
    )

    return {
        "kpis": kpis,
        "opportunity_count": len(
            opportunities
        ),
        "p0_count": p0_count,
        "p1_count": p1_count,
        "modeled_monthly_upside": round(
            total_upside,
            2,
        ),
        "top_opportunities": (
            opportunities[:5]
        ),
    }
