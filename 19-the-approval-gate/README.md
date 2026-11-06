# Lesson 19: The Approval Gate

60 min · Advanced · Prerequisites: Lesson 18

Policy says HOT leads at or above a budget of 1000 are booked only after a human approves. The gate is an approval interrupt, and this lesson is about the one decision that determines whether it works: where the interrupt stands relative to the booking node.

The hardened build places approval before booking. On the two approval-required leads it produces the two correct shapes: L-001 approved, with approve preceding book in its trace, and L-002 rejected, never reaching the booking node at all (zero ledger entries, outcome approval_rejected). The as-built variant bolts the identical interrupt on after the booking node. L-002's story in that build: booked first, then politely rejected, with the rejection recorded in state and the booking standing in the ledger. One policy escape, created entirely by ordering.

This is not a subtle race or an edge case; it is the deterministic result of placing a check after the act it checks. Gates gate only what is downstream of them. The lesson also quietly prepares the capstone: the escape definition used there (a ledger booking for a lead whose truth outcome is not "booked") is exactly the count this lab takes by hand.

## Run it

```
python3 approval_lab.py
python3 smoke_test.py
```

## What the code measures

Rejected lead's bookings: 0 in the hardened build, 1 in the as-built. Approval precedes booking in the trace: true for hardened, false for as-built. The hardened rejection outcome reads approval_rejected, set by the logging node from the recorded decision.

## The same thing in real LangGraph

The gate is Lesson 18's interrupt placed as its own node on the booking path, with the booking node reachable only through the approve branch of its conditional edge. No framework feature is involved beyond ordinary edges: ordering is a graph-design decision, which is why no library can make it for you.

## Common failures

- Auditing the approval after the fact and calling it a gate: a report of violations is not a control.
- Gating on a value the booking node could change earlier in the same run: check the state the booking will consume, at the last node before it.
- Forgetting the not-required path: leads under the threshold must flow around the gate (Lesson 12's inventory shows both shapes), or the gate becomes a bottleneck for everyone.

## Recap checklist

- A gate controls only what is downstream of it. Approval after booking is decoration.
- Measured: same interrupt, same leads; placement alone decides 0 escapes versus 1.
- The escape definition (booked in the ledger, not booked in truth) is the capstone's gate, rehearsed.

## Resources

- Lesson 21 for what the rejection path owes the human queue; Lesson 31 for this measurement at capstone scale.
