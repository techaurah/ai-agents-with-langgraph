# Solution 19

Verified: the approve node executes 0 times for L-003, and the lead books normally (outcome booked, slot wed 11:00). Zero is correct because the policy's approval rule is threshold-based: `approval_budget_threshold` is 1000 in fixtures/policy.json, and L-003's budget of 800 does not meet it, so the routing function never sends the lead to the gate.

The audit trail is not gapped: the trace and checkpoints show the score node computing the band and the router choosing book directly, with the lead's budget in state for any reviewer to check against the threshold. A gate that interrupts every lead regardless of policy would not be safer, just slower, and would train approvers to rubber-stamp, which is how real gates fail.
