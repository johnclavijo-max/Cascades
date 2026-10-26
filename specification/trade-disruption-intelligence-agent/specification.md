# Specification: trade-disruption-intelligence-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full business context before implementing any task
- [x] Bootstrap agent code in `assets/trade-disruption-intelligence-agent/` using instructions from the sap-agent-bootstrap section (invoke from inside `assets/trade-disruption-intelligence-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [x] Create `assets/trade-disruption-intelligence-agent/app/skills/disruption-detection/SKILL.md` — instructions for scoping a tariff disruption event: how to interpret a user-reported tariff change, which product categories and HS codes to use as filters, how to query open purchase orders by material/commodity, and how to surface the prioritised affected order list (R1)
- [x] Create `assets/trade-disruption-intelligence-agent/app/skills/impact-assessment/SKILL.md` — step-by-step instructions for calculating landed cost delta: retrieve current cost breakdown per affected order, apply the user-provided or system-derived duty rate change, calculate margin exposure, flag orders with incomplete cost data, and summarise total exposure (R2)
- [x] Create `assets/trade-disruption-intelligence-agent/app/skills/response-coordination/SKILL.md` — instructions for generating a cross-team response brief: format recommended actions by action type (re-route, re-source, reprice, expedite), assign each action to the relevant team (procurement / supply chain / finance), and structure the output as a prioritised action table with owner and status fields (R4, R5)
- [x] Create `assets/trade-disruption-intelligence-agent/app/skills/supplier-risk/SKILL.md` — instructions for the supplier risk assessment flow: query risk exposure and engagement data for affected suppliers, rank suppliers by risk score, surface alternative sourcing options from supplier master data, and present findings with recommended action per supplier (R3)

---

## Project-Specific Tasks

### Disruption Scope Detection (R1)

- [x] Implement `disruption_scope` tool: given a tariff change description and optional commodity codes or product categories provided by the user, query open purchase orders from S/4HANA (`CE_PURCHASEORDER_0001`) filtered by relevant materials or plant/supplier combinations; return a prioritised list of affected orders with order ID, supplier, material, quantity, value, and delivery date
- [x] Implement `supplier_activity_query` tool: query procurement-related activity records from S/4HANA (`API_SUPPLIER_ACTIVITY_SRV`) for the identified affected suppliers to surface current engagement status and open commitments
- [x] Add system prompt instruction: when a user describes a tariff event, the agent must always run disruption scope detection first (M1) before proceeding to any other step; load the `disruption-detection` skill for this workflow

### Landed Cost and Margin Impact Assessment (R2)

- [x] Implement `cost_breakdown_query` tool: for each affected order identified in R1, retrieve cost breakdown records from Ariba (`cost_breakdown:v1`) to extract current cost components (unit price, freight, duty, other charges) per order/line
- [x] Implement `pricing_query` tool: retrieve current pricing information from Ariba (`pricing:v1`) for affected materials to establish the baseline landed cost per unit before tariff change
- [x] Implement `margin_impact_calculator` tool: a pure-Python tool (no API call) that takes cost breakdown and pricing data plus a user-supplied duty rate delta (as a percentage) and computes: new landed cost per order, margin delta per order, total portfolio exposure, and a list of orders where cost data is incomplete; flag incomplete data orders explicitly in the output
- [x] Add system prompt instruction: the agent must state the data completeness of every impact calculation (what percentage of affected orders had full cost data); when cost data is missing for an order, the agent must flag it and prompt the user to confirm a manual estimate rather than silently omitting those orders from the exposure total; load the `impact-assessment` skill for this workflow

### Supplier Risk and Alternative Sourcing View (R3)

- [x] Implement `supplier_risk_exposure` tool: query Ariba Risk Exposure API (`risk_exposure:v3`) for the affected suppliers identified in R1; return risk score, risk category, and trend direction per supplier
- [x] Implement `supplier_risk_engagement` tool: query Ariba Risk Engagements API (`risk_engagement:v2`) for open risk mitigation engagements per affected supplier; surface any active engagement status that is relevant to the current disruption
- [x] Implement `alternative_supplier_query` tool: query the Ariba procurement reporting API (`procurement_reporting_details:v2`) to identify suppliers for the same material categories that are not currently flagged as high-risk; surface as a ranked list of alternative sourcing options
- [x] Add system prompt instruction: when presenting supplier risk results, the agent must always include a recommended action per supplier (continue / monitor / escalate / re-source) based on the risk score returned; load the `supplier-risk` skill for this workflow

### Cross-Team Response Brief Generation (R4)

- [x] Implement `response_brief_generator` tool: a pure-Python tool that takes the output of the impact assessment and supplier risk tools and produces a structured response brief — a list of prioritised recommended actions (re-route, re-source, reprice, expedite), each with: action type, affected orders, responsible team, estimated cost/margin impact, and initial status of "pending"
- [x] Add system prompt instruction: the agent must offer to generate a response brief after completing the impact assessment (M3); the brief must cover at least procurement, supply chain, and finance if there are affected actions in each domain; load the `response-coordination` skill for brief generation

### Action Tracking and Coordination (R5)

- [x] Implement `action_tracker` tool: an in-session state tracker (Python dict maintained across conversation turns) that records each recommended action from the response brief with fields: action_id, action_type, description, assigned_team, assigned_owner (user-provided), status (pending / in-progress / complete), and last_updated; supports update, list, and status-check operations
- [x] Add system prompt instruction: when a user assigns an owner to an action or updates its status, the agent must confirm the update and show the full current action list; the agent must never infer ownership — it must always ask the user to confirm the assigned owner before recording (M4)

### Purchase Requisition Initiation (R6)

- [x] Implement `create_purchase_requisition` tool: given user-confirmed re-sourcing details (material, quantity, preferred supplier, delivery date), construct and submit a purchase requisition to S/4HANA via the `CE_PURCHASEREQUISITION_0001` API; return the created requisition ID and status
- [x] Add system prompt instruction: before submitting any purchase requisition, the agent must display the full requisition details and ask the user for explicit confirmation; the agent must never submit a requisition without a confirmed "yes" from the user in the current conversation turn; rejection must be acknowledged and no requisition created

### Tariff Classification Query (R7)

- [x] Implement `tariff_classification_query` tool: query S/4HANA purchase order data (`CE_PURCHASEORDER_0001`) for material commodity code / tariff classification fields on the affected orders; return available classification data per material and flag materials where tariff classification is missing or incomplete
- [x] Add system prompt instruction: when presenting tariff classification results, the agent must explicitly state which materials have complete classification data and which do not; for incomplete data, it must recommend that the trade compliance officer verify the classification manually in SAP GTS; the agent must never infer or guess a tariff classification

### Procurement Reporting and Spend Visibility (supporting R1, R2, R4)

- [x] Implement `procurement_spend_report` tool: query Ariba operational procurement reporting (`procurement_reporting_details:v2`) to retrieve spend data for affected suppliers and material categories over a configurable lookback period (default: last 12 months); surface total spend by supplier, material, and plant as context for re-sourcing and repricing decisions
- [x] Add system prompt instruction: the agent should offer to pull spend context when generating the response brief, to help procurement managers understand the financial weight of each recommended action

### Leadership Post-Event Summary (R8)

- [x] Implement `leadership_summary_generator` tool: a pure-Python tool that takes the completed action tracker state and impact assessment output and produces a structured executive summary with: total landed cost exposure, number of affected orders and suppliers, actions taken (by type and team), actions still pending, and quantified outcomes where available (completed re-sources, requisitions created, cost savings estimated)
- [x] Add system prompt instruction: the agent should offer to generate a leadership summary when the user asks for a post-event overview or when all actions in the tracker are marked complete or in-progress (M5); the summary must clearly distinguish confirmed outcomes from estimates

---

## Agent System Prompt

- [x] Write a clear, concise system prompt in `assets/trade-disruption-intelligence-agent/app/agent.py` that:
  - Identifies the agent as a Trade Disruption Intelligence Agent for supply chain planners, procurement managers, finance analysts, trade compliance officers, and executive leadership
  - Instructs the agent to always start with disruption scope detection (M1) when a tariff event is described
  - Instructs the agent to progress through the milestone sequence: detect (M1) → assess (M2) → brief (M3) → coordinate (M4) → summarise (M5), but to allow users to jump to any step if context is already established
  - States the guardrails: never submit a purchase requisition without explicit user confirmation; never post financial entries; never infer tariff classifications; never infer action ownership; always flag data gaps explicitly
  - Instructs the agent to load the appropriate runtime skill for each major workflow step
  - States the available tools by category: disruption scope tools (S/4HANA), impact tools (Ariba cost + pricing), supplier risk tools (Ariba risk), coordination tools (in-session), write tools (S/4HANA requisition)

---

## Business Instrumentation

- [x] Implement structured logging and OpenTelemetry spans for all 5 milestones from the PRD:
  - `M1.achieved` / `M1.missed` — disruption scope query completed or failed
  - `M2.achieved` / `M2.missed` — impact assessment completed or incomplete cost data prevented full assessment
  - `M3.achieved` / `M3.missed` — response brief generated or not requested/generated
  - `M4.achieved` / `M4.missed` — at least one action assigned and tracked, or no actions confirmed
  - `M5.achieved` / `M5.missed` — leadership summary produced or not produced
- [x] Follow pattern `[MILESTONE_ID].[achieved|missed]: [description]` for all log statements
- [x] Extract business logic from `stream()` into plain async helpers to avoid `GeneratorExit` context errors (see guidelines-agent-python.md)
- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [x] Verify `api-discovery-results.md` exists at workspace root (created during spec generation)
- [x] Invoke `mcp-translation-file` skill for all 8 downloaded API spec files in `specification/trade-disruption-intelligence-agent/api-specs/`; then invoke `setup-solution` to create and register MCP assets
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — NEVER import directly from `sap_cloud_sdk.agentgateway`; NEVER create direct HTTP clients for SAP APIs
- [x] Add MCP server dependencies to `asset.yaml` under `requires` — one entry per generated MCP server using exact ORD IDs from generated assets
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP translation is complete

**MCP API scopes** (for `mcp-translation-file` skill pruning):

```
MCP API: sap.s4:apiResource:CE_PURCHASEORDER_0001:v1
MCP tool scope: read-only
Resources in scope: A_PurchaseOrder, A_PurchaseOrderItem, A_PurchaseOrderScheduleLine

MCP API: sap.s4:apiResource:CE_PURCHASEREQUISITION_0001:v1
MCP tool scope: read-write
Resources in scope: A_PurchaseRequisitionHeader, A_PurchaseRequisitionItem

MCP API: sap.s4:apiResource:API_SUPPLIER_ACTIVITY_SRV:v1
MCP tool scope: read-only
Resources in scope: A_ProcurRelatedActivity, A_ProcurRelatedActvTask

MCP API: sap.aribas4:apiResource:risk_exposure:v3
MCP tool scope: read-only
Resources in scope: /riskExposures, /riskExposures/{id}

MCP API: sap.aribas4:apiResource:risk_engagement:v2
MCP tool scope: read-only
Resources in scope: /engagements, /engagements/{id}

MCP API: sap.aribas4:apiResource:cost_breakdown:v1
MCP tool scope: read-only
Resources in scope: /costBreakdowns, /costBreakdowns/{id}

MCP API: sap.aribas4:apiResource:pricing:v1
MCP tool scope: read-only
Resources in scope: /prices, /prices/{id}

MCP API: sap.aribabuyer:apiResource:procurement_reporting_details:v2
MCP tool scope: read-only
Resources in scope: /views/{viewTemplateName}/execute
```

---

## Testing

- [x] `conftest.py` sets only `IBD_TESTING=true` — agent runs with mock MCP tool results during tests
- [x] Write unit tests in `assets/trade-disruption-intelligence-agent/tests/` — one per tool:
  - `test_disruption_scope.py` — mock S/4HANA PO response; verify affected order list is returned and prioritised correctly
  - `test_supplier_activity_query.py` — mock supplier activity API response; verify engagement status is surfaced correctly
  - `test_cost_breakdown_query.py` — mock Ariba cost breakdown response; verify cost components are extracted per order
  - `test_pricing_query.py` — mock Ariba pricing response; verify baseline landed cost per unit is returned
  - `test_margin_impact_calculator.py` — pure-Python tool; test with known inputs: verify landed cost delta and margin exposure calculated correctly; test incomplete data flagging
  - `test_supplier_risk_exposure.py` — mock Ariba risk exposure response; verify risk score and category returned per supplier
  - `test_supplier_risk_engagement.py` — mock Ariba risk engagement response; verify active engagement status returned
  - `test_alternative_supplier_query.py` — mock procurement reporting response; verify alternative supplier list is ranked and returned
  - `test_response_brief_generator.py` — pure-Python tool; verify structured brief is generated with correct action types and team assignments
  - `test_action_tracker.py` — pure-Python tool; verify create, update, list, and status-check operations; verify ownership is never inferred
  - `test_create_purchase_requisition.py` — mock S/4HANA requisition API; verify requisition is submitted with correct fields; verify it is NOT submitted without explicit user confirmation
  - `test_tariff_classification_query.py` — mock S/4HANA PO response with commodity code fields; verify classification data returned and missing codes flagged
  - `test_procurement_spend_report.py` — mock Ariba reporting response; verify spend returned by supplier, material, and plant
  - `test_leadership_summary_generator.py` — pure-Python tool; verify summary covers all required fields: exposure, actions, outcomes; verify estimates are labelled as estimates
- [x] Write one integration test `test_end_to_end.py` executing the full agent flow: tariff event described → disruption scoped → impact assessed → response brief generated → action assigned → summary produced; use mocked LLM responses and mocked MCP tools; test must run offline
- [x] Run `pytest` from `assets/trade-disruption-intelligence-agent/` (no args); if coverage < 70%, add tests until threshold is met
- [x] Run `pytest` again from `assets/trade-disruption-intelligence-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/trade-disruption-intelligence-agent/`
