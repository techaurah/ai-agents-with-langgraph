"""Lesson 28 lab: retries are easy; not repeating the side effect is
the work.

Three booking nodes, three failure manners. (1) Flaky-before-write: the
node raises before touching the ledger, the checkpoint retry re-runs
it, one booking results: retries alone suffice. (2) Write-then-crash,
no protection: the node writes, then raises; the retry cannot know the
write happened, so it writes again: two bookings for one lead, the
duplicate every booking system eventually meets. (3) Write-then-crash
with an idempotency key: the node checks the ledger for the lead first
and reuses the existing booking on the retry: one booking, same crash.
The crash in (3) is not prevented; it is made harmless. This is the
exact difference between the capstone's two variants.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import END, START, StateGraph
from lgx.agent import BookingLedger

SCHEMA = {
    "lead_id": {"default": "", "type": str},
    "booked_slot": {"default": None, "type": str},
    "outcome": {"default": "", "type": str},
}


def run_booking_graph(book_fn, lead_id):
    graph = StateGraph(SCHEMA)
    graph.add_node("book", book_fn)
    graph.add_node("log", lambda s: {})
    graph.add_edge(START, "book")
    graph.add_edge("book", "log")
    graph.add_edge("log", END)
    app = graph.compile()
    try:
        return app.invoke({"lead_id": lead_id}, thread_id=f"t-{lead_id}")
    except RuntimeError:
        return app.invoke(None, thread_id=f"t-{lead_id}", retry=True)


def evaluate():
    # (1) Flaky before the write.
    ledger1 = BookingLedger()
    attempts1 = {"n": 0}

    def flaky(state):
        attempts1["n"] += 1
        if attempts1["n"] == 1:
            raise RuntimeError("booking service unavailable (simulated)")
        ledger1.add(state["lead_id"], "tue 10:00")
        return {"booked_slot": "tue 10:00", "outcome": "booked"}

    run_booking_graph(flaky, "L-101")

    # (2) Write, then crash, no idempotency.
    ledger2 = BookingLedger()
    attempts2 = {"n": 0}

    def naive(state):
        attempts2["n"] += 1
        ledger2.add(state["lead_id"], "tue 10:00")
        if attempts2["n"] == 1:
            raise RuntimeError("process died after the write (simulated)")
        return {"booked_slot": "tue 10:00", "outcome": "booked"}

    run_booking_graph(naive, "L-102")

    # (3) Write, then crash, idempotency key on the lead.
    ledger3 = BookingLedger()
    attempts3 = {"n": 0}

    def guarded(state):
        attempts3["n"] += 1
        if ledger3.has(state["lead_id"]):
            return {"booked_slot": ledger3.slot_for(state["lead_id"]),
                    "outcome": "booked"}
        ledger3.add(state["lead_id"], "tue 10:00")
        if attempts3["n"] == 1:
            raise RuntimeError("process died after the write (simulated)")
        return {"booked_slot": "tue 10:00", "outcome": "booked"}

    run_booking_graph(guarded, "L-103")

    return {
        "flaky_attempts": attempts1["n"],
        "flaky_bookings": len(ledger1),
        "naive_attempts": attempts2["n"],
        "naive_duplicate_bookings": len(ledger2),
        "idempotent_attempts": attempts3["n"],
        "idempotent_bookings": len(ledger3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
