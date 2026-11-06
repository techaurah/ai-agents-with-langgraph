# lgx: the stand-in engine

`lgx` is the small local graph engine every runnable lesson in this course imports. It exists for one reason: the course's numbers must be reproducible offline, with no API keys and no hosted model, and a real agent framework driven by a hosted model cannot promise that.

It mirrors the semantics of LangGraph (the 1.2.x line; framework facts and sources in the root RESEARCH.md):

| lgx | LangGraph concept |
|---|---|
| `StateGraph`, `add_node`, `add_edge`, `add_conditional_edges`, `compile()` | The Graph API builder of the same names |
| State schema: channels with `default`, `reducer`, `type` | Typed state schema with per-key reducers |
| `Command(update, goto)` | `langgraph.types.Command` |
| `Send(node, update)` | `langgraph.types.Send` |
| `interrupt(payload)` and `invoke(resume=...)` | `langgraph.types.interrupt` and `Command(resume=...)` |
| `InMemoryCheckpointer`, `FileCheckpointer` | The checkpointer family (in-memory, SQLite, Postgres) |
| `Store` with namespaces | The long-term memory store |
| `max_steps` at compile time | The `recursion_limit` run config |

Named simplifications: fan-out branches execute sequentially inside their super-step instead of in parallel; streaming collects events and then yields them instead of flowing live; checkpointers are a dict and a JSON file instead of databases. Each is flagged again in the lesson that relies on it.

Files:

- `engine.py`: the builder, the executor, reducers, interrupts, streaming.
- `checkpoint.py`: the two checkpointers and the checkpoint record shape.
- `store.py`: the cross-thread memory store.
- `model.py`: the deterministic model stand-in (a labelled decision table, not a model).
- `agent.py`: the LeadPipe domain (rubric, booking tools, the agent graph in its hardened and as-built variants).
