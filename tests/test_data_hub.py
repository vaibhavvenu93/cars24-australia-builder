from engines.data_hub import (
    detect_dataset,
    map_columns,
    normalize_column_name,
)
from data.integrations import (
    calculate_intelligence_coverage,
    get_integration_sources,
)
from models.integration import (
    IntelligenceCapability,
    IntegrationCategory,
)


def test_column_names_are_normalized():
    assert (
        normalize_column_name("Purchase Price ($)")
        == "purchase_price"
    )

    assert (
        normalize_column_name("Days In Stock")
        == "days_in_stock"
    )


def test_inventory_dataset_is_detected():
    columns = [
        "Stock ID",
        "VIN",
        "Make",
        "Model",
        "Year",
        "Yard",
        "Purchase Date",
        "Purchase Price",
        "Retail Price",
        "Days In Stock",
        "Vehicle Status",
    ]

    detection = detect_dataset(columns)

    assert (
        detection.category
        == IntegrationCategory.INVENTORY
    )

    assert detection.confidence >= 90

    assert (
        "vehicle_id"
        in detection.matched_fields
    )

    assert (
        "inventory_age_days"
        in detection.matched_fields
    )

    assert (
        IntelligenceCapability.INVENTORY_AGEING
        in detection.unlocked_capabilities
    )


def test_crm_dataset_is_detected():
    columns = [
        "Lead ID",
        "Stock ID",
        "Lead Source",
        "Branch",
        "Enquiry Date",
        "Test Drive Date",
        "Offer Date",
        "Sale Date",
        "Pipeline Stage",
        "Lost Reason",
        "First Response Seconds",
    ]

    detection = detect_dataset(columns)

    assert (
        detection.category
        == IntegrationCategory.CRM
    )

    assert detection.confidence >= 90

    assert (
        IntelligenceCapability.FUNNEL_ANALYTICS
        in detection.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.LEAD_CONVERSION
        in detection.unlocked_capabilities
    )


def test_finance_dataset_is_detected():
    columns = [
        "Vehicle ID",
        "Purchase Cost",
        "Reconditioning Cost",
        "Transport Cost",
        "Holding Cost",
        "Selling Price",
        "Gross Profit",
        "Warranty Margin",
        "Finance Margin",
    ]

    detection = detect_dataset(columns)

    assert (
        detection.category
        == IntegrationCategory.FINANCE
    )

    assert detection.confidence >= 90

    assert (
        IntelligenceCapability.TRUE_MARGIN
        in detection.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.CASH_CYCLE
        in detection.unlocked_capabilities
    )


def test_reconditioning_dataset_is_detected():
    columns = [
        "Work Order ID",
        "Stock ID",
        "Workshop",
        "Estimated Cost",
        "Invoice Cost",
        "Job Start",
        "Job End",
        "Rework",
        "Issue Type",
        "Parts Delay Days",
    ]

    detection = detect_dataset(columns)

    assert (
        detection.category
        == IntegrationCategory.RECONDITIONING
    )

    assert detection.confidence >= 90

    assert (
        IntelligenceCapability.RECON_BOTTLENECKS
        in detection.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.VENDOR_ECONOMICS
        in detection.unlocked_capabilities
    )


def test_aliases_map_to_canonical_fields():
    mapping = map_columns(
        columns=[
            "Stock ID",
            "Yard",
            "Buy Price",
            "Days Stock",
        ],
        category=IntegrationCategory.INVENTORY,
    )

    assert mapping["Stock ID"] == "vehicle_id"
    assert mapping["Yard"] == "location"

    assert (
        mapping["Buy Price"]
        == "acquisition_price"
    )

    assert (
        mapping["Days Stock"]
        == "inventory_age_days"
    )


def test_system_registry_contains_major_sources():
    sources = get_integration_sources()

    categories = {
        source.category
        for source in sources
    }

    assert (
        IntegrationCategory.INVENTORY
        in categories
    )

    assert (
        IntegrationCategory.CRM
        in categories
    )

    assert (
        IntegrationCategory.FINANCE
        in categories
    )

    assert (
        IntegrationCategory.RECONDITIONING
        in categories
    )

    assert (
        IntegrationCategory.LOGISTICS
        in categories
    )

    assert (
        IntegrationCategory.MARKET_DATA
        in categories
    )


def test_intelligence_coverage_changes_with_connections():
    sources = get_integration_sources()

    coverage = calculate_intelligence_coverage(
        sources
    )

    assert coverage.overall_score > 0

    assert (
        IntelligenceCapability.VEHICLE_ECONOMICS
        in coverage.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.FUNNEL_ANALYTICS
        in coverage.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.MARKET_ARBITRAGE
        in coverage.unlocked_capabilities
    )

    assert (
        IntelligenceCapability.CUSTOMER_VOICE
        in coverage.locked_capabilities
    )

    assert (
        IntelligenceCapability.CAC_INTELLIGENCE
        in coverage.locked_capabilities
    )


def test_registry_recommends_next_connection():
    sources = get_integration_sources()

    coverage = calculate_intelligence_coverage(
        sources
    )

    assert (
        coverage.recommended_next_connection
        in {
            "Marketing & Attribution",
            "Customer Voice",
        }
    )

    assert coverage.recommendation_reason
