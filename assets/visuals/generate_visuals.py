"""Generate the course's branded SVG visuals.

Run from anywhere:  python3 assets/visuals/generate_visuals.py
Writes the SVGs beside this script. Every number drawn here was measured
by the lesson named in VISUALS.md; the generator only draws, it does not
compute results.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent

NAVY = "#0B1F4A"
LIGHT = "#E0F2FE"
CYAN = "#0891B2"
AMBER = "#F59E0B"
GREY = "#475569"
GREEN = "#15803D"
RED = "#B91C1C"
FONT = "Georgia, 'Times New Roman', serif"


def svg_open(width, height):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
    ]


def text(x, y, s, size=16, fill=NAVY, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{s}</text>')


def box(x, y, w, h, fill=LIGHT, stroke=NAVY, r=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')


def arrow(x1, y1, x2, y2, color=NAVY):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="2" marker-end="url(#arr)"/>')


def defs():
    return ('<defs><marker id="arr" markerWidth="8" markerHeight="8" '
            'refX="7" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" '
            f'fill="{NAVY}"/></marker></defs>')


def save(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n</svg>\n", encoding="utf-8")


def course_map():
    modules = [
        ("Module 0 · Foundations", "00-02"),
        ("Module 1 · State and nodes", "03-05"),
        ("Module 2 · Control flow", "06-09"),
        ("Module 3 · The LeadPipe agent", "10-13"),
        ("Module 4 · Persistence", "14-17"),
        ("Module 5 · Human in the loop", "18-21"),
        ("Module 6 · Memory", "22-24"),
        ("Module 7 · Composition", "25-26"),
        ("Module 8 · Production patterns", "27-28"),
        ("Module 9 · Capstone", "29-31"),
    ]
    lines = svg_open(1000, 620)
    lines.append(defs())
    lines.append(text(500, 52, "AI Agents with LangGraph: course map", 30,
                      NAVY, "middle", "bold"))
    lines.append(text(500, 82, "32 lessons · 10 modules · one running agent",
                      17, GREY, "middle"))
    for i, (title, span) in enumerate(modules):
        col, row = i % 2, i // 2
        x, y = 40 + col * 480, 110 + row * 98
        lines.append(box(x, y, 440, 82, LIGHT if row % 2 == 0 else "#FFFFFF"))
        lines.append(text(x + 24, y + 36, title, 19, NAVY, "start", "bold"))
        lines.append(text(x + 24, y + 64, f"Lessons {span}", 15, CYAN))
    save("course-map.svg", lines)


def graph_anatomy():
    lines = svg_open(1000, 430)
    lines.append(defs())
    lines.append(text(500, 48, "Anatomy of a graph run", 28, NAVY,
                      "middle", "bold"))
    # State panel
    lines.append(box(40, 90, 250, 210, "#FFFFFF"))
    lines.append(text(165, 122, "STATE", 17, NAVY, "middle", "bold"))
    for i, ch in enumerate(("lead", "score · band", "missing",
                            "booked_slot", "outcome", "events")):
        lines.append(text(65, 156 + i * 24, ch, 15, GREY))
    lines.append(text(165, 322, "channels + reducers", 13, CYAN, "middle"))
    # Node flow
    nodes = [("intake", 360), ("score", 500), ("approve", 640), ("book", 780)]
    for name, cx in nodes:
        lines.append(box(cx - 58, 130, 116, 56, LIGHT))
        lines.append(text(cx, 165, name, 17, NAVY, "middle", "bold"))
    lines.append(arrow(292, 158, 300, 158))
    for a, b in ((418, 440), (558, 580), (698, 720)):
        lines.append(arrow(a, 158, b, 158))
    lines.append(box(852, 130, 100, 56, NAVY))
    lines.append(text(902, 165, "END", 17, "#FFFFFF", "middle", "bold"))
    lines.append(arrow(838, 158, 850, 158))
    lines.append(text(640, 120, "interrupt: a human decides here", 14,
                      AMBER, "middle", "bold"))
    # Checkpointer band
    lines.append(box(360, 250, 592, 60, LIGHT))
    lines.append(text(656, 276, "CHECKPOINTER", 15, NAVY, "middle", "bold"))
    lines.append(text(656, 298, "a snapshot at every super-step boundary",
                      14, GREY, "middle"))
    lines.append(arrow(656, 190, 656, 246, CYAN))
    lines.append(text(500, 380, "Nodes return partial updates; edges and "
                      "routers decide what runs next.", 15, GREY, "middle"))
    save("graph-anatomy.svg", lines)


def super_steps():
    labels = ["initial", "intake", "score", "approve", "approve", "book",
              "crm_log", "done"]
    notes = ["snapshot", "step 1", "step 2", "PAUSED", "resumed", "step 5",
             "step 6", "terminal"]
    lines = svg_open(1000, 380)
    lines.append(defs())
    lines.append(text(500, 48, "One run, eight checkpoints (lead L-001)",
                      26, NAVY, "middle", "bold"))
    lines.append(text(500, 76, "A snapshot is written at every super-step "
                      "boundary, plus the pause and the finish.", 15, GREY,
                      "middle"))
    for i, (label, note) in enumerate(zip(labels, notes)):
        cx = 80 + i * 120
        fill = AMBER if note == "PAUSED" else (NAVY if label == "done"
                                               else LIGHT)
        tcol = "#FFFFFF" if fill == NAVY else NAVY
        lines.append(box(cx - 52, 150, 104, 64, fill))
        lines.append(text(cx, 178, label, 14, tcol, "middle", "bold"))
        lines.append(text(cx, 198, note, 12, tcol, "middle"))
        if i < len(labels) - 1:
            lines.append(arrow(cx + 54, 182, cx + 66, 182))
    lines.append(text(500, 280, "The paused checkpoint holds state, next "
                      "node (approve), and status (interrupted):", 15, GREY,
                      "middle"))
    lines.append(text(500, 306, "everything a resume needs, nothing else "
                      "required.", 15, GREY, "middle"))
    save("super-steps.svg", lines)


def crash_resume():
    steps = [
        ("run", "intake, score"),
        ("approve", "human says yes"),
        ("book", "writes the ledger"),
        ("CRASH", "mid-node, after write"),
        ("resume", "new process, same dir"),
        ("book again", "ledger check: reuse"),
        ("done", "exactly 1 booking"),
    ]
    lines = svg_open(1000, 400)
    lines.append(defs())
    lines.append(text(500, 48, "Crash and resume: the Lesson 16 drill",
                      26, NAVY, "middle", "bold"))
    for i, (title, note) in enumerate(steps):
        cx = 78 + i * 136
        fill = RED if title == "CRASH" else (AMBER if title == "book again"
                                             else LIGHT)
        tcol = "#FFFFFF" if fill == RED else NAVY
        lines.append(box(cx - 62, 140, 124, 74, fill))
        lines.append(text(cx, 170, title, 14, tcol, "middle", "bold"))
        lines.append(text(cx, 192, note, 10.5, tcol, "middle"))
        if i < len(steps) - 1:
            lines.append(arrow(cx + 64, 177, cx + 72, 177))
    lines.append(text(500, 280, "The checkpoint rolls back nothing outside "
                      "the graph; the node's own ledger check is what makes "
                      "the redo safe.", 15, GREY, "middle"))
    lines.append(text(500, 306, "Unguarded, the same drill books twice "
                      "(Lesson 28).", 15, GREY, "middle"))
    save("crash-resume.svg", lines)


def capstone_gates():
    rows = [
        ("Band accuracy (min 0.9)", "1.0", "1.0", True),
        ("Task success (min 0.9)", "0.8333", "1.0", False),
        ("Policy escapes (max 0)", "1", "0", False),
        ("Crash-lead bookings (exact 1)", "2", "1", False),
        ("Ledger entries (exact 4)", "6", "4", False),
        ("Mean steps (max 6.0)", "5.17", "4.92", True),
    ]
    lines = svg_open(1000, 560)
    lines.append(defs())
    lines.append(text(500, 48, "Capstone gates: fixed before the build",
                      26, NAVY, "middle", "bold"))
    lines.append(text(70, 108, "Gate", 16, GREY, "start", "bold"))
    lines.append(text(640, 108, "As-built", 16, GREY, "middle", "bold"))
    lines.append(text(850, 108, "Hardened", 16, GREY, "middle", "bold"))
    for i, (gate, asb, hard, asb_ok) in enumerate(rows):
        y = 128 + i * 58
        lines.append(box(40, y, 920, 48, LIGHT if i % 2 == 0 else "#FFFFFF"))
        lines.append(text(70, y + 30, gate, 16, NAVY))
        lines.append(text(640, y + 30, asb, 17, GREEN if asb_ok else RED,
                          "middle", "bold"))
        lines.append(text(850, y + 30, hard, 17, GREEN, "middle", "bold"))
    lines.append(text(500, 520, "Gates passed: as-built 2 of 6 · hardened "
                      "6 of 6 (Lesson 31)", 16, NAVY, "middle", "bold"))
    save("capstone-gates.svg", lines)


def graph_vs_pipeline():
    lines = svg_open(1000, 460)
    lines.append(defs())
    lines.append(text(500, 48, "Lesson 01: the graph costs more on linear "
                      "work", 25, NAVY, "middle", "bold"))
    # Executions bars
    lines.append(text(70, 120, "Calls / executions (12 leads)", 16, NAVY,
                      "start", "bold"))
    lines.append(box(70, 136, 56 * 11, 40, CYAN))
    lines.append(text(70 + 56 * 11 + 16, 162, "pipeline: 56", 16, NAVY))
    lines.append(box(70, 186, 59 * 11, 40, NAVY))
    lines.append(text(70 + 59 * 11 + 16, 212, "graph: 59", 16, NAVY))
    # Checkpoint bars
    lines.append(text(70, 286, "Checkpoint writes", 16, NAVY, "start",
                      "bold"))
    lines.append(box(70, 302, 8, 40, CYAN))
    lines.append(text(94, 328, "pipeline: 0", 16, NAVY))
    lines.append(box(70, 352, 84 * 7, 40, NAVY))
    lines.append(text(70 + 84 * 7 + 16, 378, "graph: 84", 16, NAVY))
    lines.append(text(500, 432, "Outcomes agree 12 of 12. The graph buys "
                      "pause, resume, recovery, and audit.", 15, GREY,
                      "middle"))
    save("graph-vs-pipeline.svg", lines)


if __name__ == "__main__":
    course_map()
    graph_anatomy()
    super_steps()
    crash_resume()
    capstone_gates()
    graph_vs_pipeline()
    print("visuals written")
