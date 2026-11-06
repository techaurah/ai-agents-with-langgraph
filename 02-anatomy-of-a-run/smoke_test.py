import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("anatomy.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["final_status"] == "done"
assert r["trace_nodes"] == ["intake", "score", "follow_up", "crm_log"]
assert r["checkpoints_written"] == 6
assert r["stream_values_events"] == 4
assert r["orphan_errors_caught"] == 1
assert r["final_outcome"] == "follow_up_scheduled"
print("smoke ok")
