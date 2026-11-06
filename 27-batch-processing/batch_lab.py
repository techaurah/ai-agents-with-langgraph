"""Lesson 27 lab: the batch is twelve threads, not one big loop.

All twelve leads run as separate threads on one compiled agent (the
same shape a production worker pulls from a queue). One extra malformed
submission (an unknown state channel) is mixed into the batch on
purpose: it fails at its own front door, is counted as failed, and the
other twelve complete unaffected. The outcome distribution and the
total execution count are the batch's report. Per-thread state is what
makes this boring, and boring is the goal: no shared-state locking, no
cross-lead contamination, failures priced per lead.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import GraphStructureError
from lgx.agent import build_lead_agent, load_leads, run_lead_once


def evaluate():
    bundle = build_lead_agent("hardened")
    graph = bundle["graph"]
    outcomes = {}
    executions = 0
    completed = 0
    failed = 0
    for lead in load_leads():
        result, steps = run_lead_once(bundle, lead, f"batch-{lead['id']}")
        outcomes[result["state"]["outcome"]] = \
            outcomes.get(result["state"]["outcome"], 0) + 1
        executions += steps
        completed += 1
    try:
        graph.invoke({"lead": {"id": "L-BAD"}, "bogus_channel": 1},
                     thread_id="batch-bad")
    except GraphStructureError:
        failed += 1
    return {
        "attempted": completed + failed,
        "completed": completed,
        "failed": failed,
        "total_executions": executions,
        "outcomes": outcomes,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
