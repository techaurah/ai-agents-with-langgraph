# Solution 24

Verified: Policy C stores 9 entries and answers 6 of 6 correctly. Per case it keeps one entry per field (the newest confirmed): 1 for BrightPath (budget), 1 for Harbour City (decision-maker), 2 for Ferns and Co (budget, channel), 2 for Northgate (channel, decision-maker), 1 for Solstice (channel only; its budget was never confirmed), 2 for Cedar Legal.

The trade against Policy B (11 entries, also 6 of 6): C destroys history at write time. B can still answer "what did we believe in March, and when did it change", which matters for auditing a bad conversation; C cannot, because the March value was never stored. C is the right default for high-volume simple facts; B is the right default anywhere an agent's past beliefs may need explaining. Correctness today is identical; the difference is what questions remain answerable tomorrow.
