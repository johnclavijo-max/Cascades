"""In-session action tracker tool.

Maintains a per-session dictionary of recommended actions from the response
brief. Supports create, update, list, and status-check operations.
Ownership is NEVER inferred — the user must always confirm the owner.
No external API calls are made.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Literal, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Module-level store — shared within a single process/session.
# In production, this is scoped per conversation thread.
_action_store: dict[str, dict] = {}


class ActionTrackerInput(BaseModel):
    operation: Literal["create", "update", "list", "status_check"] = Field(
        description=(
            "Operation to perform: "
            "'create' adds a new action, "
            "'update' modifies an existing action's owner or status, "
            "'list' returns all actions, "
            "'status_check' returns current status of a specific action."
        )
    )
    action_id: Optional[str] = Field(
        default=None,
        description="Action ID (e.g. P1, S2, F1). Required for update and status_check operations.",
    )
    action_type: Optional[str] = Field(
        default=None,
        description="Action type: re-route, re-source, reprice, or expedite. Required for create.",
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the action. Required for create.",
    )
    responsible_team: Optional[str] = Field(
        default=None,
        description="Team responsible: procurement, supply_chain, or finance. Required for create.",
    )
    assigned_owner: Optional[str] = Field(
        default=None,
        description=(
            "Name of the person assigned to own this action. "
            "MUST be explicitly confirmed by the user before setting. "
            "Never infer ownership."
        ),
    )
    status: Optional[Literal["pending", "in-progress", "complete", "cancelled"]] = Field(
        default=None,
        description="Action status. Use for update operations.",
    )
    estimated_impact: Optional[str] = Field(
        default=None,
        description="Estimated cost or margin impact. Used for create.",
    )


def _action_tracker(
    operation: str,
    action_id: Optional[str] = None,
    action_type: Optional[str] = None,
    description: Optional[str] = None,
    responsible_team: Optional[str] = None,
    assigned_owner: Optional[str] = None,
    status: Optional[str] = None,
    estimated_impact: Optional[str] = None,
) -> str:
    """Perform action tracking operations."""
    now = datetime.now(tz=timezone.utc).isoformat()

    if operation == "create":
        if not all([action_id, action_type, description, responsible_team]):
            return json.dumps({
                "error": "create requires action_id, action_type, description, and responsible_team"
            })
        _action_store[action_id] = {  # type: ignore[index]
            "action_id": action_id,
            "action_type": action_type,
            "description": description,
            "responsible_team": responsible_team,
            "assigned_owner": assigned_owner or "unassigned",
            "status": status or "pending",
            "estimated_impact": estimated_impact or "",
            "created_at": now,
            "last_updated": now,
        }
        logger.info("[M4] Action created: %s (%s)", action_id, responsible_team)
        return json.dumps({"success": True, "action": _action_store[action_id]})

    elif operation == "update":
        if not action_id:
            return json.dumps({"error": "update requires action_id"})
        if action_id not in _action_store:
            return json.dumps({"error": f"Action {action_id} not found"})
        if assigned_owner:
            _action_store[action_id]["assigned_owner"] = assigned_owner
        if status:
            _action_store[action_id]["status"] = status
        _action_store[action_id]["last_updated"] = now
        assigned = sum(1 for a in _action_store.values() if a.get("assigned_owner") != "unassigned")
        pending = sum(1 for a in _action_store.values() if a.get("status") == "pending")
        if assigned > 0:
            logger.info(
                "[M4] Action coordination active: %d actions assigned, %d pending",
                assigned, pending,
            )
        return json.dumps({"success": True, "action": _action_store[action_id]})

    elif operation == "list":
        actions = list(_action_store.values())
        summary = {
            "total": len(actions),
            "by_status": {
                "pending": sum(1 for a in actions if a["status"] == "pending"),
                "in-progress": sum(1 for a in actions if a["status"] == "in-progress"),
                "complete": sum(1 for a in actions if a["status"] == "complete"),
                "cancelled": sum(1 for a in actions if a["status"] == "cancelled"),
            },
            "actions": actions,
        }
        return json.dumps(summary, indent=2)

    elif operation == "status_check":
        if not action_id:
            return json.dumps({"error": "status_check requires action_id"})
        if action_id not in _action_store:
            return json.dumps({"error": f"Action {action_id} not found"})
        return json.dumps(_action_store[action_id], indent=2)

    return json.dumps({"error": f"Unknown operation: {operation}"})


def get_action_tracker_tool() -> StructuredTool:
    return StructuredTool(
        name="action_tracker",
        description=(
            "Tracks recommended actions from the response brief across procurement, supply chain, "
            "and finance. Supports create, update, list, and status_check operations. "
            "Ownership must always be explicitly confirmed by the user before setting assigned_owner. "
            "Never infer or guess the owner."
        ),
        args_schema=ActionTrackerInput,
        func=_action_tracker,
    )
