"""Lesson 20 lab: pause between nodes, fix the state, continue.

The graph compiles with a breakpoint before the booking node. L-003's
run pauses there with an empty ledger: nothing irreversible has
happened yet, which is the point of pausing between nodes rather than
inside one. While paused, the operator corrects the lead's preferred
slot (the lead emailed: Tuesday 15:00, not Wednesday 11:00) through
update_state, which writes the edit as a new checkpoint rather than
rewriting history. The resumed run books the corrected slot.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import (BookingLedger, band_for_score, choose_slot,
                       load_leads, load_policy, load_schedule, score_lead)
from lgx.checkpoint import InMemoryCheckpointer

SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "booked_slot": {"default": None, "type": str},
    "outcome": {"default": "", "type": str},
}


def evaluate():
    policy = load_policy()
    schedule = load_schedule()
    ledger = BookingLedger()
    lead = [l for l in load_leads() if l["id"] == "L-003"][0]
    would_have_been = choose_slot(schedule, lead)

    def score(state):
        value = score_lead(state["lead"], policy)
        return {"score": value, "band": band_for_score(value, policy)}

    def book(state):
        slot = choose_slot(schedule, state["lead"])
        ledger.add(state["lead"]["id"], slot)
        return {"booked_slot": slot, "outcome": "booked"}

    graph = StateGraph(SCHEMA)
    graph.add_node("score", score)
    graph.add_node("book", book)
    graph.add_node("log", lambda s: {})
    graph.add_edge(START, "score")
    graph.add_edge("score", "book")
    graph.add_edge("book", "log")
    graph.add_edge("log", END)
    checkpointer = InMemoryCheckpointer()
    app = graph.compile(checkpointer=checkpointer,
                        interrupt_before=["book"])

    paused = app.invoke({"lead": lead}, thread_id="edit")
    entries_while_paused = len(ledger)
    before_edit = len(checkpointer.history("edit"))
    corrected = copy.deepcopy(lead)
    corrected["preferred_slot"] = {"day": "tue", "time": "15:00"}
    app.update_state("edit", {"lead": corrected})
    after_edit = len(checkpointer.history("edit"))
    final = app.invoke(None, thread_id="edit", retry=True)
    return {
        "paused_before": paused["interrupt"]["breakpoint_before"],
        "ledger_entries_while_paused": entries_while_paused,
        "original_slot_would_have_been": would_have_been,
        "edited_booked_slot": final["state"]["booked_slot"],
        "checkpoints_added_by_edit": after_edit - before_edit,
        "final_outcome": final["state"]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
