# Lesson 07: Conditional Edges and Routers

45 min · Beginner · Prerequisites: Lesson 06

A conditional edge replaces "the next node is fixed" with "a router function reads the state and chooses". The router is deliberately small: it receives state, returns a decision, and the edge's mapping turns decisions into nodes. It does no work and writes nothing; that purity is what makes routing testable and what Lesson 12 exploits when it inventories an agent's paths.

The lab routes the twelve leads by band after scoring: 4 take the book path, 5 the follow-up path, 3 the nurture path, and the router's decision set exactly covers the mapping (3 decisions, HOT, WARM, NURTURE). One lead is misrouted against its truth band: L-004, routed as the WARM it provisionally is (score 60, no budget on record) rather than the HOT its completed record shows (90). The router did its job perfectly; the state it read was incomplete. Hold that distinction: routing bugs and state bugs look identical from the trace, and only one of them is the router's fault. Lesson 13 fixes the ordering (complete the state, then route); this lesson's job is to make the mechanism unremarkable.

## Run it

```
python3 router_lab.py
python3 smoke_test.py
```

## What the code measures

12 leads routed; path counts 4 book, 5 follow-up, 3 nurture; 3 distinct decisions covering the mapping; 1 provisional misroute (L-004). The misroute is counted against truth records, not against the router's own inputs: by its inputs, the router is 12 for 12.

## The same thing in real LangGraph

```python
def route(state) -> Literal["book", "follow", "nurture"]:
    return state["band"]

builder.add_conditional_edges("score", route,
                              {"HOT": "book", "WARM": "follow",
                               "NURTURE": "nurture"})
```

## Common failures

- A router that mutates state or calls tools: routing must be a pure read, or replays and resumes will route differently than the original run did.
- Decisions with no mapped target, and targets no decision can reach: both are silent until a rare state hits them. The stand-in's compile check catches unreachable targets; decision coverage is your tests' job.
- Routing on a provisional value without marking it provisional: if a later node completes the state, the route is already spent. Order beats cleverness (Lesson 13).

## Recap checklist

- Router: pure function of state returning a decision; mapping turns decisions into nodes.
- Coverage runs both ways: every decision mapped, every target reachable.
- A misroute can be a state problem wearing a routing costume. Check which before fixing either.

## Resources

- RESEARCH.md: conditional routing in the Graph API overview (checked 2026-11-06).
