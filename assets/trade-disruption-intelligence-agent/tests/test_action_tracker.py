"""Unit tests for the action tracker tool."""
import json
import pytest
from app.tools.action_tracker import _action_tracker, _action_store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the action store before each test."""
    _action_store.clear()
    yield
    _action_store.clear()


def test_create_action():
    result = json.loads(_action_tracker(
        operation="create",
        action_id="P1",
        action_type="re-source",
        description="Re-source steel from alternative supplier",
        responsible_team="procurement",
    ))
    assert result["success"] is True
    assert result["action"]["action_id"] == "P1"
    assert result["action"]["status"] == "pending"
    assert result["action"]["assigned_owner"] == "unassigned"


def test_create_requires_mandatory_fields():
    result = json.loads(_action_tracker(operation="create", action_id="P1"))
    assert "error" in result


def test_update_status():
    _action_tracker(operation="create", action_id="S1", action_type="re-route",
                    description="Re-route shipment", responsible_team="supply_chain")
    result = json.loads(_action_tracker(operation="update", action_id="S1", status="in-progress"))
    assert result["action"]["status"] == "in-progress"


def test_update_owner_requires_user_confirmation():
    """Owner is set only when explicitly provided — never inferred."""
    _action_tracker(operation="create", action_id="F1", action_type="reprice",
                    description="Reprice orders", responsible_team="finance")
    # Owner starts as unassigned
    result = json.loads(_action_tracker(operation="status_check", action_id="F1"))
    assert result["assigned_owner"] == "unassigned"
    # Owner only set when user explicitly provides it
    _action_tracker(operation="update", action_id="F1", assigned_owner="John Doe")
    result2 = json.loads(_action_tracker(operation="status_check", action_id="F1"))
    assert result2["assigned_owner"] == "John Doe"


def test_list_returns_all_actions():
    _action_tracker(operation="create", action_id="P1", action_type="re-source",
                    description="desc1", responsible_team="procurement")
    _action_tracker(operation="create", action_id="S1", action_type="re-route",
                    description="desc2", responsible_team="supply_chain")
    result = json.loads(_action_tracker(operation="list"))
    assert result["total"] == 2


def test_status_check_unknown_action():
    result = json.loads(_action_tracker(operation="status_check", action_id="UNKNOWN"))
    assert "error" in result


def test_update_nonexistent_action():
    result = json.loads(_action_tracker(operation="update", action_id="X99", status="complete"))
    assert "error" in result


def test_by_status_counts():
    _action_tracker(operation="create", action_id="P1", action_type="re-source",
                    description="d1", responsible_team="procurement")
    _action_tracker(operation="create", action_id="S1", action_type="re-route",
                    description="d2", responsible_team="supply_chain")
    _action_tracker(operation="update", action_id="S1", status="in-progress")
    result = json.loads(_action_tracker(operation="list"))
    assert result["by_status"]["pending"] == 1
    assert result["by_status"]["in-progress"] == 1
