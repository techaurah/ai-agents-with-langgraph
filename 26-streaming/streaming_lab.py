"""Lesson 26 lab: the same run, watched two ways.

Streaming in values mode yields the whole state after every super-step:
for L-001's first invoke that is two snapshots (intake, score) and then
the interrupt marker, because the approval pause is an event too. The
resume streams three more snapshots and the last one is the finished,
booked state. In updates mode each event is just the node name and what
it changed: four events for a WARM lead's four nodes. The stand-in
collects events during the run and then yields them (named in the
engine's docstring); the framework streams them live, which matters
for latency of first token in real systems and changes nothing about
the event contents counted here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads


def evaluate():
    leads = {l["id"]: l for l in load_leads()}
    bundle = build_lead_agent("hardened")
    graph = bundle["graph"]

    first = list(graph.stream({"lead": leads["L-001"]}, thread_id="stream-1",
                              mode="values"))
    markers = [e for e in first if "__interrupt__" in e]
    values_before = [e for e in first if "__interrupt__" not in e]
    resumed = list(graph.stream(None, thread_id="stream-1", mode="values",
                                resume="approve"))
    updates = list(graph.stream({"lead": leads["L-005"]},
                                thread_id="stream-2", mode="updates"))
    return {
        "values_events_before_pause": len(values_before),
        "interrupt_markers": len(markers),
        "values_events_after_resume": len(resumed),
        "updates_events": len(updates),
        "updates_single_key_each": all(len(e) == 1 for e in updates),
        "final_streamed_outcome": resumed[-1]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
