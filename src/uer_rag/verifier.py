"""OpenAI-compatible direct generation and structured evidence verification."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

import requests

from .retrieval import Passage

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", flags=re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_answer: str
    support_level: str
    evidence_utility: str
    supporting_doc_ids: tuple[int, ...]
    reason: str
    json_valid: bool = True
    raw: str = ""

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["supporting_doc_ids"] = list(self.supporting_doc_ids)
        return value


def _extract_json(text: str) -> Mapping[str, object]:
    candidate = text.strip()
    fenced = _FENCE.search(candidate)
    if fenced:
        candidate = fenced.group(1).strip()
    start, end = candidate.find("{"), candidate.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Verifier response contains no JSON object")
    value = json.loads(candidate[start : end + 1])
    if not isinstance(value, dict):
        raise TypeError("Verifier JSON must be an object")
    return value


class CompatibleChatClient:
    """Small dependency-light client for OpenAI-compatible chat completions."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0,
        timeout_seconds: float = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> CompatibleChatClient:
        base_env = str(config.get("base_url_env", "OPENAI_BASE_URL"))
        key_env = str(config.get("api_key_env", "OPENAI_API_KEY"))
        model_env = str(config.get("model_env", "UER_RAG_MODEL"))
        base_url = os.environ.get(base_env, "")
        api_key = os.environ.get(key_env, "")
        model = os.environ.get(model_env, "")
        if not base_url or not api_key or not model:
            raise RuntimeError(f"Set {base_env}, {key_env}, and {model_env}")
        return cls(
            base_url=base_url,
            api_key=api_key,
            model=model,
            temperature=float(config.get("temperature", 0)),
            timeout_seconds=float(config.get("timeout_seconds", 120)),
        )

    def complete(self, messages: Sequence[Mapping[str, str]], *, json_mode: bool = False) -> str:
        payload: dict[str, object] = {
            "model": self.model,
            "messages": list(messages),
            "temperature": self.temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"] or "")

    def direct_answer(self, question: str) -> str:
        text = self.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "Answer the factual question with only the shortest sufficient answer. "
                        "Do not explain and do not repeat the question."
                    ),
                },
                {"role": "user", "content": question},
            ]
        )
        return text.strip()

    def verify(
        self,
        *,
        question: str,
        direct_answer: str,
        subject: str,
        relation: str,
        passages: Sequence[Passage],
        max_reason_chars: int = 320,
    ) -> EvidenceRecord:
        evidence = "\n\n".join(
            f"Document {index}\nTitle: {passage.title}\nText: {passage.text}"
            for index, passage in enumerate(passages, start=1)
        )
        user = f"""Question: {question}
Target subject: {subject or '[not supplied]'}
Target relation: {relation or '[not supplied]'}
Untrusted direct answer: {direct_answer or '[empty]'}

Retrieved evidence:
{evidence}

Return exactly one JSON object with these keys:
- evidence_answer: shortest answer supported by the cited documents, or "".
- support_level: one of high, medium, low, none.
- evidence_utility: one of helpful, harmful, neutral, insufficient.
- supporting_doc_ids: a list containing only document numbers that directly support the answer.
- reason: a concise reason no longer than {max_reason_chars} characters.

Rules: judge only the cited evidence; resolve namesakes and the requested relation;
do not copy the untrusted direct answer unless the documents independently support it;
return an empty evidence_answer for missing, conflicting, off-subject, or relation-incompatible evidence."""
        raw = self.complete(
            [
                {
                    "role": "system",
                    "content": "You are a strict evidence verifier. Output valid JSON only.",
                },
                {"role": "user", "content": user},
            ],
            json_mode=True,
        )
        try:
            value = _extract_json(raw)
            doc_ids = tuple(
                sorted(
                    {
                        int(item)
                        for item in value.get("supporting_doc_ids", [])
                        if str(item).isdigit() and 1 <= int(item) <= len(passages)
                    }
                )
            )
            return EvidenceRecord(
                evidence_answer=str(value.get("evidence_answer", "")).strip(),
                support_level=str(value.get("support_level", "none")).strip().lower(),
                evidence_utility=str(value.get("evidence_utility", "insufficient"))
                .strip()
                .lower(),
                supporting_doc_ids=doc_ids,
                reason=str(value.get("reason", ""))[:max_reason_chars],
                json_valid=True,
                raw=raw,
            )
        except (ValueError, TypeError, json.JSONDecodeError):
            return EvidenceRecord(
                evidence_answer="",
                support_level="none",
                evidence_utility="insufficient",
                supporting_doc_ids=(),
                reason="invalid_verifier_json",
                json_valid=False,
                raw=raw,
            )

    def rescue_answer(self, question: str, passages: Sequence[Passage]) -> str:
        evidence = "\n\n".join(
            f"Document {index}: {p.title}\n{p.text}" for index, p in enumerate(passages, 1)
        )
        text = self.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "Return only the shortest answer directly supported by the documents. "
                        "Return an empty string if they do not answer the question."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\n\n{evidence}"},
            ]
        )
        return text.strip()
