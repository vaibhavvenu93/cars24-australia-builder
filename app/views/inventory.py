from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st

from engines.inventory_intelligence import (
    LOCATIONS,
    MAKES,
    SEGMENTS,
    ageing_summary,
    capital_intelligence,
    detect_inventory_decisions,
    filter_inventory_data,
    get_vehicle,
    inventory_kpis,
    load_inventory_data,
    location_inventory_performance,
    model_performance,
    vehicle_decisions,
)


# ==========================================================
# CONSTANTS
# ==========================================================

STATUSES = [
    "Healthy",
    "Watch",
    "Ageing",
    "Critical",
]


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


def _status_icon(status: str) -> str:
    icons = {
        "Healthy": "🟢",
        "Watch": "🟡",
        "Ageing": "🟠",
        "Critical": "🔴",
    }

    return icons.get(
        status,
        "⚪",
    )


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


def _filters(
    key_prefix: str,
) -> pd.DataFrame:

    data = load_inventory_data()

    f1, f2, f3, f4 = st.columns(
        [1.4, 1.4, 1.7, 1.7]
    )

    with f1:
        locations = st.multiselect(
            "Locations",
            options=LOCATIONS,
            default=LOCATIONS,
            key=f"{key_prefix}_locations",
        )

    with f2:
        segments = st.multiselect(
            "Segments",
            options=SEGMENTS,
            default=SEGMENTS,
            key=f"{key_prefix}_segments",
        )

    with f3:
        makes = st.multiselect(
            "Makes",
            options=MAKES,
            default=MAKES,
            key=f"{key_prefix}_makes",
        )

    with f4:
        statuses = st.multiselect(
            "Inventory state",
            options=STATUSES,
            default=STATUSES,
            key=f"{key_prefix}_statuses",
        )

    return filter_inventory_data(
        data,
        locations=locations,
        segments=segments,
        makes=makes,
        statuses=statuses,
    )


# ==========================================================
# PORTFOLIO
# ==========================================================


def render_portfolio() -> None:

    _header(
        "Inventory Intelligence",
        "Every vehicle is a capital decision.",
        (
            "See the portfolio through economics, ageing, demand "
            "and expected next-best action rather than inventory "
            "count alone."
        ),
    )

    df = _filters(
        "portfolio"
    )

    if df.empty:
        st.warning(
            "No vehicles match these filters."
        )
        return

    kpis = inventory_kpis(
        df
    )

    # ------------------------------------------------------
    # KPI STRIP
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Vehicles",
        f"{kpis['vehicles']:,}",
    )

    k2.metric(
        "Capital Deployed",
        _money(
            kpis[
                "capital_deployed"
            ]
        ),
    )

    k3.metric(
        "Expected Contribution",
        _money(
            kpis[
                "expected_contribution"
            ]
        ),
    )

    k4.metric(
        "Average Age",
        (
            f"{kpis['average_age_days']:.1f}d"
        ),
    )

    k5.metric(
        "Capital at Risk",
        _money(
            kpis[
                "capital_at_risk"
            ]
        ),
    )

    st.write("")

    # ------------------------------------------------------
    # PORTFOLIO DIAGNOSIS
    # ------------------------------------------------------

    decisions = detect_inventory_decisions(
        df
    )

    p0 = [
        decision
        for decision in decisions
        if decision.priority == "P0"
    ]

    p1 = [
        decision
        for decision in decisions
        if decision.priority == "P1"
    ]

    with st.container(
        border=True
    ):

        d1, d2, d3, d4 = st.columns(
            [1.5, 1, 1, 1]
        )

        with d1:
            st.caption(
                "PORTFOLIO DIAGNOSIS"
            )

            st.markdown(
                "### "
                f"{len(p0)} urgent decisions"
            )

            st.caption(
                f"{len(p1)} additional opportunities "
                "require operator review."
            )

        with d2:
            st.metric(
                "Critical Vehicles",
                kpis[
                    "critical_count"
                ],
            )

        with d3:
            st.metric(
                "Ageing Vehicles",
                kpis[
                    "ageing_count"
                ],
            )

        with d4:
            st.metric(
                "Sale Probability",
                _percent(
                    kpis[
                        "average_sale_probability"
                    ]
                ),
            )

    st.divider()

    # ------------------------------------------------------
    # AGEING
    # ------------------------------------------------------

    st.subheader(
        "Where is capital ageing?"
    )

    ageing = ageing_summary(
        df
    )

    left, right = st.columns(
        [1.2, 1]
    )

    with left:

        age_capital = ageing[
            [
                "age_bucket",
                "capital",
            ]
        ].set_index(
            "age_bucket"
        )

        st.caption(
            "CAPITAL BY AGE BUCKET"
        )

        st.bar_chart(
            age_capital,
            height=310,
        )

    with right:

        age_risk = ageing[
            [
                "age_bucket",
                "capital_at_risk",
            ]
        ].set_index(
            "age_bucket"
        )

        st.caption(
            "CAPITAL AT RISK"
        )

        st.bar_chart(
            age_risk,
            height=310,
        )

    st.divider()

    # ------------------------------------------------------
    # LOCATION
    # ------------------------------------------------------

    st.subheader(
        "Portfolio by location"
    )

    location_df = (
        location_inventory_performance(
            df
        )
    )

    l1, l2 = st.columns(
        2
    )

    with l1:

        contribution_chart = (
            location_df[
                [
                    "location",
                    "expected_contribution",
                ]
            ]
            .set_index(
                "location"
            )
        )

        st.caption(
            "EXPECTED CONTRIBUTION"
        )

        st.bar_chart(
            contribution_chart,
            height=300,
        )

    with l2:

        risk_chart = (
            location_df[
                [
                    "location",
                    "capital_at_risk",
                ]
            ]
            .set_index(
                "location"
            )
        )

        st.caption(
            "CAPITAL AT RISK"
        )

        st.bar_chart(
            risk_chart,
            height=300,
        )

    st.divider()

    # ------------------------------------------------------
    # MODEL INTELLIGENCE
    # ------------------------------------------------------

    st.subheader(
        "What inventory deserves more capital?"
    )

    model_df = model_performance(
        df
    )

    model_display = (
        model_df.head(
            12
        )
        .copy()
    )

    model_display[
        "Margin"
    ] = model_display[
        "average_margin_pct"
    ].map(
        _percent
    )

    model_display[
        "Sale Probability"
    ] = model_display[
        "average_sale_probability"
    ].map(
        _percent
    )

    model_display[
        "Expected Contribution"
    ] = model_display[
        "expected_contribution"
    ].map(
        _money
    )

    model_display[
        "Demand"
    ] = model_display[
        "average_demand_index"
    ].round(0)

    model_display[
        "Age"
    ] = (
        model_display[
            "average_age_days"
        ]
        .round(0)
        .astype(int)
        .astype(str)
        + "d"
    )

    st.dataframe(
        model_display[
            [
                "make",
                "model",
                "segment",
                "vehicles",
                "Demand",
                "Margin",
                "Sale Probability",
                "Age",
                "Expected Contribution",
            ]
        ].rename(
            columns={
                "make": "Make",
                "model": "Model",
                "segment": "Segment",
                "vehicles": "Units",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # ------------------------------------------------------
    # ACTION QUEUE
    # ------------------------------------------------------

    st.subheader(
        "Inventory Decision Queue"
    )

    st.caption(
        "Vehicles ranked by urgency and modeled economic impact."
    )

    if not decisions:

        st.success(
            "No material inventory interventions detected."
        )

    else:

        for index, decision in enumerate(
            decisions[:10],
            start=1,
        ):

            with st.container(
                border=True
            ):

                c1, c2, c3 = st.columns(
                    [2.8, 1, 1]
                )

                with c1:

                    st.caption(
                        f"{decision.priority} · "
                        f"DECISION {index:02d}"
                    )

                    st.markdown(
                        f"### {_priority_icon(decision.priority)} "
                        f"{decision.make} {decision.model}"
                    )

                    st.caption(
                        f"{decision.vehicle_id} · "
                        f"{decision.location} · "
                        f"{decision.segment}"
                    )

                    st.markdown(
                        f"**{decision.decision}**"
                    )

                    st.write(
                        decision.reason
                    )

                with c2:

                    st.caption(
                        "EXPECTED IMPACT"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            decision.expected_impact
                        )
                    )

                with c3:

                    st.caption(
                        "CAPITAL AT RISK"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            decision.capital_at_risk
                        )
                    )

                    st.caption(
                        f"{decision.confidence:.0%} confidence"
                    )

                b1, b2, b3 = st.columns(
                    3
                )

                b1.button(
                    "Open Vehicle 360",
                    key=(
                        "portfolio_vehicle_"
                        + decision.vehicle_id
                    ),
                    use_container_width=True,
                )

                b2.button(
                    "Simulate Decision",
                    key=(
                        "portfolio_simulate_"
                        + decision.vehicle_id
                    ),
                    use_container_width=True,
                )

                b3.button(
                    "Create Action",
                    key=(
                        "portfolio_action_"
                        + decision.vehicle_id
                    ),
                    use_container_width=True,
                )

    st.caption(
        "All portfolio and decision data is synthetic."
    )


# ==========================================================
# VEHICLE 360
# ==========================================================


def render_vehicle_360() -> None:

    _header(
        "Vehicle Intelligence",
        "Vehicle 360",
        (
            "One vehicle. Full economics, market context, capital "
            "exposure and next-best decision."
        ),
    )

    data = load_inventory_data()

    options = data[
        [
            "vehicle_id",
            "make",
            "model",
            "location",
            "year",
        ]
    ].copy()

    options[
        "label"
    ] = (
        options[
            "vehicle_id"
        ]
        + " — "
        + options[
            "year"
        ].astype(
            str
        )
        + " "
        + options[
            "make"
        ]
        + " "
        + options[
            "model"
        ]
        + " — "
        + options[
            "location"
        ]
    )

    label_to_id = dict(
        zip(
            options[
                "label"
            ],
            options[
                "vehicle_id"
            ],
        )
    )

    selected_label = st.selectbox(
        "Select vehicle",
        options[
            "label"
        ].tolist(),
    )

    vehicle_id = label_to_id[
        selected_label
    ]

    vehicle = get_vehicle(
        data,
        vehicle_id,
    )

    decisions = vehicle_decisions(
        data,
        vehicle_id,
    )

    # ------------------------------------------------------
    # HERO
    # ------------------------------------------------------

    top_left, top_right = st.columns(
        [3, 1]
    )

    with top_left:

        st.caption(
            vehicle[
                "vehicle_id"
            ]
        )

        st.markdown(
            f"## {_status_icon(str(vehicle['status']))} "
            f"{vehicle['year']} "
            f"{vehicle['make']} "
            f"{vehicle['model']}"
        )

        st.write(
            f"{vehicle['location']} · "
            f"{vehicle['segment']} · "
            f"{int(vehicle['mileage_km']):,} km · "
            f"{vehicle['age_days']} days in inventory"
        )

    with top_right:

        st.caption(
            "EXPECTED CONTRIBUTION"
        )

        st.markdown(
            "## "
            + _money(
                float(
                    vehicle[
                        "expected_contribution"
                    ]
                )
            )
        )

        st.caption(
            _percent(
                float(
                    vehicle[
                        "expected_margin_pct"
                    ]
                )
            )
            + " expected margin"
        )

    st.write("")

    # ------------------------------------------------------
    # CORE SCORES
    # ------------------------------------------------------

    s1, s2, s3, s4, s5 = st.columns(
        5
    )

    s1.metric(
        "Inventory Age",
        (
            f"{vehicle['age_days']}d"
        ),
    )

    s2.metric(
        "Demand Index",
        (
            f"{vehicle['demand_index']:.0f}"
        ),
    )

    s3.metric(
        "Sale Probability",
        _percent(
            float(
                vehicle[
                    "sale_probability"
                ]
            )
        ),
    )

    s4.metric(
        "Expected Days to Sale",
        (
            f"{vehicle['expected_days_to_sale']:.0f}d"
        ),
    )

    s5.metric(
        "Capital at Risk",
        _money(
            float(
                vehicle[
                    "capital_at_risk"
                ]
            )
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # ECONOMICS + MARKET
    # ------------------------------------------------------

    left, right = st.columns(
        [1, 1]
    )

    with left:

        st.subheader(
            "Vehicle Economics"
        )

        economics = pd.DataFrame(
            [
                {
                    "Line Item": "Acquisition",
                    "Value": vehicle[
                        "acquisition_price"
                    ],
                },
                {
                    "Line Item": "Reconditioning",
                    "Value": vehicle[
                        "recon_cost"
                    ],
                },
                {
                    "Line Item": "Logistics",
                    "Value": vehicle[
                        "logistics_cost"
                    ],
                },
                {
                    "Line Item": "Holding Cost",
                    "Value": vehicle[
                        "holding_cost"
                    ],
                },
                {
                    "Line Item": "Landed Cost",
                    "Value": vehicle[
                        "landed_cost"
                    ],
                },
                {
                    "Line Item": "Expected Sale",
                    "Value": vehicle[
                        "expected_sale_price"
                    ],
                },
                {
                    "Line Item": "Contribution",
                    "Value": vehicle[
                        "expected_contribution"
                    ],
                },
            ]
        )

        economics[
            "Value"
        ] = economics[
            "Value"
        ].map(
            _money
        )

        st.dataframe(
            economics,
            hide_index=True,
            use_container_width=True,
        )

        st.metric(
            "Daily Holding Burn",
            _money(
                float(
                    vehicle[
                        "holding_cost_per_day"
                    ]
                )
            )
            + " / day",
        )

    with right:

        st.subheader(
            "Market Position"
        )

        p1, p2 = st.columns(
            2
        )

        p1.metric(
            "Listing Price",
            _money(
                float(
                    vehicle[
                        "listing_price"
                    ]
                )
            ),
        )

        p2.metric(
            "Market Benchmark",
            _money(
                float(
                    vehicle[
                        "market_price"
                    ]
                )
            ),
        )

        price_position = float(
            vehicle[
                "price_position"
            ]
        )

        if price_position > 1.03:

            st.error(
                (
                    f"Vehicle is listed at "
                    f"{price_position:.1%} of market benchmark. "
                    "Price may be suppressing velocity."
                )
            )

        elif price_position < 0.98:

            st.warning(
                "Vehicle is priced below market. "
                "Review whether margin can be protected."
            )

        else:

            st.success(
                "Pricing is broadly aligned with market."
            )

        st.markdown(
            "**Demand context**"
        )

        st.progress(
            min(
                float(
                    vehicle[
                        "demand_index"
                    ]
                )
                / 100,
                1.0,
            )
        )

        st.caption(
            (
                f"Demand index: "
                f"{vehicle['demand_index']:.0f}/100"
            )
        )

        st.markdown(
            "**Sale probability**"
        )

        st.progress(
            float(
                vehicle[
                    "sale_probability"
                ]
            )
        )

    st.divider()

    # ------------------------------------------------------
    # NEXT BEST ACTION
    # ------------------------------------------------------

    st.subheader(
        "Decision Intelligence"
    )

    if decisions:

        decision = decisions[
            0
        ]

        with st.container(
            border=True
        ):

            d1, d2 = st.columns(
                [2.6, 1]
            )

            with d1:

                st.caption(
                    f"{decision.priority} · "
                    "NEXT BEST ACTION"
                )

                st.markdown(
                    f"## {_priority_icon(decision.priority)} "
                    f"{decision.decision}"
                )

                st.write(
                    decision.reason
                )

                st.caption(
                    f"Confidence: "
                    f"{decision.confidence:.0%}"
                )

            with d2:

                st.caption(
                    "EXPECTED IMPACT"
                )

                st.markdown(
                    "## "
                    + _money(
                        decision.expected_impact
                    )
                )

                st.caption(
                    "Modeled economic effect"
                )

        b1, b2, b3 = st.columns(
            3
        )

        b1.button(
            "Simulate Action",
            type="primary",
            use_container_width=True,
        )

        b2.button(
            "Create Experiment",
            use_container_width=True,
        )

        b3.button(
            "Assign Owner",
            use_container_width=True,
        )

    else:

        st.success(
            "No intervention recommended. "
            "Current vehicle economics and demand support holding course."
        )

    st.divider()

    # ------------------------------------------------------
    # LIFECYCLE
    # ------------------------------------------------------

    st.subheader(
        "Vehicle Lifecycle"
    )

    lifecycle = [
        (
            "01",
            "Acquired",
            _money(
                float(
                    vehicle[
                        "acquisition_price"
                    ]
                )
            ),
        ),
        (
            "02",
            "Reconditioned",
            _money(
                float(
                    vehicle[
                        "recon_cost"
                    ]
                )
            ),
        ),
        (
            "03",
            "Transported",
            _money(
                float(
                    vehicle[
                        "logistics_cost"
                    ]
                )
            ),
        ),
        (
            "04",
            "Listed",
            _money(
                float(
                    vehicle[
                        "listing_price"
                    ]
                )
            ),
        ),
        (
            "05",
            "Current Age",
            (
                f"{vehicle['age_days']} days"
            ),
        ),
        (
            "06",
            "Expected Sale",
            _money(
                float(
                    vehicle[
                        "expected_sale_price"
                    ]
                )
            ),
        ),
    ]

    lifecycle_cols = st.columns(
        len(
            lifecycle
        )
    )

    for index, (
        number,
        label,
        value,
    ) in enumerate(
        lifecycle
    ):

        with lifecycle_cols[
            index
        ]:

            with st.container(
                border=True
            ):

                st.caption(
                    number
                )

                st.markdown(
                    f"**{label}**"
                )

                st.write(
                    value
                )

    st.caption(
        "Vehicle 360 uses synthetic lifecycle and economics data."
    )


# ==========================================================
# CAPITAL INTELLIGENCE
# ==========================================================


def render_capital_intelligence() -> None:

    _header(
        "Capital Intelligence",
        "Where is the money actually stuck?",
        (
            "Treat inventory as deployed capital. Separate productive "
            "capital from ageing capital, quantify daily holding burn "
            "and identify the interventions most likely to release cash."
        ),
    )

    df = _filters(
        "capital"
    )

    if df.empty:
        st.warning(
            "No vehicles match these filters."
        )
        return

    capital = capital_intelligence(
        df
    )

    kpis = inventory_kpis(
        df
    )

    # ------------------------------------------------------
    # CAPITAL KPIs
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(
        5
    )

    k1.metric(
        "Productive Capital",
        _money(
            capital[
                "productive_capital"
            ]
        ),
    )

    k2.metric(
        "Ageing Capital",
        _money(
            capital[
                "ageing_capital"
            ]
        ),
    )

    k3.metric(
        "Critical Capital",
        _money(
            capital[
                "critical_capital"
            ]
        ),
    )

    k4.metric(
        "Daily Holding Burn",
        _money(
            capital[
                "daily_holding_burn"
            ]
        ),
    )

    k5.metric(
        "Modeled Release",
        _money(
            capital[
                "modeled_capital_release"
            ]
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # CAPITAL MIX
    # ------------------------------------------------------

    st.subheader(
        "Capital productivity"
    )

    total = (
        capital[
            "productive_capital"
        ]
        + capital[
            "ageing_capital"
        ]
        + capital[
            "critical_capital"
        ]
    )

    capital_mix = pd.DataFrame(
        [
            {
                "State": "Productive",
                "Capital": capital[
                    "productive_capital"
                ],
            },
            {
                "State": "Ageing",
                "Capital": capital[
                    "ageing_capital"
                ],
            },
            {
                "State": "Critical",
                "Capital": capital[
                    "critical_capital"
                ],
            },
        ]
    )

    st.bar_chart(
        capital_mix.set_index(
            "State"
        ),
        height=320,
    )

    if total:

        productive_pct = (
            capital[
                "productive_capital"
            ]
            / total
        )

        critical_pct = (
            capital[
                "critical_capital"
            ]
            / total
        )

        c1, c2 = st.columns(
            2
        )

        c1.metric(
            "Productive Share",
            _percent(
                productive_pct
            ),
        )

        c2.metric(
            "Critical Share",
            _percent(
                critical_pct
            ),
        )

    st.divider()

    # ------------------------------------------------------
    # AGEING ECONOMICS
    # ------------------------------------------------------

    st.subheader(
        "How quickly does capital deteriorate?"
    )

    ageing = ageing_summary(
        df
    )

    ageing_display = ageing.copy()

    ageing_display[
        "Capital"
    ] = ageing_display[
        "capital"
    ].map(
        _money
    )

    ageing_display[
        "Contribution"
    ] = ageing_display[
        "expected_contribution"
    ].map(
        _money
    )

    ageing_display[
        "Risk"
    ] = ageing_display[
        "capital_at_risk"
    ].map(
        _money
    )

    st.dataframe(
        ageing_display[
            [
                "age_bucket",
                "vehicles",
                "Capital",
                "Contribution",
                "Risk",
            ]
        ].rename(
            columns={
                "age_bucket": "Age Bucket",
                "vehicles": "Vehicles",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()

    # ------------------------------------------------------
    # CAPITAL RELEASE QUEUE
    # ------------------------------------------------------

    st.subheader(
        "Capital Release Queue"
    )

    decisions = [
        decision
        for decision
        in detect_inventory_decisions(
            df
        )
        if decision.priority
        in {
            "P0",
            "P1",
        }
    ]

    if not decisions:

        st.success(
            "No material capital release actions detected."
        )

    else:

        for rank, decision in enumerate(
            decisions[:10],
            start=1,
        ):

            with st.container(
                border=True
            ):

                c1, c2, c3 = st.columns(
                    [2.6, 1, 1]
                )

                with c1:

                    st.caption(
                        f"CAPITAL ACTION {rank:02d}"
                    )

                    st.markdown(
                        f"### {_priority_icon(decision.priority)} "
                        f"{decision.make} {decision.model}"
                    )

                    st.caption(
                        f"{decision.vehicle_id} · "
                        f"{decision.location}"
                    )

                    st.markdown(
                        f"**{decision.decision}**"
                    )

                    st.write(
                        decision.reason
                    )

                with c2:

                    st.caption(
                        "CAPITAL AT RISK"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            decision.capital_at_risk
                        )
                    )

                with c3:

                    st.caption(
                        "EXPECTED IMPACT"
                    )

                    st.markdown(
                        "### "
                        + _money(
                            decision.expected_impact
                        )
                    )

    st.divider()

    # ------------------------------------------------------
    # CEO QUESTION
    # ------------------------------------------------------

    with st.container(
        border=True
    ):

        st.caption(
            "CEO QUESTION"
        )

        st.markdown(
            "## What if we reduced average inventory age by 5 days?"
        )

        current_daily_burn = (
            capital[
                "daily_holding_burn"
            ]
        )

        modeled_holding_saving = (
            current_daily_burn
            * 5
        )

        approximate_cash_acceleration = (
            kpis[
                "capital_deployed"
            ]
            * (
                5
                / max(
                    kpis[
                        "average_age_days"
                    ],
                    1,
                )
            )
        )

        q1, q2 = st.columns(
            2
        )

        q1.metric(
            "Holding Cost Avoided",
            _money(
                modeled_holding_saving
            ),
        )

        q2.metric(
            "Capital Turn Accelerated",
            _money(
                approximate_cash_acceleration
            ),
        )

        st.button(
            "Open Scenario Lab",
            type="primary",
        )

    st.caption(
        "Capital Intelligence uses synthetic inventory economics."
    )
