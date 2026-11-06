import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("crash_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["crashed"] is True
assert r["file_thread_survives_new_instance"] is True
assert r["resumed_status"] == "done"
assert r["resumed_outcome"] == "booked"
assert r["booked_slot"] == "fri 14:00"
assert r["ledger_entries_for_crash_lead"] == 1
assert r["checkpoint_files"] == 1
assert r["history_entries"] == 9
assert r["in_memory_thread_survives_new_instance"] is False
print("smoke ok")
