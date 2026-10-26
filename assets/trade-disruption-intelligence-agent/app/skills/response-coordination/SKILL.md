---
name: response-coordination
description: |
  [WHAT] Guides the agent through generating a cross-team response brief with prioritised recommended actions and tracking those actions across procurement, supply chain, and finance.
  [WHEN] Use when the user asks for a response brief, recommended actions, an action plan, or wants to track what is being done about a disruption.
  [NOT] Do not use before impact-assessment has quantified exposure. Do not use for supplier risk assessment — use supplier-risk skill.
  Key terms: response brief, recommended actions, re-source, re-route, reprice, expedite, action tracking, coordination.
allowed-tools:
  - response_brief_generator
  - action_tracker
  - create_purchase_requisition
metadata:
  version: 1.0.0
  tags:
    - response
    - coordination
    - actions
    - brief
---

# Response Coordination Skill

## Purpose

This skill generates a structured cross-team response brief from the impact assessment output and tracks recommended actions across procurement, supply chain, and finance. It is the primary coordination layer for a trade disruption response cycle.

## When to use

- After impact-assessment has produced exposure data (M2 complete)
- User asks "what should we do?" or "generate a response plan"
- User wants to assign, track, or update actions
- Milestone M3: generate response brief; Milestone M4: coordinate actions

## When NOT to use

- Before impact assessment — an exposure summary is required
- User asks for cost calculations — use `impact-assessment` skill

---

## Instructions

### Step 1 — Generate the response brief

Call `response_brief_generator` with the impact assessment output. The generator produces a prioritised list of recommended actions. Each action must include:

| Field | Description |
|---|---|
| Action type | re-route / re-source / reprice / expedite |
| Description | Specific action (e.g., "Re-source material X from supplier Y") |
| Affected orders | Order IDs this action addresses |
| Responsible team | Procurement / Supply Chain / Finance |
| Estimated impact | Cost saving or margin recovery if action is taken |
| Status | "pending" (initial) |

### Step 2 — Present the response brief

Present the brief as a prioritised action table, grouped by team:

```
Cross-Team Response Brief — [Tariff Event]
Generated: [date/time]
──────────────────────────────────────────────────────────────────
PROCUREMENT ACTIONS
  [P1] Re-source: [description] | Orders: [IDs] | Est. saving: [amount] | Status: Pending
  [P2] ...

SUPPLY CHAIN ACTIONS
  [S1] Re-route: [description] | Orders: [IDs] | Est. saving: [amount] | Status: Pending
  [S2] ...

FINANCE ACTIONS
  [F1] Reprice: [description] | Orders: [IDs] | Est. impact: [amount] | Status: Pending
──────────────────────────────────────────────────────────────────
Total recommended actions: [N] | Estimated total recovery: [amount]
```

After generating, log: `M3.achieved: response brief generated — [N] recommended actions across [N] teams`

### Step 3 — Invite action assignment

After presenting the brief, ask the user if they want to assign any actions to owners:

> "Would you like to assign any of these actions to owners and start tracking them? If so, tell me which action and who should own it."

For each assignment:
1. Confirm the action ID and owner name with the user before recording
2. Call `action_tracker` to record the assignment with status "in-progress"
3. Confirm back to the user with the updated action list

Never infer ownership — always ask explicitly.

When at least one action is assigned, log: `M4.achieved: action coordination active — [N] actions assigned, [N] pending`

### Step 4 — Handle purchase requisition requests

If the user approves a re-sourcing action and wants to initiate a purchase requisition:
1. Ask the user to confirm: material, quantity, preferred supplier, required delivery date
2. Display the full requisition details and ask for explicit confirmation: "Shall I create this purchase requisition in S/4HANA? (yes/no)"
3. Only call `create_purchase_requisition` after receiving a confirmed "yes" in the current turn
4. Return the created requisition ID and update the action tracker

### Step 5 — Status check

When the user asks "what is the current status?", call `action_tracker` with the list operation and display the full current action list with statuses and owners.

---

## Gotchas

- **Never submit a requisition without explicit confirmation** — the user must say "yes" (or equivalent) in the current turn. A previous approval in an earlier turn does not count.
- **Always group actions by team** — procurement, supply chain, and finance each have different decision-makers. Mixed output is harder to act on.
- **Estimated impact is directional, not a commitment** — always label estimated savings as estimates, not guarantees.
