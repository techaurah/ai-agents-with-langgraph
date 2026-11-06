"""Validate the course structure and content rules.

Checks, from the repo root:
- every numbered lesson folder holds README.md, exercise.md,
  smoke_test.py, at least one runnable lab .py, and solution/SOLUTION.md;
- every lesson README carries the five required sections and is
  substantive (over 800 characters);
- no em dash character appears in any text file in the repo;
- the capstone gates file exists, is dated, and carries the six gates;
- the fixture truth records are exactly what the published rubric
  produces (the answer key audit from Lesson 29);
- the root files the course promises all exist.

Exits non-zero and prints every problem it finds.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EM_DASH = "\u2014"  # escape form, so this file passes its own check
TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".yml", ".svg"}
REQUIRED_SECTIONS = (
    "## Run it",
    "## What the code measures",
    "## Common failures",
    "## Recap checklist",
    "## Resources",
)
ROOT_FILES = (
    "README.md", "AGENTS.md", "CHANGELOG.md", "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md", "DESIGN.md", "LICENSE", "PROGRESS.md",
    "RESEARCH.md", "SECURITY.md", "llms.txt", "requirements.txt",
)
EXPECTED_GATES = {
    "band_accuracy_min", "task_success_rate_min", "policy_escapes_max",
    "crash_lead_bookings_exact", "booking_ledger_entries_exact",
    "mean_steps_max",
}


def lesson_dirs() -> list[Path]:
    return sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and re.match(r"^\d\d-", p.name)
    )


def main() -> int:
    problems: list[str] = []

    for name in ROOT_FILES:
        if not (ROOT / name).is_file():
            problems.append(f"missing root file: {name}")

    lessons = lesson_dirs()
    if len(lessons) != 32:
        problems.append(f"expected 32 lessons, found {len(lessons)}")
    for lesson in lessons:
        for required in ("README.md", "exercise.md", "smoke_test.py",
                         "solution/SOLUTION.md"):
            if not (lesson / required).is_file():
                problems.append(f"{lesson.name}: missing {required}")
        labs = [p for p in lesson.glob("*.py") if p.name != "smoke_test.py"]
        if not labs:
            problems.append(f"{lesson.name}: no runnable lab .py")
        readme = lesson / "README.md"
        if readme.is_file():
            text = readme.read_text(encoding="utf-8")
            if len(text) <= 800:
                problems.append(f"{lesson.name}: README too short "
                                f"({len(text)} chars)")
            for section in REQUIRED_SECTIONS:
                if section not in text:
                    problems.append(
                        f"{lesson.name}: README missing section {section!r}")

    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES \
                and "__pycache__" not in path.parts:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if EM_DASH in text:
                problems.append(f"em dash found in {path.relative_to(ROOT)}")

    gates_path = ROOT / "29-capstone-spec" / "capstone" / "gates.json"
    if not gates_path.is_file():
        problems.append("missing capstone gates file")
    else:
        doc = json.loads(gates_path.read_text(encoding="utf-8"))
        if not doc.get("fixed_on"):
            problems.append("gates file has no fixed_on date")
        gates = doc.get("capstone_system", {}).get("gates", {})
        if set(gates) != EXPECTED_GATES:
            problems.append(
                f"gates keys differ: {sorted(gates)} vs "
                f"{sorted(EXPECTED_GATES)}")

    try:
        from lgx.agent import (band_for_score, load_leads, load_policy,
                               score_lead)
        policy = load_policy()
        verified = 0
        for lead in load_leads():
            completed = dict(lead)
            for field, value in lead.get("followup_answers", {}).items():
                completed[field] = value
            score = score_lead(completed, policy)
            if score == lead["truth"]["score"] and \
                    band_for_score(score, policy) == lead["truth"]["band"]:
                verified += 1
        if verified != 12:
            problems.append(f"fixture truth verified for {verified}/12 leads")
    except Exception as exc:  # the audit itself failing is a finding
        problems.append(f"fixture audit failed: {exc}")

    if problems:
        print(f"validate_course: {len(problems)} problem(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"validate_course: OK ({len(lessons)} lessons, "
          f"gates and fixtures verified)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
