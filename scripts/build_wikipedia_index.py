#!/usr/bin/env python3
"""Build the deterministic Elasticsearch schema expected by UER-RAG.

The script accepts a legally obtained, pre-segmented JSONL corpus.  Every row
must contain ``title`` and either ``text`` or ``paragraph_text``.  It does not
download or redistribute Wikipedia.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Iterable
from pathlib import Path

import requests


def _validated_index(value: str) -> str:
    index = value.strip()
    if not index or index in {"_all", "*"} or any(token in index for token in (",", " ")):
        raise ValueError("Use one explicit Elasticsearch index name")
    return index


def _rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            title = str(value.get("title", "")).strip()
            text = str(value.get("text") or value.get("paragraph_text") or "").strip()
            if not title or not text:
                raise ValueError(f"{path}:{number}: missing title/text")
            supplied_id = str(value.get("id") or value.get("doc_id") or "").strip()
            digest = hashlib.sha256(f"{title}\n{text}".encode()).hexdigest()
            yield {"_id": supplied_id or digest, "title": title, "text": text}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--url", default=os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    )
    parser.add_argument("--index", default=os.environ.get("UER_RAG_INDEX", "wikipedia"))
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--recreate", action="store_true")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    index = _validated_index(args.index)
    auth = None
    if os.environ.get("ELASTICSEARCH_USERNAME"):
        auth = (
            os.environ["ELASTICSEARCH_USERNAME"],
            os.environ.get("ELASTICSEARCH_PASSWORD", ""),
        )
    common = {"timeout": 120, "auth": auth}

    exists = requests.head(f"{base}/{index}", **common).status_code == 200
    if exists and args.recreate:
        response = requests.delete(f"{base}/{index}", **common)
        response.raise_for_status()
        exists = False
    if not exists:
        response = requests.put(
            f"{base}/{index}",
            json={
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "text": {"type": "text", "analyzer": "standard"},
                    }
                },
            },
            **common,
        )
        response.raise_for_status()

    indexed = 0
    batch: list[dict[str, str]] = []

    def flush() -> None:
        nonlocal indexed
        if not batch:
            return
        lines = []
        for row in batch:
            lines.append(json.dumps({"index": {"_index": index, "_id": row["_id"]}}))
            lines.append(
                json.dumps({"title": row["title"], "text": row["text"]}, ensure_ascii=False)
            )
        response = requests.post(
            f"{base}/_bulk",
            data="\n".join(lines) + "\n",
            headers={"Content-Type": "application/x-ndjson"},
            **common,
        )
        response.raise_for_status()
        value = response.json()
        if value.get("errors"):
            failures = [
                item for item in value.get("items", []) if item.get("index", {}).get("error")
            ]
            raise RuntimeError(f"Elasticsearch bulk indexing failed for {len(failures)} rows")
        indexed += len(batch)
        batch.clear()

    for row in _rows(Path(args.input)):
        batch.append(row)
        if len(batch) >= args.batch_size:
            flush()
    flush()
    response = requests.post(f"{base}/{index}/_refresh", **common)
    response.raise_for_status()
    print(json.dumps({"index": index, "indexed": indexed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
