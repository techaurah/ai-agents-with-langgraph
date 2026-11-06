"""Lesson 14 lab: with a checkpointer attached, every super-step leaves
a snapshot, and the snapshots are the run.

L-001 (the approval case) runs on an in-memory checkpointer. The lab
counts the checkpoints (one initial, one per completed super-step, one
for the interrupt, one for the finish), finds the first checkpoint where
the score is visible, and confirms the paused thread's checkpoint says
"interrupted" with the approve node as its next step: that record is
everything a resume needs, and it is also everything an auditor needs.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads
from lgx.checkpoint import InMemoryCheckpointer


def evaluate():
    lead = [l for l in load_leads() if l["id"] == "L-001"][0]
    checkpointer = InMemoryCheckpointer()
    bundle = build_lead_agent("hardened", checkpointer=checkpointer)
    graph = bundle["graph"]
    first = graph.invoke({"lead": lead}, thread_id="ckpt")
    paused = checkpointer.latest("ckpt")
    graph.invoke(None, thread_id="ckpt", resume="approve")
    history = checkpointer.history("ckpt")
    first_scored = next(
        cp["checkpoint_id"] for cp in history
        if cp["state"]["score"] is not None)
    return {
        "checkpoints_written": len(history),
        "channels_per_checkpoint": len(history[0]["state"]),
        "first_checkpoint_with_score": first_scored,
        "paused_status": paused["status"],
        "paused_next_node": paused["next_node"],
        "first_status": first["status"],
        "final_status": history[-1]["status"],
        "final_outcome": history[-1]["state"]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
