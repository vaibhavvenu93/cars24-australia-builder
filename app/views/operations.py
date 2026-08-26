from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from engines.operations_intelligence import (
    LOCATIONS,
    VENDORS,
    detect_operations_actions,
    filter_recon_data,
    load_location_operations,
    load_recon_data,
    load_transfer_candidates,
    location_performance,
    operations_summary,
    transfer_recommendations,
    vendor_performance,
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


def _priority_icon(priority: str) -> str:
    if priority == "P0":
        return "🔴"

    if priority == "P1":
        return "🟠"

    return "🟢"


def _header(
    eyebrow: str,
    title: str,
    description: str,
) -> None:
    st.markdown(
        f'<div class="eyebrow">{eyebrow}</div>',
        unsafe_allow_html=True,
    )

    st.title(title)

    st.markdown(
        f'<div class="kicker">{description}</div>',
        unsafe_allow_html=True,
    )

    st.write("")


# ==========================================================
# LOCATION PERFORMANCE
# ==========================================================


def render_location_performance() -> None:

    _header(
        "Operations Intelligence",
        "Which location is actually working?",
        (
            "Compare locations on throughput, conversion, "
            "inventory velocity, recon speed and operating contribution."
        ),
    )

    df = location_performance()

    # ------------------------------------------------------
    # TOP KPIs
    # ------------------------------------------------------

    total_sales = int(
        df["sales"].sum()
    )

    total_contribution = float(
        df[
            "operating_contribution"
        ].sum()
    )

    avg_recon = float(
        df[
            "recon_days"
        ].mean()
    )

    avg_conversion = float(
        df[
            "conversion_rate"
        ].mean()
    )

    avg_inventory_age = float(
        df[
            "avg_inventory_age"
        ].mean()
    )

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Network Sales",
        f"{total_sales:,}",
    )

    k2.metric(
        "Operating Contribution",
        _money(
            total_contribution
        ),
    )

    k3.metric(
        "Avg Conversion",
        _percent(
            avg_conversion
        ),
    )

    k4.metric(
        "Avg Recon",
        f"{avg_recon:.1f}d",
    )

    k5.metric(
        "Avg Inventory Age",
        f"{avg_inventory_age:.1f}d",
    )

    st.divider()

    # ------------------------------------------------------
    # OPERATING SCORE
    # ------------------------------------------------------

    st.subheader(
        "Network operating score"
    )

    st.caption(
        "Composite view across contribution, velocity, "
        "inventory age, recon throughput and lead response."
    )

    score_chart = (
        df[
            [
                "location",
                "operating_score",
            ]
        ]
        .set_index(
            "location"
        )
    )

    st.bar_chart(
        score_chart,
        height=320,
    )

    st.write("")

    # ------------------------------------------------------
    # LOCATION CARDS
    # ------------------------------------------------------

    for rank, (_, row) in enumerate(
        df.iterrows(),
        start=1,
    ):

        with st.container(
            border=True
        ):

            c1, c2, c3, c4, c5 = st.columns(
                [2, 1, 1, 1, 1]
            )

            with c1:

                st.caption(
                    f"LOCATION #{rank}"
                )

                st.markdown(
                    f"### {row['location']}"
                )

                st.caption(
                    f"Operating score: "
                    f"{row['operating_score']:.0f}/100"
                )

            with c2:

                st.caption(
                    "CONTRIBUTION"
                )

                st.markdown(
                    "### "
                    + _money(
                        float(
                            row[
                                "operating_contribution"
                            ]
                        )
                    )
                )

            with c3:

                st.caption(
                    "CONVERSION"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "conversion_rate"
                            ]
                        )
                    )
                )

            with c4:

                st.caption(
                    "RECON"
                )

                st.markdown(
                    f"### {row['recon_days']:.1f}d"
                )

            with c5:

                st.caption(
                    "INVENTORY AGE"
                )

                st.markdown(
                    f"### {row['avg_inventory_age']:.1f}d"
                )

            st.divider()

            d1, d2, d3 = st.columns(3)

            d1.metric(
                "Vehicles",
                int(
                    row[
                        "vehicles"
                    ]
                ),
            )

            d2.metric(
                "Sales / 100 Vehicles",
                f"{row['sales_per_100_vehicles']:.1f}",
            )

            d3.metric(
                "Lead Response",
                (
                    f"{row['lead_response_minutes']:.0f} min"
                ),
            )

            if row["location"] == "Melbourne":

                st.error(
                    (
                        "Melbourne is the clearest operating constraint: "
                        f"{row['recon_days']:.1f}d recon, "
                        f"{row['lead_response_minutes']:.0f} min lead response, "
                        f"{row['conversion_rate']:.1%} conversion and "
                        f"{row['avg_inventory_age']:.1f}d average inventory age."
                    )
                )

            elif (
                row[
                    "operating_score"
                ]
                == df[
                    "operating_score"
                ].max()
            ):

                st.success(
                    "Current network operating benchmark."
                )

    st.divider()

    # ------------------------------------------------------
    # COMPARISON TABLE
    # ------------------------------------------------------

    st.subheader(
        "Location comparison"
    )

    display = df.copy()

    display[
        "Contribution"
    ] = display[
        "operating_contribution"
    ].map(
        _money
    )

    display[
        "Gross Profit"
    ] = display[
        "gross_profit"
    ].map(
        _money
    )

    display[
        "Conversion"
    ] = display[
        "conversion_rate"
    ].map(
        _percent
    )

    display[
        "Recon"
    ] = (
        display[
            "recon_days"
        ]
        .round(1)
        .astype(str)
        + "d"
    )

    display[
        "Inventory Age"
    ] = (
        display[
            "avg_inventory_age"
        ]
        .round(1)
        .astype(str)
        + "d"
    )

    display[
        "Response"
    ] = (
        display[
            "lead_response_minutes"
        ]
        .round(0)
        .astype(int)
        .astype(str)
        + " min"
    )

    display[
        "Score"
    ] = (
        display[
            "operating_score"
        ]
        .round(0)
        .astype(int)
    )

    st.dataframe(
        display[
            [
                "location",
                "vehicles",
                "sales",
                "Contribution",
                "Conversion",
                "Recon",
                "Inventory Age",
                "Response",
                "Score",
            ]
        ].rename(
            columns={
                "location": "Location",
                "vehicles": "Vehicles",
                "sales": "Sales",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# VENDOR INTELLIGENCE
# ==========================================================


def render_vendor_intelligence() -> None:

    _header(
        "Operations Intelligence",
        "Which vendor is actually cheapest?",
        (
            "Invoice price alone is misleading. Compare vendors "
            "on actual cost, turnaround, SLA breaches, rework "
            "and downstream operating impact."
        ),
    )

    raw = load_recon_data()

    f1, f2 = st.columns(
        [1.4, 2.5]
    )

    with f1:

        locations = st.multiselect(
            "Locations",
            options=LOCATIONS,
            default=LOCATIONS,
            key="vendor_locations",
        )

    with f2:

        vendors = st.multiselect(
            "Vendors",
            options=VENDORS,
            default=VENDORS,
            key="vendor_vendors",
        )

    df = filter_recon_data(
        raw,
        locations=locations,
        vendors=vendors,
    )

    if df.empty:
        st.warning(
            "No recon jobs match these filters."
        )
        return

    vendor_df = vendor_performance(
        df
    )

    # ------------------------------------------------------
    # KPIs
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Recon Jobs",
        f"{len(df):,}",
    )

    k2.metric(
        "Avg Turnaround",
        (
            f"{df['turnaround_days'].mean():.1f}d"
        ),
    )

    k3.metric(
        "SLA Breach",
        _percent(
            float(
                df[
                    "sla_breach"
                ].mean()
            )
        ),
    )

    k4.metric(
        "Rework Rate",
        _percent(
            float(
                df[
                    "rework_required"
                ].mean()
            )
        ),
    )

    k5.metric(
        "Cost Variance",
        _money(
            float(
                df[
                    "cost_variance"
                ].sum()
            )
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # VENDOR SCORE
    # ------------------------------------------------------

    st.subheader(
        "True vendor performance"
    )

    st.caption(
        "Higher score = better combination of cost, speed, quality and SLA performance."
    )

    score_chart = (
        vendor_df[
            [
                "vendor",
                "vendor_score",
            ]
        ]
        .set_index(
            "vendor"
        )
    )

    st.bar_chart(
        score_chart,
        height=320,
    )

    st.write("")

    # ------------------------------------------------------
    # VENDOR CARDS
    # ------------------------------------------------------

    for rank, (_, row) in enumerate(
        vendor_df.iterrows(),
        start=1,
    ):

        with st.container(
            border=True
        ):

            c1, c2, c3, c4, c5 = st.columns(
                [2.2, 1, 1, 1, 1]
            )

            with c1:

                st.caption(
                    f"VENDOR #{rank}"
                )

                st.markdown(
                    f"### {row['vendor']}"
                )

                st.caption(
                    f"{int(row['jobs'])} jobs"
                )

            with c2:

                st.caption(
                    "SCORE"
                )

                st.markdown(
                    f"### {row['vendor_score']:.0f}"
                )

            with c3:

                st.caption(
                    "TURNAROUND"
                )

                st.markdown(
                    f"### {row['avg_turnaround_days']:.1f}d"
                )

            with c4:

                st.caption(
                    "SLA BREACH"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "sla_breach_rate"
                            ]
                        )
                    )
                )

            with c5:

                st.caption(
                    "REWORK"
                )

                st.markdown(
                    "### "
                    + _percent(
                        float(
                            row[
                                "rework_rate"
                            ]
                        )
                    )
                )

            st.write("")

            if row[
                "cost_overrun"
            ] > 0:

                st.warning(
                    (
                        "Actual vendor cost is "
                        + _money(
                            float(
                                row[
                                    "cost_overrun"
                                ]
                            )
                        )
                        + " above quoted cost across the selected jobs."
                    )
                )

            if (
                row[
                    "vendor_score"
                ]
                < 78
            ):

                st.error(
                    "Vendor performance is below the review threshold."
                )

    st.divider()

    # ------------------------------------------------------
    # MELBOURNE ROOT CAUSE
    # ------------------------------------------------------

    melbourne = df[
        df[
            "location"
        ]
        == "Melbourne"
    ]

    if not melbourne.empty:

        st.subheader(
            "Melbourne recon diagnosis"
        )

        melbourne_vendor = (
            vendor_performance(
                melbourne
            )
        )

        if not melbourne_vendor.empty:

            weakest = (
                melbourne_vendor
                .sort_values(
                    "vendor_score"
                )
                .iloc[0]
            )

            with st.container(
                border=True
            ):

                left, right = st.columns(
                    [2.6, 1]
                )

                with left:

                    st.caption(
                        "ROOT CAUSE SIGNAL"
                    )

                    st.markdown(
                        f"## 🔴 {weakest['vendor']}"
                    )

                    st.write(
                        (
                            f"Average turnaround: "
                            f"**{weakest['avg_turnaround_days']:.1f} days** · "
                            f"SLA breach: "
                            f"**{weakest['sla_breach_rate']:.0%}** · "
                            f"Rework: "
                            f"**{weakest['rework_rate']:.0%}**"
                        )
                    )

                    st.write(
                        "This vendor appears to be contributing disproportionately "
                        "to Melbourne's recon slowdown."
                    )

                with right:

                    st.metric(
                        "Vendor Score",
                        f"{weakest['vendor_score']:.0f}/100",
                    )

            b1, b2, b3 = st.columns(3)

            b1.button(
                "Review job evidence",
                type="primary",
                use_container_width=True,
            )

            b2.button(
                "Model vendor reallocation",
                use_container_width=True,
            )

            b3.button(
                "Create vendor action",
                use_container_width=True,
            )


# ==========================================================
# TRANSFER INTELLIGENCE
# ==========================================================


def render_transfer_intelligence() -> None:

    _header(
        "Operations Intelligence",
        "Should this car really be here?",
        (
            "Match ageing inventory against regional demand and compare "
            "the economics of holding, repricing or transferring."
        ),
    )

    candidates = (
        load_transfer_candidates()
    )

    recommendations = (
        transfer_recommendations(
            candidates
        )
    )

    total_upside = sum(
        item.modeled_margin_gain
        for item in recommendations
    )

    avg_days_saved = (
        sum(
            item.days_saved
            for item in recommendations
        )
        / len(
            recommendations
        )
        if recommendations
        else 0
    )

    # ------------------------------------------------------
    # KPI STRIP
    # ------------------------------------------------------

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Vehicles Evaluated",
        len(
            candidates
        ),
    )

    k2.metric(
        "Transfer Opportunities",
        len(
            recommendations
        ),
    )

    k3.metric(
        "Modeled Margin Upside",
        _money(
            total_upside
        ),
    )

    k4.metric(
        "Avg Days Saved",
        f"{avg_days_saved:.1f}d",
    )

    st.divider()

    # ------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------

    st.subheader(
        "Best transfer opportunities"
    )

    if not recommendations:

        st.success(
            "No transfers currently outperform holding economics."
        )
        return

    for rank, recommendation in enumerate(
        recommendations[:12],
        start=1,
    ):

        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                [2.4, 1.2, 1, 1]
            )

            with c1:

                st.caption(
                    f"TRANSFER #{rank:02d}"
                )

                st.markdown(
                    f"### {recommendation.make_model}"
                )

                st.caption(
                    f"{recommendation.vehicle_id} · "
                    f"{recommendation.segment}"
                )

                st.markdown(
                    (
                        f"**{recommendation.origin} "
                        f"→ {recommendation.destination}**"
                    )
                )

            with c2:

                st.caption(
                    "DEMAND SHIFT"
                )

                st.markdown(
                    (
                        f"### {recommendation.origin_demand:.0f} "
                        f"→ {recommendation.destination_demand:.0f}"
                    )
                )

            with c3:

                st.caption(
                    "TRANSFER COST"
                )

                st.markdown(
                    "### "
                    + _money(
                        recommendation.transfer_cost
                    )
                )

            with c4:

                st.caption(
                    "MARGIN GAIN"
                )

                st.markdown(
                    "### "
                    + _money(
                        recommendation.modeled_margin_gain
                    )
                )

            st.write(
                (
                    f"Modeled to save approximately "
                    f"**{recommendation.days_saved:.1f} inventory days** "
                    f"with **{recommendation.confidence:.0%} confidence**."
                )
            )

            b1, b2, b3 = st.columns(3)

            b1.button(
                "Compare hold vs transfer",
                key=(
                    "transfer_compare_"
                    + recommendation.vehicle_id
                ),
                type="primary",
                use_container_width=True,
            )

            b2.button(
                "Approve transfer",
                key=(
                    "transfer_approve_"
                    + recommendation.vehicle_id
                ),
                use_container_width=True,
            )

            b3.button(
                "Open vehicle",
                key=(
                    "transfer_vehicle_"
                    + recommendation.vehicle_id
                ),
                use_container_width=True,
            )

    st.divider()

    # ------------------------------------------------------
    # MARKET FLOW
    # ------------------------------------------------------

    st.subheader(
        "Inventory flow opportunity"
    )

    route_df = candidates[
        [
            "origin",
            "destination",
            "modeled_margin_gain",
        ]
    ].copy()

    route_summary = (
        route_df
        .groupby(
            [
                "origin",
                "destination",
            ],
            as_index=False,
        )
        .agg(
            vehicles=(
                "modeled_margin_gain",
                "count",
            ),
            modeled_margin_gain=(
                "modeled_margin_gain",
                "sum",
            ),
        )
        .sort_values(
            "modeled_margin_gain",
            ascending=False,
        )
    )

    route_summary[
        "Route"
    ] = (
        route_summary[
            "origin"
        ]
        + " → "
        + route_summary[
            "destination"
        ]
    )

    route_summary[
        "Modeled Margin"
    ] = route_summary[
        "modeled_margin_gain"
    ].map(
        _money
    )

    st.dataframe(
        route_summary[
            [
                "Route",
                "vehicles",
                "Modeled Margin",
            ]
        ].rename(
            columns={
                "vehicles": "Vehicles Evaluated",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# ACTION CENTRE
# ==========================================================


def render_action_centre() -> None:

    _header(
        "Execution Layer",
        "What should the team do next?",
        (
            "One ranked operating queue across location performance, "
            "recon bottlenecks, vendor economics and inventory movement."
        ),
    )

    summary = (
        operations_summary()
    )

    actions = (
        detect_operations_actions()
    )

    # ------------------------------------------------------
    # TOP KPIs
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(
        5
    )

    k1.metric(
        "Open Actions",
        int(
            summary[
                "open_actions"
            ]
        ),
    )

    k2.metric(
        "Recon SLA Breach",
        _percent(
            float(
                summary[
                    "sla_breach_rate"
                ]
            )
        ),
    )

    k3.metric(
        "Rework Rate",
        _percent(
            float(
                summary[
                    "rework_rate"
                ]
            )
        ),
    )

    k4.metric(
        "Transfer Opportunities",
        int(
            summary[
                "transfer_opportunities"
            ]
        ),
    )

    k5.metric(
        "Transfer Upside",
        _money(
            float(
                summary[
                    "transfer_margin_upside"
                ]
            )
        ),
    )

    st.write("")

    # ------------------------------------------------------
    # FILTER
    # ------------------------------------------------------

    action_types = sorted(
        {
            action.action_type
            for action in actions
        }
    )

    f1, f2 = st.columns(
        2
    )

    with f1:

        priorities = st.multiselect(
            "Priority",
            options=[
                "P0",
                "P1",
                "P2",
            ],
            default=[
                "P0",
                "P1",
                "P2",
            ],
        )

    with f2:

        selected_types = st.multiselect(
            "Action type",
            options=action_types,
            default=action_types,
        )

    filtered_actions = [
        action
        for action in actions
        if (
            action.priority
            in priorities
            and action.action_type
            in selected_types
        )
    ]

    st.divider()

    # ------------------------------------------------------
    # MANAGEMENT VIEW
    # ------------------------------------------------------

    p0_count = sum(
        1
        for action in filtered_actions
        if action.priority == "P0"
    )

    p1_count = sum(
        1
        for action in filtered_actions
        if action.priority == "P1"
    )

    total_impact = sum(
        action.expected_impact
        for action in filtered_actions
    )

    with st.container(
        border=True
    ):

        c1, c2, c3 = st.columns(
            [1, 1, 2]
        )

        c1.metric(
            "P0",
            p0_count,
        )

        c2.metric(
            "P1",
            p1_count,
        )

        c3.metric(
            "Modeled Economic Impact",
            _money(
                total_impact
            ),
        )

    st.write("")

    # ------------------------------------------------------
    # ACTION QUEUE
    # ------------------------------------------------------

    if not filtered_actions:

        st.success(
            "No actions match the current filters."
        )

    else:

        for rank, action in enumerate(
            filtered_actions,
            start=1,
        ):

            with st.container(
                border=True
            ):

                top_left, top_right = st.columns(
                    [3, 1]
                )

                with top_left:

                    st.caption(
                        f"{action.priority} · "
                        f"ACTION {rank:02d} · "
                        f"{action.action_type.upper()}"
                    )

                    st.markdown(
                        f"### {_priority_icon(action.priority)} "
                        f"{action.entity}"
                    )

                    st.markdown(
                        f"**{action.issue}**"
                    )

                    st.write(
                        action.evidence
                    )

                with top_right:

                    st.caption(
                        "MODELED IMPACT"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            action.expected_impact
                        )
                    )

                    st.caption(
                        f"{action.confidence:.0%} confidence"
                    )

                st.markdown(
                    "**Recommended action**"
                )

                st.write(
                    action.recommended_action
                )

                st.caption(
                    f"Location: {action.location}"
                )

                b1, b2, b3, b4 = st.columns(
                    4
                )

                b1.button(
                    "Accept",
                    key=(
                        f"accept_{rank}_"
                        f"{action.entity}"
                    ),
                    type="primary",
                    use_container_width=True,
                )

                b2.button(
                    "Assign",
                    key=(
                        f"assign_{rank}_"
                        f"{action.entity}"
                    ),
                    use_container_width=True,
                )

                b3.button(
                    "Investigate",
                    key=(
                        f"investigate_{rank}_"
                        f"{action.entity}"
                    ),
                    use_container_width=True,
                )

                b4.button(
                    "Dismiss",
                    key=(
                        f"dismiss_{rank}_"
                        f"{action.entity}"
                    ),
                    use_container_width=True,
                )

    st.divider()

    # ------------------------------------------------------
    # AUTOMATION CONCEPT
    # ------------------------------------------------------

    st.subheader(
        "How this becomes automated"
    )

    a1, a2, a3, a4 = st.columns(
        4
    )

    with a1:

        with st.container(
            border=True
        ):

            st.caption(
                "01 · DETECT"
            )

            st.markdown(
                "**Observe operational signals**"
            )

            st.caption(
                "CRM, inventory, recon, logistics and market data."
            )

    with a2:

        with st.container(
            border=True
        ):

            st.caption(
                "02 · REASON"
            )

            st.markdown(
                "**Calculate impact**"
            )

            st.caption(
                "Benchmarks, unit economics, risk and opportunity."
            )

    with a3:

        with st.container(
            border=True
        ):

            st.caption(
                "03 · ACT"
            )

            st.markdown(
                "**Route next-best action**"
            )

            st.caption(
                "Assign owner, trigger workflow or request approval."
            )

    with a4:

        with st.container(
            border=True
        ):

            st.caption(
                "04 · LEARN"
            )

            st.markdown(
                "**Measure the outcome**"
            )

            st.caption(
                "Feed intervention results back into the operating model."
            )

    st.caption(
        "Operations data and recommendations are synthetic."
    )
