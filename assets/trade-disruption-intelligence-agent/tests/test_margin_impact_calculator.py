"""Unit tests for the margin impact calculator tool."""
import json
import pytest
from app.tools.margin_impact_calculator import _calculate_margin_impact


@pytest.fixture
def sample_cost_data():
    return json.dumps([
        {
            "order_id": "4500000001",
            "material_id": "MAT-0001",
            "unit_price": 400.0,
            "current_duty_amount": 40.0,
            "freight_charges": 50.0,
            "other_charges": 10.0,
            "quantity": 100,
        },
        {
            "order_id": "4500000002",
            "material_id": "MAT-0002",
            "unit_price": 800.0,
            "current_duty_amount": 80.0,
            "freight_charges": 60.0,
            "other_charges": 0.0,
            "quantity": 50,
        },
    ])


@pytest.fixture
def sample_pricing_data():
    return json.dumps([
        {"material_id": "MAT-0001", "selling_price": 700.0},
        {"material_id": "MAT-0002", "selling_price": 1200.0},
    ])


def test_basic_impact_calculation(sample_cost_data, sample_pricing_data):
    result = json.loads(_calculate_margin_impact(sample_cost_data, sample_pricing_data, 25.0))
    orders = result["orders"]
    assert len(orders) == 2
    # For MAT-0001: duty_delta = 400 * 0.25 = 100, new_lc = 400+40+50+10+100 = 600
    order1 = next(o for o in orders if o["order_id"] == "4500000001")
    assert order1["new_landed_cost_per_unit"] == pytest.approx(600.0)
    assert order1["landed_cost_delta_per_unit"] == pytest.approx(100.0)
    assert order1["total_landed_cost_delta"] == pytest.approx(10000.0)  # 100 * 100 qty


def test_portfolio_totals(sample_cost_data, sample_pricing_data):
    result = json.loads(_calculate_margin_impact(sample_cost_data, sample_pricing_data, 25.0))
    summary = result["portfolio_summary"]
    assert summary["orders_with_full_data"] == 2
    assert summary["orders_with_incomplete_data"] == 0
    assert summary["total_landed_cost_delta"] > 0


def test_incomplete_data_flagging():
    cost_data = json.dumps([
        {"order_id": "4500000003", "material_id": "MAT-0003"},  # missing required fields
        {"order_id": "4500000004", "material_id": "MAT-0004", "unit_price": 200.0, "current_duty_amount": 20.0, "freight_charges": 30.0, "quantity": 10},
    ])
    pricing_data = json.dumps([{"material_id": "MAT-0004", "selling_price": 500.0}])
    result = json.loads(_calculate_margin_impact(cost_data, pricing_data, 10.0))
    assert len(result["incomplete_orders"]) == 1
    assert result["incomplete_orders"][0]["order_id"] == "4500000003"
    assert result["portfolio_summary"]["orders_with_incomplete_data"] == 1
    assert result["portfolio_summary"]["orders_with_full_data"] == 1


def test_freight_surcharge_included(sample_cost_data, sample_pricing_data):
    result_without = json.loads(_calculate_margin_impact(sample_cost_data, sample_pricing_data, 25.0, False))
    result_with = json.loads(_calculate_margin_impact(sample_cost_data, sample_pricing_data, 25.0, True))
    # With freight surcharge, delta should be higher
    delta_without = result_without["portfolio_summary"]["total_landed_cost_delta"]
    delta_with = result_with["portfolio_summary"]["total_landed_cost_delta"]
    assert delta_with > delta_without


def test_invalid_json_returns_error():
    result = json.loads(_calculate_margin_impact("invalid_json", "[]", 10.0))
    assert "error" in result


def test_zero_duty_delta(sample_cost_data, sample_pricing_data):
    result = json.loads(_calculate_margin_impact(sample_cost_data, sample_pricing_data, 0.0))
    summary = result["portfolio_summary"]
    assert summary["total_landed_cost_delta"] == pytest.approx(0.0)
