from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class IntegrationCategory(str, Enum):
    CRM = "CRM"
    INVENTORY = "INVENTORY"
    FINANCE = "FINANCE"
    RECONDITIONING = "RECONDITIONING"
    LOGISTICS = "LOGISTICS"
    MARKETING = "MARKETING"
    CUSTOMER = "CUSTOMER"
    MARKET_DATA = "MARKET_DATA"


class IntegrationStatus(str, Enum):
    CONNECTED = "CONNECTED"
    SIMULATED = "SIMULATED"
    READY = "READY"
    NOT_CONNECTED = "NOT_CONNECTED"


class IntelligenceCapability(str, Enum):
    VEHICLE_ECONOMICS = "VEHICLE_ECONOMICS"
    INVENTORY_AGEING = "INVENTORY_AGEING"
    CAPITAL_EFFICIENCY = "CAPITAL_EFFICIENCY"

    DEMAND_INTELLIGENCE = "DEMAND_INTELLIGENCE"
    FUNNEL_ANALYTICS = "FUNNEL_ANALYTICS"
    LEAD_CONVERSION = "LEAD_CONVERSION"

    TRUE_MARGIN = "TRUE_MARGIN"
    CASH_CYCLE = "CASH_CYCLE"

    RECON_BOTTLENECKS = "RECON_BOTTLENECKS"
    VENDOR_ECONOMICS = "VENDOR_ECONOMICS"

    TRANSFER_INTELLIGENCE = "TRANSFER_INTELLIGENCE"
    LOGISTICS_EFFICIENCY = "LOGISTICS_EFFICIENCY"

    CHANNEL_ECONOMICS = "CHANNEL_ECONOMICS"
    CAC_INTELLIGENCE = "CAC_INTELLIGENCE"

    CUSTOMER_VOICE = "CUSTOMER_VOICE"
    EXPERIENCE_RISK = "EXPERIENCE_RISK"

    MARKET_ARBITRAGE = "MARKET_ARBITRAGE"
    ACQUISITION_OPPORTUNITY = "ACQUISITION_OPPORTUNITY"


class IntegrationSource(BaseModel):
    source_id: str
    name: str

    category: IntegrationCategory
    status: IntegrationStatus

    description: str

    coverage_pct: float = Field(
        ge=0,
        le=100,
    )

    records_available: int = Field(
        default=0,
        ge=0,
    )

    last_sync: str

    capabilities: List[
        IntelligenceCapability
    ] = Field(
        default_factory=list,
    )

    available_fields: List[str] = Field(
        default_factory=list,
    )

    missing_fields: List[str] = Field(
        default_factory=list,
    )


class IntelligenceCoverage(BaseModel):
    overall_score: float = Field(
        ge=0,
        le=100,
    )

    category_scores: Dict[
        IntegrationCategory,
        float,
    ]

    unlocked_capabilities: List[
        IntelligenceCapability
    ]

    locked_capabilities: List[
        IntelligenceCapability
    ]

    recommended_next_connection: str

    recommendation_reason: str
