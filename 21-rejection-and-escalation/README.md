# Lesson 21: Rejection and Escalation Paths

60 min · Advanced · Prerequisites: Lesson 20

A gate has three exits, not two. Approve: proceed. Reject: stop, record, and hand the thread to a human queue, because a rejected HOT lead is a business event, not a null result. Anything else: the tired approver, the malformed webhook, the UI that sent "maybe". This lesson drives a gated graph with all three resume values and counts bookings: approve books 1; reject books 0; "maybe" books 0. The gate fails closed because its routing rule is an equality check on the exact string "approve"; everything that is not approval is treated as not-approval. Design resume handling as allowlisting, never as denylisting ("book unless they said no" books on every typo).

The full run then counts escalations: of the twelve leads, exactly one ends approval_rejected (L-002), and that thread is the human queue's work item. Its state carries the score, the band, and the decision, so the human inherits the agent's whole context instead of a bare refusal.

One honest wart, kept in print: in the agent build, a garbage decision like "maybe" also books nothing, but the run's final outcome label is empty rather than approval_rejected, because the logging node only translates the exact decision "reject". The safe property (no booking) holds; the tidy label does not. The exercise asks you to find that gap before it matters, which is the correct order.

## Run it

```
python3 rejection_lab.py
python3 smoke_test.py
```

## What the code measures

Bookings by resume value: approve 1, reject 0, maybe 0. Escalations in the full twelve-lead run: 1, and it is L-002. Both numbers come from the ledger (the ground truth of what the system did), not from outcome labels.

## The same thing in real LangGraph

No new mechanism: the rejection path is a conditional edge on the approval node's update, and the escalation is a node that records the thread for a human. The framework feature doing the work is the one from Lesson 18: the resume value arrives as data, and data can be routed on, validated, and audited.

## Common failures

- Routing on inequality with rejection ("if not rejected, book"): every malformed value books. Allowlist the affirmative.
- Dropping the rejected lead silently: a rejection without an escalation record converts a policy decision into lost revenue nobody reviews.
- Trusting outcome labels over the ledger when auditing: labels are state a node wrote; the ledger is what happened. The capstone grades the ledger.

## Recap checklist

- Three exits: approve proceeds, reject escalates, anything else fails closed.
- Escalation is a state with context (score, band, decision), not a discarded thread.
- Audit bookings in the external system of record, not in labels the graph wrote about itself.

## Resources

- Lesson 19 for the gate's placement; Lesson 31 for escapes and labels graded separately.
