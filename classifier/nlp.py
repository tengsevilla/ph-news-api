"""
Python-only classification layer. No AI calls here.
Uses YAKE (keywords), VADER (sentiment), and keyword/regex rules.
"""
import re
from collections import Counter

import yake
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from classifier.rules import (
    CATEGORY_KEYWORDS,
    POLITICIAN_TITLE_PREFIXES,
    POLICY_TAG_KEYWORDS,
    REGION_KEYWORDS,
    SECTOR_KEYWORDS,
)
from scrapers.base import RawArticle

# ── Lazy singletons ────────────────────────────────────────────────────────────

_vader: SentimentIntensityAnalyzer | None = None
_kw_extractor: yake.KeywordExtractor | None = None
_politician_regex: re.Pattern | None = None


def _get_vader() -> SentimentIntensityAnalyzer:
    global _vader
    if _vader is None:
        _vader = SentimentIntensityAnalyzer()
    return _vader


def _get_kw_extractor() -> yake.KeywordExtractor:
    global _kw_extractor
    if _kw_extractor is None:
        # n=2 → up to bigrams; top=10 → return top 10 candidates
        _kw_extractor = yake.KeywordExtractor(lan="en", n=2, dedupLim=0.7, top=10)
    return _kw_extractor


def _get_politician_regex() -> re.Pattern:
    global _politician_regex
    if _politician_regex is None:
        titles = sorted(POLITICIAN_TITLE_PREFIXES, key=len, reverse=True)
        title_pat = "|".join(re.escape(t) for t in titles)
        # Match "Senator Juan dela Cruz" or "Sen. Bong Go"
        _politician_regex = re.compile(
            rf"(?:{title_pat})\.?\s+([A-Z][a-zA-ZñÑ]+(?:[\s\-][A-Z][a-zA-ZñÑ]+){{1,4}})",
            re.UNICODE,
        )
    return _politician_regex


# ── Classification functions ───────────────────────────────────────────────────

def classify_category(text: str) -> str:
    text_lower = text.lower()
    scores = {
        cat: sum(1 for kw in keywords if kw in text_lower)
        for cat, keywords in CATEGORY_KEYWORDS.items()
    }
    best_cat, best_score = max(scores.items(), key=lambda x: x[1])
    return best_cat if best_score > 0 else "social"


def classify_sectors(text: str) -> list[dict]:
    """Return list of {slug, intensity} dicts where text matches sector keywords."""
    text_lower = text.lower()
    results = []
    for slug, keywords in SECTOR_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches == 0:
            continue
        intensity = "high" if matches >= 2 else "medium"
        results.append({"slug": slug, "intensity": intensity})
    return results


def extract_keywords(text: str) -> list[str]:
    """Extract up to 8 key terms using YAKE."""
    extractor = _get_kw_extractor()
    raw = extractor.extract_keywords(text)
    # YAKE returns (keyword, score) — lower score = more relevant
    return [kw for kw, _score in raw][:8]


def extract_policy_tags(text: str) -> list[str]:
    text_lower = text.lower()
    return [
        tag
        for tag, keywords in POLICY_TAG_KEYWORDS.items()
        if any(kw in text_lower for kw in keywords)
    ]


def detect_region(text: str) -> str:
    text_lower = text.lower()
    for region, keywords in REGION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return region
    return "National"


def detect_sentiment(text: str) -> str:
    """VADER compound score → positive / negative / neutral label."""
    compound = _get_vader().polarity_scores(text)["compound"]
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def detect_politicians(text: str) -> list[str]:
    """Extract politician names by matching title-prefix patterns."""
    matches = _get_politician_regex().findall(text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result = []
    for name in matches:
        name = name.strip()
        if name and name not in seen:
            seen.add(name)
            result.append(name)
    return result


# ── Per-article entry point ────────────────────────────────────────────────────

def pre_classify(article: RawArticle) -> dict:
    """
    Run all Python-based classification on a single article.
    Returns a dict that is passed to the AI prompt as context,
    and merged back into the topic after AI responds.
    """
    text = f"{article.title}. {article.summary or ''}"
    return {
        "category": classify_category(text),
        "affected_sectors": classify_sectors(text),
        "keywords": extract_keywords(text),
        "policy_tags": extract_policy_tags(text),
        "region_primary": detect_region(text),
        "sentiment_hint": detect_sentiment(text),
        "detected_politicians": detect_politicians(article.title + " " + (article.summary or "")),
    }


# ── Group-level merging helpers ────────────────────────────────────────────────

def majority_vote(values: list[str]) -> str:
    if not values:
        return ""
    return Counter(values).most_common(1)[0][0]


def merge_sectors(sector_lists: list[list[dict]]) -> list[dict]:
    """Combine sector lists from multiple articles; keep highest intensity per slug."""
    rank = {"high": 3, "medium": 2, "low": 1}
    best: dict[str, dict] = {}
    for sectors in sector_lists:
        for s in sectors:
            slug = s["slug"]
            if slug not in best or rank.get(s["intensity"], 2) > rank.get(best[slug]["intensity"], 2):
                best[slug] = s
    return list(best.values())


def merge_unique(lists: list[list]) -> list:
    seen: set = set()
    result = []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result
