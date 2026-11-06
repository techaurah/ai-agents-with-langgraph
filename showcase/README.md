# Showcase: the capstone agent

The course's capstone (Lessons 29 to 31) assembles the LeadPipe qualification and booking agent as a graph and grades two variants against gates fixed before the build (`../29-capstone-spec/capstone/gates.json`).

| Metric (gate) | Gate | As-built | Hardened |
|---|---|---|---|
| Band accuracy (min) | 0.9 | 1.0 | 1.0 |
| Task success rate (min) | 0.9 | 0.8333 | 1.0 |
| Policy escapes (max) | 0 | 1 | 0 |
| Crash-lead bookings (exact) | 1 | 2 | 1 |
| Booking ledger entries (exact) | 4 | 6 | 4 |
| Mean steps per lead (max) | 6.0 | 5.17 | 4.92 |
| Gates passed | 6 | 2 | 6 |

The variants differ in exactly three decisions: where the approval interrupt stands (after booking versus before it), whether the booking node checks the ledger before writing, and how many clarification rounds a lead gets (one versus the policy's two). Reproduce with:

```
cd ../31-evaluate-and-harden && python3 evaluate_capstone.py
```
