from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from agents.builder_briefing import build_briefing
from economics.unit_economics import calculate_unit_economics
from engines.initiative_engine import rank_initiatives
from engines.opportunity_engine import evaluate_vehicle
from engines.scenario_engine import (
    ScenarioInputs,
    apply_scenario,
)
from models.vehicle import Vehicle


DATA_PATH = ROOT / "data" / "synthetic_vehicle_portfolio.json"


def load_portfolio() -> list[Vehicle]:
    payload = json.loads(
        DATA_PATH.read_text()
    )

    return [
        Vehicle.model_validate(item)
        for item in payload
    ]


def money(value: float) -> str:
    return f"A${value:,.0f}"


st.set_page_config(
    page_title="CARS24 Australia — Builder OS",
    page_icon="🚗",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1450px;
    }

    .hero-label {
        font-size: 0.8rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.6;
        margin-bottom: 0.3rem;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.05;
        margin-bottom: 0.5rem;
    }

    .hero-copy {
        font-size: 1.05rem;
        opacity: 0.72;
        max-width: 850px;
    }

    .synthetic-note {
        padding: 0.8rem 1rem;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
    }

    .action-card {
        padding: 1rem;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        margin-bottom: 0.75rem;
    }

    .action-title {
        font-size: 1rem;
        font-weight: 700;
    }

    .action-meta {
        font-size: 0.86rem;
        opacity: 0.65;
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


vehicles = load_portfolio()

briefing = build_briefing(
    vehicles,
    action_limit=5,
)


st.markdown(
    '<div class="hero-label">Outside-in operating prototype</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">CARS24 Australia — Builder Command Centre</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-copy">
    What would I investigate, prioritise and build if I joined
    the Australia business tomorrow?
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="synthetic-note">
    <strong>Important:</strong>
    This is not a proposed CARS24 product and does not use
    confidential CARS24 information. All operational data is
    synthetic. The prototype demonstrates the decision
    architecture and Builder methodology.
    </div>
    """,
    unsafe_allow_html=True,
)


tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Command Centre",
        "Vehicle Intelligence",
        "Builder Simulator",
        "Strategic Bets",
    ]
)


with tab1:

    st.subheader("Portfolio Pulse")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Vehicles",
        briefing.vehicles_analysed,
    )

    c2.metric(
        "Capital deployed",
        money(briefing.capital_deployed),
    )

    c3.metric(
        "Expected contribution",
        money(briefing.expected_contribution),
    )

    c4.metric(
        "Capital requiring attention",
        money(briefing.capital_at_risk),
    )

    c5.metric(
        "Critical interventions",
        briefing.critical_interventions,
    )

    st.divider()

    st.subheader("What should we attack first?")

    st.success(
        f"**{briefing.top_initiative}**\n\n"
        f"{briefing.top_initiative_reason}"
    )

    st.subheader("Top 5 Actions Today")

    for action in briefing.priority_actions:

        st.markdown(
            f"""
            <div class="action-card">
                <div class="action-title">
                    #{action.rank} — {action.headline}
                </div>
                <div class="action-meta">
                    Modeled impact:
                    {money(action.modeled_impact)}
                    &nbsp; • &nbsp;
                    Confidence:
                    {action.confidence:.0%}
                </div>
                <div style="margin-top:0.55rem">
                    {action.detail}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


with tab2:

    st.subheader("Vehicle Intelligence")

    vehicle_map = {
        (
            f"{vehicle.identity.vehicle_id} — "
            f"{vehicle.identity.year} "
            f"{vehicle.identity.make} "
            f"{vehicle.identity.model}"
        ): vehicle
        for vehicle in vehicles
    }

    selected_label = st.selectbox(
        "Choose a vehicle",
        list(vehicle_map.keys()),
    )

    selected = vehicle_map[selected_label]

    economics = calculate_unit_economics(
        selected
    )

    opportunities = evaluate_vehicle(
        selected
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Acquisition",
        money(
            selected.acquisition.acquisition_price
        ),
    )

    c2.metric(
        "Current list price",
        money(
            selected.pricing.current_list_price
            or selected.pricing.expected_market_price
        ),
    )

    c3.metric(
        "Expected contribution",
        money(
            economics.expected_contribution
        ),
    )

    c4.metric(
        "Inventory days",
        selected.inventory.days_in_inventory,
    )

    st.markdown("### Vehicle State")

    left, right = st.columns(2)

    with left:
        st.write(
            "**Location:**",
            selected.inventory.current_location.value,
        )

        st.write(
            "**Acquisition source:**",
            selected.acquisition.source.value,
        )

        st.write(
            "**Condition score:**",
            selected.condition.inspection_score,
        )

        st.write(
            "**Demand:**",
            selected.demand.level.value,
        )

    with right:
        st.write(
            "**Invested capital:**",
            money(economics.invested_capital),
        )

        st.write(
            "**Lifecycle risk cost:**",
            money(economics.expected_risk_cost),
        )

        st.write(
            "**Contribution margin:**",
            f"{economics.contribution_margin_pct:.1f}%",
        )

        st.write(
            "**Refurbishment ROI:**",
            f"{economics.refurbishment_roi:.1%}",
        )

    st.markdown("### Recommended Actions")

    for opportunity in opportunities:

        st.info(
            f"**{opportunity.action.value} "
            f"— {opportunity.priority.value}**\n\n"
            f"{opportunity.reason}\n\n"
            f"Modeled impact: "
            f"{money(opportunity.estimated_impact)} "
            f"• Confidence: "
            f"{opportunity.confidence:.0%}"
        )


with tab3:

    st.subheader("Builder Scenario Simulator")

    st.caption(
        "Change operating assumptions and observe modeled "
        "portfolio-level consequences."
    )

    left, right = st.columns(2)

    with left:

        acquisition_improvement = st.slider(
            "Acquisition cost improvement (%)",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.5,
        )

        refurbishment_improvement = st.slider(
            "Refurbishment cost improvement (%)",
            min_value=0.0,
            max_value=25.0,
            value=10.0,
            step=1.0,
        )

        inventory_improvement = st.slider(
            "Inventory cycle improvement (days)",
            min_value=0,
            max_value=20,
            value=7,
            step=1,
        )

    with right:

        markdown_improvement = st.slider(
            "Markdown risk reduction (%)",
            min_value=0.0,
            max_value=40.0,
            value=15.0,
            step=1.0,
        )

        warranty_improvement = st.slider(
            "Warranty risk reduction (%)",
            min_value=0.0,
            max_value=40.0,
            value=10.0,
            step=1.0,
        )

        transfers_enabled = st.toggle(
            "Execute profitable geographic transfers",
            value=True,
        )

    scenario = apply_scenario(
        vehicles,
        ScenarioInputs(
            acquisition_cost_reduction_pct=(
                acquisition_improvement
            ),
            refurbishment_cost_reduction_pct=(
                refurbishment_improvement
            ),
            inventory_days_reduction=(
                inventory_improvement
            ),
            markdown_risk_reduction_pct=(
                markdown_improvement
            ),
            warranty_risk_reduction_pct=(
                warranty_improvement
            ),
            execute_profitable_transfers=(
                transfers_enabled
            ),
        ),
    )

    st.divider()

    st.markdown("### Modeled Impact")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Contribution",
        money(
            scenario.scenario_contribution
        ),
        delta=money(
            scenario.contribution_improvement
        ),
    )

    c2.metric(
        "Capital deployed",
        money(
            scenario.scenario_capital
        ),
        delta=(
            f"-{money(scenario.capital_released)}"
        ),
        delta_color="inverse",
    )

    c3.metric(
        "Lifecycle risk",
        money(
            scenario.scenario_risk_cost
        ),
        delta=(
            f"-{money(scenario.risk_cost_reduction)}"
        ),
        delta_color="inverse",
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "90+ day inventory capital",
        money(
            scenario.scenario_90_plus_day_capital
        ),
    )

    c5.metric(
        "Vehicles transferred",
        scenario.vehicles_transferred,
    )

    c6.metric(
        "Modeled transfer impact",
        money(
            scenario.modeled_transfer_impact
        ),
    )

    st.warning(
        "Scenario outputs are illustrative synthetic economics, "
        "not forecasts of actual CARS24 performance."
    )


with tab4:

    st.subheader("Strategic Bets")

    initiatives = rank_initiatives(
        vehicles
    )

    for index, initiative in enumerate(
        initiatives,
        start=1,
    ):

        with st.expander(
            f"#{index} — {initiative.name}",
            expanded=(index == 1),
        ):

            st.write(
                initiative.description
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Contribution impact",
                money(
                    initiative.contribution_impact
                ),
            )

            c2.metric(
                "Capital released",
                money(
                    initiative.capital_released
                ),
            )

            c3.metric(
                "Risk reduction",
                money(
                    initiative.risk_reduction
                ),
            )

            st.write(
                "**Time to impact:**",
                f"{initiative.time_to_impact_days} days",
            )

            st.write(
                "**Effort score:**",
                initiative.effort_score,
            )

            st.write(
                "**Implementation risk:**",
                initiative.implementation_risk,
            )

            st.write(
                "**Priority score:**",
                initiative.priority_score,
            )


st.divider()

st.caption(
    "Built as an independent Business Builder application exercise. "
    "Public research + explicitly synthetic operating data."
)
