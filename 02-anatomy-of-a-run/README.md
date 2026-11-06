# Lesson 02: Anatomy of a Run

45 min · Beginner · Prerequisites: Lesson 01

Before building graphs, learn to read one. This lesson takes a single WARM lead with no approval and no clarification (L-005, the simplest full path) and reads its run three ways: the execution trace, the checkpoint history, and the streamed state events. They are three views of the same facts, and fluency is knowing which view answers which question.

The trace lists node executions in order: intake, score, follow_up, crm_log. It answers "what ran". The checkpoint history holds six records: an initial snapshot, one per completed super-step, and the final record marked done. Its `next_node` fields answer "where was the run about to go" at every point, which is what makes a paused or crashed run resumable and auditable. The streamed values events are the state after each super-step (four of them), the view a user interface would consume. Lesson 26 is devoted to streaming; here it is enough to see that a stream is the checkpoint sequence, narrated live.

The lesson also breaks a graph on purpose: a builder with an extra node that nothing points to. `compile()` refuses it, naming the orphaned node. Structural checks at compile time are part of the framework's contract (the official Graph API overview describes compile checking for problems such as orphaned nodes; RESEARCH.md), and the stand-in implements the same check.

## Run it

```
python3 anatomy.py
python3 smoke_test.py
```

## What the code measures

For L-005: 4 trace entries, 6 checkpoints written, 4 streamed values events, 1 orphan error caught, final status done, outcome follow_up_scheduled. The checkpoint `next_node` sequence is intake, score, follow_up, crm_log, then null on the done record: the history is a complete map of the run, not a sample of it.

## The same thing in real LangGraph

```python
app = builder.compile(checkpointer=InMemorySaver())
result = app.invoke({"lead": lead}, config={"configurable": {"thread_id": "anatomy"}})
history = list(app.get_state_history(config))
```

## Common failures

- Reading the trace when you need the history: the trace says what executed; only checkpoints say what state the run can resume from.
- Assuming one checkpoint per node: there is also the initial snapshot and the terminal record. Off-by-two errors in history audits start here.
- Treating a compile error as bureaucracy: the orphan check caught a node that would have silently never run. In a large graph that is a feature you forgot to wire, found for free.

## Recap checklist

- Trace = what ran; history = snapshots with next_node; stream = state after each super-step.
- A four-node run writes six checkpoints on the stand-in.
- compile() rejects unreachable nodes before any execution happens.

## Resources

- RESEARCH.md, "The concepts the course teaches": super-steps and checkpoints at super-step boundaries, from the official Graph API overview (checked 2026-11-06).
