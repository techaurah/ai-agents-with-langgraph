import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("threads_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["threads"] == 2
assert r["paused_status"] == "interrupted"
assert r["other_thread_outcome"] == "follow_up_scheduled"
assert r["resumed_outcome"] == "booked"
assert r["state_bleed_fields"] == 0
assert r["history_lengths"] == {"thread-A": 8, "thread-B": 6}
print("smoke ok")
