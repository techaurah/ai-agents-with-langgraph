import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("time_travel.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["original_score"] == 78
assert r["original_outcome"] == "follow_up_scheduled"
assert r["forked_from_checkpoint"] == 1
assert r["fork_paused_for_approval"] is True
assert r["forked_score"] == 88
assert r["forked_outcome"] == "booked"
assert r["forked_slot"] == "mon 09:00"
assert r["original_unchanged"] is True
print("smoke ok")
