# Solution 21

Verified: the ledger holds 0 bookings for L-002 (the safety property survived: the gate's router requires the exact decision "approve" to reach the booking node), crm_logged is true, but the final outcome label is the empty string, not approval_rejected (the labelling property did not survive: the logging node translates only the exact value "reject" into the rejected outcome).

The fix is one line of policy in the logging node: any decision that is not "approve", on a thread that passed through the gate, closes as approval_rejected (with the raw decision preserved in state for audit). It is deliberately left as an exercise-shaped wart in the course build: the capstone's gates grade the ledger and the outcome separately precisely because this lesson showed they can disagree.
