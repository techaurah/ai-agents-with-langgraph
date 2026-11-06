# Lesson 08: Cycles and the ReAct Loop

60 min · Intermediate · Prerequisites: Lesson 07

The ReAct pattern (reason, act, observe, repeat) is a cycle with a decider in it: a node asks the model what to do next, a tool node does it and writes the observation into state, and an edge leads back to the decider until it answers "final". Everything in this lesson runs on that shape. The decider is the course's deterministic model stand-in, a labelled decision table (see `lgx/model.py`): it asks for the first missing observation in a fixed order (company profile, slot, draft). It is not a model, and the lesson measures only what a stand-in can honestly measure: the loop's mechanics.

Four tasks run the loop. Each costs 4 model decisions (three tool choices and a final) and 3 tool executions: 16 decisions and 12 tool executions across the set, all four tasks completed. Then the lab breaks one tool: the draft tool does its work but never writes its observation. The decider cannot see progress, asks for the same tool again, and the loop only ends when the step limit stops it. That failure is the deep one in agent engineering: loops do not usually crash, they repeat. The state is the loop's memory of what is done; a tool that does not write its result has, from the loop's perspective, not happened.

## Run it

```
python3 react_loop.py
python3 smoke_test.py
```

## What the code measures

4 tasks, 4 completed; 16 stand-in decisions; 12 tool executions; 1 stuck loop caught by the step limit. With a hosted model the decision counts would vary run to run; the stand-in's contribution is a loop whose costs can be asserted exactly, so the mechanics (and the failure) can be studied without noise.

## The same thing in real LangGraph

```python
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue,
                              {"tools": "tools", END: END})
builder.add_edge("tools", "agent")
```

(The framework's prebuilt agent helpers assemble this same loop; since the 1.0 line, LangChain's `create_agent` is the recommended entry point and it runs on the LangGraph runtime. See RESEARCH.md.)

## Common failures

- A tool that returns its result to the caller but not into state: the loop re-asks forever, exactly as measured.
- No step limit on a loop because "the model will stop": the model stops when the state says the work is done. Broken state, endless loop.
- Counting a loop's cost in tokens only: decisions and tool executions are the units you can budget, retry, and cache. Count them from the first version.

## Recap checklist

- ReAct = decide node, tool nodes, a back edge, and state as the loop's memory.
- A healthy task here costs 4 decisions and 3 tool executions; the loop's price is countable.
- The failure mode of loops is repetition, and the step limit is the backstop, not the fix.

## Resources

- RESEARCH.md: cycles and conditional routing in the Graph API; the 1.0 note on prebuilt agents (checked 2026-11-06).
