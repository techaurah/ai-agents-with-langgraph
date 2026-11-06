# Fixtures

The data every lesson measures against. Synthetic throughout: fictional people and companies, no real personal data.

- `leads.json`: twelve leads for the LeadPipe agent. Each record carries the as-arrived fields (channel, budget, days since inquiry, decision-maker flag, preferred slot), the answers a clarification conversation would produce (`followup_answers`), the human's approval decision where policy requires one (`approval`), one sabotage flag (`crash_in_booking` on L-009), and a truth record (score, band, outcome, slot) that Lesson 29's audit proves is exactly what the rubric produces from the completed record.
- `schedule.json`: the discovery-call slots the booking tool chooses from, with free and booked entries.
- `policy.json`: the scoring rubric (budget and recency brackets, decision-maker points), the band thresholds (HOT at 80, WARM at 55), the approval budget threshold (1000), the clarification round budget (2), and the follow-up delay.
- `memory.json`: the six returning-lead cases for Module 6, each listing facts an earlier conversation produced (with confirmed flags and dates, and stale markers for the reader) plus the true current value a recall must return.

Changing a fixture changes the course's answer key: expect smoke tests across many lessons to fail, correctly. Fixture changes belong in their own commit with the affected lessons updated in the same change.
