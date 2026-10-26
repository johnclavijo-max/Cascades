---
name: supplier-risk
description: |
  [WHAT] Guides the agent through assessing supplier risk exposure and identifying alternative sourcing options for suppliers affected by a trade disruption.
  [WHEN] Use when the user asks about supplier risk, at-risk suppliers, supplier alternatives, or re-sourcing options related to a trade disruption.
  [NOT] Do not use for cost or margin calculations — use impact-assessment skill. Do not use for generating the full response brief — use response-coordination skill.
  Key terms: supplier risk, risk score, risk exposure, risk engagement, alternative supplier, re-sourcing.
allowed-tools:
  - supplier_risk_exposure
  - supplier_risk_engagement
  - alternative_supplier_query
metadata:
  version: 1.0.0
  tags:
    - supplier
    - risk
    - ariba
    - sourcing
---

# Supplier Risk Assessment Skill

## Purpose

This skill assesses risk exposure for suppliers affected by a trade disruption, surfaces active risk mitigation engagements, and identifies alternative sourcing options. It gives procurement managers the information they need to decide whether to continue, monitor, escalate, or re-source from each affected supplier.

## When to use

- User asks "which suppliers are at risk?" or "are there alternative suppliers?"
- After disruption detection has identified affected suppliers (M1 complete)
- As part of generating a response brief (in parallel with impact assessment)

## When NOT to use

- Before disruption detection — a list of affected suppliers is required as input
- User asks for financial exposure — use `impact-assessment` skill
- User asks for a full action plan — use `response-coordination` skill

---

## Instructions

### Step 1 — Query risk exposure per affected supplier

Call `supplier_risk_exposure` with the list of affected supplier IDs from the disruption detection output. For each supplier, retrieve:
- Overall risk score (numeric, 0–100)
- Primary risk category (e.g., financial, operational, compliance, geographic)
- Risk trend direction (improving / stable / deteriorating)

### Step 2 — Query active risk engagements

Call `supplier_risk_engagement` for each high-risk supplier (risk score > 60). Retrieve:
- Active mitigation engagement title and status
- Engagement owner
- Any open findings or unresolved items relevant to trade compliance or supply continuity

### Step 3 — Query alternative suppliers

Call `alternative_supplier_query` with the material categories or commodity codes of the affected orders. Retrieve:
- Suppliers who supply the same material categories and are not currently flagged as high-risk
- Rank by existing spend relationship (preferred suppliers first)

### Step 4 — Determine recommended action per supplier

For each affected supplier, assign a recommended action based on risk score:

| Risk Score | Trend | Recommended Action |
|---|---|---|
| 0–39 | Any | Continue — monitor in next standard review |
| 40–59 | Improving or stable | Monitor — schedule a check-in within 30 days |
| 40–59 | Deteriorating | Escalate — engage supplier on mitigation plan |
| 60–79 | Any | Escalate — open formal risk engagement if none exists |
| 80–100 | Any | Re-source — initiate alternative sourcing immediately |

If no risk data is available for a supplier, flag it as "data unavailable" and recommend escalation as a precaution.

### Step 5 — Present supplier risk summary

```
Supplier Risk Summary — [Tariff Event]
──────────────────────────────────────────────────────────────────
Supplier         | Risk Score | Category      | Trend        | Recommendation
──────────────────────────────────────────────────────────────────
[rows ranked by risk score, highest first]
──────────────────────────────────────────────────────────────────

Alternative sourcing options identified:
  Material: [category] → Alternatives: [supplier names, ranked by spend]
```

### Step 6 — Offer next steps

After presenting, offer:
- "Add re-sourcing actions to the response brief" → passes recommendations to response-coordination
- "Create a purchase requisition for an alternative supplier" → routes to response-coordination skill

---

## Gotchas

- **No risk data does not mean low risk** — always flag suppliers with no Ariba risk data as "data unavailable" and recommend escalation as a precaution. Never imply they are safe.
- **Alternative suppliers are candidates, not approvals** — always present alternatives as options for procurement review. The agent does not approve new suppliers.
- **Risk score thresholds are guidance, not absolute rules** — if the user's organisation uses different thresholds, respect what the user tells you and adjust the recommendations accordingly.
