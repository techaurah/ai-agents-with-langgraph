"""Lesson 00 lab: prove the lab works before learning anything in it.

Checks the interpreter, the lgx stand-in, the fixtures (including that the
fixture truth records are exactly what the published rubric produces), and
the course layout. If evaluate() is not all green, nothing later in the
course can be trusted.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx.agent import band_for_score, load_leads, load_policy, score_lead


def evaluate():
    import lgx  # noqa: F401  (the import itself is one of the checks)

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
    root = Path(__file__).resolve().parents[1]
    lesson_folders = len([
        p for p in root.iterdir()
        if p.is_dir() and len(p.name) > 2 and p.name[:2].isdigit()
        and p.name[2] == "-"
    ])
    python_ok = sys.version_info >= (3, 10)
    return {
        "python_ok": python_ok,
        "python_version": ".".join(str(v) for v in sys.version_info[:3]),
        "engine_imports": True,
        "leads": len(leads),
        "truth_verified": truth_verified,
        "lesson_folders": lesson_folders,
        "all_ok": python_ok and truth_verified == len(leads)
                  and lesson_folders == 32,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
