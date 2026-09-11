"""Normalization shared by routing and offline evaluation."""

from __future__ import annotations

import re
import string
import unicodedata

_ARTICLES = re.compile(r"\b(a|an|the)\b", flags=re.IGNORECASE)
_SPACE = re.compile(r"\s+")


def normalize_answer(value: object) -> str:
    """Apply the paper's deterministic English short-answer normalization."""

    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    text = "".join(ch for ch in text if ch not in string.punctuation)
    text = _ARTICLES.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def normalized_tokens(value: object) -> list[str]:
    return normalize_answer(value).split()


def contains_complete_words(container: object, candidate: object) -> bool:
    """Return true when normalized candidate tokens occur contiguously."""

    haystack = normalized_tokens(container)
    needle = normalized_tokens(candidate)
    if not needle or len(needle) > len(haystack):
        return False
    width = len(needle)
    return any(haystack[i : i + width] == needle for i in range(len(haystack) - width + 1))


def join_observable_fields(*values: object) -> str:
    """Join fields without inventing data or repeating normalized strings."""

    parts: list[str] = []
    seen: set[str] = set()
    for value in values:
        rendered = _SPACE.sub(" ", str(value or "")).strip()
        key = normalize_answer(rendered)
        if rendered and key and key not in seen:
            parts.append(rendered)
            seen.add(key)
    return " ".join(parts)
