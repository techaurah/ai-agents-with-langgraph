# Lesson 14: Checkpointing Every Super-Step

60 min · Intermediate · Prerequisites: Lesson 13

Attach a checkpointer and the graph changes character: every super-step boundary writes a snapshot of the full state, the next node, and the run's status, keyed by thread. This lesson reads L-001's complete run as its checkpoint history: 8 records. An initial snapshot, one after intake, one after scoring, the interrupt record (status interrupted, next_node approve), then the resume's records for the re-executed approve, book, crm_log, and the terminal done.

Two properties deserve attention. First, completeness: each record carries all 12 state channels, so any record is a self-sufficient resume point and audit entry; nothing about the run lives only in process memory. Second, timing: checkpoints land at super-step boundaries, never mid-node. A node that crashes halfway leaves the previous boundary's snapshot as the latest truth, which is exactly the guarantee Lessons 16 and 28 build on: completed steps are durable, the in-flight step is redone.

The first checkpoint in which the score is visible is index 2 (after the scoring super-step), a small fact that teaches the reading skill: a checkpoint's state is the world as of the boundary before its next_node runs.

## Run it

```
python3 checkpoint_lab.py
python3 smoke_test.py
```

## What the code measures

8 checkpoints for a 6-execution run (executions plus the initial and terminal records); 12 channels per checkpoint; first scored checkpoint at index 2; the pause record's status is interrupted with next_node approve; the final record's status is done with the outcome booked. Checkpoint arithmetic from Lesson 05's exercise generalises: records equal completed super-steps plus two, plus one per pause.

## The same thing in real LangGraph

```python
from langgraph.checkpoint.memory import InMemorySaver
app = builder.compile(checkpointer=InMemorySaver())
state = app.get_state(config)          # latest checkpoint
history = list(app.get_state_history(config))
```

The framework's saver family (in-memory, SQLite, Postgres) is the production version of the stand-in's two checkpointers; see RESEARCH.md.

## Common failures

- Checkpointing and then mutating state objects in place elsewhere: snapshots are copies; code that reaches into a retrieved checkpoint and edits it is editing a photograph.
- Assuming a checkpoint exists for a node that is still running: boundaries only. Design nodes so that redoing one node is acceptable (Lesson 28 makes that precise).
- Treating the history as a log to prune casually: it is the audit trail and the time-travel substrate (Lesson 17). Prune by policy, not by tidiness.

## Recap checklist

- One snapshot per super-step boundary, plus initial and terminal records: 8 for L-001.
- A checkpoint is state, next node, and status: everything a resume or an audit needs.
- Nothing mid-node is ever checkpointed; the in-flight step is the unit of redo.

## Resources

- RESEARCH.md: checkpoints at super-step boundaries and node re-execution, per the official docs (checked 2026-11-06).
