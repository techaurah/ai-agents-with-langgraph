# Exercise 16: The same crash, the unguarded build

Repeat the drill with the as-built variant (approval after booking, no idempotency check). Note: in that variant the booking node runs before the approval interrupt, so the crash strikes inside the first invoke, not the resume. Recover the thread the same way (retry, then answer the interrupt). Report the crash point, the crash lead's final ledger entries, and its outcome.

The answer is in `solution/SOLUTION.md`.
