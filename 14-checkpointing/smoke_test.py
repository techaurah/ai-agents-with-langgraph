import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("checkpoint_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["checkpoints_written"] == 8
assert r["channels_per_checkpoint"] == 12
assert r["first_checkpoint_with_score"] == 2
assert r["paused_status"] == "interrupted"
assert r["paused_next_node"] == "approve"
assert r["first_status"] == "interrupted"
assert r["final_status"] == "done"
assert r["final_outcome"] == "booked"
print("smoke ok")
