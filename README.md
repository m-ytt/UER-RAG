# UER-RAG

Official implementation of **Unified Entity-Relation Adaptive RAG (UER-RAG)**,
a training-free framework for evidence-verified and risk-controlled answer
replacement in long-tail entity question answering.

Repository: <https://github.com/m-ytt/UER-RAG>

UER-RAG protects the initial short answer as a fallback. It constructs an
answer-free entity-relation query and, only when the direct answer is non-empty,
a second query that uses that answer as an explicitly untrusted lexical cue.
The retrieved rankings are deduplicated and combined by reciprocal rank fusion
(RRF). A structured verifier proposes a cited evidence answer; the replacement
is authorized only when all six deterministic checks pass. A final local
post-audit applies relation-specific safeguards and conservative short-answer
canonicalization. No rule reads or branches on a dataset name.

## Method

For a question `x`, optional entity metadata `m=(title, subject, relation)`, and
direct answer `d`, the system executes:

1. Persist `d` before retrieval so it remains an available fallback.
2. Construct the answer-free query `q0 = N(x + m)`.
3. If `d` is non-empty, construct `q1 = N(q0 + d)`; otherwise omit `q1`.
4. Retrieve up to 50 passages per active query, deduplicate by passage identity,
   and use RRF with `k=20` to retain the top three passages.
5. Request a fixed-schema record containing the candidate answer, support level,
   evidence utility, cited document IDs, and a concise reason.
6. Replace `d` only if the candidate is non-empty, helpful, sufficiently
   supported, grounded in cited evidence, grounded to the target subject when
   entity metadata is available, and different from `d`.
7. Apply `PostAudit = Canon ∘ G_rel ∘ G_safe`, recording every intervention and
   its reason code.

When entity metadata is absent, UER-RAG uses the documented generic branch. The
subject-grounding check is then not applicable; the other five checks remain in
force.

## Repository layout

```text
src/uer_rag/                 core pipeline, verifier, gate, post-audit, metrics
configs/default.yaml         frozen default configuration
scripts/                     data preparation, indexing, and statistical replay
manifests/                   frozen PopQA and EntityQuestions qid splits
analysis/                    standalone vector figure builders and source data
results/                     frozen aggregate metrics and provenance notes
tests/                       unit and integration-style regression tests
examples/input.jsonl         minimal input example
```

## Installation

Python 3.10 or later is required.

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The package uses an OpenAI-compatible chat-completions endpoint and an
Elasticsearch index. Set credentials in the shell or in a private local file;
the runner does not automatically read `.env`.

Linux/macOS:

```bash
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="https://provider.example/v1"
export UER_RAG_MODEL="model-id"
export ELASTICSEARCH_URL="http://localhost:9200"
export UER_RAG_INDEX="wikipedia"
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "..."
$env:OPENAI_BASE_URL = "https://provider.example/v1"
$env:UER_RAG_MODEL = "model-id"
$env:ELASTICSEARCH_URL = "http://localhost:9200"
$env:UER_RAG_INDEX = "wikipedia"
```

Optional Elasticsearch basic-auth variables are
`ELASTICSEARCH_USERNAME` and `ELASTICSEARCH_PASSWORD`. Never commit an actual
`.env` file or API key.

## Prepare benchmark data

Obtain PopQA or EntityQuestions under its original license. Normalize a JSON or
JSONL export and apply one of the frozen manifests:

```bash
python scripts/prepare_dataset.py \
  --input /path/to/original.jsonl \
  --manifest manifests/popqa_test13267_qids.txt \
  --output data/popqa_test13267.jsonl
```

Accepted aliases include `qid/id`, `question/query`,
`entity/entity_title/s_wiki_title`, `subject/subj`, and
`relation/property/prop`. The script stops on missing or duplicate qids.

## Build the retrieval index

Provide a legally obtained, pre-segmented Wikipedia JSONL file with `title` and
`text` fields. The script creates a deterministic one-shard schema and stable
document IDs:

```bash
python scripts/build_wikipedia_index.py \
  --input /path/to/wikipedia_passages.jsonl \
  --url http://localhost:9200 \
  --index wikipedia
```

Use `--recreate` only when intentionally replacing that exact index. The
original experiment's private Wikipedia snapshot is not redistributed, so a
new snapshot may not reproduce every retrieval result exactly.

## Run or resume

Input is one JSON object per line:

```json
{"qid":"1788652","question":"In what city was Louis Renault born?","entity":"Louis Renault (jurist)","subject":"Louis Renault","relation":"place of birth","gold_answers":["Autun"]}
```

Only `qid` and `question` are required.

```bash
uer-rag run \
  --input data/popqa_test13267.jsonl \
  --output outputs/popqa_predictions.jsonl \
  --config configs/default.yaml
```

The output is append-only JSONL. Re-running the command skips successful qids
and retries failed or interrupted qids. Every success stores both retrieval
views (when active), fused passages, raw structured verification, six gate
checks, post-audit reason codes, selected source, and final answer.

## Offline evaluation and uncertainty

```bash
uer-rag evaluate \
  --prediction outputs/popqa_predictions.jsonl \
  --reference data/popqa_test13267.jsonl
```

The evaluator collapses retry logs to the latest row per qid and rejects
`call_error` or interrupted rows by default. It reports normalized exact match
(EM), complete-word-boundary answer-containment Accuracy, maximum token F1 over
all gold aliases, paired gain, and harm rate. It performs no model or retrieval
calls.

Recompute 20,000-resample paired bootstrap intervals and exact sign tests:

```bash
python scripts/recompute_statistics.py \
  --prediction outputs/popqa_predictions.jsonl \
  --reference data/popqa_test13267.jsonl \
  --resamples 20000 \
  --seed 20260730 \
  --output outputs/popqa_statistics.json
```

## Frozen manuscript results

| Evaluation scope | n | Direct F1 | UER-RAG F1 | Harm rate |
|---|---:|---:|---:|---:|
| PopQA complete collection† | 14,267 | 42.77 | **69.82** | **1.07** |
| PopQA development-disjoint test | 13,267 | 42.90 | **70.31** | **1.06** |
| EntityQuestions frozen test | 5,000 | 48.07 | **59.57** | **2.76** |

†The complete PopQA collection includes 1,000 examples used during development;
it is descriptive. The 13,267-example split is the held-out result.

The exact aggregate values and metric definitions are in
`results/paper_metrics.json`. Raw provider responses and retrieved Wikipedia
text are excluded. All neural-generation results reported by the current
manuscript use one fixed generator. The release therefore makes cross-dataset,
cross-relation, and PopQA split-robustness claims, but no cross-model claim. See
`results/README.md` for the reproducibility boundary.

## Reproduce figures

```bash
python analysis/build_figures.py
```

Figures 1–4 are editable SVG flowcharts. Quantitative figures are emitted as
SVG, vector PDF, and 450-dpi PNG. Values are loaded from
`results/figure_statistics.json`, while relation-level values are loaded from
`analysis/data/relation_results.csv`; captions are intentionally left to the
manuscript rather than drawn above the artwork. The final quantitative panel
compares the complete PopQA collection with the development-disjoint split; it
does not report a second generator.

## Tests

```bash
python -m pytest
python -m ruff check .
```

GitHub Actions runs both commands on Python 3.10 and 3.12.

## Citation

Citation metadata is provided in `CITATION.cff`. Until the accompanying paper
has a stable bibliographic record, cite the software release and include the
repository URL.

## License and data

The implementation is released under the MIT License. Benchmark datasets,
Wikipedia indexes, model responses, and third-party services remain subject to
their respective licenses and terms.
