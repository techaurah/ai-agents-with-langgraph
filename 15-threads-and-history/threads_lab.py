"""Lesson 15 lab: a thread is one conversation, and threads do not leak.

L-001 is driven to its approval pause. While it sits paused, L-005 runs
to completion on its own thread against the same checkpointer. Then
L-001 resumes and books. The lab verifies the isolation both ways:
L-005's final state carries no approval decision, L-001's carries no
follow-up outcome, and the checkpointer holds exactly two threads.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads
from lgx.checkpoint import InMemoryCheckpointer


def evaluate():
    leads = {l["id"]: l for l in load_leads()}
    checkpointer = InMemoryCheckpointer()
    bundle = build_lead_agent("hardened", checkpointer=checkpointer)
    graph = bundle["graph"]

    paused = graph.invoke({"lead": leads["L-001"]}, thread_id="thread-A")
    other = graph.invoke({"lead": leads["L-005"]}, thread_id="thread-B")
    resumed = graph.invoke(None, thread_id="thread-A", resume="approve")

    bleed = 0
    if other["state"]["approval_decision"] != "":
        bleed += 1
    if other["state"]["booked_slot"] is not None:
        bleed += 1
    if resumed["state"]["outcome"] == "follow_up_scheduled":
        bleed += 1
    return {
        "threads": len(checkpointer.threads()),
        "paused_status": paused["status"],
        "other_thread_outcome": other["state"]["outcome"],
        "resumed_outcome": resumed["state"]["outcome"],
        "state_bleed_fields": bleed,
        "history_lengths": {
            "thread-A": len(checkpointer.history("thread-A")),
            "thread-B": len(checkpointer.history("thread-B")),
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
