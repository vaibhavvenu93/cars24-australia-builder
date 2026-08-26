from __future__ import annotations

from typing import Dict, List, Set

from models.integration import (
    IntelligenceCapability,
    IntelligenceCoverage,
    IntegrationCategory,
    IntegrationSource,
    IntegrationStatus,
)


def get_integration_sources() -> List[IntegrationSource]:
    """
    Synthetic integration registry for the CARS24 Australia
    Intelligence OS prototype.

    These sources demonstrate how the OS would adapt as more
    operational systems are connected.

    No live CARS24 systems are connected.
    """

    return [
        IntegrationSource(
            source_id="inventory_core",
            name="Inventory / Fleet System",
            category=IntegrationCategory.INVENTORY,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Vehicle lifecycle, acquisition, location, ageing, "
                "listing status and inventory movement."
            ),
            coverage_pct=100,
            records_available=150,
            last_sync="2 min ago",
            capabilities=[
                IntelligenceCapability.VEHICLE_ECONOMICS,
                IntelligenceCapability.INVENTORY_AGEING,
                IntelligenceCapability.CAPITAL_EFFICIENCY,
            ],
            available_fields=[
                "vehicle_id",
                "vin",
                "make",
                "model",
                "year",
                "location",
                "acquisition_date",
                "acquisition_price",
                "listing_price",
                "inventory_age_days",
                "status",
            ],
            missing_fields=[],
        ),
        IntegrationSource(
            source_id="crm_core",
            name="CRM / Lead Management",
            category=IntegrationCategory.CRM,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Customer enquiries, lead progression, test drives, "
                "offers and sales conversion."
            ),
            coverage_pct=82,
            records_available=2840,
            last_sync="5 min ago",
            capabilities=[
                IntelligenceCapability.DEMAND_INTELLIGENCE,
                IntelligenceCapability.FUNNEL_ANALYTICS,
                IntelligenceCapability.LEAD_CONVERSION,
            ],
            available_fields=[
                "lead_id",
                "vehicle_id",
                "source",
                "location",
                "enquiry_date",
                "test_drive_date",
                "offer_date",
                "sale_date",
                "lead_status",
            ],
            missing_fields=[
                "lost_reason",
                "response_time_seconds",
            ],
        ),
        IntegrationSource(
            source_id="finance_core",
            name="Finance / ERP",
            category=IntegrationCategory.FINANCE,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Vehicle-level cost, realised margin, holding cost "
                "and cash-cycle information."
            ),
            coverage_pct=76,
            records_available=132,
            last_sync="18 min ago",
            capabilities=[
                IntelligenceCapability.TRUE_MARGIN,
                IntelligenceCapability.CASH_CYCLE,
                IntelligenceCapability.VEHICLE_ECONOMICS,
                IntelligenceCapability.CAPITAL_EFFICIENCY,
            ],
            available_fields=[
                "vehicle_id",
                "acquisition_cost",
                "recon_cost",
                "logistics_cost",
                "holding_cost",
                "sale_price",
                "gross_profit",
            ],
            missing_fields=[
                "warranty_contribution",
                "finance_contribution",
            ],
        ),
        IntegrationSource(
            source_id="recon_network",
            name="Reconditioning Vendor Network",
            category=IntegrationCategory.RECONDITIONING,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Recon jobs, vendor cost, turnaround time, SLA "
                "performance and rework."
            ),
            coverage_pct=61,
            records_available=418,
            last_sync="31 min ago",
            capabilities=[
                IntelligenceCapability.RECON_BOTTLENECKS,
                IntelligenceCapability.VENDOR_ECONOMICS,
            ],
            available_fields=[
                "job_id",
                "vehicle_id",
                "vendor",
                "quoted_cost",
                "actual_cost",
                "start_date",
                "completion_date",
                "rework_required",
            ],
            missing_fields=[
                "defect_category",
                "parts_delay",
                "sla_reason",
            ],
        ),
        IntegrationSource(
            source_id="logistics_core",
            name="Vehicle Logistics",
            category=IntegrationCategory.LOGISTICS,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Vehicle transfers, transport cost, route duration "
                "and movement history."
            ),
            coverage_pct=73,
            records_available=224,
            last_sync="42 min ago",
            capabilities=[
                IntelligenceCapability.TRANSFER_INTELLIGENCE,
                IntelligenceCapability.LOGISTICS_EFFICIENCY,
            ],
            available_fields=[
                "vehicle_id",
                "origin",
                "destination",
                "transfer_cost",
                "dispatch_date",
                "arrival_date",
            ],
            missing_fields=[
                "carrier",
                "delay_reason",
            ],
        ),
        IntegrationSource(
            source_id="market_feed",
            name="Australian Market Data",
            category=IntegrationCategory.MARKET_DATA,
            status=IntegrationStatus.SIMULATED,
            description=(
                "Market pricing, regional demand, comparable inventory "
                "and supply signals."
            ),
            coverage_pct=88,
            records_available=12640,
            last_sync="7 min ago",
            capabilities=[
                IntelligenceCapability.MARKET_ARBITRAGE,
                IntelligenceCapability.ACQUISITION_OPPORTUNITY,
                IntelligenceCapability.DEMAND_INTELLIGENCE,
            ],
            available_fields=[
                "make",
                "model",
                "year",
                "location",
                "market_price",
                "market_supply",
                "demand_index",
                "median_days_to_sale",
            ],
            missing_fields=[
                "competitor_price_history",
            ],
        ),
        IntegrationSource(
            source_id="marketing_stack",
            name="Marketing & Attribution",
            category=IntegrationCategory.MARKETING,
            status=IntegrationStatus.NOT_CONNECTED,
            description=(
                "Paid and organic acquisition, campaign spend, "
                "attribution and customer acquisition economics."
            ),
            coverage_pct=0,
            records_available=0,
            last_sync="Not connected",
            capabilities=[
                IntelligenceCapability.CHANNEL_ECONOMICS,
                IntelligenceCapability.CAC_INTELLIGENCE,
            ],
            available_fields=[],
            missing_fields=[
                "campaign",
                "channel",
                "spend",
                "lead_id",
                "attributed_sale",
                "customer_acquisition_cost",
            ],
        ),
        IntegrationSource(
            source_id="customer_voice",
            name="Customer Voice",
            category=IntegrationCategory.CUSTOMER,
            status=IntegrationStatus.NOT_CONNECTED,
            description=(
                "Support conversations, NPS, reviews, call transcripts "
                "and customer experience signals."
            ),
            coverage_pct=0,
            records_available=0,
            last_sync="Not connected",
            capabilities=[
                IntelligenceCapability.CUSTOMER_VOICE,
                IntelligenceCapability.EXPERIENCE_RISK,
            ],
            available_fields=[],
            missing_fields=[
                "customer_id",
                "vehicle_id",
                "nps",
                "review_text",
                "support_category",
                "call_transcript",
            ],
        ),
    ]


def _all_capabilities() -> Set[IntelligenceCapability]:
    return set(IntelligenceCapability)


def calculate_intelligence_coverage(
    sources: List[IntegrationSource],
) -> IntelligenceCoverage:
    """
    Calculate intelligence coverage from the currently available
    system connections.

    A capability is unlocked when at least one active source
    exposes it.
    """

    category_scores: Dict[IntegrationCategory, float] = {}

    for category in IntegrationCategory:
        category_sources = [
            source
            for source in sources
            if source.category == category
        ]

        if not category_sources:
            category_scores[category] = 0.0
            continue

        category_scores[category] = round(
            sum(
                source.coverage_pct
                for source in category_sources
            )
            / len(category_sources),
            1,
        )

    active_sources = [
        source
        for source in sources
        if source.status
        in {
            IntegrationStatus.CONNECTED,
            IntegrationStatus.SIMULATED,
        }
    ]

    unlocked: Set[IntelligenceCapability] = set()

    for source in active_sources:
        if source.coverage_pct <= 0:
            continue

        unlocked.update(source.capabilities)

    locked = _all_capabilities() - unlocked

    overall_score = round(
        sum(category_scores.values())
        / len(IntegrationCategory),
        1,
    )

    disconnected_sources = sorted(
        [
            source
            for source in sources
            if source.status
            in {
                IntegrationStatus.NOT_CONNECTED,
                IntegrationStatus.READY,
            }
        ],
        key=lambda source: len(source.capabilities),
        reverse=True,
    )

    if disconnected_sources:
        next_source = disconnected_sources[0]

        recommended_next_connection = next_source.name

        capability_names = ", ".join(
            capability.value.replace("_", " ").title()
            for capability in next_source.capabilities
        )

        recommendation_reason = (
            "Connecting this source would unlock "
            f"{capability_names}."
        )

    else:
        recommended_next_connection = (
            "Improve existing data coverage"
        )

        recommendation_reason = (
            "All major source categories are connected. "
            "Improve field completeness and data quality next."
        )

    return IntelligenceCoverage(
        overall_score=overall_score,
        category_scores=category_scores,
        unlocked_capabilities=sorted(
            unlocked,
            key=lambda capability: capability.value,
        ),
        locked_capabilities=sorted(
            locked,
            key=lambda capability: capability.value,
        ),
        recommended_next_connection=(
            recommended_next_connection
        ),
        recommendation_reason=recommendation_reason,
    )


def get_intelligence_coverage() -> IntelligenceCoverage:
    """
    Convenience function used by the application layer.
    """

    return calculate_intelligence_coverage(
        get_integration_sources()
    )
