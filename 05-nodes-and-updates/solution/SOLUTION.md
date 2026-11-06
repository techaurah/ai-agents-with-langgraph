# Solution 05

With `goto=END`, the triage node's update is applied and the run terminates: the trace holds exactly one entry (triage). The checkpoint count is 3: the initial snapshot, the snapshot after triage's super-step (whose next_node is END), and the terminal done record. Compare the lab's HOT run at 4 checkpoints: one additional node execution, one additional snapshot. Checkpoint arithmetic is always executions plus two on the stand-in, a useful sanity check when reading histories in Module 4.

The pattern matters beyond tidiness: a Command to END is how a node says "this run is legitimately over" from inside its own logic, for example a disqualified lead that should not be routed anywhere at all.
