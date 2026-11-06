import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("reliability_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["flaky_attempts"] == 2
assert r["flaky_bookings"] == 1
assert r["naive_attempts"] == 2
assert r["naive_duplicate_bookings"] == 2
assert r["idempotent_attempts"] == 2
assert r["idempotent_bookings"] == 1
print("smoke ok")
