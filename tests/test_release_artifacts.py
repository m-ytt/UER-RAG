import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _qid_manifest(name):
    path = ROOT / "manifests" / name
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_frozen_manifests_have_expected_sizes_and_are_disjoint():
    development = _qid_manifest("popqa_dev1000_qids.txt")
    test = _qid_manifest("popqa_test13267_qids.txt")
    entityquestions = _qid_manifest("entityquestions_test5000_qids.txt")
    assert len(development) == len(set(development)) == 1000
    assert len(test) == len(set(test)) == 13267
    assert len(entityquestions) == len(set(entityquestions)) == 5000
    assert set(development).isdisjoint(test)


def test_result_counts_and_figure_source_are_internally_consistent():
    paper = json.loads((ROOT / "results" / "paper_metrics.json").read_text())
    figures = json.loads((ROOT / "results" / "figure_statistics.json").read_text())
    pairs = [
        ("popqa_complete_14267", 14267),
        ("entityquestions_test_5000", 5000),
    ]
    for name, count in pairs:
        result = paper[name]
        assert result["improved"] + result["harmed"] + result["unchanged"] == count
        expected = [
            round(100 * result["uer_rag"][metric], 2) for metric in ("em", "accuracy", "f1")
        ]
        assert figures["benchmarks"][name][-1] == expected

    split = figures["popqa_split_sensitivity"]
    complete = paper["popqa_complete_14267"]
    disjoint = paper["popqa_disjoint_13267"]
    assert split["direct_pct"] == [
        *[round(100 * complete["direct"][metric], 2) for metric in ("em", "accuracy", "f1")],
        *[round(100 * disjoint["direct"][metric], 2) for metric in ("em", "accuracy", "f1")],
    ]
    assert split["uer_rag_pct"] == [
        *[round(100 * complete["uer_rag"][metric], 2) for metric in ("em", "accuracy", "f1")],
        *[round(100 * disjoint["uer_rag"][metric], 2) for metric in ("em", "accuracy", "f1")],
    ]


def test_release_contains_no_unsupported_cross_model_result():
    paper_text = (ROOT / "results" / "paper_metrics.json").read_text(encoding="utf-8")
    figure_text = (ROOT / "results" / "figure_statistics.json").read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "GPT-4o" not in paper_text + figure_text + readme_text
    assert "cross_model_2000" not in paper_text + figure_text


def test_all_24_relation_level_f1_gains_are_positive():
    with (ROOT / "analysis" / "data" / "relation_results.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 24
    assert all(float(row["f1_gain"]) > 0 for row in rows)
