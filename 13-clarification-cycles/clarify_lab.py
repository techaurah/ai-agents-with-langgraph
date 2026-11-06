"""Lesson 13 lab: route after you know, not before.

Two builds of the same flow differ in exactly one edge. The no-cycle
build routes on the provisional score; the cycle build sends leads with
missing fields back through a clarify node (which fills one field per
round from the lead's recorded answers, the stand-in for asking) and
scores again. Everything else (rubric, approval interrupt, actions) is
shared. On the fixture set the cycle costs three extra node executions
across two leads and buys two score corrections and one outcome
correction: without it, L-004's completed HOT record is handled as a
WARM follow-up. With an exhausted round budget the cycle build still
fails honestly: Lesson 31's as-built variant keeps that failure.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph, interrupt
from lgx.agent import (band_for_score, choose_slot, load_leads, load_policy,
                       load_schedule, missing_fields, needs_approval,
                       run_lead_once, build_lead_agent, score_lead)

SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "missing": {"default": list, "type": list},
    "outcome": {"default": "", "type": str},
}


def build_no_cycle():
    policy = load_policy()
    schedule = load_schedule()

    def score(state):
        value = score_lead(state["lead"], policy)
        return {"score": value, "band": band_for_score(value, policy),
                "missing": missing_fields(state["lead"])}

    def approve(state):
        decision = interrupt({"action": "approve_booking"})
        if decision != "approve":
            return {"outcome": "approval_rejected"}
        return {}

    def book(state):
        slot = choose_slot(schedule, state["lead"])
        return {"outcome": "booked" if slot else "no_slot"}

    def route(state):
        if state["outcome"] == "approval_rejected":
            return "log"
        if state["band"] == "HOT":
            return "approve" if needs_approval(state["lead"], policy) \
                else "book"
        return "follow_up" if state["band"] == "WARM" else "nurture"

    graph = StateGraph(SCHEMA)
    graph.add_node("score", score)
    graph.add_node("approve", approve)
    graph.add_node("book", book)
    graph.add_node("follow_up", lambda s: {"outcome": "follow_up_scheduled"})
    graph.add_node("nurture", lambda s: {"outcome": "nurtured"})
    graph.add_node("log", lambda s: {})
    def route_after_approve(state):
        return "log" if state["outcome"] == "approval_rejected" else "book"

    graph.add_edge(START, "score")
    graph.add_conditional_edges("score", route, {
        "approve": "approve", "book": "book", "follow_up": "follow_up",
        "nurture": "nurture", "log": "log"})
    graph.add_conditional_edges("approve", route_after_approve, {
        "book": "book", "log": "log"})
    graph.add_edge("book", "log")
    graph.add_edge("follow_up", "log")
    graph.add_edge("nurture", "log")
    graph.add_edge("log", END)
    return graph.compile()


def evaluate():
    leads = load_leads()

    no_cycle = build_no_cycle()
    nc_scores = 0
    nc_outcomes = 0
    for lead in leads:
        result = no_cycle.invoke({"lead": lead},
                                 thread_id=f"nc-{lead['id']}")
        while result["status"] == "interrupted":
            result = no_cycle.invoke(
                None, thread_id=f"nc-{lead['id']}",
                resume=lead.get("approval") or "approve")
        if result["state"]["score"] == lead["truth"]["score"]:
            nc_scores += 1
        if result["state"]["outcome"] == lead["truth"]["outcome"]:
            nc_outcomes += 1

    bundle = build_lead_agent("hardened")
    wc_scores = 0
    rounds_total = 0
    rounds_max = 0
    for lead in leads:
        result, _ = run_lead_once(bundle, lead, f"wc-{lead['id']}")
        rounds = sum(1 for e in result["trace"] if e["node"] == "clarify")
        rounds_total += rounds
        rounds_max = max(rounds_max, rounds)
        if result["state"]["score"] == lead["truth"]["score"]:
            wc_scores += 1
    return {
        "clarify_rounds_total": rounds_total,
        "max_rounds_on_one_lead": rounds_max,
        "with_cycle_score_matches": wc_scores,
        "without_cycle_score_matches": nc_scores,
        "without_cycle_outcome_matches": nc_outcomes,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
