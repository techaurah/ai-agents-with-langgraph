import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("reducers_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["overwrite_kept"] == 1
assert r["overwrite_final"] == ["msg-3"]
assert r["append_kept"] == 3
assert r["append_final"] == ["msg-1", "msg-2", "msg-3"]
assert r["add_reducer_total"] == 2
assert r["agent_events"] == ["intake", "score", "approve", "book", "crm_log"]
print("smoke ok")
