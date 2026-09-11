"""Dataset-name-independent UER-RAG execution pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .gate import decide
from .retrieval import ElasticsearchRetriever, dual_retrieve
from .verifier import CompatibleChatClient


@dataclass
class Pipeline:
    client: CompatibleChatClient
    retriever: ElasticsearchRetriever
    retrieval_config: Mapping[str, object]
    verification_config: Mapping[str, object]
    allow_rescue: bool = True

    def run_one(self, row: Mapping[str, object]) -> dict[str, object]:
        qid = str(row.get("qid", ""))
        question = str(row.get("question", "")).strip()
        if not qid or not question:
            raise ValueError("Every input row requires non-empty qid and question")

        direct_answer = str(row.get("direct_answer", "")).strip()
        direct_reused = bool(direct_answer)
        if not direct_answer:
            direct_answer = self.client.direct_answer(question)

        (q0, q1), passages = dual_retrieve(
            self.retriever,
            row,
            direct_answer,
            retrieve_k=int(self.retrieval_config.get("retrieve_k", 50)),
            top_k=int(self.retrieval_config.get("top_k", 3)),
            rrf_k=int(self.retrieval_config.get("rrf_k", 20)),
        )
        subject = str(row.get("subject") or row.get("subj") or "").strip()
        entity = str(
            row.get("entity") or row.get("entity_title") or row.get("s_wiki_title") or ""
        ).strip()
        relation = str(
            row.get("relation") or row.get("property") or row.get("prop") or ""
        ).strip()
        record = self.client.verify(
            question=question,
            direct_answer=direct_answer,
            subject=subject or entity,
            relation=relation,
            passages=passages,
            max_reason_chars=int(self.verification_config.get("max_reason_chars", 320)),
        )
        decision = decide(
            direct_answer=direct_answer,
            subject=subject,
            entity=entity,
            record=record,
            passages=passages,
            support_allowed=tuple(
                str(value).lower()
                for value in self.verification_config.get(
                    "support_allowed", ["high", "medium"]
                )
            ),
            utility_required=str(
                self.verification_config.get("utility_required", "helpful")
            ).lower(),
        )

        final_answer = decision.final_answer
        selected_source = decision.selected_source
        rescue_triggered = False
        if self.allow_rescue and not direct_answer and not record.evidence_answer:
            rescue_triggered = True
            rescued = self.client.rescue_answer(question, passages)
            if rescued:
                final_answer = rescued
                selected_source = "rescue"

        result = dict(row)
        result.update(
            {
                "qid": qid,
                "question": question,
                "direct_answer": direct_answer,
                "direct_reused": direct_reused,
                "retrieval_query_info": {
                    "query_variants": [
                        {"kind": "entity_relation", "query": q0},
                        {"kind": "entity_relation_plus_direct", "query": q1},
                    ],
                    "direct_answer_conditioned_retrieval": True,
                    "rrf_k": int(self.retrieval_config.get("rrf_k", 20)),
                    "dataset_conditioned_branch": False,
                },
                "retrieved_docs": [passage.to_dict() for passage in passages],
                "evidence_answer_info": record.to_dict(),
                "router_decision": {
                    **decision.to_dict(),
                    "selected_source": selected_source,
                    "final_answer": final_answer,
                    "dataset_conditioned": False,
                },
                "final_answer": final_answer,
                "rescue_triggered": rescue_triggered,
                "method_branch": "entity_relation" if (entity or subject or relation) else "generic",
                "dataset_conditioned_branch": False,
                "model_id": self.client.model,
            }
        )
        return result
