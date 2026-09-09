from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Iterable

import spacy


logger = logging.getLogger("resume_optimizer.ats")

TECH_TERMS = {
    "aws",
    "aws lambda",
    "azure",
    "docker",
    "kubernetes",
    "react",
    "fastapi",
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "postgresql",
    "mysql",
    "mongodb",
    "redis",
    "graphql",
    "rest",
    "rest api",
    "spring boot",
    "microsoft sql server",
    "ci/cd",
    "terraform",
    "linux",
    "machine learning",
    "nlp",
    "llm",
}

STOPWORDS = {
    "ability",
    "across",
    "around",
    "build",
    "building",
    "built",
    "candidate",
    "collaborate",
    "collaboration",
    "company",
    "culture",
    "environment",
    "experience",
    "excellent",
    "including",
    "initiative",
    "initiatives",
    "opportunity",
    "responsibilities",
    "responsibility",
    "role",
    "skills",
    "strong",
    "team",
    "teams",
    "using",
    "work",
    "working",
}


@lru_cache(maxsize=1)
def _load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' is unavailable; using a blank deterministic fallback pipeline.")
        return spacy.blank("en")


def extract_keywords(text: str) -> list[str]:
    normalized = (text or "").strip()
    if not normalized:
        return []

    nlp = _load_nlp()
    doc = nlp(normalized)
    keywords: set[str] = set()

    for ent in getattr(doc, "ents", []):
        value = _clean_token(ent.text)
        if value:
            keywords.add(value)

    for token in doc:
        pos = getattr(token, "pos_", "")
        if pos in {"NOUN", "PROPN", "VERB"} or _clean_token(token.text) in TECH_TERMS:
            value = _clean_token(token.lemma_ if getattr(token, "lemma_", "") else token.text)
            if value:
                keywords.add(value)

    for value in _fallback_terms(normalized):
        keywords.add(value)

    return sorted(keywords)


def calculate_ats_score(resume_text: str, jd_text: str) -> dict:
    keywords = extract_keywords(jd_text)
    if not keywords:
        return {"score": 0.0, "matched_keywords": [], "missing_keywords": []}

    resume_normalized = _normalize_for_match(resume_text)
    matched = [keyword for keyword in keywords if _keyword_present(keyword, resume_normalized)]
    missing = [keyword for keyword in keywords if keyword not in matched]
    score = min(100.0, (len(matched) / len(keywords)) * 100.0)

    return {
        "score": round(score, 2),
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def _fallback_terms(text: str) -> Iterable[str]:
    lowered = text.lower()
    for phrase in sorted(TECH_TERMS, key=len, reverse=True):
        if phrase in lowered:
            yield phrase

    for raw in re.findall(r"\b[a-zA-Z][a-zA-Z0-9+./#-]{2,}\b", text):
        value = _clean_token(raw)
        if value and value not in STOPWORDS:
            yield value


def _clean_token(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.lower()).strip(" .,;:()[]{}")
    if not cleaned or cleaned in STOPWORDS:
        return ""
    if len(cleaned) < 3 and cleaned not in {"c", "r"}:
        return ""
    return cleaned


def _normalize_for_match(text: str) -> str:
    return " " + re.sub(r"\s+", " ", (text or "").lower()) + " "


def _keyword_present(keyword: str, normalized_resume: str) -> bool:
    escaped = re.escape(keyword.lower())
    return re.search(rf"(?<![a-z0-9+#./-]){escaped}(?![a-z0-9+#./-])", normalized_resume) is not None
