from uer_rag.postaudit import canonicalize_short_answer, post_audit
from uer_rag.retrieval import Passage
from uer_rag.verifier import EvidenceRecord


def _record(answer="Autun", ids=(1,)):
    return EvidenceRecord(
        evidence_answer=answer,
        support_level="high",
        evidence_utility="helpful",
        supporting_doc_ids=ids,
        reason="supported",
    )


def test_direct_preserving_guard_rejects_unnecessary_answer_expansion():
    audit = post_audit(
        row={"entity": "Kyoto Animation", "relation": "headquarters location"},
        question="Where is the headquarters of Kyoto Animation?",
        direct_answer="Uji",
        proposed_answer="Uji, Kyoto Prefecture, Japan",
        selected_source="evidence",
        record=_record("Uji, Kyoto Prefecture, Japan"),
        passages=[Passage("Kyoto Animation", "Kyoto Animation is headquartered in Uji.")],
    )
    assert audit.final_answer == "Uji"
    assert audit.selected_source == "direct"
    assert audit.safety_guard_applied
    assert audit.safety_guard_reason == "direct_is_shorter_supported_form"


def test_disambiguated_title_mismatch_restores_direct_answer():
    audit = post_audit(
        row={"s_wiki_title": "Waves (Charles Lloyd album)", "prop": "genre"},
        question="What genre is Waves?",
        direct_answer="Drama",
        proposed_answer="folk-rock",
        selected_source="evidence",
        record=_record("folk-rock"),
        passages=[Passage("Waves (Waves album)", "Waves was made by a folk-rock band.")],
    )
    assert audit.final_answer == "Drama"
    assert audit.safety_guard_reason == "disambiguated_entity_title_mismatch"


def test_country_relation_guard_rejects_non_country_replacement():
    audit = post_audit(
        row={"entity": "Zuster Theresia", "relation": "country of origin"},
        question="Which country was Zuster Theresia created in?",
        direct_answer="Netherlands",
        proposed_answer="Dutch East Indies",
        selected_source="evidence",
        record=_record("Dutch East Indies"),
        passages=[Passage("Zuster Theresia", "The film was made in the Dutch East Indies.")],
    )
    assert audit.final_answer == "Netherlands"
    assert audit.relation_guard_applied
    assert audit.relation_guard_reason == "country_type_mismatch"


def test_short_answer_canonicalizer_replays_frozen_rules():
    assert (
        canonicalize_short_answer("What is Alice's occupation?", "singer and pianist") == "singer"
    )
    assert (
        canonicalize_short_answer("What genre is Enter?", "symphonic/gothic metal") == "symphonic"
    )
