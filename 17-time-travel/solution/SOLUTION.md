# Solution 17

Verified: the forked run finishes with score 78 and outcome follow_up_scheduled, identical to the original, despite the lead's budget now reading 1500 in its state. Forking from checkpoint 2 (the after-score record) means the scoring node never re-executes in the fork: score and band are channels already written into the checkpoint, and the remaining nodes (follow_up, crm_log) do not recompute them.

The one-sentence explanation: a fork resumes the computation from the checkpoint's next_node onward, so any value computed before the fork point is inherited as fact, edited inputs notwithstanding. Choose fork points by which computations must be redone, not by which state you want to change.
