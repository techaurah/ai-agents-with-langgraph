# Lesson 00: Course Setup and the Stand-in Lab

45 min · Beginner · Prerequisites: none

This course teaches the LangGraph way of building agents: state first, then nodes and edges, with checkpoints, interrupts, and memory as primitives rather than afterthoughts. It runs entirely offline on the Python standard library. That is possible because the runnable track uses `lgx`, a small graph engine in this repo that mirrors LangGraph's semantics. It is a teaching stand-in, labelled as one everywhere. It is not LangGraph, and nothing in this course claims it is. Each lesson pairs the stand-in code with the equivalent real LangGraph code (the 1.2.x line; framework facts and sources are in the root RESEARCH.md) so the transfer to the real framework is explicit.

Why a stand-in at all: a course whose numbers depend on a hosted model cannot be checked. Here, every number in every lesson is produced by the lesson's own code running on the bundled fixtures, and the smoke tests assert them exactly. When a framework behaviour is described rather than measured, the lesson says so and RESEARCH.md carries the citation.

The running example is a lead qualification and booking agent in the LeadPipe pattern: twelve fixture leads, a published scoring rubric, band routing, human approval for policy-flagged leads, and a booking ledger that stands in for an external booking system.

## Run it

```
python3 check_environment.py
python3 smoke_test.py
```

## What the code measures

`check_environment.py` verifies the lab before anything is learned in it: the interpreter is Python 3.10 or newer, the engine imports, the fixture set holds 12 leads, and every lead's truth record is exactly what the published rubric produces from its completed record (12 of 12 verified). It also counts the course layout: 32 numbered lesson folders. If any of these fail, later lessons' numbers cannot be trusted, which is why this check exists as a lesson and not a footnote.

## Common failures

- Running from the repo root instead of the lesson folder: the labs add the repo root to `sys.path` relative to their own file, so they work either way, but the smoke test pattern used across the TechAura courses assumes the lesson folder. Stay consistent.
- A Python older than 3.10: the engine uses current standard library typing. Check `python3 --version` first.
- Editing fixtures to make a check pass: the truth records are the course's answer key. Lesson 29 audits them again before the capstone is graded.

## Recap checklist

- The runnable track is the `lgx` stand-in on the standard library; no API keys, no network.
- Real LangGraph code appears as labelled reference snippets, never as executed code.
- The fixtures are 12 leads, a schedule, a policy, and a memory set, and their truth records are rubric-derived.

## Resources

- Root RESEARCH.md: the dated field scan, including LangGraph 1.2.20 on PyPI (checked 2026-11-06) and the official Academy curriculum this course parallels.
- Root DESIGN.md: the course design and its honesty rules.
