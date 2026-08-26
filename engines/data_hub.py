from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from models.integration import (
    IntelligenceCapability,
    IntegrationCategory,
)


@dataclass
class DatasetDetection:
    category: IntegrationCategory
    confidence: float
    matched_fields: List[str]
    missing_fields: List[str]
    column_mapping: Dict[str, str]
    unlocked_capabilities: List[IntelligenceCapability]


FIELD_ALIASES: Dict[IntegrationCategory, Dict[str, List[str]]] = {
    IntegrationCategory.INVENTORY: {
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
            "stockid",
            "inventory_id",
            "car_id",
            "unit_id",
        ],
        "vin": [
            "vin",
            "vehicle_identification_number",
        ],
        "make": [
            "make",
            "brand",
            "manufacturer",
        ],
        "model": [
            "model",
            "vehicle_model",
        ],
        "year": [
            "year",
            "model_year",
            "manufacture_year",
        ],
        "location": [
            "location",
            "yard",
            "branch",
            "site",
            "city",
            "hub",
        ],
        "acquisition_date": [
            "acquisition_date",
            "purchase_date",
            "bought_date",
            "intake_date",
        ],
        "acquisition_price": [
            "acquisition_price",
            "purchase_price",
            "buy_price",
            "cost_price",
        ],
        "listing_price": [
            "listing_price",
            "asking_price",
            "retail_price",
            "current_price",
        ],
        "inventory_age_days": [
            "inventory_age_days",
            "days_stock",
            "days_in_stock",
            "stock_age",
            "age_days",
            "days_inventory",
        ],
        "status": [
            "status",
            "vehicle_status",
            "inventory_status",
            "listing_status",
        ],
    },
    IntegrationCategory.CRM: {
        "lead_id": [
            "lead_id",
            "leadid",
            "enquiry_id",
            "enquiryid",
            "customer_lead_id",
        ],
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
            "car_id",
        ],
        "source": [
            "source",
            "lead_source",
            "channel",
            "acquisition_source",
        ],
        "location": [
            "location",
            "branch",
            "site",
            "city",
        ],
        "enquiry_date": [
            "enquiry_date",
            "inquiry_date",
            "lead_date",
            "created_date",
        ],
        "test_drive_date": [
            "test_drive_date",
            "testdrive_date",
            "demo_date",
        ],
        "offer_date": [
            "offer_date",
            "quote_date",
            "proposal_date",
        ],
        "sale_date": [
            "sale_date",
            "sold_date",
            "conversion_date",
            "close_date",
        ],
        "lead_status": [
            "lead_status",
            "status",
            "stage",
            "pipeline_stage",
        ],
        "lost_reason": [
            "lost_reason",
            "loss_reason",
            "closed_lost_reason",
        ],
        "response_time_seconds": [
            "response_time_seconds",
            "response_seconds",
            "first_response_seconds",
        ],
    },
    IntegrationCategory.FINANCE: {
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
            "car_id",
        ],
        "acquisition_cost": [
            "acquisition_cost",
            "purchase_cost",
            "buy_cost",
            "purchase_price",
        ],
        "recon_cost": [
            "recon_cost",
            "reconditioning_cost",
            "refurb_cost",
            "repair_cost",
        ],
        "logistics_cost": [
            "logistics_cost",
            "transport_cost",
            "freight_cost",
            "transfer_cost",
        ],
        "holding_cost": [
            "holding_cost",
            "inventory_holding_cost",
            "carrying_cost",
        ],
        "sale_price": [
            "sale_price",
            "sold_price",
            "revenue",
            "selling_price",
        ],
        "gross_profit": [
            "gross_profit",
            "gross_margin_value",
            "contribution",
            "vehicle_profit",
        ],
        "warranty_contribution": [
            "warranty_contribution",
            "warranty_margin",
            "warranty_profit",
        ],
        "finance_contribution": [
            "finance_contribution",
            "finance_margin",
            "finance_profit",
        ],
    },
    IntegrationCategory.RECONDITIONING: {
        "job_id": [
            "job_id",
            "recon_job_id",
            "work_order_id",
            "repair_id",
        ],
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
            "car_id",
        ],
        "vendor": [
            "vendor",
            "supplier",
            "workshop",
            "repairer",
        ],
        "quoted_cost": [
            "quoted_cost",
            "quote",
            "estimated_cost",
        ],
        "actual_cost": [
            "actual_cost",
            "final_cost",
            "invoice_cost",
        ],
        "start_date": [
            "start_date",
            "job_start",
            "recon_start",
        ],
        "completion_date": [
            "completion_date",
            "completed_date",
            "job_end",
            "recon_end",
        ],
        "rework_required": [
            "rework_required",
            "rework",
            "repeat_repair",
        ],
        "defect_category": [
            "defect_category",
            "repair_category",
            "issue_type",
        ],
        "parts_delay": [
            "parts_delay",
            "parts_delay_days",
        ],
    },
    IntegrationCategory.LOGISTICS: {
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
            "car_id",
        ],
        "origin": [
            "origin",
            "from_location",
            "source_location",
        ],
        "destination": [
            "destination",
            "to_location",
            "target_location",
        ],
        "transfer_cost": [
            "transfer_cost",
            "transport_cost",
            "freight_cost",
        ],
        "dispatch_date": [
            "dispatch_date",
            "shipped_date",
            "departure_date",
        ],
        "arrival_date": [
            "arrival_date",
            "received_date",
            "delivery_date",
        ],
        "carrier": [
            "carrier",
            "transporter",
            "logistics_vendor",
        ],
        "delay_reason": [
            "delay_reason",
            "late_reason",
        ],
    },
    IntegrationCategory.MARKETING: {
        "campaign": [
            "campaign",
            "campaign_name",
        ],
        "channel": [
            "channel",
            "source",
            "marketing_channel",
        ],
        "spend": [
            "spend",
            "cost",
            "ad_spend",
            "marketing_spend",
        ],
        "lead_id": [
            "lead_id",
            "leadid",
            "enquiry_id",
        ],
        "attributed_sale": [
            "attributed_sale",
            "conversion",
            "sale",
        ],
        "customer_acquisition_cost": [
            "customer_acquisition_cost",
            "cac",
            "acquisition_cost",
        ],
    },
    IntegrationCategory.CUSTOMER: {
        "customer_id": [
            "customer_id",
            "customerid",
            "user_id",
        ],
        "vehicle_id": [
            "vehicle_id",
            "vehicleid",
            "stock_id",
        ],
        "nps": [
            "nps",
            "nps_score",
        ],
        "review_text": [
            "review_text",
            "review",
            "feedback",
            "comment",
        ],
        "support_category": [
            "support_category",
            "ticket_category",
            "issue_category",
        ],
        "call_transcript": [
            "call_transcript",
            "transcript",
            "call_notes",
        ],
    },
    IntegrationCategory.MARKET_DATA: {
        "make": [
            "make",
            "brand",
        ],
        "model": [
            "model",
            "vehicle_model",
        ],
        "year": [
            "year",
            "model_year",
        ],
        "location": [
            "location",
            "city",
            "market",
            "region",
        ],
        "market_price": [
            "market_price",
            "median_price",
            "benchmark_price",
        ],
        "market_supply": [
            "market_supply",
            "supply",
            "available_units",
        ],
        "demand_index": [
            "demand_index",
            "demand_score",
            "search_demand",
        ],
        "median_days_to_sale": [
            "median_days_to_sale",
            "days_to_sale",
            "market_days",
        ],
    },
}


CATEGORY_CAPABILITIES: Dict[
    IntegrationCategory,
    List[IntelligenceCapability],
] = {
    IntegrationCategory.INVENTORY: [
        IntelligenceCapability.VEHICLE_ECONOMICS,
        IntelligenceCapability.INVENTORY_AGEING,
        IntelligenceCapability.CAPITAL_EFFICIENCY,
    ],
    IntegrationCategory.CRM: [
        IntelligenceCapability.DEMAND_INTELLIGENCE,
        IntelligenceCapability.FUNNEL_ANALYTICS,
        IntelligenceCapability.LEAD_CONVERSION,
    ],
    IntegrationCategory.FINANCE: [
        IntelligenceCapability.TRUE_MARGIN,
        IntelligenceCapability.CASH_CYCLE,
        IntelligenceCapability.VEHICLE_ECONOMICS,
        IntelligenceCapability.CAPITAL_EFFICIENCY,
    ],
    IntegrationCategory.RECONDITIONING: [
        IntelligenceCapability.RECON_BOTTLENECKS,
        IntelligenceCapability.VENDOR_ECONOMICS,
    ],
    IntegrationCategory.LOGISTICS: [
        IntelligenceCapability.TRANSFER_INTELLIGENCE,
        IntelligenceCapability.LOGISTICS_EFFICIENCY,
    ],
    IntegrationCategory.MARKETING: [
        IntelligenceCapability.CHANNEL_ECONOMICS,
        IntelligenceCapability.CAC_INTELLIGENCE,
    ],
    IntegrationCategory.CUSTOMER: [
        IntelligenceCapability.CUSTOMER_VOICE,
        IntelligenceCapability.EXPERIENCE_RISK,
    ],
    IntegrationCategory.MARKET_DATA: [
        IntelligenceCapability.MARKET_ARBITRAGE,
        IntelligenceCapability.ACQUISITION_OPPORTUNITY,
        IntelligenceCapability.DEMAND_INTELLIGENCE,
    ],
}


def normalize_column_name(column: str) -> str:
    """
    Convert a source column into a predictable snake_case form.
    """

    normalized = column.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    normalized = normalized.strip("_")

    return normalized


def _build_alias_lookup(
    category: IntegrationCategory,
) -> Dict[str, str]:
    """
    Build alias -> canonical field lookup for one category.
    """

    lookup: Dict[str, str] = {}

    for canonical, aliases in FIELD_ALIASES[category].items():
        lookup[normalize_column_name(canonical)] = canonical

        for alias in aliases:
            lookup[normalize_column_name(alias)] = canonical

    return lookup


def map_columns(
    columns: List[str],
    category: IntegrationCategory,
) -> Dict[str, str]:
    """
    Map source columns to canonical CARS24 OS fields.

    Return format:
        {
            "source column": "canonical_field"
        }
    """

    alias_lookup = _build_alias_lookup(category)

    mapping: Dict[str, str] = {}

    for column in columns:
        normalized = normalize_column_name(column)

        if normalized in alias_lookup:
            mapping[column] = alias_lookup[normalized]

    return mapping


def _category_score(
    columns: List[str],
    category: IntegrationCategory,
) -> Tuple[float, Dict[str, str]]:
    mapping = map_columns(
        columns=columns,
        category=category,
    )

    expected_fields = set(
        FIELD_ALIASES[category].keys()
    )

    matched_fields = set(mapping.values())

    if not expected_fields:
        return 0.0, mapping

    coverage = (
        len(matched_fields)
        / len(expected_fields)
    )

    # Reward datasets with several independently matched fields.
    evidence_bonus = min(
        len(matched_fields) / 5,
        1.0,
    )

    score = (
        coverage * 0.75
        + evidence_bonus * 0.25
    )

    return round(score * 100, 1), mapping


def detect_dataset(
    columns: List[str],
) -> DatasetDetection:
    """
    Infer the most likely operational dataset from its columns.

    Detection is deterministic and explainable.
    """

    if not columns:
        raise ValueError(
            "Dataset must contain at least one column."
        )

    scores: List[
        Tuple[
            IntegrationCategory,
            float,
            Dict[str, str],
        ]
    ] = []

    for category in IntegrationCategory:
        score, mapping = _category_score(
            columns=columns,
            category=category,
        )

        scores.append(
            (
                category,
                score,
                mapping,
            )
        )

    scores.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    category, confidence, mapping = scores[0]

    matched_fields: Set[str] = set(
        mapping.values()
    )

    expected_fields: Set[str] = set(
        FIELD_ALIASES[category].keys()
    )

    missing_fields = sorted(
        expected_fields - matched_fields
    )

    return DatasetDetection(
        category=category,
        confidence=confidence,
        matched_fields=sorted(
            matched_fields
        ),
        missing_fields=missing_fields,
        column_mapping=mapping,
        unlocked_capabilities=(
            CATEGORY_CAPABILITIES[category]
        ),
    )


def describe_detection(
    detection: DatasetDetection,
) -> str:
    """
    Human-readable explanation for the Data Hub UI.
    """

    category_name = (
        detection.category.value
        .replace("_", " ")
        .title()
    )

    capabilities = ", ".join(
        capability.value
        .replace("_", " ")
        .title()
        for capability
        in detection.unlocked_capabilities
    )

    return (
        f"This looks like {category_name} data "
        f"with {detection.confidence:.0f}% confidence. "
        f"{len(detection.matched_fields)} canonical fields "
        f"were mapped. Connecting it can unlock "
        f"{capabilities}."
    )


def get_supported_dataset_types() -> List[str]:
    """
    Dataset categories supported by the current prototype.
    """

    return [
        category.value
        for category in IntegrationCategory
    ]
