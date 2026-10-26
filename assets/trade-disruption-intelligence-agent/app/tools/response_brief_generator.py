"""Pure-Python tool to generate a cross-team response brief.

Takes impact assessment and supplier risk output and produces a structured
action brief with prioritised recommendations per team.
No external API calls are made.
"""
import json
import logging
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_ACTION_TYPES = ("re-route", "re-source", "reprice", "expedite")
_TEAMS = ("procurement", "supply_chain", "finance")


class ResponseBriefInput(BaseModel):
    impact_assessment_json: str = Field(
        description=(
            "JSON string from margin_impact_calculator containing orders and portfolio_summary. "
            "Used to derive recommended actions."
        )
    )
    supplier_risk_json: Optional[str] = Field(
        default=None,
        description=(
            "Optional JSON string of supplier risk results from supplier_risk_exposure tool. "
            "Used to enrich re-source recommendations."
        ),
    )
    tariff_event_description: str = Field(
        description="Brief description of the tariff event triggering this response."
    )


def _generate_response_brief(
    impact_assessment_json: str,
    tariff_event_description: str,
    supplier_risk_json: Optional[str] = None,
) -> str:
    """Generate a cross-team response brief from impact and risk data."""
    try:
        impact = json.loads(impact_assessment_json)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid impact_assessment_json: {exc}"})

    supplier_risks: list[dict] = []
    if supplier_risk_json:
        try:
            supplier_risks = json.loads(supplier_risk_json)
        except json.JSONDecodeError:
            logger.warning("Could not parse supplier_risk_json — proceeding without risk data")

    orders: list[dict] = impact.get("orders", [])
    portfolio: dict = impact.get("portfolio_summary", {})
    total_delta = portfolio.get("total_landed_cost_delta", 0)

    actions = []
    action_counter = {"P": 0, "S": 0, "F": 0}

    # High-impact orders (top 30% by landed cost delta) → expedite or re-source
    sorted_orders = sorted(orders, key=lambda o: abs(o.get("total_landed_cost_delta", 0)), reverse=True)
    top_n = max(1, len(sorted_orders) // 3)
    high_impact = sorted_orders[:top_n]
    low_impact = sorted_orders[top_n:]

    # Re-source actions for high-risk suppliers
    high_risk_supplier_ids = [
        s["supplier_id"] for s in supplier_risks
        if isinstance(s, dict) and s.get("risk_score", 0) >= 60
    ]

    if high_risk_supplier_ids:
        action_counter["P"] += 1
        actions.append({
            "action_id": f"P{action_counter['P']}",
            "action_type": "re-source",
            "description": (
                f"Initiate alternative sourcing for {len(high_risk_supplier_ids)} high-risk "
                f"supplier(s) identified in risk assessment"
            ),
            "affected_supplier_ids": high_risk_supplier_ids,
            "affected_order_count": len([
                o for o in orders
                if o.get("supplier_id") in high_risk_supplier_ids
            ]),
            "responsible_team": "procurement",
            "estimated_impact": "Reduces supply continuity risk; cost saving depends on alternative pricing",
            "status": "pending",
        })

    # Expedite actions for high-impact orders with near delivery dates
    if high_impact:
        action_counter["S"] += 1
        actions.append({
            "action_id": f"S{action_counter['S']}",
            "action_type": "expedite",
            "description": (
                f"Review delivery schedules for {len(high_impact)} highest-impact order(s) "
                f"and prioritise those with delivery dates within 30 days"
            ),
            "affected_order_ids": [o["order_id"] for o in high_impact],
            "responsible_team": "supply_chain",
            "estimated_impact": f"Avoids delay on orders with combined landed cost delta of "
                                 f"{sum(abs(o.get('total_landed_cost_delta', 0)) for o in high_impact):.2f}",
            "status": "pending",
        })

    # Re-route for remaining affected orders
    if low_impact:
        action_counter["S"] += 1
        actions.append({
            "action_id": f"S{action_counter['S']}",
            "action_type": "re-route",
            "description": (
                f"Evaluate alternative shipping routes for {len(low_impact)} lower-impact order(s) "
                f"to reduce cross-border duty exposure"
            ),
            "affected_order_ids": [o["order_id"] for o in low_impact],
            "responsible_team": "supply_chain",
            "estimated_impact": "Potential reduction in freight and duty charges; requires route analysis",
            "status": "pending",
        })

    # Reprice action for finance
    margin_delta = portfolio.get("total_margin_delta", 0)
    if margin_delta < 0:
        action_counter["F"] += 1
        actions.append({
            "action_id": f"F{action_counter['F']}",
            "action_type": "reprice",
            "description": (
                f"Review customer pricing for affected product categories to recover "
                f"margin impact of {abs(margin_delta):.2f} from landed cost increase"
            ),
            "affected_order_count": len(orders),
            "responsible_team": "finance",
            "estimated_impact": f"Full margin recovery: {abs(margin_delta):.2f} if repricing approved",
            "status": "pending",
        })

    brief = {
        "tariff_event": tariff_event_description,
        "total_actions": len(actions),
        "total_affected_orders": len(orders),
        "total_landed_cost_delta": total_delta,
        "actions_by_team": {
            "procurement": [a for a in actions if a["responsible_team"] == "procurement"],
            "supply_chain": [a for a in actions if a["responsible_team"] == "supply_chain"],
            "finance": [a for a in actions if a["responsible_team"] == "finance"],
        },
        "all_actions": actions,
    }

    logger.info(
        "[M3] Response brief generated: %d actions across %d teams",
        len(actions),
        len(set(a["responsible_team"] for a in actions)),
    )
    return json.dumps(brief, indent=2)


def get_response_brief_generator_tool() -> StructuredTool:
    return StructuredTool(
        name="response_brief_generator",
        description=(
            "Generates a structured cross-team response brief from impact assessment and "
            "supplier risk data. Produces prioritised recommended actions (re-route, re-source, "
            "reprice, expedite) assigned to procurement, supply chain, and finance teams. "
            "Returns a JSON brief with all actions and their initial 'pending' status."
        ),
        args_schema=ResponseBriefInput,
        func=_generate_response_brief,
    )
