# Lesson 10: Tools as Nodes

60 min · Intermediate · Prerequisites: Lesson 09

A tool call buried inside a node is invisible to the graph: no trace entry, no checkpoint boundary, no retry granularity. The same tool as its own node gets all three for free. This lesson proves the difference with one flaky tool: a follow-up sender that fails the first time it is called for L-005.

Two builds absorb the failure. The monolith does intake, scoring, routing, the tool call, and the CRM log inside a single node. When the tool raises, the run's checkpoint still holds the initial state: zero visible progress, because from the graph's perspective nothing has completed. Recovery means executing the whole node again (2 attempts, everything redone). The tool-node build gives intake, score, the tool, and the log their own nodes behind a checkpointer. At the failure, the latest checkpoint records 2 completed steps, and the retry re-executes exactly 2 nodes (the tool and the log). Same failure, same tool, radically different blast radius.

The full agent at the end, with the same flaky behaviour in play, lands all 12 outcomes: per-node checkpoints turn a mid-flow failure from a restart into a resume. This is also the shape the framework encourages for real tools (its ToolNode pattern runs each tool call as a node for the same observability and control; RESEARCH.md).

## Run it

```
python3 tools_lab.py
python3 smoke_test.py
```

## What the code measures

Monolith: 2 attempts, 0 visible progress at failure. Tool-node build: 2 completed steps preserved at failure, 2 executions on retry, and the flaky tool attempted exactly 2 times (once failing, once succeeding). Full agent: 12 of 12 outcomes correct. The granularity of recovery is exactly the granularity of your nodes: no finer, no coarser.

## The same thing in real LangGraph

```python
from langgraph.prebuilt import ToolNode
builder.add_node("tools", ToolNode([book_slot, send_follow_up]))
```

(In the 1.x line the prebuilt helpers moved toward LangChain's `create_agent`, but the node-per-tool structure is the same idea; see RESEARCH.md.)

## Common failures

- One mega-node "for simplicity": simplicity that deletes your retry boundaries and your trace. Node granularity is failure granularity.
- Retrying a whole run because a tool failed: if the tool is a node behind a checkpointer, the retry is the node, not the run.
- Hiding a tool's result in a variable instead of state: the checkpoint then cannot show what the tool did, and a resume cannot reuse it.

## Recap checklist

- Tool as node = trace entry, checkpoint boundary, retry unit.
- A failure preserves exactly the nodes that completed before it: here, 2 of 4.
- The monolith's recovery cost is everything; the node build's is the remainder of the flow.

## Resources

- RESEARCH.md: nodes as the unit of work in the Graph API (checked 2026-11-06).
