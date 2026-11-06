"""Lesson 06 lab: edges decide where a run goes, and what stops it.

Three graphs. A well-formed one reaches END and reports done. A ping-pong
cycle with no exit condition would run forever in a chain framework that
trusts the author; here the compiled step limit stops it, and the
checkpointer shows exactly how many executions happened before the stop.
A graph whose node has no outgoing path never runs at all: compile()
rejects it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, GraphStructureError, StateGraph, StepLimitExceeded
from lgx.checkpoint import InMemoryCheckpointer

SCHEMA = {"count": {"default": 0, "type": int}}


def evaluate():
    ok = StateGraph(SCHEMA)
    ok.add_node("once", lambda s: {"count": s["count"] + 1})
    ok.add_edge(START, "once")
    ok.add_edge("once", END)
    normal = ok.compile().invoke({}, thread_id="ok")

    cycle_cp = InMemoryCheckpointer()
    cycle = StateGraph(SCHEMA)
    cycle.add_node("ping", lambda s: {"count": s["count"] + 1})
    cycle.add_node("pong", lambda s: {"count": s["count"] + 1})
    cycle.add_edge(START, "ping")
    cycle.add_edge("ping", "pong")
    cycle.add_edge("pong", "ping")
    stopped_at = None
    try:
        cycle.compile(checkpointer=cycle_cp, max_steps=10).invoke(
            {}, thread_id="cycle")
    except StepLimitExceeded:
        stopped_at = cycle_cp.latest("cycle")["total_steps"]

    compile_errors = 0
    broken = StateGraph(SCHEMA)
    broken.add_node("stranded", lambda s: {"count": 1})
    broken.add_edge(START, "stranded")
    try:
        broken.compile()
    except GraphStructureError:
        compile_errors = 1

    return {
        "normal_status": normal["status"],
        "normal_executions": normal["total_steps"],
        "step_limit": 10,
        "cycle_stopped_at": stopped_at,
        "compile_errors_caught": compile_errors,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
