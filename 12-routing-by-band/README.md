# Lesson 12: Routing by Band, the Full Path Inventory

60 min · Intermediate · Prerequisites: Lesson 11

"Route HOT leads to booking, WARM to follow-up, NURTURE to nurture" sounds like one conditional edge. Run the finished agent over twelve leads and the truth is a path inventory: seven distinct logical paths. Approval-then-book, approval-then-rejection, direct booking, clarify-then-book, follow-up, clarify-twice-then-nurture, and plain nurture. Three of the twelve threads pause at the approval interrupt on the way. The outcome split is 4 booked, 4 follow-ups, 3 nurtures, 1 rejection.

The inventory matters because it is the real test surface. A test that exercises "the HOT path" and misses that HOT arrives in three shapes (direct, approved, rejected) has tested a third of the behaviour. Paths here are counted from execution traces, collapsing the approval node's double appearance after a resume (pause plus re-execution is one logical stage; Lesson 18 dissects the re-execution itself). When your own agent's inventory surprises you (it will), the surprise is information: every path in the inventory is a behaviour you are shipping, whether or not you designed it.

This is also where the module's pieces visibly become one agent: scoring (Lesson 11), routing (Lesson 07), clarification (next lesson), tools (Lesson 10), all reading and writing one state schema (Lesson 03).

## Run it

```
python3 band_router.py
python3 smoke_test.py
```

## What the code measures

12 leads; 7 distinct paths; 3 threads paused for approval (the three policy-flagged HOT leads, L-001, L-002, L-009); outcomes 4 booked, 4 follow_up_scheduled, 3 nurtured, 1 approval_rejected. Every number is counted from traces of the real agent graph, not from the fixture truth: the inventory is observed behaviour.

## The same thing in real LangGraph

Nothing new: the inventory emerges from `add_conditional_edges` on the score node plus the approval node returning a Command-like routing decision. What the framework adds in production is tracing tooling (LangSmith) that draws this inventory from live runs; the stand-in counts it from traces, which is the same evidence at course scale.

## Common failures

- Testing bands instead of paths: a band is an input class; a path is a behaviour. Only paths can regress.
- Forgetting the rejection path exists until an approver uses it: 1 of the 12 leads walks it here, and it is the path with a policy consequence (Lesson 21).
- Treating the paused threads as a separate system: 3 of 12 threads pause mid-path. Pause is part of the inventory, not an exception to it.

## Recap checklist

- Twelve leads, seven paths, three pauses: the inventory is the agent's real shape.
- Outcome split: 4 booked, 4 follow-ups, 3 nurtures, 1 rejection.
- Paths are counted from traces, with interrupt re-executions collapsed into one stage.

## Resources

- Lessons 07 and 11: the router and the rubric whose interaction produces this inventory.
