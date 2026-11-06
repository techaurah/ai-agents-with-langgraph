# Lesson 16: Crash and Resume (Durable Execution)

75 min · Advanced · Prerequisites: Lesson 15

L-009's fixture record asks the booking node to do the worst thing at the worst moment: write the booking to the external ledger, then crash before returning. This lesson runs it for real, with a file-backed checkpointer in a temp directory. The approval resume raises the simulated crash out of the invoke. Then a new agent instance, with a new checkpointer object pointed at the same directory, resumes the thread: the state survived because it was never only in memory. The booking node re-executes from the last checkpoint boundary, checks the ledger first (the hardened build's idempotency), finds its own earlier write, and reuses it. The lead ends booked, once: exactly one ledger entry.

The control experiment is the lesson's other half: the same trick with an in-memory checkpointer fails completely. A new checkpointer instance sees no thread at all, because in-memory checkpoints live and die with the object. Neither behaviour is a bug; they are the two durability levels, and choosing between them per environment is an engineering decision this course expects you to make deliberately. The framework's saver family spans the same range (in-memory for development, SQLite files, Postgres for production; RESEARCH.md).

Note what the crash did not roll back: the ledger write. External side effects are outside the checkpoint's jurisdiction, which is why the redo-safe node (check before write) is the pattern, and why Lesson 28 grades it.

## Run it

```
python3 crash_lab.py
python3 smoke_test.py
```

## What the code measures

The crash is raised (crashed: true); the file thread survives a brand new checkpointer instance (true) while the in-memory thread does not (false); the resumed run finishes done with outcome booked at "fri 14:00"; ledger entries for the crash lead: exactly 1; checkpoint files on disk: 1 (one per thread); history entries for the thread: 9, including the error record written when the crash was caught.

## The same thing in real LangGraph

Durable execution is the framework's headline property: with a persistent checkpointer (SQLite or Postgres savers), a crashed run resumes from its last checkpoint on a new process, and nodes must be written to tolerate re-execution, per the official persistence documentation (RESEARCH.md).

## Common failures

- Testing crash recovery with an in-memory checkpointer and a shared instance: that tests nothing about durability. New instance, same storage, or it did not happen.
- Assuming resume rolls back external writes: it cannot. The ledger kept the booking; only the node's own check made that safe.
- Checkpointing to storage slower than the work: file-per-thread JSON is a teaching tool. The decision to make in real systems is which saver, not whether to save.

## Recap checklist

- Completed super-steps are durable; the in-flight node re-executes on resume.
- File-backed state survives a new process; in-memory state survives nothing.
- Side effects outside the graph are never rolled back; nodes must check before they write.

## Resources

- RESEARCH.md: durable execution and the checkpointer family (checked 2026-11-06); Lesson 28 for the idempotency pattern in isolation.
