# Lesson 11: The Scoring Node

45 min · Intermediate · Prerequisites: Lesson 10

The agent's scoring node applies the course's rubric (fixtures/policy.json): budget brackets worth up to 40 points, recency up to 30, a decision-maker flag up to 30, with bands at 80 (HOT) and 55 (WARM). The rubric is boring on purpose: it is the same shape as the LeadPipe scoring from Course 3, published in a fixture where everyone can read it, so disagreements are about the rubric and not about hidden behaviour.

The lesson's real subject is the two leads the rubric cannot score yet. Scored as they arrived, ten leads match their truth scores exactly. L-004 (no budget declared) provisionally scores 60 against a completed 90; L-008 (no budget, no decision-maker flag) scores 25 against 53. The rubric pays 0 for unknown fields, which is a policy choice with a consequence: an unscored lead is indistinguishable from a weak lead until something asks for the missing data. Every routing mistake in Lessons 07 and 13 is born in this paragraph.

The set also runs close to its thresholds: the smallest distance from any completed score to a band boundary is 1 point (L-005 at 56, one above the WARM floor). Boundary sensitivity is a property of the rubric and the market it scores, and measuring it beats discovering it in a dispute about one lead.

## Run it

```
python3 scoring_lab.py
python3 smoke_test.py
```

## What the code measures

12 leads; 10 arrive with complete data; as-arrived scores match truth on 10; after recorded answers complete the records, 12 of 12. Provisional scores: L-004 at 60, L-008 at 25. Completed band split: 5 HOT, 4 WARM, 3 NURTURE. Minimum distance to a band threshold: 1 point.

## The same thing in real LangGraph

The scoring node is an ordinary node; the framework has no opinion about your rubric. What it gives you is the guarantee that this function's inputs and outputs are checkpointed state, so the score a route was based on can always be audited afterwards:

```python
builder.add_node("score", score_node)  # returns {"score": ..., "band": ...}
```

## Common failures

- Scoring missing data as zero without flagging it: the score is then a lie of omission, and every downstream route inherits it. Return the missing list with the score (the agent's scoring node does).
- A rubric that lives only in code: the fixture policy is the spec; if the code and the policy disagree, one of them is the bug.
- Ignoring boundary distance: a lead 1 point from a band will flip bands when any input is corrected. Lesson 17's fork is that story.

## Recap checklist

- Rubric: budget 40, recency 30, decision-maker 30; HOT at 80, WARM at 55.
- Unknown fields score 0 and must travel with a missing-fields flag.
- Provisional scores (60 and 25) are the root of the course's routing mistakes.

## Resources

- fixtures/policy.json and fixtures/leads.json: the rubric and the answer key, both audited again in Lesson 29.
