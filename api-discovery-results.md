# API Discovery Results — Trade Disruption Intelligence Agent

Generated during specification phase.

## SAP S/4HANA APIs

| API Name | ORD ID | Type | Spec File | Usage |
|---|---|---|---|---|
| Purchase Order | `sap.s4:apiResource:CE_PURCHASEORDER_0001:v1` | OData | `specification/trade-disruption-intelligence-agent/api-specs/CE_PURCHASEORDER_0001.edmx` | Disruption scope detection, tariff classification query |
| Purchase Requisition | `sap.s4:apiResource:CE_PURCHASEREQUISITION_0001:v1` | OData | `specification/trade-disruption-intelligence-agent/api-specs/CE_PURCHASEREQUISITION_0001.edmx` | Re-sourcing purchase requisition creation |
| Procurement-Related Activity | `sap.s4:apiResource:API_SUPPLIER_ACTIVITY_SRV:v1` | OData | `specification/trade-disruption-intelligence-agent/api-specs/API_SUPPLIER_ACTIVITY_SRV.edmx` | Supplier activity and open commitment status |

## SAP Ariba APIs

| API Name | ORD ID | Type | Spec File | Usage |
|---|---|---|---|---|
| Risk Exposure API | `sap.aribas4:apiResource:risk_exposure:v3` | REST | `specification/trade-disruption-intelligence-agent/api-specs/risk_exposure_v3.json` | Supplier risk scoring |
| Supplier Risk Engagements API | `sap.aribas4:apiResource:risk_engagement:v2` | REST | `specification/trade-disruption-intelligence-agent/api-specs/risk_engagement_v2.json` | Active risk mitigation engagement status |
| Cost Breakdown Data Extraction API | `sap.aribas4:apiResource:cost_breakdown:v1` | REST | `specification/trade-disruption-intelligence-agent/api-specs/cost_breakdown_v1.json` | Landed cost component breakdown per order |
| Pricing API for Product Sourcing | `sap.aribas4:apiResource:pricing:v1` | REST | `specification/trade-disruption-intelligence-agent/api-specs/pricing_v1.json` | Baseline landed cost per unit |
| Operational Reporting for Procurement | `sap.aribabuyer:apiResource:procurement_reporting_details:v2` | REST | `specification/trade-disruption-intelligence-agent/api-specs/procurement_reporting_details_v2.json` | Spend visibility, alternative supplier sourcing |

## APIs Not Available (Gaps noted in PRD)

| API Name | Status | Notes |
|---|---|---|
| Margin Health Indicators | Not active in landscape | Agent uses cost_breakdown + pricing to derive margin exposure |
| IBP Replanning API | No agent-callable API surface | Agent surfaces replanning recommendations for human execution in IBP |
| Live Tariff Rate Feed | Not active in landscape | Agent relies on S/4HANA master data and user-provided duty rates |
| SAP GTS Tariff Classification Feed | Not active in landscape | Agent surfaces available commodity code fields from S/4HANA PO data |
