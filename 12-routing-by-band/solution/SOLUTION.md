# Solution 12

Two of the seven paths pass through clarify: clarify-then-book (L-004) and clarify-twice-then-nurture (L-008), walked by 2 leads in total. The most-walked path is plain follow-up, shared by the four WARM leads with complete data (L-005, L-006, L-010, L-012).

The path that exists because of a sabotage fixture is approval-then-book as walked by L-009: identical in shape to L-001's path, but L-009's record sets `crash_in_booking`, so its booking node will crash mid-write when Lesson 16 runs it under a file checkpointer. The inventory cannot see the difference (same nodes, same order), which is precisely why path coverage is necessary but not sufficient: the crash lives in a side effect, and only the ledger and the checkpoint history will tell that story.
