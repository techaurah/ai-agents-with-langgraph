# Research: the field scan this course is built on

Checked 2026-11-06. Every external claim below names its source and the date it was checked. Numbers reported by sources are labelled as reported; they are never mixed with this course's own measurements, which live in the lessons and come only from the bundled stand-in engine running on the bundled fixtures.

## The framework, as of the check date

- LangGraph describes itself as "a low-level orchestration framework for building, managing, and deploying long-running, stateful agents", providing "durable execution, streaming, human-in-the-loop, persistence, memory, and more" (PyPI project page for `langgraph`, checked 2026-11-06). The version current at the check date is **1.2.20**, uploaded to PyPI on 2026-11-05; the licence is MIT. This course's reference snippets target the 1.2.x line.
- The GitHub repository `langchain-ai/langgraph` carried 44,547 stars and 7,665 forks on the check date (GitHub repository page, checked 2026-11-06). Its README states the library is inspired by Google's Pregel and Apache Beam, and that the public interface draws inspiration from NetworkX.
- LangGraph reached 1.0 in October 2025, announced together with LangChain 1.0 on 2025-10-22. LangChain positioned 1.0 as a stability release: the core graph APIs and execution model were unchanged, `langgraph.prebuilt` was deprecated in favour of LangChain's `create_agent` (which itself runs on the LangGraph runtime), and the team committed to no breaking changes until 2.0 (1.0 announcement coverage: LangChain blog as reported by inductivee.com and peliqan.io, checked 2026-11-06). The hosted products were renamed in the same window: LangGraph Platform became LangSmith Deployment and LangGraph Studio became LangSmith Studio.
- LangChain's own positioning, repeated on the PyPI page: use LangGraph when you need deterministic and agentic workflows combined, heavy customisation, and controlled latency; use LangChain's prebuilt agents when you want speed over control, noting those agents run on LangGraph underneath (PyPI, checked 2026-11-06).

## The concepts the course teaches (framework documentation, checked 2026-11-06)

From the official Graph API overview at docs.langchain.com:

- A graph is three things: **State** (a shared snapshot, usually a typed schema; its keys are called channels), **Nodes** (functions that read state, do work, and return partial updates), and **Edges** (fixed or conditional transitions). `StateGraph` is the builder; you add nodes and edges, then `compile()`, which checks the structure (for example for orphaned nodes) and is where checkpointers and breakpoints attach.
- Execution follows Google's Pregel model: the graph advances in discrete **super-steps**. A node becomes active when it receives input on an incoming edge; nodes running in parallel share a super-step.
- Two control objects matter beyond plain edges: **`Send`**, which dynamically invokes nodes for fan-out (map-reduce), and **`Command`**, which updates state and routes in one object, and whose `resume` form supplies the value a paused `interrupt()` call returns.
- Persistence is checkpoint-based: with a checkpointer attached, state is saved at super-step boundaries, keyed by thread. The docs are explicit about the consequence this course builds two lessons around: after an interrupt or a retry, the affected node **re-executes from the start of its function**, so side effects placed before the pause point run again, and node logic must be designed to be safe under re-execution (idempotency keys, upserts, read-before-write).
- The ecosystem ships checkpointers at several durability levels (in-memory for development, SQLite for local files, Postgres for production concurrency, per the documentation and its persistence guides) and a separate **Store** abstraction for long-term memory that crosses threads, distinct from per-thread checkpoint state.
- Human-in-the-loop is a first-class feature, not a pattern bolted on: `interrupt()` pauses a node mid-function, and breakpoints (`interrupt_before` / `interrupt_after` at compile time) pause between nodes so a human can inspect or edit state. State history and state updates support "time travel": replaying or forking a run from an earlier checkpoint.

## What exists, and the gap

**The official course.** LangChain Academy's "Introduction to LangGraph" (Python) is free and structured: 55 lessons and about 6 hours of video across six modules (academy.langchain.com course page, checked 2026-11-06). Its arc: Module 1 foundations (simple graph, chains, routers, agents, agents with memory, a deployment intro); Module 2 state (schemas, reducers, message trimming); Module 3 user experience (streaming, interrupts and breakpoints, time travel); Module 4 building assistants (parallelisation, subgraphs, map-reduce, a research assistant); Module 5 long-term memory (the Store, structured extraction); Module 6 deployment (concepts, creating a deployment, connecting a client). The notebooks live in the `langchain-ai/langchain-academy` GitHub repository. It is the reference curriculum, and this course deliberately covers the same conceptual ground. Its constraint is execution: the notebooks call hosted models and hosted search, so following it needs API keys, a network, and usually the hosted Studio and deployment stack for the later modules.

**Third-party courses.** KodeKloud's LangGraph course runs eight modules from graph primitives through routing, state, short and long-term memory, human-in-the-loop, and a debugging and observability module (notes.kodekloud.com course outline, checked 2026-11-06); it sits behind a subscription. Great Learning offers a free "AI Agents in LangGraph" with three modules (fundamentals, setup and implementation, multi-agent patterns) (mygreatlearning.com, checked 2026-11-06): a useful orientation, too short to reach persistence failure modes or evaluation. "Learn LangGraph" (En Dash, a community resource, not official) is an interactive twelve-module course covering state and reducers, routing, ReAct cycles, checkpointers, interrupts, Send and Command, subgraphs, Store versus checkpointer, and multi-agent (dev.endash.us, checked 2026-11-06); it is account-based and browser-bound. Around these sit hundreds of GitHub tutorial repos and video walkthroughs, nearly all of which stop at a ReAct agent with a memory saver, and nearly all of which need a model key to run at all.

**The gap this course fills.** No offering found combines: a complete, free, text-first course; fully offline execution on the Python standard library, with no API keys and no hosted services; the engine itself shipped as small readable source inside the repo, with each framework concept mapped one-to-one to the real LangGraph API in reference snippets; measured comparisons on bundled fixtures (graph versus plain pipeline, fan-out bookkeeping cost, memory write policies) instead of asserted best practice; and a capstone graded against gates fixed before the build, including a policy escape count, an approval ordering check, and a crash-resume drill with a side-effect ledger. That combination is this course.

## How the stand-in maps to the framework

| This course (`lgx`) | LangGraph 1.2.x | Where the mapping is taught |
|---|---|---|
| `StateGraph`, `add_node`, `add_edge`, `compile()` | Same names in `langgraph.graph` | Lessons 02, 05, 06 |
| State schema dict with per-channel reducers | TypedDict schema with reducer functions (for example `add_messages`) | Lessons 03, 04 |
| `Command(update=..., goto=...)` | `langgraph.types.Command` | Lesson 05 |
| Conditional edges with a router function | `add_conditional_edges` | Lesson 07 |
| Step limit (`max_steps`) | `recursion_limit` config | Lessons 06, 08 |
| `Send(node, update)` fan-out | `langgraph.types.Send` | Lesson 09 |
| `MemoryCheckpointer`, `FileCheckpointer` | `InMemorySaver`, SqliteSaver and PostgresSaver family | Lessons 14 to 17 |
| `interrupt(payload)` and resume values | `langgraph.types.interrupt` and `Command(resume=...)` | Lessons 18 to 21 |
| `Store` with namespaces | `langgraph.store` (`InMemoryStore` and database stores) | Lessons 22 to 24 |
| Subgraph as a node | A compiled graph added as a node | Lesson 25 |
| `stream(mode="values" / "updates")` | `stream` / `astream` stream modes | Lesson 26 |

The stand-in simplifies where the framework is distributed (its fan-out runs sequentially inside one super-step; its checkpointers are a dict and a JSON file). Every simplification is named in the lesson that introduces it.
