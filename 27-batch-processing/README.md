# Lesson 27: Batch Processing over Threads

45 min · Intermediate · Prerequisites: Lesson 26

Production agents rarely run one conversation at a time; they drain queues. The graph model makes the batch shape almost disappointingly simple: the batch is twelve threads, not one big loop. Each lead runs on its own thread of the same compiled agent, so isolation (Lesson 15) does the concurrency design work, and the batch's job is intake validation, per-lead error containment, and bookkeeping.

The lab runs the twelve fixture leads plus one malformed submission (an unknown state channel) mixed into the same batch. The malformed item fails at its own front door with a structure error, is counted failed, and the twelve complete unaffected: 13 attempted, 12 completed, 1 failed. The totals are the batch report this course has been building toward: 59 node executions across the set and the outcome distribution of 4 booked, 4 follow-ups, 3 nurtures, 1 rejection.

The failure policy deserves the same deliberateness as the graph design. Containment (fail one, continue the rest) is right for independent leads; it would be wrong for an all-or-nothing import. The mechanism offers both: per-thread errors are recorded per thread, and the decision to halt or continue belongs to the batch driver, which is application code, not framework magic.

## Run it

```
python3 batch_lab.py
python3 smoke_test.py
```

## What the code measures

13 attempted, 12 completed, 1 failed (the malformed submission, rejected at invoke); 59 total executions; outcomes 4 booked, 4 follow_up_scheduled, 3 nurtured, 1 approval_rejected. Every figure reconciles with Lesson 12's path inventory and Lesson 30's capstone run, as it should: the batch adds a driver, not new behaviour.

## The same thing in real LangGraph

In the hosted runtime, this driver is the platform's job (runs are created per thread and executed by workers); in a self-hosted deployment it is a queue consumer invoking the compiled graph per thread. The stand-in's loop is the honest miniature of both: one graph object, many threads, errors priced per lead.

## Common failures

- One shared thread for the batch "to keep it simple": the second lead continues the first's state. Threads are cheap; contamination is not.
- Letting one poisoned item kill the batch: validate at the door (schema checks do this naturally) and count failures as data.
- Reporting only completions: a batch report that omits the failed count is how malformed inputs become silent data loss. Attempted, completed, failed: all three, always.

## Recap checklist

- A batch is many threads on one compiled graph; the driver owns validation and error policy.
- Malformed input failed alone; 12 of 13 completed; nothing shared, nothing contaminated.
- Report attempted, completed, failed, and the outcome distribution: four numbers, no adjectives.

## Resources

- Lesson 15: the thread isolation this lesson spends; Lesson 30: the same twelve leads under capstone grading.
