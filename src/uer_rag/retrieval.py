"""Field-adaptive dual retrieval and reciprocal rank fusion."""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from typing import Protocol

import requests

from .normalize import join_observable_fields, normalize_answer


@dataclass(frozen=True)
class Passage:
    title: str
    text: str
    score: float = 0.0
    rank: int = 0
    rrf_score: float = 0.0
    query_sources: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["query_sources"] = list(self.query_sources)
        return value


class Retriever(Protocol):
    def search(self, query: str, size: int) -> list[Passage]: ...


def build_queries(row: Mapping[str, object], direct_answer: str) -> tuple[str, str]:
    question = row.get("question", "")
    entity = row.get("entity") or row.get("entity_title") or row.get("s_wiki_title")
    subject = row.get("subject") or row.get("subj")
    relation = row.get("relation") or row.get("property") or row.get("prop")
    q0 = join_observable_fields(question, entity, subject, relation)
    q1 = join_observable_fields(q0, direct_answer)
    return q0, q1


def _passage_key(passage: Passage) -> tuple[str, str]:
    return normalize_answer(passage.title), normalize_answer(passage.text[:240])


def reciprocal_rank_fusion(
    rankings: Mapping[str, Iterable[Passage]], *, k: int = 20, top_k: int = 3
) -> list[Passage]:
    """Fuse named rankings without assuming comparable retriever scores."""

    totals: dict[tuple[str, str], float] = {}
    passages: dict[tuple[str, str], Passage] = {}
    sources: dict[tuple[str, str], set[str]] = {}
    for source, ranking in rankings.items():
        for rank, passage in enumerate(ranking, start=1):
            key = _passage_key(passage)
            totals[key] = totals.get(key, 0.0) + 1.0 / (k + rank)
            passages.setdefault(key, passage)
            sources.setdefault(key, set()).add(source)
    ordered = sorted(totals, key=lambda key: (-totals[key], key))[:top_k]
    return [
        Passage(
            title=passages[key].title,
            text=passages[key].text,
            score=passages[key].score,
            rank=index,
            rrf_score=totals[key],
            query_sources=tuple(sorted(sources[key])),
        )
        for index, key in enumerate(ordered, start=1)
    ]


class ElasticsearchRetriever:
    def __init__(
        self,
        *,
        base_url: str,
        index: str,
        title_field: str = "title",
        text_field: str = "text",
        timeout_seconds: float = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.index = index
        self.title_field = title_field
        self.text_field = text_field
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> ElasticsearchRetriever:
        url_env = str(config.get("elasticsearch_url_env", "ELASTICSEARCH_URL"))
        index_env = str(config.get("index_env", "UER_RAG_INDEX"))
        base_url = os.environ.get(url_env, "")
        index = os.environ.get(index_env, "")
        if not base_url or not index:
            raise RuntimeError(f"Set {url_env} and {index_env} before running retrieval")
        return cls(
            base_url=base_url,
            index=index,
            title_field=str(config.get("title_field", "title")),
            text_field=str(config.get("text_field", "text")),
            timeout_seconds=float(config.get("request_timeout_seconds", 60)),
        )

    def search(self, query: str, size: int) -> list[Passage]:
        payload = {
            "size": size,
            "_source": [self.title_field, self.text_field],
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [f"{self.title_field}^3", self.text_field],
                    "type": "best_fields",
                }
            },
        }
        response = requests.post(
            f"{self.base_url}/{self.index}/_search",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])
        result = []
        for rank, hit in enumerate(hits, start=1):
            source = hit.get("_source", {})
            result.append(
                Passage(
                    title=str(source.get(self.title_field, "")),
                    text=str(source.get(self.text_field, "")),
                    score=float(hit.get("_score") or 0.0),
                    rank=rank,
                )
            )
        return result


def dual_retrieve(
    retriever: Retriever,
    row: Mapping[str, object],
    direct_answer: str,
    *,
    retrieve_k: int = 50,
    top_k: int = 3,
    rrf_k: int = 20,
) -> tuple[tuple[str, str], list[Passage]]:
    q0, q1 = build_queries(row, direct_answer)
    rankings = {
        "answer_free": retriever.search(q0, retrieve_k),
        "answer_conditioned": retriever.search(q1, retrieve_k),
    }
    return (q0, q1), reciprocal_rank_fusion(rankings, k=rrf_k, top_k=top_k)
