"""Lesson 29 lab: the capstone spec, checked as code before any
capstone code exists.

The gates live in capstone/gates.json, fixed on 2026-11-06 from the
earlier modules' measurements (the file's set_from field says from
where). This lab does not build anything. It verifies that the fixture
truth the gates will grade against is itself sound: every lead's truth
score and band are exactly what the published rubric produces from its
completed record, the approval-required set is the three leads policy
says it is, exactly one lead carries the crash drill, and the truth
outcomes imply exactly four bookings. A capstone graded against a
broken answer key would prove nothing; this is the answer key's audit.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import (band_for_score, load_leads, load_policy,
                       needs_approval, score_lead)

GATES_PATH = Path(__file__).with_name("capstone") / "gates.json"


def evaluate():
    gates_doc = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    gates = gates_doc["capstone_system"]["gates"]
    policy = load_policy()
    leads = load_leads()
    truth_verified = 0
    for lead in leads:
        completed = dict(lead)
        for field, value in lead.get("followup_answers", {}).items():
            completed[field] = value
        score = score_lead(completed, policy)
        if score == lead["truth"]["score"] and \
                band_for_score(score, policy) == lead["truth"]["band"]:
            truth_verified += 1
    approval_required = sum(1 for l in leads if needs_approval(l, policy))
    crash_leads = sum(1 for l in leads if l.get("crash_in_booking"))
    expected_bookings = sum(1 for l in leads
                            if l["truth"]["outcome"] == "booked")
    return {
        "gates_count": len(gates),
        "gates_fixed_on": gates_doc["fixed_on"],
        "truth_records_verified": truth_verified,
        "approval_required": approval_required,
        "crash_leads": crash_leads,
        "expected_bookings": expected_bookings,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
