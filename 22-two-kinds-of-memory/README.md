# Lesson 22: Two Kinds of Memory

45 min · Intermediate · Prerequisites: Lesson 21

Agent memory is two mechanisms wearing one name, and this lesson separates them with measurements. Short-term memory is the thread's state: within a conversation, everything the checkpoints hold is present at every step. The lab's three-node conversation pauses at a question with 2 messages already in its checkpoint, and after the resume it holds 3: continuity inside a thread is free, automatic, and total.

Long-term memory is what survives the thread. A new thread for a company the agent has spoken to before starts knowing 0 profile fields: checkpoints are per-thread by design, and nothing carries over. That is not a flaw to patch with bigger thread state; it is a boundary to design across. The bridge is a store: the earlier conversation writes confirmed facts under the company's namespace, and the new thread's intake reads them back, starting with 2 known fields (budget and decision-maker status) instead of none.

The design questions all live at the boundary: what earns a write (Lesson 24 shows the cost of writing everything), what shape it is stored in (Lesson 23), and what a reader should do when memory and the current conversation disagree (the current conversation wins; memory is a prior, not a fact). Modules 4 and 5 were about one conversation's lifetime; this module is about everything outside it.

## Run it

```
python3 memory_kinds.py
python3 smoke_test.py
```

## What the code measures

Messages in the paused thread's checkpoint: 2; after resume: 3. Profile fields known to a fresh thread with no store: 0; with a store lookup at intake: 2. The numbers are small because the distinction is binary: inside the thread, everything; across threads, only what was deliberately written and read.

## The same thing in real LangGraph

```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
store.put(("leads", "haddad-real-estate"), "profile",
          {"budget_usd_monthly": 900})
profile = store.get(("leads", "haddad-real-estate"), "profile")
```

Checkpoints give the thread memory; the Store gives cross-thread memory. The framework documentation draws the same line (RESEARCH.md).

## Common failures

- Expecting a new thread to "remember" a returning customer because the same checkpointer is attached: the checkpointer serves all threads and shares nothing between them.
- Writing thread state into the store verbatim, including provisional scores and half-finished drafts: the store outlives the context that made those values meaningful. Write facts, not transcripts (Lesson 24 prices this).
- Reading memory and treating it as current truth: budgets change. Memory opens the conversation; the conversation confirms.

## Recap checklist

- Short-term = thread state, complete and automatic within a conversation.
- Long-term = the store, deliberate and selective across conversations.
- A fresh thread knows 0 by default and exactly what the store gives it, no more.

## Resources

- RESEARCH.md: the Store as long-term memory distinct from per-thread checkpoints (checked 2026-11-06).
