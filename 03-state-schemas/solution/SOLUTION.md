# Solution 03

`validate_state` reports exactly 1 error: the fresh state's score is the string "0" where the schema declares int. Nothing has run yet; the schema disagrees with itself, and validation over the default state is the cheapest possible place to find that.

Lesson 00's audit would not catch an equivalent mistake in fixtures because it checks fixture records against the rubric, not schema definitions against their own defaults; the two audits guard different layers. What catches this class is validating the default state at compile or import time, which is why the stand-in's `invoke` validates a fresh thread's initial state before the first node executes (the same check this exercise runs by hand).
