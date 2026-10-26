"""Unit tests for the response brief generator tool."""
import json
import pytest
from app.tools.response_brief_generator import _generate_response_brief


@pytest.fixture
def impact_json():
    return json.dumps({
        "orders": [
            {"order_id": "4500000001", "supplier_id": "VENDOR-1001", "total_landed_cost_delta": -10000.0, "margin_delta": -3000.0},
            {"order_id": "4500000002", "supplier_id": "VENDOR-1002", "total_landed_cost_delta": -5000.0, "margin_delta": -1500.0},
            {"order_id": "4500000003", "supplier_id": "VENDOR-1003", "total_landed_cost_delta": -2000.0, "margin_delta": -600.0},
        ],
        "portfolio_summary": {
            "total_landed_cost_delta": -17000.0,
            "total_margin_delta": -5100.0,
            "orders_with_full_data": 3,
            "orders_with_incomplete_data": 0,
        }
    })


def test_generates_actions(impact_json):
    result = json.loads(_generate_response_brief(impact_json, "25% US steel tariff"))
    assert result["total_actions"] > 0
    assert len(result["all_actions"]) > 0


def test_actions_have_required_fields(impact_json):
    result = json.loads(_generate_response_brief(impact_json, "25% US steel tariff"))
    for action in result["all_actions"]:
        assert "action_id" in action
        assert "action_type" in action
        assert "description" in action
        assert "responsible_team" in action
        assert action["status"] == "pending"


def test_covers_finance_team_for_margin_impact(impact_json):
    result = json.loads(_generate_response_brief(impact_json, "25% US steel tariff"))
    teams = {a["responsible_team"] for a in result["all_actions"]}
    assert "finance" in teams


def test_supply_chain_action_present(impact_json):
    result = json.loads(_generate_response_brief(impact_json, "25% US steel tariff"))
    teams = {a["responsible_team"] for a in result["all_actions"]}
    assert "supply_chain" in teams


def test_resource_action_for_high_risk_suppliers(impact_json):
    risk_json = json.dumps([
        {"supplier_id": "VENDOR-1001", "risk_score": 75},
        {"supplier_id": "VENDOR-1002", "risk_score": 30},
    ])
    result = json.loads(_generate_response_brief(impact_json, "25% steel tariff", risk_json))
    procurement_actions = result["actions_by_team"].get("procurement", [])
    action_types = [a["action_type"] for a in procurement_actions]
    assert "re-source" in action_types


def test_invalid_json_returns_error():
    result = json.loads(_generate_response_brief("not_valid_json", "test event"))
    assert "error" in result
