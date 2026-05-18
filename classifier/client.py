"""
Hybrid classification pipeline:
  1. nlp.pre_classify()  → Python handles category, sectors, keywords, region, sentiment, politicians
  2. _ai_enrich_batch()  → AI handles grouping, summary, civic_action, urgency, resolution_status,
                           government_response, confidence_score, and politician impact ratings
  3. _merge()            → Python metadata is merged back into each AI-produced topic
"""
import json
import os

from openai import OpenAI

from classifier.nlp import (
    majority_vote,
    merge_sectors,
    merge_unique,
    pre_classify,
)
from classifier.prompts import SYSTEM_PROMPT, build_user_prompt
from scrapers.base import RawArticle

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def _ai_enrich_batch(
    articles: list[RawArticle],
    python_meta: list[dict],
) -> list[dict]:
    """Send one batch to AI. AI only generates the fields Python cannot."""
    batch_input = [
        {
            "title": a.title,
            "summary": (a.summary or "")[:300],
            "py_category": python_meta[i]["category"],
            "py_sentiment": python_meta[i]["sentiment_hint"],
            "py_politicians": python_meta[i]["detected_politicians"],
        }
        for i, a in enumerate(articles)
    ]

    response = _get_client().chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(batch_input)},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    result = json.loads(response.choices[0].message.content)
    topics = result.get("topics", [])

    for topic in topics:
        indices = topic.pop("source_indices", [])
        valid_indices = [i for i in indices if 0 <= i < len(articles)]

        topic["raw_sources"] = [articles[i] for i in valid_indices]

        # Merge Python classifications across all articles in this group
        group_meta = [python_meta[i] for i in valid_indices]
        _merge_python_into_topic(topic, group_meta)

    return topics


def _merge_python_into_topic(topic: dict, group_meta: list[dict]) -> None:
    """
    Fill in fields that Python computed. Only set if AI did not already provide them
    (AI can override category/sentiment if it detects a clear mismatch).
    """
    if not group_meta:
        return

    topic.setdefault(
        "category",
        majority_vote([m["category"] for m in group_meta]),
    )
    topic.setdefault(
        "affected_sectors",
        merge_sectors([m["affected_sectors"] for m in group_meta]),
    )
    topic["keywords"] = merge_unique([m["keywords"] for m in group_meta])[:8]
    topic["policy_tags"] = merge_unique([m["policy_tags"] for m in group_meta])
    topic.setdefault(
        "region_primary",
        majority_vote([m["region_primary"] for m in group_meta]),
    )
    # sentiment: AI provides the final label; fall back to Python's VADER hint
    topic.setdefault(
        "sentiment",
        majority_vote([m["sentiment_hint"] for m in group_meta]),
    )
    # Derive impact_level from region_primary and source count.
    # AI no longer returns this field directly.
    # Heuristic: National → national; named region with multiple sources → regional;
    # named region with only one source (likely a local beat story) → local.
    region = topic.get("region_primary", "")
    source_count = len(topic.get("raw_sources", []))
    if not region or region == "National":
        topic.setdefault("impact_level", "national")
    elif source_count == 1:
        topic.setdefault("impact_level", "local")
    else:
        topic.setdefault("impact_level", "regional")


def classify_all(articles: list[RawArticle], batch_size: int = 10) -> list[dict]:
    if not articles:
        return []

    # Step 1: Python pre-classification (free, fast, deterministic)
    python_meta = [pre_classify(a) for a in articles]

    # Step 2: AI enrichment in batches (grouping + generative fields only)
    all_topics: list[dict] = []
    failed = 0
    total_batches = -(-len(articles) // batch_size)  # ceiling division

    for start in range(0, len(articles), batch_size):
        batch = articles[start : start + batch_size]
        batch_meta = python_meta[start : start + batch_size]
        try:
            topics = _ai_enrich_batch(batch, batch_meta)
            all_topics.extend(topics)
        except Exception as e:
            failed += 1
            print(f"[classifier] Batch {start // batch_size} failed: {e}")

    if failed == total_batches:
        raise RuntimeError(
            f"All {total_batches} AI classification batches failed. "
            "Check OPENAI_API_KEY, quota, and network connectivity."
        )

    if failed:
        print(f"[classifier] WARNING: {failed}/{total_batches} batches failed — some articles were not classified.")

    return all_topics
