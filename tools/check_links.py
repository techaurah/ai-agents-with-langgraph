"""Check that relative Markdown links resolve to files in the repo.

External links (http, https, mailto) and pure anchors are skipped; a
relative link target must exist on disk relative to the file that links
it. Exits non-zero and prints every broken link it finds.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def main() -> int:
    broken: list[str] = []
    checked = 0
    for md in sorted(ROOT.rglob("*.md")):
        if "__pycache__" in md.parts:
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        for target in LINK_RE.findall(text):
            target = target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            checked += 1
            if not (md.parent / path_part).exists():
                broken.append(
                    f"{md.relative_to(ROOT)}: broken link {target!r}")
    if broken:
        print(f"check_links: {len(broken)} broken link(s)")
        for entry in broken:
            print(f"  - {entry}")
        return 1
    print(f"check_links: OK ({checked} relative links checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
