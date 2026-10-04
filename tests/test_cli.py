import argparse
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from uer_rag.cli import evaluate_command


def _args(path: Path, *, allow_incomplete=False):
    return argparse.Namespace(
        prediction=str(path),
        reference=None,
        direct_field="direct_answer",
        prediction_field="final_answer",
        allow_incomplete=allow_incomplete,
    )


def test_evaluator_rejects_incomplete_latest_rows_by_default():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "predictions.jsonl"
        path.write_text(
            json.dumps(
                {
                    "qid": "q1",
                    "gold_answers": ["Autun"],
                    "direct_answer": "Paris",
                    "final_answer": "Paris",
                    "call_error": "TimeoutError",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            evaluate_command(_args(path))
        except ValueError as exc:
            assert "Refusing to score" in str(exc)
        else:
            raise AssertionError("incomplete predictions must not be scored silently")


def test_evaluator_uses_latest_success_after_retry():
    with TemporaryDirectory() as directory:
        path = Path(directory) / "predictions.jsonl"
        rows = [
            {
                "qid": "q1",
                "gold_answers": ["Autun"],
                "direct_answer": "Paris",
                "final_answer": "Paris",
                "call_error": "TimeoutError",
            },
            {
                "qid": "q1",
                "gold_answers": ["Autun"],
                "direct_answer": "Paris",
                "final_answer": "Autun",
            },
        ]
        path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows),
            encoding="utf-8",
        )
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            assert evaluate_command(_args(path)) == 0
        result = json.loads(buffer.getvalue())
        assert result["count"] == 1
        assert result["final"]["f1"] == 1.0
        assert result["evaluation_audit"]["superseded_retry_rows"] == 1
