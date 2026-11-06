"""Lesson 19 lab: an approval gate only gates if it stands before the
thing it approves.

Two builds of the LeadPipe agent, two leads. The hardened build places
the approval interrupt before the booking node: L-001 (approved) books
with approval recorded first in its trace, and L-002 (rejected) never
reaches the booking node at all, zero ledger entries. The as-built
variant bolts the same interrupt on after the booking node, the mistake
this lesson exists to prevent: L-002 is rejected, politely, after it has
already been booked. The rejection is recorded; the booking stands. One
policy escape, measured in the ledger the graph cannot unwrite.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import build_lead_agent, load_leads, run_lead_once


def approval_precedes_booking(bundle, lead):
    graph = bundle["graph"]
    thread = f"gate-{lead['id']}"
    result = graph.invoke({"lead": lead}, thread_id=thread)
    sequence = [e["node"] for e in result["trace"]]
    if result["status"] == "interrupted":
        result = graph.invoke(None, thread_id=thread, resume="approve")
        sequence += [e["node"] for e in result["trace"]]
    if "book" not in sequence:
        return True  # never booked: ordering cannot be violated
    return sequence.index("approve") < sequence.index("book")


def evaluate():
    leads = {l["id"]: l for l in load_leads()}
    hardened = build_lead_agent("hardened")
    run_lead_once(hardened, leads["L-001"], "gate-h-L-001")
    rej_h = run_lead_once(hardened, leads["L-002"], "gate-h-L-002")
    hardened_order = approval_precedes_booking(
        build_lead_agent("hardened"), leads["L-001"])

    as_built = build_lead_agent("as_built")
    run_lead_once(as_built, leads["L-001"], "gate-a-L-001")
    run_lead_once(as_built, leads["L-002"], "gate-a-L-002")
    asbuilt_order = approval_precedes_booking(
        build_lead_agent("as_built"), leads["L-001"])

    return {
        "hardened_rejected_bookings": hardened["ledger"].count_for("L-002"),
        "asbuilt_rejected_bookings": as_built["ledger"].count_for("L-002"),
        "hardened_approval_before_booking": hardened_order,
        "asbuilt_approval_before_booking": asbuilt_order,
        "hardened_rejected_outcome": rej_h[0]["state"]["outcome"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
