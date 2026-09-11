"""Deterministic six-check answer-adoption gate."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

from .normalize import contains_complete_words, normalize_answer
from .retrieval import Passage
from .verifier import EvidenceRecord


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    checks: Mapping[str, bool]
    selected_source: str
    final_answer: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _cited(passages: Sequence[Passage], ids: Sequence[int]) -> list[Passage]:
    return [passages[index - 1] for index in ids if 1 <= index <= len(passages)]


def _grounded(value: str, passages: Sequence[Passage]) -> bool:
    return bool(value and any(contains_complete_words(f"{p.title} {p.text}", value) for p in passages))


def decide(
    *,
    direct_answer: str,
    subject: str,
    entity: str,
    record: EvidenceRecord,
    passages: Sequence[Passage],
    support_allowed: Sequence[str] = ("high", "medium"),
    utility_required: str = "helpful",
) -> GateDecision:
    cited = _cited(passages, record.supporting_doc_ids)
    target = subject or entity
    checks = {
        "nonempty_answer": bool(normalize_answer(record.evidence_answer)),
        "utility_helpful": record.evidence_utility == utility_required,
        "support_high_or_medium": record.support_level in set(support_allowed),
        "answer_grounded_in_cited_doc": _grounded(record.evidence_answer, cited),
        "subject_grounded_in_cited_doc": _grounded(target, cited),
        "different_from_direct": (
            bool(normalize_answer(record.evidence_answer))
            and normalize_answer(record.evidence_answer) != normalize_answer(direct_answer)
        ),
    }
    passed = all(checks.values())
    return GateDecision(
        passed=passed,
        checks=checks,
        selected_source="evidence" if passed else "direct",
        final_answer=record.evidence_answer if passed else direct_answer,
    )
