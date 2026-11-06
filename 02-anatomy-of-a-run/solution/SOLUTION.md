# Solution 02

After the first invoke, the thread holds 4 checkpoints: the initial snapshot, the snapshots after intake and after score, and the interrupt record. The latest has `status` "interrupted" and `next_node` "approve": the run paused inside the approve node, so resume means re-executing that node with the recorded state, which the checkpoint also carries in full.

That is the entire resume contract. No separate session object, no "where was I" bookkeeping in application code: the latest checkpoint is state, position, and status in one record. Lesson 14 counts the full eight checkpoints of this lead's completed run (four more arrive with the resume: approve re-executed, book, crm_log, done).
