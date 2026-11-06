"""Lesson 25 lab: build the qualification flow once, use it as a node
in two different graphs.

The qualification subgraph (intake, score, and the clarification cycle)
is compiled on its own schema. Parent A is the agent shape: qualify,
then route by band to an action. Parent B is a reporting shape: qualify,
then count. Both parents run the same twelve leads through the same
compiled subgraph object, invoked 24 times in total, and both see the
same bands the standalone rubric produces (12 of 12 in the agent parent;
a 5/4/3 band split in the report). The subgraph's internals (its own
threads, its own checkpoints) never leak into either parent's state:
parents only receive the channels the two schemas share.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import (band_for_score, load_leads, load_policy,
                       missing_fields, score_lead)

QUAL_SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "missing": {"default": list, "type": list},
    "clarify_rounds": {"default": 0, "type": int},
}


def build_qualification_subgraph():
    policy = load_policy()

    def score(state):
        value = score_lead(state["lead"], policy)
        return {"score": value, "band": band_for_score(value, policy),
                "missing": missing_fields(state["lead"])}

    def clarify(state):
        import copy
        lead = copy.deepcopy(state["lead"])
        field = state["missing"][0]
        lead[field] = lead["followup_answers"][field]
        return {"lead": lead,
                "clarify_rounds": state["clarify_rounds"] + 1}

    def route(state):
        if state["missing"] and state["clarify_rounds"] < \
                policy["clarify_max_rounds"]:
            return "clarify"
        return "done"

    graph = StateGraph(QUAL_SCHEMA)
    graph.add_node("score", score)
    graph.add_node("clarify", clarify)
    graph.add_edge(START, "score")
    graph.add_conditional_edges("score", route,
                                {"clarify": "clarify", "done": END})
    graph.add_edge("clarify", "score")
    return graph.compile()


def evaluate():
    subgraph = build_qualification_subgraph()
    leads = load_leads()

    agent_schema = dict(QUAL_SCHEMA)
    agent_schema["outcome"] = {"default": "", "type": str}
    agent = StateGraph(agent_schema)
    agent.add_node("qualify", subgraph)
    for band, outcome in (("book", "booked"), ("follow", "follow_up_scheduled"),
                          ("nurture", "nurtured")):
        agent.add_node(band, lambda s, o=outcome: {"outcome": o})
        agent.add_edge(band, END)
    agent.add_edge(START, "qualify")
    agent.add_conditional_edges("qualify", lambda s: s["band"], {
        "HOT": "book", "WARM": "follow", "NURTURE": "nurture"})
    agent_app = agent.compile()

    band_matches = 0
    invocations = 0
    for lead in leads:
        result = agent_app.invoke({"lead": lead},
                                  thread_id=f"agent-{lead['id']}")
        invocations += sum(1 for e in result["trace"]
                           if e["node"] == "qualify")
        if result["state"]["band"] == lead["truth"]["band"]:
            band_matches += 1

    report_schema = dict(QUAL_SCHEMA)
    report_schema["counted"] = {"default": False, "type": bool}
    report = StateGraph(report_schema)
    report.add_node("qualify", subgraph)
    report.add_node("count", lambda s: {"counted": True})
    report.add_edge(START, "qualify")
    report.add_edge("qualify", "count")
    report.add_edge("count", END)
    report_app = report.compile()
    counts = {"HOT": 0, "WARM": 0, "NURTURE": 0}
    for lead in leads:
        result = report_app.invoke({"lead": lead},
                                   thread_id=f"report-{lead['id']}")
        invocations += sum(1 for e in result["trace"]
                           if e["node"] == "qualify")
        counts[result["state"]["band"]] += 1

    return {
        "leads": len(leads),
        "subgraph_invocations": invocations,
        "agent_band_matches": band_matches,
        "report_band_counts": counts,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
