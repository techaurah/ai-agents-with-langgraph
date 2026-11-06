# Course Design: AI Agents with LangGraph

This document records the design as specified before the lessons were written, including the capstone gates policy. The measured outcomes live in the lessons and the root README's scorecard.

## Audience and promise

For builders who have written agents as loops and chains (or finished Agentic AI for Beginners) and keep hitting the same walls: state that evaporates between steps, flows that cannot pause for a human, runs that cannot resume after a crash. The promise: the LangGraph way of thinking (state first, nodes and edges, checkpoints as a primitive) taught as engineering with fixtures and measurements, not as API tourism. Every design claim in the course is either measured by the lesson's own code on the bundled fixtures, or cited to a dated source in RESEARCH.md.

## Principles

1. **The graph is the syllabus.** The module order follows the framework's own concepts in dependency order: state, nodes, edges, control flow, then the agent, then persistence, human-in-the-loop, memory, composition, production, and the capstone that uses all of it.
2. **A stand-in engine, labelled as such.** Real LangGraph needs hosted models to do anything interesting, which would make every number in the course depend on a network and a key. So the runnable track runs on `lgx`, a small local graph engine in this repo that mirrors LangGraph semantics (typed state channels with reducers, node functions returning partial updates, conditional edges, cycles with a step limit, checkpoints at super-step boundaries, interrupts that re-execute their node on resume, Send-style fan-out, a cross-thread store). It is a teaching stand-in, named as one in every lesson that introduces it. It is not LangGraph, and the course never claims it is.
3. **Every lesson maps to the real API.** Each lesson's README carries a short reference snippet in real LangGraph (the 1.2.x line, see RESEARCH.md) beside the stand-in code, so the transfer is explicit: the same state schema, the same edges, the framework's names for them. The snippets are reference material, clearly marked, and are not executed by CI; the stand-in code is what runs and what the numbers come from.
4. **One agent, every lesson.** The running example is a lead qualification and booking agent in the LeadPipe pattern (continuity with Courses 3 and 6): twelve fixture leads scored by a published rubric, routed by band, booked into a schedule, with human approval for the leads policy says need it. Early lessons build its pieces; the capstone assembles it whole.
5. **Failures are curriculum.** The fixture set deliberately contains the traps the framework's own documentation warns about: a node whose side effect sits before an interrupt and runs twice on resume, a booking that must not duplicate when a crashed run resumes, a rejected approval that must never become a booking, leads with missing data that need a clarification cycle, and a linear task where the graph honestly costs more than a plain pipeline.
6. **Gates before code.** The capstone's gates were fixed in `29-capstone-spec/capstone/gates.json`, dated 2026-11-06, from the measurements of the earlier modules (band rubric behaviour, step counts, the approval and crash drills), before any capstone code existed. The as-built verdict and the hardening are both reported against those unchanged numbers.

## Structure

32 lessons in 10 modules:

- Module 0, Foundations (00-02): setup and the stand-in lab, why graphs (measured against a plain pipeline), anatomy of a run (super-steps and snapshots).
- Module 1, State and nodes (03-05): state schemas and channels, reducers, nodes and partial updates (including Command-style routing updates).
- Module 2, Control flow (06-09): edges and termination, conditional edges and routers, cycles and the ReAct loop, fan-out with Send and the merge.
- Module 3, The LeadPipe agent (10-13): tools as nodes, the scoring node, routing by band, clarification cycles for missing data.
- Module 4, Persistence (14-17): checkpointing every super-step, threads and state history, crash and resume (durable execution), time travel and forks.
- Module 5, Human in the loop (18-21): interrupts and resume values, the approval gate, editing state at a breakpoint, rejection and escalation paths.
- Module 6, Memory (22-24): short-term versus long-term memory, the Store, memory write policies measured on returning leads.
- Module 7, Composition (25-26): subgraphs, streaming modes.
- Module 8, Production patterns (27-28): batch processing over many threads, failures, retries, and idempotency.
- Module 9, Capstone (29-31): spec and gates, build the LeadPipe agent end to end, evaluate and harden.

## Shared machinery

- `lgx/` is the shared stand-in engine: the graph builder and executor, checkpointers (in-memory and file-backed), the cross-thread store, and the deterministic model stand-in. Lessons import it so the semantics stay identical across the course.
- `lgx/agent.py` holds the LeadPipe domain: the scoring rubric, the booking tools with their ledger, and the graph factory the later lessons and the capstone assemble.
- `fixtures/` holds the twelve leads with their truth records, the booking schedule, the policy (rubric weights, band thresholds, the approval rule), and the memory set used by Module 6.

## The honesty rules

- The stand-in is never presented as LangGraph, and a framework behaviour is never claimed as measured unless the stand-in's code produced the number. Framework claims live in RESEARCH.md with sources and check dates.
- Honest negatives stay in print, including where the graph loses: the linear-task overhead in Lesson 01, the fan-out bookkeeping cost in Lesson 09, what indiscriminate memory writes do in Lesson 24, and whatever the capstone's as-built verdict turns out to be.
- No number appears in prose unless running the lesson's code on the fixtures produces it.
