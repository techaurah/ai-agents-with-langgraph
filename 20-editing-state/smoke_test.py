import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("edit_state.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["paused_before"] == "book"
assert r["ledger_entries_while_paused"] == 0
assert r["original_slot_would_have_been"] == "wed 11:00"
assert r["edited_booked_slot"] == "tue 15:00"
assert r["checkpoints_added_by_edit"] == 1
assert r["final_outcome"] == "booked"
print("smoke ok")
