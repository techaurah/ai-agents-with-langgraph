import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("react_loop.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["tasks"] == 4
assert r["tasks_completed"] == 4
assert r["model_calls"] == 16
assert r["tool_executions"] == 12
assert r["stuck_loops_caught"] == 1
print("smoke ok")
