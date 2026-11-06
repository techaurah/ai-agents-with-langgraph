import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("edges_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["normal_status"] == "done"
assert r["normal_executions"] == 1
assert r["step_limit"] == 10
assert r["cycle_stopped_at"] == 11
assert r["compile_errors_caught"] == 1
print("smoke ok")
