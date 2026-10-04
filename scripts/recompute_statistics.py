#!/usr/bin/env python3
"""Recompute paired metrics, bootstrap intervals, and exact sign tests."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from uer_rag.io import latest_rows_by_qid, read_jsonl
from uer_rag.metrics import containment_accuracy, exact_match, token_f1


def _attach_references(rows: list[dict[str, object]], path: str | None) -> None:
    if not path:
        return
    references: dict[str, list[object]] = {}
    for row in read_jsonl(path):
        qid = str(row.get("qid", "")).strip()
        if not qid or qid in references:
            raise ValueError(f"Invalid or duplicate reference qid: {qid!r}")
        references[qid] = list(row.get("gold_answers") or [])
    missing = []
    for row in rows:
        qid = str(row["qid"])
        if qid not in references or not references[qid]:
            missing.append(qid)
        else:
            row["gold_answers"] = references[qid]
    if missing:
        raise ValueError(f"Missing gold answers for {len(missing)} qids")


def _score_arrays(
    rows: list[dict[str, object]], direct_field: str, final_field: str
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    values: dict[str, tuple[list[float], list[float]]] = {
        "em": ([], []),
        "accuracy": ([], []),
        "f1": ([], []),
    }
    functions = {
        "em": exact_match,
        "accuracy": containment_accuracy,
        "f1": token_f1,
    }
    for row in rows:
        golds = list(row.get("gold_answers") or [])
        if not golds:
            raise ValueError(f"Missing gold_answers for qid={row.get('qid')}")
        for name, function in functions.items():
            before, after = values[name]
            before.append(function(row.get(direct_field, ""), golds))
            after.append(function(row.get(final_field, ""), golds))
    return {
        name: (np.asarray(before, dtype=float), np.asarray(after, dtype=float))
        for name, (before, after) in values.items()
    }


def _bootstrap_interval(
    differences: np.ndarray,
    *,
    resamples: int,
    seed: int,
    confidence: float = 0.95,
    batch_size: int = 250,
) -> tuple[float, float]:
    if differences.size == 0:
        return 0.0, 0.0
    rng = np.random.default_rng(seed)
    means = np.empty(resamples, dtype=float)
    for start in range(0, resamples, batch_size):
        width = min(batch_size, resamples - start)
        indices = rng.integers(0, differences.size, size=(width, differences.size))
        means[start : start + width] = differences[indices].mean(axis=1)
    tail = (1.0 - confidence) / 2.0
    low, high = np.quantile(means, [tail, 1.0 - tail])
    return float(low), float(high)


def _exact_sign_pvalue(better: int, worse: int) -> float:
    n = better + worse
    if n == 0:
        return 1.0
    k = min(better, worse)
    logs = [
        math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2)
        for i in range(k + 1)
    ]
    maximum = max(logs)
    lower_tail = math.exp(maximum) * sum(math.exp(value - maximum) for value in logs)
    return min(1.0, 2.0 * lower_tail)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", required=True)
    parser.add_argument("--reference")
    parser.add_argument("--direct-field", default="direct_answer")
    parser.add_argument("--prediction-field", default="final_answer")
    parser.add_argument("--resamples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument("--output")
    args = parser.parse_args()

    rows, superseded = latest_rows_by_qid(read_jsonl(args.prediction))
    incomplete = [
        str(row["qid"]) for row in rows if row.get("call_error") or row.get("interrupted")
    ]
    if incomplete:
        raise ValueError(f"Refusing to analyse {len(incomplete)} incomplete qids")
    _attach_references(rows, args.reference)
    arrays = _score_arrays(rows, args.direct_field, args.prediction_field)

    metrics = {}
    for offset, (name, (before, after)) in enumerate(arrays.items()):
        differences = after - before
        better = int(np.count_nonzero(differences > 0))
        worse = int(np.count_nonzero(differences < 0))
        interval = _bootstrap_interval(
            differences,
            resamples=args.resamples,
            seed=args.seed + offset,
        )
        metrics[name] = {
            "direct": float(before.mean()),
            "final": float(after.mean()),
            "gain": float(differences.mean()),
            "gain_95ci": list(interval),
            "better": better,
            "worse": worse,
            "unchanged": int(differences.size - better - worse),
            "two_sided_exact_sign_p": _exact_sign_pvalue(better, worse),
        }

    result = {
        "count": len(rows),
        "superseded_retry_rows": superseded,
        "paired_resamples": args.resamples,
        "seed": args.seed,
        "metrics": metrics,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
