from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from engines.builder_intelligence import (
    build_opportunity_radar,
    experiment_summary,
)
from engines.growth_intelligence import (
    filter_growth_data,
    growth_executive_summary,
    load_growth_data,
)
from engines.inventory_intelligence import (
    capital_intelligence,
    detect_inventory_decisions,
    inventory_kpis,
    load_inventory_data,
)
from engines.operations_intelligence import (
    detect_operations_actions,
    operations_summary,
)


# ==========================================================
# DATA CLASSES
# ==========================================================


@dataclass
class ExecutiveSignal:
    priority: str
    domain: str
    title: str
    summary: str
    modeled_impact: float
    confidence: float
    recommended_action: str
    source: str


@dataclass
class ExecutiveMetric:
    label: str
    value: float
    unit: str
    context: str


# ==========================================================
# EXECUTIVE KPI LAYER
# ==========================================================


def executive_kpis() -> Dict[str, float]:
    """
    Combine the strongest executive-level measures from
    Growth, Inventory, Operations and Builder Intelligence.
    """

    # ------------------------------------------------------
    # GROWTH
    # ------------------------------------------------------

    growth = filter_growth_data(
        load_growth_data(),
        month="2026-08",
    )

    growth_summary = (
        growth_executive_summary(
            growth
        )
    )

    growth_kpis = growth_summary[
        "kpis"
    ]

    # ------------------------------------------------------
    # INVENTORY
    # ------------------------------------------------------

    inventory = (
        load_inventory_data()
    )

    inventory_summary = (
        inventory_kpis(
            inventory
        )
    )

    capital_summary = (
        capital_intelligence(
            inventory
        )
    )

    # ------------------------------------------------------
    # OPERATIONS
    # ------------------------------------------------------

    operations = (
        operations_summary()
    )

    # ------------------------------------------------------
    # BUILDER
    # ------------------------------------------------------

    opportunities = (
        build_opportunity_radar()
    )

    experiments = (
        experiment_summary()
    )

    modeled_opportunity = sum(
        item.modeled_impact
        for item in opportunities
    )

    return {
        "revenue": float(
            growth_kpis[
                "revenue"
            ]
        ),
        "sales": float(
            growth_kpis[
                "sales"
            ]
        ),
        "enquiry_to_sale": float(
            growth_kpis[
                "enquiry_to_sale"
            ]
        ),
        "average_response_minutes": float(
            growth_kpis[
                "average_response_minutes"
            ]
        ),
        "growth_modeled_upside": float(
            growth_summary[
                "modeled_monthly_upside"
            ]
        ),
        "capital_deployed": float(
            inventory_summary[
                "capital_deployed"
            ]
        ),
        "expected_contribution": float(
            inventory_summary[
                "expected_contribution"
            ]
        ),
        "capital_at_risk": float(
            inventory_summary[
                "capital_at_risk"
            ]
        ),
        "average_inventory_age": float(
            inventory_summary[
                "average_age_days"
            ]
        ),
        "productive_capital": float(
            capital_summary[
                "productive_capital"
            ]
        ),
        "ageing_capital": float(
            capital_summary[
                "ageing_capital"
            ]
        ),
        "critical_capital": float(
            capital_summary[
                "critical_capital"
            ]
        ),
        "modeled_capital_release": float(
            capital_summary[
                "modeled_capital_release"
            ]
        ),
        "average_recon_days": float(
            operations[
                "average_recon_days"
            ]
        ),
        "sla_breach_rate": float(
            operations[
                "sla_breach_rate"
            ]
        ),
        "rework_rate": float(
            operations[
                "rework_rate"
            ]
        ),
        "transfer_opportunities": float(
            operations[
                "transfer_opportunities"
            ]
        ),
        "transfer_margin_upside": float(
            operations[
                "transfer_margin_upside"
            ]
        ),
        "open_actions": float(
            operations[
                "open_actions"
            ]
        ),
        "total_modeled_opportunity": float(
            modeled_opportunity
        ),
        "running_experiments": float(
            experiments[
                "running"
            ]
        ),
        "scaled_experiments": float(
            experiments[
                "scaled"
            ]
        ),
        "experiment_expected_impact": float(
            experiments[
                "expected_impact"
            ]
        ),
    }


# ==========================================================
# SIGNAL NORMALIZATION
# ==========================================================


def _growth_signals() -> List[
    ExecutiveSignal
]:
    """
    Convert Growth Intelligence into executive signals.
    """

    growth = filter_growth_data(
        load_growth_data(),
        month="2026-08",
    )

    summary = (
        growth_executive_summary(
            growth
        )
    )

    signals: List[
        ExecutiveSignal
    ] = []

    for opportunity in summary[
        "top_opportunities"
    ]:

        signals.append(
            ExecutiveSignal(
                priority=(
                    opportunity.priority
                ),
                domain="Growth",
                title=(
                    f"{opportunity.location} · "
                    f"{opportunity.segment}"
                ),
                summary=(
                    opportunity.evidence
                ),
                modeled_impact=(
                    opportunity
                    .modeled_monthly_revenue_upside
                ),
                confidence=(
                    opportunity.confidence
                ),
                recommended_action=(
                    opportunity
                    .recommended_action
                ),
                source=(
                    "Growth Intelligence"
                ),
            )
        )

    return signals


def _inventory_signals() -> List[
    ExecutiveSignal
]:
    """
    Convert Inventory Intelligence into executive signals.
    """

    inventory = (
        load_inventory_data()
    )

    decisions = (
        detect_inventory_decisions(
            inventory
        )
    )

    signals: List[
        ExecutiveSignal
    ] = []

    for decision in decisions:

        if decision.priority not in {
            "P0",
            "P1",
        }:
            continue

        signals.append(
            ExecutiveSignal(
                priority=(
                    decision.priority
                ),
                domain="Inventory",
                title=(
                    f"{decision.make} "
                    f"{decision.model} · "
                    f"{decision.vehicle_id}"
                ),
                summary=(
                    decision.reason
                ),
                modeled_impact=(
                    decision.expected_impact
                ),
                confidence=(
                    decision.confidence
                ),
                recommended_action=(
                    decision.decision
                ),
                source=(
                    "Inventory Intelligence"
                ),
            )
        )

    return signals


def _operations_signals() -> List[
    ExecutiveSignal
]:
    """
    Convert Operations Intelligence into executive signals.
    """

    actions = (
        detect_operations_actions()
    )

    signals: List[
        ExecutiveSignal
    ] = []

    for action in actions:

        signals.append(
            ExecutiveSignal(
                priority=(
                    action.priority
                ),
                domain="Operations",
                title=(
                    action.entity
                ),
                summary=(
                    action.evidence
                ),
                modeled_impact=(
                    action.expected_impact
                ),
                confidence=(
                    action.confidence
                ),
                recommended_action=(
                    action.recommended_action
                ),
                source=(
                    "Operations Intelligence"
                ),
            )
        )

    return signals


# ==========================================================
# EXECUTIVE SIGNAL QUEUE
# ==========================================================


def executive_signals() -> List[
    ExecutiveSignal
]:
    """
    Build one ranked executive signal queue.

    Priority is considered first, then modeled impact.
    """

    signals = (
        _growth_signals()
        + _inventory_signals()
        + _operations_signals()
    )

    priority_order = {
        "P0": 0,
        "P1": 1,
        "P2": 2,
    }

    signals.sort(
        key=lambda item: (
            priority_order.get(
                item.priority,
                9,
            ),
            -item.modeled_impact,
        )
    )

    return signals


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================


def executive_summary() -> Dict[
    str,
    object,
]:
    """
    Main payload consumed by the Executive UI.
    """

    kpis = executive_kpis()

    signals = executive_signals()

    p0_signals = [
        item
        for item in signals
        if item.priority == "P0"
    ]

    p1_signals = [
        item
        for item in signals
        if item.priority == "P1"
    ]

    return {
        "kpis": kpis,
        "signals": signals,
        "top_signals": signals[:5],
        "p0_count": len(
            p0_signals
        ),
        "p1_count": len(
            p1_signals
        ),
        "total_signal_count": len(
            signals
        ),
        "top_signal": (
            signals[0]
            if signals
            else None
        ),
    }


# ==========================================================
# MORNING BRIEF
# ==========================================================


def morning_brief() -> List[
    ExecutiveSignal
]:
    """
    Return a concise executive briefing.

    Keep the brief focused on the highest-priority
    signals across different domains where possible.
    """

    signals = (
        executive_signals()
    )

    if not signals:
        return []

    brief: List[
        ExecutiveSignal
    ] = []

    used_domains = set()

    # First pass:
    # try to surface one meaningful signal per domain.
    for signal in signals:

        if signal.domain in used_domains:
            continue

        brief.append(
            signal
        )

        used_domains.add(
            signal.domain
        )

        if len(brief) >= 3:
            break

    # Second pass:
    # fill remaining slots from highest-ranked signals.
    if len(brief) < 5:

        for signal in signals:

            if signal in brief:
                continue

            brief.append(
                signal
            )

            if len(brief) >= 5:
                break

    return brief


# ==========================================================
# DECISION SUMMARY
# ==========================================================


def decision_summary() -> Dict[
    str,
    float,
]:
    """
    Compact executive decision-queue summary.
    """

    signals = (
        executive_signals()
    )

    return {
        "open_decisions": float(
            len(
                signals
            )
        ),
        "p0_decisions": float(
            sum(
                1
                for signal in signals
                if signal.priority == "P0"
            )
        ),
        "p1_decisions": float(
            sum(
                1
                for signal in signals
                if signal.priority == "P1"
            )
        ),
        "modeled_impact": float(
            sum(
                signal.modeled_impact
                for signal in signals
            )
        ),
        "average_confidence": float(
            sum(
                signal.confidence
                for signal in signals
            )
            / len(
                signals
            )
            if signals
            else 0
        ),
    }


# ==========================================================
# EXECUTIVE HEALTH
# ==========================================================


def executive_health() -> Dict[
    str,
    object,
]:
    """
    Create simple health indicators for the Executive UI.
    """

    kpis = executive_kpis()

    health = {
        "growth": "Healthy",
        "inventory": "Watch",
        "operations": "Watch",
        "builder": "Healthy",
    }

    if (
        kpis[
            "growth_modeled_upside"
        ]
        > 500000
    ):
        health[
            "growth"
        ] = "Opportunity"

    if (
        kpis[
            "capital_at_risk"
        ]
        > 1000000
    ):
        health[
            "inventory"
        ] = "Critical"

    if (
        kpis[
            "sla_breach_rate"
        ]
        > 0.35
    ):
        health[
            "operations"
        ] = "Critical"

    if (
        kpis[
            "running_experiments"
        ]
        <= 0
    ):
        health[
            "builder"
        ] = "Watch"

    return {
        "status": health,
        "critical_domains": [
            domain
            for domain, state
            in health.items()
            if state == "Critical"
        ],
        "opportunity_domains": [
            domain
            for domain, state
            in health.items()
            if state == "Opportunity"
        ],
    }
