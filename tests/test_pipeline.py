from uer_rag.pipeline import Pipeline
from uer_rag.retrieval import Passage
from uer_rag.verifier import EvidenceRecord


class FakeRetriever:
    def __init__(self):
        self.queries = []

    def search(self, query, size):
        self.queries.append(query)
        return [Passage("Louis Renault (jurist)", "Louis Renault was born at Autun.")]


class FakeClient:
    model = "fake-model"

    def __init__(self, direct="Paris", evidence="Autun"):
        self.direct = direct
        self.evidence = evidence

    def direct_answer(self, question):
        return self.direct

    def verify(self, **_kwargs):
        return EvidenceRecord(
            evidence_answer=self.evidence,
            support_level="high" if self.evidence else "none",
            evidence_utility="helpful" if self.evidence else "insufficient",
            supporting_doc_ids=(1,) if self.evidence else (),
            reason="supported" if self.evidence else "missing",
        )

    def rescue_answer(self, question, passages):
        return "Autun"


def _pipeline(client, retriever):
    return Pipeline(
        client=client,
        retriever=retriever,
        retrieval_config={"retrieve_k": 50, "top_k": 3, "rrf_k": 20},
        verification_config={"support_allowed": ["high", "medium"], "utility_required": "helpful"},
    )


def test_pipeline_persists_post_audit_and_dynamic_query_metadata():
    retriever = FakeRetriever()
    result = _pipeline(FakeClient(), retriever).run_one(
        {
            "qid": "1788652",
            "question": "In what city was Louis Renault born?",
            "entity": "Louis Renault (jurist)",
            "subject": "Louis Renault",
            "relation": "place of birth",
        }
    )
    assert result["final_answer"] == "Autun"
    assert result["post_audit"]["final_answer"] == "Autun"
    assert result["retrieval_query_info"]["direct_answer_conditioned_retrieval"]
    assert len(result["retrieval_query_info"]["query_variants"]) == 2


def test_empty_direct_uses_one_retrieval_view_and_rescue():
    retriever = FakeRetriever()
    result = _pipeline(FakeClient(direct="", evidence=""), retriever).run_one(
        {"qid": "q-empty", "question": "In what city was Louis Renault born?"}
    )
    assert result["final_answer"] == "Autun"
    assert result["router_decision"]["selected_source"] == "rescue"
    assert not result["retrieval_query_info"]["direct_answer_conditioned_retrieval"]
    assert len(retriever.queries) == 1
