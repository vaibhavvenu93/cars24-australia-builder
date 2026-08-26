from __future__ import annotations

import streamlit as st

from engines.executive_intelligence import (
    decision_summary,
    executive_health,
    executive_kpis,
    executive_signals,
    morning_brief,
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
    if value <= 1:
        value *= 100

    return f"{value:.1f}%"


def _priority_icon(priority: str) -> str:
    return {
        "P0": "🔴",
        "P1": "🟠",
        "P2": "🟢",
    }.get(priority, "⚪")


def _health_icon(status: str) -> str:
    return {
        "Critical": "🔴",
        "Opportunity": "🟠",
        "Watch": "🟡",
        "Healthy": "🟢",
    }.get(status, "⚪")


# ==========================================================
# EXECUTIVE COMMAND CENTRE
# ==========================================================


def render_executive_command_centre() -> None:
    kpis = executive_kpis()
    decisions = decision_summary()
    health = executive_health()
    signals = executive_signals()

    st.caption("EXECUTIVE INTELLIGENCE")

    st.title(
        "What needs leadership attention today?"
    )

    st.write(
        "One operating view across growth, inventory, "
        "operations and capital — ranked by economic impact."
    )

    # ------------------------------------------------------
    # TOP KPI STRIP
    # ------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Revenue",
        _money(kpis["revenue"]),
    )

    c2.metric(
        "Sales",
        f'{int(kpis["sales"]):,}',
    )

    c3.metric(
        "Capital at Risk",
        _money(kpis["capital_at_risk"]),
    )

    c4.metric(
        "Open Decisions",
        int(decisions["open_decisions"]),
    )

    c5.metric(
        "Modeled Opportunity",
        _money(
            kpis["total_modeled_opportunity"]
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # MORNING BRIEF
    # ------------------------------------------------------

    st.header("Morning Brief")

    st.caption(
        "Highest-value signals leadership should know "
        "before the operating day begins."
    )

    brief = morning_brief()

    for index, signal in enumerate(
        brief,
        start=1,
    ):
        with st.container(border=True):

            left, right = st.columns(
                [4, 1]
            )

            with left:
                st.caption(
                    f"{signal.priority} · "
                    f"{signal.domain.upper()} · "
                    f"SIGNAL {index:02d}"
                )

                st.subheader(
                    f"{_priority_icon(signal.priority)} "
                    f"{signal.title}"
                )

                st.write(
                    signal.summary
                )

                st.markdown(
                    "**Recommended action**"
                )

                st.write(
                    signal.recommended_action
                )

            with right:
                st.caption(
                    "MODELED IMPACT"
                )

                st.subheader(
                    _money(
                        signal.modeled_impact
                    )
                )

                st.caption(
                    f"{_percent(signal.confidence)} "
                    "confidence"
                )

    st.divider()

    # ------------------------------------------------------
    # BUSINESS HEALTH
    # ------------------------------------------------------

    st.header("Operating Health")

    st.caption(
        "Where the system sees risk, opportunity "
        "or healthy execution."
    )

    statuses = health["status"]

    columns = st.columns(4)

    domains = [
        "growth",
        "inventory",
        "operations",
        "builder",
    ]

    for column, domain in zip(
        columns,
        domains,
    ):
        status = statuses[domain]

        with column:
            with st.container(border=True):

                st.caption(
                    domain.upper()
                )

                st.subheader(
                    f"{_health_icon(status)} "
                    f"{status}"
                )

    # ------------------------------------------------------
    # ECONOMIC EXPOSURE
    # ------------------------------------------------------

    st.divider()

    st.header("Economic Exposure")

    e1, e2, e3, e4 = st.columns(4)

    e1.metric(
        "Growth Upside",
        _money(
            kpis[
                "growth_modeled_upside"
            ]
        ),
    )

    e2.metric(
        "Ageing Capital",
        _money(
            kpis[
                "ageing_capital"
            ]
        ),
    )

    e3.metric(
        "Critical Capital",
        _money(
            kpis[
                "critical_capital"
            ]
        ),
    )

    e4.metric(
        "Transfer Upside",
        _money(
            kpis[
                "transfer_margin_upside"
            ]
        ),
    )

    # ------------------------------------------------------
    # EXECUTION HEALTH
    # ------------------------------------------------------

    st.divider()

    st.header("Execution Health")

    x1, x2, x3, x4 = st.columns(4)

    x1.metric(
        "Avg Response",
        f'{kpis["average_response_minutes"]:.0f} min',
    )

    x2.metric(
        "Avg Recon",
        f'{kpis["average_recon_days"]:.1f}d',
    )

    x3.metric(
        "SLA Breach",
        _percent(
            kpis["sla_breach_rate"]
        ),
    )

    x4.metric(
        "Rework",
        _percent(
            kpis["rework_rate"]
        ),
    )

    # ------------------------------------------------------
    # DECISION QUEUE
    # ------------------------------------------------------

    st.divider()

    st.header("Leadership Decision Queue")

    st.caption(
        "Cross-functional decisions ranked by "
        "priority and modeled economic impact."
    )

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "P0 Decisions",
        int(decisions["p0_decisions"]),
    )

    q2.metric(
        "P1 Decisions",
        int(decisions["p1_decisions"]),
    )

    q3.metric(
        "Decision Impact",
        _money(
            decisions["modeled_impact"]
        ),
    )

    # Filters

    filter_col1, filter_col2 = (
        st.columns(2)
    )

    with filter_col1:
        selected_domains = st.multiselect(
            "Domain",
            [
                "Growth",
                "Inventory",
                "Operations",
            ],
            default=[
                "Growth",
                "Inventory",
                "Operations",
            ],
        )

    with filter_col2:
        selected_priorities = st.multiselect(
            "Priority",
            [
                "P0",
                "P1",
                "P2",
            ],
            default=[
                "P0",
                "P1",
            ],
        )

    filtered_signals = [
        signal
        for signal in signals
        if (
            signal.domain
            in selected_domains
            and signal.priority
            in selected_priorities
        )
    ]

    # ------------------------------------------------------
    # SIGNAL CARDS
    # ------------------------------------------------------

    for index, signal in enumerate(
        filtered_signals,
        start=1,
    ):
        with st.container(border=True):

            left, right = st.columns(
                [4, 1]
            )

            with left:
                st.caption(
                    f"{signal.priority} · "
                    f"{signal.domain.upper()} · "
                    f"DECISION {index:02d}"
                )

                st.subheader(
                    f"{_priority_icon(signal.priority)} "
                    f"{signal.title}"
                )

                st.write(
                    signal.summary
                )

                st.markdown(
                    "**Recommended action**"
                )

                st.write(
                    signal.recommended_action
                )

                st.caption(
                    f"Source: {signal.source}"
                )

            with right:
                st.caption(
                    "MODELED IMPACT"
                )

                st.subheader(
                    _money(
                        signal.modeled_impact
                    )
                )

                st.caption(
                    f"{_percent(signal.confidence)} "
                    "confidence"
                )

                st.button(
                    "Open decision",
                    key=(
                        f"executive_decision_"
                        f"{index}"
                    ),
                    use_container_width=True,
                )


# ==========================================================
# MORNING BRIEF PAGE
# ==========================================================


def render_morning_brief() -> None:
    brief = morning_brief()
    health = executive_health()
    decisions = decision_summary()

    st.caption("EXECUTIVE BRIEFING")

    st.title(
        "Good morning. Here's what changed."
    )

    st.write(
        "A concise operating brief generated from "
        "Growth, Inventory and Operations Intelligence."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Critical Decisions",
        int(
            decisions[
                "p0_decisions"
            ]
        ),
    )

    c2.metric(
        "Open Decisions",
        int(
            decisions[
                "open_decisions"
            ]
        ),
    )

    c3.metric(
        "Modeled Impact",
        _money(
            decisions[
                "modeled_impact"
            ]
        ),
    )

    st.divider()

    # ------------------------------------------------------
    # DOMAIN STATUS
    # ------------------------------------------------------

    st.header("System Status")

    columns = st.columns(4)

    for column, (
        domain,
        status,
    ) in zip(
        columns,
        health["status"].items(),
    ):
        with column:
            with st.container(border=True):

                st.caption(
                    domain.upper()
                )

                st.subheader(
                    f"{_health_icon(status)} "
                    f"{status}"
                )

    # ------------------------------------------------------
    # BRIEFING
    # ------------------------------------------------------

    st.divider()

    st.header(
        "Today's Leadership Brief"
    )

    for index, signal in enumerate(
        brief,
        start=1,
    ):
        with st.container(border=True):

            st.caption(
                f"{signal.priority} · "
                f"{signal.domain.upper()}"
            )

            st.subheader(
                f"{index}. {signal.title}"
            )

            st.write(
                signal.summary
            )

            col1, col2 = st.columns(
                [3, 1]
            )

            with col1:
                st.markdown(
                    "**What to do**"
                )

                st.write(
                    signal.recommended_action
                )

            with col2:
                st.metric(
                    "Potential Impact",
                    _money(
                        signal.modeled_impact
                    ),
                )

                st.caption(
                    f"{_percent(signal.confidence)} "
                    "confidence"
                )

    # ------------------------------------------------------
    # END-OF-BRIEF SUMMARY
    # ------------------------------------------------------

    st.divider()

    st.subheader(
        "Leadership takeaway"
    )

    if brief:
        top = brief[0]

        st.info(
            f"The highest-priority signal today is "
            f"{top.title} in {top.domain}. "
            f"The modeled economic impact is "
            f"{_money(top.modeled_impact)}."
        )

    else:
        st.success(
            "No material executive signals "
            "require intervention."
        )
