"""Command-line interface for running and evaluating UER-RAG."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

import yaml

from .io import append_jsonl, completed_qids, latest_rows_by_qid, read_jsonl
from .metrics import summarize_paired
from .pipeline import Pipeline
from .retrieval import ElasticsearchRetriever
from .verifier import CompatibleChatClient


def _load_config(path: str | Path) -> dict[str, object]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise TypeError("Configuration root must be a mapping")
    return value


def run_command(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    model_config = config.get("model", {})
    retrieval_config = config.get("retrieval", {})
    verification_config = config.get("verification", {})
    run_config = config.get("run", {})
    sections = [model_config, retrieval_config, verification_config, run_config]
    if not all(isinstance(item, dict) for item in sections):
        raise ValueError("model, retrieval, verification, and run must be mappings")

    pipeline = Pipeline(
        client=CompatibleChatClient.from_config(model_config),
        retriever=ElasticsearchRetriever.from_config(retrieval_config),
        retrieval_config=retrieval_config,
        verification_config=verification_config,
        allow_rescue=bool(run_config.get("allow_rescue", True)),
    )
    done = completed_qids(args.output)
    processed = skipped = failed = 0
    for row in read_jsonl(args.input):
        qid = str(row.get("qid", "")).strip()
        question = str(row.get("question", "")).strip()
        if not qid or not question:
            raise ValueError("Every input row requires non-empty qid and question")
        if qid in done:
            skipped += 1
            continue
        try:
            result = pipeline.run_one(row)
        # Preserve transport, parsing, and retrieval failures in the append-only
        # log so each qid remains auditable and retryable.
        except Exception as exc:  # noqa: BLE001
            result = {
                **row,
                "qid": qid,
                "final_answer": str(row.get("direct_answer", "")),
                "call_error": f"{type(exc).__name__}: {exc}",
                "interrupted": False,
            }
            failed += 1
        append_jsonl(args.output, [result])
        if not result.get("call_error") and not result.get("interrupted"):
            done.add(qid)
        processed += 1
        if args.limit and processed >= args.limit:
            break
    print(json.dumps({"processed": processed, "resumed": skipped, "failed": failed}))
    return int(failed > 0)


def evaluate_command(args: argparse.Namespace) -> int:
    rows, superseded = latest_rows_by_qid(read_jsonl(args.prediction))
    incomplete = [
        str(row.get("qid", "")) for row in rows if row.get("call_error") or row.get("interrupted")
    ]
    if incomplete and not args.allow_incomplete:
        preview = ", ".join(incomplete[:5])
        raise ValueError(
            f"Refusing to score {len(incomplete)} incomplete qids"
            f" ({preview}). Re-run the pipeline or pass --allow-incomplete explicitly."
        )
    if args.reference:
        references = {}
        for row in read_jsonl(args.reference):
            qid = str(row.get("qid", "")).strip()
            if not qid:
                raise ValueError("Every reference row requires a non-empty qid")
            if qid in references:
                raise ValueError(f"Duplicate reference qid: {qid}")
            references[qid] = list(row.get("gold_answers") or [])
        missing = []
        for row in rows:
            qid = str(row.get("qid", ""))
            if qid not in references or not references[qid]:
                missing.append(qid)
            else:
                # The reference file is authoritative because prediction logs
                # may retain only a subset of accepted aliases.
                row["gold_answers"] = references[qid]
        if missing:
            raise ValueError(f"Missing gold answers for {len(missing)} qids")
    if any(not row.get("gold_answers") for row in rows):
        raise ValueError("gold_answers must be present in predictions or supplied by --reference")
    summary = summarize_paired(
        rows,
        direct_field=args.direct_field,
        final_field=args.prediction_field,
    )
    result = summary.to_dict()
    result["evaluation_audit"] = {
        "unique_qids": len(rows),
        "superseded_retry_rows": superseded,
        "incomplete_qids": len(incomplete),
        "incomplete_included": bool(incomplete and args.allow_incomplete),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uer-rag")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run or resume the UER-RAG pipeline")
    run.add_argument("--input", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--config", default="configs/default.yaml")
    run.add_argument("--limit", type=int, default=0)
    run.set_defaults(func=run_command)

    evaluate = subparsers.add_parser("evaluate", help="Evaluate saved JSONL offline")
    evaluate.add_argument("--prediction", required=True)
    evaluate.add_argument("--reference")
    evaluate.add_argument("--prediction-field", default="final_answer")
    evaluate.add_argument("--direct-field", default="direct_answer")
    evaluate.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Explicitly include latest call_error/interrupted rows in scoring",
    )
    evaluate.set_defaults(func=evaluate_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
