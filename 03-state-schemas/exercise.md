# Exercise 03: A bad default

Add a channel whose default contradicts its declared type: `{"score": {"default": "0", "type": int}}` in a two-channel schema. Run `validate_state` over a fresh default state and count the errors. Then say why Lesson 00's audit would not catch this class of mistake in the fixtures, and what would.

The answer is in `solution/SOLUTION.md`.
