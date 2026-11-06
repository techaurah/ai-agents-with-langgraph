"""Lesson 02 lab: open up one run and look at its moving parts.

One WARM lead (no approval, no clarification) goes through the agent
graph. The lab reads the run three ways: the execution trace, the
checkpoint history (one snapshot per super-step boundary), and the
streamed state events. A fourth check compiles a graph with a deliberate
orphaned node to show compile() doing the structural check the framework
documentation describes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, GraphStructureError, StateGraph
from lgx.agent import build_lead_agent, load_leads
from lgx.checkpoint import InMemoryCheckpointer


def evaluate():
    warm = [l for l in load_leads() if l["id"] == "L-005"][0]
    checkpointer = InMemoryCheckpointer()
    bundle = build_lead_agent("hardened", checkpointer=checkpointer)
    graph = bundle["graph"]
    result = graph.invoke({"lead": warm}, thread_id="anatomy")
    history = checkpointer.history("anatomy")
    trace_nodes = [entry["node"] for entry in result["trace"]]

    streamed = list(graph.stream({"lead": warm}, thread_id="anatomy-stream",
                                 mode="values"))

    orphan_errors = 0
    try:
        bad = StateGraph({"x": {"default": 0, "type": int}})
        bad.add_node("used", lambda s: {"x": 1})
        bad.add_node("lost", lambda s: {"x": 2})
        bad.add_edge(START, "used")
        bad.add_edge("used", END)
        bad.compile()
    except GraphStructureError:
        orphan_errors = 1

    return {
        "final_status": result["status"],
        "trace_nodes": trace_nodes,
        "checkpoints_written": len(history),
        "checkpoint_next_nodes": [cp["next_node"] for cp in history],
        "stream_values_events": len(streamed),
        "orphan_errors_caught": orphan_errors,
        "final_outcome": result["state"]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
