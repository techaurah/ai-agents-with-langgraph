# Solution 08

Verified totals: 20 model decisions, 16 tool executions, 4 tasks completed. Each task now costs 5 decisions (four tool choices plus the final) and 4 tool executions, so both totals rise by exactly the number of tasks (4). The loop's cost is linear in required observations per task, which is the budgeting rule of thumb: a loop's price is (observations per task + 1 decision) times the number of tasks, before any retries. If a real model's per-decision cost is known, this arithmetic is the estimate; the stand-in exists to make the counts exact so the arithmetic can be practised.
