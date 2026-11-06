"""Lesson 18 lab: an interrupt pauses a node mid-function, and resume
runs the node again from its first line.

The approve node below does one thing before it interrupts: it appends
to a notifications list that lives outside the graph state, the stand-in
for emailing the approver. After the resume, that list has two entries.
Nothing is wrong with the code; that is the documented semantics of
interrupts (the node re-executes from the start), and it is why every
side effect placed before a pause point must be safe to repeat. Lesson
19 builds the gate that respects this; Lesson 28 makes the writes
idempotent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph, interrupt

SCHEMA = {
    "lead_id": {"default": "", "type": str},
    "approval_decision": {"default": "", "type": str},
    "outcome": {"default": "", "type": str},
}


def evaluate():
    notifications = []

    def approve(state):
        notifications.append(f"approval requested for {state['lead_id']}")
        decision = interrupt({"lead_id": state["lead_id"],
                              "action": "approve_booking"})
        return {"approval_decision": decision}

    def book(state):
        return {"outcome": "booked"}

    graph = StateGraph(SCHEMA)
    graph.add_node("approve", approve)
    graph.add_node("book", book)
    graph.add_edge(START, "approve")
    graph.add_conditional_edges(
        "approve",
        lambda s: "book" if s["approval_decision"] == "approve" else "end",
        {"book": "book", "end": END})
    graph.add_edge("book", END)
    app = graph.compile()

    first = app.invoke({"lead_id": "L-001"}, thread_id="hitl")
    payload = first["interrupt"]
    approve_executions = sum(
        1 for e in first["trace"] if e["node"] == "approve")
    second = app.invoke(None, thread_id="hitl", resume="approve")
    approve_executions += sum(
        1 for e in second["trace"] if e["node"] == "approve")
    return {
        "status_before_resume": first["status"],
        "payload_action": payload["action"],
        "payload_lead": payload["lead_id"],
        "approve_executions": approve_executions,
        "pre_interrupt_side_effects": len(notifications),
        "final_outcome": second["state"]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
