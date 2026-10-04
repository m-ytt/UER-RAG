#!/usr/bin/env python3
"""Build one dense, publication-style UER-RAG flowchart as editable SVG."""

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)
SVG = OUT / "UER_RAG_academic_flowchart_sample.svg"

W, H = 2000, 1260
INK = "#1F2323"
BLUE = "#E5EDF1"
BLUE_D = "#91A9B5"
GREEN = "#E7ECE3"
GREEN_D = "#9CAD97"
WHITE = "#FFFFFF"
GRAY = "#F5F6F4"

parts: list[str] = []


def add(s: str) -> None:
    parts.append(s)


def txt(x, y, value, size=22, weight=400, anchor="start", fill=INK, italic=False, family="Arial"):
    style = "italic" if italic else "normal"
    add(
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}" '
        f'fill="{fill}">{escape(str(value))}</text>'
    )


def line_text(x, y, lines, size=20, gap=28, weight=400, fill=INK, xpad=0):
    for i, line in enumerate(lines):
        txt(x + xpad, y + i * gap, line, size=size, weight=weight, fill=fill)


def box(x, y, w, h, fill=WHITE, stroke=INK, sw=2.2, rx=12):
    add(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
    )


def panel(x, y, w, h, title, fill, head, step_no, title_size=24):
    box(x, y, w, h, fill=fill, stroke=INK, sw=2.4, rx=14)
    add(
        f'<path d="M{x + 14},{y} H{x + w - 14} Q{x + w},{y} {x + w},{y + 14} '
        f'V{y + 50} H{x} V{y + 14} Q{x},{y} {x + 14},{y} Z" fill="{head}"/>'
    )
    add(
        f'<line x1="{x}" y1="{y + 50}" x2="{x + w}" y2="{y + 50}" '
        f'stroke="{INK}" stroke-width="2.2"/>'
    )
    txt(x + 18, y + 33, title, size=title_size, weight=700)
    add(
        f'<circle cx="{x - 22}" cy="{y + 25}" r="24" fill="{WHITE}" '
        f'stroke="{INK}" stroke-width="2.4"/>'
    )
    txt(x - 22, y + 33, step_no, size=22, weight=700, anchor="middle")


def small_box(x, y, w, h, title, lines=(), fill=WHITE, title_size=21, body_size=18, centered=False):
    box(x, y, w, h, fill=fill, stroke=INK, sw=1.8, rx=9)
    anchor = "middle" if centered else "start"
    tx = x + w / 2 if centered else x + 14
    txt(tx, y + 27, title, size=title_size, weight=700, anchor=anchor)
    for i, line in enumerate(lines):
        txt(tx, y + 53 + i * 24, line, size=body_size, anchor=anchor)


def arrow(path, label=None, lx=None, ly=None, label_w=None):
    add(
        f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrow)"/>'
    )
    if label and lx is not None and ly is not None:
        # Labels are placed in dedicated gutters and never drawn on top of an
        # arrow.  Keeping the label background transparent also makes an
        # accidental overlap visible during visual QA instead of masking it.
        txt(lx, ly, label, size=17, weight=400, anchor="middle")


def divider(x1, y1, x2, y2):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.5"/>')


add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>UER-RAG academic workflow sample</title>
<desc>Dense two-color academic flowchart with protected direct generation, dual retrieval, reciprocal-rank fusion, structured verification, deterministic auditing, and source selection.</desc>
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/>
  </marker>
</defs>
<rect x="0" y="0" width="{W}" height="{H}" fill="{WHITE}"/>
''')

# Step 1 — observable input packet.
panel(70, 70, 330, 470, "Input query and metadata", BLUE, BLUE_D, 1)
small_box(92, 145, 286, 70, "Question text  x", ["Entity-oriented QA request"], fill=WHITE)
small_box(92, 230, 136, 82, "Title  t", ["surface name"], fill=WHITE)
small_box(242, 230, 136, 82, "Subject  s", ["entity sense"], fill=WHITE)
small_box(92, 327, 286, 82, "Relation  r", ["target attribute / predicate"], fill=WHITE)
small_box(
    92,
    424,
    286,
    86,
    "Normalized packet  m=(t,s,r)",
    ["Unicode cleanup · alias normalization"],
    fill=GRAY,
    body_size=17,
)

# Step 2 — direct answer, protected before retrieval.
panel(460, 70, 300, 210, "Protected direct generation", GREEN, GREEN_D, 2, title_size=20)
small_box(
    483,
    140,
    254,
    108,
    "LLM call 1",
    ["short answer  d", "persisted before retrieval", "protected fallback"],
    fill=WHITE,
)

# Step 3 — two retrieval views.
panel(460, 330, 300, 270, "Dual-query construction", BLUE, BLUE_D, 3, title_size=21)
small_box(482, 400, 256, 78, "Answer-free  q₀", ["N(x ⊕ t ⊕ s ⊕ r)"], fill=WHITE)
small_box(
    482,
    493,
    256,
    78,
    "Conditional view  q₁",
    ["if d ≠ ∅: N(q₀ ⊕ d); d is untrusted"],
    fill=WHITE,
    body_size=16,
)

# Step 4 — one corpus, two ranked views.
panel(830, 70, 500, 530, "Parallel retrieval from a shared corpus", BLUE, BLUE_D, 4)
small_box(
    955,
    135,
    250,
    72,
    "Wikipedia passage index",
    ["retrieve_k = 50 per query"],
    fill=WHITE,
    centered=True,
    body_size=17,
)
small_box(858, 257, 205, 277, "Ranking  R₀", [], fill=WHITE)
small_box(1097, 257, 205, 277, "Ranking  R₁", [], fill=WHITE)
for i, (pid, desc) in enumerate(
    [
        ("p1 · rank 1", "subject + relation"),
        ("p3 · rank 2", "biographical context"),
        ("p5 · rank 3", "answer-bearing span"),
        ("p7 · rank 4", "background context"),
    ]
):
    yy = 307 + i * 52
    box(875, yy, 171, 42, fill=GREEN if i in (0, 2) else GRAY, stroke=INK, sw=1.2, rx=4)
    txt(887, yy + 18, pid, size=16, weight=700)
    txt(887, yy + 35, desc, size=13)
for i, (pid, desc) in enumerate(
    [
        ("p2 · rank 1", "direct-answer cue"),
        ("p1 · rank 2", "shared support"),
        ("p5 · rank 3", "shared support"),
        ("p8 · rank 4", "background context"),
    ]
):
    yy = 307 + i * 52
    box(1114, yy, 171, 42, fill=GREEN if i in (1, 2) else GRAY, stroke=INK, sw=1.2, rx=4)
    txt(1126, yy + 18, pid, size=16, weight=700)
    txt(1126, yy + 35, desc, size=13)
arrow("M1080,207 V247 H960 V257", "retrieve q₀", 1005, 238, 104)
arrow("M1080,207 V225 H1200 V257", "retrieve q₁", 1195, 250, 104)

# Step 5 — rank-only fusion and addressable evidence.
panel(1400, 70, 520, 530, "Passage alignment, RRF, and evidence", GREEN, GREEN_D, 5)
small_box(
    1423,
    137,
    474,
    90,
    "Identity-based deduplication",
    ["same passage ID → merge; duplicates never count twice"],
    fill=WHITE,
    body_size=17,
)
small_box(
    1423,
    245,
    474,
    98,
    "Reciprocal-rank fusion",
    ["S(p)=Σq∈{q₀,q₁} 1/(20+rankq(p))", "rank positions only; raw retriever scores are not mixed"],
    fill=WHITE,
    body_size=16,
)
small_box(1423, 361, 474, 170, "Top-3 evidence bundle  D", [], fill=WHITE)
for i, (d, p, role) in enumerate(
    [
        ("D1", "p1", "subject + answer support"),
        ("D2", "p5", "answer context"),
        ("D3", "p2", "q₁-only distractor context"),
    ]
):
    yy = 410 + i * 36
    box(1443, yy, 434, 29, fill=BLUE if i < 2 else GRAY, stroke=INK, sw=1.0, rx=3)
    txt(1454, yy + 20, f"{d} = {p}", size=15, weight=700)
    txt(1560, yy + 20, role, size=15)

# Step 6 — structured verifier.
panel(1400, 670, 520, 340, "Structured evidence verification", BLUE, BLUE_D, 6)
small_box(
    1423,
    740,
    205,
    220,
    "Verifier input",
    ["x : question", "m : metadata", "d : direct answer", "D : cited passages", "LLM call 2"],
    fill=WHITE,
)
small_box(
    1650,
    740,
    247,
    220,
    "Fixed-schema record  v",
    [
        "candidate: e",
        "support: H / M / L / N",
        "utility: helpful / neutral",
        "citations: C ⊆ {1,2,3}",
        "reason: short rationale",
    ],
    fill=WHITE,
    body_size=17,
)

# Step 7 — deterministic audit.
panel(830, 670, 500, 340, "Deterministic six-check risk audit", GREEN, GREEN_D, 7)
checks = [
    ("c1", "e ≠ ∅", "candidate exists"),
    ("c2", "u = helpful", "usefulness"),
    ("c3", "s ∈ {H,M}", "support level"),
    ("c4", "ground(e,C)", "answer grounding"),
    ("c5", "ground(subject,C)", "entity grounding"),
    ("c6", "N(e) ≠ N(d)", "non-trivial change"),
]
for i, (ci, pred, desc) in enumerate(checks):
    col, row = i % 3, i // 3
    xx, yy = 854 + col * 153, 742 + row * 100
    box(xx, yy, 137, 82, fill=WHITE, stroke=INK, sw=1.5, rx=7)
    txt(xx + 12, yy + 24, ci, size=18, weight=700)
    txt(xx + 68, yy + 49, pred, size=16, weight=700, anchor="middle")
    txt(xx + 68, yy + 70, desc, size=13, anchor="middle")
small_box(
    854,
    943,
    452,
    42,
    "Recompute lexical grounding only on cited set  C",
    [],
    fill=BLUE,
    centered=True,
    title_size=16,
)

# Step 8 — conjunctive authorization and archived deterministic post-audit.
panel(460, 670, 300, 340, "Source gate and post-audit", GREEN, GREEN_D, 8, title_size=19)
small_box(
    482,
    735,
    256,
    60,
    "Authorization gate",
    ["g = ∏ⱼ₌₁⁶ cⱼ"],
    fill=WHITE,
    centered=True,
    body_size=18,
)
small_box(482, 807, 256, 42, "g = 1  →  Evidence e", [], fill=BLUE, centered=True, title_size=16)
small_box(482, 860, 256, 42, "g = 0  →  Direct d", [], fill=WHITE, centered=True, title_size=16)
small_box(482, 913, 256, 34, "d=e=∅  →  Rescue(D)", [], fill=GRAY, centered=True, title_size=14)
small_box(482, 958, 256, 36, "G_safe → G_rel → Canon", [], fill=WHITE, centered=True, title_size=14)

# Step 9 — final answer and selected provenance.
panel(70, 670, 330, 340, "Answer selection and provenance", BLUE, BLUE_D, 9, title_size=20)
small_box(
    93,
    740,
    284,
    72,
    "Selected source",
    ["Evidence / Direct / Rescue"],
    fill=WHITE,
    centered=True,
    body_size=17,
)
small_box(
    93,
    830,
    284,
    92,
    "Final answer  ŷ",
    ["short entity answer", "citation IDs retained"],
    fill=GREEN,
    centered=True,
    body_size=17,
)
small_box(
    93, 940, 284, 48, "Return ŷ + source + audit code", [], fill=WHITE, centered=True, title_size=16
)

# External data-flow arrows.  All are black, single-headed, and labelled.
arrow("M400,170 H460", "Direct d", 430, 148, 100)
arrow("M400,445 H460", "packet x,m", 430, 422, 112)
arrow("M610,280 V330", "if d ≠ ∅, append untrusted d", 714, 307, 236)
arrow("M760,465 H830", "q₀, q₁", 795, 442, 196)
# Route the Step 4 → Step 5 transfer through the empty inter-row gutter;
# the former horizontal connector crossed the R1 text block.
arrow("M1330,575 V630 H1510 V600", "align passage IDs", 1418, 618, 168)
arrow("M1800,600 V670", "verification input", 1870, 642, 142)
arrow("M1400,835 H1330", "record v", 1365, 810, 142)
arrow("M830,835 H760", "checks", 795, 810, 136)
arrow("M460,835 H400", "source", 430, 810, 125)

# Reproducibility record — a dense but subordinate bottom strip.
box(70, 1080, 1850, 130, fill=GRAY, stroke=INK, sw=2.0, rx=10)
txt(90, 1113, "Reproducible decision record — one persisted row per question", size=21, weight=700)
fields = [
    "qid",
    "q₀ text",
    "q₁ text",
    "R₀/R₁ ranks",
    "Top-3 D",
    "raw v",
    "parse status",
    "c₁…c₆",
    "selected source",
    "ŷ",
]
fw = 176
for i, field in enumerate(fields):
    xx = 90 + i * 181
    box(xx, 1136, fw, 48, fill=WHITE, stroke=INK, sw=1.2, rx=4)
    txt(xx + fw / 2, 1167, field, size=15, weight=700, anchor="middle")
arrow("M235,1010 V1080", "persist decision trace", 330, 1055, 156)

add("</svg>")
SVG.write_text("\n".join(parts), encoding="utf-8")
print(SVG)
