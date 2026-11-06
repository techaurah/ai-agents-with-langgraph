# Resources: decision cards

Short synthesis from the course's own measurements. Each card names the lessons that produced its numbers.

## Graph or pipeline?

If the flow is linear, has no human in it, and losing an in-flight run is acceptable, a plain pipeline is cheaper and this course measured by how much: 56 calls against the graph's 59 executions, and zero checkpoint writes against 84 (Lesson 01). The moment any of these become true, the pipeline stops being able to express the requirement at any price: the flow must pause for a person (Lessons 18 to 21), resume after a crash (Lesson 16), branch on completed-versus-partial state (Lesson 13), or be audited after the fact (Lesson 14). Choose by requirements, not by fashion.

## Where do I put the human?

Before the irreversible act, never after it (Lesson 19: same interrupt, 0 escapes before the booking node, 1 after it). Inside a node when the human answers a question the node is asking (interrupt); between nodes when the human may change the facts (breakpoint plus update_state, Lesson 20). Route on the exact affirmative (Lesson 21): anything that is not "approve" is not approval.

## What do I write to memory?

Confirmed facts, keyed by identity, dated, with the newest winning the read (Lesson 24: 6 of 6 returning-lead recalls, against 3 of 6 for save-everything). Treat "no confirmed value" as a first-class answer. Supersede rather than delete when past beliefs may need auditing; dedupe at write when volume matters more (Lesson 24 exercise: same 6 of 6 with 9 entries instead of 11).

## How do I make retries safe?

Assume at-least-once execution of every node that can pause or fail. Give each side effect an idempotency key naming the logical operation (one booking per lead) and read before writing (Lesson 28: the guarded variant takes the same crash and produces 1 booking instead of 2). Grade the external system of record, not the graph's labels (Lessons 21 and 31).

## Further reading (checked 2026-11-06, see root RESEARCH.md)

- The official LangGraph documentation, Graph API overview, at docs.langchain.com: the concepts this course maps to.
- LangChain Academy, "Introduction to LangGraph" (Python): the official free course; notebook-based and model-powered where this course is text-first and offline.
- The `langchain-ai/langgraph` repository on GitHub: source, releases, and examples for the real framework.
