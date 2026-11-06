# Lesson 29: Capstone Specification and Gates

60 min · Advanced · Prerequisites: Lesson 28

The capstone assembles the whole course into one agent: the LeadPipe qualification and booking flow as a graph, with the clarification cycle, band routing, an approval interrupt before booking for policy-flagged HOT leads, an idempotent booking write, durable checkpoints, and a CRM log, run over the twelve fixture leads including the one whose booking node crashes mid-write.

Before any of that is built, the grading is fixed. `capstone/gates.json` was written on 2026-11-06, before the capstone code existed, and its `set_from` field records the provenance of every number: band accuracy at least 0.9 and task success at least 0.9 (the reference behaviour from Lessons 11 to 13 matched truth 12 of 12, so the floors leave exactly one lead of slack); policy escapes at most 0 (Lessons 19 and 21: a gate that leaks is not a gate); the crash lead's bookings exactly 1 and the total ledger exactly 4 (Lesson 16's drill; the truth holds four bookings); mean checkpointed steps at most 6.0 (the Module 3 reference flow averaged under 5, so the gate prices loops and pauses without rewarding waste).

This lesson's lab builds nothing. It audits the answer key the gates will grade against: every lead's truth score and band recomputed from the rubric (12 of 12), the approval-required set counted from policy (3), the crash leads counted (1), and the expected bookings implied by the truth outcomes (4). A capstone graded against a broken answer key proves nothing, and a gate written after seeing the results is not a gate.

## Run it

```
python3 capstone_spec.py
python3 smoke_test.py
```

## What the code measures

6 gates in the file, fixed_on 2026-11-06; 12 of 12 truth records verified against the rubric; 3 approval-required leads; 1 crash lead; 4 expected bookings. These are the capstone's constants: Lesson 30 builds to them and Lesson 31 grades against them, and neither is permitted to edit them.

## Common failures

- Writing gates after the build, tuned to whatever the build achieved: that is a description, not a specification, and it teaches nothing.
- Gating only on outcome labels: the ledger gates (escapes, crash bookings, total entries) grade the external record, because Lesson 21 showed labels and ledgers can disagree.
- An un-audited answer key: if a truth record is wrong, a correct agent fails and a broken one passes. Audit first (this lesson), build second (Lesson 30), grade third (Lesson 31), in that order.

## Recap checklist

- Six gates, fixed in writing before the capstone code, each traced to an earlier lesson's measurement.
- The answer key is audited as code: 12 truth records, 3 approvals, 1 crash, 4 bookings.
- Rate gates at 0.9 over 12 leads mean 11 of 12 is the minimum passing score.

## Resources

- capstone/gates.json: the specification itself, including its set_from provenance.
