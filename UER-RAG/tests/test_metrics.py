from uer_rag.metrics import containment_accuracy, exact_match, summarize_paired, token_f1


def test_short_answer_metrics_distinguish_strict_and_partial_credit():
    golds = ["New York City"]
    assert exact_match("New York City", golds) == 1.0
    assert exact_match("The answer is New York City", golds) == 0.0
    assert containment_accuracy("The answer is New York City", golds) == 1.0
    assert token_f1("New York", golds) == 0.8


def test_paired_harm_uses_all_examples_as_denominator():
    rows = [
        {"gold_answers": ["Autun"], "direct_answer": "Paris", "final_answer": "Autun"},
        {"gold_answers": ["Paris"], "direct_answer": "Paris", "final_answer": "France"},
        {"gold_answers": ["Rome"], "direct_answer": "Rome", "final_answer": "Rome"},
    ]
    summary = summarize_paired(rows)
    assert summary.improved == 1
    assert summary.harmed == 1
    assert summary.unchanged == 1
    assert summary.harm_rate == 1 / 3
