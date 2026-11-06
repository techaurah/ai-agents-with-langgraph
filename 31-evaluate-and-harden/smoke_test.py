import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("evaluate_capstone.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
a = r["as_built"]
h = r["hardened"]
assert a["band_accuracy"] == 1.0
assert a["task_success_rate"] == 0.8333
assert a["policy_escapes"] == 1
assert a["crash_lead_bookings"] == 2
assert a["booking_ledger_entries"] == 6
assert a["mean_steps"] == 5.17
assert a["grade"]["passed"] == 2
assert a["grade"]["total"] == 6
assert h["band_accuracy"] == 1.0
assert h["task_success_rate"] == 1.0
assert h["policy_escapes"] == 0
assert h["crash_lead_bookings"] == 1
assert h["booking_ledger_entries"] == 4
assert h["mean_steps"] == 4.92
assert h["grade"]["passed"] == 6
print("smoke ok")
