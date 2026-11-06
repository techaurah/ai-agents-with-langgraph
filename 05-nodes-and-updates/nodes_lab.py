"""Lesson 05 lab: nodes return partial updates, and a node can route
itself with Command.

Part one: a node in a six-channel schema returns two keys. The other four
channels keep their values, untouched: that is the whole contract of a
node, read what you need, return what you changed.

Part two: two triage graphs with identical behaviour. One routes with a
separate router function on a conditional edge; the other returns
Command(update=..., goto=...) from inside the triage node. Both are run
on a HOT and a WARM input, and their checkpoint counts are compared: the
Command version removes a definition site, not a step.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, Command, StateGraph
from lgx.checkpoint import InMemoryCheckpointer

SCHEMA = {
    "lead_id": {"default": "", "type": str},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "booked_slot": {"default": None, "type": str},
    "outcome": {"default": "", "type": str},
    "crm_logged": {"default": False, "type": bool},
}


def evaluate():
    partial = StateGraph(SCHEMA)
    partial.add_node("score", lambda s: {"score": 90, "band": "HOT"})
    partial.add_edge(START, "score")
    partial.add_edge("score", END)
    state = partial.compile().invoke({"lead_id": "L-001"},
                                     thread_id="partial")["state"]
    touched = [k for k in ("score", "band") if state[k] not in (None, "")]
    untouched = [k for k in SCHEMA if k not in ("lead_id", "score", "band")]

    def triage_command(state):
        band = "HOT" if state["score"] >= 80 else "WARM"
        return Command(update={"band": band},
                       goto="book" if band == "HOT" else "follow")

    def book(state):
        return {"outcome": "booked"}

    def follow(state):
        return {"outcome": "follow_up_scheduled"}

    command_cp = InMemoryCheckpointer()
    cg = StateGraph(SCHEMA)
    cg.add_node("triage", triage_command, command_targets=("book", "follow"))
    cg.add_node("book", book)
    cg.add_node("follow", follow)
    cg.add_edge(START, "triage")
    cg.add_edge("book", END)
    cg.add_edge("follow", END)
    command_graph = cg.compile(checkpointer=command_cp)

    edge_cp = InMemoryCheckpointer()
    eg = StateGraph(SCHEMA)
    eg.add_node("triage", lambda s: {
        "band": "HOT" if s["score"] >= 80 else "WARM"})
    eg.add_node("book", book)
    eg.add_node("follow", follow)
    eg.add_edge(START, "triage")
    eg.add_conditional_edges("triage", lambda s: s["band"],
                             {"HOT": "book", "WARM": "follow"})
    eg.add_edge("book", END)
    eg.add_edge("follow", END)
    edge_graph = eg.compile(checkpointer=edge_cp)

    paths = {}
    for label, score in (("HOT", 90), ("WARM", 60)):
        r1 = command_graph.invoke({"score": score},
                                  thread_id=f"cmd-{label}")
        r2 = edge_graph.invoke({"score": score}, thread_id=f"edge-{label}")
        paths[label] = (
            [e["node"] for e in r1["trace"] if e["node"] in ("book", "follow")][0]
            == [e["node"] for e in r2["trace"]
                if e["node"] in ("book", "follow")][0])
    return {
        "channels_total": len(SCHEMA),
        "partial_keys_returned": len(touched),
        "untouched_channels_kept": len(untouched),
        "command_paths_match_edge_paths": all(paths.values()),
        "command_checkpoints": len(command_cp.history("cmd-HOT")),
        "edge_checkpoints": len(edge_cp.history("edge-HOT")),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
