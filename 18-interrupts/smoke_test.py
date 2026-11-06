import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("interrupt_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["status_before_resume"] == "interrupted"
assert r["payload_action"] == "approve_booking"
assert r["payload_lead"] == "L-001"
assert r["approve_executions"] == 2
assert r["pre_interrupt_side_effects"] == 2
assert r["final_outcome"] == "booked"
print("smoke ok")
