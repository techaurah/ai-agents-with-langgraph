import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("clarify_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["clarify_rounds_total"] == 3
assert r["max_rounds_on_one_lead"] == 2
assert r["with_cycle_score_matches"] == 12
assert r["without_cycle_score_matches"] == 10
assert r["without_cycle_outcome_matches"] == 11
print("smoke ok")
