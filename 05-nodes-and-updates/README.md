# Lesson 05: Nodes and Partial Updates

60 min · Intermediate · Prerequisites: Lesson 04

A node is a function that reads the state it needs and returns the channels it changed: a partial update. This lesson's schema has six channels; the scoring node returns two of them (score and band), and the other four keep their values untouched. That small contract is what makes nodes composable: a node cannot accidentally reset a channel it does not mention, and the engine's reducer layer (Lesson 04) is the only place state changes.

The second half compares two ways to route from inside the flow. A triage node can return a plain update and let a separate router function on a conditional edge decide the next node; or it can return `Command(update=..., goto=...)`, updating state and choosing the next node in one object. The lab builds both, runs a HOT and a WARM input through each, and finds identical paths and identical checkpoint counts (4 each on the HOT run). Command is not faster and not shorter-running; it removes a definition site and keeps the decision beside the computation that produced it. That is the honest trade, and it is why the framework offers both. Command has one more job, supplying the resume value after an interrupt, which Module 5 uses heavily.

In the stand-in, a node's Command targets are declared at `add_node` time (`command_targets=...`) so compile() can check reachability; the framework reads them from the node's return-type annotation for the same reason.

## Run it

```
python3 nodes_lab.py
python3 smoke_test.py
```

## What the code measures

Partial update: 2 keys returned against 6 channels, with the 3 unrelated channels verified intact afterwards (the fourth, lead_id, was the input). Command versus conditional edges: paths match on both test inputs, and the checkpoint counts are equal at 4, which is the lab's way of saying the two mechanisms differ in structure, not in execution cost.

## The same thing in real LangGraph

```python
from langgraph.types import Command
from typing import Literal

def triage(state) -> Command[Literal["book", "follow"]]:
    band = "HOT" if state["score"] >= 80 else "WARM"
    return Command(update={"band": band},
                   goto="book" if band == "HOT" else "follow")
```

## Common failures

- Returning the whole state from every node: it works, and it destroys the partial-update contract. A stale copy of a channel, returned by a node that never meant to touch it, overwrites a fresher value through the default reducer.
- Mutating state in place inside a node: the engine checkpoints what updates produced; in-place edits are invisible to the trace and break the checkpoint story.
- Using Command goto to jump somewhere the graph never declared: undeclared targets are exactly what compile-time reachability exists to catch.

## Recap checklist

- Nodes read what they need and return only what they changed.
- Command(update, goto) folds routing into the node; conditional edges keep it outside. Same steps, different structure.
- Declared Command targets let compile() verify the jumps before runtime.

## Resources

- RESEARCH.md: Command as update-plus-route, and its resume form, per the official Graph API overview (checked 2026-11-06).
