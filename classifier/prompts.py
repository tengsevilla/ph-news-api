"""
AI prompt — only asks for fields Python cannot produce:
  topic headline, summary, civic_action, urgency, resolution_status,
  government_response, confidence_score, event_type, severity,
  affected_population_estimate, politician impact ratings,
  and affected_sectors (AI supplements Python keyword detection with contextual inference).

Python already provides: category, keywords, policy_tags, region, sentiment hint,
and a first-pass py_sectors list from keyword matching.
"""

_VALID_SECTOR_SLUGS = (
    "farmer, fisherman, miner, forest_worker, health_worker, social_worker, "
    "senior_citizen, pwd, teacher, student, labor_worker, kasambahay, "
    "security_guard, bpo_worker, retail_worker, hospitality_worker, driver, "
    "seafarer, delivery_rider, business_owner, vendor, freelancer, ofw, "
    "government_employee, barangay_official, military_police, engineer_architect, "
    "lawyer, journalist, it_tech_worker, artist_creative, solo_parent, "
    "informal_settler, indigenous_people, youth, lgbtq, prisoner_returnee"
)

SYSTEM_PROMPT = f"""\
You are a Philippine civic impact analyst. You receive a batch of pre-classified news articles.
Each article already has Python-computed fields: py_category, py_sentiment, py_politicians, py_sectors.

Your job:
1. Group articles that cover the SAME story into a single deduplicated topic.
2. For each topic, generate the fields below.

Return ONLY a JSON object:
{{
  "topics": [
    {{
      "topic": "<concise deduplicated headline, ≤120 chars>",
      "summary": "<2-3 sentences explaining the issue and its meaning for ordinary Filipinos>",

      "sentiment": "<positive|negative|neutral — from ordinary Filipino citizens' perspective; you may correct py_sentiment if clearly wrong>",
      "urgency": "<immediate|short_term|ongoing|chronic>",
      "resolution_status": "<developing|ongoing|resolved|escalating>",
      "government_response": "<yes|no|partial|unknown>",
      "civic_action": "<one concrete actionable step an ordinary Filipino can take right now>",
      "confidence_score": <float 0.0–1.0>,

      "event_type": "<legislation|policy|disaster|crime|corruption|protest|election|diplomacy|economic|health|environment|social|other>",
      "severity": <integer 1–5 — 1=minor local, 3=significant national, 5=crisis affecting millions>,
      "affected_population_estimate": "<e.g. '2.3M farmers', '500K students', 'all Filipinos'>",

      "affected_sectors": [
        {{"slug": "<slug from the valid list below>", "intensity": "<high|medium|low>"}}
      ],

      "politicians": [
        {{
          "name": "<full name — prefer names from py_politicians if listed>",
          "position": "<e.g. Senator, House Representative, President, DILG Secretary>",
          "party": "<party name or empty string>",
          "branch": "<legislative|executive|local>",
          "province": "<province or region they represent, or empty string>",
          "impact": "<positive|negative|neutral — on ordinary Filipinos>",
          "reason": "<one sentence: what they did and why it matters to Filipinos>"
        }}
      ],

      "source_indices": [<0-based indices of input articles that belong to this topic>]
    }}
  ]
}}

Rules:
- urgency: immediate = action needed today; short_term = within weeks; ongoing = active recurring issue; chronic = structural long-term problem.
- resolution_status: developing = just broke; ongoing = actively progressing; escalating = getting worse; resolved = concluded.
- sentiment is always from the perspective of ordinary Filipino citizens, not politicians or business elites.
- Only include politicians explicitly named or very strongly implied in the articles.
- Every input article must appear in exactly one topic's source_indices.
- confidence_score: 0.9+ when you are certain; 0.5–0.7 when the article lacks detail or is ambiguous.
- severity: 1=minor local incident; 2=notable but limited impact; 3=significant, affects thousands; 4=major, affects hundreds of thousands; 5=crisis-level, affects millions or is nationally destabilizing.
- affected_population_estimate: give a concrete estimate with archetype label (e.g. "2.3M farmers", "500K students in NCR", "all 18M registered voters"). Use "unknown" only if truly unquantifiable.
- affected_sectors: use py_sectors as a starting point, then add any sectors you can infer from context \
(e.g. "minimum wage bill" implies labor_worker and business_owner even if those words aren't in py_sectors). \
Only use slugs from this list: {_VALID_SECTOR_SLUGS}. \
If the story has no direct impact on any citizen archetype (e.g. pure political infighting, \
celebrity news, abstract statistics), return an empty array.
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
        if article.get("py_sectors"):
            slugs = [s["slug"] for s in article["py_sectors"]]
            hints.append(f"py_sectors={slugs}")
        if hints:
            lines.append(f"    [{', '.join(hints)}]")
    return "\n".join(lines)
