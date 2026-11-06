# Lesson 24: Memory Write Policies, Measured

60 min · Advanced · Prerequisites: Lesson 23

Reading memory is easy to demo and easy to get right. Writing it is where systems quietly rot. This lesson takes six returning-lead cases (fixtures/memory.json): each carries the facts an earlier conversation produced, marked confirmed or tentative, dated, and in two cases stale, meaning true once and false now. Two write policies face the same recall question per case (what is this company's current value for one field).

Policy A saves everything and recalls the oldest stored value. It answers 3 of 6 correctly, and the misses are the important part: a budget of 400 recalled for a lead now at 1500, a decision-maker flag the company outgrew, and a tentative 900 (never confirmed) treated as settled fact. Each is a stale or unconfirmed value presented as current truth, the precise failure that makes sales teams distrust agent memory. Policy B saves only confirmed facts and recalls the newest: 6 of 6, including the case where the correct answer is "no confirmed budget on record" (the truth records null), which A answers wrongly with the tentative number.

The volumes are nearly identical (12 stored facts against 11), so the difference is not discipline by deletion; it is policy: what earns a write (confirmed), and what wins a read (newest). The exercise adds a third policy that also dedupes at write time and reaches the same 6 of 6 with 9 entries: same correctness, cheaper store. There is no policy in the lesson that makes stale facts safe to keep unlabelled.

## Run it

```
python3 write_policies.py
python3 smoke_test.py
```

## What the code measures

6 cases. Policy A: 3 correct, 12 entries, wrong on BrightPath Dental, Harbour City Plumbing, and Solstice Med Spa. Policy B: 6 correct, 11 entries. Every figure comes from running both policies against the same store implementation and the same fixture cases; the fixture's stale flags are documentation for the reader, not inputs to the policies (neither policy is told which facts are stale; B survives them by construction, which is the point).

## The same thing in real LangGraph

The framework gives you the store; the write policy is application code, typically a node (or a background task) that decides what a finished conversation contributes. Managed memory services exist in the ecosystem, but the policy questions (confirmed by whom, superseded how, retained how long) remain yours. See RESEARCH.md for the store's documented role.

## Common failures

- Saving model inferences as facts: an inferred budget is a hypothesis. If it must be stored, store it labelled unconfirmed, which is to say, in Policy B's world, not at all.
- Recalling the first or the arbitrary match: without a recency rule, recall order is storage order, and storage order is archaeology.
- Deleting stale facts on sight: the correct move is supersession (a newer confirmed value wins the read), because deletion destroys the audit of why the agent believed what it believed.

## Recap checklist

- Write policy beats read cleverness: confirmed-only writes plus newest-wins reads scored 6 of 6.
- Save-everything scored 3 of 6, failing exactly on stale and unconfirmed facts.
- "No confirmed value on record" is a correct recall result, and policies must be able to say it.

## Resources

- fixtures/memory.json: the six cases, including the stale flags neither policy is allowed to peek at.
