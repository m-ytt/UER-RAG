#!/usr/bin/env python3
"""Generate the standalone figures used by the no-appendix manuscript."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    # Figure 1 is emitted when its vector source module is executed.
    runpy.run_path(str(ROOT / "build_flowchart.py"), run_name="__main__")

    flowcharts = runpy.run_path(str(ROOT / "build_flowcharts_2_4.py"))
    for name in ("figure2", "figure3", "figure4"):
        flowcharts[name]()

    results = runpy.run_path(str(ROOT / "build_result_figures.py"))
    results["main"]()
    print(f"Wrote standalone manuscript figures to: {ROOT / 'output'}")


if __name__ == "__main__":
    main()
