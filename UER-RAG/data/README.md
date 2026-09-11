# Data

Download PopQA and EntityQuestions from their official releases. Do not commit
restricted retrieval-corpus text or API responses containing such text.

Use the qid lists in `../manifests/` to reconstruct the exact development and
evaluation scopes reported in the manuscript. The runner accepts JSONL with
`qid`, `question`, optional `entity`/`subject`/`relation`, and optional
`gold_answers` fields.
