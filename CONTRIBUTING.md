# Contributing

Contributions are welcome: corrections, clearer explanations, additional exercises, and translations.

Ground rules, enforced by the validators in `tools/` and by CI:

- Runnable code uses the Python standard library only and must run offline. No API keys, no live model calls; anything model-like uses the labelled deterministic stand-in.
- Every number in prose must be produced by the lesson's own code on the bundled fixtures, and asserted by that lesson's smoke test.
- The stand-in engine is never described as LangGraph. Framework claims belong in RESEARCH.md with a source and a check date.
- No em dashes anywhere.
- Capstone gates are fixed; proposing a gate change is a specification discussion, opened as an issue first.

Process: open an issue or a pull request, keep changes scoped to one lesson or one concern, and run the full local check before submitting:

```
python3 -m compileall .
python3 tools/validate_course.py
python3 tools/check_links.py
for d in [0-9][0-9]-*/; do (cd "$d" && python3 smoke_test.py); done
```
