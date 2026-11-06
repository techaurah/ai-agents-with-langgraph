# Lesson 23: The Store, Namespaces, and Keys

45 min · Intermediate · Prerequisites: Lesson 22

The store's surface is small: put, get, delete, and search, addressed by a namespace (a tuple, conventionally hierarchical like ("leads", company)) and a key. This lesson exercises the whole surface so Module 6's policy lesson can argue about content rather than mechanics.

Five lead profiles go in under their company namespaces. A prefix search over ("leads",) returns all 5; a substring query for "dental" narrows to the 1 dental profile. Two operations notes written under a different namespace do not disturb the count: namespaces partition the store the way threads partition checkpoints, and for the same reason (Lesson 22's exercise: no cross-company leakage). Rewriting an existing key updates it in place (the count stays 5, the value changes), and a delete brings the count to 4. A get on a missing key returns None, which Lesson 22 already used as the "new company" signal.

Two design notes for real systems. First, the stand-in's search is a substring scan over JSON; the framework's stores support richer queries and semantic search in some backends. The mechanics differ, the discipline does not: searches return memory, and memory is a prior. Second, keys are identities: "profile" per company here, but event-style memories want one key per fact (Lesson 24 writes field-at-date keys, which is what makes its write policies expressible).

## Run it

```
python3 store_lab.py
python3 smoke_test.py
```

## What the code measures

Profiles stored: 5; prefix search: 5; substring query hits: 1; leads count after writing to another namespace: still 5; after an in-place update: 5, with the updated channel value visible; after a delete: 4; a missing key returns None. Four operations, one partition rule, all counted.

## The same thing in real LangGraph

```python
store.put(("leads", "brightpath-dental"), "profile", {...})
items = store.search(("leads",), query="dental")
```

The framework's store API mirrors this shape (namespaces as tuples, items with namespace, key, and value); see RESEARCH.md.

## Common failures

- One flat namespace for everything: profiles, notes, and drafts collide and cross-contaminate. Partition by kind and owner from the first write.
- Keys that encode mutable facts ("current-budget"): the key then lies when the fact changes. Key by identity; let the value carry the fact and its date.
- Treating a None get as an error: absence is information (a new company, an unwritten fact) and Lesson 24's best policy depends on reading it that way.

## Recap checklist

- put, get, delete, search; namespace plus key; prefix search respects partitions.
- Updates rewrite in place; deletes remove; absence returns None, meaningfully.
- Key design (identity versus fact) decides which write policies are even possible.

## Resources

- Lesson 24: the write-policy argument that these mechanics enable.
