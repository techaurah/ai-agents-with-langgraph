# Lesson 03: State Schemas and Channels

45 min · Beginner · Prerequisites: Lesson 02

A graph's state is a schema: named channels, each with a default, an update rule (its reducer, next lesson), and, in this course's stand-in, a declared type. The schema is the contract every node codes against, and this lesson measures what the contract is worth by breaking it two ways.

The same bad node writes the string "ninety" into the score channel. Against a schema with no declared types, the write succeeds silently: validation has nothing to check, and the run only fails later, downstream, when the band calculation tries to compare a string with an integer. The error message names the comparison, not the node that caused it. Against a typed schema, the engine rejects the update at the moment the bad node returns it, with an error naming the channel and the expected type. Same bug, two debugging experiences: one at the boundary where it happened, one wherever it happened to surface.

The schema also fills a fresh state from its defaults: all four channels of the lab's schema exist before any node runs, so nodes read state defensively only where the schema genuinely allows absence (the score channel's default is None, on purpose: unscored is a real state).

In real LangGraph, schemas are typed dicts (TypedDict) with optional per-key reducers, and the framework validates structure in its own way; the stand-in's explicit `type` field is its teaching equivalent, labelled as such.

## Run it

```
python3 schemas.py
python3 smoke_test.py
```

## What the code measures

Untyped schema: 0 schema errors, 1 downstream failure (the band calculation raises). Typed schema: 1 error caught at the node boundary. The lab's schema declares 4 channels and its defaults fill 4 of 4 on a fresh state. These are small numbers with a large lesson: validation placement decides whether errors are cheap or archaeological.

## The same thing in real LangGraph

```python
from typing import TypedDict

class LeadState(TypedDict):
    lead_id: str
    score: int | None
    band: str
    events: list[str]
```

## Common failures

- One giant state dict with no schema discipline: every node reads whatever key it hopes exists. The schema is the API between your nodes; treat it like one.
- Using absence (a missing key) to mean "not yet computed" in one node and "error" in another. Declare a default (often None) and mean one thing by it.
- Declaring types and then bypassing them by writing state directly in a node: nodes return updates, the engine applies them. Direct mutation skips the boundary check this lesson just priced.

## Recap checklist

- Channels have defaults, reducers, and (here) types; the schema is the nodes' shared contract.
- Typed boundaries catch bad updates where they happen; untyped state defers the failure downstream.
- Defaults define what a fresh thread looks like before any node runs.

## Resources

- RESEARCH.md: state as a shared snapshot whose keys are channels, per the official Graph API overview (checked 2026-11-06).
