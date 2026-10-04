#!/usr/bin/env python3
"""Build standalone quantitative panels from versioned result sources."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import figure_style as palette
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

with (ROOT.parent / "results" / "figure_statistics.json").open("r", encoding="utf-8") as handle:
    STATS = json.load(handle)

INK = palette.INK
GRID = palette.GRID
TEAL = palette.TEAL
TEAL_2 = palette.TEAL_2
TEAL_PALE = palette.TEAL_PALE
BLUE = palette.BLUE
CORAL_DARK = palette.CORAL_DARK
AMBER = palette.AMBER
GRAY = palette.GRAY
GRAY_PALE = palette.GRAY_PALE

METHODS = list(STATS["method_order"])
METRICS = list(STATS["metric_order"])
COLORS = [GRAY, AMBER, BLUE, TEAL]
DATASETS = ["PopQA", "EntityQuestions"]
POP = np.asarray(STATS["benchmarks"]["popqa_complete_14267"], dtype=float)
ENT = np.asarray(STATS["benchmarks"]["entityquestions_test_5000"], dtype=float)

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "mathtext.fontset": "stixsans",
        "font.size": 8.0,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.0,
        "ytick.labelsize": 7.0,
        "axes.edgecolor": INK,
        "axes.linewidth": 0.7,
        "grid.color": GRID,
        "grid.linewidth": 0.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    }
)


def save(fig: plt.Figure, stem: str) -> None:
    """Save an editable vector pair and a high-resolution review image."""

    for extension in ("svg", "pdf"):
        fig.savefig(OUT / f"{stem}.{extension}", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(OUT / f"{stem}.png", dpi=450, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def clean(ax: plt.Axes, grid: str | None = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=2.8, width=0.65, color=INK)
    if grid:
        ax.grid(True, axis=grid, zorder=0)


def benchmark(values: np.ndarray, stem: str) -> None:
    """Grouped scores; the maximum in every metric group is bold."""

    x = np.arange(len(METRICS))
    width = 0.18
    fig, ax = plt.subplots(figsize=(6.15, 3.25))
    for index, (method, color) in enumerate(zip(METHODS, COLORS)):
        offset = (index - 1.5) * width
        bars = ax.bar(
            x + offset,
            values[index],
            width,
            label=method,
            color=color,
            edgecolor="white",
            linewidth=0.5,
            zorder=3,
        )
        for metric_index, (bar, score) in enumerate(zip(bars, values[index])):
            maximum = np.isclose(score, values[:, metric_index].max())
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                score + 0.65,
                f"{score:.2f}",
                ha="center",
                va="bottom",
                fontsize=6.2,
                weight="bold" if maximum else "normal",
                color=INK,
            )
    ax.set_xticks(x, METRICS)
    ax.set_ylabel("Score (%)")
    ax.set_ylim(0, max(76, float(values.max()) + 8))
    ax.legend(
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        handlelength=1.0,
        columnspacing=1.1,
    )
    clean(ax)
    save(fig, stem)


def paired_intervals() -> None:
    intervals = STATS["paired_gain_intervals_pp"]
    labels = list(intervals["order"])
    means = np.asarray(intervals["mean"], dtype=float)
    low = np.asarray(intervals["low"], dtype=float)
    high = np.asarray(intervals["high"], dtype=float)
    errors = np.vstack([means - low, high - means])
    y = np.arange(len(labels))[::-1]
    colors = [TEAL] * 3 + [BLUE] * 3
    fig, ax = plt.subplots(figsize=(6.25, 3.35))
    for index, yi in enumerate(y):
        ax.errorbar(
            means[index],
            yi,
            xerr=errors[:, index : index + 1],
            fmt="o",
            color=colors[index],
            ecolor=colors[index],
            capsize=3,
            markersize=5.2,
            linewidth=1.2,
            zorder=3,
        )
        ax.text(
            high[index] + 0.35,
            yi,
            f"+{means[index]:.2f} [{low[index]:.2f}, {high[index]:.2f}]",
            va="center",
            fontsize=6.5,
            weight="bold" if np.isclose(means[index], means.max()) else "normal",
        )
    ax.axvline(0, color=INK, linewidth=0.8)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 33)
    ax.set_xlabel("Paired gain over Direct (percentage points), 95% bootstrap CI")
    clean(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "Fig07_paired_intervals_original")


def performance_risk() -> None:
    harm = np.asarray(STATS["popqa_harm_rate_pct"], dtype=float)
    f1 = POP[:, 2]
    markers = ["o", "s", "D", "o"]
    offsets = {
        "Direct": (0.25, 0.25),
        "Always Evidence": (-3.25, 0.7),
        "Prior Reference": (0.35, -1.45),
        "UER-RAG": (0.30, 0.55),
    }
    fig, ax = plt.subplots(figsize=(5.65, 3.35))
    for method, x_value, y_value, color, marker in zip(METHODS, harm, f1, COLORS, markers):
        ax.scatter(
            x_value,
            y_value,
            s=64 if method == "UER-RAG" else 46,
            color=color,
            marker=marker,
            edgecolor="white",
            linewidth=0.7,
            zorder=4,
        )
        dx, dy = offsets[method]
        ax.text(
            x_value + dx,
            y_value + dy,
            method,
            fontsize=7.0,
            weight="bold" if method == "UER-RAG" else "normal",
        )
    ax.annotate(
        "lower harm / higher F1",
        xy=(1.1, 69.8),
        xytext=(5.0, 57.2),
        arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 1.0},
        fontsize=7.0,
        color=TEAL,
    )
    ax.set_xlim(-0.6, 10.7)
    ax.set_ylim(40, 72.2)
    ax.set_xlabel("Harm rate relative to Direct (%)")
    ax.set_ylabel("Token F1 (%)")
    clean(ax, "both")
    save(fig, "Fig08_performance_risk_original")


def stacked_panel(
    values: np.ndarray,
    names: list[str],
    colors: list[str],
    xlabel: str,
    stem: str,
    *,
    small_labels: list[str],
) -> None:
    y = np.arange(2)[::-1]
    fig, ax = plt.subplots(figsize=(6.35, 2.55))
    left = np.zeros(2)
    for column, (name, color) in enumerate(zip(names, colors)):
        current = values[:, column]
        ax.barh(
            y,
            current,
            left=left,
            height=0.44,
            color=color,
            edgecolor="white",
            linewidth=0.5,
            label=name,
        )
        for row, (yi, offset, value) in enumerate(zip(y, left, current)):
            if value >= 7:
                maximum = np.isclose(value, values[row].max())
                text_color = "white" if color not in (GRAY_PALE,) else INK
                ax.text(
                    offset + value / 2,
                    yi,
                    f"{value:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=7.0,
                    color=text_color,
                    weight="bold" if maximum else "normal",
                )
        left += current
    for row, label in enumerate(small_labels):
        ax.text(
            99.5,
            y[row] + 0.30,
            label,
            ha="right",
            va="center",
            fontsize=6.4,
            color=CORAL_DARK,
        )
    ax.set_yticks([])
    for yi, dataset in zip(y, DATASETS):
        ax.text(
            -2.0,
            yi,
            dataset,
            ha="right",
            va="center",
            fontsize=7.2,
            color=INK,
            clip_on=False,
        )
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, 1.55)
    ax.set_xlabel(xlabel)
    ax.legend(
        frameon=False,
        ncol=len(names),
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        handlelength=1.0,
        columnspacing=1.0,
    )
    clean(ax, None)
    ax.spines["left"].set_visible(False)
    save(fig, stem)


def outcome_composition() -> None:
    stacked_panel(
        np.asarray(STATS["outcome_composition_pct"], dtype=float),
        ["Improved", "Harmed", "Unchanged"],
        [TEAL, CORAL_DARK, GRAY_PALE],
        "Share of examples (%)",
        "Fig09_outcome_composition_original",
        small_labels=["Harmed: 1.07%", "Harmed: 2.76%"],
    )


def evidence_utility() -> None:
    stacked_panel(
        np.asarray(STATS["evidence_utility_pct"], dtype=float),
        ["Helpful", "Neutral", "Insufficient", "Harmful"],
        [TEAL, GRAY, AMBER, CORAL_DARK],
        "Verifier-assessed evidence utility (%)",
        "Fig11_evidence_utility_original",
        small_labels=["Harmful: 0.22%", "Harmful: 0.16%"],
    )


def em_transitions() -> None:
    colormap = LinearSegmentedColormap.from_list(
        "paper_green", ["#F2F5F0", "#8FC8A5", "#1E8055", "#0A4C32"]
    )
    transition_data = STATS["em_transitions"]
    matrices = [
        (
            "Fig12_popqa_em_transitions_original",
            np.asarray(transition_data["popqa_complete_14267"], dtype=int),
        ),
        (
            "Fig13_entityquestions_em_transitions_original",
            np.asarray(transition_data["entityquestions_test_5000"], dtype=int),
        ),
    ]
    for stem, matrix in matrices:
        total = int(matrix.sum())
        repairs = int(matrix[0, 1])
        corruptions = int(matrix[1, 0])
        fig, ax = plt.subplots(figsize=(3.55, 3.05))
        ax.imshow(matrix / total * 100, cmap=colormap, vmin=0, vmax=40, aspect="equal")
        ax.set_xticks([0, 1], ["Final\nwrong", "Final\ncorrect"])
        ax.set_yticks([0, 1], ["Direct wrong", "Direct correct"])
        ax.tick_params(length=0)
        for row in range(2):
            for column in range(2):
                percentage = matrix[row, column] / total * 100
                ax.text(
                    column,
                    row,
                    f"{matrix[row, column]:,}\n({percentage:.1f}%)",
                    ha="center",
                    va="center",
                    fontsize=7.0,
                    color="white" if percentage > 22 else INK,
                    weight="bold" if matrix[row, column] == matrix.max() else "normal",
                )
        for spine in ax.spines.values():
            spine.set_linewidth(0.7)
            spine.set_color(INK)
        ax.text(
            0.5,
            -0.28,
            f"repairs: {repairs:,}   |   corruptions: {corruptions:,}",
            transform=ax.transAxes,
            ha="center",
            fontsize=6.5,
            color=INK,
        )
        save(fig, stem)


def relation_gains() -> None:
    with (ROOT / "data" / "relation_results.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        rows = sorted(csv.DictReader(handle), key=lambda row: float(row["f1_gain"]))
    labels = [f"{row['relation']} · {row['relation_name']} (n={int(row['count'])})" for row in rows]
    gains = np.asarray([100 * float(row["f1_gain"]) for row in rows])
    y = np.arange(len(rows))
    colors = [TEAL_PALE if value < 8 else TEAL_2 if value < 15 else TEAL for value in gains]
    fig, ax = plt.subplots(figsize=(6.45, 5.10))
    bars = ax.barh(
        y,
        gains,
        color=colors,
        edgecolor="white",
        linewidth=0.4,
        height=0.72,
        zorder=3,
    )
    for bar, yi, gain in zip(bars, y, gains):
        ax.text(
            gain + 0.35,
            yi,
            f"+{gain:.1f}",
            va="center",
            fontsize=6.2,
            weight="bold" if np.isclose(gain, gains.max()) else "normal",
        )
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 31.5)
    ax.set_xlabel("Token F1 gain over Direct (percentage points)")
    clean(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "Fig14_relation_gains_original")


def popqa_split_sensitivity() -> None:
    """Compare complete PopQA with the development-disjoint subset."""

    source = STATS["popqa_split_sensitivity"]
    direct = np.asarray(source["direct_pct"], dtype=float)
    final = np.asarray(source["uer_rag_pct"], dtype=float)
    labels = list(source["labels"])
    y = np.arange(len(labels))[::-1]
    fig, ax = plt.subplots(figsize=(6.25, 3.25))
    for yi, direct_value, final_value in zip(y, direct, final):
        ax.plot([direct_value, final_value], [yi, yi], color=TEAL_2, linewidth=1.8)
        ax.scatter(
            direct_value,
            yi,
            s=32,
            color=GRAY,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        ax.scatter(
            final_value,
            yi,
            s=37,
            color=TEAL,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        ax.text(
            direct_value - 0.65,
            yi + 0.18,
            f"{direct_value:.2f}",
            ha="right",
            fontsize=6.4,
            color=GRAY,
        )
        ax.text(
            final_value + 0.65,
            yi + 0.18,
            f"{final_value:.2f}",
            ha="left",
            fontsize=6.4,
            color=TEAL,
            weight="bold",
        )
    ax.set_yticks(y, labels)
    ax.set_xlim(35, 73)
    ax.set_xlabel("Score (%)")
    ax.axhline(2.5, color=GRID, linewidth=0.8, linestyle=(0, (3, 3)), zorder=0)
    ax.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=GRAY,
                markeredgecolor="white",
                label="Direct",
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=TEAL,
                markeredgecolor="white",
                label="UER-RAG",
            ),
        ],
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
    )
    clean(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    save(fig, "Fig15_popqa_split_sensitivity_original")


def main() -> None:
    benchmark(POP, "Fig05_popqa_scores_original")
    benchmark(ENT, "Fig06_entityquestions_scores_original")
    paired_intervals()
    performance_risk()
    outcome_composition()
    evidence_utility()
    em_transitions()
    relation_gains()
    popqa_split_sensitivity()
    print(f"Wrote standalone quantitative figures to {OUT}")


if __name__ == "__main__":
    main()
