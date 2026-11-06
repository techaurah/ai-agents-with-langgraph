import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("band_router.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["distinct_paths"] == 7
assert r["threads_paused_for_approval"] == 3
assert r["outcomes"] == {"booked": 4, "follow_up_scheduled": 4,
                         "nurtured": 3, "approval_rejected": 1}
print("smoke ok")
