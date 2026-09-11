#!/usr/bin/env python3
"""Build the first-round UER-RAG journal figure review package.

The visual system is intentionally compact and paper-like: muted cream panels,
thin charcoal rules, teal/sage structure, restrained coral emphasis, no large
in-plot titles, and multiple related analyses grouped into composite figures.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

DATA_ROOT = ROOT / "data"
if not DATA_ROOT.exists():
    DATA_ROOT = (
        ROOT.parent
        / "recovered"
        / "unpacked"
        / "adaptive_rag_paper_artifacts"
        / "data"
    )


# Reference-paper-inspired visual grammar. The palette is newly constructed;
# it borrows only the high-level idea of muted teal/coral on cream.
INK = "#273331"
GRID = "#D8DDD7"
CREAM = "#F4F3E7"
CREAM_2 = "#FAF9F3"
SAGE = "#DDE7D8"
SAGE_DARK = "#8FA690"
TEAL = "#187C6B"
TEAL_2 = "#5AA79C"
TEAL_PALE = "#C9E3DE"
BLUE = "#527D94"
BLUE_PALE = "#DCE8ED"
CORAL = "#EF8065"
CORAL_DARK = "#C95642"
CORAL_PALE = "#F8D7CE"
AMBER = "#D5A33E"
AMBER_PALE = "#F2E6B9"
GRAY = "#87928F"
GRAY_PALE = "#E6E8E4"
GREEN = "#2F9565"
GREEN_PALE = "#D7EBDD"


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Nimbus Sans", "Arial", "DejaVu Sans"],
        "font.size": 7.2,
        "axes.labelsize": 7.0,
        "axes.titlesize": 7.8,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "axes.edgecolor": INK,
        "axes.linewidth": 0.65,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "grid.color": GRID,
        "grid.linewidth": 0.45,
        "grid.alpha": 0.65,
        "legend.fontsize": 6.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "none",
    }
)


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save the same figure as editable SVG, vector PDF and 400-dpi PNG."""
    for ext in ("svg", "pdf"):
        fig.savefig(OUT / f"{stem}.{ext}", bbox_inches="tight", pad_inches=0.035)
    fig.savefig(
        OUT / f"{stem}.png",
        dpi=400,
        bbox_inches="tight",
        pad_inches=0.035,
    )
    plt.close(fig)


def rounded_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str = CREAM_2,
    edgecolor: str = INK,
    fontsize: float = 6.4,
    linewidth: float = 0.75,
    radius: float = 0.012,
    weight: str = "normal",
    align: str = "center",
    textcolor: str = INK,
    zorder: int = 3,
) -> patches.FancyBboxPatch:
    x, y = xy
    box = patches.FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0.006,rounding_size={radius}",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
        zorder=zorder,
    )
    ax.add_patch(box)
    tx = x + (width / 2 if align == "center" else 0.014)
    ax.text(
        tx,
        y + height / 2,
        text,
        ha=align,
        va="center",
        fontsize=fontsize,
        color=textcolor,
        weight=weight,
        linespacing=1.16,
        zorder=zorder + 1,
    )
    return box


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = INK,
    lw: float = 0.85,
    connectionstyle: str = "arc3,rad=0",
    style: str = "-|>",
    zorder: int = 2,
) -> None:
    ax.add_patch(
        patches.FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=8,
            linewidth=lw,
            color=color,
            connectionstyle=connectionstyle,
            shrinkA=0,
            shrinkB=0,
            zorder=zorder,
        )
    )


def panel_label(ax: plt.Axes, label: str, subtitle: str | None = None) -> None:
    ax.text(
        0.0,
        1.035,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        weight="bold",
        fontsize=7.6,
        color=INK,
    )
    if subtitle:
        ax.text(
            0.055,
            1.035,
            subtitle,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=7.2,
            color=INK,
        )


def clean_axes(ax: plt.Axes, *, grid: str | None = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=2.5, width=0.55, color=INK)
    if grid:
        ax.grid(True, axis=grid, zorder=0)


def _figure_1_flowchart_deprecated() -> None:
    fig = plt.figure(figsize=(7.08, 4.78))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Panel (a): compact method overview.
    panel_a = patches.FancyBboxPatch(
        (0.014, 0.515),
        0.972,
        0.465,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        linewidth=0.65,
        edgecolor="#BEC8BE",
        facecolor=CREAM,
    )
    ax.add_patch(panel_a)
    ax.text(0.028, 0.952, "(a)", weight="bold", fontsize=8.0, color=INK)
    ax.text(
        0.073,
        0.952,
        "Dataset-name-independent, two-call answer replacement",
        fontsize=7.4,
        weight="bold",
        color=INK,
    )

    y_top = 0.765
    h = 0.115
    rounded_box(
        ax,
        (0.035, y_top),
        0.112,
        h,
        "Question  x\n+ optional entity fields",
        facecolor=BLUE_PALE,
        edgecolor=BLUE,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.177, y_top),
        0.112,
        h,
        "Call 1\nDirect answer  d",
        facecolor="#E9EEF0",
        edgecolor=GRAY,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.320, y_top),
        0.170,
        h,
        "Field-adaptive query pair\n$q_0$: x + entity + relation\n$q_1$: $q_0$ + untrusted d",
        facecolor=SAGE,
        edgecolor=SAGE_DARK,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.525, y_top),
        0.118,
        h,
        "Retrieve + RRF\nTop-3 passages",
        facecolor=TEAL_PALE,
        edgecolor=TEAL,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.679, y_top),
        0.142,
        h,
        "Call 2\nStructured verifier\n(e, support, utility, citations)",
        facecolor=AMBER_PALE,
        edgecolor=AMBER,
        fontsize=6.1,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.856, y_top),
        0.108,
        h,
        "Six-check\nrisk gate",
        facecolor=CORAL_PALE,
        edgecolor=CORAL_DARK,
        weight="bold",
    )

    xs = [(0.147, 0.822), (0.289, 0.822), (0.490, 0.822), (0.643, 0.822), (0.821, 0.822)]
    xe = [(0.177, 0.822), (0.320, 0.822), (0.525, 0.822), (0.679, 0.822), (0.856, 0.822)]
    for s, e in zip(xs, xe):
        arrow(ax, s, e, color=INK)

    ax.text(
        0.405,
        0.743,
        "branch is selected from observable fields - never from the dataset name",
        ha="center",
        va="center",
        fontsize=5.8,
        color="#56625F",
        style="italic",
    )

    # Outputs and the conservative fallback logic.
    rounded_box(
        ax,
        (0.395, 0.565),
        0.154,
        0.095,
        "Direct fallback\nkeep d when any check fails",
        facecolor="#E7EDF0",
        edgecolor=BLUE,
        fontsize=6.1,
    )
    rounded_box(
        ax,
        (0.586, 0.565),
        0.154,
        0.095,
        "Evidence answer\nreplace d only if all checks pass",
        facecolor=GREEN_PALE,
        edgecolor=GREEN,
        fontsize=6.1,
    )
    rounded_box(
        ax,
        (0.777, 0.565),
        0.154,
        0.095,
        "Conditional Rescue\nonly when d and e are empty",
        facecolor=CORAL_PALE,
        edgecolor=CORAL_DARK,
        fontsize=6.1,
    )
    arrow(ax, (0.910, y_top), (0.472, 0.660), color=BLUE, connectionstyle="arc3,rad=0.16")
    arrow(ax, (0.910, y_top), (0.663, 0.660), color=GREEN, connectionstyle="arc3,rad=0.06")
    arrow(ax, (0.910, y_top), (0.854, 0.660), color=CORAL_DARK, connectionstyle="arc3,rad=-0.16")
    ax.text(0.515, 0.681, "fail", fontsize=5.7, color=BLUE, ha="center")
    ax.text(0.688, 0.681, "pass", fontsize=5.7, color=GREEN, ha="center")
    ax.text(0.865, 0.681, "both empty", fontsize=5.7, color=CORAL_DARK, ha="center")

    # Panel (b): real PopQA example from the archived run.
    panel_b = patches.FancyBboxPatch(
        (0.014, 0.018),
        0.972,
        0.470,
        boxstyle="round,pad=0.008,rounding_size=0.018",
        linewidth=0.65,
        edgecolor="#BEC8BE",
        facecolor=CREAM_2,
    )
    ax.add_patch(panel_b)
    ax.text(0.028, 0.460, "(b)", weight="bold", fontsize=8.0, color=INK)
    ax.text(
        0.073,
        0.460,
        "Worked PopQA case (qid 1788652): a wrong Direct answer is repaired",
        fontsize=7.4,
        weight="bold",
        color=INK,
    )

    rounded_box(
        ax,
        (0.035, 0.285),
        0.210,
        0.118,
        "Question\nIn what city was Louis Renault born?\n\nMetadata\nLouis Renault (jurist) · place of birth",
        facecolor="#EFF4F5",
        edgecolor=BLUE,
        fontsize=6.3,
        align="left",
        weight="bold",
    )
    rounded_box(
        ax,
        (0.035, 0.100),
        0.210,
        0.105,
        "Direct answer (untrusted clue)\nParis   ×\nEM: 0    F1: 0",
        facecolor=CORAL_PALE,
        edgecolor=CORAL_DARK,
        fontsize=6.6,
        align="left",
        weight="bold",
    )

    rounded_box(
        ax,
        (0.285, 0.278),
        0.225,
        0.125,
        "Dual retrieval\n$q_0$ = question + entity + relation\n$q_1$ = $q_0$ + ‘Paris’\nRRF fuses both rankings",
        facecolor=SAGE,
        edgecolor=SAGE_DARK,
        fontsize=6.4,
        align="left",
        weight="bold",
    )
    rounded_box(
        ax,
        (0.285, 0.085),
        0.225,
        0.125,
        "Top passage\n‘Louis Renault (jurist) ...\nRenault was born at Autun.’",
        facecolor=TEAL_PALE,
        edgecolor=TEAL,
        fontsize=6.6,
        align="left",
        weight="bold",
    )

    rounded_box(
        ax,
        (0.552, 0.248),
        0.185,
        0.155,
        "Verifier record\nevidence_answer = Autun\nsupport = high\nutility = helpful\ncited docs = {1, 2}",
        facecolor=AMBER_PALE,
        edgecolor=AMBER,
        fontsize=6.35,
        align="left",
        weight="bold",
    )
    rounded_box(
        ax,
        (0.552, 0.085),
        0.185,
        0.095,
        "Audit result\n6 / 6 checks pass",
        facecolor=GREEN_PALE,
        edgecolor=GREEN,
        fontsize=6.6,
        align="left",
        weight="bold",
    )

    rounded_box(
        ax,
        (0.782, 0.170),
        0.168,
        0.155,
        "Final answer\nAutun   [PASS]\n\nEM: 0 → 1\nF1: 0 → 1",
        facecolor=GREEN_PALE,
        edgecolor=GREEN,
        fontsize=7.2,
        weight="bold",
    )

    arrow(ax, (0.245, 0.344), (0.285, 0.344), color=INK)
    arrow(ax, (0.140, 0.285), (0.140, 0.205), color=INK)
    arrow(ax, (0.245, 0.152), (0.285, 0.300), color=CORAL_DARK, connectionstyle="arc3,rad=-0.23")
    arrow(ax, (0.397, 0.278), (0.397, 0.210), color=TEAL)
    arrow(ax, (0.510, 0.147), (0.552, 0.287), color=TEAL, connectionstyle="arc3,rad=-0.22")
    arrow(ax, (0.644, 0.248), (0.644, 0.180), color=GREEN)
    arrow(ax, (0.737, 0.132), (0.782, 0.220), color=GREEN, connectionstyle="arc3,rad=-0.18")

    save_figure(fig, "Fig01_overview_and_worked_example")


def figure_1_overview_and_example() -> None:
    """Reference-style system schematic with an embedded real example.

    This is deliberately not a conventional left-to-right flowchart. It uses a
    coupled upper system band and two lower mechanism panels, mirroring the
    information density and visual hierarchy of the supplied reference figure.
    """

    fig = plt.figure(figsize=(7.08, 4.33))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    bg = "#F1F2DF"
    panel = "#F8F7ED"
    lower_panel = "#E4E6C9"
    line = "#263330"
    muted = "#63716D"

    ax.add_patch(
        patches.FancyBboxPatch(
            (0.012, 0.020),
            0.976,
            0.955,
            boxstyle="round,pad=0.006,rounding_size=0.020",
            facecolor=bg,
            edgecolor="#C9CEBC",
            linewidth=0.7,
            zorder=0,
        )
    )

    def card(x, y, w, h, label, fc, ec=line, fs=6.0, weight="bold", ls=1.1, z=4):
        p = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.004,rounding_size=0.008",
            facecolor=fc,
            edgecolor=ec,
            linewidth=0.75,
            zorder=z,
        )
        ax.add_patch(p)
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=fs,
            color=line,
            weight=weight,
            linespacing=ls,
            zorder=z + 1,
        )
        return p

    def tag(x, y, w, text, fc="#FFFFFF", ec=line, color=line, fs=4.9, z=6):
        p = patches.FancyBboxPatch(
            (x, y),
            w,
            0.032,
            boxstyle="round,pad=0.002,rounding_size=0.006",
            facecolor=fc,
            edgecolor=ec,
            linewidth=0.55,
            zorder=z,
        )
        ax.add_patch(p)
        ax.text(x + w / 2, y + 0.016, text, ha="center", va="center", fontsize=fs, color=color, zorder=z + 1)
        return p

    def line_arrow(points, color=line, lw=0.8, dashed=False, z=2):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=(0, (4, 2)) if dashed else "-", zorder=z)
        arrow(
            ax,
            points[-2],
            points[-1],
            color=color,
            lw=lw,
            style="-|>",
            zorder=z + 1,
        )

    def draw_chip(x, y, size, label):
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, y),
                size,
                size,
                boxstyle="round,pad=0.003,rounding_size=0.006",
                facecolor="#D7E3E8",
                edgecolor=BLUE,
                linewidth=0.75,
                zorder=5,
            )
        )
        # Chip pins and a small neural lattice.
        for k in range(4):
            t = (k + 0.65) / 4.8
            ax.plot([x - 0.006, x], [y + size * t, y + size * t], color=BLUE, lw=0.6, zorder=4)
            ax.plot([x + size, x + size + 0.006], [y + size * t, y + size * t], color=BLUE, lw=0.6, zorder=4)
        pts = [
            (x + size * 0.28, y + size * 0.30),
            (x + size * 0.72, y + size * 0.30),
            (x + size * 0.50, y + size * 0.55),
            (x + size * 0.28, y + size * 0.76),
            (x + size * 0.72, y + size * 0.76),
        ]
        for a, b in [(0, 2), (1, 2), (2, 3), (2, 4), (0, 1)]:
            ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color=muted, lw=0.45, zorder=6)
        for px, py in pts:
            ax.add_patch(patches.Circle((px, py), size * 0.055, facecolor=CORAL, edgecolor=line, linewidth=0.35, zorder=7))
        ax.text(x + size / 2, y - 0.017, label, ha="center", va="top", fontsize=5.1, weight="bold", color=line)

    def draw_database(x, y, w, h):
        ax.add_patch(patches.Rectangle((x, y + h * 0.16), w, h * 0.67, facecolor="#161B1A", edgecolor="#161B1A", zorder=5))
        ax.add_patch(patches.Ellipse((x + w / 2, y + h * 0.83), w, h * 0.27, facecolor="#252C2A", edgecolor="#111514", linewidth=0.55, zorder=6))
        ax.add_patch(patches.Ellipse((x + w / 2, y + h * 0.50), w, h * 0.23, facecolor="none", edgecolor="white", linewidth=0.45, alpha=0.8, zorder=6))
        ax.add_patch(patches.Ellipse((x + w / 2, y + h * 0.17), w, h * 0.27, facecolor="#111514", edgecolor="#111514", zorder=6))
        ax.text(x + w / 2, y - 0.018, "Wikipedia index", ha="center", va="top", fontsize=5.0, weight="bold", color=line)

    def draw_rank_panel(x, y, w, h, title, accent, labels):
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.004,rounding_size=0.007",
                facecolor="#F8F7E9",
                edgecolor=line,
                linewidth=0.65,
                linestyle=(0, (4, 2)),
                zorder=4,
            )
        )
        ax.text(x + w / 2, y + h + 0.014, title, ha="center", va="bottom", fontsize=5.8, weight="bold", color=line)
        # Small subject-relation graph.
        nodes = [
            (x + w * 0.22, y + h * 0.64),
            (x + w * 0.47, y + h * 0.78),
            (x + w * 0.70, y + h * 0.61),
            (x + w * 0.47, y + h * 0.45),
        ]
        for a, b in [(0, 1), (1, 2), (0, 3), (2, 3)]:
            ax.plot([nodes[a][0], nodes[b][0]], [nodes[a][1], nodes[b][1]], color=muted, lw=0.5, zorder=5)
        for j, (nx, ny) in enumerate(nodes):
            ax.add_patch(patches.Circle((nx, ny), w * 0.040, facecolor=accent if j == 3 else "#A4AAA4", edgecolor=line, linewidth=0.4, zorder=6))
        # Rank vector.
        for j, lab in enumerate(labels):
            bx = x + w * (0.12 + j * 0.20)
            bh = h * (0.08 + (4 - j) * 0.018)
            ax.add_patch(patches.Rectangle((bx, y + h * 0.12), w * 0.13, bh, facecolor=mpl.colors.to_rgba(accent, 0.35 + 0.12 * (3 - j)), edgecolor=accent, linewidth=0.35, zorder=5))
            ax.text(bx + w * 0.065, y + h * 0.08, lab, ha="center", va="top", fontsize=4.0, color=line, zorder=7)

    def draw_document(x, y, w, h, label, accent, rank):
        # Slightly slanted paper with folded corner.
        poly = patches.Polygon(
            [(x, y), (x + w, y), (x + w, y + h * 0.82), (x + w * 0.79, y + h), (x, y + h)],
            closed=True,
            facecolor=mpl.colors.to_rgba(accent, 0.22),
            edgecolor=accent,
            linewidth=0.65,
            zorder=6,
        )
        ax.add_patch(poly)
        ax.plot([x + w * 0.79, x + w * 0.79, x + w], [y + h, y + h * 0.82, y + h * 0.82], color=accent, lw=0.45, zorder=7)
        ax.text(x + w * 0.12, y + h * 0.80, label, fontsize=5.0, weight="bold", color=line, zorder=8)
        for j, frac in enumerate([0.68, 0.55, 0.42, 0.29]):
            ax.plot([x + w * 0.12, x + w * frac], [y + h * (0.61 - j * 0.13)] * 2, color=muted, lw=0.55, zorder=8)
        tag(x + w * 0.55, y + h * 0.05, w * 0.32, f"#{rank}", fc="#FFFFFF", ec=accent, color=accent, fs=4.4, z=9)

    # ------------------------------------------------------------------
    # Upper coupled system band.
    # ------------------------------------------------------------------
    ax.text(0.036, 0.938, "Question and observable fields", fontsize=6.7, weight="bold", color=line)
    card(0.035, 0.835, 0.102, 0.062, "<QUESTION>", "#FFF9E8", CORAL_DARK, fs=5.4)
    draw_chip(0.058, 0.724, 0.054, "Call 1: Direct")
    card(0.035, 0.625, 0.102, 0.060, "Field adapter", "#DCE7EC", BLUE, fs=5.5)
    line_arrow([(0.086, 0.835), (0.086, 0.782)], color=line, lw=0.75)
    line_arrow([(0.137, 0.866), (0.146, 0.866), (0.146, 0.655), (0.137, 0.655)], color=line, lw=0.75)
    ax.text(0.086, 0.604, "observable fields\nnot dataset name", ha="center", va="top", fontsize=4.35, color=muted, style="italic", linespacing=1.05)

    # Two query streams use token capsules rather than flowchart boxes.
    ax.text(0.168, 0.906, r"$q_0$  answer-free", fontsize=6.0, weight="bold", color=TEAL)
    ax.text(0.168, 0.716, r"$q_1$  answer-conditioned", fontsize=6.0, weight="bold", color=CORAL_DARK)
    ax.add_patch(patches.FancyBboxPatch((0.158, 0.755), 0.185, 0.132, boxstyle="round,pad=0.004,rounding_size=0.009", facecolor="#DDE8DA", edgecolor=SAGE_DARK, linewidth=0.65, zorder=3))
    ax.add_patch(patches.FancyBboxPatch((0.158, 0.565), 0.185, 0.132, boxstyle="round,pad=0.004,rounding_size=0.009", facecolor="#F4D6CB", edgecolor=CORAL_DARK, linewidth=0.65, zorder=3))
    for x, label, fc, ec in [
        (0.169, "x", "#FFFFFF", TEAL),
        (0.211, "entity", "#FFFFFF", TEAL),
        (0.270, "relation", "#FFFFFF", TEAL),
    ]:
        tag(x, 0.800, 0.035 if label == "x" else 0.052, label, fc=fc, ec=ec, color=line, fs=4.6)
    for x, label, width in [(0.169, "x", 0.035), (0.211, "entity", 0.052), (0.270, "relation", 0.052), (0.306, "d", 0.025)]:
        # Move the last two capsules slightly to keep the row compact.
        if label == "relation":
            x = 0.263
        if label == "d":
            x = 0.318
        tag(x, 0.610, width, label, fc="#FFFFFF", ec=CORAL_DARK if label == "d" else TEAL, color=CORAL_DARK if label == "d" else line, fs=4.6)
    ax.text(0.249, 0.767, r"$q_0=\mathcal{N}(x\oplus t\oplus s\oplus r)$", ha="center", fontsize=5.4, color=line)
    ax.text(0.249, 0.577, r"$q_1=\mathcal{N}(q_0\oplus d)$", ha="center", fontsize=5.4, color=line)
    line_arrow([(0.137, 0.655), (0.158, 0.815)], color=TEAL, lw=0.75)
    line_arrow([(0.112, 0.748), (0.158, 0.635)], color=CORAL_DARK, lw=0.75)

    draw_database(0.367, 0.650, 0.054, 0.120)
    line_arrow([(0.343, 0.815), (0.376, 0.760)], color=TEAL, lw=0.75)
    line_arrow([(0.343, 0.635), (0.376, 0.650)], color=CORAL_DARK, lw=0.75)

    draw_rank_panel(0.455, 0.755, 0.135, 0.137, r"ranking $R_0$", TEAL_2, ["p1", "p3", "p5", "p7"])
    draw_rank_panel(0.625, 0.755, 0.135, 0.137, r"ranking $R_1$", CORAL, ["p2", "p1", "p5", "p8"])
    line_arrow([(0.421, 0.715), (0.455, 0.815)], color=TEAL, lw=0.7)
    line_arrow([(0.421, 0.690), (0.625, 0.815)], color=CORAL_DARK, lw=0.7)

    # Thick shared fusion arrow, a visual anchor similar to the reference.
    ax.add_patch(
        patches.FancyArrow(
            0.440,
            0.675,
            0.355,
            0,
            width=0.045,
            head_width=0.095,
            head_length=0.045,
            length_includes_head=True,
            facecolor="#4D8274",
            edgecolor="#4D8274",
            zorder=2,
        )
    )
    tag(0.485, 0.660, 0.066, r"$R_0$", fc="#F8F7ED", ec=line, fs=5.0, z=7)
    tag(0.605, 0.660, 0.066, r"$R_1$", fc="#F8F7ED", ec=line, fs=5.0, z=7)
    tag(0.704, 0.660, 0.067, "RRF", fc="#F8F7ED", ec=line, fs=5.0, z=7)
    ax.text(0.615, 0.626, r"$S_{\mathrm{RRF}}(p)=\sum_q(20+\mathrm{rank}_q(p))^{-1}$", ha="center", fontsize=5.2, color=line)

    ax.text(0.815, 0.912, "Top-3 evidence set", fontsize=6.0, weight="bold", color=line)
    draw_document(0.805, 0.700, 0.065, 0.170, "p1", TEAL, 1)
    draw_document(0.858, 0.700, 0.065, 0.170, "p2", BLUE, 2)
    draw_document(0.911, 0.700, 0.065, 0.170, "p3", AMBER, 3)
    ax.text(0.890, 0.650, r"$D_3=\{p_1,p_2,p_3\}$", ha="center", fontsize=5.7, weight="bold", color=line)

    # ------------------------------------------------------------------
    # Lower-left: worked evidence graph, echoing the reference AMR panel.
    # ------------------------------------------------------------------
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.030, 0.067),
            0.445,
            0.445,
            boxstyle="round,pad=0.005,rounding_size=0.006",
            facecolor=panel,
            edgecolor=line,
            linewidth=0.7,
            linestyle=(0, (5, 3)),
            zorder=1,
        )
    )
    ax.text(0.044, 0.485, "Worked evidence graph - PopQA qid 1788652", fontsize=6.4, weight="bold", color=line)

    card(0.050, 0.382, 0.145, 0.058, "In what city was\nLouis Renault born?", "#FFFFFF", BLUE, fs=5.2)
    card(0.222, 0.370, 0.112, 0.075, "Louis Renault\n(jurist)", "#DDE8EC", BLUE, fs=5.3)
    tag(0.337, 0.309, 0.096, "place of birth", fc="#FFF7DF", ec=AMBER, color=line, fs=4.7)
    card(0.350, 0.215, 0.078, 0.058, "Autun", "#D7EBDD", GREEN, fs=6.0)
    card(0.222, 0.225, 0.078, 0.052, "Paris", "#F8D7CE", CORAL_DARK, fs=5.6)
    ax.text(0.261, 0.290, "Direct d", ha="center", fontsize=4.6, color=CORAL_DARK, weight="bold")

    line_arrow([(0.195, 0.411), (0.222, 0.408)], color=line, lw=0.75)
    line_arrow([(0.334, 0.395), (0.385, 0.341), (0.389, 0.273)], color=GREEN, lw=1.0)
    ax.plot([0.300, 0.335], [0.251, 0.333], color=CORAL_DARK, lw=0.8, ls=(0, (4, 2)), zorder=3)
    ax.text(0.308, 0.305, "untrusted", fontsize=4.3, color=CORAL_DARK, rotation=64)

    # Supporting documents as graph leaves.
    card(0.055, 0.220, 0.055, 0.050, "p1", "#C9E3DE", TEAL, fs=5.2)
    card(0.125, 0.220, 0.055, 0.050, "p2", "#DCE8ED", BLUE, fs=5.2)
    line_arrow([(0.110, 0.245), (0.185, 0.320), (0.337, 0.325)], color=TEAL, lw=0.65)
    line_arrow([(0.180, 0.245), (0.195, 0.190), (0.330, 0.190), (0.350, 0.236)], color=BLUE, lw=0.65)
    ax.text(0.122, 0.302, "subject + relation support", fontsize=4.35, color=muted)

    ax.add_patch(
        patches.FancyBboxPatch(
            (0.048, 0.095),
            0.405,
            0.078,
            boxstyle="round,pad=0.004,rounding_size=0.006",
            facecolor="#EEF1E7",
            edgecolor="#A7B0A5",
            linewidth=0.5,
            zorder=3,
        )
    )
    ax.text(0.058, 0.143, "Retrieved statement", fontsize=4.7, weight="bold", color=line)
    ax.text(0.058, 0.114, "‘Louis Renault (jurist) ... Renault was born at Autun.’", fontsize=5.2, color=line, style="italic")

    # ------------------------------------------------------------------
    # Lower-right: structured verifier and layered six-check audit.
    # ------------------------------------------------------------------
    ax.add_patch(
        patches.FancyBboxPatch(
            (0.490, 0.067),
            0.478,
            0.445,
            boxstyle="round,pad=0.005,rounding_size=0.008",
            facecolor=lower_panel,
            edgecolor="#C7C9A9",
            linewidth=0.7,
            zorder=1,
        )
    )
    ax.text(0.506, 0.485, "Structured verification and six-check risk audit", fontsize=6.4, weight="bold", color=line)

    # Two model views, analogous to graph/vector encoders in the reference.
    card(0.512, 0.342, 0.105, 0.074, "Call 2\nVerifier", "#F4C39C", CORAL, fs=5.5)
    card(0.512, 0.216, 0.105, 0.074, "String + graph\ngrounding", "#BFD3D5", BLUE, fs=5.3)
    ax.text(0.564, 0.306, r"$v=(e,s,u,C,\rho)$", ha="center", fontsize=5.2, color=line)
    line_arrow([(0.565, 0.342), (0.565, 0.290)], color=CORAL_DARK, lw=0.75)

    # Verifier record chip.
    card(0.628, 0.340, 0.118, 0.085, "e = Autun\ns = high,  u = helpful\nC = {1, 2}", "#FFF4CF", AMBER, fs=5.0)
    line_arrow([(0.617, 0.379), (0.628, 0.379)], color=CORAL_DARK, lw=0.75)

    # Three slanted audit sheets, visually coupled rather than boxed in a row.
    audit_specs = [
        (0.632, "candidate", ("$c_1$", "$c_2$"), "#D5E2D1", TEAL),
        (0.708, "support", ("$c_3$", "$c_4$"), "#D7E2E1", BLUE),
        (0.784, "subject", ("$c_5$", "$c_6$"), "#E7E2C9", AMBER),
    ]
    for idx, (x, name, check_labels, fc, ec) in enumerate(audit_specs):
        y = 0.168
        w = 0.080
        h = 0.150
        slant = 0.014
        ax.add_patch(
            patches.Polygon(
                [(x, y), (x + w, y), (x + w + slant, y + h), (x + slant, y + h)],
                closed=True,
                facecolor=mpl.colors.to_rgba(fc, 0.82),
                edgecolor=ec,
                linewidth=0.6,
                zorder=4 + idx,
            )
        )
        ax.text(x + w / 2 + slant / 2, y + h + 0.014, name, ha="center", fontsize=4.75, weight="bold", color=line, zorder=9)
        for j, check_label in enumerate(check_labels):
            cx = x + slant + w * 0.48
            cy = y + h - 0.050 - j * 0.060
            ax.add_patch(patches.Circle((cx, cy), 0.016, facecolor=GREEN, edgecolor=ec, linewidth=0.5, zorder=8 + idx))
            ax.text(cx, cy, "1", ha="center", va="center", fontsize=4.2, color="white", weight="bold", zorder=10)
            ax.text(cx - 0.025, cy, check_label, ha="right", va="center", fontsize=4.5, color=line, zorder=10)

    # Evidence documents feed the verifier/audits through dashed links.
    line_arrow([(0.837, 0.700), (0.750, 0.520), (0.680, 0.318)], color=line, lw=0.7, dashed=True, z=2)
    line_arrow([(0.890, 0.700), (0.818, 0.520), (0.756, 0.318)], color=line, lw=0.7, dashed=True, z=2)
    line_arrow([(0.943, 0.700), (0.930, 0.520), (0.832, 0.318)], color=line, lw=0.7, dashed=True, z=2)

    card(0.625, 0.090, 0.238, 0.055, r"$g(x,d,e,D,m)=\prod_{j=1}^{6}c_j=1$", "#F8F7ED", line, fs=6.1)
    for x in (0.679, 0.755, 0.831):
        line_arrow([(x, 0.168), (x, 0.145)], color=muted, lw=0.55)

    card(0.878, 0.128, 0.073, 0.126, "Final\nAutun\n[PASS]", "#CFE6D6", GREEN, fs=5.7)
    line_arrow([(0.863, 0.118), (0.878, 0.170)], color=GREEN, lw=1.0)
    ax.text(0.914, 0.103, r"$\hat{y}=e$", ha="center", fontsize=5.2, color=GREEN, weight="bold")

    save_figure(fig, "Fig01_overview_and_worked_example")


def figure_2_formal_audit() -> None:
    fig = plt.figure(figsize=(7.08, 3.55))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Three aligned regions, visually echoing the compact method schematics of
    # the reference paper without copying its specific artwork.
    for x, w, fc in [(0.018, 0.304, CREAM), (0.348, 0.270, CREAM_2), (0.644, 0.338, CREAM)]:
        ax.add_patch(
            patches.FancyBboxPatch(
                (x, 0.035),
                w,
                0.93,
                boxstyle="round,pad=0.008,rounding_size=0.018",
                linewidth=0.65,
                edgecolor="#BEC8BE",
                facecolor=fc,
            )
        )

    ax.text(0.035, 0.925, "(a) Dual retrieval and fusion", weight="bold", fontsize=7.6, color=INK)
    ax.text(0.365, 0.925, "(b) Structured evidence record", weight="bold", fontsize=7.6, color=INK)
    ax.text(0.661, 0.925, "(c) Deterministic audit and decision", weight="bold", fontsize=7.6, color=INK)

    rounded_box(
        ax,
        (0.043, 0.742),
        0.252,
        0.105,
        r"$q_0=\mathcal{N}(x\oplus t\oplus s\oplus r)$",
        facecolor=SAGE,
        edgecolor=SAGE_DARK,
        fontsize=8.0,
        weight="bold",
    )
    rounded_box(
        ax,
        (0.043, 0.575),
        0.252,
        0.105,
        r"$q_1=\mathcal{N}(q_0\oplus d)$",
        facecolor=CORAL_PALE,
        edgecolor=CORAL_DARK,
        fontsize=8.0,
        weight="bold",
    )
    # Each query feeds its own ranking before fusion.
    ax.plot([0.043, 0.030, 0.030, 0.083], [0.795, 0.795, 0.440, 0.440], color=SAGE_DARK, lw=0.75, zorder=2)
    arrow(ax, (0.083, 0.440), (0.100, 0.425), color=SAGE_DARK)
    arrow(ax, (0.169, 0.575), (0.233, 0.425), color=CORAL_DARK, connectionstyle="arc3,rad=-0.10")
    ax.text(0.098, 0.487, "answer-free", fontsize=5.8, color=SAGE_DARK, ha="center")
    ax.text(0.238, 0.470, "answer-conditioned", fontsize=5.8, color=CORAL_DARK, ha="center")

    # Rank-list glyphs. Different passage orders make the purpose of RRF visible.
    rank_specs = [
        (0.055, TEAL_2, r"$R_0$", ["p1", "p3", "p5", "p7"]),
        (0.188, CORAL, r"$R_1$", ["p2", "p1", "p5", "p8"]),
    ]
    for x0, col, name, passage_ids in rank_specs:
        ax.text(x0 + 0.045, 0.405, name, ha="center", va="bottom", fontsize=7.2, weight="bold")
        for i, passage_id in enumerate(passage_ids):
            ax.add_patch(
                patches.FancyBboxPatch(
                    (x0, 0.346 - 0.052 * i),
                    0.09,
                    0.038,
                    boxstyle="round,pad=0.002,rounding_size=0.006",
                    facecolor=mpl.colors.to_rgba(col, 0.18 + 0.13 * (3 - i)),
                    edgecolor=col,
                    linewidth=0.55,
                )
            )
            ax.text(x0 + 0.012, 0.365 - 0.052 * i, passage_id, fontsize=5.8, va="center")
            ax.text(x0 + 0.077, 0.365 - 0.052 * i, f"{i+1}", fontsize=5.8, va="center", ha="right")

    rounded_box(
        ax,
        (0.043, 0.078),
        0.252,
        0.102,
        r"$S_{\mathrm{RRF}}(p)=\sum_{q\in\{q_0,q_1\}}\frac{1}{20+\operatorname{rank}_{q}(p)}$",
        facecolor=TEAL_PALE,
        edgecolor=TEAL,
        fontsize=7.1,
        weight="bold",
    )
    arrow(ax, (0.169, 0.215), (0.169, 0.180), color=TEAL)

    # Verifier record.
    ax.text(0.483, 0.835, r"$v=(e,\ s,\ u,\ C,\ \rho)$", ha="center", fontsize=10.0, color=INK, weight="bold")
    record_rows = [
        ("evidence answer", r"$e$", TEAL_PALE, TEAL),
        ("support level", r"$s\in\{H,M,L,N\}$", AMBER_PALE, AMBER),
        ("evidence utility", r"$u\in\{helpful,harmful,neutral,insuff.\}$", SAGE, SAGE_DARK),
        ("cited documents", r"$C\subseteq\{1,2,3\}$", BLUE_PALE, BLUE),
        ("reason", r"$\rho$", GRAY_PALE, GRAY),
    ]
    y = 0.690
    for label, symbol, fc, ec in record_rows:
        rounded_box(
            ax,
            (0.374, y),
            0.218,
            0.092,
            f"{label}\n{symbol}",
            facecolor=fc,
            edgecolor=ec,
            fontsize=6.3,
            weight="bold",
        )
        y -= 0.123
    ax.text(
        0.483,
        0.085,
        "The verifier may return an empty e when support is missing,\nconflicting, off-subject, or relation-incompatible.",
        ha="center",
        va="center",
        fontsize=5.8,
        color="#56625F",
        style="italic",
    )

    # Gate conditions.
    checks = [
        r"$c_1=\mathbb{1}[e\ne\varnothing]$",
        r"$c_2=\mathbb{1}[u=helpful]$",
        r"$c_3=\mathbb{1}[s\in\{H,M\}]$",
        r"$c_4=\operatorname{ground}(e,C)$",
        r"$c_5=\operatorname{ground}(subject,C)$",
        r"$c_6=\mathbb{1}[\mathcal{N}(e)\ne\mathcal{N}(d)]$",
    ]
    for i, txt in enumerate(checks):
        row = i // 2
        col = i % 2
        x = 0.671 + col * 0.148
        y = 0.750 - row * 0.126
        rounded_box(
            ax,
            (x, y),
            0.132,
            0.085,
            txt,
            facecolor=GREEN_PALE if i < 3 else TEAL_PALE,
            edgecolor=GREEN if i < 3 else TEAL,
            fontsize=6.05,
            weight="bold",
        )

    rounded_box(
        ax,
        (0.700, 0.315),
        0.226,
        0.105,
        r"$g(x,d,e,D,m)=\prod_{j=1}^{6}c_j$",
        facecolor=AMBER_PALE,
        edgecolor=AMBER,
        fontsize=8.2,
        weight="bold",
    )
    arrow(ax, (0.813, 0.535), (0.813, 0.420), color=INK)

    # Piecewise decision as two compact lines; this is more legible than a tall
    # TeX cases environment at journal column scale.
    rounded_box(
        ax,
        (0.672, 0.105),
        0.282,
        0.135,
        "Final selection\nŷ = e,  if g = 1\nŷ = Rescue(D),  if d = e = ∅\nŷ = d,  otherwise",
        facecolor="#F9F7EE",
        edgecolor=INK,
        fontsize=6.8,
        weight="bold",
    )
    arrow(ax, (0.813, 0.315), (0.813, 0.240), color=INK)

    arrow(ax, (0.322, 0.505), (0.348, 0.505), color=TEAL, lw=1.0)
    arrow(ax, (0.618, 0.505), (0.644, 0.505), color=TEAL, lw=1.0)
    ax.text(0.335, 0.530, "top-3", fontsize=5.6, color=TEAL, ha="center")
    ax.text(0.631, 0.530, "audit", fontsize=5.6, color=TEAL, ha="center")

    save_figure(fig, "Fig02_formal_retrieval_and_risk_audit")


def figure_3_main_results() -> None:
    methods = ["Direct", "Always Evidence", "Prior Reference", "UER-RAG"]
    colors = [GRAY, CORAL, TEAL_2, TEAL]
    pop = np.array(
        [
            [38.12, 40.30, 42.77],
            [57.95, 66.36, 65.56],
            [61.23, 68.54, 69.52],
            [63.01, 68.31, 69.82],
        ]
    )
    ent = np.array(
        [
            [38.08, 42.74, 48.07],
            [40.34, 50.10, 51.59],
            [47.16, 55.96, 59.51],
            [47.58, 55.68, 59.57],
        ]
    )

    fig = plt.figure(figsize=(7.08, 4.78))
    gs = fig.add_gridspec(
        2,
        2,
        left=0.07,
        right=0.985,
        bottom=0.105,
        top=0.925,
        hspace=0.46,
        wspace=0.34,
    )
    ax_pop = fig.add_subplot(gs[0, 0])
    ax_ent = fig.add_subplot(gs[0, 1])
    ax_ci = fig.add_subplot(gs[1, 0])
    ax_trade = fig.add_subplot(gs[1, 1])

    width = 0.18
    x = np.arange(3)
    for ax, arr, label in [(ax_pop, pop, "(a)  PopQA - complete 14,267"), (ax_ent, ent, "(b)  EntityQuestions - 5,000")]:
        for i, (method, color) in enumerate(zip(methods, colors)):
            bars = ax.bar(
                x + (i - 1.5) * width,
                arr[i],
                width,
                color=color,
                edgecolor="white",
                linewidth=0.35,
                zorder=3,
            )
            for bar, val in zip(bars, arr[i]):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + 1.05,
                    f"{val:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=5.15,
                    color=INK,
                )
        ax.set_xticks(x, ["EM", "Accuracy", "Token F1"])
        ax.set_ylim(0, 75)
        ax.set_ylabel("Score (%)")
        clean_axes(ax, grid="y")
        ax.text(0.0, 1.045, label, transform=ax.transAxes, weight="bold", fontsize=7.6)
    handles = [patches.Patch(facecolor=c, label=m) for m, c in zip(methods, colors)]
    fig.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.52, 0.995),
        frameon=False,
        ncol=4,
        handlelength=1.3,
        columnspacing=1.25,
    )

    # Paired gain CIs.
    labels = [
        "PopQA · EM",
        "PopQA · Accuracy",
        "PopQA · F1",
        "EntityQuestions · EM",
        "EntityQuestions · Accuracy",
        "EntityQuestions · F1",
    ]
    delta = np.array([24.88, 28.02, 27.05, 9.50, 12.94, 11.50])
    lo = np.array([24.15, 27.25, 26.33, 8.56, 11.88, 10.59])
    hi = np.array([25.62, 28.78, 27.77, 10.46, 14.00, 12.45])
    y = np.arange(len(labels))[::-1]
    ci_colors = [BLUE] * 3 + [TEAL] * 3
    for yi, d, l, h_, c in zip(y, delta, lo, hi, ci_colors):
        ax_ci.plot([l, h_], [yi, yi], color=c, lw=1.6, solid_capstyle="round", zorder=2)
        ax_ci.plot(d, yi, "o", color=c, ms=4.3, mec="white", mew=0.5, zorder=3)
        ax_ci.text(h_ + 0.55, yi, f"+{d:.1f}", va="center", fontsize=5.8, color=INK)
    ax_ci.axvline(0, color=INK, lw=0.65, ls=(0, (3, 2)))
    ax_ci.set_yticks(y, labels)
    ax_ci.set_xlim(-1.5, 31.5)
    ax_ci.set_xlabel("Paired gain over Direct (percentage points)")
    ax_ci.text(0.0, 1.045, "(c)  Paired 95% bootstrap intervals", transform=ax_ci.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_ci, grid="x")

    # Performance-harm frontier on PopQA.
    harm = np.array([0.0, 9.61, 3.71, 1.07])
    f1 = pop[:, 2]
    markers = ["o", "s", "D", "o"]
    sizes = [36, 42, 42, 62]
    for m, xh, yf, c, mk, sz in zip(methods, harm, f1, colors, markers, sizes):
        ax_trade.scatter(xh, yf, s=sz, color=c, marker=mk, edgecolor="white", linewidth=0.6, zorder=4)
        dx, dy = {
            "Direct": (0.28, 0.2),
            "Always Evidence": (-3.2, 0.55),
            "Prior Reference": (0.35, -1.55),
            "UER-RAG": (0.35, 0.42),
        }[m]
        ax_trade.text(xh + dx, yf + dy, m, fontsize=6.0, color=INK)
    ax_trade.annotate(
        "preferred",
        xy=(0.6, 71.0),
        xytext=(4.2, 58.0),
        arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 0.9},
        color=TEAL,
        fontsize=6.0,
        weight="bold",
    )
    ax_trade.set_xlim(-0.6, 10.6)
    ax_trade.set_ylim(40, 72.2)
    ax_trade.set_xlabel("Harm rate relative to Direct (%)")
    ax_trade.set_ylabel("Token F1 (%)")
    ax_trade.text(0.0, 1.045, "(d)  PopQA performance-risk frontier", transform=ax_trade.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_trade, grid="both")

    save_figure(fig, "Fig03_main_results_and_risk_frontier")


def figure_4_routing_and_safety() -> None:
    fig = plt.figure(figsize=(7.08, 4.90))
    gs = fig.add_gridspec(
        2,
        2,
        left=0.085,
        right=0.985,
        bottom=0.105,
        top=0.935,
        hspace=0.50,
        wspace=0.40,
    )
    ax_outcome = fig.add_subplot(gs[0, 0])
    ax_route = fig.add_subplot(gs[0, 1])
    ax_utility = fig.add_subplot(gs[1, 0])
    ax_trans = fig.add_subplot(gs[1, 1])

    datasets = ["PopQA", "EntityQuestions"]
    y = np.array([1, 0])

    # (a) outcome composition.
    outcome = np.array([[31.28, 1.07, 67.65], [17.66, 2.76, 79.58]])
    left = np.zeros(2)
    for j, (name, color) in enumerate(zip(["Improved", "Harmed", "Unchanged"], [TEAL, CORAL_DARK, GRAY_PALE])):
        vals = outcome[:, j]
        ax_outcome.barh(y, vals, left=left, color=color, height=0.42, edgecolor="white", linewidth=0.4)
        for yi, l, v in zip(y, left, vals):
            if v >= 7:
                ax_outcome.text(l + v / 2, yi, f"{v:.1f}%", ha="center", va="center", fontsize=5.9, color="white" if name != "Unchanged" else INK)
            elif v >= 0.8:
                ax_outcome.text(l + v / 2, yi + 0.28, f"{v:.1f}%", ha="center", va="center", fontsize=5.7, color=CORAL_DARK)
        left += vals
    ax_outcome.set_yticks(y, datasets)
    ax_outcome.set_xlim(0, 100)
    ax_outcome.set_xlabel("Share of examples (%)")
    ax_outcome.text(0.0, 1.055, "(a)  F1 outcome composition", transform=ax_outcome.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_outcome, grid=None)
    ax_outcome.spines["left"].set_visible(False)
    ax_outcome.legend(
        handles=[patches.Patch(color=c, label=n) for n, c in zip(["Improved", "Harmed", "Unchanged"], [TEAL, CORAL_DARK, GRAY_PALE])],
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.50, -0.43),
        handlelength=1.1,
        columnspacing=1.0,
    )

    # (b) selected answer source.
    route_counts = np.array([[8593, 5671, 3], [3602, 1397, 1]])
    route = route_counts / route_counts.sum(axis=1, keepdims=True) * 100
    left = np.zeros(2)
    route_names = ["Direct", "Evidence", "Rescue"]
    route_cols = [GRAY, BLUE, CORAL]
    for j, (name, color) in enumerate(zip(route_names, route_cols)):
        vals = route[:, j]
        ax_route.barh(y, vals, left=left, color=color, height=0.42, edgecolor="white", linewidth=0.4)
        for yi, l, v in zip(y, left, vals):
            if v >= 5:
                ax_route.text(l + v / 2, yi, f"{v:.1f}%", ha="center", va="center", fontsize=5.9, color="white")
        left += vals
    # The Rescue proportions are subpixel at publication width; show exact counts.
    ax_route.text(99.5, 1.30, "Rescue: 3", ha="right", va="center", fontsize=5.6, color=CORAL_DARK)
    ax_route.text(99.5, 0.30, "Rescue: 1", ha="right", va="center", fontsize=5.6, color=CORAL_DARK)
    ax_route.set_yticks(y, datasets)
    ax_route.set_xlim(0, 100)
    ax_route.set_xlabel("Selected final-answer source (%)")
    ax_route.text(0.0, 1.055, "(b)  Conservative source selection", transform=ax_route.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_route, grid=None)
    ax_route.spines["left"].set_visible(False)
    ax_route.legend(
        handles=[patches.Patch(color=c, label=n) for n, c in zip(route_names, route_cols)],
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.50, -0.43),
        handlelength=1.1,
        columnspacing=1.0,
    )

    # (c) verifier utility.
    utility = np.array([[43.05, 34.13, 22.60, 0.22], [31.26, 39.00, 29.58, 0.16]])
    utility_names = ["Helpful", "Neutral", "Insufficient", "Harmful"]
    utility_cols = [TEAL, GRAY, AMBER, CORAL_DARK]
    left = np.zeros(2)
    for j, (name, color) in enumerate(zip(utility_names, utility_cols)):
        vals = utility[:, j]
        ax_utility.barh(y, vals, left=left, color=color, height=0.42, edgecolor="white", linewidth=0.4)
        for yi, l, v in zip(y, left, vals):
            if v >= 8:
                ax_utility.text(l + v / 2, yi, f"{v:.1f}%", ha="center", va="center", fontsize=5.7, color="white" if name != "Insufficient" else INK)
        left += vals
    ax_utility.text(99.6, 1.30, "Harmful: 0.22%", ha="right", va="center", fontsize=5.6, color=CORAL_DARK)
    ax_utility.text(99.6, 0.30, "Harmful: 0.16%", ha="right", va="center", fontsize=5.6, color=CORAL_DARK)
    ax_utility.set_yticks(y, datasets)
    ax_utility.set_xlim(0, 100)
    ax_utility.set_xlabel("Verifier-assessed evidence utility (%)")
    ax_utility.text(0.0, 1.055, "(c)  Evidence is often non-actionable", transform=ax_utility.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_utility, grid=None)
    ax_utility.spines["left"].set_visible(False)
    ax_utility.legend(
        handles=[patches.Patch(color=c, label=n) for n, c in zip(utility_names, utility_cols)],
        frameon=False,
        ncol=4,
        loc="lower center",
        bbox_to_anchor=(0.50, -0.43),
        handlelength=1.0,
        columnspacing=0.75,
    )

    # (d) EM transition matrices as compact inset heatmaps.
    ax_trans.axis("off")
    ax_trans.text(0.0, 1.055, "(d)  Exact-match transitions", transform=ax_trans.transAxes, weight="bold", fontsize=7.6)
    cmap = LinearSegmentedColormap.from_list("paper_green", ["#F2F5F0", "#8FC8A5", "#1E8055", "#0A4C32"])
    matrices = [
        ("PopQA", np.array([[5179, 3649], [99, 5340]]), 14267),
        ("EntityQuestions", np.array([[2541, 555], [80, 1824]]), 5000),
    ]
    for i, (name, mat, total) in enumerate(matrices):
        iax = ax_trans.inset_axes([0.00 + i * 0.52, 0.03, 0.43, 0.88])
        iax.imshow(mat / total * 100, cmap=cmap, vmin=0, vmax=40, aspect="equal")
        iax.set_xticks([0, 1], ["Final\nwrong", "Final\ncorrect"], fontsize=5.6)
        iax.set_yticks([0, 1], ["Direct wrong", "Direct correct"] if i == 0 else ["", ""], fontsize=5.6)
        iax.tick_params(length=0)
        iax.set_title(name, fontsize=6.8, pad=4, weight="bold")
        for r in range(2):
            for c in range(2):
                pct = mat[r, c] / total * 100
                txt_color = "white" if pct > 22 else INK
                iax.text(c, r, f"{mat[r,c]:,}\n({pct:.1f}%)", ha="center", va="center", fontsize=5.6, color=txt_color, weight="bold" if (r, c) in [(0, 1), (1, 0)] else "normal")
        for spine in iax.spines.values():
            spine.set_linewidth(0.55)
            spine.set_color(INK)
    ax_trans.text(0.205, -0.08, "repairs: 3,649   |   corruptions: 99", transform=ax_trans.transAxes, ha="center", fontsize=5.5, color=INK)
    ax_trans.text(0.73, -0.08, "repairs: 555   |   corruptions: 80", transform=ax_trans.transAxes, ha="center", fontsize=5.5, color=INK)

    save_figure(fig, "Fig04_routing_evidence_and_safety")


def load_relation_rows() -> list[dict[str, str]]:
    with (DATA_ROOT / "relation_results.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def figure_5_generalization() -> None:
    rows = load_relation_rows()
    rows = sorted(rows, key=lambda r: float(r["f1_gain"]))
    rel_labels = [f"{r['relation']} · {r['relation_name']}  (n={int(r['count'])})" for r in rows]
    gains = np.array([100 * float(r["f1_gain"]) for r in rows])

    fig = plt.figure(figsize=(7.08, 5.05))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.40, 1.00],
        height_ratios=[1.05, 0.95],
        left=0.145,
        right=0.985,
        bottom=0.095,
        top=0.955,
        hspace=0.49,
        wspace=0.38,
    )
    ax_rel = fig.add_subplot(gs[:, 0])
    ax_model = fig.add_subplot(gs[0, 1])
    ax_cases = fig.add_subplot(gs[1, 1])

    y = np.arange(len(rows))
    bar_cols = [TEAL_PALE if g < 8 else TEAL_2 if g < 15 else TEAL for g in gains]
    ax_rel.barh(y, gains, color=bar_cols, edgecolor="white", linewidth=0.35, height=0.72, zorder=3)
    for yi, g in zip(y, gains):
        ax_rel.text(g + 0.40, yi, f"+{g:.1f}", va="center", fontsize=5.25, color=INK)
    ax_rel.set_yticks(y, rel_labels)
    ax_rel.set_xlim(0, 31.5)
    ax_rel.set_xlabel("Token F1 gain over Direct (percentage points)")
    ax_rel.text(0.0, 1.02, "(a)  Positive mean gain across all 24 relations", transform=ax_rel.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_rel, grid="x")
    ax_rel.spines["left"].set_visible(False)
    ax_rel.tick_params(axis="y", length=0)

    models = ["DeepSeek-v4-flash", "GPT-4o"]
    direct_vals = np.array([37.60, 46.98, 44.35, 53.01])
    final_vals = np.array([48.10, 59.67, 50.80, 60.17])
    row_labels = ["DeepSeek · EM", "DeepSeek · F1", "GPT-4o · EM", "GPT-4o · F1"]
    yy = np.arange(4)[::-1]
    for yi, dval, fval in zip(yy, direct_vals, final_vals):
        ax_model.plot([dval, fval], [yi, yi], color=TEAL_2, lw=1.5, zorder=2)
        ax_model.scatter(dval, yi, s=24, color=GRAY, edgecolor="white", linewidth=0.5, zorder=3)
        ax_model.scatter(fval, yi, s=29, color=TEAL, edgecolor="white", linewidth=0.5, zorder=3)
        ax_model.text(dval - 0.7, yi + 0.20, f"{dval:.1f}", ha="right", fontsize=5.3, color=GRAY)
        ax_model.text(fval + 0.7, yi + 0.20, f"{fval:.1f}", ha="left", fontsize=5.3, color=TEAL)
    ax_model.set_yticks(yy, row_labels)
    ax_model.set_xlim(32, 64)
    ax_model.set_xlabel("Score (%)")
    ax_model.text(0.0, 1.055, "(b)  Cross-model transfer (same 2,000 cases)", transform=ax_model.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_model, grid="x")
    ax_model.spines["left"].set_visible(False)
    ax_model.tick_params(axis="y", length=0)
    ax_model.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=GRAY, markeredgecolor="white", label="Direct"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=TEAL, markeredgecolor="white", label="UER-RAG"),
        ],
        frameon=False,
        ncol=2,
        loc="upper right",
        fontsize=5.6,
        handlelength=0.8,
        columnspacing=0.9,
    )

    improved = np.array([373, 223])
    harmed = np.array([44, 51])
    yy = np.arange(2)[::-1]
    ax_cases.barh(yy, improved, color=TEAL, height=0.34, label="Improved", zorder=3)
    ax_cases.barh(yy, -harmed, color=CORAL_DARK, height=0.34, label="Harmed", zorder=3)
    for yi, imp, harm in zip(yy, improved, harmed):
        ax_cases.text(imp + 10, yi, f"{imp}", va="center", fontsize=5.8, color=TEAL, weight="bold")
        ax_cases.text(-harm - 7, yi, f"{harm}", va="center", ha="right", fontsize=5.8, color=CORAL_DARK, weight="bold")
    ax_cases.axvline(0, color=INK, lw=0.6)
    ax_cases.set_yticks(yy, models)
    ax_cases.set_xlim(-90, 430)
    ax_cases.set_xticks([-50, 0, 100, 200, 300, 400], ["50", "0", "100", "200", "300", "400"])
    ax_cases.set_xlabel("Number of paired cases")
    ax_cases.text(0.0, 1.055, "(c)  Improvements remain more frequent than harms", transform=ax_cases.transAxes, weight="bold", fontsize=7.6)
    clean_axes(ax_cases, grid="x")
    ax_cases.spines["left"].set_visible(False)
    ax_cases.legend(
        handles=[patches.Patch(color=TEAL, label="Improved"), patches.Patch(color=CORAL_DARK, label="Harmed")],
        frameon=False,
        ncol=1,
        loc="center right",
        fontsize=5.7,
        handlelength=1.0,
    )

    save_figure(fig, "Fig05_relation_and_cross_model_generalization")


def main() -> None:
    figure_1_overview_and_example()
    figure_2_formal_audit()
    figure_3_main_results()
    figure_4_routing_and_safety()
    figure_5_generalization()
    print(f"Wrote review figures to: {OUT}")


if __name__ == "__main__":
    main()
