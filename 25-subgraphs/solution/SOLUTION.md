# Solution 25

Verified: 3 leads are flagged (L-001 at 1500, L-002 at 1200, L-009 at 2000). The flag node reads the subgraph's returned state, so its band and its lead are the completed versions: L-004 ends HOT, but its completed budget is 900, below the 1000 threshold, so it is correctly not flagged. Had the parent read the as-arrived lead instead, L-004's budget would be missing entirely and the approval test would be guessing.

The parent took a handful of lines and no changes to the subgraph, which is the reuse argument made concrete: the component's contract (completed lead, score, band out) was sufficient for a question its author never asked. That is the standard to hold shared subgraphs to.
