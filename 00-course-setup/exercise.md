# Exercise 00: Extend the environment audit

`check_environment.py` verifies that fixture truth scores match the rubric. It does not verify the schedule. Add a check: every lead whose truth outcome is "booked" names a truth slot, and that slot exists in `fixtures/schedule.json` with status "free" (the booking tool's precondition). Report how many of the booked leads pass.

Work in a copy of the lab file or a scratch file; do not edit the fixtures. The answer is in `solution/SOLUTION.md`.
