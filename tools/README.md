# Tools

Course maintenance checks, run in CI and before any release:

- `validate_course.py`: lesson structure, required README sections, the no-em-dash rule, the capstone gates file, and the fixture truth audit.
- `check_links.py`: every relative Markdown link in the repo resolves to a real file.

Run from the repo root:

```
python3 tools/validate_course.py
python3 tools/check_links.py
```
