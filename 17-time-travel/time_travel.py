"""Lesson 17 lab: fork a finished run and change one fact.

L-012 finished as a WARM follow-up (score 78, two points under HOT). The
lab walks its checkpoint history back to the moment just after intake,
forks that checkpoint into a new thread, edits the forked state (the
budget was actually 1500, and the lead can do Monday 09:00), and resumes.
The fork re-scores at 88, pauses for the approval the new budget
triggers, and books. The original thread is untouched: still 78, still
a follow-up. Time travel here is not nostalgia; it is how you answer
"what would the agent have done if the data had been right" without
rerunning the world.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads
from lgx.checkpoint import InMemoryCheckpointer


def evaluate():
    lead = [l for l in load_leads() if l["id"] == "L-012"][0]
    checkpointer = InMemoryCheckpointer()
    bundle = build_lead_agent("hardened", checkpointer=checkpointer)
    graph = bundle["graph"]
    original = graph.invoke({"lead": lead}, thread_id="original")
    history = checkpointer.history("original")
    after_intake = next(cp for cp in history if cp["next_node"] == "score")

    graph.fork("original", after_intake["checkpoint_id"], "whatif")
    corrected = copy.deepcopy(lead)
    corrected["budget_usd_monthly"] = 1500
    corrected["preferred_slot"] = {"day": "mon", "time": "09:00"}
    graph.update_state("whatif", {"lead": corrected})
    forked = graph.invoke(None, thread_id="whatif", retry=True)
    paused = forked["status"] == "interrupted"
    if paused:
        forked = graph.invoke(None, thread_id="whatif", resume="approve")

    original_after = checkpointer.latest("original")
    return {
        "original_score": original["state"]["score"],
        "original_outcome": original["state"]["outcome"],
        "forked_from_checkpoint": after_intake["checkpoint_id"],
        "fork_paused_for_approval": paused,
        "forked_score": forked["state"]["score"],
        "forked_outcome": forked["state"]["outcome"],
        "forked_slot": forked["state"]["booked_slot"],
        "original_unchanged": original_after["state"]["score"] == 78
        and original_after["state"]["outcome"] == "follow_up_scheduled",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
