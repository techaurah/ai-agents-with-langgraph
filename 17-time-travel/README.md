# Lesson 17: Time Travel and Forks

60 min · Advanced · Prerequisites: Lesson 16

A checkpoint history is not only for recovery; it is a set of alternate starting points. This lesson finishes L-012 as a WARM follow-up (score 78), then walks its history back to the checkpoint just after intake (id 1), forks it into a new thread, edits the fork's state (the budget was actually 1500, and the lead can do Monday 09:00), and resumes. The fork re-scores at 88, pauses for the approval the corrected budget triggers, and books Monday 09:00. The original thread is verified untouched: still 78, still a follow-up.

Two uses justify the feature. Debugging: "what would the agent have done if this field had been right" becomes a runnable question instead of a speculation, answered against the same code and fixtures that produced the original run. Product: a corrected record can be re-decided from the moment the error entered, rather than restarted from zero or, worse, patched at the end state.

The exercise covers the sharp edge: a fork inherits everything its checkpoint had computed. Fork from after the scoring checkpoint and the edited budget is ignored by the already-written score: the fork completes as the same follow-up, carrying a stale 78 next to a corrected 1500. Fork points are semantic choices; pick the boundary before the computation you want redone.

## Run it

```
python3 time_travel.py
python3 smoke_test.py
```

## What the code measures

Original: score 78, outcome follow_up_scheduled. Forked from checkpoint 1 (after intake, before scoring): the fork pauses for approval (the corrected budget crosses the policy threshold), then finishes at score 88 with outcome booked, slot "mon 09:00". Original unchanged after the fork completes.

## The same thing in real LangGraph

```python
history = list(app.get_state_history(config))
target = history[-3]  # the checkpoint to fork from
new_config = app.update_state(target.config, values={...})
app.invoke(None, new_config)  # resume the fork
```

The framework exposes the same two primitives, history plus update_state, as a supported time-travel workflow (RESEARCH.md).

## Common failures

- Forking from a checkpoint after the computation you want to change: computed channels (score, band) are state too, and they travel with the fork.
- Editing the original thread instead of forking: update_state on the live thread rewrites its future; forking keeps both timelines auditable.
- Assuming a fork re-runs side effects safely by default: the fork re-executes nodes, including the booking node. Idempotency (Lesson 28) is what makes that safe.

## Recap checklist

- Fork = new thread seeded from an old checkpoint; edit = update_state on the fork.
- Correct fork point for a data fix is before the computation that consumed the bad data.
- The original thread is never modified by its forks (verified).

## Resources

- RESEARCH.md: state history and time travel in the official docs (checked 2026-11-06).
