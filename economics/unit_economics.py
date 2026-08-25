from __future__ import annotations

from dataclasses import dataclass

from models.vehicle import Vehicle


@dataclass
class UnitEconomics:
    invested_capital: float
    expected_risk_cost: float
    expected_lifecycle_cost: float
    expected_sale_price: float
    expected_contribution: float
    contribution_margin_pct: float
    capital_days: int
    annualised_inventory_turns: float
    contribution_per_capital_day: float
    refurbishment_roi: float


def calculate_invested_capital(vehicle: Vehicle) -> float:
    """
    Capital deployed before the vehicle is sold.

    Includes:
    - acquisition price
    - transport to hub
    - refurbishment cost
    - accumulated storage cost
    """
    refurbishment_cost = (
        vehicle.refurbishment.actual_cost
        if vehicle.refurbishment.actual_cost is not None
        else vehicle.refurbishment.estimated_cost
    )

    storage_cost = (
        vehicle.inventory.days_since_acquisition
        * vehicle.inventory.storage_cost_per_day
    )

    return (
        vehicle.acquisition.acquisition_price
        + vehicle.acquisition.transport_to_hub_cost
        + refurbishment_cost
        + storage_cost
    )


def calculate_expected_risk_cost(vehicle: Vehicle) -> float:
    """
    Expected lifecycle cost arising from probabilistic risks.

    Rather than assuming every vehicle will generate a warranty,
    return, or markdown event, this calculates the expected value
    of those risks.
    """
    warranty_risk = (
        vehicle.lifecycle_risk.warranty_probability
        * vehicle.lifecycle_risk.expected_warranty_cost
    )

    return_risk = (
        vehicle.lifecycle_risk.return_probability
        * vehicle.lifecycle_risk.expected_return_cost
    )

    markdown_risk = (
        vehicle.lifecycle_risk.markdown_probability
        * vehicle.lifecycle_risk.expected_markdown_cost
    )

    return warranty_risk + return_risk + markdown_risk


def calculate_expected_sale_price(vehicle: Vehicle) -> float:
    """
    Determine the best available expected sale-price signal.

    Priority:
    1. final sale price
    2. current list price
    3. initial list price
    4. expected market price
    """
    pricing = vehicle.pricing

    if pricing.final_sale_price is not None:
        return pricing.final_sale_price

    if pricing.current_list_price is not None:
        return pricing.current_list_price

    if pricing.initial_list_price is not None:
        return pricing.initial_list_price

    return pricing.expected_market_price


def calculate_refurbishment_roi(vehicle: Vehicle) -> float:
    """
    Estimate the return on refurbishment spend.

    This intentionally uses expected price uplift rather than
    pretending that all refurbishment creates equivalent value.

    Example:
        $500 refurbishment
        $1,000 expected price uplift
        ROI = 1.0 (100%)
    """
    refurbishment_cost = (
        vehicle.refurbishment.actual_cost
        if vehicle.refurbishment.actual_cost is not None
        else vehicle.refurbishment.estimated_cost
    )

    if refurbishment_cost == 0:
        return 0.0

    return (
        vehicle.refurbishment.expected_price_uplift
        - refurbishment_cost
    ) / refurbishment_cost


def calculate_unit_economics(vehicle: Vehicle) -> UnitEconomics:
    """
    Calculate vehicle-level lifecycle economics.

    The purpose is not to model CARS24's actual accounting.

    This is a synthetic decision framework designed to compare
    vehicles and alternative actions consistently.
    """

    invested_capital = calculate_invested_capital(vehicle)

    expected_risk_cost = calculate_expected_risk_cost(vehicle)

    expected_sale_price = calculate_expected_sale_price(vehicle)

    expected_lifecycle_cost = invested_capital + expected_risk_cost

    expected_contribution = (
        expected_sale_price - expected_lifecycle_cost
    )

    if expected_sale_price > 0:
        contribution_margin_pct = (
            expected_contribution / expected_sale_price
        ) * 100
    else:
        contribution_margin_pct = 0.0

    capital_days = max(
        vehicle.inventory.days_since_acquisition,
        1,
    )

    annualised_inventory_turns = 365 / capital_days

    if invested_capital > 0:
        contribution_per_capital_day = (
            expected_contribution
            / invested_capital
            / capital_days
        )
    else:
        contribution_per_capital_day = 0.0

    refurbishment_roi = calculate_refurbishment_roi(vehicle)

    return UnitEconomics(
        invested_capital=round(invested_capital, 2),
        expected_risk_cost=round(expected_risk_cost, 2),
        expected_lifecycle_cost=round(
            expected_lifecycle_cost,
            2,
        ),
        expected_sale_price=round(expected_sale_price, 2),
        expected_contribution=round(
            expected_contribution,
            2,
        ),
        contribution_margin_pct=round(
            contribution_margin_pct,
            2,
        ),
        capital_days=capital_days,
        annualised_inventory_turns=round(
            annualised_inventory_turns,
            2,
        ),
        contribution_per_capital_day=round(
            contribution_per_capital_day,
            8,
        ),
        refurbishment_roi=round(
            refurbishment_roi,
            4,
        ),
    )
