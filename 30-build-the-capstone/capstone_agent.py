"""Lesson 30 lab: the capstone agent, assembled whole.

Everything the course built separately is one graph here (the factory
lives in lgx/agent.py so Lessons 12 to 28 could share it): intake, the
rubric scoring node, the clarification cycle, band routing, the approval
interrupt standing before booking for the policy-flagged HOT leads, the
idempotent booking node writing to an external ledger, and the CRM log.
Twelve leads run end to end, each on its own thread, with approval
answers taken from the fixtures and the one simulated crash absorbed by
checkpoint retry. This lesson reports what the finished agent does;
Lesson 31 grades it, and the naive variant, against the fixed gates.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads, run_lead_once


def evaluate():
    bundle = build_lead_agent("hardened")
    outcomes = {}
    matches = 0
    total_steps = 0
    for lead in load_leads():
        result, steps = run_lead_once(bundle, lead, f"cap-{lead['id']}")
        state = result["state"]
        outcomes[state["outcome"]] = outcomes.get(state["outcome"], 0) + 1
        total_steps += steps
        if state["band"] == lead["truth"]["band"] and \
                state["outcome"] == lead["truth"]["outcome"] and \
                state["score"] == lead["truth"]["score"]:
            matches += 1
    leads = len(load_leads())
    return {
        "leads": leads,
        "full_matches": matches,
        "ledger_entries": len(bundle["ledger"]),
        "crash_lead_bookings": bundle["ledger"].count_for("L-009"),
        "mean_steps": round(total_steps / leads, 2),
        "outcomes": outcomes,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
