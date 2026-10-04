"""Archived deterministic post-authorization audit used by UER-RAG.

The paper reports scores after three local operations: a direct-preserving
safety guard, a relation-aware guard, and short-answer canonicalization.  They
make no model calls and record every intervention with a machine-readable
reason code.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

from .retrieval import Passage
from .verifier import EvidenceRecord


def _clean(value: object) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip().strip('"').strip("'")
    text = re.sub(
        r"^(final answer|answer|evidence answer)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    if "\n" in text:
        text = text.splitlines()[0].strip()
    invalid = {
        "no answer",
        "no answer found",
        "not found",
        "unknown",
        "none",
        "n/a",
        "no evidence",
    }
    return "" if text.lower().strip(".") in invalid else text


def _key(value: object) -> str:
    text = unicodedata.normalize("NFKD", _clean(value).lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _row_fields(row: Mapping[str, object]) -> tuple[str, str, str]:
    title = str(
        row.get("entity_title") or row.get("s_wiki_title") or row.get("entity") or ""
    ).strip()
    subject = str(row.get("subject") or row.get("subj") or "").strip()
    relation = str(row.get("relation") or row.get("property") or row.get("prop") or "").strip()
    return title, subject, relation


def _docs_contain(answer: str, passages: Sequence[Passage]) -> bool:
    answer_key = _key(answer)
    return bool(
        answer_key
        and any(answer_key in _key(f"{passage.title} {passage.text}") for passage in passages)
    )


def _has_exact_disambiguated_title(entity_title: str, passages: Sequence[Passage]) -> bool:
    """Replay the frozen wrong-entity guard.

    Only explicitly disambiguated titles require an exact normalized title
    match.  Plain surface names are intentionally left to the verifier and the
    six-check gate.
    """

    title = _clean(entity_title)
    if not title or ("(" not in title and "," not in title):
        return True
    expected = _key(title)
    return any(_key(passage.title) == expected for passage in passages)


def direct_preserving_safety_guard(
    *,
    question: str,
    direct_answer: str,
    proposed_answer: str,
    selected_source: str,
    entity_title: str,
    passages: Sequence[Passage],
) -> tuple[str, str]:
    """Apply the frozen direct-preserving guard and return answer/reason."""

    direct = _clean(direct_answer)
    proposed = _clean(proposed_answer)
    if not proposed:
        return direct, "empty_proposal_restore_direct" if direct else ""
    if not direct or selected_source.lower() not in {"evidence", "candidate"}:
        return proposed, ""
    if _key(proposed) == _key(direct):
        return direct, ""
    if not _has_exact_disambiguated_title(entity_title, passages):
        return direct, "disambiguated_entity_title_mismatch"
    if _key(direct) and _key(direct) in _key(proposed):
        return direct, "direct_is_shorter_supported_form"
    q = question.lower()
    sensitive = any(
        token in q for token in ("occupation", "profession", "what sport", "which sport")
    )
    if sensitive and _docs_contain(direct, passages):
        return direct, "sensitive_relation_direct_grounded"
    return proposed, ""


def canonicalize_short_answer(question: str, answer: str) -> str:
    """Replay the frozen conservative PopQA-style answer canonicalizer."""

    q = _clean(question).lower()
    value = _clean(answer)
    if not value:
        return value
    multi = (
        q.startswith(("who are ", "what are ", "which are "))
        or " list " in f" {q} "
        or "name all" in q
        or "multiple" in q
    )
    if multi:
        return value
    if any(token in q for token in ("genre", "type", "category", "kind")):
        if "/" in value and not value.lower().startswith("http"):
            value = value.split("/", 1)[0].strip()
        if ";" in value:
            value = value.split(";", 1)[0].strip()
        return _clean(value)
    if any(token in q for token in ("occupation", "profession", "job", "role")):
        value = re.sub(r"\s+as well as\s+.*$", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"\s+together with\s+.*$", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"\s+along with\s+.*$", "", value, flags=re.IGNORECASE).strip()
        value = re.sub(r"\s+and\s+.*$", "", value, flags=re.IGNORECASE).strip()
        if ";" in value:
            value = value.split(";", 1)[0].strip()
        if "/" in value and not value.lower().startswith("http"):
            value = value.split("/", 1)[0].strip()
    return _clean(value)


def _country_key(value: object) -> str:
    key = _key(value)
    return key.removeprefix("the ")


_COUNTRY_ALIASES = {
    _country_key(name)
    for name in [
        "\nAfghanistan",
        "Albania",
        "Algeria",
        "Andorra",
        "Angola",
        "Antigua and Barbuda",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "\nBahamas",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belarus",
        "Belgium",
        "Belize",
        "Benin",
        "Bhutan",
        "Bolivia",
        "Bosnia and Herzegovina",
        "Botswana",
        "Brazil",
        "Brunei",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "\nCabo Verde",
        "Cape Verde",
        "Cambodia",
        "Cameroon",
        "Canada",
        "Central African Republic",
        "Chad",
        "Chile",
        "China",
        "Colombia",
        "Comoros",
        "Costa Rica",
        "Croatia",
        "Cuba",
        "Cyprus",
        "Czechia",
        "Czech Republic",
        "\nDemocratic Republic of the Congo",
        "DR Congo",
        "Congo-Kinshasa",
        "Republic of the Congo",
        "Congo",
        "Congo-Brazzaville",
        "Cote d'Ivoire",
        "Ivory Coast",
        "\nDenmark",
        "Djibouti",
        "Dominica",
        "Dominican Republic",
        "Ecuador",
        "Egypt",
        "El Salvador",
        "Equatorial Guinea",
        "Eritrea",
        "Estonia",
        "Eswatini",
        "Swaziland",
        "Ethiopia",
        "\nFiji",
        "Finland",
        "France",
        "Gabon",
        "Gambia",
        "Georgia",
        "Germany",
        "Ghana",
        "Greece",
        "Grenada",
        "Guatemala",
        "Guinea",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hungary",
        "\nIceland",
        "India",
        "Indonesia",
        "Iran",
        "Iraq",
        "Ireland",
        "Israel",
        "Italy",
        "Jamaica",
        "Japan",
        "Jordan",
        "Kazakhstan",
        "Kenya",
        "Kiribati",
        "Kosovo",
        "Kuwait",
        "Kyrgyzstan",
        "\nLaos",
        "Lao People's Democratic Republic",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libya",
        "Liechtenstein",
        "Lithuania",
        "Luxembourg",
        "\nMadagascar",
        "Malawi",
        "Malaysia",
        "Maldives",
        "Mali",
        "Malta",
        "Marshall Islands",
        "Mauritania",
        "Mauritius",
        "Mexico",
        "Micronesia",
        "Federated States of Micronesia",
        "Moldova",
        "Monaco",
        "Mongolia",
        "Montenegro",
        "Morocco",
        "Mozambique",
        "Myanmar",
        "Burma",
        "\nNamibia",
        "Nauru",
        "Nepal",
        "Netherlands",
        "New Zealand",
        "Nicaragua",
        "Niger",
        "Nigeria",
        "North Korea",
        "Democratic People's Republic of Korea",
        "North Macedonia",
        "Macedonia",
        "Norway",
        "\nOman",
        "Pakistan",
        "Palau",
        "Palestine",
        "State of Palestine",
        "Panama",
        "Papua New Guinea",
        "Paraguay",
        "Peru",
        "Philippines",
        "Poland",
        "Portugal",
        "Qatar",
        "\nRomania",
        "Russia",
        "Russian Federation",
        "Rwanda",
        "Saint Kitts and Nevis",
        "St Kitts and Nevis",
        "Saint Lucia",
        "St Lucia",
        "Saint Vincent and the Grenadines",
        "St Vincent and the Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome and Principe",
        "Saudi Arabia",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Sierra Leone",
        "Singapore",
        "Slovakia",
        "Slovak Republic",
        "Slovenia",
        "Solomon Islands",
        "Somalia",
        "South Africa",
        "South Korea",
        "Republic of Korea",
        "South Sudan",
        "Spain",
        "Sri Lanka",
        "Sudan",
        "Suriname",
        "Sweden",
        "Switzerland",
        "Syria",
        "Syrian Arab Republic",
        "\nTaiwan",
        "Republic of China",
        "Tajikistan",
        "Tanzania",
        "United Republic of Tanzania",
        "Thailand",
        "Timor-Leste",
        "East Timor",
        "Togo",
        "Tonga",
        "Trinidad and Tobago",
        "Tunisia",
        "Turkey",
        "Turkiye",
        "Turkmenistan",
        "Tuvalu",
        "\nUganda",
        "Ukraine",
        "United Arab Emirates",
        "UAE",
        "United Kingdom",
        "UK",
        "Great Britain",
        "Britain",
        "England",
        "Scotland",
        "Wales",
        "Northern Ireland",
        "United States",
        "United States of America",
        "USA",
        "US",
        "America",
        "Uruguay",
        "Uzbekistan",
        "\nVanuatu",
        "Vatican City",
        "Vatican",
        "Holy See",
        "Venezuela",
        "Vietnam",
        "Viet Nam",
        "Yemen",
        "Zambia",
        "Zimbabwe\n",
    ]
    if _country_key(name)
}

_RELIGIOUS_ROLE_WORDS = {
    "priest",
    "bishop",
    "pastor",
    "cleric",
    "clergyman",
    "clergy",
    "rabbi",
    "imam",
    "monk",
    "nun",
    "minister",
    "missionary",
    "theologian",
    "preacher",
    "chaplain",
    "cardinal",
    "pope",
}


def _cited(passages: Sequence[Passage], ids: Sequence[int]) -> list[Passage]:
    return [passages[index - 1] for index in ids if 1 <= index <= len(passages)]


def _contains(passage: Passage, answer: str) -> bool:
    key = _key(answer)
    return bool(key and key in _key(f"{passage.title} {passage.text}"))


def _quote_question(question: str) -> bool:
    q = _key(question)
    return bool(
        re.search(r"\bwho (?:said|says|stated|uttered|spoke|remarked|declared|replied)\b", q)
        or re.search(r"\bwho (?:is|was) (?:quoted|credited) (?:as|with) saying\b", q)
    )


def _attributes_speech(passage: Passage, answer: str) -> bool:
    answer_key = _key(answer)
    text_key = _key(passage.text)
    if not answer_key or not text_key:
        return False
    attribution = re.compile(
        r"\b(?:said|says|stated|uttered|spoke|remarked|declared|replied|"
        r"according to|quote by|quotation by|quoted|credited with saying)\b"
    )
    start = 0
    while True:
        position = text_key.find(answer_key, start)
        if position < 0:
            return False
        window = text_key[max(0, position - 120) : position + len(answer_key) + 120]
        if attribution.search(window):
            return True
        start = position + len(answer_key)


def _relation_name(question: str, relation: str) -> str:
    prop = _key(relation)
    if prop in {"capital", "capital of"}:
        return "capital"
    if prop in {"composer", "producer", "country", "religion"}:
        return prop
    q = f" {_key(question)} "
    for name, tokens in {
        "capital": (" capital ",),
        "composer": (" composer ", " composed "),
        "producer": (" producer ", " produced "),
        "country": (" country ",),
        "religion": (" religion ", " religious "),
    }.items():
        if any(token in q for token in tokens):
            return name
    return ""


def relation_safety_guard(
    *,
    question: str,
    relation: str,
    direct_answer: str,
    proposed_answer: str,
    selected_source: str,
    record: EvidenceRecord,
    passages: Sequence[Passage],
) -> tuple[str, str]:
    direct = _clean(direct_answer)
    proposed = _clean(proposed_answer)
    if selected_source.lower() != "evidence" or not direct or not proposed:
        return proposed, ""
    if _key(direct) == _key(proposed):
        return direct, ""
    cited = _cited(passages, record.supporting_doc_ids)
    name = _relation_name(question, relation)
    if _quote_question(question) and not any(_attributes_speech(p, proposed) for p in cited):
        return direct, "quote_speaker_not_explicitly_attributed"
    if name == "capital" and any(_contains(p, direct) for p in cited):
        return direct, "capital_direct_supported"
    if name == "composer":
        direct_tokens = _key(direct).split()
        proposed_tokens = set(_key(proposed).split())
        surname = direct_tokens[-1] if len(direct_tokens) >= 2 else ""
        joined = bool(re.search(r"\b(?:and)\b|[;&]", proposed.lower()))
        if (
            surname
            and len(surname) >= 3
            and surname not in {"jr", "sr", "ii", "iii", "iv"}
            and surname in proposed_tokens
            and joined
        ):
            return direct, "composer_surname_expansion"
    if (
        name == "country"
        and _country_key(direct) in _COUNTRY_ALIASES
        and _country_key(proposed) not in _COUNTRY_ALIASES
    ):
        return direct, "country_type_mismatch"
    if name == "religion":
        direct_words = set(_key(direct).split())
        proposed_words = set(_key(proposed).split())
        if not (direct_words & _RELIGIOUS_ROLE_WORDS) and (proposed_words & _RELIGIOUS_ROLE_WORDS):
            return direct, "religion_role_mismatch"
    return proposed, ""


@dataclass(frozen=True)
class PostAuditResult:
    final_answer: str
    selected_source: str
    pre_safety_answer: str
    pre_relation_answer: str
    pre_canonical_answer: str
    safety_guard_applied: bool
    relation_guard_applied: bool
    short_answer_applied: bool
    safety_guard_reason: str
    relation_guard_reason: str
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["reason_codes"] = list(self.reason_codes)
        return value


def post_audit(
    *,
    row: Mapping[str, object],
    question: str,
    direct_answer: str,
    proposed_answer: str,
    selected_source: str,
    record: EvidenceRecord,
    passages: Sequence[Passage],
) -> PostAuditResult:
    """Apply ``Canon o G_rel o G_safe`` and retain a replayable trace."""

    entity_title, _subject, relation = _row_fields(row)
    safe, safe_reason = direct_preserving_safety_guard(
        question=question,
        direct_answer=direct_answer,
        proposed_answer=proposed_answer,
        selected_source=selected_source,
        entity_title=entity_title,
        passages=passages,
    )
    relation_answer, relation_reason = relation_safety_guard(
        question=question,
        relation=relation,
        direct_answer=direct_answer,
        proposed_answer=safe,
        selected_source=selected_source,
        record=record,
        passages=passages,
    )
    final = canonicalize_short_answer(question, relation_answer)
    safety_applied = _key(safe) != _key(proposed_answer)
    relation_applied = _key(relation_answer) != _key(safe)
    short_applied = _key(final) != _key(relation_answer)
    source = selected_source
    if (safety_applied or relation_applied) and _key(final) == _key(direct_answer):
        source = "direct"
    codes = tuple(
        code
        for code in (
            safe_reason,
            relation_reason,
            "short_answer_canonicalized" if short_applied else "",
        )
        if code
    )
    return PostAuditResult(
        final_answer=final,
        selected_source=source,
        pre_safety_answer=_clean(proposed_answer),
        pre_relation_answer=safe,
        pre_canonical_answer=relation_answer,
        safety_guard_applied=safety_applied,
        relation_guard_applied=relation_applied,
        short_answer_applied=short_applied,
        safety_guard_reason=safe_reason,
        relation_guard_reason=relation_reason,
        reason_codes=codes,
    )
