# Result provenance

`paper_metrics.json` records the frozen aggregate values used in the
manuscript. `figure_statistics.json` is the single data source used by the
figure builder. Neither file is presented as a fresh execution of the public
code.

Raw model responses and retrieved Wikipedia passages are not redistributed.
They may contain provider output or third-party corpus text. With authorized
local prediction and reference files, recompute all paired metrics and
bootstrap intervals with:

```bash
python scripts/recompute_statistics.py \
  --prediction outputs/predictions.jsonl \
  --reference data/references.jsonl \
  --resamples 20000 \
  --seed 20260730 \
  --output outputs/statistics.json
```

All neural-generation results retained for the current manuscript use one fixed
generator. Earlier exploratory values from a different model protocol are not
included because they do not satisfy the same frozen qid, index, prompt, and
per-example archival requirements. Consequently, this release makes no
cross-model claim.

The PopQA split-sensitivity panel compares the complete 14,267-example
collection with the 13,267-example development-disjoint subset. The complete
collection includes 1,000 development examples and is descriptive; the
disjoint result is the held-out estimate.

The 5,000 EntityQuestions manifest and both PopQA manifests are provided under
`manifests/`. Benchmark data must be obtained under its original terms.
