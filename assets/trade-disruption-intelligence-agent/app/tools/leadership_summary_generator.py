"""Pure-Python tool to generate a post-event leadership summary.

Combines action tracker state and impact assessment output into a concise
executive summary. No external API calls are made.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LeadershipSummaryInput(BaseModel):
    action_tracker_json: str = Field(
        description=(
            "JSON string from action_tracker list operation containing all actions "
            "with their current status, owners, and estimated impacts."
        )
    )
    impact_assessment_json: str = Field(
        description=(
            "JSON string from margin_impact_calculator containing portfolio_summary "
            "with total landed cost delta and margin delta."
        )
    )
    tariff_event_description: str = Field(
        description="Brief description of the tariff event this summary covers."
    )
    is_final: bool = Field(
        default=False,
        description=(
            "Set to True when all actions are complete or in-progress (post-event). "
            "Set to False for an interim summary. Affects summary tone and labelling."
        ),
    )


def _generate_leadership_summary(
    action_tracker_json: str,
    impact_assessment_json: str,
    tariff_event_description: str,
    is_final: bool = False,
) -> str:
    """Generate a post-event executive summary."""
    try:
        tracker = json.loads(action_tracker_json)
        impact = json.loads(impact_assessment_json)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON input: {exc}"})

    portfolio = impact.get("portfolio_summary", {})
    actions = tracker.get("actions", [])
    by_status = tracker.get("by_status", {})

    total_exposure = abs(portfolio.get("total_landed_cost_delta", 0))
    margin_delta = portfolio.get("total_margin_delta", 0)
    affected_orders = portfolio.get("orders_with_full_data", 0) + portfolio.get("orders_with_incomplete_data", 0)

    completed_actions = [a for a in actions if a.get("status") == "complete"]
    in_progress_actions = [a for a in actions if a.get("status") == "in-progress"]
    pending_actions = [a for a in actions if a.get("status") == "pending"]

    # Derive quantified outcomes from completed re-source / re-route actions
    outcomes = []
    for a in completed_actions:
        if a.get("action_type") in ("re-source", "re-route"):
            outcomes.append({
                "action_id": a["action_id"],
                "type": a["action_type"],
                "description": a["description"],
                "impact": a.get("estimated_impact", "Outcome not quantified"),
                "owner": a.get("assigned_owner", "unassigned"),
                "note": "estimate" if "estimate" in a.get("estimated_impact", "").lower() else "confirmed",
            })

    summary_type = "Post-Event Summary" if is_final else "Interim Summary"
    generated_at = datetime.now(tz=timezone.utc).isoformat()

    summary = {
        "summary_type": summary_type,
        "generated_at": generated_at,
        "tariff_event": tariff_event_description,
        "exposure": {
            "total_landed_cost_delta": total_exposure,
            "total_margin_delta": margin_delta,
            "affected_orders_count": affected_orders,
            "note": (
                "Includes estimate for orders with incomplete cost data"
                if portfolio.get("orders_with_incomplete_data", 0) > 0
                else "Full cost data available for all affected orders"
            ),
        },
        "response_actions": {
            "total": len(actions),
            "completed": len(completed_actions),
            "in_progress": len(in_progress_actions),
            "pending": len(pending_actions),
        },
        "outcomes": outcomes,
        "outstanding_risks": [
            {
                "action_id": a["action_id"],
                "description": a["description"],
                "responsible_team": a["responsible_team"],
            }
            for a in pending_actions
        ],
        "data_quality_note": (
            f"{portfolio.get('orders_with_incomplete_data', 0)} order(s) had incomplete cost data; "
            f"exposure figures for those orders are estimated."
            if portfolio.get("orders_with_incomplete_data", 0) > 0
            else "Full cost data available for all affected orders."
        ),
    }

    log_status = "M5.achieved" if (is_final or len(pending_actions) == 0) else "M5.achieved (interim)"
    logger.info(
        "[%s]: leadership summary produced — total exposure %.2f, %d actions completed, %d outcomes quantified",
        log_status,
        total_exposure,
        len(completed_actions),
        len(outcomes),
    )
    return json.dumps(summary, indent=2)


def get_leadership_summary_generator_tool() -> StructuredTool:
    return StructuredTool(
        name="leadership_summary_generator",
        description=(
            "Generates a post-event executive summary combining action tracker state and "
            "impact assessment output. Covers total exposure, actions taken, and quantified "
            "outcomes. Clearly distinguishes estimates from confirmed figures. "
            "Use after all actions are assigned (M4 complete) or when leadership requests a summary."
        ),
        args_schema=LeadershipSummaryInput,
        func=_generate_leadership_summary,
    )
