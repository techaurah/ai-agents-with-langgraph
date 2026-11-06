import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("rejection_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["bookings_by_decision"] == {"approve": 1, "reject": 0, "maybe": 0}
assert r["escalations_in_full_run"] == 1
assert r["escalated_lead"] == "L-002"
print("smoke ok")
