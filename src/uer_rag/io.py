"""Small JSONL helpers with qid-based resume support."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path


def read_jsonl(path: str | Path) -> Iterator[dict[str, object]]:
    with Path(path).open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TypeError(f"{path}:{number}: each JSONL value must be an object")
            yield value


def completed_qids(path: str | Path) -> set[str]:
    target = Path(path)
    if not target.exists():
        return set()
    return {str(row["qid"]) for row in read_jsonl(target) if "qid" in row}


def append_jsonl(path: str | Path, rows: Iterable[Mapping[str, object]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
        handle.flush()
