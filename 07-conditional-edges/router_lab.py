"""Lesson 07 lab: a router reads state and nothing else.

The twelve fixture leads go through intake and scoring, then a router
function sends each to one of three path nodes by band. The lab counts
the routes, checks the router's decision set against the edge mapping,
and flags the one lead whose provisional route disagrees with its truth
band: L-004 arrives with no budget, scores as a provisional WARM, and
would be routed to follow-up even though its completed record is HOT.
Routers are only as good as the state they read; Lesson 13 fixes the
ordering with a clarification cycle before the route.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import (band_for_score, load_leads, load_policy, score_lead)

SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "path": {"default": "", "type": str},
}


def evaluate():
    policy = load_policy()
    decisions = set()

    def score(state):
        value = score_lead(state["lead"], policy)
        return {"score": value, "band": band_for_score(value, policy)}

    def router(state):
        decisions.add(state["band"])
        return state["band"]

    graph = StateGraph(SCHEMA)
    graph.add_node("score", score)
    for band, path in (("HOT", "book_path"), ("WARM", "follow_path"),
                       ("NURTURE", "nurture_path")):
        graph.add_node(path, lambda s, p=path: {"path": p})
        graph.add_edge(path, END)
    graph.add_edge(START, "score")
    graph.add_conditional_edges("score", router, {
        "HOT": "book_path", "WARM": "follow_path", "NURTURE": "nurture_path",
    })
    app = graph.compile()

    by_path = {"book_path": 0, "follow_path": 0, "nurture_path": 0}
    misroutes = 0
    for lead in load_leads():
        result = app.invoke({"lead": lead}, thread_id=f"route-{lead['id']}")
        by_path[result["state"]["path"]] += 1
        if result["state"]["band"] != lead["truth"]["band"]:
            misroutes += 1
    return {
        "routed": sum(by_path.values()),
        "by_path": by_path,
        "decisions_covered": len(decisions),
        "provisional_misroutes": misroutes,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
