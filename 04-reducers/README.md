# Lesson 04: Reducers Decide What an Update Means

45 min · Beginner · Prerequisites: Lesson 03

When a node returns `{"messages": ["msg-2"]}`, what happens to the messages already in state? The channel's reducer decides. The default is overwrite: the new value replaces the old. For a status field that is right. For a conversation history it is silent data loss, and this lesson measures it: three nodes each contribute one message, and under overwrite the finished state holds exactly one message, the last one. The contributions of the first two nodes are gone, and no error occurred anywhere.

Switch the channel's reducer to append and the same three nodes produce all three messages in order. A numeric channel with the add reducer totals two increments (2) instead of keeping the second (1). These are the stand-in's three reducers (overwrite, append, add); the framework's best-known reducer is `add_messages`, which appends with message-specific merging, and the pattern generalises: any function of (current value, update) can be a reducer, including ones that deduplicate or keep the maximum.

The agent itself depends on this: its events channel uses append, so a finished L-001 run carries its whole path (intake, score, approve, book, crm_log) as evidence. Several later lessons read that channel as the run's own testimony.

## Run it

```
python3 reducers_lab.py
python3 smoke_test.py
```

## What the code measures

Overwrite keeps 1 of 3 messages (["msg-3"]); append keeps 3 of 3 in order; the add reducer totals 2 from two increments of 1; the agent's events channel ends with 5 entries for L-001. Every one of those numbers is a reducer choice made visible.

## The same thing in real LangGraph

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
    rounds: Annotated[int, operator.add]
```

## Common failures

- Forgetting the reducer on a list channel and wondering where the history went. This is the single most common beginner bug in graph frameworks, and it fails silently.
- Appending when you meant to replace: a band channel with append becomes a list of every band the lead ever had, and routers downstream read the wrong element.
- Writing a reducer with side effects or randomness: reducers run during checkpoint merges and replays; they must be pure functions of the two values.

## Recap checklist

- A reducer combines the current channel value with a node's update: overwrite, append, and add are the stand-in's three.
- History-like channels need append; status-like channels need overwrite; counters need add.
- The agent's events channel (append) is why later lessons can audit a run from its own state.

## Resources

- RESEARCH.md: reducers as part of the state schema, per the official docs (checked 2026-11-06).
