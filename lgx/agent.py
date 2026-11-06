"""The LeadPipe domain: one lead qualification and booking agent, assembled
from graph pieces, used across the course and graded by the capstone.

The domain mirrors the LeadPipe pattern used in Courses 3 and 6: a lead
arrives on some channel, a rubric scores it, a band routes it, and the
outcome is a booked discovery call, a scheduled follow-up, or a nurture
path. Policy (fixtures/policy.json) adds the two rules that make the graph
interesting: leads at or above the approval budget threshold may only be
booked after a human approves (an interrupt), and leads with missing
scoring fields go through a clarification cycle before routing.

`build_lead_agent` takes a `variant` because the capstone grades two
builds against gates fixed in advance:

- "hardened": approval happens before booking, the booking write is
  idempotent per lead, and clarification gets the full policy rounds.
- "as_built": the first-pass composition of the naive pieces from earlier
  lessons: the approval interrupt sits after the booking node (Lesson 19's
  anti-pattern), the booking node writes without an idempotency check
  (Lesson 28's first version), and clarification gives up after one round.

Everything here runs on the lgx stand-in engine and the bundled fixtures.
No model is called; no message leaves the machine. Bookings are rows in a
ledger object that stands in for the booking system, and the ledger is
deliberately outside the graph's state, like a real external system: the
graph cannot roll it back, which is the entire point of Lessons 16 and 28.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from .engine import END, START, StateGraph, interrupt
from .checkpoint import InMemoryCheckpointer

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"

REQUIRED_FIELDS = ("budget_usd_monthly", "decision_maker")


class SimulatedCrashError(Exception):
    """Raised by the booking node for the fixture lead whose record asks
    for a crash mid-write, so resume behaviour can be drilled for real."""


def _load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_leads():
    return _load("leads.json")


def load_schedule():
    return _load("schedule.json")


def load_policy():
    return _load("policy.json")


def load_memory_cases():
    return _load("memory.json")


# --------------------------------------------------------------------------
# Scoring rubric (identical inputs to the scoring in Course 3's LeadPipe:
# a budget bracket, a recency bracket, and a decision-maker flag).
# --------------------------------------------------------------------------

def score_lead(lead, policy):
    """Score a lead dict against the policy rubric. Missing fields score
    the policy's missing value (0); callers that care about provisional
    scores check missing_fields first."""
    rubric = policy["rubric"]
    budget = lead.get("budget_usd_monthly")
    points = 0
    if budget is not None:
        for minimum, bracket_points in rubric["budget_brackets"]:
            if budget >= minimum:
                points += bracket_points
                break
    days = lead.get("days_since_inquiry", 0)
    for max_days, bracket_points in rubric["recency_brackets"]:
        if days <= max_days:
            points += bracket_points
            break
    dm = lead.get("decision_maker")
    key = "missing" if dm is None else ("true" if dm else "false")
    points += rubric["decision_maker_points"][key]
    return points


def band_for_score(score, policy):
    if score >= policy["bands"]["hot_min"]:
        return "HOT"
    if score >= policy["bands"]["warm_min"]:
        return "WARM"
    return "NURTURE"


def missing_fields(lead):
    return [f for f in REQUIRED_FIELDS if lead.get(f) is None]


def needs_approval(lead, policy):
    budget = lead.get("budget_usd_monthly")
    return budget is not None and budget >= policy["approval_budget_threshold"]


def choose_slot(schedule, lead):
    """The booking tool's choice: the lead's preferred slot when free,
    else the next free slot the same day, else None. Pure: it reads the
    schedule snapshot in state and does not write anything."""
    preferred = lead.get("preferred_slot")
    if not preferred:
        return None
    free = {(s["day"], s["time"]) for s in schedule["slots"]
            if s["status"] == "free"}
    if (preferred["day"], preferred["time"]) in free:
        return f"{preferred['day']} {preferred['time']}"
    for slot in schedule["slots"]:
        if slot["day"] == preferred["day"] and slot["status"] == "free":
            return f"{slot['day']} {slot['time']}"
    return None


class BookingLedger:
    """The external booking system, in miniature: an append-only list the
    graph writes to and cannot unwrite. Keyed lookups are what idempotency
    is built from in Lesson 28."""

    def __init__(self):
        self.entries: list[dict] = []

    def add(self, lead_id, slot):
        self.entries.append({"lead_id": lead_id, "slot": slot})

    def has(self, lead_id):
        return any(e["lead_id"] == lead_id for e in self.entries)

    def count_for(self, lead_id):
        return sum(1 for e in self.entries if e["lead_id"] == lead_id)

    def slot_for(self, lead_id):
        for entry in self.entries:
            if entry["lead_id"] == lead_id:
                return entry["slot"]
        return None

    def __len__(self):
        return len(self.entries)


# --------------------------------------------------------------------------
# The agent graph.
# --------------------------------------------------------------------------

AGENT_SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "lead_id": {"default": "", "type": str},
    "intake_done": {"default": False, "type": bool},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "missing": {"default": list, "type": list},
    "clarify_rounds": {"default": 0, "type": int},
    "approval_decision": {"default": "", "type": str},
    "booked_slot": {"default": None, "type": str},
    "outcome": {"default": "", "type": str},
    "crm_logged": {"default": False, "type": bool},
    "events": {"default": list, "reducer": "append", "type": list},
}


def build_lead_agent(variant="hardened", checkpointer=None, ledger=None,
                     attempts=None):
    """Compile the LeadPipe agent on the stand-in engine.

    Returns a dict with the compiled graph and the external systems it
    writes to (ledger, crash-attempt counters, the mutable schedule copy),
    so a caller can inspect side effects the graph itself cannot see.
    """
    if variant not in ("hardened", "as_built"):
        raise ValueError(f"unknown variant: {variant}")
    policy = load_policy()
    ledger = ledger if ledger is not None else BookingLedger()
    attempts = attempts if attempts is not None else {}
    schedule = load_schedule()
    clarify_limit = policy["clarify_max_rounds"] if variant == "hardened" else 1
    idempotent = variant == "hardened"

    def intake(state):
        lead = state["lead"]
        return {"lead_id": lead["id"], "intake_done": True,
                "events": ["intake"]}

    def score(state):
        lead = state["lead"]
        value = score_lead(lead, policy)
        return {"score": value, "band": band_for_score(value, policy),
                "missing": missing_fields(lead), "events": ["score"]}

    def clarify(state):
        lead = copy.deepcopy(state["lead"])
        field = state["missing"][0]
        answer = lead.get("followup_answers", {}).get(field)
        if answer is not None:
            lead[field] = answer
        return {"lead": lead, "clarify_rounds": state["clarify_rounds"] + 1,
                "events": [f"clarify:{field}"]}

    def approve(state):
        decision = interrupt({
            "lead_id": state["lead_id"], "band": state["band"],
            "score": state["score"], "action": "approve_booking",
        })
        return {"approval_decision": decision, "events": ["approve"]}

    def book(state):
        lead = state["lead"]
        slot = choose_slot(schedule, lead)
        if idempotent and ledger.has(lead["id"]):
            return {"booked_slot": ledger.slot_for(lead["id"]),
                    "outcome": "booked", "events": ["book:reused"]}
        ledger.add(lead["id"], slot)
        if lead.get("crash_in_booking") and attempts.get(lead["id"], 0) == 0:
            attempts[lead["id"]] = attempts.get(lead["id"], 0) + 1
            raise SimulatedCrashError(
                f"simulated crash inside book, after the ledger write, "
                f"for {lead['id']}")
        for entry in schedule["slots"]:
            if f"{entry['day']} {entry['time']}" == slot:
                entry["status"] = "booked"
        return {"booked_slot": slot, "outcome": "booked",
                "events": ["book"]}

    def follow_up(state):
        return {"outcome": "follow_up_scheduled", "events": ["follow_up"]}

    def nurture(state):
        return {"outcome": "nurtured", "events": ["nurture"]}

    def unresolved(state):
        return {"outcome": "needs_info", "events": ["unresolved"]}

    def crm_log(state):
        outcome = state["outcome"] or (
            "approval_rejected" if state["approval_decision"] == "reject"
            else state["outcome"])
        return {"crm_logged": True, "outcome": outcome,
                "events": ["crm_log"]}

    def route_after_score(state):
        if state["missing"]:
            if state["clarify_rounds"] < clarify_limit:
                return "clarify"
            return "unresolved"
        if state["band"] == "HOT":
            if variant == "hardened" and needs_approval(state["lead"], policy):
                return "approve"
            return "book"
        if state["band"] == "WARM":
            return "follow_up"
        return "nurture"

    def route_after_approve(state):
        if variant == "as_built":
            return "crm_log"
        return "book" if state["approval_decision"] == "approve" else "crm_log"

    graph = StateGraph(AGENT_SCHEMA)
    for name, fn in (("intake", intake), ("score", score),
                     ("clarify", clarify), ("approve", approve),
                     ("book", book), ("follow_up", follow_up),
                     ("nurture", nurture), ("unresolved", unresolved),
                     ("crm_log", crm_log)):
        graph.add_node(name, fn)
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "score")
    graph.add_conditional_edges("score", route_after_score, {
        "clarify": "clarify", "approve": "approve", "book": "book",
        "follow_up": "follow_up", "nurture": "nurture",
        "unresolved": "unresolved",
    })
    graph.add_edge("clarify", "score")
    graph.add_edge("unresolved", "crm_log")
    graph.add_edge("follow_up", "crm_log")
    graph.add_edge("nurture", "crm_log")
    graph.add_edge("crm_log", END)
    if variant == "hardened":
        graph.add_conditional_edges("approve", route_after_approve,
                                    {"book": "book", "crm_log": "crm_log"})
        graph.add_edge("book", "crm_log")
    else:
        # as_built: booking happens on the score route; the approval
        # interrupt is bolted on afterwards, where it can no longer stop
        # anything (Lesson 19's anti-pattern, kept for the capstone).
        graph.add_edge("book", "approve")
        graph.add_conditional_edges("approve", route_after_approve,
                                    {"crm_log": "crm_log"})
    compiled = graph.compile(
        checkpointer=checkpointer or InMemoryCheckpointer(), max_steps=25)
    return {"graph": compiled, "ledger": ledger, "attempts": attempts,
            "schedule": schedule, "policy": policy}


def run_lead_once(bundle, lead, thread_id):
    """Drive one lead through a built agent, answering its approval
    interrupt from the fixture's recorded decision and retrying once after
    a simulated crash. Returns (final_result, executions) where executions
    counts every node execution across all invoke calls for the thread,
    including re-executions."""
    graph = bundle["graph"]

    def resilient(*args, **kwargs):
        # A crash can strike on any invoke, including a resume (L-009
        # crashes inside book, which runs after the approval resume), so
        # every call gets the same retry-from-checkpoint treatment.
        try:
            return graph.invoke(*args, **kwargs)
        except SimulatedCrashError:
            return graph.invoke(None, thread_id=thread_id, retry=True)

    result = resilient({"lead": copy.deepcopy(lead)}, thread_id=thread_id)
    while result["status"] == "interrupted":
        decision = lead.get("approval") or "approve"
        result = resilient(None, thread_id=thread_id, resume=decision)
    return result, result["total_steps"]
