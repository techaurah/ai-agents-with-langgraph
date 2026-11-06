"""Lesson 21 lab: the paths a gate takes when the answer is no, and
when the answer is not an answer at all.

A small approval-gated graph is driven with three resume values. Only
the exact string "approve" books; "reject" routes to the rejection
path, and "maybe" (a tired approver, a malformed webhook, a UI bug)
also books nothing: the gate fails closed, because the routing rule is
an equality check on approval, not a check for rejection. The lab then
counts escalations in the full twelve-lead run: every approval_rejected
outcome is a thread a human now owns, and there is exactly one.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph, interrupt
from lgx.agent import (BookingLedger, build_lead_agent, load_leads,
                       run_lead_once)

SCHEMA = {
    "lead_id": {"default": "", "type": str},
    "approval_decision": {"default": "", "type": str},
    "outcome": {"default": "", "type": str},
}


def gated_run(decision, ledger):
    def approve(state):
        answer = interrupt({"action": "approve_booking"})
        if answer == "approve":
            return {"approval_decision": answer}
        return {"approval_decision": answer, "outcome": "approval_rejected"}

    def book(state):
        ledger.add(state["lead_id"], "tue 10:00")
        return {"outcome": "booked"}

    graph = StateGraph(SCHEMA)
    graph.add_node("approve", approve)
    graph.add_node("book", book)
    graph.add_node("escalate", lambda s: {})
    graph.add_edge(START, "approve")
    graph.add_conditional_edges(
        "approve",
        lambda s: "book" if s["approval_decision"] == "approve"
        else "escalate",
        {"book": "book", "escalate": "escalate"})
    graph.add_edge("book", END)
    graph.add_edge("escalate", END)
    app = graph.compile()
    app.invoke({"lead_id": "L-002"}, thread_id=f"decision-{decision}")
    return app.invoke(None, thread_id=f"decision-{decision}",
                      resume=decision)


def evaluate():
    bookings = {}
    for decision in ("approve", "reject", "maybe"):
        ledger = BookingLedger()
        gated_run(decision, ledger)
        bookings[decision] = len(ledger)

    bundle = build_lead_agent("hardened")
    escalations = []
    for lead in load_leads():
        result, _ = run_lead_once(bundle, lead, f"esc-{lead['id']}")
        if result["state"]["outcome"] == "approval_rejected":
            escalations.append(lead["id"])
    return {
        "bookings_by_decision": bookings,
        "escalations_in_full_run": len(escalations),
        "escalated_lead": escalations[0] if escalations else None,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
