"""Unit tests for the action tracker tool."""
import json
import pytest
from app.tools.action_tracker import (
    _action_tracker,
    _action_store,
    set_action_thread,
    reset_action_thread,
)


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


def test_actions_isolated_between_threads():
    """Actions created under one conversation thread must not be visible to,
    or collide with, another thread — even when action IDs are identical."""
    tok_a = set_action_thread("userA:ctx1")
    try:
        _action_tracker(operation="create", action_id="P1", action_type="re-source",
                        description="A's resource action", responsible_team="procurement")
    finally:
        reset_action_thread(tok_a)

    # Thread B sees none of thread A's actions.
    tok_b = set_action_thread("userB:ctx1")
    try:
        listed = json.loads(_action_tracker(operation="list"))
        assert listed["total"] == 0
        assert "error" in json.loads(_action_tracker(operation="status_check", action_id="P1"))

        # B creates its own P1 — same ID, different content — without touching A's.
        _action_tracker(operation="create", action_id="P1", action_type="expedite",
                        description="B's expedite action", responsible_team="supply_chain")
        _action_tracker(operation="update", action_id="P1", status="complete")
    finally:
        reset_action_thread(tok_b)

    # A's P1 is untouched: still pending, still A's description.
    tok_a2 = set_action_thread("userA:ctx1")
    try:
        a_p1 = json.loads(_action_tracker(operation="status_check", action_id="P1"))
        assert a_p1["status"] == "pending"
        assert a_p1["description"] == "A's resource action"
        assert json.loads(_action_tracker(operation="list"))["total"] == 1
    finally:
        reset_action_thread(tok_a2)


def test_same_thread_shares_bucket():
    """A re-bind to the same thread key resumes the same action bucket."""
    tok = set_action_thread("userA:ctx1")
    try:
        _action_tracker(operation="create", action_id="S1", action_type="re-route",
                        description="d", responsible_team="supply_chain")
    finally:
        reset_action_thread(tok)
    tok2 = set_action_thread("userA:ctx1")
    try:
        assert json.loads(_action_tracker(operation="status_check", action_id="S1"))["action_id"] == "S1"
    finally:
        reset_action_thread(tok2)
