"""Integration test: end-to-end agent flow with mocked LLM and MCP tools."""
import asyncio
import json
import os
import pytest

os.environ["IBD_TESTING"] = "1"


@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    monkeypatch.setenv("IBD_TESTING", "1")


@pytest.mark.asyncio
async def test_agent_invoke_returns_response():
    """Agent.invoke() completes with a non-empty response given a trade disruption query."""
    from app.agent import SampleAgent, AgentResponse
    from app.tools.action_tracker import _action_store
    from app.tools.margin_impact_calculator import get_margin_impact_calculator_tool
    from app.tools.response_brief_generator import get_response_brief_generator_tool
    from app.tools.action_tracker import get_action_tracker_tool
    from app.tools.leadership_summary_generator import get_leadership_summary_generator_tool
    from app.datetime_tool import get_datetime_tool

    _action_store.clear()

    agent = SampleAgent()
    tools = [
        get_datetime_tool(),
        get_margin_impact_calculator_tool(),
        get_response_brief_generator_tool(),
        get_action_tracker_tool(),
        get_leadership_summary_generator_tool(),
    ]

    response = await agent.invoke(
        query="What is the current date?",
        context_id="test-context-001",
        tools=tools,
    )

    assert response.status in ("completed", "input_required")
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_stream_yields_chunks():
    """Agent.stream() yields at least one processing chunk and a final chunk."""
    from app.agent import SampleAgent
    from app.datetime_tool import get_datetime_tool

    agent = SampleAgent()
    tools = [get_datetime_tool()]

    chunks = []
    async for chunk in agent.stream(
        query="Hello, what can you help me with?",
        context_id="test-context-002",
        tools=tools,
    ):
        chunks.append(chunk)

    assert len(chunks) >= 2
    final = chunks[-1]
    assert final["is_task_complete"] is True
    assert len(final["content"]) > 0


@pytest.mark.asyncio
async def test_margin_calculator_tool_in_agent_context():
    """Pure-Python tools work correctly in isolation (offline)."""
    from app.tools.margin_impact_calculator import _calculate_margin_impact

    cost_data = json.dumps([{
        "order_id": "4500000001",
        "material_id": "MAT-0001",
        "unit_price": 400.0,
        "current_duty_amount": 40.0,
        "freight_charges": 50.0,
        "other_charges": 0.0,
        "quantity": 100,
    }])
    pricing_data = json.dumps([{"material_id": "MAT-0001", "selling_price": 700.0}])

    result = json.loads(_calculate_margin_impact(cost_data, pricing_data, 25.0))
    assert result["portfolio_summary"]["total_landed_cost_delta"] > 0
    assert result["portfolio_summary"]["orders_with_full_data"] == 1


@pytest.mark.asyncio
async def test_action_tracker_full_lifecycle():
    """Full create → update → list lifecycle works correctly."""
    from app.tools.action_tracker import _action_tracker, _action_store

    _action_store.clear()

    r1 = json.loads(_action_tracker("create", action_id="P1", action_type="re-source",
                                     description="Re-source steel", responsible_team="procurement"))
    assert r1["success"]
    assert r1["action"]["status"] == "pending"

    r2 = json.loads(_action_tracker("update", action_id="P1", assigned_owner="Jane", status="in-progress"))
    assert r2["action"]["assigned_owner"] == "Jane"
    assert r2["action"]["status"] == "in-progress"

    r3 = json.loads(_action_tracker("list"))
    assert r3["total"] == 1
    assert r3["by_status"]["in-progress"] == 1


@pytest.mark.asyncio
async def test_response_brief_to_action_tracking_pipeline():
    """Brief generation → action tracking pipeline works end-to-end (offline)."""
    from app.tools.response_brief_generator import _generate_response_brief
    from app.tools.action_tracker import _action_tracker, _action_store
    from app.tools.leadership_summary_generator import _generate_leadership_summary

    _action_store.clear()

    impact = json.dumps({
        "orders": [{"order_id": "4500000001", "supplier_id": "VENDOR-1001", "total_landed_cost_delta": -10000.0, "margin_delta": -3000.0}],
        "portfolio_summary": {"total_landed_cost_delta": -10000.0, "total_margin_delta": -3000.0, "orders_with_full_data": 1, "orders_with_incomplete_data": 0}
    })

    brief = json.loads(_generate_response_brief(impact, "25% steel tariff"))
    assert brief["total_actions"] > 0

    # Simulate user assigning first action
    first_action = brief["all_actions"][0]
    _action_tracker("create", action_id=first_action["action_id"],
                    action_type=first_action["action_type"],
                    description=first_action["description"],
                    responsible_team=first_action["responsible_team"],
                    assigned_owner="Maria")
    _action_tracker("update", action_id=first_action["action_id"], status="complete")

    tracker = json.loads(_action_tracker("list"))

    summary = json.loads(_generate_leadership_summary(
        action_tracker_json=json.dumps(tracker),
        impact_assessment_json=impact,
        tariff_event_description="25% steel tariff",
        is_final=True,
    ))

    assert summary["response_actions"]["completed"] >= 1
    assert summary["exposure"]["total_landed_cost_delta"] > 0
