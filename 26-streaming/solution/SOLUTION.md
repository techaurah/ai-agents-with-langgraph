# Solution 26

Verified: 8 updates events, naming intake, score, clarify, score, clarify, score, nurture, crm_log. The sequence is the clarification cycle drawn as a stream: score appears three times because the state was scored, repaired, scored, repaired, and scored again.

No second stream call is needed because nothing pauses: L-008 requires no approval, so a single invoke runs to completion and one stream covers it. L-001's stream ended at the interrupt marker, and its resume was a second invoke with its own stream. The rule for consumers follows directly: a stream ends when its invoke ends, and an interrupted invoke is one of the ways an invoke ends.
