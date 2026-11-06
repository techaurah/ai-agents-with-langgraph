"""Lesson 08 lab: the ReAct loop is a cycle with a decider in it.

Four tasks run through the canonical agent loop: a decide node asks the
model stand-in what is needed next, a tool node gathers it, and the loop
returns to decide until the stand-in answers "final". The stand-in is a
labelled decision table (see lgx/model.py), not a model: it asks for the
first missing observation in a fixed order, which is exactly the part of
a real model's behaviour this lesson can measure deterministically: how
many decisions and tool calls a loop costs, and what happens when a tool
forgets to write its observation (the loop can no longer tell it is
done, and only the step limit saves it).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, Command, ModelStandin, StateGraph, StepLimitExceeded
from lgx.agent import choose_slot, load_leads, load_schedule

SCHEMA = {
    "task": {"default": dict, "type": dict},
    "observations": {"default": dict, "type": dict},
    "done": {"default": False, "type": bool},
}

PROFILES = {
    "BrightPath Dental": {"sector": "dental", "team_size": 14},
    "Northgate Physio": {"sector": "physiotherapy", "team_size": 6},
    "Solstice Med Spa": {"sector": "med spa", "team_size": 9},
    "Cedar Legal": {"sector": "law firm", "team_size": 22},
}


def build_loop(model, broken_draft=False):
    schedule = load_schedule()

    def decide(state):
        choice = model.decide(state["observations"])
        if "final" in choice:
            return Command(update={}, goto="finish")
        return Command(update={}, goto=choice["tool"])

    def lookup_company(state):
        profile = PROFILES[state["task"]["company"]]
        obs = dict(state["observations"])
        obs["company"] = profile
        return {"observations": obs}

    def check_slot(state):
        slot = choose_slot(schedule, state["task"])
        obs = dict(state["observations"])
        obs["slot"] = slot
        return {"observations": obs}

    def draft_reply(state):
        if broken_draft:
            return {}  # the bug: work done, observation never written
        obs = dict(state["observations"])
        obs["draft"] = f"Draft for {state['task']['company']}"
        return {"observations": obs}

    graph = StateGraph(SCHEMA)
    graph.add_node("decide", decide, command_targets=(
        "lookup_company", "check_slot", "draft_reply", "finish"))
    graph.add_node("lookup_company", lookup_company)
    graph.add_node("check_slot", check_slot)
    graph.add_node("draft_reply", draft_reply)
    graph.add_node("finish", lambda s: {"done": True})
    graph.add_edge(START, "decide")
    for tool in ("lookup_company", "check_slot", "draft_reply"):
        graph.add_edge(tool, "decide")
    graph.add_edge("finish", END)
    return graph


def evaluate():
    leads = {l["id"]: l for l in load_leads()}
    tasks = []
    for lead_id in ("L-001", "L-003", "L-009", "L-010"):
        lead = leads[lead_id]
        tasks.append({"company": lead["company"],
                      "preferred_slot": lead["preferred_slot"]})

    model = ModelStandin()
    app = build_loop(model).compile(max_steps=25)
    completed = 0
    tool_executions = 0
    for i, task in enumerate(tasks):
        result = app.invoke({"task": task}, thread_id=f"task-{i}")
        if result["state"]["done"]:
            completed += 1
        tool_executions += sum(
            1 for e in result["trace"]
            if e["node"] in ("lookup_company", "check_slot", "draft_reply"))

    stuck = 0
    broken_model = ModelStandin()
    broken = build_loop(broken_model, broken_draft=True).compile(max_steps=12)
    try:
        broken.invoke({"task": tasks[0]}, thread_id="stuck")
    except StepLimitExceeded:
        stuck = 1

    return {
        "tasks": len(tasks),
        "tasks_completed": completed,
        "model_calls": model.calls,
        "tool_executions": tool_executions,
        "stuck_loops_caught": stuck,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
