# Lesson 25: Subgraphs

60 min · Advanced · Prerequisites: Lesson 24

A compiled graph can be a node in another graph. This lesson compiles the qualification flow (intake-less scoring plus the clarification cycle, on its own five-channel schema) once, then uses the same compiled object as a node in two parents: an agent-shaped parent that routes by band to actions, and a reporting parent that only counts. Both run the twelve leads: the subgraph is invoked 24 times, the agent parent's bands match truth 12 of 12, and the report counts the familiar 5 HOT, 4 WARM, 3 NURTURE.

The boundaries are the lesson. The subgraph sees only the channels its schema declares (parents pass a filtered view), returns only the channels the schemas share, and runs on its own internal threads with its own checkpoints: a parent cannot reach into a subgraph's mid-flight state, and the subgraph cannot see the parent's outcome channel at all. That opacity is the point of the pattern: qualification becomes a component with a state contract, testable alone (Lessons 11 to 13 effectively tested it), reusable in shapes its author did not anticipate. The exercise adds a third parent the author did not plan, in a dozen lines.

One stand-in rule, named: subgraphs run to completion inside their parent node. A subgraph that pauses (an interrupt inside it) is a real framework pattern with real complexity in how the pause surfaces; the stand-in raises instead, and the course's approval flows all live in parent graphs for that reason.

## Run it

```
python3 subgraph_lab.py
python3 smoke_test.py
```

## What the code measures

24 subgraph invocations across two parents over the same 12 leads; agent parent band matches 12 of 12; report band counts 5, 4, 3. Reuse is measured, not asserted: one compiled object, two parents, zero changes to the subgraph between them.

## The same thing in real LangGraph

```python
qualification = qualification_builder.compile()
parent.add_node("qualify", qualification)   # a compiled graph is a node
```

The framework supports exactly this composition, including per-subgraph checkpointing options; see RESEARCH.md.

## Common failures

- Sharing one mutable schema object between parent and subgraph and editing it for one of them (the lab copies the schema dict deliberately): contracts must be able to diverge safely.
- Expecting the parent to see subgraph internals mid-run: it sees inputs and final shared channels. Design the shared channels as the component's API.
- Rebuilding a flow inline in each parent "because it is short": the third use is the one that diverges. The exercise manufactures that third use.

## Recap checklist

- A compiled graph is a node; its schema is its contract; its internals are its own.
- One qualification subgraph served an agent parent and a report parent unchanged, 24 invocations.
- The stand-in runs subgraphs to completion; pausing subgraphs are out of its scope, by declaration.

## Resources

- RESEARCH.md: subgraphs in the Graph API and in the Academy curriculum's Module 4 (checked 2026-11-06).
