import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "artifact", pathlib.Path(__file__).with_name("fanout_lab.py"))
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)
r = artifact.evaluate()
assert r["leads"] == 12
assert r["seq_executions"] == 48
assert r["fan_executions"] == 48
assert r["seq_super_steps"] == 48
assert r["fan_super_steps"] == 36
assert r["seq_time_units"] == 84
assert r["fan_time_units"] == 60
assert r["branch_state_copies"] == 24
assert r["slot_results_equal"] == 12
assert r["conflict_values_written"] == 2
assert r["conflict_values_kept"] == 1
print("smoke ok")
