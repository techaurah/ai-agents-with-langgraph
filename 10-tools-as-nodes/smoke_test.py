import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("tools_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["monolith_attempts"] == 2
assert r["monolith_visible_progress_at_failure"] == 0
assert r["tool_graph_progress_at_failure"] == 2
assert r["tool_graph_retry_executions"] == 2
assert r["flaky_tool_attempts"] == 2
assert r["agent_outcomes_correct"] == 12
print("smoke ok")
