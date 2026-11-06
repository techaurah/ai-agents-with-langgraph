# Solution 00

Load the schedule, build the set of `(day, time)` pairs whose status is "free", and test each booked lead's truth slot against it:

```python
free = {(s["day"], s["time"]) for s in load_schedule()["slots"]
        if s["status"] == "free"}
ok = sum(1 for lead in load_leads()
         if lead["truth"]["slot"]
         and tuple(lead["truth"]["slot"].split()) in free)
```

Measured result: 4 of 4 booked leads (L-001, L-003, L-004, L-009) name a slot that is free in the fixture schedule. This matters beyond tidiness: the booking node in later lessons trusts `choose_slot` to only return free slots, and the capstone's ledger gate (exactly 4 entries) assumes the four truth bookings are all achievable. An audit that catches a booked truth slot marked "booked" in the schedule would be catching a contradiction in the answer key itself.
