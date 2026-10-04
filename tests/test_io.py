import json
from pathlib import Path
from tempfile import TemporaryDirectory

from uer_rag.io import completed_qids, latest_rows_by_qid


def test_call_error_row_remains_retryable():
    with TemporaryDirectory() as directory:
        output = Path(directory) / "predictions.jsonl"
        output.write_text(
            json.dumps({"qid": "failed", "call_error": "TimeoutError"})
            + "\n"
            + json.dumps({"qid": "done", "final_answer": "Autun"})
            + "\n",
            encoding="utf-8",
        )
        assert completed_qids(output) == {"done"}


def test_latest_success_supersedes_an_earlier_error():
    rows, superseded = latest_rows_by_qid(
        [
            {"qid": "q1", "call_error": "TimeoutError"},
            {"qid": "q1", "final_answer": "Autun"},
            {"qid": "q2", "final_answer": "Paris"},
        ]
    )
    assert superseded == 1
    assert {row["qid"] for row in rows} == {"q1", "q2"}
    assert next(row for row in rows if row["qid"] == "q1")["final_answer"] == "Autun"


def test_latest_error_after_success_remains_retryable():
    with TemporaryDirectory() as directory:
        output = Path(directory) / "predictions.jsonl"
        output.write_text(
            json.dumps({"qid": "q1", "final_answer": "Autun"})
            + "\n"
            + json.dumps({"qid": "q1", "call_error": "TimeoutError"})
            + "\n",
            encoding="utf-8",
        )
        assert completed_qids(output) == set()
