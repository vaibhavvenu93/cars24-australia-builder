from __future__ import annotations

import pandas as pd
import streamlit as st

from engines.builder_intelligence import (
    build_opportunity_radar,
    builder_summary,
    experiment_summary,
    load_experiments,
    simulate_growth_scenario,
    simulate_inventory_scenario,
    simulate_operations_scenario,
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


def _domain_icon(domain: str) -> str:
    icons = {
        "Growth": "↗",
        "Inventory": "◫",
        "Operations": "⚙",
    }

    return icons.get(
        domain,
        "•",
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


# ==========================================================
# OPPORTUNITY RADAR
# ==========================================================


def render_opportunity_radar() -> None:

    _header(
        "Builder Intelligence",
        "Where should we build next?",
        (
            "Combine growth, inventory and operations intelligence "
            "into one ranked portfolio of business opportunities."
        ),
    )

    summary = builder_summary()

    opportunity_summary = summary[
        "opportunity_summary"
    ]

    opportunities = build_opportunity_radar()

    # ------------------------------------------------------
    # KPI STRIP
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Opportunities",
        int(
            opportunity_summary[
                "opportunities"
            ]
        ),
    )

    k2.metric(
        "P0",
        int(
            opportunity_summary[
                "p0"
            ]
        ),
    )

    k3.metric(
        "P1",
        int(
            opportunity_summary[
                "p1"
            ]
        ),
    )

    k4.metric(
        "Modeled Impact",
        _money(
            float(
                opportunity_summary[
                    "modeled_impact"
                ]
            )
        ),
    )

    k5.metric(
        "Avg Confidence",
        _percent(
            float(
                opportunity_summary[
                    "average_confidence"
                ]
            )
        ),
    )

    st.write("")

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    domains = sorted(
        {
            opportunity.domain
            for opportunity
            in opportunities
        }
    )

    priorities = sorted(
        {
            opportunity.priority
            for opportunity
            in opportunities
        }
    )

    f1, f2 = st.columns(2)

    with f1:

        selected_domains = st.multiselect(
            "Domains",
            options=domains,
            default=domains,
        )

    with f2:

        selected_priorities = st.multiselect(
            "Priority",
            options=priorities,
            default=priorities,
        )

    filtered = [
        opportunity
        for opportunity
        in opportunities
        if (
            opportunity.domain
            in selected_domains
            and opportunity.priority
            in selected_priorities
        )
    ]

    st.divider()

    # ------------------------------------------------------
    # PORTFOLIO VIEW
    # ------------------------------------------------------

    st.subheader(
        "Opportunity portfolio"
    )

    domain_totals = []

    for domain in domains:

        domain_opportunities = [
            item
            for item in opportunities
            if item.domain == domain
        ]

        domain_totals.append(
            {
                "Domain": domain,
                "Modeled Impact": sum(
                    item.modeled_impact
                    for item
                    in domain_opportunities
                ),
            }
        )

    domain_df = pd.DataFrame(
        domain_totals
    )

    if not domain_df.empty:

        st.bar_chart(
            domain_df.set_index(
                "Domain"
            ),
            height=300,
        )

    st.write("")

    # ------------------------------------------------------
    # RANKED RADAR
    # ------------------------------------------------------

    if not filtered:

        st.success(
            "No opportunities match the current filters."
        )

        return

    for rank, opportunity in enumerate(
        filtered,
        start=1,
    ):

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [3, 1]
            )

            with c1:

                st.caption(
                    (
                        f"{opportunity.priority} · "
                        f"OPPORTUNITY {rank:02d} · "
                        f"{opportunity.domain.upper()}"
                    )
                )

                st.markdown(
                    (
                        f"### {_priority_icon(opportunity.priority)} "
                        f"{_domain_icon(opportunity.domain)} "
                        f"{opportunity.entity}"
                    )
                )

                st.markdown(
                    f"**{opportunity.title}**"
                )

                st.write(
                    opportunity.evidence
                )

            with c2:

                st.caption(
                    "MODELED IMPACT"
                )

                st.markdown(
                    "## "
                    + _money(
                        opportunity.modeled_impact
                    )
                )

                st.caption(
                    f"{opportunity.confidence:.0%} confidence"
                )

            st.markdown(
                "**Recommended action**"
            )

            st.write(
                opportunity.recommended_action
            )

            st.caption(
                f"Source: {opportunity.source}"
            )

            b1, b2, b3 = st.columns(3)

            b1.button(
                "Open Scenario",
                key=(
                    f"radar_scenario_"
                    f"{rank}"
                ),
                type="primary",
                use_container_width=True,
            )

            b2.button(
                "Create Experiment",
                key=(
                    f"radar_experiment_"
                    f"{rank}"
                ),
                use_container_width=True,
            )

            b3.button(
                "Assign Owner",
                key=(
                    f"radar_owner_"
                    f"{rank}"
                ),
                use_container_width=True,
            )

    st.caption(
        "Opportunity Radar combines synthetic Growth, Inventory "
        "and Operations intelligence."
    )


# ==========================================================
# SCENARIO LAB
# ==========================================================


def render_scenario_lab() -> None:

    _header(
        "Decision Simulation",
        "What happens if we change the system?",
        (
            "Adjust operating assumptions and model the economic "
            "effect before committing capital or execution capacity."
        ),
    )

    scenario_type = st.selectbox(
        "Scenario",
        [
            "Growth Acceleration",
            "Inventory Productivity",
            "Operations Throughput",
        ],
    )

    st.write("")

    # ======================================================
    # GROWTH
    # ======================================================

    if scenario_type == "Growth Acceleration":

        st.subheader(
            "Growth Acceleration"
        )

        st.caption(
            "Model faster response, improved test-drive conversion "
            "and additional inventory availability."
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            response_improvement = st.slider(
                "Response-time improvement",
                min_value=0,
                max_value=60,
                value=25,
                step=5,
                format="%d%%",
            )

        with c2:

            conversion_lift = st.slider(
                "Test-drive conversion lift",
                min_value=0,
                max_value=15,
                value=5,
                step=1,
                format="%d pp",
            )

        with c3:

            inventory_growth = st.slider(
                "Additional inventory",
                min_value=0,
                max_value=30,
                value=10,
                step=5,
                format="%d%%",
            )

        result = simulate_growth_scenario(
            response_time_improvement_pct=(
                response_improvement
                / 100
            ),
            test_drive_conversion_lift_pp=(
                conversion_lift
            ),
            additional_inventory_pct=(
                inventory_growth
            ),
        )

    # ======================================================
    # INVENTORY
    # ======================================================

    elif scenario_type == "Inventory Productivity":

        st.subheader(
            "Inventory Productivity"
        )

        st.caption(
            "Model the effect of faster stock turns, stronger "
            "pricing discipline and broader transfer adoption."
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            age_reduction = st.slider(
                "Inventory age reduction",
                min_value=0,
                max_value=15,
                value=5,
                step=1,
                format="%d days",
            )

        with c2:

            pricing_efficiency = st.slider(
                "Pricing efficiency",
                min_value=0,
                max_value=10,
                value=2,
                step=1,
                format="%d%%",
            )

        with c3:

            transfer_adoption = st.slider(
                "Transfer adoption",
                min_value=0,
                max_value=100,
                value=25,
                step=5,
                format="%d%%",
            )

        result = simulate_inventory_scenario(
            inventory_age_reduction_days=(
                age_reduction
            ),
            pricing_efficiency_pct=(
                pricing_efficiency
            ),
            transfer_adoption_pct=(
                transfer_adoption
            ),
        )

    # ======================================================
    # OPERATIONS
    # ======================================================

    else:

        st.subheader(
            "Operations Throughput"
        )

        st.caption(
            "Model recon improvement, SLA recovery and "
            "conversion lift together."
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            recon_reduction = st.slider(
                "Recon-day reduction",
                min_value=0.0,
                max_value=3.0,
                value=1.2,
                step=0.1,
            )

        with c2:

            sla_improvement = st.slider(
                "SLA improvement",
                min_value=0,
                max_value=30,
                value=10,
                step=1,
                format="%d pp",
            )

        with c3:

            conversion_lift = st.slider(
                "Conversion lift",
                min_value=0,
                max_value=10,
                value=2,
                step=1,
                format="%d pp",
            )

        result = simulate_operations_scenario(
            recon_day_reduction=(
                recon_reduction
            ),
            sla_improvement_pp=(
                sla_improvement
            ),
            conversion_lift_pp=(
                conversion_lift
            ),
        )

    st.divider()

    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------

    st.subheader(
        "Modeled outcome"
    )

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Baseline",
        _money(
            result.baseline_value
        ),
    )

    r2.metric(
        "Modeled",
        _money(
            result.modeled_value
        ),
    )

    r3.metric(
        "Economic Delta",
        _money(
            result.delta_value
        ),
    )

    r4.metric(
        "Improvement",
        _percent(
            result.delta_pct
        ),
    )

    st.write("")

    with st.container(
        border=True
    ):

        st.caption(
            "SCENARIO INTERPRETATION"
        )

        st.markdown(
            f"## {result.scenario_name}"
        )

        st.write(
            result.interpretation
        )

        st.markdown(
            "**Assumptions**"
        )

        assumption_rows = []

        for key, value in (
            result.assumptions.items()
        ):

            assumption_rows.append(
                {
                    "Assumption": (
                        key
                        .replace(
                            "_",
                            " ",
                        )
                        .title()
                    ),
                    "Value": value,
                }
            )

        st.dataframe(
            pd.DataFrame(
                assumption_rows
            ),
            hide_index=True,
            use_container_width=True,
        )

    b1, b2, b3 = st.columns(3)

    b1.button(
        "Save Scenario",
        type="primary",
        use_container_width=True,
    )

    b2.button(
        "Turn into Experiment",
        use_container_width=True,
    )

    b3.button(
        "Share with Leadership",
        use_container_width=True,
    )

    st.divider()

    # ------------------------------------------------------
    # DECISION LOOP
    # ------------------------------------------------------

    st.subheader(
        "Scenario → experiment → operating change"
    )

    s1, s2, s3, s4 = st.columns(4)

    cards = [
        (
            s1,
            "01",
            "Model",
            (
                "Change assumptions before "
                "committing resources."
            ),
        ),
        (
            s2,
            "02",
            "Test",
            (
                "Convert the strongest scenario "
                "into a controlled experiment."
            ),
        ),
        (
            s3,
            "03",
            "Measure",
            (
                "Compare observed outcome "
                "against baseline."
            ),
        ),
        (
            s4,
            "04",
            "Scale",
            (
                "Promote proven interventions "
                "into standard operations."
            ),
        ),
    ]

    for column, number, title, copy in cards:

        with column:

            with st.container(
                border=True
            ):

                st.caption(
                    number
                )

                st.markdown(
                    f"**{title}**"
                )

                st.caption(
                    copy
                )


# ==========================================================
# EXPERIMENTS
# ==========================================================


def render_experiments() -> None:

    _header(
        "Learning System",
        "Which interventions are actually working?",
        (
            "Track hypotheses, owners, targets and expected impact "
            "so operational improvements become repeatable rather "
            "than anecdotal."
        ),
    )

    experiments = load_experiments()

    summary = experiment_summary()

    # ------------------------------------------------------
    # KPI STRIP
    # ------------------------------------------------------

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Experiments",
        int(
            summary[
                "experiments"
            ]
        ),
    )

    k2.metric(
        "Running",
        int(
            summary[
                "running"
            ]
        ),
    )

    k3.metric(
        "Scaled",
        int(
            summary[
                "scaled"
            ]
        ),
    )

    k4.metric(
        "Planned",
        int(
            summary[
                "planned"
            ]
        ),
    )

    k5.metric(
        "Expected Impact",
        _money(
            float(
                summary[
                    "expected_impact"
                ]
            )
        ),
    )

    st.write("")

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    domains = sorted(
        experiments[
            "domain"
        ].unique()
    )

    statuses = sorted(
        experiments[
            "status"
        ].unique()
    )

    f1, f2 = st.columns(2)

    with f1:

        selected_domains = st.multiselect(
            "Domain",
            options=domains,
            default=list(
                domains
            ),
        )

    with f2:

        selected_statuses = st.multiselect(
            "Status",
            options=statuses,
            default=list(
                statuses
            ),
        )

    filtered = experiments[
        (
            experiments[
                "domain"
            ].isin(
                selected_domains
            )
        )
        & (
            experiments[
                "status"
            ].isin(
                selected_statuses
            )
        )
    ]

    st.divider()

    # ------------------------------------------------------
    # PORTFOLIO
    # ------------------------------------------------------

    if filtered.empty:

        st.success(
            "No experiments match these filters."
        )

        return

    for _, row in filtered.iterrows():

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [3, 1]
            )

            with c1:

                st.caption(
                    (
                        f"{row['experiment_id']} · "
                        f"{row['domain'].upper()} · "
                        f"{row['status'].upper()}"
                    )
                )

                st.markdown(
                    f"### {row['title']}"
                )

                st.markdown(
                    "**Hypothesis**"
                )

                st.write(
                    row[
                        "hypothesis"
                    ]
                )

            with c2:

                st.caption(
                    "EXPECTED IMPACT"
                )

                st.markdown(
                    "## "
                    + _money(
                        float(
                            row[
                                "expected_impact"
                            ]
                        )
                    )
                )

                st.caption(
                    f"{float(row['confidence']):.0%} confidence"
                )

            st.write("")

            m1, m2, m3, m4 = st.columns(4)

            with m1:

                st.caption(
                    "METRIC"
                )

                st.markdown(
                    f"**{row['metric']}**"
                )

            with m2:

                st.caption(
                    "BASELINE"
                )

                baseline = row[
                    "baseline"
                ]

                if isinstance(
                    baseline,
                    float,
                ) and baseline < 1:
                    baseline_display = (
                        f"{baseline:.1%}"
                    )
                else:
                    baseline_display = (
                        f"{baseline:g}"
                    )

                st.markdown(
                    f"**{baseline_display}**"
                )

            with m3:

                st.caption(
                    "TARGET"
                )

                target = row[
                    "target"
                ]

                if isinstance(
                    target,
                    float,
                ) and target < 1:
                    target_display = (
                        f"{target:.1%}"
                    )
                else:
                    target_display = (
                        f"{target:g}"
                    )

                st.markdown(
                    f"**{target_display}**"
                )

            with m4:

                st.caption(
                    "DURATION"
                )

                st.markdown(
                    f"**{int(row['duration_days'])} days**"
                )

            st.write("")

            st.caption(
                f"Owner: {row['owner']}"
            )

            b1, b2, b3 = st.columns(3)

            if row[
                "status"
            ] == "Planned":

                b1.button(
                    "Launch Experiment",
                    key=(
                        "launch_"
                        + row[
                            "experiment_id"
                        ]
                    ),
                    type="primary",
                    use_container_width=True,
                )

            elif row[
                "status"
            ] == "Running":

                b1.button(
                    "Review Progress",
                    key=(
                        "progress_"
                        + row[
                            "experiment_id"
                        ]
                    ),
                    type="primary",
                    use_container_width=True,
                )

            else:

                b1.button(
                    "View Results",
                    key=(
                        "results_"
                        + row[
                            "experiment_id"
                        ]
                    ),
                    type="primary",
                    use_container_width=True,
                )

            b2.button(
                "Edit Hypothesis",
                key=(
                    "edit_"
                    + row[
                        "experiment_id"
                    ]
                ),
                use_container_width=True,
            )

            b3.button(
                "Open Evidence",
                key=(
                    "evidence_"
                    + row[
                        "experiment_id"
                    ]
                ),
                use_container_width=True,
            )

    st.divider()

    # ------------------------------------------------------
    # LEARNING LOOP
    # ------------------------------------------------------

    st.subheader(
        "Institutional learning"
    )

    st.caption(
        "The product becomes more useful when successful "
        "interventions become reusable operating knowledge."
    )

    l1, l2, l3 = st.columns(3)

    with l1:

        with st.container(
            border=True
        ):

            st.caption(
                "OBSERVE"
            )

            st.markdown(
                "### Signals become hypotheses"
            )

            st.write(
                "Growth, inventory and operations anomalies "
                "become candidate interventions."
            )

    with l2:

        with st.container(
            border=True
        ):

            st.caption(
                "TEST"
            )

            st.markdown(
                "### Hypotheses become experiments"
            )

            st.write(
                "Targets, owners, timeframes and expected "
                "economics are defined before execution."
            )

    with l3:

        with st.container(
            border=True
        ):

            st.caption(
                "LEARN"
            )

            st.markdown(
                "### Outcomes improve future decisions"
            )

            st.write(
                "Successful interventions can become new "
                "benchmarks, rules or automated workflows."
            )

    st.caption(
        "Experiment data is synthetic and demonstrates the "
        "intended operating model."
    )
