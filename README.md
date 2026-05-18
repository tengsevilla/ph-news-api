# ph-news-api

Philippine news scraper and civic impact classifier. Scrapes 10 news and government sources daily, classifies each article with OpenAI, and exposes structured data through a FastAPI service backed by PostgreSQL.

---

## Pre-Deploy Checklist (Railway)

Complete these steps in order before your first deployment.

### 1. Add the Postgres plugin

In your Railway project dashboard, click **+ New** → **Database** → **PostgreSQL**. Railway will auto-inject `DATABASE_URL` into your service's environment — no manual copying needed.

### 2. Set environment variables

In Railway → your service → **Variables**, add:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | Your OpenAI API key (`sk-...`) |
| `SCRAPE_SECRET` | A random secret string (protects `POST /scrape`) |

`DATABASE_URL` is injected automatically by the Postgres plugin.

### 3. Deploy the service

Push your code. Railway builds via nixpacks and starts:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Initialize the database schema

After the first deploy, open a Railway shell (or run via the CLI) and execute:
```bash
python db/init_db.py
```

This creates all tables. For subsequent schema additions, run `python db/migrate.py` instead — it only adds missing columns and is safe to run repeatedly.

### 5. Set up the daily cron trigger

Railway does not have a built-in cron scheduler. Use an external service (e.g. [cron-job.org](https://cron-job.org)) to call `POST /scrape` daily.

- **Schedule:** `0 16 * * *` (16:00 UTC = midnight Philippine time)
- **URL:** `https://your-service.railway.app/scrape`
- **Method:** `POST`
- **Header:** `Authorization: Bearer <your SCRAPE_SECRET>`

### 6. Verify

```bash
curl https://your-service.railway.app/health
# → {"status": "ok"}

curl -X POST https://your-service.railway.app/scrape \
  -H "Authorization: Bearer <SCRAPE_SECRET>"
# → {"status": "queued", "message": "..."}
```

---

## API Endpoints

### `POST /scrape`

Triggers the full pipeline: scrape → classify → persist. Requires `Authorization` header if `SCRAPE_SECRET` is set.

Runs asynchronously — returns `202 Accepted` immediately and processes in the background. Poll `GET /scrape/status` for the result.

**Headers**
```
Authorization: Bearer <SCRAPE_SECRET>
```

**Query parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `dry_run` | bool | `false` | Classify and return results without writing to the database. Runs synchronously. |

**Response — async (default)**
```json
{
  "status": "queued",
  "message": "Scrape started. Poll GET /scrape/status for the result."
}
```

**Response — `dry_run=true`**
```json
{
  "date": "2026-05-18",
  "scraped_at": "2026-05-18T16:00:00Z",
  "raw_article_count": 87,
  "topic_count": 34,
  "dry_run": true,
  "topics": [...]
}
```

**409 Conflict** — returned if a scrape is already running:
```json
{
  "status": "already_running",
  "message": "A scrape is already in progress. Check GET /scrape/status.",
  "started_at": "2026-05-18T16:00:01Z"
}
```

---

### `GET /scrape/status`

Returns the result of the most recent scrape run. Requires `Authorization` header if `SCRAPE_SECRET` is set.

**Response — success**
```json
{
  "status": "success",
  "date": "2026-05-18",
  "scraped_at": "2026-05-18T16:00:00Z",
  "raw_article_count": 87,
  "topic_count": 34,
  "dry_run": false
}
```

**Response — error**
```json
{
  "status": "error",
  "error": "OpenAI API timeout"
}
```

**Response — never run**
```json
{ "status": "never_run" }
```

---

### `GET /topics`

Returns a list of classified topics, newest first.

**Query parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `date` | string | — | Filter by date (`YYYY-MM-DD`) |
| `category` | string | — | Filter by category (e.g. `politics`, `economy`, `health`) |
| `limit` | int | `50` | Max results, up to `200` |

**Response**
```json
[
  {
    "id": "uuid",
    "topic": "Senate Passes Anti-ENDO Bill",
    "summary": "...",
    "category": "politics",
    "sentiment": "positive",
    "impact_level": "national",
    "event_type": "legislation",
    "urgency": "immediate",
    "resolution_status": "developing",
    "government_response": "yes",
    "region_primary": "National",
    "severity": 3,
    "affected_population_estimate": "10 million workers",
    "civic_action": "Contact your senator to express support.",
    "keywords": ["endo", "labor", "senate"],
    "policy_tags": ["security_of_tenure", "labor_reform"],
    "confidence_score": 0.91,
    "source_count": 4,
    "digest_date": "2026-05-18",
    "created_at": "2026-05-18T16:05:12Z",
    "affected_sectors": [
      { "slug": "labor_worker", "intensity": "high" }
    ],
    "sources": [
      {
        "source": "gma_news",
        "url": "https://...",
        "title": "Senate approves anti-endo measure",
        "published_at": "2026-05-18T10:00:00"
      }
    ]
  }
]
```

---

### `GET /topics/{date}`

Returns the full daily digest for a given date, including all topics and digest metadata.

**Path parameters**

| Param | Format | Example |
|-------|--------|---------|
| `date` | `YYYY-MM-DD` | `2026-05-18` |

**Response**
```json
{
  "date": "2026-05-18",
  "digest": {
    "scraped_at": "2026-05-18T16:05:00Z",
    "raw_article_count": 87,
    "topic_count": 34
  },
  "topics": [...]
}
```

---

### `GET /politicians`

Returns all tracked politicians ordered by `impact_score` descending.

**Response**
```json
[
  {
    "slug": "juan-dela-cruz",
    "name": "Juan Dela Cruz",
    "position": "Senator",
    "party": "PDP-Laban",
    "branch": "legislative",
    "province": "National",
    "positive_count": 12,
    "negative_count": 5,
    "neutral_count": 3,
    "total_mentions": 20,
    "impact_score": 0.35,
    "last_updated": "2026-05-18T16:05:00Z"
  }
]
```

`impact_score` = (positive − negative) / total, ranging from **−1.0** (purely harmful) to **+1.0** (purely beneficial).

---

### `GET /politicians/{slug}`

Returns a politician's full profile and complete impact history.

**Path parameters**

| Param | Format | Example |
|-------|--------|---------|
| `slug` | kebab-case name | `juan-dela-cruz` |

**Response**
```json
{
  "slug": "juan-dela-cruz",
  "name": "Juan Dela Cruz",
  "position": "Senator",
  "party": "PDP-Laban",
  "branch": "legislative",
  "province": "National",
  "positive_count": 12,
  "negative_count": 5,
  "neutral_count": 3,
  "total_mentions": 20,
  "impact_score": 0.35,
  "last_updated": "2026-05-18T16:05:00Z",
  "impact_history": [
    {
      "topic_id": "uuid",
      "topic": "Senate Passes Anti-ENDO Bill",
      "impact": "positive",
      "reason": "Authored and championed the security of tenure bill for workers.",
      "date": "2026-05-18",
      "topic_severity": 3,
      "topic_category": "politics"
    }
  ]
}
```

Returns `404` if the slug does not exist.

---

### `GET /sectors/{slug}`

Returns recent topics that affect a given citizen archetype.

**Path parameters**

| Param | Format | Example |
|-------|--------|---------|
| `slug` | sector slug | `farmer`, `ofw`, `driver` |

**Query parameters**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | `20` | Max results, up to `100` |

**Response**
```json
{
  "sector": "farmer",
  "topics": [...]
}
```

**Available sector slugs**

`farmer` · `fisherman` · `miner` · `forest_worker` · `health_worker` · `social_worker` · `senior_citizen` · `pwd` · `teacher` · `student` · `labor_worker` · `kasambahay` · `security_guard` · `bpo_worker` · `retail_worker` · `hospitality_worker` · `driver` · `seafarer` · `delivery_rider` · `business_owner` · `vendor` · `freelancer` · `ofw` · `government_employee` · `barangay_official` · `military_police` · `engineer_architect` · `lawyer` · `journalist` · `it_tech_worker` · `artist_creative` · `solo_parent` · `informal_settler` · `indigenous_people` · `youth` · `lgbtq` · `prisoner_returnee`

---

### `GET /health`

Health check endpoint used by Railway's healthcheck probe.

**Response**
```json
{ "status": "ok" }
```

---

## Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY and DATABASE_URL in .env

python db/init_db.py          # create tables
uvicorn main:app --reload --port 8000

# Dry-run (classifies but does not write to DB)
curl -X POST "http://localhost:8000/scrape?dry_run=true"

# Full run
curl -X POST http://localhost:8000/scrape \
  -H "Authorization: Bearer <SCRAPE_SECRET>"
```
