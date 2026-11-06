# Solution 16

Verified: the crash raises out of the first invoke, immediately after the booking write, before approval is ever requested. After the retry, the booking node re-executes without checking the ledger and writes a second entry; the approval interrupt then fires and is approved, and the thread finishes with outcome booked and 2 ledger entries for L-009.

Every element of the failure is an ordering or guarding decision, not bad luck: the write precedes the approval that should have gated it, and the retry cannot tell a fresh write from a repeated one. Compare the hardened drill in the lesson (1 entry, approval first) and hold both results for Lesson 31, where this exact difference is worth two capstone gates.
