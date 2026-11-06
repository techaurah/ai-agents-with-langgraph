# Solution 06

Add a conditional edge after pong: `lambda s: "stop" if s["count"] >= 6 else "again"`, mapped to END and ping. Verified result: status done, 6 total executions (ping and pong three times each), no StepLimitExceeded.

This is the first of the lesson's three endings: proper termination at END, decided by state. The step limit is still compiled in (25 by default here) but now plays its proper role: a backstop that fires only if the exit condition is ever broken by a later edit, converting an infinite loop into a loud error with a checkpointed count.
