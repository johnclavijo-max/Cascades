# Trade Disruption Intelligence Agent

## Business challenge

Sudden changes in tariffs, duties, and cross-border shipping costs are increasing landed cost on imported products and creating disruption across procurement, supply chain, and finance. The organisation needs to quickly understand which products, suppliers, routes, and open orders are affected, how this impacts margin, inventory, and customer commitments, and where the current response process is too slow or manual. The goal is to detect disruptions, assess business impact, and coordinate the right response across teams to reduce margin leakage, avoid order delays and expensive expedites, improve response time to trade disruptions, and give leaders clear visibility into risks, options, and actions in progress.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time-to-coordinate tariff disruption response | 5 days | 1 day | 3 months after go-live | Cross-team trade disruption response coordination | user |
| Expedite cost reduction from tariff disruptions | — | 25% reduction | 3 months after go-live | Supply chain replanning & order management | user |

## Key Milestones

1. **Disruption detected** — A tariff or duty change event is identified and affected open purchase orders, products, and suppliers are surfaced automatically.
2. **Impact assessed** — Landed cost delta, margin exposure, and inventory risk are quantified across all affected orders and routes.
3. **Response brief generated** — A cross-team action brief with prioritised recommendations is produced for procurement, supply chain, and finance.
4. **Actions coordinated** — Recommended actions (re-route, re-source, expedite, reprice) are tracked and assigned across teams via the agent.
5. **Leadership visibility** — A post-event summary of exposure, decisions made, and outcomes is available for executive review.

## Business Architecture (RBA)

### End-to-End Process

Source to Pay (E2E)

### Process Hierarchy

```
Source to Pay (E2E)
└── Manage Suppliers and Collaboration
    └── Manage international trade (BPS-401)
        └── Manage customs declarations and processes
        └── Manage trade product classification
└── Plan to Optimize Fulfillment
    └── Monitor and optimize supply chain performance (BPS-340)
        └── Control and monitor supply chain
    └── Plan inventory and supply (BPS-339)
        └── Generate collaborative supply plan
└── Source to Contract
    └── Manage procurement contracts (BPS-328)
        └── Manage procurement contracts
```

### Summary

Sudden tariff and duty changes map primarily to Source to Pay — anchored by Manage International Trade (customs, duties, product classification) — with cross-cutting impact on supply chain monitoring and inventory replanning, and downstream effects on procurement contracts and landed cost management.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|--------------------|--------------------|--------------------|------|---------------------|
| Detect affected open purchase orders when tariff changes | SAP S/4HANA Cloud, SAP Ariba | `sap.s4:apiResource:API_SUPPLIER_ACTIVITY_SRV:v1` | — | — | — | — | No | Purchase order and supplier activity available via S/4HANA API |
| Assess landed cost and margin impact per order/product | SAP S/4HANA, SAP Ariba | `sap.aribas4:apiResource:cost_breakdown:v1`, `sap.aribas4:apiResource:pricing:v1` | — | — | — | — | Maybe | Cost breakdown and pricing APIs available; real-time margin health API not active in landscape |
| Identify at-risk suppliers and alternative sourcing options | SAP Ariba | `sap.aribas4:apiResource:risk_exposure:v3`, `sap.aribas4:apiResource:risk_engagement:v2`, `sap.aribabuyer:apiResource:mds_search:v1` | — | — | — | — | No | Risk exposure and supplier master data APIs available via Ariba |
| Monitor and replan inventory/supply in response to disruption | SAP IBP | — | — | — | — | — | Yes | SAP IBP is in landscape but no API surface available for agent invocation; agent will flag replanning recommendations for human action in IBP |
| Coordinate response actions across procurement, supply chain, finance | Custom agent capability | — | — | — | — | — | Yes | No standard SAP product covers cross-team coordination via natural language; agent must orchestrate this |
| Trade compliance — verify tariff classifications and duty rates | SAP GTS, SAP S/4HANA | — | — | — | — | — | Yes | GTS is in landscape; tariff classification and tariff rate feed APIs are not active — agent will surface classification data from S/4HANA where available |
| Procurement reporting and spend visibility across affected orders | SAP Ariba | `sap.aribabuyer:apiResource:procurement_reporting_details:v2` | — | — | — | — | No | Operational reporting API available |
| Purchase requisition management for re-sourcing actions | SAP S/4HANA | `sap.s4:apiResource:CE_PURCHASEREQUISITION_0001:v1`, `sap.s4:apiResource:API_PURCHASEREQ_PROCESS_SRV:v1` | — | — | — | — | No | Purchase requisition APIs available for agent-initiated re-sourcing actions |

### Key findings

- SAP S/4HANA (with GTS), SAP Ariba, and SAP IBP are all confirmed in the customer landscape, providing a strong foundation for procurement, trade, and supply data.
- No pre-built MCP servers exist for any of the relevant APIs — the agent will call APIs directly using available ORD IDs.
- Real-time tariff rate feeds, active margin health indicators, and inventory availability APIs are not active in the landscape; the agent will work with available transactional data and flag gaps requiring human confirmation.
- SAP IBP is available for supply replanning but lacks an agent-callable API surface; the agent will generate replanning recommendations that planners execute in IBP directly.
- The largest gap is cross-team coordination — no standard SAP product provides an AI-driven response orchestration layer; this is the primary value the custom agent delivers.
- SAP Fieldglass (VMS) capabilities identified in fit-gap are not relevant to this scenario (no contingent workforce dimension) and have been excluded.

## Recommendations

### Trade Disruption Intelligence Agent

#### Executive Summary

AI agent that detects tariff events, assesses impact, and coordinates cross-team response via S/4HANA and Ariba.

#### Recommended Solution

A Python-based AI agent (A2A protocol) deployed on SAP BTP that continuously monitors for tariff and duty disruption signals, queries live procurement and supplier data from SAP S/4HANA and SAP Ariba, calculates landed cost and margin exposure across open orders, and generates prioritised response recommendations for supply chain planners, procurement managers, and finance leads. The agent uses natural language interaction, enabling users to ask questions like "Which open orders are affected by the new US tariff on steel imports?" or "What is our total margin exposure this week?" and receive structured, actionable answers with recommended next steps.

#### Problem Statement

When tariff changes occur, the organisation takes up to 5 days to coordinate a response because no single system connects trade event data, open order impact, margin calculations, and cross-team action tracking. This delay creates margin leakage and expensive expedite costs.

#### Affected User Roles

- Supply chain planners — primary users; replan inventory and customer commitments
- Procurement managers — assess supplier and PO risk, initiate re-sourcing
- Finance / margin analysts — quantify P&L impact of landed cost changes
- Trade compliance officers — verify import classifications against updated duty rates
- Executive leadership — receive visibility into exposure, options, and actions in flight

#### Important factors

##### Real-time data access across S/4HANA and Ariba
The agent connects to live transactional data via available OData and REST APIs, ensuring impact assessments reflect the current order book, not last month's report.

##### Natural language coordination layer
Supply chain planners and procurement managers interact with the agent in plain language, removing the need for manual data gathering across multiple systems before a response decision can be made.

##### Gap management through human-in-the-loop
Where APIs are not active (tariff rate feeds, IBP replanning), the agent surfaces the gap, provides its best available analysis, and routes the remaining action to the appropriate human team — avoiding silent errors.

#### Potential risks

##### Incomplete tariff rate data
Tariff classification and live duty rate APIs are not active in the landscape. The agent will rely on S/4HANA master data and user-provided tariff information; accuracy of impact calculations depends on data quality in the source systems.

##### IBP integration gap
SAP IBP is in the landscape but has no agent-callable API. Supply replanning remains a manual step for planners — the agent provides recommendations but cannot execute replanning automatically.

##### Cross-system data latency
Open order and cost data may not be real-time in all cases (depending on replication frequency between Ariba and S/4HANA), which could affect the accuracy of the first impact assessment after a tariff event.

#### Recommended solution category

AI Agent

#### Intent fit
82%
