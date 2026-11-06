# Lesson 26: Streaming Modes

45 min · Intermediate · Prerequisites: Lesson 25

A finished run tells you the destination; a stream tells you the journey while it is still useful. The stand-in's stream offers the two modes that matter conceptually. Values mode yields the full state after every super-step: the view a progress UI or a supervising human wants. Updates mode yields one small dict per node execution, naming the node and only the channels it changed: the view a debugger or a cost accountant wants.

The lab streams L-001's approval run in values mode: two state snapshots (intake, score), then an interrupt marker, because the pause is itself an event a consumer must handle; the resume streams three more snapshots, the last of them the finished, booked state. A WARM lead in updates mode produces four single-key events, one per node. Same runs as always; the only new thing is when and in what shape the information leaves the graph.

One simplification, named in the engine and repeated here: the stand-in collects events during the run and then yields them, while the framework streams them live as super-steps complete. Event contents and counts are identical; only their timing differs. Timing is a real production concern (first-token latency, hanging connections), and it is also the one property this offline course cannot measure honestly, so it does not pretend to.

## Run it

```
python3 streaming_lab.py
python3 smoke_test.py
```

## What the code measures

Values events before the pause: 2, plus 1 interrupt marker; after the resume: 3, the final one carrying outcome booked. Updates events for the WARM lead: 4, each with exactly 1 key (the node that produced it). Streaming changes observability, not execution: every count here reconciles with the traces and checkpoints of the same runs in earlier lessons.

## The same thing in real LangGraph

```python
for chunk in app.stream(state, config, stream_mode="updates"):
    print(chunk)   # {"score": {"score": 90, "band": "HOT"}} and so on
for state_snapshot in app.stream(state, config, stream_mode="values"):
    ...
```

## Common failures

- Building a UI on values mode and shipping full state (including fields the user should not see) to the client: stream modes are not access control. Filter at the boundary.
- Assuming a stream that yields nothing is a hung run: an interrupt is a terminal event for that invoke. Handle the marker.
- Counting costs from updates events and forgetting pauses: re-executions appear as repeated node events after a resume, which is correct accounting and Lesson 18's duplication made visible.

## Recap checklist

- Values = whole state per super-step; updates = per-node deltas. Choose by consumer.
- Interrupts appear in the stream as events; consumers must handle them.
- The stand-in collects then yields; the framework flows live. Contents equal, timing out of scope.

## Resources

- RESEARCH.md: streaming among the framework's headline features (checked 2026-11-06).
