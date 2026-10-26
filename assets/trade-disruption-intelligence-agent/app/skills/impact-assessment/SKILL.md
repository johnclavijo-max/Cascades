---
name: impact-assessment
description: |
  [WHAT] Guides the agent through calculating landed cost delta and margin exposure across affected purchase orders using Ariba cost breakdown and pricing data.
  [WHEN] Use when the user asks for cost impact, margin exposure, financial impact, or landed cost analysis of a tariff disruption event. Always run after disruption-detection has produced an affected order list.
  [NOT] Do not use before disruption-detection has identified affected orders. Do not use for supplier risk scoring — use supplier-risk skill.
  Key terms: landed cost, cost breakdown, margin exposure, duty delta, cost impact, financial exposure.
allowed-tools:
  - cost_breakdown_query
  - pricing_query
  - margin_impact_calculator
metadata:
  version: 1.0.0
  tags:
    - landed-cost
    - margin
    - impact
    - finance
---

# Impact Assessment Skill

## Purpose

This skill calculates the landed cost delta and margin exposure for each affected purchase order identified in the disruption detection step. It uses Ariba cost breakdown and pricing data to quantify the financial impact of a tariff change, producing a per-order and portfolio-level exposure summary.

## When to use

- After disruption-detection has produced an affected order list (M1 complete)
- User asks "what is our cost/margin impact?" or "how much are we exposed?"
- Milestone M2: quantify landed cost delta and margin exposure

## When NOT to use

- Before disruption-detection — an affected order list is required as input
- User asks for supplier risk — use `supplier-risk` skill
- User asks for recommended actions — use `response-coordination` skill

---

## Instructions

### Step 1 — Confirm the duty rate delta with the user

Before calculating, confirm the duty rate change to apply:

| Input | Description | Example |
|---|---|---|
| Duty rate delta | Percentage point increase in duty | "+25 percentage points" |
| Currency | Currency for exposure calculations | "USD" |
| Include freight in landed cost? | Whether to include shipping cost changes | "Yes, include 15% freight surcharge" |

If the user cannot provide the exact duty delta, ask for their best estimate and flag that the calculation is based on an estimated rate.

### Step 2 — Retrieve cost breakdown per affected order

Call `cost_breakdown_query` for each affected order from the disruption scope. Extract:
- Unit price (base cost)
- Current duty amount
- Freight and other charges
- Total current landed cost per unit

If cost breakdown data is missing for an order, flag it explicitly — do not skip it from the portfolio total without noting it.

### Step 3 — Retrieve baseline pricing

Call `pricing_query` for the affected materials to confirm the current baseline price per unit used in margin calculations.

### Step 4 — Calculate impact

Call `margin_impact_calculator` with:
- Cost breakdown data per order (from Step 2)
- Pricing data per material (from Step 3)
- User-confirmed duty rate delta (from Step 1)

The calculator returns:
- New landed cost per order
- Margin delta per order (in currency and as %)
- Total portfolio exposure
- List of orders with incomplete cost data

### Step 5 — Present results

Present as a two-part summary:

**Part 1 — Per-order impact:**
```
Landed Cost Impact — [Tariff Event]
──────────────────────────────────────────────────────────────────
Order ID | Supplier | Current LC | New LC | Delta | Margin Impact | Data Complete?
──────────────────────────────────────────────────────────────────
[rows ranked by margin impact, highest first]
⚠ [N] orders have incomplete cost data — flagged for manual review
```

**Part 2 — Portfolio summary:**
```
Total Portfolio Exposure
  Affected orders with full data:  [N]  Total exposure: [amount]
  Affected orders, incomplete data: [N]  Estimated additional exposure: [amount]*
  * Based on average landed cost delta from orders with full data
```

After presenting, log: `M2.achieved: impact assessment complete — total landed cost delta [amount], margin exposure [amount] across [N] orders`

If more than 30% of orders have incomplete data, also log: `M2.missed: impact assessment incomplete — cost or pricing data unavailable for [N] orders`

### Step 6 — Offer next steps

After presenting the impact, offer:
- "Generate a cross-team response brief with recommended actions" → triggers response-coordination skill
- "Review supplier risk and alternative sourcing options" → triggers supplier-risk skill

---

## Gotchas

- **Never omit incomplete-data orders from the portfolio total** — always include them with an explicit flag and an estimated contribution based on average delta. Silently dropping them understates exposure.
- **Duty rate delta must be confirmed by the user** — never assume or derive a duty rate from S/4HANA or Ariba data. The rate change is an external event input.
- **Freight surcharges** — if the user mentions shipping cost changes alongside duty changes, include them in the landed cost delta. Ask explicitly if unsure.
