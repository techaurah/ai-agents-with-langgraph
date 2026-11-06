# Solution 01

Without the clarification loop, the pipeline matches fixture truth on 11 of 12 outcomes. The lead that changes is L-004: it arrives with no budget, provisionally scores 60 (WARM), and gets a follow-up instead of the booking its completed record (budget 900, score 90, HOT) earns. L-008 also scores provisionally (25 against a completed 53), but both values land in NURTURE, so its outcome survives.

The removed loop is a cycle: score, notice missing state, go back and get it, score again. In graph terms it is a conditional edge from the scoring node back through a clarify node, which is exactly the edge Lesson 13 adds. A pipeline can grow the same loop inline (the lab's full pipeline does), but then the "simple" version and the "correct" version are different code; the graph's flow changes by adding a node and an edge.
