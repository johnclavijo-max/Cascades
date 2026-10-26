"""Pure-Python tool to calculate landed cost delta and margin exposure.

This tool performs in-process calculations using cost breakdown and pricing
data retrieved from Ariba. No external API calls are made.
"""
import json
import logging
from typing import Any, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MarginImpactInput(BaseModel):
    cost_breakdown_data: str = Field(
        description=(
            "JSON string of cost breakdown records per order. Each record must include: "
            "order_id, unit_price, current_duty_amount, freight_charges, other_charges, quantity."
        )
    )
    pricing_data: str = Field(
        description=(
            "JSON string of pricing records per material. Each record must include: "
            "material_id, selling_price."
        )
    )
    duty_rate_delta_pct: float = Field(
        description=(
            "Duty rate change in percentage points (e.g. 25.0 for a 25 percentage point increase). "
            "Must be user-confirmed before passing to this tool."
        )
    )
    include_freight_surcharge: bool = Field(
        default=False,
        description="If True, also apply the duty_rate_delta_pct to freight charges as a surcharge.",
    )


def _calculate_margin_impact(
    cost_breakdown_data: str,
    pricing_data: str,
    duty_rate_delta_pct: float,
    include_freight_surcharge: bool = False,
) -> str:
    """Calculate landed cost delta and margin exposure across affected orders."""
    try:
        cost_records: list[dict[str, Any]] = json.loads(cost_breakdown_data)
        price_records: list[dict[str, Any]] = json.loads(pricing_data)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    price_map: dict[str, float] = {
        r["material_id"]: float(r.get("selling_price", 0)) for r in price_records
    }

    results = []
    incomplete_orders = []
    total_current_lc = 0.0
    total_new_lc = 0.0
    total_margin_delta = 0.0

    for rec in cost_records:
        order_id = rec.get("order_id", "UNKNOWN")

        # Check required fields
        required = ["unit_price", "current_duty_amount", "freight_charges", "quantity"]
        missing = [f for f in required if rec.get(f) is None]

        if missing:
            incomplete_orders.append({"order_id": order_id, "missing_fields": missing})
            continue

        unit_price = float(rec["unit_price"])
        current_duty = float(rec["current_duty_amount"])
        freight = float(rec["freight_charges"])
        other = float(rec.get("other_charges", 0))
        qty = float(rec["quantity"])
        material_id = rec.get("material_id", "")

        current_lc_per_unit = unit_price + current_duty + freight + other
        duty_delta = unit_price * (duty_rate_delta_pct / 100.0)
        freight_delta = (freight * (duty_rate_delta_pct / 100.0)) if include_freight_surcharge else 0.0
        new_lc_per_unit = current_lc_per_unit + duty_delta + freight_delta

        selling_price = price_map.get(material_id, 0.0)
        current_margin = (selling_price - current_lc_per_unit) * qty if selling_price else None
        new_margin = (selling_price - new_lc_per_unit) * qty if selling_price else None
        margin_delta = (new_margin - current_margin) if (current_margin is not None and new_margin is not None) else None

        order_result: dict[str, Any] = {
            "order_id": order_id,
            "material_id": material_id,
            "quantity": qty,
            "current_landed_cost_per_unit": round(current_lc_per_unit, 2),
            "new_landed_cost_per_unit": round(new_lc_per_unit, 2),
            "landed_cost_delta_per_unit": round(new_lc_per_unit - current_lc_per_unit, 2),
            "total_landed_cost_delta": round((new_lc_per_unit - current_lc_per_unit) * qty, 2),
            "data_complete": True,
        }
        if margin_delta is not None:
            order_result["margin_delta"] = round(margin_delta, 2)
            order_result["current_margin"] = round(current_margin, 2)  # type: ignore[arg-type]
            order_result["new_margin"] = round(new_margin, 2)  # type: ignore[arg-type]

        total_current_lc += current_lc_per_unit * qty
        total_new_lc += new_lc_per_unit * qty
        if margin_delta is not None:
            total_margin_delta += margin_delta

        results.append(order_result)

    summary = {
        "orders": results,
        "incomplete_orders": incomplete_orders,
        "portfolio_summary": {
            "orders_with_full_data": len(results),
            "orders_with_incomplete_data": len(incomplete_orders),
            "total_current_landed_cost": round(total_current_lc, 2),
            "total_new_landed_cost": round(total_new_lc, 2),
            "total_landed_cost_delta": round(total_new_lc - total_current_lc, 2),
            "total_margin_delta": round(total_margin_delta, 2),
            "duty_rate_delta_applied_pct": duty_rate_delta_pct,
            "freight_surcharge_included": include_freight_surcharge,
        },
    }

    logger.info(
        "[M2] Margin impact calculated: %d orders full data, %d incomplete",
        len(results),
        len(incomplete_orders),
    )
    return json.dumps(summary, indent=2)


def get_margin_impact_calculator_tool() -> StructuredTool:
    return StructuredTool(
        name="margin_impact_calculator",
        description=(
            "Calculates landed cost delta and margin exposure across affected purchase orders. "
            "Requires cost breakdown data and pricing data retrieved from Ariba, plus a "
            "user-confirmed duty rate delta in percentage points. Returns per-order impact "
            "and portfolio-level exposure summary. Flags orders with incomplete cost data."
        ),
        args_schema=MarginImpactInput,
        func=_calculate_margin_impact,
    )
