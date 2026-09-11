# UER-RAG

Reference implementation for **Unified Entity-Relation Adaptive RAG (UER-RAG)**,
a risk-controlled answer-replacement pipeline for long-tail entity question
answering.

UER-RAG keeps a direct short answer as a protected fallback. It retrieves with
both an answer-free entity-relation query and an answer-conditioned query,
combines the rankings with reciprocal rank fusion (RRF), requests a structured
evidence record from a verifier, and changes the answer only when six
deterministic checks all pass.

## Method at a glance

1. Generate or load a concise direct answer `d`.
2. Build `q0` from the question plus observable entity/relation fields.
3. Build `q1` by adding `d` as an explicitly untrusted lexical clue.
4. Retrieve both rankings and fuse them with RRF (`k=20`).
5. Ask a verifier for `(e, support, utility, cited_docs, reason)`.
6. Adopt `e` only if it is non-empty, helpful, sufficiently supported, grounded
   in cited evidence, grounded to the target subject, and different from `d`.

The implementation never branches on a dataset name.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Copy `.env.example` to your own environment configuration. Never commit keys.
The runner expects an OpenAI-compatible chat-completions endpoint and an
Elasticsearch index containing `title` and `text` fields.

## Input format

One JSON object per line:

```json
{"qid":"1788652","question":"In what city was Louis Renault born?","entity":"Louis Renault (jurist)","subject":"Louis Renault","relation":"place of birth","gold_answers":["Autun"]}
```

Only `qid` and `question` are required. Entity, subject, and relation are
observable metadata; the generic branch uses the question when they are absent.

## Run

```bash
uer-rag run \
  --input examples/input.jsonl \
  --output outputs/predictions.jsonl \
  --config configs/default.yaml
```

The output is append-only JSONL. Re-running the same command resumes by `qid`.
No API key is written to logs.

## Offline evaluation

```bash
uer-rag evaluate \
  --prediction outputs/predictions.jsonl \
  --prediction-field final_answer \
  --direct-field direct_answer
```

The evaluator reports exact match (EM), normalized complete-word-boundary
containment Accuracy, token F1, paired gain, and harm rate over all gold aliases.
It performs no model or retrieval calls.

## Frozen paper protocol

| Dataset/scope | n | Direct F1 | UER-RAG F1 | Harm rate |
|---|---:|---:|---:|---:|
| PopQA complete collection (includes 1,000 development examples) | 14,267 | 42.77 | 69.82 | 1.07 |
| PopQA development-disjoint test | 13,267 | 42.90 | 70.31 | 1.06 |
| EntityQuestions frozen test | 5,000 | 48.07 | 59.57 | 2.76 |

The complete PopQA result is descriptive because it includes the development
portion. Use `manifests/` to reconstruct the exact reported splits from the
original benchmark releases. This repository intentionally excludes retrieved
Wikipedia passages and model outputs containing corpus text.

## Reproduce figures

```bash
python analysis/build_figures.py
```

Editable SVG, vector PDF, and 400-dpi PNG files are written to
`analysis/output/`.

## Tests

```bash
pytest
```

## Repository status

This directory is ready to initialize and push to a public GitHub repository.
Replace the repository URL in `CITATION.cff` and the manuscript before release.

## License

Code is released under the MIT License. Benchmark datasets, Wikipedia indexes,
model outputs, and third-party APIs retain their original terms.
