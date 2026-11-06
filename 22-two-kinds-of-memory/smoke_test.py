import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("memory_kinds.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["messages_before_pause"] == 2
assert r["messages_after_resume"] == 3
assert r["fresh_thread_fields_known"] == 0
assert r["store_thread_fields_known"] == 2
print("smoke ok")
