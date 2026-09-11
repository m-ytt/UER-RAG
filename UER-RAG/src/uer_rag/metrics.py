"""Offline EM, containment Accuracy, token F1, and paired risk metrics."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass

from .normalize import contains_complete_words, normalize_answer, normalized_tokens


def exact_match(prediction: object, golds: Sequence[object]) -> float:
    pred = normalize_answer(prediction)
    return float(any(pred == normalize_answer(gold) for gold in golds))


def containment_accuracy(prediction: object, golds: Sequence[object]) -> float:
    return float(any(contains_complete_words(prediction, gold) for gold in golds))


def _single_token_f1(prediction: object, gold: object) -> float:
    pred_tokens = normalized_tokens(prediction)
    gold_tokens = normalized_tokens(gold)
    if not pred_tokens or not gold_tokens:
        return float(pred_tokens == gold_tokens)
    overlap = sum((Counter(pred_tokens) & Counter(gold_tokens)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def token_f1(prediction: object, golds: Sequence[object]) -> float:
    return max((_single_token_f1(prediction, gold) for gold in golds), default=0.0)


@dataclass(frozen=True)
class MetricSummary:
    count: int
    em: float
    accuracy: float
    f1: float


@dataclass(frozen=True)
class PairedSummary:
    count: int
    direct: MetricSummary
    final: MetricSummary
    em_gain: float
    accuracy_gain: float
    f1_gain: float
    improved: int
    harmed: int
    unchanged: int
    harm_rate: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def summarize(rows: Sequence[Mapping[str, object]], field: str) -> MetricSummary:
    scores = []
    for row in rows:
        golds = list(row.get("gold_answers") or [])
        prediction = row.get(field, "")
        scores.append(
            (
                exact_match(prediction, golds),
                containment_accuracy(prediction, golds),
                token_f1(prediction, golds),
            )
        )
    return MetricSummary(
        count=len(scores),
        em=_mean(score[0] for score in scores),
        accuracy=_mean(score[1] for score in scores),
        f1=_mean(score[2] for score in scores),
    )


def summarize_paired(
    rows: Sequence[Mapping[str, object]],
    *,
    direct_field: str = "direct_answer",
    final_field: str = "final_answer",
) -> PairedSummary:
    direct = summarize(rows, direct_field)
    final = summarize(rows, final_field)
    improved = harmed = unchanged = 0
    for row in rows:
        golds = list(row.get("gold_answers") or [])
        before = token_f1(row.get(direct_field, ""), golds)
        after = token_f1(row.get(final_field, ""), golds)
        if after > before:
            improved += 1
        elif after < before:
            harmed += 1
        else:
            unchanged += 1
    return PairedSummary(
        count=len(rows),
        direct=direct,
        final=final,
        em_gain=final.em - direct.em,
        accuracy_gain=final.accuracy - direct.accuracy,
        f1_gain=final.f1 - direct.f1,
        improved=improved,
        harmed=harmed,
        unchanged=unchanged,
        harm_rate=harmed / len(rows) if rows else 0.0,
    )
