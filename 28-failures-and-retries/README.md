# Lesson 28: Failures, Retries, and Idempotency

75 min · Advanced · Prerequisites: Lesson 27

Retries are the easiest reliability feature to add and the easiest to add wrong. This lesson runs one booking node in three failure manners and counts ledger entries, because the ledger is where retry mistakes become visible.

Flaky-before-write: the node raises before touching the ledger (a service outage). The checkpoint retry re-runs it; result, 2 attempts and exactly 1 booking. Retries alone suffice, because the failed attempt did nothing. Write-then-crash, unguarded: the node writes, then dies (Lesson 16's drill, isolated). The retry cannot know the write happened, so it writes again: 2 attempts, 2 bookings, one of them a duplicate a customer will eventually find. Write-then-crash, guarded by an idempotency key: the node first asks the ledger whether this lead already has a booking, and reuses it. Same crash, same retry: 2 attempts, 1 booking. The crash was not prevented; it was made harmless.

The pattern generalises beyond bookings: any node whose side effect can repeat needs a key the external system can deduplicate on (here, the lead id; in real systems, a request id the API honours), and a read-before-write or an upsert in the node. Checkpoint retries give you at-least-once execution of nodes; idempotency is how you build effectively-once outcomes on top of it. The framework documentation makes the same demand of nodes that pause or retry (RESEARCH.md), and the capstone's crash gate is this lesson, graded.

## Run it

```
python3 reliability_lab.py
python3 smoke_test.py
```

## What the code measures

Three variants, two attempts each. Bookings: flaky-before-write 1; write-then-crash naive 2; write-then-crash idempotent 1. The only difference between the second and third rows is one ledger check at the top of the node.

## The same thing in real LangGraph

```python
def book(state):
    existing = ledger.find(lead_id=state["lead_id"])   # read before write
    if existing:
        return {"booked_slot": existing.slot, "outcome": "booked"}
    ...
```

Framework retry policies (per-node retry configuration) automate the re-invocation; the idempotency remains the node's own responsibility, in the framework just as here.

## Common failures

- Retrying a node whose writes are not idempotent because "it only failed once in testing": the duplicate appears under exactly the conditions (crashes, timeouts) that testing under-samples.
- Idempotency keys scoped too widely (one key for all leads collapses distinct bookings) or too narrowly (a fresh key per attempt deduplicates nothing). The key names the logical operation: one booking per lead.
- Treating a timeout as a failure that did not happen: a timed-out write may have landed. Read back before rewriting, which is the same check, worn for a different failure.

## Recap checklist

- Checkpoint retries re-execute nodes: at-least-once is the execution guarantee.
- Effectively-once outcomes come from idempotency keys plus read-before-write in the node.
- Count duplicates in the external system (the ledger), never in the graph's own state.

## Resources

- Lesson 16: this lesson's second and third rows at full-agent scale; Lesson 31: the gate they decide.
