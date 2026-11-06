"""Lesson 03 lab: what a state schema actually buys you.

The same bad node (it writes a string into the score channel) runs
against two schemas. With no declared types, nothing catches it at the
state boundary: validation has nothing to check, and the failure surfaces
later, downstream, inside the band calculation. With declared types, the
engine rejects the update at the moment the node returns it, naming the
channel. The lab also counts how much of a fresh state the schema's
defaults fill in for free.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, GraphStructureError, StateGraph
from lgx.agent import band_for_score, load_policy
from lgx.engine import apply_update, validate_state

UNTYPED = {
    "lead_id": {"default": ""},
    "score": {"default": None},
    "band": {"default": ""},
    "events": {"default": list, "reducer": "append"},
}
TYPED = {
    "lead_id": {"default": "", "type": str},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "events": {"default": list, "reducer": "append", "type": list},
}


def bad_node(state):
    return {"score": "ninety"}


def evaluate():
    policy = load_policy()

    untyped_graph = StateGraph(UNTYPED)
    untyped_graph.add_node("bad", bad_node)
    untyped_graph.add_edge(START, "bad")
    untyped_graph.add_edge("bad", END)
    result = untyped_graph.compile().invoke({}, thread_id="untyped")
    untyped_schema_errors = len(validate_state(UNTYPED, result["state"]))
    downstream_failures = 0
    try:
        band_for_score(result["state"]["score"], policy)
    except TypeError:
        downstream_failures = 1

    typed_errors = 0
    typed_graph = StateGraph(TYPED)
    typed_graph.add_node("bad", bad_node)
    typed_graph.add_edge(START, "bad")
    typed_graph.add_edge("bad", END)
    try:
        typed_graph.compile().invoke({}, thread_id="typed")
    except GraphStructureError:
        typed_errors = 1

    fresh = {}
    apply_update(TYPED, fresh, {})
    from lgx.engine import _default_state
    defaults = _default_state(TYPED)
    return {
        "untyped_schema_errors": untyped_schema_errors,
        "untyped_downstream_failures": downstream_failures,
        "typed_errors_caught_at_boundary": typed_errors,
        "schema_channels": len(TYPED),
        "default_channels_filled": len(defaults),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
