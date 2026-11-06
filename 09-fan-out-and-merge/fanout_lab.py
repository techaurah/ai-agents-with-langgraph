"""Lesson 09 lab: Send fans work out; the merge is where it costs you.

Each of the twelve leads needs two independent enrichments (a slot check
and a memory lookup). The lab runs them two ways and counts honestly.
Sequentially: enrich, slot, memory, merge, four executions in four
super-steps. Fanned out: the router returns two Sends, both branches run
inside one super-step, then merge: the same four executions, one fewer
super-step, and a lower modelled latency (a super-step costs its slowest
branch, so 1 + max(3, 2) + 1 = 5 time units against the sequential 7).
The fan-out's price is bookkeeping: every Send deep-copies the state
(24 copies across the set), and when two branches write the same
overwrite channel, one value silently wins. The conflict at the end is
deliberate: branch A and branch B both write "note", and only B's
survives.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, Send, StateGraph, Store
from lgx.agent import choose_slot, load_leads, load_schedule
from lgx.checkpoint import InMemoryCheckpointer

COSTS = {"enrich": 1, "check_slot": 3, "check_memory": 2, "merge": 1}

SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "slot": {"default": None, "type": str},
    "memory_hits": {"default": 0, "type": int},
    "enriched": {"default": False, "type": bool},
    "note": {"default": "", "type": str},
}


def make_store(leads):
    store = Store()
    for lead in leads:
        slug = lead["company"].lower().replace(" ", "-")
        store.put(("leads", slug), "profile", {"company": lead["company"]})
    return store


def evaluate():
    leads = load_leads()
    schedule = load_schedule()
    store = make_store(leads)

    def enrich(state):
        return {}

    def check_slot(state):
        return {"slot": choose_slot(schedule, state["lead"]) or "none"}

    def check_memory(state):
        hits = store.search(("leads",), query=state["lead"]["company"])
        return {"memory_hits": len(hits)}

    def merge(state):
        return {"enriched": True}

    # Sequential variant.
    seq = StateGraph(SCHEMA)
    for name, fn in (("enrich", enrich), ("check_slot", check_slot),
                     ("check_memory", check_memory), ("merge", merge)):
        seq.add_node(name, fn)
    seq.add_edge(START, "enrich")
    seq.add_edge("enrich", "check_slot")
    seq.add_edge("check_slot", "check_memory")
    seq.add_edge("check_memory", "merge")
    seq.add_edge("merge", END)
    seq_cp = InMemoryCheckpointer()
    seq_app = seq.compile(checkpointer=seq_cp)

    # Fan-out variant.
    fan = StateGraph(SCHEMA)
    fan.add_node("enrich", enrich)
    fan.add_node("check_slot", check_slot, via_send=True)
    fan.add_node("check_memory", check_memory, via_send=True)
    fan.add_node("merge", merge)
    fan.add_edge(START, "enrich")
    fan.add_conditional_edges("enrich", lambda s: [
        Send("check_slot"), Send("check_memory")])
    fan.add_edge("enrich", "merge")
    fan.add_edge("merge", END)
    fan_cp = InMemoryCheckpointer()
    fan_app = fan.compile(checkpointer=fan_cp)

    seq_exec = fan_exec = seq_steps = fan_steps = 0
    seq_time = 0
    sends = 0
    slot_equal = 0
    for lead in leads:
        tid = f"lead-{lead['id']}"
        r1 = seq_app.invoke({"lead": lead}, thread_id=f"seq-{tid}")
        r2 = fan_app.invoke({"lead": lead}, thread_id=f"fan-{tid}")
        seq_exec += r1["total_steps"]
        fan_exec += r2["total_steps"]
        # Super-steps are counted from the trace: every sequential
        # execution is its own super-step; a fan-out group (the source
        # node, then all its Sends together) is two.
        seq_steps += len(r1["trace"])
        fan_sends = sum(1 for e in r2["trace"] if e["kind"] == "send")
        fan_steps += len(r2["trace"]) - fan_sends + (1 if fan_sends else 0)
        seq_time += sum(COSTS[e["node"]] for e in r1["trace"])
        sends += sum(1 for e in r2["trace"] if e["kind"] == "send")
        if r1["state"]["slot"] == r2["state"]["slot"]:
            slot_equal += 1
    fan_time = len(leads) * (COSTS["enrich"]
                             + max(COSTS["check_slot"], COSTS["check_memory"])
                             + COSTS["merge"])

    # The merge conflict, isolated: two branches, one overwrite channel.
    conflict = StateGraph(SCHEMA)
    conflict.add_node("enrich", enrich)
    conflict.add_node("branch_a", lambda s: {"note": "from-a"}, via_send=True)
    conflict.add_node("branch_b", lambda s: {"note": "from-b"}, via_send=True)
    conflict.add_node("merge", merge)
    conflict.add_edge(START, "enrich")
    conflict.add_conditional_edges("enrich", lambda s: [
        Send("branch_a"), Send("branch_b")])
    conflict.add_edge("enrich", "merge")
    conflict.add_edge("merge", END)
    kept = conflict.compile().invoke(
        {"lead": leads[0]}, thread_id="conflict")["state"]["note"]

    return {
        "leads": len(leads),
        "seq_executions": seq_exec,
        "fan_executions": fan_exec,
        "seq_super_steps": seq_steps,
        "fan_super_steps": fan_steps,
        "seq_time_units": seq_time,
        "fan_time_units": fan_time,
        "branch_state_copies": sends,
        "slot_results_equal": slot_equal,
        "conflict_values_written": 2,
        "conflict_values_kept": 1 if kept == "from-b" else 0,
        "conflict_survivor": kept,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
