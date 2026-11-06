# Solution 30

Verified: 3 threads contain an interrupted checkpoint (L-001, L-002, and L-009, the three approval-required leads; each paused exactly once at the approval interrupt), and 1 thread contains an error checkpoint (L-009 again, whose booking node crashed and whose resume wrote the error record before the retry).

The counts are the fixture design read back through the history: three leads meet the approval threshold in policy, and one lead carries crash_in_booking. An audit that found 4 interrupted threads would not be a curiosity; it would mean a fourth lead crossed a gate it should not have, and the history is where you would go to find out why. This is the operational habit the whole persistence module was building: the histories are the agent's memory of itself, and they reconcile with the fixtures exactly.
