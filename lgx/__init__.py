"""lgx: the local graph engine this course runs on.

A teaching stand-in that mirrors LangGraph semantics (state channels with
reducers, nodes, conditional edges, cycles with a step limit, checkpoints,
interrupts, Send fan-out, a cross-thread store). It is not LangGraph, is
not affiliated with it, and is never presented as it: see RESEARCH.md for
the sourced mapping between the two.
"""

from .checkpoint import FileCheckpointer, InMemoryCheckpointer
from .engine import (
    END,
    START,
    Command,
    GraphStructureError,
    Send,
    StateGraph,
    StepLimitExceeded,
    interrupt,
)
from .model import ModelStandin
from .store import Store

__all__ = [
    "END",
    "START",
    "Command",
    "FileCheckpointer",
    "GraphStructureError",
    "InMemoryCheckpointer",
    "ModelStandin",
    "Send",
    "StateGraph",
    "StepLimitExceeded",
    "Store",
    "interrupt",
]
