import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("batch_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["attempted"] == 13
assert r["completed"] == 12
assert r["failed"] == 1
assert r["total_executions"] == 59
assert r["outcomes"] == {"booked": 4, "follow_up_scheduled": 4,
                         "nurtured": 3, "approval_rejected": 1}
print("smoke ok")
