# Lesson 13: Clarification Cycles

60 min · Intermediate · Prerequisites: Lesson 12

The fix for provisional routing is ordering: complete the state, then route. The agent's scoring node returns the missing-fields list with every score; a conditional edge sends leads with missing fields to a clarify node instead of onward, one field per round is filled from the lead's answer (the stand-in for asking the question on the lead's channel), and an edge leads back to scoring. A cycle, with the policy's round budget (2) as its exit guarantee alongside the step limit.

The lab isolates the variable: two builds share the rubric, the approval interrupt, and the actions, differing in exactly the clarification cycle. With it, scores match truth 12 of 12. Without it, scores match 10 of 12 and outcomes 11 of 12: L-004 is followed up as a WARM instead of booked as the HOT it is, while L-008's outcome accidentally survives (both its provisional 25 and completed 53 are NURTURE) even though its score is wrong. Outcome agreement alone would have hidden that: score-level grading is what catches a right answer reached from wrong data.

The cycle's price is three extra node executions across the set (one round for L-004, two for L-008, the maximum any lead needs). Cheap, bounded, and honest: when the round budget runs out with fields still missing, the agent does not guess; it routes to an unresolved outcome (needs_info), which the capstone's as-built variant demonstrates by shrinking the budget to a single round.

## Run it

```
python3 clarify_lab.py
python3 smoke_test.py
```

## What the code measures

Clarify rounds across the set: 3 total, at most 2 on one lead. With the cycle: 12 of 12 scores match truth. Without: 10 of 12 scores and 11 of 12 outcomes match. The two-point score gap and one-point outcome gap, on identical everything-else, is the measured value of one conditional edge and one node.

## The same thing in real LangGraph

```python
def after_score(state) -> Literal["clarify", "route"]:
    return "clarify" if state["missing"] and \
        state["clarify_rounds"] < 2 else "route"

builder.add_conditional_edges("score", after_score,
                              {"clarify": "clarify", "route": "route"})
builder.add_edge("clarify", "score")
```

## Common failures

- Clarifying after routing: the route is spent by the time the data arrives. Order is the whole lesson.
- An unbounded clarify cycle: a lead that never answers loops forever or burns the step limit. Round budgets are policy (here, 2, in the fixture), not implementation detail.
- Treating an unresolved lead as a failed lead: needs_info is a legitimate terminal state with its own follow-up process, not an exception.

## Recap checklist

- Score returns missing fields; a conditional edge cycles missing leads through clarify before routing.
- The cycle costs 3 executions and buys 2 score corrections and 1 outcome correction on this set.
- Exhausted budgets end at needs_info, honestly, not at a guess.

## Resources

- Lesson 07: the provisional misroute this lesson eliminates; Lesson 31: what a one-round budget does to the capstone.
