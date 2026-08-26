from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from engines.growth_intelligence import (
    detect_growth_opportunities,
    filter_growth_data,
    load_growth_data,
)
from engines.inventory_intelligence import (
    detect_inventory_decisions,
    load_inventory_data,
)
from engines.operations_intelligence import (
    detect_operations_actions,
)


# ==========================================================
# DATA CLASSES
# ==========================================================


@dataclass
class BuilderOpportunity:
    priority: str
    domain: str
    entity: str
    title: str
    evidence: str
    recommended_action: str
    modeled_impact: float
    confidence: float
    source: str


@dataclass
class ScenarioResult:
    scenario_name: str
    baseline_value: float
    modeled_value: float
    delta_value: float
    delta_pct: float
    assumptions: Dict[str, float]
    interpretation: str


@dataclass
class Experiment:
    experiment_id: str
    title: str
    domain: str
    hypothesis: str
    metric: str
    baseline: float
    target: float
    duration_days: int
    owner: str
    status: str
    confidence: float
    expected_impact: float


# ==========================================================
# OPPORTUNITY RADAR
# ==========================================================


def build_opportunity_radar() -> List[BuilderOpportunity]:
    """
    Combine Growth, Inventory and Operations intelligence
    into one cross-functional opportunity queue.
    """

    opportunities: List[BuilderOpportunity] = []

    # ------------------------------------------------------
    # GROWTH
    # ------------------------------------------------------

    growth = load_growth_data()

    growth = filter_growth_data(
        growth,
        month="2026-08",
    )

    for item in detect_growth_opportunities(
        growth
    ):

        opportunities.append(
            BuilderOpportunity(
                priority=item.priority,
                domain="Growth",
                entity=(
                    f"{item.location} · "
                    f"{item.segment}"
                ),
                title=item.issue,
                evidence=item.evidence,
                recommended_action=(
                    item.recommended_action
                ),
                modeled_impact=(
                    item
                    .modeled_monthly_revenue_upside
                ),
                confidence=item.confidence,
                source="Growth Intelligence",
            )
        )

    # ------------------------------------------------------
    # INVENTORY
    # ------------------------------------------------------

    inventory = load_inventory_data()

    for item in detect_inventory_decisions(
        inventory
    ):

        if item.priority not in {
            "P0",
            "P1",
        }:
            continue

        opportunities.append(
            BuilderOpportunity(
                priority=item.priority,
                domain="Inventory",
                entity=(
                    f"{item.make} "
                    f"{item.model} · "
                    f"{item.vehicle_id}"
                ),
                title=item.decision,
                evidence=item.reason,
                recommended_action=(
                    item.decision
                ),
                modeled_impact=(
                    item.expected_impact
                ),
                confidence=item.confidence,
                source="Inventory Intelligence",
            )
        )

    # ------------------------------------------------------
    # OPERATIONS
    # ------------------------------------------------------

    for item in detect_operations_actions():

        opportunities.append(
            BuilderOpportunity(
                priority=item.priority,
                domain="Operations",
                entity=item.entity,
                title=item.issue,
                evidence=item.evidence,
                recommended_action=(
                    item.recommended_action
                ),
                modeled_impact=(
                    item.expected_impact
                ),
                confidence=item.confidence,
                source="Operations Intelligence",
            )
        )

    opportunities.sort(
        key=lambda item: (
            item.priority,
            -item.modeled_impact,
        )
    )

    return opportunities


def opportunity_summary() -> Dict[str, float]:
    opportunities = (
        build_opportunity_radar()
    )

    return {
        "opportunities": float(
            len(
                opportunities
            )
        ),
        "p0": float(
            sum(
                1
                for item in opportunities
                if item.priority == "P0"
            )
        ),
        "p1": float(
            sum(
                1
                for item in opportunities
                if item.priority == "P1"
            )
        ),
        "modeled_impact": float(
            sum(
                item.modeled_impact
                for item in opportunities
            )
        ),
        "average_confidence": float(
            sum(
                item.confidence
                for item in opportunities
            )
            / len(
                opportunities
            )
            if opportunities
            else 0
        ),
    }


# ==========================================================
# SCENARIO LAB
# ==========================================================


def simulate_growth_scenario(
    response_time_improvement_pct: float,
    test_drive_conversion_lift_pp: float,
    additional_inventory_pct: float,
) -> ScenarioResult:
    """
    Simulate a growth intervention.
    """

    growth = filter_growth_data(
        load_growth_data(),
        month="2026-08",
    )

    baseline_revenue = float(
        growth[
            "revenue"
        ].sum()
    )

    baseline_sales = float(
        growth[
            "sales"
        ].sum()
    )

    response_effect = (
        response_time_improvement_pct
        * 0.15
    )

    conversion_effect = (
        test_drive_conversion_lift_pp
        / 100
        * 0.70
    )

    inventory_effect = (
        additional_inventory_pct
        / 100
        * 0.22
    )

    modeled_revenue = (
        baseline_revenue
        * (
            1
            + response_effect
            + conversion_effect
            + inventory_effect
        )
    )

    delta = (
        modeled_revenue
        - baseline_revenue
    )

    delta_pct = (
        delta
        / baseline_revenue
        if baseline_revenue
        else 0
    )

    interpretation = (
        "Growth improves primarily through "
        "faster customer response and better "
        "enquiry-to-test-drive conversion."
    )

    return ScenarioResult(
        scenario_name="Growth Acceleration",
        baseline_value=baseline_revenue,
        modeled_value=modeled_revenue,
        delta_value=delta,
        delta_pct=delta_pct,
        assumptions={
            "response_time_improvement_pct": (
                response_time_improvement_pct
            ),
            "test_drive_conversion_lift_pp": (
                test_drive_conversion_lift_pp
            ),
            "additional_inventory_pct": (
                additional_inventory_pct
            ),
            "baseline_sales": (
                baseline_sales
            ),
        },
        interpretation=interpretation,
    )


def simulate_inventory_scenario(
    inventory_age_reduction_days: float,
    pricing_efficiency_pct: float,
    transfer_adoption_pct: float,
) -> ScenarioResult:
    """
    Simulate inventory and capital efficiency.
    """

    inventory = load_inventory_data()

    baseline_capital = float(
        inventory[
            "landed_cost"
        ].sum()
    )

    daily_holding_burn = float(
        inventory[
            "holding_cost_per_day"
        ].sum()
    )

    holding_saving = (
        daily_holding_burn
        * inventory_age_reduction_days
    )

    pricing_gain = (
        float(
            inventory[
                "expected_contribution"
            ].sum()
        )
        * pricing_efficiency_pct
        / 100
    )

    transfer_gain = (
        float(
            inventory[
                "capital_at_risk"
            ].sum()
        )
        * transfer_adoption_pct
        / 100
        * 0.035
    )

    modeled_value = (
        baseline_capital
        + holding_saving
        + pricing_gain
        + transfer_gain
    )

    delta = (
        modeled_value
        - baseline_capital
    )

    delta_pct = (
        delta
        / baseline_capital
        if baseline_capital
        else 0
    )

    return ScenarioResult(
        scenario_name="Inventory Productivity",
        baseline_value=baseline_capital,
        modeled_value=modeled_value,
        delta_value=delta,
        delta_pct=delta_pct,
        assumptions={
            "inventory_age_reduction_days": (
                inventory_age_reduction_days
            ),
            "pricing_efficiency_pct": (
                pricing_efficiency_pct
            ),
            "transfer_adoption_pct": (
                transfer_adoption_pct
            ),
        },
        interpretation=(
            "Capital productivity improves by reducing "
            "holding time, protecting margin and reallocating "
            "inventory toward stronger demand."
        ),
    )


def simulate_operations_scenario(
    recon_day_reduction: float,
    sla_improvement_pp: float,
    conversion_lift_pp: float,
) -> ScenarioResult:
    """
    Simulate operational throughput improvements.
    """

    baseline_operating_value = 715000.0

    recon_gain = (
        recon_day_reduction
        * 32000
    )

    sla_gain = (
        sla_improvement_pp
        * 5500
    )

    conversion_gain = (
        conversion_lift_pp
        * 21000
    )

    modeled_value = (
        baseline_operating_value
        + recon_gain
        + sla_gain
        + conversion_gain
    )

    delta = (
        modeled_value
        - baseline_operating_value
    )

    delta_pct = (
        delta
        / baseline_operating_value
    )

    return ScenarioResult(
        scenario_name="Operations Throughput",
        baseline_value=(
            baseline_operating_value
        ),
        modeled_value=(
            modeled_value
        ),
        delta_value=delta,
        delta_pct=delta_pct,
        assumptions={
            "recon_day_reduction": (
                recon_day_reduction
            ),
            "sla_improvement_pp": (
                sla_improvement_pp
            ),
            "conversion_lift_pp": (
                conversion_lift_pp
            ),
        },
        interpretation=(
            "Operating contribution improves when recon "
            "throughput, SLA performance and conversion "
            "improve together."
        ),
    )


# ==========================================================
# EXPERIMENTS
# ==========================================================


def load_experiments() -> pd.DataFrame:
    """
    Deterministic synthetic experiment portfolio.
    """

    rows = [
        {
            "experiment_id": "EXP-001",
            "title": (
                "Melbourne lead response sprint"
            ),
            "domain": "Growth",
            "hypothesis": (
                "Reducing first-response time below "
                "15 minutes will improve enquiry-to-test-drive conversion."
            ),
            "metric": (
                "Enquiry → Test Drive"
            ),
            "baseline": 0.31,
            "target": 0.39,
            "duration_days": 14,
            "owner": "Growth Lead",
            "status": "Running",
            "confidence": 0.72,
            "expected_impact": 214000,
        },
        {
            "experiment_id": "EXP-002",
            "title": (
                "Melbourne recon vendor reallocation"
            ),
            "domain": "Operations",
            "hypothesis": (
                "Moving 30% of recon volume away from "
                "the weakest vendor will reduce turnaround time."
            ),
            "metric": (
                "Recon Days"
            ),
            "baseline": 5.7,
            "target": 4.3,
            "duration_days": 21,
            "owner": "Operations Lead",
            "status": "Running",
            "confidence": 0.68,
            "expected_impact": 46000,
        },
        {
            "experiment_id": "EXP-003",
            "title": (
                "Brisbane SUV acquisition expansion"
            ),
            "domain": "Inventory",
            "hypothesis": (
                "Increasing Brisbane SUV acquisition by "
                "10% will produce profitable incremental volume."
            ),
            "metric": (
                "SUV Sales"
            ),
            "baseline": 100,
            "target": 112,
            "duration_days": 30,
            "owner": "Supply Lead",
            "status": "Planned",
            "confidence": 0.64,
            "expected_impact": 153000,
        },
        {
            "experiment_id": "EXP-004",
            "title": (
                "Sydney response-time automation"
            ),
            "domain": "Growth",
            "hypothesis": (
                "Automated lead routing will reduce median "
                "response time while maintaining qualification quality."
            ),
            "metric": (
                "Response Minutes"
            ),
            "baseline": 13,
            "target": 8,
            "duration_days": 14,
            "owner": "Growth Ops",
            "status": "Scaled",
            "confidence": 0.93,
            "expected_impact": 88000,
        },
        {
            "experiment_id": "EXP-005",
            "title": (
                "Adelaide → Brisbane SUV transfer test"
            ),
            "domain": "Operations",
            "hypothesis": (
                "Transferring ageing SUVs into stronger Brisbane "
                "demand will reduce days-to-sale."
            ),
            "metric": (
                "Days to Sale"
            ),
            "baseline": 22,
            "target": 16,
            "duration_days": 21,
            "owner": "Inventory Ops",
            "status": "Running",
            "confidence": 0.79,
            "expected_impact": 51000,
        },
    ]

    return pd.DataFrame(
        rows
    )


def experiment_summary() -> Dict[str, float]:
    df = load_experiments()

    return {
        "experiments": float(
            len(df)
        ),
        "running": float(
            (
                df["status"]
                == "Running"
            ).sum()
        ),
        "scaled": float(
            (
                df["status"]
                == "Scaled"
            ).sum()
        ),
        "planned": float(
            (
                df["status"]
                == "Planned"
            ).sum()
        ),
        "expected_impact": float(
            df[
                "expected_impact"
            ].sum()
        ),
        "average_confidence": float(
            df[
                "confidence"
            ].mean()
        ),
    }


# ==========================================================
# BUILDER SUMMARY
# ==========================================================


def builder_summary() -> Dict[str, object]:
    opportunity = (
        opportunity_summary()
    )

    experiments = (
        experiment_summary()
    )

    return {
        "opportunity_summary": (
            opportunity
        ),
        "experiment_summary": (
            experiments
        ),
        "top_opportunities": (
            build_opportunity_radar()[:10]
        ),
    }
