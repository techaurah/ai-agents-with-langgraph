"""Lesson 23 lab: the store's four operations and its one organising
idea, the namespace.

Five lead profiles go in under ("leads", <company slug>). A prefix
search over ("leads",) finds all five; a substring query narrows to the
one dental profile. Two ops notes go in under a different namespace and
the leads prefix still returns five: namespaces are how one store holds
many kinds of memory without them colliding. Rewriting an existing key
updates in place (still five), and a delete brings the count to four.
None of this is a database course; it is the minimum surface the memory
lessons build on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lgx import Store
from lgx.agent import load_leads


def evaluate():
    store = Store()
    companies = []
    for lead in load_leads()[:5]:
        slug = lead["company"].lower().replace(" ", "-")
        companies.append(slug)
        store.put(("leads", slug), "profile",
                  {"company": lead["company"], "channel": lead["channel"]})
    prefix = store.count(("leads",))
    dental = store.search(("leads",), query="dental")
    store.put(("notes", "ops"), "standup", {"text": "review approvals"})
    store.put(("notes", "ops"), "retro", {"text": "clarify rounds worked"})
    leads_after_notes = store.count(("leads",))
    store.put(("leads", companies[0]), "profile",
              {"company": "BrightPath Dental", "channel": "whatsapp"})
    after_update = store.count(("leads",))
    updated = store.get(("leads", companies[0]), "profile")
    store.delete(("leads", companies[4]), "profile")
    return {
        "profiles_stored": prefix,
        "prefix_search": prefix,
        "query_hits": len(dental),
        "leads_after_notes": leads_after_notes,
        "after_update_count": after_update,
        "updated_channel": updated["channel"],
        "after_delete_count": store.count(("leads",)),
        "missing_key_returns": store.get(("leads", "nope"), "profile"),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), indent=2, sort_keys=True))
