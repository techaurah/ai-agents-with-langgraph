# Lesson 09: Fan-Out with Send, and What the Merge Costs

60 min · Intermediate · Prerequisites: Lesson 08

When a step produces independent pieces of work, a router can return `Send` objects to invoke nodes dynamically: fan-out. The results merge back through the channel reducers: the map-reduce shape. This lesson enriches all twelve leads with two independent checks (a slot check, cost 3; a memory lookup, cost 2) in both styles and counts everything.

The results are deliberately two-sided. Executions tie at 48 each: fan-out does not create or destroy work. Super-steps favour fan-out, 36 against 48, because the two branches share one super-step. Modelled latency follows: at a super-step cost of its slowest branch, fan-out prices at 5 time units per lead (1 + max(3, 2) + 1) against the sequential 7, for totals of 60 against 84. But the bookkeeping is real: every Send runs its branch on a copy of the state, 24 copies across the set, and the merge is a correctness surface. The lab ends with the proof: two branches writing the same overwrite channel ("note") produce two written values and one survivor. Nobody errors; one branch's work silently wins. Reducer choice per channel (append for contributions, overwrite only where last-writer-wins is truly intended) is the whole defence.

One stand-in simplification, named: its branches execute sequentially inside the super-step and share one checkpoint with their source node; the framework runs branches in parallel and checkpoints at each super-step boundary. The counts above are computed from traces (execution groups), so they describe the shape, not the stand-in's serialisation.

## Run it

```
python3 fanout_lab.py
python3 smoke_test.py
```

## What the code measures

Executions 48 against 48; super-steps 36 against 48; modelled time 60 against 84 units; 24 branch state copies; slot results identical in 12 of 12 leads (fan-out changed the schedule of the work, not its answers); the conflict demo writes 2 values and keeps 1.

## The same thing in real LangGraph

```python
from langgraph.types import Send

def fan_out(state):
    return [Send("check_slot", state), Send("check_memory", state)]

builder.add_conditional_edges("enrich", fan_out, ["check_slot", "check_memory"])
```

## Common failures

- Fanning out work that is not independent: branches that need each other's results serialise anyway, and you pay the copies for nothing.
- Two branches writing one overwrite channel: measured above, one value silently wins. Contributions belong on append channels.
- Assuming fan-out reduces executions: it reduces super-steps and latency. The work is the work.

## Recap checklist

- Send fans out; reducers merge. Executions tie, super-steps and latency improve.
- The price is state copies (24 here) and a merge that must be designed channel by channel.
- Slot answers agreed 12 of 12: fan-out is a scheduling decision, never a semantics change.

## Resources

- RESEARCH.md: Send for dynamic fan-out and map-reduce, per the official Graph API overview (checked 2026-11-06).
