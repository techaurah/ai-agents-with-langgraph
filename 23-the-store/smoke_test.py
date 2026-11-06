import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("store_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["profiles_stored"] == 5
assert r["prefix_search"] == 5
assert r["query_hits"] == 1
assert r["leads_after_notes"] == 5
assert r["after_update_count"] == 5
assert r["updated_channel"] == "whatsapp"
assert r["after_delete_count"] == 4
assert r["missing_key_returns"] is None
print("smoke ok")
