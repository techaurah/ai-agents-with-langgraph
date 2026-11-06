# Lesson 18: Interrupts and Resume Values

75 min · Advanced · Prerequisites: Lesson 17

An interrupt pauses a node in the middle of its function and hands a payload to whoever is driving the run. The run's checkpoint records the pause; the thread then waits, indefinitely, at no cost (Lesson 15). Resuming supplies a value, the paused node re-executes from its first line, and the interrupt call returns the resume value as if it had been a function call all along.

The re-execution is the part to internalise, so the lab measures it. Its approve node appends to a notifications list (the stand-in for emailing the approver) before calling interrupt. After the resume, the list holds 2 entries and the approve node has executed 2 times: once to pause, once to complete. Nothing malfunctioned. That is the documented semantics, stated plainly in the framework's own docs: after a pause, the node restarts from the beginning of its function, so anything before the interrupt point runs again (RESEARCH.md). Every side effect placed before a pause must therefore be repeatable: a notification becomes a duplicate email, a booking becomes a double booking, unless the node is written defensively (Lessons 19 and 28 are the defences).

The payload is the contract with the human: here, the lead id and the action requested ("approve_booking"). Design payloads like API schemas, because a person (or their UI) is the other endpoint.

## Run it

```
python3 interrupt_lab.py
python3 smoke_test.py
```

## What the code measures

First invoke: status interrupted, payload action approve_booking for L-001. Across both invokes: 2 approve executions and 2 pre-interrupt side effects. After an "approve" resume: outcome booked. The duplication is counted, not asserted: 2 is what re-execution means in ledger entries.

## The same thing in real LangGraph

```python
from langgraph.types import interrupt, Command

def approve(state):
    decision = interrupt({"action": "approve_booking",
                          "lead_id": state["lead_id"]})
    return {"approval_decision": decision}

result = app.invoke(state, config)                 # pauses
result = app.invoke(Command(resume="approve"), config)  # resumes
```

## Common failures

- Side effects before the interrupt that are not idempotent: the single most expensive interrupt bug, measured here at notification scale and in Lesson 16 at booking scale.
- Assuming the resume value is validated: it is whatever the driver passes. Lesson 21 routes on exact equality for this reason.
- Interrupting without a checkpointer: a pause with nowhere to record itself is just an exception.

## Recap checklist

- interrupt(payload) pauses mid-node; resume re-executes the node and interrupt() returns the resume value.
- Anything before the interrupt runs twice across a pause: measured 2 executions, 2 side effects.
- The payload is a contract with the human on the other side; design it like one.

## Resources

- RESEARCH.md: interrupts and Command(resume=...) in the official docs (checked 2026-11-06).
