import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("check_environment.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["python_ok"] is True
assert r["engine_imports"] is True
assert r["leads"] == 12
assert r["truth_verified"] == 12
assert r["lesson_folders"] == 32
assert r["all_ok"] is True
print("smoke ok")
