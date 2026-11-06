import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("subgraph_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["subgraph_invocations"] == 24
assert r["agent_band_matches"] == 12
assert r["report_band_counts"] == {"HOT": 5, "WARM": 4, "NURTURE": 3}
print("smoke ok")
