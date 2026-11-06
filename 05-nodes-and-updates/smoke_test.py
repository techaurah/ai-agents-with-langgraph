import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("nodes_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["channels_total"] == 6
assert r["partial_keys_returned"] == 2
assert r["untouched_channels_kept"] == 3
assert r["command_paths_match_edge_paths"] is True
assert r["command_checkpoints"] == 4
assert r["edge_checkpoints"] == 4
print("smoke ok")
