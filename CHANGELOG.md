# Changelog

## 1.2.0 — 2026-10-04

- Removed exploratory cross-model aggregates that were not backed by a common
  frozen qid manifest and per-example archive.
- Added the complete-versus-development-disjoint PopQA sensitivity source and
  standalone figure.
- Aligned the README, result provenance, tests, and publishing instructions
  with the fact-checked no-appendix manuscript.

## 1.1.0 — 2026-10-02

- Replayed the frozen deterministic post-authorization audit used by the paper.
- Made failed and interrupted qids retryable and evaluation fail closed.
- Omitted duplicate answer-conditioned retrieval when the direct answer is empty.
- Enabled evidence adoption in the documented metadata-free generic branch.
- Added dataset normalization, deterministic index construction, paired
  bootstrap/sign-test recomputation, and traceable figure statistics.
- Added Elasticsearch basic authentication, CI, regression tests, and explicit
  reproducibility limitations.

## 1.0.0 — 2026-09-11

- Initial public reference implementation.
