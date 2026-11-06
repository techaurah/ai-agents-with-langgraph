# Solution 18

Verified: the book node never appears in the trace (the router reads the decision and ends the run); the final outcome is the empty string, since no node set it on the rejection path in this minimal graph; and the notification count is 2, identical to the approve case.

The count is decision-independent because the side effect sits before the interrupt call: it executes on the pausing run and again on the resumed run, whichever value the resume carries. A rejection does not refund the duplicate notification. Placement is the only control: work that must happen exactly once either moves after the resume value is known, or carries an idempotency key (Lesson 28).
