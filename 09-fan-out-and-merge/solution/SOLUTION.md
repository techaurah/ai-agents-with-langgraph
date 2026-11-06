# Solution 09

Verified by the extended counts: executions 60 against 60 (five per lead either way; fan-out never changes the amount of work, only its grouping); super-steps 36 against 60 (the fan-out still takes three per lead: enrich, one shared branch super-step, merge); modelled time 72 against 132 (fan-out per lead is 1 + max(3, 2, 4) + 1 = 6; sequential is 1 + 3 + 2 + 4 + 1 = 11); branch state copies rise to 36 (three Sends per lead).

The number fan-out changed least is the one beginners expect it to change most: total executions. Its wins are latency shape and super-step count; its costs are copies and merge design. A third branch widened both sides of that trade exactly as the model predicts, which is the sign of a cost model worth keeping.
