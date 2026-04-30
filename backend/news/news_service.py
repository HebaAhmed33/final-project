# SmartISMS News Aggregation Service.
#
# Fetches real cybersecurity and GRC-related articles from public RSS feeds,
# normalizes output fields, deduplicates, sorts by date, and categorizes.
#
# Includes an in-memory cache (6-hour TTL) to avoid redundant external requests.
# Falls back gracefully to an empty list with error info when feeds are unreachable.

import time
import traceback
from datetime import datetime, timezone

import feedparser

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours
MAX_ARTICLES = 30

# Public RSS feeds — free, no API key required
RSS_FEEDS = [
    {
        "url": "https://feeds.feedburner.com/TheHackersNews",
        "source_name": "The Hacker News",
    },
    {
        "url": "https://www.bleepingcomputer.com/feed/",
        "source_name": "BleepingComputer",
    },
    {
        "url": "https://www.cisa.gov/news.xml",
        "source_name": "CISA",
    },
    {
        "url": "https://feeds.feedburner.com/securityweek",
        "source_name": "SecurityWeek",
    },
    {
        "url": "https://www.darkreading.com/rss.xml",
        "source_name": "Dark Reading",
    },
]

# ---------------------------------------------------------------------------
# Category classification rules
# ---------------------------------------------------------------------------

CATEGORY_RULES = {
    "breach":        ["breach", "leak", "exposed", "stolen", "hack", "ransomware", "phishing", "attack"],
    "vulnerability": ["vulnerability", "cve", "exploit", "zero-day", "patch", "flaw", "rce", "bug"],
    "compliance":    ["compliance", "iso", "nist", "pci", "hipaa", "sama", "audit", "regulation", "gdpr", "standard", "framework"],
    "governance":    ["governance", "risk management", "board", "oversight", "policy", "grc", "ciso"],
}


def _categorize_article(title: str, description: str) -> str:
    """Assign a category based on keyword presence in title + description."""
    text = f"{title} {description}".lower()
    for category, triggers in CATEGORY_RULES.items():
        for trigger in triggers:
            if trigger in text:
                return category
    return "general"


# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_cache = {
    "data": None,
    "timestamp": 0,
}


def _is_cache_valid() -> bool:
    return (
        _cache["data"] is not None
        and (time.time() - _cache["timestamp"]) < CACHE_TTL_SECONDS
    )


# ---------------------------------------------------------------------------
# RSS feed parser
# ---------------------------------------------------------------------------

def _parse_published_date(entry) -> str:
    """Extract and normalize the publication date from a feed entry."""
    # feedparser provides parsed time tuples in 'published_parsed' or 'updated_parsed'
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                dt = datetime(*parsed[:6], tzinfo=timezone.utc)
                return dt.isoformat()
            except Exception:
                pass

    # Fallback: raw string fields
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            return raw

    return ""


def _fetch_rss_feed(feed_config: dict) -> list:
    """Fetch and parse articles from a single RSS feed."""
    url = feed_config["url"]
    source_name = feed_config["source_name"]
    articles = []

    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            # Feed is malformed and has no entries
            print(f"[NEWS] Warning: RSS feed {source_name} returned no entries (bozo={feed.bozo})")
            return []

        for entry in feed.entries[:10]:  # Limit per-feed
            title = getattr(entry, "title", "").strip()
            if not title:
                continue

            description = getattr(entry, "summary", "") or getattr(entry, "description", "")
            # Strip HTML tags from description (basic cleanup)
            if description:
                import re
                description = re.sub(r"<[^>]+>", "", description).strip()
                # Truncate long descriptions
                if len(description) > 300:
                    description = description[:297] + "..."

            link = getattr(entry, "link", "")
            published_at = _parse_published_date(entry)

            articles.append({
                "title": title,
                "source": source_name,
                "description": description,
                "url": link,
                "published_at": published_at,
                "category": _categorize_article(title, description),
            })

    except Exception as exc:
        print(f"[NEWS] Error fetching RSS feed '{source_name}': {exc}")
        traceback.print_exc()

    return articles


# ---------------------------------------------------------------------------
# Core aggregation logic
# ---------------------------------------------------------------------------

def _fetch_all_feeds() -> list:
    """Fetch articles from all configured RSS feeds, deduplicate, sort by date."""
    all_articles = []

    for feed_config in RSS_FEEDS:
        articles = _fetch_rss_feed(feed_config)
        all_articles.extend(articles)

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for article in all_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)

    # Also deduplicate by title (in case same article appears in multiple feeds)
    seen_titles = set()
    deduped = []
    for article in unique:
        title_key = article["title"].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            deduped.append(article)

    # Sort by published_at descending (newest first)
    def sort_key(a):
        pub = a.get("published_at", "")
        if not pub:
            return ""
        return pub

    deduped.sort(key=sort_key, reverse=True)

    return deduped[:MAX_ARTICLES]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_news() -> dict:
    """
    Primary entry point for the /news endpoint.
    Fetches real articles from public RSS feeds with caching.
    Returns is_live=True when real data is served, is_live=False on error.
    """
    # Return cached data if still valid
    if _is_cache_valid():
        return _cache["data"]

    try:
        articles = _fetch_all_feeds()

        if articles:
            result = {
                "articles": articles,
                "is_live": True,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source_count": len(RSS_FEEDS),
            }

            # Update cache
            _cache["data"] = result
            _cache["timestamp"] = time.time()

            print(f"[NEWS] Successfully fetched {len(articles)} articles from {len(RSS_FEEDS)} RSS feeds")
            return result
        else:
            print("[NEWS] Warning: All RSS feeds returned empty results")
            return {
                "articles": [],
                "is_live": False,
                "error": "All news feeds returned empty results. Please try again later.",
            }

    except Exception as exc:
        print(f"[NEWS] Error during news aggregation: {exc}")
        traceback.print_exc()
        return {
            "articles": [],
            "is_live": False,
            "error": "Unable to load live news right now. Please try again later.",
        }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    result = fetch_news()
    print(json.dumps(result, indent=2))
    print(f"\nTotal articles: {len(result['articles'])}")
    if result["articles"]:
        categories = set(a["category"] for a in result["articles"])
        print(f"Categories: {categories}")
        print(f"Sources: {set(a['source'] for a in result['articles'])}")
