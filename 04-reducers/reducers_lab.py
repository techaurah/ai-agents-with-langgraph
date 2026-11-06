"""Lesson 04 lab: reducers decide what an update means.

Three nodes each contribute one message. Under the default overwrite
reducer, the channel keeps only the last contribution: the conversation
silently loses its history. Under the append reducer, all three survive
in order. A numeric channel with the add reducer totals two increments
instead of keeping the second one. The lab finishes on the real agent:
its events channel uses append, so a finished run carries the whole path
it took, in order.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import build_lead_agent, load_leads, run_lead_once


def message_graph(reducer):
    schema = {"messages": {"default": list, "type": list}}
    if reducer:
        schema["messages"]["reducer"] = reducer
    graph = StateGraph(schema)
    for i in (1, 2, 3):
        graph.add_node(f"step{i}", lambda s, i=i: {"messages": [f"msg-{i}"]})
    graph.add_edge(START, "step1")
    graph.add_edge("step1", "step2")
    graph.add_edge("step2", "step3")
    graph.add_edge("step3", END)
    return graph.compile().invoke({}, thread_id=f"reducer-{reducer}")


def evaluate():
    overwritten = message_graph(None)["state"]["messages"]
    appended = message_graph("append")["state"]["messages"]

    counter = StateGraph({
        "rounds": {"default": 0, "reducer": "add", "type": int},
    })
    counter.add_node("a", lambda s: {"rounds": 1})
    counter.add_node("b", lambda s: {"rounds": 1})
    counter.add_edge(START, "a")
    counter.add_edge("a", "b")
    counter.add_edge("b", END)
    total = counter.compile().invoke({}, thread_id="counter")["state"]["rounds"]

    lead = [l for l in load_leads() if l["id"] == "L-001"][0]
    bundle = build_lead_agent("hardened")
    result, _ = run_lead_once(bundle, lead, "reducer-agent")
    return {
        "overwrite_kept": len(overwritten),
        "overwrite_final": overwritten,
        "append_kept": len(appended),
        "append_final": appended,
        "add_reducer_total": total,
        "agent_events": result["state"]["events"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
