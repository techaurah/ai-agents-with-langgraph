# Solution 10

Verified: at the failure the checkpoint shows 1 completed step (intake only), and the retry needs 3 executions (score, follow_up, crm_log) to finish, ending with the same correct outcome.

The rule the two data points establish: recovery re-executes the suffix of the flow from the failed node onward, and preserves the prefix before it. Lab version: failure at node 3 of 4 preserved 2 and re-ran 2. This version: failure at node 2 of 4 preserved 1 and re-ran 3. Prefix plus suffix always equals the whole flow, so the design lever is where you place node boundaries around expensive or fragile work: a boundary just before a flaky tool confines its retries to itself, which is exactly the placement Lesson 28 exploits.
