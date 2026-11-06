"""Lesson 10 lab: a tool inside a node is invisible; a tool as a node is
a checkpoint, a trace entry, and a retry boundary.

The drill uses one flaky tool: the follow-up sender fails the first time
it is called for L-005. Two builds absorb that failure. The monolith does
intake, scoring, routing, the tool call, and the CRM log inside a single
node: when the tool raises, the run dies with the initial state still in
the checkpoint, zero visible progress, and recovery means doing the
whole node again. The tool-node build (the LeadPipe agent's shape) has
the tool as its own node behind a checkpointer: at the failure, the
checkpoint already holds the intake and the score, and the retry
re-executes exactly two nodes. The full agent then runs all twelve
leads with the same flaky tool in play and lands every outcome.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import (band_for_score, build_lead_agent, load_leads,
                       load_policy, run_lead_once, score_lead)
from lgx.checkpoint import InMemoryCheckpointer

SCHEMA = {
    "lead": {"default": dict, "type": dict},
    "score": {"default": None, "type": int},
    "band": {"default": "", "type": str},
    "outcome": {"default": "", "type": str},
    "crm_logged": {"default": False, "type": bool},
}


def evaluate():
    policy = load_policy()
    lead = [l for l in load_leads() if l["id"] == "L-005"][0]
    attempts = {"n": 0}

    def flaky_follow_up():
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise RuntimeError("follow-up sender unavailable (simulated)")

    # Monolith: everything inside one node.
    def everything(state):
        value = score_lead(state["lead"], policy)
        band = band_for_score(value, policy)
        if band == "WARM":
            flaky_follow_up()
        return {"score": value, "band": band,
                "outcome": "follow_up_scheduled", "crm_logged": True}

    mono_cp = InMemoryCheckpointer()
    mono = StateGraph(SCHEMA)
    mono.add_node("everything", everything)
    mono.add_edge(START, "everything")
    mono.add_edge("everything", END)
    mono_app = mono.compile(checkpointer=mono_cp)
    mono_attempts = 0
    mono_progress = None
    while True:
        mono_attempts += 1
        try:
            mono_app.invoke({"lead": lead}, thread_id="mono",
                            retry=mono_attempts > 1)
            break
        except RuntimeError:
            failed = mono_cp.latest("mono")
            mono_progress = 0 if failed["state"]["score"] is None else 1

    # Tool as node: intake, score, the tool, the log, each a node.
    attempts["n"] = 0

    def follow_up_node(state):
        flaky_follow_up()
        return {"outcome": "follow_up_scheduled"}

    tool_cp = InMemoryCheckpointer()
    tool = StateGraph(SCHEMA)
    tool.add_node("intake", lambda s: {})
    tool.add_node("score", lambda s: {
        "score": score_lead(s["lead"], policy),
        "band": band_for_score(score_lead(s["lead"], policy), policy)})
    tool.add_node("follow_up", follow_up_node)
    tool.add_node("crm_log", lambda s: {"crm_logged": True})
    tool.add_edge(START, "intake")
    tool.add_edge("intake", "score")
    tool.add_edge("score", "follow_up")
    tool.add_edge("follow_up", "crm_log")
    tool.add_edge("crm_log", END)
    tool_app = tool.compile(checkpointer=tool_cp)
    progress_at_failure = None
    try:
        tool_app.invoke({"lead": lead}, thread_id="tool")
    except RuntimeError:
        failed = tool_cp.latest("tool")
        progress_at_failure = failed["total_steps"]
    retry_result = tool_app.invoke(None, thread_id="tool", retry=True)

    bundle = build_lead_agent("hardened")
    correct = 0
    for fixture_lead in load_leads():
        result, _ = run_lead_once(bundle, fixture_lead,
                                  f"tools-{fixture_lead['id']}")
        if result["state"]["outcome"] == fixture_lead["truth"]["outcome"]:
            correct += 1

    return {
        "monolith_attempts": mono_attempts,
        "monolith_visible_progress_at_failure": mono_progress,
        "tool_graph_progress_at_failure": progress_at_failure,
        "tool_graph_retry_executions": retry_result["steps"],
        "flaky_tool_attempts": attempts["n"],
        "agent_outcomes_correct": correct,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
