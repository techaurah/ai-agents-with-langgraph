import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("write_policies.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["cases"] == 6
assert r["policy_a_correct"] == 3
assert r["policy_b_correct"] == 6
assert r["policy_a_entries"] == 12
assert r["policy_b_entries"] == 11
assert r["policy_a_wrong_cases"] == [
    "BrightPath Dental", "Harbour City Plumbing", "Solstice Med Spa"]
print("smoke ok")
