# Lesson 15: Threads and State History

45 min · Intermediate · Prerequisites: Lesson 14

A thread is one conversation's identity: every invoke names its thread, every checkpoint is filed under it, and threads do not share state. This lesson interleaves two leads against one checkpointer. L-001 is driven to its approval pause; while it sits paused, L-005 runs to completion on its own thread; then L-001 resumes and books.

The isolation check is the point: L-005's final state has an empty approval_decision and no booked slot (it never went near those nodes), L-001's outcome is booked rather than follow_up_scheduled, and the checkpointer holds exactly two threads with histories of 8 and 6 records. Concurrency in this model is not locking; it is naming. One compiled graph serves any number of threads because everything mutable lives in per-thread checkpoints.

This is also the moment to fix the vocabulary the rest of the course uses: a thread is a conversation (one lead's qualification), a checkpoint is a moment in it, and the history is the whole conversation's audit trail. Long-term memory across threads is a different mechanism entirely (Module 6), and confusing the two is the most common design error in agent systems.

## Run it

```
python3 threads_lab.py
python3 smoke_test.py
```

## What the code measures

2 threads on one checkpointer; the paused thread's status is interrupted while the other completes; bleed between threads is 0 fields on every check the lab runs; histories are 8 records (L-001, with its pause) and 6 (L-005, straight through).

## The same thing in real LangGraph

Threads are addressed through the run config: `{"configurable": {"thread_id": "..."}}`. The framework's hosted runtime builds assistants, threads, and runs into an API; the stand-in keeps the same identity model in a dict and a JSON file.

## Common failures

- Reusing a thread id for a new conversation: the new invoke continues the old conversation's state and, if it finished, returns the old result. Thread ids are identities, not labels.
- Storing cross-conversation facts in thread state "temporarily": they die with the thread's relevance. That is what the store (Lesson 23) is for.
- Debugging two interleaved threads from one combined log: read histories per thread; interleaving is a display artifact, not a state interaction.

## Recap checklist

- Threads isolate state completely; one graph, many threads, zero bleed (measured).
- Interleaving is safe because all mutable state is per-thread checkpoint data.
- Thread state is conversation memory; cross-thread memory is Module 6's separate mechanism.

## Resources

- Lesson 14 for the checkpoint record; Lesson 22 for the short-term versus long-term distinction this lesson sets up.
