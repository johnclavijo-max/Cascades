---
name: disruption-detection
description: |
  [WHAT] Guides the agent through scoping a tariff or duty disruption event by identifying all affected open purchase orders, products, and suppliers from SAP S/4HANA.
  [WHEN] Use when the user describes a tariff change, duty increase, cross-border shipping cost change, or asks which orders or suppliers are affected by a trade event.
  [NOT] Do not use for landed cost calculations — use impact-assessment skill instead. Do not use for supplier risk scoring — use supplier-risk skill instead.
  Key terms: tariff, duty, affected orders, disruption scope, commodity code, HS code, open POs.
allowed-tools:
  - disruption_scope
  - supplier_activity_query
metadata:
  version: 1.0.0
  tags:
    - trade
    - tariff
    - disruption
    - purchase-orders
---

# Disruption Detection Skill

## Purpose

This skill guides the agent through detecting the scope of a tariff or duty disruption event. It produces a prioritised list of affected open purchase orders, products, and suppliers so that downstream impact assessment and response planning can begin immediately.

## When to use

- User describes a tariff change, duty rate increase, or cross-border shipping cost change
- User asks "which orders are affected by [tariff event]?"
- User asks "which suppliers are impacted by [trade change]?"
- Beginning of a new trade disruption response cycle (Milestone M1)

## When NOT to use

- User asks for margin or cost impact — use `impact-assessment` skill
- User asks for supplier risk scores — use `supplier-risk` skill
- User asks for a response brief — use `response-coordination` skill

---

## Instructions

### Step 1 — Gather event context from the user

Before querying any system, confirm the following inputs with the user. If any are missing, ask explicitly — do not assume defaults.

| Input | Description | Example |
|---|---|---|
| Tariff event description | What changed (tariff, duty, surcharge, etc.) | "25% tariff on steel imports from China" |
| Affected commodity / product category | HS codes, material groups, or product names | "HS 7208, steel flat-rolled products" |
| Effective date | When the change takes effect | "2026-01-15" |
| Scope (optional) | Specific plants, countries, or supplier groups to filter | "All US plants, suppliers in CN" |

If the user cannot provide commodity codes, ask for product names or material groups and use those as filter terms.

### Step 2 — Query open purchase orders from S/4HANA

Call the `disruption_scope` tool with the gathered inputs:
- Pass the commodity codes or product category as the primary filter
- If a plant or country scope was provided, pass it as an additional filter
- Request open orders only (delivery date in the future, not yet goods-receipted)

The tool returns a list of affected orders. If the list is empty:
1. Confirm with the user that the commodity codes or product categories are correct
2. Broaden the search to related material groups if the user agrees
3. If still empty, explicitly state that no affected open orders were found and log `M1.missed`

### Step 3 — Query supplier activity for affected suppliers

From the affected order list returned in Step 2, extract the unique supplier IDs. Call `supplier_activity_query` with these supplier IDs to retrieve:
- Current engagement status per supplier
- Open commitments (quantities and values) per supplier
- Any active dispute or escalation flags

### Step 4 — Prioritise and present the affected order list

Rank the affected orders by:
1. **Value at risk** (order value × estimated duty rate change) — highest first
2. **Delivery date** — earliest delivery dates within the next 30 days flagged as urgent

Present the result as a structured table:

```
Affected Orders — [Tariff Event Description]
──────────────────────────────────────────────────────────────────
Order ID | Supplier       | Material        | Qty | Value  | Delivery | Priority
──────────────────────────────────────────────────────────────────
[rows from tool output, ranked by value at risk]
──────────────────────────────────────────────────────────────────
Total affected: [N] orders | [N] suppliers | Total value: [amount]
```

After presenting, log: `M1.achieved: disruption scope identified — [N] orders, [N] suppliers, [N] products surfaced from S/4HANA`

### Step 5 — Offer next steps

After presenting the affected order list, offer:
- "Assess landed cost and margin impact across these orders" → triggers impact-assessment skill
- "Review supplier risk and alternative sourcing options" → triggers supplier-risk skill
- "Both" → run both in sequence

---

## Gotchas

- **Empty order list is not an error** — if no orders match, state this clearly and confirm the commodity codes are correct before concluding. Do not skip M1 logging.
- **Commodity codes vs material groups** — S/4HANA may store tariff classification at material level, not always on the PO line. If commodity codes return no results, try material group or product hierarchy filters.
- **Open orders only** — always filter for orders that are not yet fully goods-receipted. Closed orders are not at risk and should not appear in the scope list.
