#!/usr/bin/env python3
"""Normalize benchmark exports and optionally apply a frozen qid manifest."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


def _load(path: Path) -> list[dict[str, object]]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".jsonl":
        values = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        value = json.loads(text)
        values = value.get("data", []) if isinstance(value, dict) else value
    if not isinstance(values, list) or not all(isinstance(row, dict) for row in values):
        raise TypeError("Input must be a JSON array or JSONL stream of objects")
    return values


def _first(row: dict[str, object], *names: str) -> object:
    for name in names:
        value = row.get(name)
        if value is not None and value != "":
            return value
    return ""


def _answers(value: object) -> list[str]:
    if isinstance(value, dict):
        value = value.get("text") or value.get("aliases") or []
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("[", "(")):
            try:
                value = ast.literal_eval(stripped)
            except (ValueError, SyntaxError):
                value = [stripped]
        else:
            value = [stripped]
    if not isinstance(value, (list, tuple, set)):
        value = [value]
    result = []
    for item in value:
        rendered = str(item or "").strip()
        if rendered and rendered not in result:
            result.append(rendered)
    return result


def _normalize(row: dict[str, object]) -> dict[str, object]:
    qid = str(_first(row, "qid", "id", "_id")).strip()
    question = str(_first(row, "question", "query")).strip()
    if not qid or not question:
        raise ValueError("Each source row requires qid/id and question/query")
    golds = _answers(_first(row, "gold_answers", "possible_answers", "answers", "answer", "obj"))
    result: dict[str, object] = {"qid": qid, "question": question}
    fields = {
        "entity": ("entity", "entity_title", "s_wiki_title"),
        "subject": ("subject", "subj"),
        "relation": ("relation", "property", "prop"),
    }
    for target, names in fields.items():
        value = str(_first(row, *names)).strip()
        if value:
            result[target] = value
    if golds:
        result["gold_answers"] = golds
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", help="Optional qid list; output follows this exact order")
    args = parser.parse_args()

    rows = [_normalize(row) for row in _load(Path(args.input))]
    by_qid: dict[str, dict[str, object]] = {}
    for row in rows:
        qid = str(row["qid"])
        if qid in by_qid:
            raise ValueError(f"Duplicate qid in source: {qid}")
        by_qid[qid] = row
    if args.manifest:
        qids = [
            line.strip() for line in Path(args.manifest).read_text().splitlines() if line.strip()
        ]
        if len(qids) != len(set(qids)):
            raise ValueError("Manifest contains duplicate qids")
        missing = [qid for qid in qids if qid not in by_qid]
        if missing:
            raise ValueError(f"Source is missing {len(missing)} manifest qids")
        rows = [by_qid[qid] for qid in qids]

    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"count": len(rows), "output": str(target)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
