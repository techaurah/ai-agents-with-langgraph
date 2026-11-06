"""A deterministic stand-in for a hosted language model.

This is not a model. It is a fixed decision table, labelled as a stand-in
everywhere it appears, used wherever a lesson needs "the model decides
which tool to call next" behaviour: the ReAct loop in Lesson 08 and the
batch drills. Hosted models are non-deterministic and need API keys, which
would make the course's numbers unrepeatable; the stand-in reads the same
state a real model would be shown and applies the stated rule every time,
so any number a lesson quotes can be reproduced by re-running it.

The rule, stated once here and in Lesson 08: work through the task's
required observations in order. Ask for the first one that is missing
(company profile, then slot availability, then a drafted reply); when all
three are present, answer "final".
"""

from __future__ import annotations


class ModelStandin:
    """Rule-based decider with a call counter, so lessons can count how
    many model decisions a loop actually made."""

    REQUIRED = ("company", "slot", "draft")
    TOOLS = {
        "company": "lookup_company",
        "slot": "check_slot",
        "draft": "draft_reply",
    }

    def __init__(self):
        self.calls = 0

    def decide(self, observations: dict) -> dict:
        self.calls += 1
        for field in self.REQUIRED:
            if field not in observations:
                return {"tool": self.TOOLS[field], "for": field}
        return {"final": "all observations gathered"}
