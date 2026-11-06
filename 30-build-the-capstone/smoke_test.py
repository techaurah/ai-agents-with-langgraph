import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("capstone_agent.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["full_matches"] == 12
assert r["ledger_entries"] == 4
assert r["crash_lead_bookings"] == 1
assert r["mean_steps"] == 4.92
assert r["outcomes"] == {"booked": 4, "follow_up_scheduled": 4,
                         "nurtured": 3, "approval_rejected": 1}
print("smoke ok")
