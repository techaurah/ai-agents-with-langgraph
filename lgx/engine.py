"""The lgx graph engine: a teaching stand-in for LangGraph's runtime.

This module is NOT LangGraph. It is a small local engine, written for this
course, that mirrors the semantics the official Graph API documentation
describes (checked 2026-11-06, see RESEARCH.md):

- a graph is State (channels with reducers) plus Nodes plus Edges;
- execution advances in discrete super-steps, checkpointed at their
  boundaries when a checkpointer is attached;
- `Command` updates state and routes in one object, and supplies the resume
  value after an interrupt;
- `Send` fans work out dynamically and the results merge back by reducer;
- `interrupt()` pauses a node mid-function, and on resume the node
  re-executes from the start of its function, exactly the behaviour the
  framework documentation warns about, so side effects before the pause
  point run again unless the node is written to be safe under re-execution.

Named simplifications: fan-out branches run sequentially inside their
super-step (the framework runs them in parallel); there is one active node
at a time outside fan-out; streaming materialises its event list instead of
flowing live. Each simplification is named again in the lesson that uses it.
"""

from __future__ import annotations

import contextvars
import copy

from .checkpoint import InMemoryCheckpointer

START = "__start__"
END = "__end__"

_UNSET = object()


class StepLimitExceeded(Exception):
    """Raised when a run passes the compiled step limit.

    Stand-in for the framework's recursion limit error: cycles are legal in
    a graph, so every compiled graph carries a budget of node executions.
    """


class GraphStructureError(Exception):
    """Raised for unknown channels, bad updates, and orphaned nodes."""


class InterruptSignal(Exception):
    """Internal control flow for interrupt(); carries the pause payload."""

    def __init__(self, payload):
        super().__init__("interrupt")
        self.payload = payload


_resume_values: contextvars.ContextVar = contextvars.ContextVar(
    "lgx_resume_values", default=None
)


def interrupt(payload):
    """Pause the current node and surface `payload` to the caller.

    Mirrors langgraph.types.interrupt: on resume, the node re-executes from
    its first line and this call returns the resume value instead of
    pausing. Anything the node did before this call (writes, bookings,
    messages) has already happened, and will happen again on re-execution.
    """
    values = _resume_values.get()
    if values:
        return values.pop(0)
    raise InterruptSignal(payload)


class Command:
    """A node return value that updates state and chooses the next node.

    Mirrors langgraph.types.Command(update=..., goto=...).
    """

    def __init__(self, update=None, goto=None):
        self.update = update or {}
        self.goto = goto


class Send:
    """A dynamic invocation of a node with a branch-local state overlay.

    Mirrors langgraph.types.Send: a router returns one or more Sends to fan
    work out; each target runs as part of the same super-step and its update
    merges back through the channel reducers.
    """

    def __init__(self, node, update=None):
        self.node = node
        self.update = update or {}


# --------------------------------------------------------------------------
# Reducers. A reducer combines the current channel value with a node's
# update. The default (no reducer in the schema) is overwrite.
# --------------------------------------------------------------------------

def overwrite(old, new):
    return new


def append_list(old, new):
    base = list(old) if old else []
    if new is None:
        return base
    if isinstance(new, list):
        return base + new
    return base + [new]


def add_numbers(old, new):
    return (old or 0) + (new or 0)


REDUCERS = {"overwrite": overwrite, "append": append_list, "add": add_numbers}


def _spec_reducer(spec):
    reducer = spec.get("reducer", "overwrite")
    if isinstance(reducer, str):
        return REDUCERS[reducer]
    return reducer


def _default_state(schema):
    state = {}
    for channel, spec in schema.items():
        default = spec.get("default")
        state[channel] = default() if callable(default) else copy.deepcopy(default)
    return state


def validate_state(schema, state):
    """Return a list of schema violations (empty when the state is valid)."""
    errors = []
    for channel, value in state.items():
        if channel not in schema:
            errors.append(f"unknown channel: {channel}")
            continue
        expected = schema[channel].get("type")
        if expected is not None and value is not None and not isinstance(value, expected):
            errors.append(
                f"channel {channel}: expected {expected}, got {type(value).__name__}"
            )
    return errors


def apply_update(schema, state, update):
    """Merge a node's partial update into state through the reducers."""
    for channel, value in (update or {}).items():
        if channel not in schema:
            raise GraphStructureError(f"node returned unknown channel: {channel}")
        merged = _spec_reducer(schema[channel])(state.get(channel), value)
        expected = schema[channel].get("type")
        if expected is not None and merged is not None and not isinstance(merged, expected):
            raise GraphStructureError(
                f"channel {channel}: update produced {type(merged).__name__}, "
                f"schema expects {expected}"
            )
        state[channel] = merged
    return state


class StateGraph:
    """Builder mirroring langgraph.graph.StateGraph."""

    def __init__(self, schema):
        self.schema = schema
        self.nodes: dict[str, object] = {}
        self.edges: dict[str, str] = {}
        self.routers: dict[str, tuple] = {}
        self.send_targets: set[str] = set()
        self.command_targets: dict[str, tuple] = {}

    def add_node(self, name, fn, via_send=False, command_targets=()):
        if name in (START, END):
            raise GraphStructureError(f"{name} is reserved")
        self.nodes[name] = fn
        if via_send:
            # Fan-out targets are invoked dynamically by Send, so they have
            # no incoming fixed edge and no outgoing edge of their own.
            self.send_targets.add(name)
        if command_targets:
            # Nodes a Command(goto=...) may jump to. Declared up front, the
            # way the framework reads them from the node's Command
            # annotation, so compile() can check reachability honestly.
            self.command_targets[name] = tuple(command_targets)
        return self

    def add_edge(self, source, target):
        self.edges[source] = target
        return self

    def add_conditional_edges(self, source, router, mapping=None):
        self.routers[source] = (router, mapping or {})
        return self

    def compile(self, checkpointer=None, interrupt_before=(), interrupt_after=(),
                max_steps=25):
        return CompiledGraph(
            self, checkpointer or InMemoryCheckpointer(),
            tuple(interrupt_before), tuple(interrupt_after), max_steps,
        )


class CompiledGraph:
    """A checked, runnable graph. Mirrors the compiled graph object that
    LangGraph's compile() returns, including its structural checks."""

    def __init__(self, builder, checkpointer, interrupt_before, interrupt_after,
                 max_steps):
        self.schema = builder.schema
        self.nodes = builder.nodes
        self.edges = builder.edges
        self.routers = builder.routers
        self.send_targets = builder.send_targets
        self.command_targets = builder.command_targets
        self.checkpointer = checkpointer
        self.interrupt_before = set(interrupt_before)
        self.interrupt_after = set(interrupt_after)
        self.max_steps = max_steps
        self._check_structure()

    # -- structure ---------------------------------------------------------
    def _check_structure(self):
        if START not in self.edges and START not in self.routers:
            raise GraphStructureError("graph has no entry edge from START")
        reachable = set()
        frontier = [self.edges.get(START)]
        while frontier:
            node = frontier.pop()
            if node is None or node == END or node in reachable:
                continue
            if node not in self.nodes:
                raise GraphStructureError(f"edge leads to unknown node: {node}")
            reachable.add(node)
            if node in self.edges:
                frontier.append(self.edges[node])
            if node in self.routers:
                _, mapping = self.routers[node]
                frontier.extend(mapping.values())
            frontier.extend(self.command_targets.get(node, ()))
        orphaned = sorted(set(self.nodes) - reachable - self.send_targets)
        if orphaned:
            raise GraphStructureError(f"orphaned nodes (unreachable): {orphaned}")
        for node in reachable:
            if node not in self.edges and node not in self.routers \
                    and node not in self.command_targets:
                raise GraphStructureError(f"node has no outgoing path: {node}")

    # -- checkpoint helpers -------------------------------------------------
    def _save(self, thread_id, state, next_node, status, total_steps,
              interrupt_payload=None, edited=False):
        return self.checkpointer.save(thread_id, {
            "step": total_steps,
            "total_steps": total_steps,
            "state": copy.deepcopy(state),
            "next_node": next_node,
            "status": status,
            "interrupt": interrupt_payload,
            "edited": edited,
        })

    def get_state(self, thread_id):
        return self.checkpointer.latest(thread_id)

    def get_state_history(self, thread_id):
        """All checkpoints for a thread, oldest first (stand-in for
        LangGraph's get_state_history)."""
        return self.checkpointer.history(thread_id)

    def update_state(self, thread_id, values):
        """Write values into the latest checkpoint as a new checkpoint.

        Mirrors LangGraph's update_state: the edit forks the history (the
        old checkpoint stays), and a paused thread resumes from the edited
        state. Returns the new checkpoint.
        """
        cp = self.checkpointer.latest(thread_id)
        if cp is None:
            raise GraphStructureError(f"unknown thread: {thread_id}")
        state = copy.deepcopy(cp["state"])
        apply_update(self.schema, state, values)
        return self._save(thread_id, state, cp["next_node"], cp["status"],
                          cp["total_steps"], cp.get("interrupt"), edited=True)

    def fork(self, thread_id, checkpoint_id, new_thread_id):
        """Start a new thread from an earlier checkpoint (time travel)."""
        cp = self.checkpointer.load(thread_id, checkpoint_id)
        if cp is None:
            raise GraphStructureError(
                f"no checkpoint {checkpoint_id} on thread {thread_id}")
        status = "done" if cp["status"] == "done" else "interrupted"
        return self._save(new_thread_id, cp["state"], cp["next_node"], status,
                          cp["total_steps"], cp.get("interrupt"), edited=True)

    # -- execution ----------------------------------------------------------
    def _run_node(self, name, state):
        fn = self.nodes[name]
        if isinstance(fn, CompiledGraph):
            # A compiled graph used as a node is a subgraph: it receives
            # only the channels its own schema declares, runs on its own
            # fresh thread per invocation (a finished thread would return
            # its old state), and returns the channels the parent shares.
            self._subgraph_calls = getattr(self, "_subgraph_calls", 0) + 1
            sub_input = {ch: copy.deepcopy(state[ch])
                         for ch in fn.schema if ch in state}
            sub = fn.invoke(sub_input,
                            thread_id=f"subgraph:{name}:{self._subgraph_calls}")
            if sub["status"] != "done":
                raise GraphStructureError(
                    f"subgraph {name} paused ({sub['status']}); the stand-in "
                    "runs subgraphs to completion")
            return {ch: sub["state"][ch] for ch in fn.schema
                    if ch in self.schema}
        return fn(state)

    def _route(self, source, state):
        router, mapping = self.routers[source]
        decision = router(state)
        if isinstance(decision, (Send, list)):
            sends = decision if isinstance(decision, list) else [decision]
            return ("send", sends)
        target = mapping.get(decision, decision)
        return ("node", target)

    def _execute(self, input_state, thread_id, resume, retry, events=None):
        cp = self.checkpointer.latest(thread_id)
        trace = []
        steps = 0
        if cp is None:
            state = _default_state(self.schema)
            if input_state:
                apply_update(self.schema, state, copy.deepcopy(input_state))
            errors = validate_state(self.schema, state)
            if errors:
                raise GraphStructureError("; ".join(errors))
            next_node = self.edges.get(START)
            total_steps = 0
            self._save(thread_id, state, next_node, "running", 0)
            skip_before_for = None
        else:
            state = copy.deepcopy(cp["state"])
            next_node = cp["next_node"]
            total_steps = cp["total_steps"]
            if cp["status"] == "done":
                return self._result("done", state, thread_id, 0, total_steps,
                                    trace, None)
            resumable = resume is not _UNSET or retry or cp.get("edited")
            if cp["status"] in ("interrupted", "error") and not resumable:
                raise RuntimeError(
                    f"thread {thread_id} is {cp['status']}; pass resume=... "
                    "or retry=True to continue it")
            # Resuming a breakpoint-before pause must execute the node it
            # paused in front of, not pause in front of it again.
            payload = cp.get("interrupt") or {}
            skip_before_for = (
                next_node if payload.get("breakpoint_before") == next_node
                else None
            )

        token = _resume_values.set([resume] if resume is not _UNSET else [])
        try:
            while True:
                if next_node == END or next_node is None:
                    self._save(thread_id, state, None, "done", total_steps)
                    return self._result("done", state, thread_id, steps,
                                        total_steps, trace, None)
                node = next_node
                if node in self.interrupt_before and node != skip_before_for:
                    saved = self._save(thread_id, state, node, "interrupted",
                                       total_steps,
                                       {"breakpoint_before": node})
                    return self._result("interrupted", state, thread_id, steps,
                                        total_steps, trace,
                                        saved["interrupt"])
                skip_before_for = None
                # Execute one node (one super-step in this stand-in, fan-out
                # handled below as one super-step with several executions).
                try:
                    raw = self._run_node(node, state)
                except InterruptSignal as signal:
                    steps += 1
                    total_steps += 1
                    trace.append({"step": total_steps, "node": node,
                                  "kind": "interrupt"})
                    self._save(thread_id, state, node, "interrupted",
                               total_steps, signal.payload)
                    return self._result("interrupted", state, thread_id, steps,
                                        total_steps, trace, signal.payload)
                except Exception as exc:  # crash: completed steps persist
                    self._save(thread_id, state, node, "error", total_steps)
                    raise
                steps += 1
                total_steps += 1
                goto = None
                update = raw
                if isinstance(raw, Command):
                    update, goto = raw.update, raw.goto
                update = update or {}
                apply_update(self.schema, state, copy.deepcopy(update))
                trace.append({"step": total_steps, "node": node,
                              "kind": "node",
                              "update_keys": sorted(update)})
                if events is not None:
                    events.append(("updates", {node: copy.deepcopy(update)}))
                    events.append(("values", copy.deepcopy(state)))
                if total_steps > self.max_steps:
                    self._save(thread_id, state, node, "error", total_steps)
                    raise StepLimitExceeded(
                        f"step limit {self.max_steps} exceeded at node {node}")
                # Decide the next step.
                if goto is not None:
                    following = goto
                elif node in self.routers:
                    kind, payload = self._route(node, state)
                    if kind == "send":
                        for send in payload:
                            branch = copy.deepcopy(state)
                            apply_update(self.schema, branch,
                                         copy.deepcopy(send.update))
                            sub_raw = self._run_node(send.node, branch)
                            sub_update = sub_raw.update if isinstance(
                                sub_raw, Command) else sub_raw
                            steps += 1
                            total_steps += 1
                            apply_update(self.schema, state,
                                         copy.deepcopy(sub_update or {}))
                            trace.append({"step": total_steps,
                                          "node": send.node, "kind": "send",
                                          "update_keys": sorted(
                                              sub_update or {})})
                            if events is not None:
                                events.append(("updates", {
                                    send.node: copy.deepcopy(
                                        sub_update or {})}))
                                events.append(("values",
                                               copy.deepcopy(state)))
                            if total_steps > self.max_steps:
                                self._save(thread_id, state, node, "error",
                                           total_steps)
                                raise StepLimitExceeded(
                                    f"step limit {self.max_steps} exceeded "
                                    f"in fan-out at {send.node}")
                        following = self.edges.get(node)
                        if following is None:
                            raise GraphStructureError(
                                f"fan-out source {node} needs a fixed edge "
                                "for the merge continuation")
                    else:
                        following = payload
                else:
                    following = self.edges.get(node)
                if node in self.interrupt_after:
                    saved = self._save(thread_id, state, following,
                                       "interrupted", total_steps,
                                       {"breakpoint_after": node})
                    return self._result("interrupted", state, thread_id, steps,
                                        total_steps, trace,
                                        saved["interrupt"])
                self._save(thread_id, state, following, "running", total_steps)
                next_node = following
        finally:
            _resume_values.reset(token)

    def _result(self, status, state, thread_id, steps, total_steps, trace,
                interrupt_payload):
        return {
            "status": status,
            "state": copy.deepcopy(state),
            "thread_id": thread_id,
            "steps": steps,
            "total_steps": total_steps,
            "trace": trace,
            "interrupt": interrupt_payload,
        }

    def invoke(self, input_state=None, *, thread_id="default", resume=_UNSET,
               retry=False):
        """Run the graph on a thread until it finishes or pauses.

        Mirrors the compiled graph's invoke: pass a state dict to start a
        thread, pass nothing plus resume=... (or retry=True after an error)
        to continue a paused one.
        """
        return self._execute(input_state, thread_id, resume, retry)

    def stream(self, input_state=None, *, thread_id="default", mode="values",
               resume=_UNSET, retry=False):
        """Yield run events. mode "values" yields the full state after each
        super-step; mode "updates" yields {node: update} per execution.

        Simplification, named: the stand-in collects the events during the
        run and then yields them; the framework streams them live.
        """
        events = []
        result = self._execute(input_state, thread_id, resume, retry, events)
        for kind, payload in events:
            if kind == mode:
                yield payload
        if result["status"] == "interrupted":
            yield {"__interrupt__": result["interrupt"]}
