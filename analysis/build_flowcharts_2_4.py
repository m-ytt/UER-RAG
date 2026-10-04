#!/usr/bin/env python3
"""Build Figures 2-4 in the approved two-colour academic flowchart style."""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#1F2323"
BLUE = "#E5EDF1"
BLUE_D = "#91A9B5"
GREEN = "#E7ECE3"
GREEN_D = "#9CAD97"
WHITE = "#FFFFFF"
GRAY = "#F5F6F4"


class S:
    def __init__(self, w=2000, h=1160):
        self.w, self.h = w, h
        self.p = [
            f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker></defs>
<rect width="{w}" height="{h}" fill="#FFFFFF"/>'''
        ]

    def add(self, x):
        self.p.append(x)

    def text(self, x, y, value, size=21, weight=400, anchor="start", italic=False, fill=INK):
        self.add(
            f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{weight}" font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}" fill="{fill}">{escape(str(value))}</text>'
        )

    def box(self, x, y, w, h, fill=WHITE, sw=2.0, rx=10):
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>'
        )

    def panel(self, x, y, w, h, title, fill, head, n, title_size=23):
        self.box(x, y, w, h, fill=fill, sw=2.2, rx=13)
        self.add(
            f'<path d="M{x + 13},{y} H{x + w - 13} Q{x + w},{y} {x + w},{y + 13} V{y + 50} H{x} V{y + 13} Q{x},{y} {x + 13},{y} Z" fill="{head}"/>'
        )
        self.add(
            f'<line x1="{x}" y1="{y + 50}" x2="{x + w}" y2="{y + 50}" stroke="{INK}" stroke-width="2.0"/>'
        )
        self.text(x + 17, y + 33, title, size=title_size, weight=700)
        self.add(
            f'<circle cx="{x - 22}" cy="{y + 25}" r="24" fill="{WHITE}" stroke="{INK}" stroke-width="2.2"/>'
        )
        self.text(x - 22, y + 33, n, size=22, weight=700, anchor="middle")

    def small(self, x, y, w, h, title, lines=(), fill=WHITE, ts=19, bs=16, centered=False):
        self.box(x, y, w, h, fill=fill, sw=1.7, rx=7)
        tx = x + w / 2 if centered else x + 12
        an = "middle" if centered else "start"
        self.text(tx, y + 25, title, size=ts, weight=700, anchor=an)
        for i, line in enumerate(lines):
            self.text(tx, y + 49 + i * 22, line, size=bs, anchor=an)

    def arrow(self, path, label=None, lx=None, ly=None, lw=None):
        self.add(
            f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#arrow)"/>'
        )
        if label is not None:
            # Labels sit beside, above, or below their connector in a reserved
            # gutter.  They never erase a segment of the arrow line.
            self.text(lx, ly, label, size=16, anchor="middle")

    def table(self, x, y, widths, row_h, headers, rows, header_fill=BLUE):
        total = sum(widths)
        yy = y
        xx = x
        for j, (h, w) in enumerate(zip(headers, widths)):
            self.add(
                f'<rect x="{xx}" y="{yy}" width="{w}" height="{row_h}" fill="{header_fill}" stroke="{INK}" stroke-width="1.2"/>'
            )
            self.text(xx + w / 2, yy + row_h * 0.67, h, size=14, weight=700, anchor="middle")
            xx += w
        for i, row in enumerate(rows):
            yy = y + (i + 1) * row_h
            xx = x
            for val, w in zip(row, widths):
                self.add(
                    f'<rect x="{xx}" y="{yy}" width="{w}" height="{row_h}" fill="{WHITE if i % 2 == 0 else GRAY}" stroke="{INK}" stroke-width="1.0"/>'
                )
                self.text(xx + w / 2, yy + row_h * 0.67, val, size=13, anchor="middle")
                xx += w
        return total

    def save(self, name):
        self.p.append("</svg>")
        path = OUT / f"{name}.svg"
        path.write_text("\n".join(self.p), encoding="utf-8")
        return path


def figure2():
    s = S()
    # Upper row: observable fields -> query views -> retrieval.
    s.panel(70, 70, 410, 430, "Observable packet and protected answer", BLUE, BLUE_D, 1, 21)
    s.table(
        95,
        145,
        [82, 268],
        46,
        ["field", "normalized value"],
        [
            ["x", "entity question text"],
            ["t", "Louis Renault"],
            ["s", "Louis Renault (jurist)"],
            ["r", "place of birth"],
        ],
    )
    s.small(
        95,
        390,
        350,
        80,
        "Direct answer d = Paris",
        ["stored before retrieval; not trusted as evidence"],
        fill=GREEN,
        bs=15,
    )

    s.panel(550, 70, 410, 430, "Two explicitly different query views", GREEN, GREEN_D, 2, 21)
    s.small(
        575,
        145,
        360,
        115,
        "Answer-free query q₀",
        ["N(x ⊕ t ⊕ s ⊕ r)", "entity sense + target relation", "independent of d"],
        fill=WHITE,
    )
    s.small(
        575,
        285,
        360,
        145,
        "Conditional query q₁",
        [
            "created only when d is non-empty",
            "N(q₀ ⊕ d)",
            "d is tagged as untrusted",
            "q₁ cannot authorize replacement",
        ],
        fill=WHITE,
    )

    s.panel(
        1030, 70, 900, 430, "Shared-corpus retrieval produces two ranked lists", BLUE, BLUE_D, 3, 23
    )
    s.small(
        1060,
        138,
        270,
        82,
        "Wikipedia passage index",
        ["retrieve_k = 50 per query"],
        fill=WHITE,
        centered=True,
    )
    s.small(1370, 138, 245, 82, "Ranking R₀", ["answer-free view"], fill=WHITE, centered=True)
    s.small(
        1650, 138, 245, 82, "Ranking R₁", ["answer-conditioned view"], fill=WHITE, centered=True
    )
    rows0 = [
        ["p1", "1", "jurist + Autun"],
        ["p3", "2", "biography"],
        ["p5", "3", "Autun context"],
        ["p7", "4", "background"],
    ]
    rows1 = [
        ["p2", "1", "Paris cue"],
        ["p1", "2", "jurist + Autun"],
        ["p5", "3", "Autun context"],
        ["p8", "4", "background"],
    ]
    s.table(1345, 250, [55, 55, 185], 44, ["pid", "rank", "role"], rows0)
    s.table(1630, 250, [55, 55, 185], 44, ["pid", "rank", "role"], rows1)
    s.arrow("M1330,179 H1370", "q₀", 1350, 158, 52)
    # q1 is routed below the three boxes, then enters R1 from its lower edge;
    # it no longer runs through the R0 label or body text.
    s.arrow("M1330,198 V240 H1772 V220", "q₁", 1600, 231, 52)

    # Lower row: identity ledger -> RRF -> Top-3 evidence.
    s.panel(1030, 610, 520, 390, "Identity ledger before fusion", GREEN, GREEN_D, 4, 21)
    s.table(
        1055,
        685,
        [82, 90, 90, 105, 105],
        36,
        ["passage", "rank q₀", "rank q₁", "identity", "action"],
        [
            ["p1", "1", "2", "same ID", "merge"],
            ["p2", "—", "1", "unique", "keep"],
            ["p5", "3", "3", "same ID", "merge"],
            ["p3", "2", "—", "unique", "keep"],
            ["p7", "4", "—", "unique", "keep"],
            ["p8", "—", "4", "unique", "keep"],
        ],
        header_fill=GREEN,
    )
    s.text(
        1290,
        974,
        "Duplicate passages never count as independent support.",
        size=15,
        italic=True,
        anchor="middle",
    )

    s.panel(550, 610, 410, 390, "Reciprocal-rank fusion", BLUE, BLUE_D, 5, 22)
    s.small(
        575,
        685,
        360,
        82,
        "Rank-only score",
        ["S_RRF(p)=Σq∈{q₀,q₁} 1/(20+rankq(p))"],
        fill=WHITE,
        centered=True,
        bs=16,
    )
    s.table(
        585,
        790,
        [70, 82, 82, 82],
        36,
        ["p", "q₀ term", "q₁ term", "sum"],
        [
            ["p1", ".0476", ".0455", ".0931"],
            ["p5", ".0435", ".0435", ".0870"],
            ["p2", "0", ".0476", ".0476"],
            ["p3", ".0455", "0", ".0455"],
        ],
    )
    s.text(
        755, 986, "Raw retriever score scales are not mixed.", size=15, italic=True, anchor="middle"
    )

    s.panel(70, 610, 410, 390, "Addressable Top-3 evidence bundle", GREEN, GREEN_D, 6, 20)
    for i, (d, pid, role) in enumerate(
        [
            ("D1", "p1", "shared subject + answer support"),
            ("D2", "p5", "shared answer context"),
            ("D3", "p2", "q₁-only distractor context"),
        ]
    ):
        s.small(95, 690 + i * 88, 360, 67, f"{d} = {pid}", [role], fill=WHITE, bs=15)
    s.small(
        95,
        956,
        360,
        31,
        "Verifier payload:  x + m + d + D1,D2,D3",
        [],
        fill=BLUE,
        centered=True,
        ts=14,
    )

    s.arrow("M480,230 H550", "serialize x,m,d", 515, 207, 145)
    s.arrow("M960,285 H1030", "retrieve q₀,q₁", 995, 262, 118)
    s.arrow("M1480,500 V610", "align passage IDs", 1565, 558, 138)
    s.arrow("M1030,810 H960", "deduplicate", 995, 787, 100)
    s.arrow("M550,810 H480", "retain Top-3", 515, 787, 112)

    s.box(70, 1050, 1860, 70, fill=GRAY, sw=2.0, rx=8)
    s.text(92, 1080, "Saved retrieval trace", size=18, weight=700)
    fields = [
        "q₀ text",
        "q₁ text",
        "R₀ IDs+ranks",
        "R₁ IDs+ranks",
        "dedup map",
        "RRF terms",
        "Top-3 IDs",
        "passage text",
    ]
    for i, f in enumerate(fields):
        x = 285 + i * 200
        s.box(x, 1064, 185, 37, fill=WHITE, sw=1.2, rx=4)
        s.text(x + 92.5, 1089, f, size=13, weight=700, anchor="middle")
    return s.save("Fig02_academic_dual_retrieval")


def figure3():
    s = S()
    s.panel(70, 70, 470, 450, "Verifier input packet", BLUE, BLUE_D, 1, 23)
    s.small(
        95,
        145,
        420,
        72,
        "Protected Direct  d",
        ["available if any evidence check fails"],
        fill=WHITE,
        bs=16,
    )
    for i, (name, role, fill) in enumerate(
        [
            ("D1 · cited", "candidate + subject support", GREEN),
            ("D2 · cited", "additional subject support", GREEN),
            ("D3 · uncited", "context retained; not used for grounding", GRAY),
        ]
    ):
        s.small(95, 238 + i * 82, 420, 65, name, [role], fill=fill, bs=15)

    s.panel(610, 70, 560, 450, "Structured verification", GREEN, GREEN_D, 2, 24)
    s.small(
        635,
        145,
        510,
        84,
        "Verifier instruction",
        ["propose one short entity value · cite only D · emit fixed-schema JSON"],
        fill=WHITE,
        bs=16,
    )
    s.small(
        635,
        252,
        510,
        235,
        "Structured record  v",
        [
            '"candidate": e',
            '"support": high / medium / low / none',
            '"utility": helpful / neutral',
            '"citations": C ⊆ {1,2,3}',
            '"reason": one short rationale',
            "parse failure → evidence rejected",
        ],
        fill=WHITE,
        bs=16,
    )

    s.panel(1240, 70, 690, 450, "Grounding recomputation on cited passages", BLUE, BLUE_D, 3, 22)
    s.small(
        1265,
        145,
        640,
        82,
        "Cited set  C",
        ["only passages named by v enter deterministic grounding"],
        fill=WHITE,
        centered=True,
        bs=16,
    )
    s.table(
        1275,
        255,
        [155, 200, 250],
        42,
        ["field", "observed string", "verified against"],
        [
            ["candidate e", "Autun", "passage P1"],
            ["subject", "Louis Renault (jurist)", "passages P1 and P2"],
            ["direct d", "Paris", "protected comparison only"],
            ["normalization", "N(e) ≠ N(d)", "non-trivial change"],
        ],
    )
    s.text(
        1585,
        495,
        "Uncited passages cannot satisfy c4 or c5.",
        size=15,
        italic=True,
        anchor="middle",
    )

    s.panel(
        1030, 620, 900, 390, "Six independently inspectable binary checks", GREEN, GREEN_D, 4, 23
    )
    checks = [
        ("c1", "e ≠ ∅", "candidate exists"),
        ("c2", "u=helpful", "usefulness"),
        ("c3", "s∈{H,M}", "support strength"),
        ("c4", "ground(e,C)", "answer grounding"),
        ("c5", "ground(subject,C)", "entity grounding"),
        ("c6", "N(e)≠N(d)", "meaningful change"),
    ]
    for i, (c, pred, role) in enumerate(checks):
        col, row = i % 3, i // 3
        x, y = 1060 + col * 280, 700 + row * 115
        s.small(x, y, 250, 90, c, [pred, role], fill=WHITE, centered=True, ts=18, bs=15)

    s.panel(550, 620, 410, 390, "Conjunctive authorization gate", BLUE, BLUE_D, 5, 21)
    s.small(
        575, 700, 360, 82, "Gate value", ["g(x,d,e,D,m)=∏ⱼ₌₁⁶ cⱼ"], fill=WHITE, centered=True, bs=19
    )
    s.small(
        575,
        808,
        360,
        60,
        "all six checks = 1  →  authorize e",
        [],
        fill=GREEN,
        centered=True,
        ts=16,
    )
    s.small(575, 888, 360, 60, "any check = 0  →  retain d", [], fill=WHITE, centered=True, ts=16)

    s.panel(70, 620, 410, 390, "Source policy and rejection record", GREEN, GREEN_D, 6, 20)
    s.table(
        95,
        700,
        [112, 150, 112],
        41,
        ["code", "trigger", "source"],
        [
            ["E_PARSE", "invalid JSON", "Direct"],
            ["E_SUPPORT", "c2=0 or c3=0", "Direct"],
            ["E_GROUND", "c4=0 or c5=0", "Direct"],
            ["E_SAME", "c6=0", "Direct"],
            ["E_RESCUE", "d=e=∅", "Rescue"],
        ],
        header_fill=GREEN,
    )
    s.small(
        95,
        958,
        360,
        35,
        "Post-audit; persist source, code, and answer",
        [],
        fill=WHITE,
        centered=True,
        ts=14,
    )

    s.arrow("M540,280 H610", "submit x,m,d,D", 575, 257, 132)
    s.arrow("M1170,280 H1240", "emit v,C", 1205, 257, 100)
    s.arrow("M1585,520 V620", "candidate + cited C", 1700, 574, 145)
    s.arrow("M1030,815 H960", "checks", 995, 792, 82)
    s.arrow("M550,815 H480", "decision", 515, 792, 132)

    s.box(70, 1060, 1860, 65, fill=GRAY, sw=2.0, rx=8)
    s.text(92, 1091, "Auditable record", size=18, weight=700)
    fields = [
        "qid",
        "Top-3 D",
        "raw v",
        "parse status",
        "c₁…c₆",
        "failed check",
        "selected source",
        "final answer",
    ]
    for i, f in enumerate(fields):
        x = 285 + i * 200
        s.box(x, 1074, 185, 37, fill=WHITE, sw=1.2, rx=4)
        s.text(x + 92.5, 1099, f, size=13, weight=700, anchor="middle")
    return s.save("Fig03_academic_risk_audit")


def figure4():
    s = S(h=1180)
    s.panel(70, 70, 420, 350, "Archived evaluation item", BLUE, BLUE_D, 1, 23)
    s.small(
        95, 145, 370, 82, "Question", ["In what city was Louis Renault born?"], fill=WHITE, bs=16
    )
    s.table(
        95,
        250,
        [120, 250],
        43,
        ["field", "resolved value"],
        [
            ["title", "Louis Renault"],
            ["subject", "Louis Renault (jurist)"],
            ["relation", "place of birth"],
        ],
    )

    s.panel(560, 70, 360, 350, "Protected direct answer", GREEN, GREEN_D, 2, 22)
    s.small(
        585,
        145,
        310,
        105,
        "d = Paris",
        ["EM = 0 · Token F1 = 0", "saved before retrieval", "remains available as fallback"],
        fill=WHITE,
        centered=True,
        bs=16,
    )
    s.small(
        585,
        278,
        310,
        88,
        "Intervention rule",
        ["retrieval proposes a replacement", "it cannot overwrite d by default"],
        fill=BLUE,
        centered=True,
        bs=15,
    )

    s.panel(990, 70, 940, 350, "Query construction and entity disambiguation", BLUE, BLUE_D, 3, 23)
    s.small(
        1015,
        145,
        265,
        103,
        "Resolved subject",
        ["Louis Renault", "→ jurist sense"],
        fill=WHITE,
        centered=True,
    )
    s.small(
        1310,
        145,
        280,
        103,
        "Answer-free q₀",
        ["question + jurist", "+ place of birth"],
        fill=WHITE,
        centered=True,
    )
    s.small(
        1620,
        145,
        285,
        103,
        "Answer-conditioned q₁",
        ["q₀ + Paris", "Paris remains untrusted"],
        fill=WHITE,
        centered=True,
    )
    s.table(
        1015,
        282,
        [95, 520, 245],
        43,
        ["view", "serialized retrieval text", "constraint"],
        [
            ["q₀", "Louis Renault (jurist) | born | place of birth", "answer-free"],
            ["q₁", "q₀ | Paris", "untrusted cue only"],
        ],
    )
    s.arrow("M1280,197 H1310", "build q₀", 1295, 177, 70)
    s.arrow("M1590,197 H1620", "append d", 1605, 177, 78)

    s.panel(70, 520, 1030, 440, "Retrieval, rank fusion, and cited evidence", GREEN, GREEN_D, 4, 23)
    s.small(95, 595, 220, 72, "Wikipedia index", ["top-50 per view"], fill=WHITE, centered=True)
    s.table(
        350,
        635,
        [60, 60, 150],
        34,
        ["R₀", "rank", "role"],
        [["p1", "1", "jurist"], ["p3", "2", "bio"], ["p5", "3", "Autun"]],
    )
    s.table(
        655,
        635,
        [60, 60, 150],
        34,
        ["R₁", "rank", "role"],
        [["p2", "1", "Paris"], ["p1", "2", "jurist"], ["p5", "3", "Autun"]],
    )
    s.small(
        350,
        795,
        270,
        90,
        "RRF ranking",
        ["p1 → 1", "p5 → 2", "p2 → 3"],
        fill=WHITE,
        centered=True,
        bs=14,
    )
    s.small(
        655,
        795,
        270,
        90,
        "Top-3 bundle D",
        ["D1=p1 · D2=p5 · D3=p2", "citation IDs remain stable"],
        fill=BLUE,
        centered=True,
        bs=13,
    )
    s.small(
        95,
        720,
        220,
        165,
        "Selected evidence role",
        [
            "P1: answer + subject",
            "P2: subject support",
            "P3: uncited context",
            "candidate e = Autun",
            "C = {1,2}",
        ],
        fill=WHITE,
        bs=15,
    )
    s.small(
        95,
        906,
        830,
        35,
        "P1: “Louis Renault (jurist) ... was born at Autun.”",
        [],
        fill=WHITE,
        centered=True,
        ts=15,
    )
    s.arrow("M315,662 H350", "R₀", 332, 639, 48)
    # The R1 branch uses the clear band above both tables instead of crossing R0.
    s.arrow("M315,690 V605 H790 V635", "R₁", 625, 598, 48)
    s.arrow("M620,840 H655", "fuse", 637, 817, 52)

    s.panel(
        1170, 520, 760, 440, "Structured verification and deterministic audit", BLUE, BLUE_D, 5, 22
    )
    s.small(
        1195,
        595,
        300,
        255,
        "Structured record v",
        [
            "candidate: Autun",
            "support: high",
            "utility: helpful",
            "citations: [1,2]",
            "reason: subject and relation agree",
        ],
        fill=WHITE,
        bs=16,
    )
    s.table(
        1530,
        595,
        [70, 185, 95],
        38,
        ["check", "observed", "result"],
        [
            ["c1", "e non-empty", "1"],
            ["c2", "helpful", "1"],
            ["c3", "high support", "1"],
            ["c4", "Autun in P1", "1"],
            ["c5", "subject in P1,P2", "1"],
            ["c6", "Autun ≠ Paris", "1"],
        ],
        header_fill=BLUE,
    )
    s.small(
        1195,
        880,
        685,
        45,
        "g = c1·c2·c3·c4·c5·c6 = 1  →  Evidence authorized",
        [],
        fill=GREEN,
        centered=True,
        ts=16,
    )
    s.arrow("M1100,745 H1170", "submit x,m,d,D", 1135, 722, 132)

    s.panel(
        70, 1020, 1860, 105, "Authorized replacement and persisted outcome", GREEN, GREEN_D, 6, 23
    )
    s.small(
        95, 1082, 250, 30, "Direct: Paris  (not selected)", [], fill=WHITE, centered=True, ts=14
    )
    s.small(385, 1082, 250, 30, "Evidence: Autun  (g=1)", [], fill=BLUE, centered=True, ts=14)
    s.small(
        675, 1082, 250, 30, "Final ŷ: Autun  (EM=1; F1=1)", [], fill=WHITE, centered=True, ts=14
    )
    fields = [
        "q₀/q₁ saved",
        "R₀/R₁ saved",
        "Top-3 D saved",
        "raw v saved",
        "checks 111111",
        "source Evidence",
    ]
    for i, f in enumerate(fields):
        x = 970 + i * 153
        s.box(x, 1082, 140, 30, fill=WHITE, sw=1.1, rx=3)
        s.text(x + 70, 1103, f, size=11, weight=700, anchor="middle")
    return s.save("Fig04_academic_worked_case")


if __name__ == "__main__":
    for fn in (figure2, figure3, figure4):
        print(fn())
