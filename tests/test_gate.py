from uer_rag.gate import decide
from uer_rag.retrieval import Passage
from uer_rag.verifier import EvidenceRecord


def _record(**changes):
    values = {
        "evidence_answer": "Autun",
        "support_level": "high",
        "evidence_utility": "helpful",
        "supporting_doc_ids": (1, 2),
        "reason": "supported",
    }
    values.update(changes)
    return EvidenceRecord(**values)


def test_louis_renault_worked_example_passes_all_checks():
    passages = [
        Passage("Louis Renault (jurist)", "Louis Renault was born at Autun."),
        Passage("Louis Renault", "The jurist Louis Renault was a native of Autun."),
    ]
    decision = decide(
        direct_answer="Paris",
        subject="Louis Renault",
        entity="Louis Renault (jurist)",
        record=_record(),
        passages=passages,
    )
    assert decision.passed
    assert decision.final_answer == "Autun"
    assert all(decision.checks.values())


def test_off_subject_evidence_is_rejected():
    passages = [Passage("Autun", "Autun is a city in France.")]
    decision = decide(
        direct_answer="Paris",
        subject="Louis Renault",
        entity="Louis Renault (jurist)",
        record=_record(supporting_doc_ids=(1,)),
        passages=passages,
    )
    assert not decision.passed
    assert decision.final_answer == "Paris"
    assert not decision.checks["subject_grounded_in_cited_doc"]
