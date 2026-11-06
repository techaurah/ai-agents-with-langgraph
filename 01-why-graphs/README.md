# Lesson 01: Why Graphs, Measured

45 min · Beginner · Prerequisites: Lesson 00

Agents built as chains and loops work until the flow needs to branch on state, pause for a human, or survive a crash. This lesson does not argue that in the abstract. It builds the LeadPipe flow twice: once as a plain pipeline of function calls (an intake, a scoring call, an inline clarification loop, an inline approval check, an action, a log), and once as a graph on the stand-in engine, then runs both over the same twelve leads and counts what each costs.

The honest headline first: on this mostly linear workload, the pipeline is cheaper. It makes 56 function calls; the graph makes 59 node executions and writes 84 checkpoints the pipeline never writes. The graph's extra executions are the approval node's re-runs after interrupts, and the 84 checkpoints are pure bookkeeping from the pipeline's point of view. If your flow is truly linear, has no human in it, and may never crash, the pipeline wins and this course will not pretend otherwise.

What the pipeline cannot do at any price is the rest of the course: its approval is an inline check that blocks the process, so there is no pausing and resuming a day later; it keeps no snapshots, so a crash mid-lead restarts the lead and cannot prove what already happened; and its flow lives in nested conditionals, so adding the clarification cycle or a second approval means surgery on the one function everything passes through. The graph pays 3 extra executions and 84 snapshots for a flow that is data (nodes and edges) instead of code paths, and for state that survives the process. Lessons 14 to 21 cash that in.

## Run it

```
python3 graph_vs_chain.py
python3 smoke_test.py
```

## What the code measures

Both implementations use the same rubric, the same clarification data, and the same booking choice, and their outcomes agree with fixture truth on 12 of 12 leads: the comparison is about cost and capability, not correctness. The pipeline counts its own calls (56). The graph's executions (59) come from the checkpointer's per-thread totals, and its checkpoint writes (84) from the history lengths across the twelve threads. The pipeline's checkpoint count is 0, not as a rounding of anything, but because it has no checkpointer: that absence is the measured difference the rest of the course exploits.

## The same thing in real LangGraph

The pipeline is what you write with plain functions and LangChain chains. The graph version's shape, in the real framework (reference only, not executed):

```python
from langgraph.graph import StateGraph, START, END
builder = StateGraph(LeadState)
builder.add_node("intake", intake)
builder.add_node("score", score)
builder.add_edge(START, "intake")
builder.add_edge("intake", "score")
graph = builder.compile(checkpointer=checkpointer)
```

## Common failures

- Comparing a graph with a checkpointer against a pipeline and calling the checkpoint writes waste: they are the mechanism behind pause, resume, and audit. Price them, do not dismiss them.
- Benchmarking a graph on a linear task and generalising: Lesson 09 shows a case where the graph's structure pays, and Lesson 13 shows correctness the linear version cannot reach without becoming a graph in disguise.
- Letting the two implementations drift: the lab shares the rubric and tools between both, deliberately. A comparison where each side has its own scoring code measures the drift, not the architecture.

## Recap checklist

- On linear work the graph costs more: 59 executions and 84 checkpoint writes against 56 calls and none.
- The graph buys pause/resume, crash recovery, and a flow made of data. The pipeline cannot buy them at all.
- Outcomes agree 12 of 12, so the choice is architectural, not about correctness on this workload.

## Resources

- RESEARCH.md: LangGraph's own positioning (low-level orchestration for long-running, stateful agents; PyPI, checked 2026-11-06).
