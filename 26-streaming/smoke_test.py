import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("streaming_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["values_events_before_pause"] == 2
assert r["interrupt_markers"] == 1
assert r["values_events_after_resume"] == 3
assert r["updates_events"] == 4
assert r["updates_single_key_each"] is True
assert r["final_streamed_outcome"] == "booked"
print("smoke ok")
