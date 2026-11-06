"""Lesson 01 lab: the same LeadPipe flow as a plain pipeline and as a
graph, run over the same twelve leads, counting what each one costs.

The pipeline is honest competition: straight-line Python calling the same
rubric and tools, with an inline approval check and an inline
clarification loop. The graph is the course's agent on the lgx stand-in.
Outcomes must agree lead for lead; the interesting numbers are the costs
that do not agree.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import (band_for_score, build_lead_agent, choose_slot,
                       load_leads, load_policy, missing_fields,
                       needs_approval, run_lead_once, score_lead)
from lgx.checkpoint import InMemoryCheckpointer


def run_pipeline(lead, policy, schedule):
    """The flow as nested function calls. Returns (outcome, calls)."""
    calls = 0
    lead = copy.deepcopy(lead)
    calls += 1  # intake
    rounds = 0
    while True:
        calls += 1  # score
        score = score_lead(lead, policy)
        band = band_for_score(score, policy)
        missing = missing_fields(lead)
        if missing and rounds < policy["clarify_max_rounds"]:
            field = missing[0]
            if lead.get("followup_answers", {}).get(field) is not None:
                calls += 1  # clarify
                lead[field] = lead["followup_answers"][field]
                rounds += 1
                continue
        break
    if missing and rounds >= policy["clarify_max_rounds"]:
        outcome = "needs_info"
    elif band == "HOT":
        if needs_approval(lead, policy):
            calls += 1  # approve (an inline human check)
            if (lead.get("approval") or "approve") != "approve":
                outcome = "approval_rejected"
                calls += 1  # crm log
                return outcome, calls
        calls += 1  # book
        outcome = "booked" if choose_slot(schedule, lead) else "no_slot"
    elif band == "WARM":
        calls += 1  # follow up
        outcome = "follow_up_scheduled"
    else:
        calls += 1  # nurture
        outcome = "nurtured"
    calls += 1  # crm log
    return outcome, calls


def evaluate():
    policy = load_policy()
    leads = load_leads()
    from lgx.agent import load_schedule
    schedule = load_schedule()

    pipeline_calls = 0
    pipeline_outcomes = {}
    for lead in leads:
        outcome, calls = run_pipeline(lead, policy, schedule)
        pipeline_outcomes[lead["id"]] = outcome
        pipeline_calls += calls

    checkpointer = InMemoryCheckpointer()
    bundle = build_lead_agent("hardened", checkpointer=checkpointer)
    graph_outcomes = {}
    graph_executions = 0
    for lead in leads:
        result, executions = run_lead_once(bundle, lead, f"lead-{lead['id']}")
        graph_outcomes[lead["id"]] = result["state"]["outcome"]
        graph_executions += executions
    checkpoint_writes = sum(
        len(checkpointer.history(f"lead-{lead['id']}")) for lead in leads)

    outcomes_equal = sum(
        1 for lead in leads
        if pipeline_outcomes[lead["id"]] == graph_outcomes[lead["id"]]
        == lead["truth"]["outcome"])
    return {
        "leads": len(leads),
        "outcomes_equal": outcomes_equal,
        "pipeline_calls": pipeline_calls,
        "graph_executions": graph_executions,
        "graph_checkpoint_writes": checkpoint_writes,
        "pipeline_checkpoint_writes": 0,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
