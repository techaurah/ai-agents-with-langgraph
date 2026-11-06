# Solution 20

Verified: without the edit, the run books wed 11:00 (the fixture's original preference) and finishes with 6 checkpoints: initial, after score, the breakpoint record, then book, log, and the terminal done record added by the resume. The lab's edited run has 7 at the equivalent point of comparison because update_state appended one record of its own between the breakpoint and the resume.

The reconciliation is the general rule: every state-changing operation on a thread (a super-step, a pause, an edit, the finish) is one checkpoint. When a history's length surprises you, enumerate those events and the count will explain itself.
