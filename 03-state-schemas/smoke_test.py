import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("schemas.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["untyped_schema_errors"] == 0
assert r["untyped_downstream_failures"] == 1
assert r["typed_errors_caught_at_boundary"] == 1
assert r["schema_channels"] == 4
assert r["default_channels_filled"] == 4
print("smoke ok")
