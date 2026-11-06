# Lesson 06: Edges and Termination

45 min · Beginner · Prerequisites: Lesson 05

Edges are the graph's control flow, and this lesson is about the three ways a run ends: properly, forcibly, and never (because it was rejected before it started). A well-formed graph reaches END and reports done. A cycle with no exit (two nodes pointing at each other) does not hang the process: the compiled step limit stops it, and the checkpointer shows it stopped after exactly 11 executions against a limit of 10 (the limit is exceeded by the execution that crosses it). And a graph whose node has no outgoing path is refused by `compile()` entirely.

The step limit deserves respect rather than tuning. Cycles are legitimate: the clarification loop and the ReAct loop later in this course are cycles on purpose. The limit (in the framework, the `recursion_limit` run configuration; in the stand-in, `max_steps` at compile time) is not there to prevent cycles but to price them: every cycle must either exit on state or be stopped by the budget. When a run hits the limit in production, the right response is almost never "raise the limit"; it is "find the state that was supposed to change and did not", which Lesson 08 demonstrates with a tool that forgets to write its observation.

## Run it

```
python3 edges_lab.py
python3 smoke_test.py
```

## What the code measures

Normal graph: status done after 1 execution. Cycle: stopped at 11 total executions with a limit of 10, and the checkpointer's record proves the count. Broken graph: 1 compile error caught, zero executions. Termination is a measurable property of a graph, not a hope.

## The same thing in real LangGraph

```python
app = builder.compile()
app.invoke(state, config={"recursion_limit": 10,
                          "configurable": {"thread_id": "t"}})
```

## Common failures

- A router that can return a value with no mapped edge: the run fails mid-flight at routing time. Map every decision, or make the router return node names you have verified.
- Cycles whose exit depends on a channel no node updates. The state must change every lap, or the step limit is your exit condition.
- Raising the step limit to silence an error: the limit firing is a symptom report. Read the trace first; Lesson 02 taught you how.

## Recap checklist

- Runs end at END (done), at the step limit (an error with a checkpointed count), or not at all (compile rejection).
- Cycles are legal and necessary; their exit must be a state condition, with the step limit as backstop.
- compile() checks outgoing paths as well as reachability.

## Resources

- RESEARCH.md: the Graph API's execution model and compile checks (checked 2026-11-06).
