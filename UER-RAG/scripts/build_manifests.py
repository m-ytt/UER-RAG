#!/usr/bin/env python3
"""Extract qid-only split manifests from frozen prediction JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    qids = []
    seen = set()
    with Path(args.input).open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            qid = str(json.loads(line)["qid"])
            if qid in seen:
                raise ValueError(f"duplicate qid {qid!r} at line {number}")
            seen.add(qid)
            qids.append(qid)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(qids) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(qids), "output": str(target)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
