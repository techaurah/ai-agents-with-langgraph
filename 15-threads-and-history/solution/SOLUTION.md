# Solution 15

Verified: after resuming L-001, thread A's latest status is done and thread B's latest status is still interrupted. Both threads sat paused simultaneously without interfering, because a pause is not a lock on the graph or the checkpointer; it is a status value in one thread's latest checkpoint.

The operational rule: pauses are per-thread and indefinite. A fleet of agent conversations can hold any number of threads waiting on humans at any moment, each resumable independently, which is the entire basis for human-in-the-loop at scale in Module 5. Nothing in the system needs to "keep a process alive" for a paused thread; the checkpoint is the waiting.
