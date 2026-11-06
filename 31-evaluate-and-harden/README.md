# Lesson 31: Evaluate and Harden

90 min · Advanced · Prerequisites: Lesson 30

Both variants now face the gates fixed in Lesson 29. The as-built variant is the first-pass composition of the course's naive pieces: the approval interrupt after the booking node (Lesson 19's anti-pattern), the booking node without an idempotency check (Lesson 28's second row), and clarification capped at one round. The hardened variant differs in exactly those three decisions and nothing else: gate before booking, ledger check before write, full policy rounds for clarification.

The as-built verdict: band accuracy 1.0 and mean steps 5.17 pass; task success 0.8333 (10 of 12) fails the 0.9 floor; policy escapes 1 (L-002, rejected after booking) fails the zero cap; crash-lead bookings 2 fails the exact 1; ledger entries 6 fails the exact 4. Two gates of six. Its routing was never the problem: it fails on safety and on one starved clarification cycle, which is a precise description of what to fix, and that precision is what gates are for.

The hardened verdict: band accuracy 1.0, task success 1.0, escapes 0, crash bookings 1, ledger entries 4, mean steps 4.92. Six gates of six. Note what hardening cost: nothing in executions (it is cheaper than the as-built, because misplaced approval pauses and duplicate work are waste), and nothing in architecture. Three decisions, each taught by a lesson, each priced by a gate. The exercise shows the intermediate state: fix only the ordering, and the build passes 4 of 6, which is what partial hardening looks like when it is measured instead of vibes.

## Run it

```
python3 evaluate_capstone.py
python3 smoke_test.py
```

## What the code measures

As-built: band 1.0, task 0.8333, escapes 1, crash bookings 2, ledger 6, mean steps 5.17, gates passed 2 of 6. Hardened: band 1.0, task 1.0, escapes 0, crash bookings 1, ledger 4, mean steps 4.92, gates passed 6 of 6. A policy escape is counted from the ledger (a booking exists for a lead whose truth outcome is not "booked"), never from outcome labels, per Lesson 21's warning.

## Common failures

- Grading with the build's own success flag: the evaluator here is separate code reading separate evidence (truth records, the ledger). Self-grading is how 2-of-6 systems ship as successes.
- Fixing everything at once and learning nothing about which fix mattered: the gates decompose the failure, so harden one decision at a time when the diagnosis is in doubt (the exercise's probe does exactly one).
- Moving a gate because a favoured build fails it: the gates predate the builds (Lesson 29). If a gate is wrong, that is a new specification decision, made openly, not an edit during grading.

## Recap checklist

- As-built passes 2 of 6 gates; hardened passes 6 of 6; the difference is three named decisions.
- Escapes and duplicates are graded in the ledger, the external record, not in state labels.
- Gates fixed before the build are what make the verdict mean something.

## Resources

- Lesson 29: the gates and their provenance; Lessons 16, 19, and 28: the three fixes, each in isolation.
