import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("capstone_spec.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["gates_count"] == 6
assert r["gates_fixed_on"] == "2026-11-06"
assert r["truth_records_verified"] == 12
assert r["approval_required"] == 3
assert r["crash_leads"] == 1
assert r["expected_bookings"] == 4
print("smoke ok")
