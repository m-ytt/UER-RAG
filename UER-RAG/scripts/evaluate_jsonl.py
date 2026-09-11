#!/usr/bin/env python3
"""Convenience wrapper for the package's offline evaluator."""

from uer_rag.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["evaluate", *__import__("sys").argv[1:]]))
