# Product Requirements Document (PRD)

**Title:** Trade Disruption Intelligence Agent
**Date:** 2026-10-26
**Owner:** Supply Chain / Procurement Leadership
**Solution Category:** AI Agent (Python, A2A protocol on SAP BTP)

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
When tariffs or duties change, the organisation loses up to 5 days coordinating a response across procurement, supply chain, and finance — during which margin leaks and expedite costs accumulate. This agent detects disruptions, immediately identifies the affected orders and suppliers, calculates landed cost and margin exposure, and generates a prioritised cross-team response brief — compressing 5 days of manual effort into a single day.

**Business Need:**
No single system currently connects trade event data, open order impact, margin calculations, and cross-team action tracking. Teams work in silos, pulling data manually from S/4HANA, Ariba, and IBP before any coordinated response can begin. The agent eliminates this gap by acting as an always-on coordination layer across these systems, accessible via natural language.

**Expected Value:**
- Reduce time-to-coordinate tariff disruption response from 5 days to 1 day within 3 months of go-live
- Reduce expedite costs from tariff disruptions by 25% within 3 months of go-live
- Give leadership real-time visibility into exposure, options, and actions in progress

**Product Objectives (Prioritised):**
1. Detect affected open orders, products, and suppliers immediately when a tariff event is reported
2. Quantify landed cost delta and margin exposure across the affected portfolio
3. Generate a prioritised cross-team response brief with recommended actions
4. Track and coordinate recommended actions across procurement, supply chain, and finance
5. Provide leadership with a post-event summary of exposure, decisions, and outcomes

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time-to-coordinate tariff disruption response | 5 days | 1 day | 3 months after go-live | Cross-team trade disruption response coordination | user |
| Expedite cost reduction from tariff disruptions | — | 25% reduction | 3 months after go-live | Supply chain replanning & order management | user |

---

## User Profiles & Personas

### Primary Persona: Supply Chain Planner

Maria is a 34-year-old supply chain planner responsible for maintaining inventory levels and fulfilling customer commitments for a portfolio of imported product categories. When a tariff event hits, she spends the first two days gathering data from S/4HANA and Ariba before she can even begin replanning. She is comfortable with SAP tools but frustrated by the lack of a single view that connects trade changes to open orders and customer impact. She needs to know — fast — which customer commitments are at risk, what her options are, and who she needs to loop in. Her success is measured by on-time delivery rates and the absence of expensive expedites.

### Secondary Persona: Procurement Manager

James is a 42-year-old procurement manager overseeing a supplier base with significant import exposure. When tariffs change, he needs to quickly identify which suppliers are now high-risk, which contracts need renegotiation, and whether alternative sources exist. He currently manages this through spreadsheets and email chains, which creates delays and missed opportunities to re-source before costs lock in. He wants a clear supplier risk view and the ability to initiate re-sourcing actions directly from the same tool he uses to assess the situation.

### Other User Types

- **Finance / Margin Analyst**: requires a quantified P&L impact view of landed cost changes across the affected order book
- **Trade Compliance Officer**: needs to verify product tariff classifications and available duty rate data against updated tariff schedules
- **Executive Leadership**: requires a concise post-event summary of total exposure, decisions made, and outcomes — without operational detail

---

## User Goals & Tasks

### For Maria (Supply Chain Planner):

**Goals:**
- Identify which customer commitments and open orders are at risk within hours of a tariff event, not days
- Replan inventory and supply with full visibility of the landed cost impact per order

**Key Tasks:**
- Ask the agent which open purchase orders are affected by a specific tariff change
- Review landed cost delta and margin exposure per order and route
- Generate a response brief with recommended actions for procurement and supply chain
- Track which replanning actions are in progress and who owns them

### For James (Procurement Manager):

**Goals:**
- Rapidly identify at-risk suppliers and initiate re-sourcing actions before costs are locked in
- Maintain contract and spend visibility across the affected supplier portfolio

**Key Tasks:**
- Query at-risk suppliers by risk score and import exposure
- Review alternative sourcing options surfaced by the agent
- Initiate purchase requisitions for re-sourcing actions via the agent
- Monitor procurement reporting across affected orders

---

## Product Principles

1. **Detect first, recommend second**: The agent always surfaces what is affected before suggesting what to do — planners need facts before actions.
2. **Human-in-the-loop for high-risk actions**: The agent proposes; humans approve. No re-sourcing, financial posting, or replanning action is executed autonomously.
3. **Transparent about gaps**: Where data is unavailable (tariff rate feeds, IBP replanning), the agent states the limitation clearly and routes the action to the appropriate team rather than making assumptions.
4. **Natural language first**: All interactions are conversational — users ask questions in plain language and receive structured, actionable answers without navigating multiple systems.
5. **Extensible by design**: New data sources (IBP, tariff rate feeds) can be added as APIs become available without redesigning the agent's core coordination logic.

---

## Business Context

**Current State:**
When a tariff event occurs, procurement, supply chain, and finance each run their own manual assessment independently. Procurement queries Ariba for supplier risk; supply chain pulls open orders from S/4HANA; finance calculates margin impact in spreadsheets. No single view exists. The first coordinated response meeting typically happens 3–5 days after the event — by which time margin leakage and expedite commitments have already begun.

**Strategic Alignment:**
Reducing trade disruption response time directly supports the organisation's supply chain resilience and landed cost optimisation priorities. The agent also creates the foundation for future capabilities as IBP and tariff rate feed APIs become available.

**Success Criteria:**
See the Business Metrics section above.

---

## Goals and Non-Goals

### Goals (In Scope)

- Detect affected open purchase orders, products, suppliers, and routes from S/4HANA and Ariba when a tariff event is reported
- Calculate landed cost delta and margin exposure per order across the affected portfolio
- Surface supplier risk scores and alternative sourcing options from Ariba
- Generate a prioritised cross-team response brief with recommended actions
- Track recommended actions and their owners across procurement, supply chain, and finance
- Enable trade compliance officers to query tariff classifications and available duty rate data
- Produce a post-event leadership summary of exposure, decisions, and outcomes
- Initiate purchase requisitions for re-sourcing actions via S/4HANA API

### Non-Goals (Out of Scope)

- Automated supply replanning in SAP IBP (no agent-callable API; agent surfaces recommendations for human execution)
- Automated financial postings or journal entries in SAP S/4HANA
- Live tariff rate feed integration (API not active in landscape; agent uses available master data and user-provided rates)
- Contingent workforce or Fieldglass-related capabilities
- Direct customer-facing communication or order confirmation updates

---

## Requirements

### Must-Have Requirements

**R1: Disruption Scope Query**
- **Problem to Solve**: Planners and managers have no single view of which open orders, products, and suppliers are affected when a tariff event occurs.
- **User Story**: As a supply chain planner, I need to ask the agent which open purchase orders are affected by a specific tariff or duty change so that I can immediately understand the scope of the disruption without manual data gathering.
- **Acceptance Criteria**:
  - Given a tariff change description or affected product category, when I query the agent, then I receive a prioritised list of affected open purchase orders, products, and suppliers sourced from S/4HANA and Ariba
- **Maps to Objective**: Objective 1
- **Priority Rank**: 1

**R2: Landed Cost and Margin Impact Assessment**
- **Problem to Solve**: Finance and supply chain have no fast way to calculate how a tariff change affects landed cost and margin across the live order book.
- **User Story**: As a supply chain planner or finance analyst, I need to see the landed cost delta and estimated margin exposure per order and supplier so that I can prioritise which situations require immediate action.
- **Acceptance Criteria**:
  - Given an affected order list, when I request an impact assessment, then the agent returns landed cost delta and margin exposure per order using cost and pricing data from Ariba and S/4HANA
- **Maps to Objective**: Objective 2
- **Priority Rank**: 2

**R3: Supplier Risk and Alternative Sourcing View**
- **Problem to Solve**: Procurement managers cannot quickly identify which suppliers are highest risk and whether alternative sources exist without manually searching Ariba.
- **User Story**: As a procurement manager, I need to view at-risk suppliers with their risk scores and available alternative sourcing options so that I can initiate re-sourcing decisions before costs are locked in.
- **Acceptance Criteria**:
  - Given a tariff event, when I ask for supplier risk, then the agent returns a ranked list of at-risk suppliers with risk scores from Ariba and flags any alternative suppliers available in the supplier master
- **Maps to Objective**: Objective 1 and 2
- **Priority Rank**: 3

**R4: Cross-Team Response Brief Generation**
- **Problem to Solve**: No structured, prioritised action brief exists after a tariff event — each team creates its own plan in isolation.
- **User Story**: As a supply chain planner or procurement manager, I need the agent to generate a cross-team response brief with prioritised recommended actions so that procurement, supply chain, and finance can respond in a coordinated way from a single source of truth.
- **Acceptance Criteria**:
  - Given a completed impact assessment, when I request a response brief, then the agent produces a structured document with prioritised actions (re-route, re-source, expedite, reprice) assigned to the relevant team
- **Maps to Objective**: Objective 3
- **Priority Rank**: 4

**R5: Action Tracking and Coordination**
- **Problem to Solve**: After a response brief is generated, there is no mechanism to track which actions are in progress and who owns them.
- **User Story**: As any user, I need to track which recommended actions are in progress and see who owns each one so that response coordination does not rely on manual follow-up and email chains.
- **Acceptance Criteria**:
  - Given a response brief, when I ask for a status update, then the agent returns the current state of each recommended action and its assigned owner
- **Maps to Objective**: Objective 4
- **Priority Rank**: 5

**R6: Purchase Requisition Initiation for Re-Sourcing**
- **Problem to Solve**: Initiating a re-sourcing purchase requisition requires navigating S/4HANA manually, adding delay after a sourcing decision is made.
- **User Story**: As a procurement manager, I need to initiate a purchase requisition for a re-sourcing action directly via the agent so that re-sourcing decisions are acted on immediately.
- **Acceptance Criteria**:
  - Given a re-sourcing decision, when I instruct the agent to create a purchase requisition, then a requisition is created in S/4HANA via the purchase requisition API and confirmation is returned
- **Maps to Objective**: Objective 3 and 4
- **Priority Rank**: 6

**R7: Tariff Classification Query**
- **Problem to Solve**: Trade compliance officers have no fast way to check product tariff classifications against updated duty schedules during a disruption event.
- **User Story**: As a trade compliance officer, I need to query tariff classifications and available duty rate data for affected products so that I can confirm compliance exposure during a tariff event.
- **Acceptance Criteria**:
  - Given a product or order, when I ask for tariff classification, then the agent returns available classification data from S/4HANA and flags where duty rate data is not active
- **Maps to Objective**: Objective 1
- **Priority Rank**: 7

**R8: Leadership Post-Event Summary**
- **Problem to Solve**: Leadership has no structured post-event view of total exposure, actions taken, and outcomes.
- **User Story**: As an executive, I need a concise post-event summary of total margin exposure, decisions made, and outcomes so that I can assess the effectiveness of the response and report to the board.
- **Acceptance Criteria**:
  - Given a completed disruption response cycle, when I request a summary, then the agent produces a structured executive brief covering total exposure, actions taken, and quantified outcomes
- **Maps to Objective**: Objective 5
- **Priority Rank**: 8

---

## Non-Functional Requirements

### Performance
- **Latency**: Agent responses to disruption scope and impact queries should complete within 15 seconds at the 95th percentile
- **Throughput**: Support concurrent use by up to 20 planners and managers during a peak disruption event

### Reliability
- **Availability**: 99% uptime during business hours
- **Fallback**: If an upstream API (S/4HANA or Ariba) is unavailable, the agent informs the user of the limitation and returns partial results from available sources rather than failing silently

### Explainability
- **Traceability**: All impact calculations must reference the source orders and cost data used, so users can verify results
- **Decision Logging**: All agent-initiated actions (purchase requisition creation, response brief generation) are logged with timestamp, user, and inputs
- **Uncertainty Communication**: Where data is incomplete (e.g., duty rate not available), the agent explicitly states the limitation and quantifies the affected portion of the calculation

---

## Solution Architecture

**Architecture Overview:**
A Python-based AI agent following the A2A (Agent-to-Agent) protocol, deployed on SAP BTP. The agent interacts with users via natural language, calls SAP S/4HANA and SAP Ariba APIs directly using available ORD IDs, and maintains action tracking state across a disruption response cycle. No pre-built MCP servers exist for the target APIs; the agent calls them directly.

**Key Components:**
- **Trade Disruption Agent (Python, A2A)**: core reasoning and coordination layer; handles user queries, orchestrates API calls, calculates impact, generates response briefs
- **S/4HANA Connector**: calls supplier activity, purchase order, and purchase requisition APIs
- **Ariba Connector**: calls risk exposure, cost breakdown, pricing, and procurement reporting APIs
- **Action Tracker**: maintains in-session state of recommended actions, owners, and status across a disruption cycle

**Integration Points:**
- SAP S/4HANA: `API_SUPPLIER_ACTIVITY_SRV` (purchase orders and supplier activity, read), `CE_PURCHASEREQUISITION_0001` and `API_PURCHASEREQ_PROCESS_SRV` (purchase requisition creation, write)
- SAP Ariba: `cost_breakdown`, `pricing` (cost and margin data, read), `risk_exposure`, `risk_engagement` (supplier risk, read), `mds_search` (supplier master, read), `procurement_reporting_details` (spend and order reporting, read)

**Deployment Environment:**
SAP BTP — single environment. Data access is scoped to the authenticated user's authorisations in S/4HANA and Ariba.

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with named extension points so that new capabilities can be added without redesigning the core coordination logic:
- **Tariff rate feed extension point**: when a live tariff rate API becomes active in the landscape, it can be registered as an additional tool without modifying impact calculation logic
- **IBP replanning extension point**: when SAP IBP exposes an agent-callable API, replanning recommendations can transition from human-routed to agent-initiated
- **Additional source systems**: new data sources (e.g., logistics track-and-trace, customs clearance status) can be added as tools following the same connector pattern

**Business Step Instrumentation:**
All five milestones are instrumented with structured log statements (see Milestones section). Log format: `[MILESTONE_ID].[achieved|missed]: [description]`. Logs are emitted at the point each milestone is reached or determined to have been skipped, enabling production monitoring and post-event diagnostics.

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent with human-in-the-loop for write actions

**Actions the agent performs without human approval:**
- Query open purchase orders and supplier activity from S/4HANA
- Query supplier risk scores and cost data from Ariba
- Calculate landed cost delta and margin exposure
- Generate cross-team response brief and leadership summary
- Surface tariff classification data and flag compliance gaps

**Actions that require human review or approval:**
- Create purchase requisition in S/4HANA (user must confirm before agent submits)
- Mark a recommended action as assigned to an owner (user confirms the assignment)
- All supply replanning actions in IBP (agent recommends; planner executes in IBP directly)

**Model / engine used:** SAP Generative AI Hub (GPT-4o or equivalent LLM available on BTP at deployment time)

**Knowledge & data sources accessed:**
- SAP S/4HANA: open purchase orders, supplier activity, purchase requisitions — owned by Procurement Operations
- SAP Ariba: supplier risk scores, cost breakdown, pricing, procurement reporting — owned by Procurement Operations and Finance
- User-provided tariff event context: user supplies tariff change description or affected commodity codes as conversation input

**Guardrails & fail-safes:**
- The agent never posts financial entries or modifies accounting records autonomously
- All purchase requisition creation requires explicit user confirmation before API submission
- If confidence in an impact calculation is low due to missing data, the agent states the limitation and flags the affected orders for manual review
- If an upstream API returns an error, the agent informs the user and continues with available data rather than failing the entire response

---

## Governance, Risk & Compliance

**Data Handling:**
- The agent accesses only transactional procurement and supply chain data; no personal employee data is processed
- All API calls are scoped to the authenticated user's existing SAP authorisations — the agent does not elevate privileges
- No data is persisted outside the user's BTP session beyond structured action tracking state

**Compliance Frameworks:**
- Trade compliance queries surface available classification data; final compliance decisions remain with the Trade Compliance Officer
- Purchase requisitions created by the agent follow the same approval workflow as manually created requisitions in S/4HANA

**Approval Flows:**
- Purchase requisition creation: user confirms in-conversation before agent submits to S/4HANA API
- Re-sourcing and replanning recommendations: human decision required before any system action

---

## Goals and Non-Goals

_(See Goals and Non-Goals section above.)_

---

## Milestones

### M1: Disruption Detected

- **Description**: A tariff or duty change event is identified and affected open purchase orders, products, and suppliers are surfaced from S/4HANA and Ariba.
- **Achieved when**: The agent returns a confirmed list of affected orders, products, and suppliers in response to a user-reported tariff event.
- **Log on achievement**: `M1.achieved: disruption scope identified — [N] orders, [N] suppliers, [N] products surfaced from S/4HANA and Ariba`
- **Log on miss**: `M1.missed: disruption scope query did not complete — API unavailable or no matching orders found`

### M2: Impact Assessed

- **Description**: Landed cost delta, margin exposure, and inventory risk are quantified across all affected orders and routes.
- **Achieved when**: The agent returns a landed cost delta and margin exposure calculation covering all affected orders identified in M1.
- **Log on achievement**: `M2.achieved: impact assessment complete — total landed cost delta [amount], margin exposure [amount] across [N] orders`
- **Log on miss**: `M2.missed: impact assessment incomplete — cost or pricing data unavailable for [N] orders`

### M3: Response Brief Generated

- **Description**: A cross-team action brief with prioritised recommendations is produced for procurement, supply chain, and finance.
- **Achieved when**: The agent produces a structured response brief with at least one prioritised action per affected team.
- **Log on achievement**: `M3.achieved: response brief generated — [N] recommended actions across [N] teams`
- **Log on miss**: `M3.missed: response brief not generated — impact assessment (M2) did not complete or user did not request brief`

### M4: Actions Coordinated

- **Description**: Recommended actions (re-route, re-source, expedite, reprice) are tracked and assigned across teams via the agent.
- **Achieved when**: At least one recommended action from the response brief has been assigned to an owner and is tracked as in-progress.
- **Log on achievement**: `M4.achieved: action coordination active — [N] actions assigned, [N] pending`
- **Log on miss**: `M4.missed: no actions assigned — response brief generated but no actions confirmed by user`

### M5: Leadership Visibility

- **Description**: A post-event summary of exposure, decisions made, and outcomes is available for executive review.
- **Achieved when**: The agent produces a post-event executive summary covering total exposure, actions taken, and quantified outcomes.
- **Log on achievement**: `M5.achieved: leadership summary produced — total exposure [amount], [N] actions completed, [N] outcomes quantified`
- **Log on miss**: `M5.missed: leadership summary not produced — disruption response cycle did not reach closure or user did not request summary`

---

## Risks, Assumptions, and Dependencies

### Risks

- **Incomplete tariff rate data**: Tariff classification and live duty rate APIs are not active. Impact calculations depend on S/4HANA master data quality and user-provided rates; accuracy may be limited for novel tariff events.
- **IBP integration gap**: Supply replanning remains a manual step; agent recommendations do not automatically update supply plans, creating a potential lag between recommendation and execution.
- **Cross-system data latency**: Depending on replication frequency between Ariba and S/4HANA, the first post-event impact assessment may not reflect the most recent order changes.

### Assumptions

- SAP S/4HANA, Ariba, IBP, and GTS are all live and accessible via the available API ORD IDs confirmed in the fit-gap analysis.
- Users have existing SAP authorisations that permit the agent to query the data sources in scope; no new authorisation roles are required for read operations.
- The organisation will provide tariff event context (commodity codes or product categories) as input to the agent; the agent does not independently source tariff schedule updates.

### Dependencies

- SAP BTP environment provisioned with Generative AI Hub access
- S/4HANA and Ariba API connectivity via SAP Business Connector or equivalent
- User authentication and authorisation aligned with existing SAP role model

---

## Open Questions

- Will the agent need to support multiple company codes or legal entities, or is scope limited to a single entity initially?
- Is there a preferred action-tracking mechanism for M4 (e.g., integration with SAP Task Centre, or in-session state only)?
- Should the response brief be exportable (PDF, email) or is in-conversation output sufficient for go-live?
