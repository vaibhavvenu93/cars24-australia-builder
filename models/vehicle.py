from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AcquisitionSource(str, Enum):
    DIRECT_SELLER = "DIRECT_SELLER"
    AUCTION = "AUCTION"
    DEALER = "DEALER"
    WHOLESALE = "WHOLESALE"
    TRADE_IN = "TRADE_IN"


class VehicleLocation(str, Enum):
    MELBOURNE = "MELBOURNE"
    SYDNEY = "SYDNEY"
    BRISBANE = "BRISBANE"
    PERTH = "PERTH"
    ADELAIDE = "ADELAIDE"


class VehicleStatus(str, Enum):
    EVALUATION = "EVALUATION"
    ACQUIRED = "ACQUIRED"
    INSPECTION = "INSPECTION"
    REFURBISHMENT = "REFURBISHMENT"
    READY_TO_LIST = "READY_TO_LIST"
    LISTED = "LISTED"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    RETURNED = "RETURNED"
    WHOLESALE = "WHOLESALE"


class ConditionGrade(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"


class DemandLevel(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class VehicleIdentity(BaseModel):
    vehicle_id: str

    make: str
    model: str
    variant: Optional[str] = None

    year: int = Field(ge=1990, le=2030)
    kilometres: int = Field(ge=0)

    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    body_type: Optional[str] = None


class Acquisition(BaseModel):
    source: AcquisitionSource

    initial_valuation: float = Field(ge=0)
    acquisition_price: float = Field(ge=0)

    valuation_date: Optional[date] = None
    acquisition_date: Optional[date] = None

    seller_region: Optional[str] = None

    transport_to_hub_cost: float = Field(default=0, ge=0)


class Condition(BaseModel):
    grade: ConditionGrade

    inspection_score: float = Field(ge=0, le=100)

    mechanical_risk: RiskLevel
    cosmetic_risk: RiskLevel

    service_history_complete: bool = False
    ppsr_clear: bool = True

    inspection_notes: list[str] = Field(default_factory=list)


class Refurbishment(BaseModel):
    estimated_cost: float = Field(default=0, ge=0)
    actual_cost: Optional[float] = Field(default=None, ge=0)

    estimated_hours: float = Field(default=0, ge=0)
    actual_hours: Optional[float] = Field(default=None, ge=0)

    expected_price_uplift: float = Field(default=0, ge=0)

    safety_work_required: bool = False
    cosmetic_work_required: bool = False

    rework_required: bool = False


class Pricing(BaseModel):
    expected_market_price: float = Field(ge=0)

    initial_list_price: Optional[float] = Field(default=None, ge=0)
    current_list_price: Optional[float] = Field(default=None, ge=0)
    final_sale_price: Optional[float] = Field(default=None, ge=0)

    competitor_median_price: Optional[float] = Field(default=None, ge=0)

    price_changes: int = Field(default=0, ge=0)


class DemandSignals(BaseModel):
    level: DemandLevel

    listing_views_7d: int = Field(default=0, ge=0)
    enquiries_7d: int = Field(default=0, ge=0)
    test_drives_7d: int = Field(default=0, ge=0)

    local_inventory_count: int = Field(default=0, ge=0)

    estimated_days_to_sale: int = Field(default=30, ge=1)


class Inventory(BaseModel):
    current_location: VehicleLocation

    listed_date: Optional[date] = None

    days_in_inventory: int = Field(default=0, ge=0)
    days_since_acquisition: int = Field(default=0, ge=0)

    storage_cost_per_day: float = Field(default=0, ge=0)


class LifecycleRisk(BaseModel):
    warranty_probability: float = Field(
        default=0.05,
        ge=0,
        le=1,
    )

    expected_warranty_cost: float = Field(default=0, ge=0)

    return_probability: float = Field(
        default=0.03,
        ge=0,
        le=1,
    )

    expected_return_cost: float = Field(default=0, ge=0)

    markdown_probability: float = Field(
        default=0.10,
        ge=0,
        le=1,
    )

    expected_markdown_cost: float = Field(default=0, ge=0)


class Vehicle(BaseModel):
    identity: VehicleIdentity

    status: VehicleStatus

    acquisition: Acquisition
    condition: Condition
    refurbishment: Refurbishment
    pricing: Pricing
    demand: DemandSignals
    inventory: Inventory
    lifecycle_risk: LifecycleRisk

    notes: list[str] = Field(default_factory=list)
