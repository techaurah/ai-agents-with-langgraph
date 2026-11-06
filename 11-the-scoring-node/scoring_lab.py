"""Lesson 11 lab: the rubric, scored honestly, including the leads it
cannot score yet.

All twelve fixture leads are scored twice: as they arrived, and after
their recorded follow-up answers fill the missing fields. Ten leads
arrive complete and score identically both times. L-004 (no budget on
arrival) provisionally scores 60, a WARM, against a completed 90; L-008
(no budget, no decision-maker flag) provisionally scores 25 against a
completed 53. Neither provisional score is a rounding issue: the rubric
pays 0 for unknown fields, by design, so an unscored lead looks like a
weak lead until something asks. The lab also measures how close the set
runs to the band thresholds: L-005 sits one point above the WARM floor.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import band_for_score, load_leads, load_policy, score_lead


def evaluate():
    policy = load_policy()
    thresholds = (policy["bands"]["hot_min"], policy["bands"]["warm_min"])
    as_arrived = {}
    completed = {}
    provisional = {}
    bands = {"HOT": 0, "WARM": 0, "NURTURE": 0}
    min_distance = None
    for lead in load_leads():
        raw = score_lead(lead, policy)
        as_arrived[lead["id"]] = raw == lead["truth"]["score"]
        filled = dict(lead)
        for field, value in lead.get("followup_answers", {}).items():
            filled[field] = value
        final = score_lead(filled, policy)
        completed[lead["id"]] = final == lead["truth"]["score"]
        if raw != final:
            provisional[lead["id"]] = raw
        bands[band_for_score(final, policy)] += 1
        distance = min(abs(final - t) for t in thresholds)
        min_distance = distance if min_distance is None else min(
            min_distance, distance)
    return {
        "leads": len(as_arrived),
        "complete_data": sum(1 for l in load_leads()
                             if not l["id"] in provisional),
        "as_arrived_score_matches": sum(as_arrived.values()),
        "after_answers_score_matches": sum(completed.values()),
        "provisional_scores": provisional,
        "bands": bands,
        "min_boundary_distance": min_distance,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
