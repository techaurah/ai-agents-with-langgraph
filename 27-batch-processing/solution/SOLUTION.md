# Solution 27

Verified: both malformed submissions are rejected (the unknown channel and the type violation each raise the structure error at invoke), so the counts become 14 attempted, 12 completed, 2 failed. Total executions are unchanged at 59.

The executions answer is the boundary rule from Lesson 14 again: a rejected invoke never completes a super-step, so it contributes no executions and no checkpoints beyond, at most, a failed thread's absence. Validation failures are free in execution terms, which is precisely why validating at the door beats validating mid-flow: mid-flow failures arrive after side effects have started pricing themselves in.
