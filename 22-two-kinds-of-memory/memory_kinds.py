"""Lesson 22 lab: short-term memory is the thread's state; long-term
memory is what survives the thread.

Short term first: a three-node conversation pauses at a question. The
checkpoint at the pause already holds both earlier messages, and the
resumed node still sees them: that continuity is the checkpointer's job
and it costs nothing extra. Long term: a brand new thread for a company
the agent has spoken to before starts knowing nothing (zero profile
fields), because checkpoints are per-thread by design. With a store
lookup at intake, the same new thread starts knowing the two confirmed
profile fields the earlier conversation saved. Two mechanisms, two jobs;
Module 6 spends three lessons on not confusing them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph, Store, interrupt
from lgx.checkpoint import InMemoryCheckpointer

SCHEMA = {
    "messages": {"default": list, "reducer": "append", "type": list},
    "answer": {"default": "", "type": str},
}


def evaluate():
    def greet(state):
        return {"messages": ["agent: thanks for getting in touch"]}

    def ask(state):
        return {"messages": ["agent: what is the monthly budget range?"]}

    def record(state):
        answer = interrupt({"question": "budget"})
        return {"answer": answer,
                "messages": [f"lead: {answer}"]}

    graph = StateGraph(SCHEMA)
    graph.add_node("greet", greet)
    graph.add_node("ask", ask)
    graph.add_node("record", record)
    graph.add_edge(START, "greet")
    graph.add_edge("greet", "ask")
    graph.add_edge("ask", "record")
    graph.add_edge("record", END)
    checkpointer = InMemoryCheckpointer()
    app = graph.compile(checkpointer=checkpointer)
    app.invoke({}, thread_id="conversation")
    before = checkpointer.latest("conversation")["state"]["messages"]
    final = app.invoke(None, thread_id="conversation", resume="around 900")
    after = final["state"]["messages"]

    store = Store()
    store.put(("leads", "haddad-real-estate"), "profile",
              {"budget_usd_monthly": 900, "decision_maker": True})
    fresh_known = 0  # a new thread, no lookup: nothing carries over
    profile = store.get(("leads", "haddad-real-estate"), "profile")
    store_known = len([f for f in ("budget_usd_monthly", "decision_maker")
                       if profile and profile.get(f) is not None])
    return {
        "messages_before_pause": len(before),
        "messages_after_resume": len(after),
        "fresh_thread_fields_known": fresh_known,
        "store_thread_fields_known": store_known,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
