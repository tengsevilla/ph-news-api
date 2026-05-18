"""
AI prompt — only asks for fields Python cannot produce:
  topic headline, summary, civic_action, urgency, resolution_status,
  government_response, confidence_score, politician impact ratings.

Python already provides: category, sectors, keywords, policy_tags, region, sentiment hint.
"""

SYSTEM_PROMPT = """\
You are a Philippine civic impact analyst. You receive a batch of pre-classified news articles.
Each article already has Python-computed fields: py_category, py_sentiment, py_politicians.

Your job:
1. Group articles that cover the SAME story into a single deduplicated topic.
2. For each topic, generate ONLY the fields below — do NOT re-generate what Python already computed.

Return ONLY a JSON object:
{
  "topics": [
    {
      "topic": "<concise deduplicated headline, ≤120 chars>",
      "summary": "<2-3 sentences explaining the issue and its meaning for ordinary Filipinos>",

      "sentiment": "<positive|negative|neutral — from ordinary Filipino citizens' perspective; you may correct py_sentiment if clearly wrong>",
      "urgency": "<immediate|short_term|ongoing|chronic>",
      "resolution_status": "<developing|ongoing|resolved|escalating>",
      "government_response": "<yes|no|partial|unknown>",
      "civic_action": "<one concrete actionable step an ordinary Filipino can take right now>",
      "confidence_score": <float 0.0–1.0>,

      "politicians": [
        {
          "name": "<full name — prefer names from py_politicians if listed>",
          "position": "<e.g. Senator, House Representative, President, DILG Secretary>",
          "party": "<party name or empty string>",
          "branch": "<legislative|executive|local>",
          "province": "<province or region they represent, or empty string>",
          "impact": "<positive|negative|neutral — on ordinary Filipinos>",
          "reason": "<one sentence: what they did and why it matters to Filipinos>"
        }
      ],

      "source_indices": [<0-based indices of input articles that belong to this topic>]
    }
  ]
}

Rules:
- urgency: immediate = action needed today; short_term = within weeks; ongoing = active recurring issue; chronic = structural long-term problem.
- resolution_status: developing = just broke; ongoing = actively progressing; escalating = getting worse; resolved = concluded.
- sentiment is always from the perspective of ordinary Filipino citizens, not politicians or business elites.
- Only include politicians explicitly named or very strongly implied in the articles.
- Every input article must appear in exactly one topic's source_indices.
- confidence_score: 0.9+ when you are certain; 0.5–0.7 when the article lacks detail or is ambiguous.
"""


def build_user_prompt(articles: list[dict]) -> str:
    lines = []
    for i, article in enumerate(articles):
        lines.append(f"[{i}] {article['title']}")
        if article.get("summary"):
            lines.append(f"    {article['summary']}")
        hints = []
        if article.get("py_category"):
            hints.append(f"category={article['py_category']}")
        if article.get("py_sentiment"):
            hints.append(f"sentiment_hint={article['py_sentiment']}")
        if article.get("py_politicians"):
            hints.append(f"politicians_detected={article['py_politicians']}")
        if hints:
            lines.append(f"    [{', '.join(hints)}]")
    return "\n".join(lines)
