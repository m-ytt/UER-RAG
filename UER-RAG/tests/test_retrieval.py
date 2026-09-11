from uer_rag.retrieval import Passage, build_queries, reciprocal_rank_fusion


def test_queries_do_not_use_dataset_name():
    row = {
        "question": "In what city was Louis Renault born?",
        "entity": "Louis Renault (jurist)",
        "relation": "place of birth",
        "dataset": "ignored",
    }
    q0, q1 = build_queries(row, "Paris")
    assert "ignored" not in q0
    assert "Paris" not in q0
    assert "Paris" in q1


def test_rrf_rewards_passages_found_by_both_queries():
    shared = Passage("Louis Renault", "Renault was born at Autun.")
    only_a = Passage("A", "A")
    only_b = Passage("B", "B")
    result = reciprocal_rank_fusion(
        {"answer_free": [shared, only_a], "answer_conditioned": [only_b, shared]},
        k=20,
        top_k=3,
    )
    assert result[0].title == "Louis Renault"
    assert result[0].query_sources == ("answer_conditioned", "answer_free")
