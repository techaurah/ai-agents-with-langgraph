import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("graph_vs_chain.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["outcomes_equal"] == 12
assert r["pipeline_calls"] == 56
assert r["graph_executions"] == 59
assert r["graph_checkpoint_writes"] == 84
assert r["pipeline_checkpoint_writes"] == 0
print("smoke ok")
