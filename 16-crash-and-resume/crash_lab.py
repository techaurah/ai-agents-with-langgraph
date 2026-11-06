"""Lesson 16 lab: durable execution, drilled with a real crash.

L-009's fixture record asks the booking node to crash after writing to
the booking ledger and before returning, the worst moment to die. The
run uses a file-backed checkpointer in a temp directory. After the
crash, a brand new agent instance with a brand new checkpointer object
pointed at the same directory resumes the thread: the state survived
because it was never only in memory. The booking node re-executes; the
hardened build checks the ledger first and reuses the existing booking,
so the lead ends with exactly one booking. The control experiment runs
the same trick with an in-memory checkpointer: a new instance sees no
thread at all. That difference is the whole lesson.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import (BookingLedger, SimulatedCrashError,
                       build_lead_agent, load_leads)
from lgx.checkpoint import FileCheckpointer, InMemoryCheckpointer


def evaluate():
    lead = [l for l in load_leads() if l["id"] == "L-009"][0]
    directory = tempfile.mkdtemp(prefix="lgx-crash-")
    ledger = BookingLedger()
    attempts = {}

    bundle1 = build_lead_agent("hardened",
                               checkpointer=FileCheckpointer(directory),
                               ledger=ledger, attempts=attempts)
    graph1 = bundle1["graph"]
    graph1.invoke({"lead": lead}, thread_id="crash-lead")
    crashed = False
    try:
        graph1.invoke(None, thread_id="crash-lead", resume="approve")
    except SimulatedCrashError:
        crashed = True

    bundle2 = build_lead_agent("hardened",
                               checkpointer=FileCheckpointer(directory),
                               ledger=ledger, attempts=attempts)
    graph2 = bundle2["graph"]
    survived = graph2.get_state("crash-lead") is not None
    final = graph2.invoke(None, thread_id="crash-lead", retry=True)
    history = FileCheckpointer(directory).history("crash-lead")
    files = len(list(Path(directory).glob("*.json")))

    memory = InMemoryCheckpointer()
    bundle3 = build_lead_agent("hardened", checkpointer=memory)
    warm = [l for l in load_leads() if l["id"] == "L-005"][0]
    bundle3["graph"].invoke({"lead": warm}, thread_id="memory-lead")
    memory_survives = InMemoryCheckpointer().latest("memory-lead") is not None

    return {
        "crashed": crashed,
        "file_thread_survives_new_instance": survived,
        "resumed_status": final["status"],
        "resumed_outcome": final["state"]["outcome"],
        "booked_slot": final["state"]["booked_slot"],
        "ledger_entries_for_crash_lead": ledger.count_for("L-009"),
        "checkpoint_files": files,
        "history_entries": len(history),
        "in_memory_thread_survives_new_instance": memory_survives,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
