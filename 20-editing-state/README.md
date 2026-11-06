# Lesson 20: Editing State at a Breakpoint

60 min · Advanced · Prerequisites: Lesson 19

Interrupts pause inside a node; breakpoints pause between nodes. Compile with `interrupt_before=["book"]` and the run stops before the booking node executes, with the state of that moment available for inspection and correction. This lesson uses the pause for the most common production correction: the lead emails a new constraint (Tuesday 15:00, not Wednesday 11:00) while their qualification is mid-flight.

The mechanics matter. While paused, the ledger holds 0 entries: nothing irreversible has happened, which is exactly why between-node pauses are the safe editing surface. The correction goes through `update_state`, which writes a new checkpoint carrying the edited lead (one additional record; the pre-edit history is untouched, so the correction itself is auditable). The resumed run then books Tuesday 15:00, a slot it would never have chosen from the original record (Wednesday 11:00).

Compare Lesson 18: editing during an in-node interrupt is not possible, because the node is mid-function; the state you would edit is the checkpoint from the previous boundary, and the node will re-execute over it. Breakpoints exist for the moments when a human needs to change the facts, not just answer a question.

## Run it

```
python3 edit_state.py
python3 smoke_test.py
```

## What the code measures

Pause payload names the breakpoint (book); ledger entries while paused: 0; the slot the original record would have booked: wed 11:00; the slot actually booked after the edit: tue 15:00; checkpoints added by the edit itself: exactly 1.

## The same thing in real LangGraph

```python
app = builder.compile(checkpointer=saver, interrupt_before=["book"])
app.invoke(state, config)                       # pauses before book
app.update_state(config, {"lead": corrected})   # the edit, as a new checkpoint
app.invoke(None, config)                        # resumes into book
```

## Common failures

- Editing state to fix a computed channel instead of its inputs: the next node may recompute over your edit, or a stale derived value may contradict it. Edit facts; let nodes recompute derivations (Lesson 17's fork-point rule is the same law).
- Editing without a checkpoint trail: update_state appends rather than rewrites for a reason. A correction nobody can see is a future incident's mystery.
- Pausing before a node that has already done its side effect elsewhere: breakpoints guard the node they precede, nothing else. Place them before the irreversible step (Lesson 19's law again).

## Recap checklist

- Breakpoints pause between nodes; interrupts pause inside them. Editing belongs at breakpoints.
- update_state writes a new checkpoint: the edit is itself auditable history.
- While paused before booking, the ledger is empty: corrections are free exactly until the side effect.

## Resources

- RESEARCH.md: interrupt_before and interrupt_after as compile-time breakpoints (checked 2026-11-06).
