# Solution 13

Verified result: outcome needs_info, final score 45, clarify rounds used 2. The first round fills the budget (250), lifting the score to 45; the second round asks for the decision-maker flag, gets no answer (the clarify node finds nothing recorded and leaves the field empty), and the round budget is spent. The score node still reports the field missing, but the routing condition (missing AND rounds left) is now false, so the lead exits to unresolved instead of cycling again.

The agent stops asking because the budget, not the lead's silence, is the exit condition: silence is indistinguishable from a slow reply inside one run, so policy caps the rounds and routes the lead to a human-owned state. Guessing the flag (say, assuming false for 8 points) would have produced a confident, wrong score; needs_info produces an honest queue entry.
