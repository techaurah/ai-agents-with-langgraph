"""Lesson 24 lab: what you write to memory matters more than that you
write.

Six returning-lead cases (fixtures/memory.json) each carry the facts an
earlier conversation produced, marked confirmed or tentative, dated, and
in two cases stale (true once, not any more). Two write policies face
the same recall question per case. Policy A saves everything and recalls
the oldest stored value: it answers 3 of 6 correctly, and every miss is
a stale or unconfirmed fact presented as current truth (a budget of 400
for a lead now at 1500; a decision-maker flag the company outgrew; a
tentative 900 treated as settled). Policy B saves only confirmed facts
and recalls the newest: 6 of 6, including the case where the honest
answer is "no confirmed budget on record", which the truth records as
null. The entry counts are nearly the same (12 against 11); the
difference is entirely policy, not volume.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import Store
from lgx.agent import load_memory_cases


def slug(company):
    return company.lower().replace(" ", "-").replace(" and ", "-")


def build_store(cases, policy):
    store = Store()
    for case in cases:
        ns = ("leads", slug(case["company"]))
        for fact in case["facts"]:
            if policy == "B" and not fact["confirmed"]:
                continue
            store.put(ns, f"{fact['field']}@{fact['recorded']}",
                      dict(fact))
    return store


def recall(store, case, policy):
    items = store.search(("leads", slug(case["company"])))
    candidates = [i["value"] for i in items
                  if i["value"]["field"] == case["field"]]
    if not candidates:
        return None
    if policy == "A":
        chosen = min(candidates, key=lambda f: f["recorded"])
    else:
        chosen = max(candidates, key=lambda f: f["recorded"])
    return chosen["value"]


def evaluate():
    cases = load_memory_cases()["cases"]
    results = {}
    wrong = {}
    entries = {}
    for policy in ("A", "B"):
        store = build_store(cases, policy)
        entries[policy] = store.count()
        correct = 0
        wrong[policy] = []
        for case in cases:
            if recall(store, case, policy) == case["truth"]:
                correct += 1
            else:
                wrong[policy].append(case["company"])
        results[policy] = correct
    return {
        "cases": len(cases),
        "policy_a_correct": results["A"],
        "policy_b_correct": results["B"],
        "policy_a_entries": entries["A"],
        "policy_b_entries": entries["B"],
        "policy_a_wrong_cases": wrong["A"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
