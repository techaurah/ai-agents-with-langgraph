"""Lesson 31 lab: both capstone variants, graded against the gates that
were fixed before either was built.

A policy escape is a ledger booking for a lead that was rejected at
approval, or that was booked without its required approval being
granted first. Steps are checkpointed node executions per lead,
re-executions after interrupts and retries included, which is why the
as-built variant's extra approval pauses show up in its mean.

The as-built variant is the first-pass composition of the naive pieces
from the lessons: the approval interrupt bolted on after the booking
node (Lesson 19's anti-pattern), the booking node without an
idempotency check (Lesson 28, part two), and clarification limited to a
single round. It fails four of the six gates: it books the rejected
lead (one escape, and its outcome disagrees with truth), it gives up on
L-008's second missing field, it double-books the crash lead, and its
ledger holds six entries where the truth has four bookings. Its band
accuracy is perfect and its step count passes: routing was never its
problem. The hardened variant changes exactly those three decisions
and passes all six gates.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads, needs_approval, \
    run_lead_once

GATES_PATH = Path(__file__).resolve().parents[1] / \
    "29-capstone-spec" / "capstone" / "gates.json"


def evaluate_variant(variant, leads, policy):
    bundle = build_lead_agent(variant)
    graph = bundle["graph"]
    band_hits = 0
    task_hits = 0
    total_steps = 0
    escapes = 0
    for lead in leads:
        result, steps = run_lead_once(bundle, lead, f"{variant}-{lead['id']}")
        state = result["state"]
        total_steps += steps
        if state["band"] == lead["truth"]["band"]:
            band_hits += 1
        if state["outcome"] == lead["truth"]["outcome"] and \
                state["score"] == lead["truth"]["score"]:
            task_hits += 1
        booked = bundle["ledger"].count_for(lead["id"]) > 0
        if booked and lead["truth"]["outcome"] != "booked":
            escapes += 1
    n = len(leads)
    return {
        "band_accuracy": round(band_hits / n, 4),
        "task_success_rate": round(task_hits / n, 4),
        "policy_escapes": escapes,
        "crash_lead_bookings": bundle["ledger"].count_for("L-009"),
        "booking_ledger_entries": len(bundle["ledger"]),
        "mean_steps": round(total_steps / n, 2),
    }


def grade(metrics, gates):
    checks = {
        "band_accuracy_min": metrics["band_accuracy"]
        >= gates["band_accuracy_min"],
        "task_success_rate_min": metrics["task_success_rate"]
        >= gates["task_success_rate_min"],
        "policy_escapes_max": metrics["policy_escapes"]
        <= gates["policy_escapes_max"],
        "crash_lead_bookings_exact": metrics["crash_lead_bookings"]
        == gates["crash_lead_bookings_exact"],
        "booking_ledger_entries_exact": metrics["booking_ledger_entries"]
        == gates["booking_ledger_entries_exact"],
        "mean_steps_max": metrics["mean_steps"] <= gates["mean_steps_max"],
    }
    return {"checks": checks, "passed": sum(checks.values()),
            "total": len(checks)}


def evaluate():
    gates_doc = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    gates = gates_doc["capstone_system"]["gates"]
    from lgx.agent import load_policy
    policy = load_policy()
    leads = load_leads()
    report = {}
    for variant in ("as_built", "hardened"):
        metrics = evaluate_variant(variant, leads, policy)
        report[variant] = {**metrics, "grade": grade(metrics, gates)}
    return report


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
