# Lesson 30: Build the Capstone Agent

90 min · Advanced · Prerequisites: Lesson 29

The build is an assembly, not an invention. The graph factory lives in `lgx/agent.py`, where it has been since the middle lessons needed it, and this lesson runs its hardened configuration end to end: intake, rubric scoring with the missing-fields report, the clarification cycle (at most two rounds), band routing, the approval interrupt standing before booking for the three policy-flagged HOT leads, the booking node that checks the ledger before it writes, and the CRM log that closes every path. Twelve leads, twelve threads, approval answers from the fixtures, and the one simulated crash absorbed by checkpoint retry.

The result, reported here and graded in the next lesson: all twelve leads match their truth records in full (score, band, and outcome), the ledger holds exactly 4 entries, the crash lead holds exactly 1 of them, and the mean cost is 4.92 checkpointed node executions per lead, re-executions included. The outcome split is the familiar one: 4 booked, 4 follow-ups, 3 nurtures, 1 rejection.

Read the factory code with the course behind you and notice how little of it is new: the scoring is Lesson 11, the routing Lesson 07, the cycle Lesson 13, the interrupt Lesson 18 placed by Lesson 19's rule, the booking guard Lesson 28, the durability Lesson 16. Capstones in this programme are like that on purpose: the final build should feel like recognition, with the difficulty moved to the grading.

## Run it

```
python3 capstone_agent.py
python3 smoke_test.py
```

## What the code measures

12 leads, 12 full matches (score, band, outcome all equal to truth); 4 ledger entries; 1 booking for the crash lead; mean 4.92 steps per lead. Every figure is a capstone gate's input in the next lesson; nothing here is graded yet, by design.

## The same thing in real LangGraph

The factory is the course-long mapping made concrete: a StateGraph with a typed schema and reducers, conditional edges, an interrupt node, a persistent checkpointer, and nodes written to be safe under re-execution. In the real framework the same assembly takes the same decisions; only the imports change.

## Common failures

- Building the capstone as a fresh rewrite instead of an assembly: new code at the end of a course hides which lesson's pattern was not learned.
- Counting the crash lead's steps as an anomaly to exclude: the mean includes re-executions and crash retries for every lead, because production means include them too.
- Declaring victory at "outcomes look right": Lesson 31 grades the ledger and the step counts as well, and the as-built variant's outcomes mostly look right too.

## Recap checklist

- The capstone is the course's patterns composed, not new machinery.
- Full matches 12 of 12; ledger 4; crash lead 1 booking; mean steps 4.92.
- Grading is a separate lesson with separate code, against gates fixed in Lesson 29.

## Resources

- lgx/agent.py: the factory, including the as-built variant Lesson 31 grades; capstone/gates.json in Lesson 29.
