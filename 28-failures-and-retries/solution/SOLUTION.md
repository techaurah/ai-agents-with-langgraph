# Solution 28

Verified: 3 attempts, 1 booking. The two failed attempts raised before the ledger write, so they left no trace in the external system; only the successful attempt wrote, once. Attempt counts measure the node's luck; booking counts measure its effects, and for failures that happen before the effect, the two are independent.

Contrast Lesson 16's write-then-crash shape, where each attempt can add an entry: there, attempts and effects are coupled, and the idempotency check is what decouples them. Knowing which side of the write your failures land on is the first diagnostic question for any flaky node.
