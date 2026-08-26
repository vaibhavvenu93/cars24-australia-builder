from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from engines.growth_intelligence import (
    LOCATIONS,
    MONTHS,
    SEGMENTS,
    detect_growth_opportunities,
    filter_growth_data,
    funnel_summary,
    growth_executive_summary,
    growth_kpis,
    largest_conversion_leakage,
    load_growth_data,
    location_performance,
    monthly_growth_trend,
    segment_performance,
)


# ==========================================================
# HELPERS
# ==========================================================


def _money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"

    return f"${value:,.0f}"


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _month_label(month: str) -> str:
    labels = {
        "2026-06": "June 2026",
        "2026-07": "July 2026",
        "2026-08": "August 2026",
    }

    return labels.get(
        month,
        month,
    )


def _priority_icon(
    priority: str,
) -> str:
    if priority == "P0":
        return "🔴"

    if priority == "P1":
        return "🟠"

    return "⚪"


def _header(
    title: str,
    description: str,
) -> None:
    st.markdown(
        '<div class="eyebrow">Growth Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.title(title)

    st.markdown(
        f'<div class="kicker">{description}</div>',
        unsafe_allow_html=True,
    )

    st.write("")


def _filter_controls(
    key_prefix: str,
):
    f1, f2, f3 = st.columns(
        [1.1, 2, 2]
    )

    with f1:
        month = st.selectbox(
            "Period",
            options=list(
                reversed(MONTHS)
            ),
            format_func=_month_label,
            key=f"{key_prefix}_month",
        )

    with f2:
        locations = st.multiselect(
            "Locations",
            options=LOCATIONS,
            default=LOCATIONS,
            key=f"{key_prefix}_locations",
        )

    with f3:
        segments = st.multiselect(
            "Vehicle segments",
            options=SEGMENTS,
            default=SEGMENTS,
            key=f"{key_prefix}_segments",
        )

    return (
        month,
        locations,
        segments,
    )


def _filtered_dataset(
    key_prefix: str,
) -> pd.DataFrame:
    raw = load_growth_data()

    month, locations, segments = (
        _filter_controls(
            key_prefix
        )
    )

    return filter_growth_data(
        raw,
        month=month,
        locations=locations,
        segments=segments,
    )


# ==========================================================
# GROWTH INTELLIGENCE
# ==========================================================


def render_growth_intelligence() -> None:

    _header(
        "Where is growth leaking?",
        (
            "Move from topline performance to the exact location, "
            "vehicle cohort and operating constraint responsible "
            "for revenue movement."
        ),
    )

    df = _filtered_dataset(
        "growth"
    )

    if df.empty:
        st.warning(
            "No operating cohorts match these filters."
        )
        return

    summary = growth_executive_summary(
        df
    )

    kpis = summary["kpis"]

    # ------------------------------------------------------
    # TOP KPIs
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Revenue",
        _money(
            kpis["revenue"]
        ),
    )

    k2.metric(
        "Sales",
        f"{int(kpis['sales']):,}",
    )

    k3.metric(
        "Enquiry → Sale",
        _percent(
            kpis[
                "enquiry_to_sale"
            ]
        ),
    )

    k4.metric(
        "Avg Response",
        (
            f"{kpis['average_response_minutes']:.0f} min"
        ),
    )

    k5.metric(
        "Modeled Upside",
        _money(
            summary[
                "modeled_monthly_upside"
            ]
        ),
    )

    st.write("")

    # ------------------------------------------------------
    # EXECUTIVE DIAGNOSIS
    # ------------------------------------------------------

    opportunities = summary[
        "top_opportunities"
    ]

    if opportunities:

        top = opportunities[0]

        with st.container(
            border=True
        ):
            c1, c2 = st.columns(
                [2.6, 1]
            )

            with c1:

                st.caption(
                    "TOP GROWTH SIGNAL"
                )

                st.markdown(
                    f"## {_priority_icon(top.priority)} "
                    f"{top.location} · {top.segment}"
                )

                st.markdown(
                    f"**{top.issue}**"
                )

                st.write(
                    top.evidence
                )

                st.caption(
                    f"Confidence: "
                    f"{top.confidence:.0%}"
                )

            with c2:

                st.caption(
                    "MODELED MONTHLY UPSIDE"
                )

                st.markdown(
                    "## "
                    + _money(
                        top.modeled_monthly_revenue_upside
                    )
                )

                st.write(
                    f"Current: "
                    f"**{_percent(top.current_value)}**"
                )

                st.write(
                    f"Benchmark: "
                    f"**{_percent(top.benchmark_value)}**"
                )

        action1, action2, action3 = st.columns(
            [1, 1, 1]
        )

        action1.button(
            "Investigate cohort",
            type="primary",
            key="growth_investigate",
            use_container_width=True,
        )

        action2.button(
            "Create experiment",
            key="growth_experiment",
            use_container_width=True,
        )

        action3.button(
            "Run scenario",
            key="growth_scenario",
            use_container_width=True,
        )

    st.divider()

    # ------------------------------------------------------
    # REVENUE TREND
    # ------------------------------------------------------

    st.subheader(
        "Growth trajectory"
    )

    st.caption(
        "Revenue and conversion performance across the synthetic "
        "Australian operating dataset."
    )

    raw = load_growth_data()

    trend = monthly_growth_trend(
        raw
    )

    trend_display = (
        trend[
            [
                "month",
                "revenue",
            ]
        ]
        .set_index(
            "month"
        )
    )

    st.line_chart(
        trend_display,
        height=290,
    )

    t1, t2 = st.columns(2)

    with t1:

        conversion_trend = (
            trend[
                [
                    "month",
                    "enquiry_to_test_drive",
                ]
            ]
            .set_index(
                "month"
            )
        )

        st.caption(
            "ENQUIRY → TEST DRIVE"
        )

        st.line_chart(
            conversion_trend,
            height=220,
        )

    with t2:

        sale_trend = (
            trend[
                [
                    "month",
                    "enquiry_to_sale",
                ]
            ]
            .set_index(
                "month"
            )
        )

        st.caption(
            "ENQUIRY → SALE"
        )

        st.line_chart(
            sale_trend,
            height=220,
        )

    st.divider()

    # ------------------------------------------------------
    # FUNNEL
    # ------------------------------------------------------

    st.subheader(
        "Commercial funnel"
    )

    funnel = funnel_summary(
        df
    )

    funnel_cols = st.columns(
        len(funnel)
    )

    previous_volume = None

    for index, row in funnel.iterrows():

        with funnel_cols[index]:

            volume = int(
                row["volume"]
            )

            st.caption(
                str(
                    row["stage"]
                ).upper()
            )

            st.markdown(
                f"## {volume:,}"
            )

            if previous_volume is None:
                st.caption(
                    "100% entry"
                )
            else:
                conversion = (
                    volume
                    / previous_volume
                    if previous_volume
                    else 0
                )

                st.caption(
                    f"{conversion:.1%} "
                    "from prior stage"
                )

            previous_volume = volume

    st.write("")

    funnel_chart = (
        funnel[
            [
                "stage",
                "volume",
            ]
        ]
        .set_index(
            "stage"
        )
    )

    st.bar_chart(
        funnel_chart,
        height=260,
    )

    st.divider()

    # ------------------------------------------------------
    # LOCATION PERFORMANCE
    # ------------------------------------------------------

    st.subheader(
        "Where is the business outperforming?"
    )

    location_df = (
        location_performance(
            df
        )
    )

    left, right = st.columns(
        [1.2, 1]
    )

    with left:

        location_revenue = (
            location_df[
                [
                    "location",
                    "revenue",
                ]
            ]
            .set_index(
                "location"
            )
        )

        st.caption(
            "REVENUE BY LOCATION"
        )

        st.bar_chart(
            location_revenue,
            height=320,
        )

    with right:

        location_conversion = (
            location_df[
                [
                    "location",
                    "enquiry_to_sale",
                ]
            ]
            .set_index(
                "location"
            )
        )

        st.caption(
            "ENQUIRY → SALE"
        )

        st.bar_chart(
            location_conversion,
            height=320,
        )

    location_table = (
        location_df[
            [
                "location",
                "enquiries",
                "sales",
                "revenue",
                "enquiry_to_test_drive",
                "enquiry_to_sale",
                "response_minutes",
                "inventory_age_days",
            ]
        ]
        .copy()
    )

    location_table[
        "Revenue"
    ] = location_table[
        "revenue"
    ].map(
        _money
    )

    location_table[
        "Enquiry → Test Drive"
    ] = location_table[
        "enquiry_to_test_drive"
    ].map(
        _percent
    )

    location_table[
        "Enquiry → Sale"
    ] = location_table[
        "enquiry_to_sale"
    ].map(
        _percent
    )

    location_table[
        "Response"
    ] = (
        location_table[
            "response_minutes"
        ]
        .round(0)
        .astype(int)
        .astype(str)
        + " min"
    )

    location_table[
        "Inventory Age"
    ] = (
        location_table[
            "inventory_age_days"
        ]
        .round(0)
        .astype(int)
        .astype(str)
        + " d"
    )

    location_table = location_table[
        [
            "location",
            "enquiries",
            "sales",
            "Revenue",
            "Enquiry → Test Drive",
            "Enquiry → Sale",
            "Response",
            "Inventory Age",
        ]
    ]

    location_table.columns = [
        "Location",
        "Enquiries",
        "Sales",
        "Revenue",
        "Enquiry → Test Drive",
        "Enquiry → Sale",
        "Response",
        "Inventory Age",
    ]

    st.dataframe(
        location_table,
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # ------------------------------------------------------
    # SEGMENT PERFORMANCE
    # ------------------------------------------------------

    st.subheader(
        "What is actually driving growth?"
    )

    segment_df = (
        segment_performance(
            df
        )
    )

    s1, s2 = st.columns(2)

    with s1:

        segment_revenue = (
            segment_df[
                [
                    "segment",
                    "revenue",
                ]
            ]
            .set_index(
                "segment"
            )
        )

        st.caption(
            "REVENUE BY SEGMENT"
        )

        st.bar_chart(
            segment_revenue,
            height=300,
        )

    with s2:

        segment_conversion = (
            segment_df[
                [
                    "segment",
                    "enquiry_to_sale",
                ]
            ]
            .set_index(
                "segment"
            )
        )

        st.caption(
            "CONVERSION BY SEGMENT"
        )

        st.bar_chart(
            segment_conversion,
            height=300,
        )

    st.divider()

    # ------------------------------------------------------
    # OPPORTUNITY QUEUE
    # ------------------------------------------------------

    st.subheader(
        "Growth Opportunity Queue"
    )

    st.caption(
        "System-detected opportunities ranked by modeled economic impact."
    )

    all_opportunities = (
        detect_growth_opportunities(
            df
        )
    )

    if not all_opportunities:

        st.success(
            "No material growth leakage detected for the selected cohort."
        )

    else:

        for index, opportunity in enumerate(
            all_opportunities[:8],
            start=1,
        ):

            with st.container(
                border=True
            ):

                top_left, top_right = (
                    st.columns(
                        [3, 1]
                    )
                )

                with top_left:

                    st.caption(
                        f"{opportunity.priority} · "
                        f"OPPORTUNITY {index:02d}"
                    )

                    st.markdown(
                        f"### {_priority_icon(opportunity.priority)} "
                        f"{opportunity.location} · "
                        f"{opportunity.segment}"
                    )

                    st.markdown(
                        f"**{opportunity.issue}**"
                    )

                with top_right:

                    st.caption(
                        "MODELED UPSIDE"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            opportunity.modeled_monthly_revenue_upside
                        )
                    )

                st.write(
                    opportunity.evidence
                )

                st.markdown(
                    "**Recommended action**"
                )

                st.write(
                    opportunity.recommended_action
                )

                m1, m2, m3 = st.columns(3)

                m1.metric(
                    "Current",
                    _percent(
                        opportunity.current_value
                    ),
                )

                m2.metric(
                    "Benchmark",
                    _percent(
                        opportunity.benchmark_value
                    ),
                )

                m3.metric(
                    "Confidence",
                    f"{opportunity.confidence:.0%}",
                )

    st.caption(
        "All growth analytics use synthetic CARS24 Australia operating data."
    )


# ==========================================================
# FUNNEL ANALYTICS
# ==========================================================


def render_funnel_analytics() -> None:

    _header(
        "Funnel Analytics",
        (
            "Find the exact stage where customer intent stops "
            "turning into transactions."
        ),
    )

    df = _filtered_dataset(
        "funnel"
    )

    if df.empty:
        st.warning(
            "No cohorts match these filters."
        )
        return

    kpis = growth_kpis(
        df
    )

    funnel = funnel_summary(
        df
    )

    # ------------------------------------------------------
    # KPI STRIP
    # ------------------------------------------------------

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Enquiry → Test Drive",
        _percent(
            kpis[
                "enquiry_to_test_drive"
            ]
        ),
    )

    k2.metric(
        "Test Drive → Offer",
        _percent(
            kpis[
                "test_drive_to_offer"
            ]
        ),
    )

    k3.metric(
        "Offer → Sale",
        _percent(
            kpis[
                "offer_to_sale"
            ]
        ),
    )

    k4.metric(
        "End-to-End Conversion",
        _percent(
            kpis[
                "enquiry_to_sale"
            ]
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # FUNNEL VISUAL
    # ------------------------------------------------------

    st.subheader(
        "Customer journey"
    )

    cols = st.columns(4)

    previous = None

    for index, row in funnel.iterrows():

        volume = int(
            row["volume"]
        )

        with cols[index]:

            with st.container(
                border=True
            ):

                st.caption(
                    str(
                        row["stage"]
                    ).upper()
                )

                st.markdown(
                    f"## {volume:,}"
                )

                if previous is not None:

                    drop = (
                        1
                        - (
                            volume
                            / previous
                        )
                        if previous
                        else 0
                    )

                    st.caption(
                        f"{drop:.1%} drop-off"
                    )

        previous = volume

    st.write("")

    st.bar_chart(
        funnel[
            [
                "stage",
                "volume",
            ]
        ].set_index(
            "stage"
        ),
        height=300,
    )

    st.divider()

    # ------------------------------------------------------
    # LEAKAGE
    # ------------------------------------------------------

    st.subheader(
        "Largest conversion disagreements"
    )

    leakage = (
        largest_conversion_leakage(
            df
        )
    )

    for _, row in leakage.head(
        8
    ).iterrows():

        gap = float(
            row[
                "conversion_gap"
            ]
        )

        with st.container(
            border=True
        ):

            l1, l2, l3, l4 = st.columns(
                [2, 1, 1, 1]
            )

            with l1:

                st.markdown(
                    f"### {row['location']} · "
                    f"{row['segment']}"
                )

                st.caption(
                    f"{int(row['enquiries']):,} enquiries"
                )

            with l2:

                st.caption(
                    "CURRENT"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "enquiry_to_test_drive"
                            ]
                        )
                    )
                )

            with l3:

                st.caption(
                    "BENCHMARK"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "benchmark_test_drive"
                            ]
                        )
                    )
                )

            with l4:

                st.caption(
                    "GAP"
                )

                st.markdown(
                    "### "
                    + f"{gap * 100:+.1f}pp"
                )

            if gap < -0.05:

                st.error(
                    (
                        f"Response time: "
                        f"{row['response_minutes']:.0f} min · "
                        f"Inventory age: "
                        f"{row['inventory_age_days']:.0f} days · "
                        f"Price index: "
                        f"{row['price_index']:.3f}"
                    )
                )

    st.caption(
        "Synthetic funnel diagnostics. Benchmark is calculated "
        "from the selected operating cohort."
    )


# ==========================================================
# MARKET INTELLIGENCE
# ==========================================================


def render_market_intelligence() -> None:

    _header(
        "Market Intelligence",
        (
            "Use demand and conversion evidence to decide where "
            "inventory should be acquired, allocated and expanded."
        ),
    )

    df = _filtered_dataset(
        "market"
    )

    if df.empty:
        st.warning(
            "No cohorts match these filters."
        )
        return

    location_df = (
        location_performance(
            df
        )
    )

    opportunities = (
        detect_growth_opportunities(
            df
        )
    )

    expansion = [
        opportunity
        for opportunity
        in opportunities
        if opportunity.priority == "P1"
    ]

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Markets monitored",
        df[
            "location"
        ].nunique(),
    )

    m2.metric(
        "Expansion signals",
        len(
            expansion
        ),
    )

    m3.metric(
        "Expansion upside",
        _money(
            sum(
                item.modeled_monthly_revenue_upside
                for item
                in expansion
            )
        ),
    )

    st.divider()

    st.subheader(
        "Market attractiveness"
    )

    market_view = (
        location_df[
            [
                "location",
                "enquiries",
                "sales",
                "revenue",
                "enquiry_to_sale",
                "inventory_age_days",
                "price_index",
            ]
        ]
        .copy()
    )

    # Higher demand + better conversion + younger stock
    # creates a simple explainable opportunity score.
    market_view[
        "demand_score"
    ] = (
        market_view[
            "enquiries"
        ]
        / market_view[
            "enquiries"
        ].max()
        * 100
    )

    market_view[
        "conversion_score"
    ] = (
        market_view[
            "enquiry_to_sale"
        ]
        / market_view[
            "enquiry_to_sale"
        ].max()
        * 100
    )

    max_age = market_view[
        "inventory_age_days"
    ].max()

    market_view[
        "velocity_score"
    ] = (
        1
        - (
            market_view[
                "inventory_age_days"
            ]
            / max_age
        )
    ) * 100

    market_view[
        "opportunity_score"
    ] = (
        market_view[
            "demand_score"
        ]
        * 0.45
        + market_view[
            "conversion_score"
        ]
        * 0.35
        + market_view[
            "velocity_score"
        ]
        * 0.20
    )

    market_chart = (
        market_view[
            [
                "location",
                "opportunity_score",
            ]
        ]
        .sort_values(
            "opportunity_score",
            ascending=False,
        )
        .set_index(
            "location"
        )
    )

    st.bar_chart(
        market_chart,
        height=320,
    )

    st.write("")

    ranked = market_view.sort_values(
        "opportunity_score",
        ascending=False,
    )

    for rank, (_, row) in enumerate(
        ranked.iterrows(),
        start=1,
    ):

        with st.container(
            border=True
        ):

            r1, r2, r3, r4, r5 = st.columns(
                [2.2, 1, 1, 1, 1]
            )

            with r1:

                st.caption(
                    f"MARKET #{rank}"
                )

                st.markdown(
                    f"### {row['location']}"
                )

            with r2:

                st.caption(
                    "OPPORTUNITY"
                )

                st.markdown(
                    f"### {row['opportunity_score']:.0f}"
                )

            with r3:

                st.caption(
                    "DEMAND"
                )

                st.markdown(
                    f"### {row['demand_score']:.0f}"
                )

            with r4:

                st.caption(
                    "CONVERSION"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "enquiry_to_sale"
                            ]
                        )
                    )
                )

            with r5:

                st.caption(
                    "STOCK AGE"
                )

                st.markdown(
                    f"### {row['inventory_age_days']:.0f}d"
                )

    if expansion:

        st.divider()

        st.subheader(
            "Acquisition & allocation signals"
        )

        for opportunity in expansion:

            with st.container(
                border=True
            ):

                c1, c2 = st.columns(
                    [3, 1]
                )

                with c1:

                    st.markdown(
                        f"### {opportunity.location} · "
                        f"{opportunity.segment}"
                    )

                    st.write(
                        opportunity.evidence
                    )

                    st.markdown(
                        "**Recommendation:** "
                        + opportunity.recommended_action
                    )

                with c2:

                    st.caption(
                        "MODELED UPSIDE"
                    )

                    st.markdown(
                        "## "
                        + _money(
                            opportunity.modeled_monthly_revenue_upside
                        )
                    )

                    st.caption(
                        f"{opportunity.confidence:.0%} confidence"
                    )

    st.caption(
        "Market Intelligence uses synthetic demand and conversion evidence."
    )
