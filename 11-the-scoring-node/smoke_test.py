import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("scoring_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["complete_data"] == 10
assert r["as_arrived_score_matches"] == 10
assert r["after_answers_score_matches"] == 12
assert r["provisional_scores"] == {"L-004": 60, "L-008": 25}
assert r["bands"] == {"HOT": 5, "WARM": 4, "NURTURE": 3}
assert r["min_boundary_distance"] == 1
print("smoke ok")
