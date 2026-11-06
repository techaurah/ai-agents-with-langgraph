# Solution 14

The first checkpoint with crm_logged true is id 6 of 8 (ids 0 to 7). Checkpoint 6 is written when the crm_log super-step completes: its state includes the log's update, and its next_node is END. The final checkpoint, id 7, is the terminal record written when the run observes that next node: same state, status flipped to done and next_node null.

The pair teaches the boundary rule from the other side: a node's effects are visible in the checkpoint written after its super-step, and termination itself is also a recorded event rather than an absence of records. Audits that count "the last state where X was false" should expect this one-record lag everywhere.
