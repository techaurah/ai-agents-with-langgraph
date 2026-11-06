import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("approval_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["hardened_rejected_bookings"] == 0
assert r["asbuilt_rejected_bookings"] == 1
assert r["hardened_approval_before_booking"] is True
assert r["asbuilt_approval_before_booking"] is False
assert r["hardened_rejected_outcome"] == "approval_rejected"
print("smoke ok")
