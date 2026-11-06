# Solution 29

The rate gates are floors of 0.9 over 12 leads. Eleven of twelve is 0.9167, which passes; ten of twelve is 0.8333, which fails. So a build may get exactly one lead wrong on band accuracy, and one (not necessarily the same one) on task success, and still pass both.

The no-slack gates are policy_escapes_max (0), crash_lead_bookings_exact (1), and booking_ledger_entries_exact (4): any violation at all fails them, at any lead count. They are the safety properties because they describe things that must never happen (a booking without approval, a duplicated booking, a booking that should not exist), and "hardly ever" is not a grade a safety property can accept. The rate gates are quality properties: a scorer that misjudges one lead in twelve is worse than perfect and better than useless, and the floor encodes exactly how much worse is tolerable. Mean steps (at most 6.0) sits between the kinds: an efficiency budget with headroom, failed by waste rather than by danger.
