# Working in this repo

Notes for anyone (human or agent) changing the course:

- The runnable track is the `lgx` stand-in engine on the Python standard library. Never present it as LangGraph, in code or prose. Real LangGraph appears only as labelled reference snippets in lesson READMEs; those snippets are not executed by CI and must target the version recorded in RESEARCH.md.
- Every number quoted in a lesson must be produced by that lesson's own code on the bundled fixtures, and the lesson's smoke test must assert it. If a number changes, the prose, the smoke test, and the root README scorecard change together.
- The capstone gates in `29-capstone-spec/capstone/gates.json` are fixed. Changing them is a specification decision: do it openly, in its own commit, with the reason recorded in the file's set_from field, never during grading.
- No em dashes in any file. Validators enforce this; write around it.
- Keep honest negatives. If a change makes a measured result worse, the printed number changes and the prose says so.
- Before publishing changes: run `python3 -m compileall .`, `python3 tools/validate_course.py`, `python3 tools/check_links.py`, and every lesson's smoke test from its own folder (the CI workflow does exactly this).
