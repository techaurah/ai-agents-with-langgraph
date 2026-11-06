import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("router_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["routed"] == 12
assert r["by_path"] == {"book_path": 4, "follow_path": 5, "nurture_path": 3}
assert r["decisions_covered"] == 3
assert r["provisional_misroutes"] == 1
print("smoke ok")
