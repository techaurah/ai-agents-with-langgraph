"""Lesson 12 lab: the whole agent, read as a set of paths.

The twelve leads run through the hardened LeadPipe agent, driven by hand
here so the pauses are visible: three threads stop at the approval
interrupt (the three policy-flagged HOT leads), and the set walks seven
distinct node paths between them (approval then book, approval then
rejection, direct book, clarify then book, follow-up, clarify twice then
nurture, plain nurture). Paths collapse an interrupt's re-execution (the
approval node appears twice in a row in a resumed thread's trace, once
for the pause and once for the resume; it is one logical stage). Routing
by band sounds like one conditional edge; in a real flow it is a small
path inventory, and the inventory is what you end up testing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import SimulatedCrashError, build_lead_agent, load_leads


def evaluate():
    bundle = build_lead_agent("hardened")
    graph = bundle["graph"]
    paths = set()
    paused = 0
    outcomes = {"booked": 0, "follow_up_scheduled": 0, "nurtured": 0,
                "approval_rejected": 0}
    for lead in load_leads():
        thread = f"paths-{lead['id']}"

        def call(*args, **kwargs):
            try:
                return graph.invoke(*args, **kwargs)
            except SimulatedCrashError:
                return graph.invoke(None, thread_id=thread, retry=True)

        result = call({"lead": lead}, thread_id=thread)
        sequence = [e["node"] for e in result["trace"]]
        if result["status"] == "interrupted":
            paused += 1
            result = call(None, thread_id=thread,
                          resume=lead.get("approval") or "approve")
            sequence += [e["node"] for e in result["trace"]]
        collapsed = tuple(node for i, node in enumerate(sequence)
                          if i == 0 or node != sequence[i - 1])
        paths.add(collapsed)
        outcomes[result["state"]["outcome"]] += 1
    return {
        "leads": 12,
        "distinct_paths": len(paths),
        "threads_paused_for_approval": paused,
        "outcomes": outcomes,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
