# Changelog

## 1.0.0 (2026-11-06)

First release. 32 lessons in 10 modules teaching the graph model of agent design (state schemas, reducers, nodes, conditional routing, cycles, Send fan-out, checkpointing, threads, crash recovery, time travel, interrupts, approval gates, state editing, memory stores and write policies, subgraphs, streaming, batching, and retry/idempotency), all runnable offline on a local stand-in engine with the equivalent LangGraph 1.2.x code shown as reference snippets.

Capstone: the LeadPipe qualification and booking agent in two variants against gates fixed before the build. As-built passes 2 of 6 gates (policy escapes 1, crash-lead bookings 2, task success 0.8333); hardened passes 6 of 6 (task success 1.0, escapes 0, crash-lead bookings 1, ledger entries 4, mean steps 4.92).
