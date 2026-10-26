"""Unit tests for the leadership summary generator tool."""
import json
import pytest
from app.tools.leadership_summary_generator import _generate_leadership_summary


@pytest.fixture
def tracker_json():
    return json.dumps({
        "total": 3,
        "by_status": {"pending": 1, "in-progress": 1, "complete": 1, "cancelled": 0},
        "actions": [
            {"action_id": "P1", "action_type": "re-source", "description": "Re-source steel", "responsible_team": "procurement", "assigned_owner": "Jane", "status": "complete", "estimated_impact": "Save 50000 USD"},
            {"action_id": "S1", "action_type": "re-route", "description": "Re-route Asia shipment", "responsible_team": "supply_chain", "assigned_owner": "Bob", "status": "in-progress", "estimated_impact": ""},
            {"action_id": "F1", "action_type": "reprice", "description": "Reprice steel products", "responsible_team": "finance", "assigned_owner": "unassigned", "status": "pending", "estimated_impact": ""},
        ]
    })


@pytest.fixture
def impact_json():
    return json.dumps({
        "portfolio_summary": {
            "total_landed_cost_delta": 17000.0,
            "total_margin_delta": -5100.0,
            "orders_with_full_data": 3,
            "orders_with_incomplete_data": 1,
        }
    })


def test_summary_contains_required_fields(tracker_json, impact_json):
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    assert "exposure" in result
    assert "response_actions" in result
    assert "outcomes" in result
    assert "tariff_event" in result


def test_exposure_figures(tracker_json, impact_json):
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    assert result["exposure"]["total_landed_cost_delta"] == pytest.approx(17000.0)
    assert result["exposure"]["total_margin_delta"] == pytest.approx(-5100.0)


def test_action_counts(tracker_json, impact_json):
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    assert result["response_actions"]["completed"] == 1
    assert result["response_actions"]["in_progress"] == 1
    assert result["response_actions"]["pending"] == 1


def test_outcomes_from_completed_actions(tracker_json, impact_json):
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    assert len(result["outcomes"]) >= 1
    assert result["outcomes"][0]["type"] == "re-source"


def test_incomplete_data_note(tracker_json, impact_json):
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    assert "incomplete" in result["data_quality_note"].lower() or "estimate" in result["data_quality_note"].lower()


def test_estimates_labelled(tracker_json, impact_json):
    """Outcomes with 'estimate' in impact should be labelled accordingly."""
    result = json.loads(_generate_leadership_summary(tracker_json, impact_json, "25% steel tariff"))
    for outcome in result["outcomes"]:
        if "estimate" in (outcome.get("impact", "")).lower():
            assert outcome["note"] == "estimate"


def test_invalid_json_returns_error():
    result = json.loads(_generate_leadership_summary("bad", "bad", "event"))
    assert "error" in result
