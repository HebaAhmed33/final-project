# SmartISMS News Aggregation Service.
#
# Fetches cybersecurity and GRC-related articles from GNews API,
# normalizes output fields, and categorizes articles.
#
# Includes a simple in-memory cache to avoid redundant API calls.
# Falls back to curated demo data when no API key is configured.

import os
import time
import requests

# ---------------------------------------------------------------------------
# Configuration  (all tunables in one place)
# ---------------------------------------------------------------------------

GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "")
GNEWS_BASE_URL = "https://gnews.io/api/v4/search"

KEYWORDS = [
    "cybersecurity",
    "data breach",
    "compliance",
    "ISO 27001",
    "NIST",
    "PCI DSS",
    "HIPAA",
    "SAMA cybersecurity",
    "vulnerability",
    "governance risk management",
]

CACHE_TTL_SECONDS = 600   # 10 minutes
MAX_ARTICLES = 30

# ---------------------------------------------------------------------------
# Category classification rules
# ---------------------------------------------------------------------------

CATEGORY_RULES = {
    "breach":        ["breach", "leak", "exposed", "stolen", "hack", "ransomware", "phishing"],
    "vulnerability": ["vulnerability", "CVE", "exploit", "zero-day", "patch", "flaw", "RCE"],
    "compliance":    ["compliance", "ISO", "NIST", "PCI", "HIPAA", "SAMA", "audit", "regulation", "GDPR", "standard"],
    "governance":    ["governance", "risk management", "board", "oversight", "policy", "framework", "GRC", "CISO"],
}


def _categorize_article(title: str, description: str) -> str:
    """Assign a category based on keyword presence in title + description."""
    text = f"{title} {description}".lower()
    for category, triggers in CATEGORY_RULES.items():
        for trigger in triggers:
            if trigger.lower() in text:
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
# Core fetcher
# ---------------------------------------------------------------------------

def _fetch_from_gnews(query: str, max_results: int = 10) -> list:
    """Fetch articles from GNews API for a single query string."""
    if not GNEWS_API_KEY:
        return []

    params = {
        "q": query,
        "lang": "en",
        "max": min(max_results, 10),  # GNews free tier caps at 10
        "token": GNEWS_API_KEY,
    }

    try:
        resp = requests.get(GNEWS_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception:
        return []


def _normalize_article(raw: dict) -> dict:
    """Normalize a raw GNews article into the exact output schema."""
    title = raw.get("title", "")
    description = raw.get("description", "")
    return {
        "title": title,
        "source": raw.get("source", {}).get("name", "Unknown"),
        "description": description,
        "url": raw.get("url", ""),
        "published_at": raw.get("publishedAt", ""),
        "category": _categorize_article(title, description),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_cybersecurity_news() -> dict:
    """
    Fetch, normalize, deduplicate, and categorize cybersecurity news.
    Returns cached data if within TTL window.
    """
    if _is_cache_valid():
        return _cache["data"]

    all_raw = []
    for keyword in KEYWORDS:
        articles = _fetch_from_gnews(keyword, max_results=10)
        all_raw.extend(articles)

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for article in all_raw:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)

    # Normalize and limit
    normalized = [_normalize_article(a) for a in unique[:MAX_ARTICLES]]

    result = {"articles": normalized}

    # Update cache
    _cache["data"] = result
    _cache["timestamp"] = time.time()

    return result


# ---------------------------------------------------------------------------
# Fallback: curated demo data when no API key is configured
# ---------------------------------------------------------------------------

DEMO_ARTICLES = [
    {
        "title": "Critical Zero-Day Vulnerability Found in Enterprise Firewall Software",
        "source": "CyberNews",
        "description": "Security researchers have identified a critical zero-day vulnerability affecting multiple enterprise firewall vendors, with active exploitation observed in the wild.",
        "url": "https://example.com/zero-day-firewall",
        "published_at": "2026-04-18T08:00:00Z",
        "category": "vulnerability",
    },
    {
        "title": "Major Healthcare Provider Reports Data Breach Affecting 2.3M Patients",
        "source": "HealthSec Today",
        "description": "A large healthcare network disclosed a data breach that exposed personal health information of 2.3 million patients across 14 states.",
        "url": "https://example.com/healthcare-breach",
        "published_at": "2026-04-18T06:30:00Z",
        "category": "breach",
    },
    {
        "title": "NIST Releases Updated Cybersecurity Framework 3.0 Draft",
        "source": "GovTech Weekly",
        "description": "The National Institute of Standards and Technology published the latest draft of the Cybersecurity Framework 3.0, introducing expanded supply chain and AI governance controls.",
        "url": "https://example.com/nist-csf-3",
        "published_at": "2026-04-17T14:00:00Z",
        "category": "compliance",
    },
    {
        "title": "PCI DSS 4.1 Compliance Deadline Approaches for Global Merchants",
        "source": "Payment Security Journal",
        "description": "Organizations processing card payments have until Q3 2026 to meet all PCI DSS 4.1 requirements or face increased audit scrutiny and potential penalties.",
        "url": "https://example.com/pci-dss-deadline",
        "published_at": "2026-04-17T10:00:00Z",
        "category": "compliance",
    },
    {
        "title": "Ransomware Gang Exploits Unpatched VPN Appliances in New Campaign",
        "source": "Threat Intelligence Report",
        "description": "A sophisticated ransomware group is actively exploiting known CVEs in popular VPN appliances to gain initial access to corporate networks.",
        "url": "https://example.com/ransomware-vpn",
        "published_at": "2026-04-16T22:15:00Z",
        "category": "vulnerability",
    },
    {
        "title": "Board-Level Cybersecurity Governance Now Mandatory Under SEC Rules",
        "source": "Corporate Governance Today",
        "description": "New SEC regulations require publicly traded companies to disclose board-level cybersecurity governance practices and CISO reporting structures in annual filings.",
        "url": "https://example.com/sec-governance",
        "published_at": "2026-04-16T18:00:00Z",
        "category": "governance",
    },
    {
        "title": "European Union Adopts Stricter Cybersecurity Certification for Cloud Providers",
        "source": "EU Regulatory Monitor",
        "description": "New EU regulations mandate all cloud service providers serving public sector clients to achieve enhanced cybersecurity certification under the EUCS scheme.",
        "url": "https://example.com/eu-cloud-cert",
        "published_at": "2026-04-16T16:00:00Z",
        "category": "compliance",
    },
    {
        "title": "Financial Sector Faces Rising Credential Stuffing Attacks",
        "source": "FinSec Digest",
        "description": "Banks and fintech companies are reporting a 340% increase in credential stuffing attacks targeting online banking and payment portals.",
        "url": "https://example.com/credential-stuffing",
        "published_at": "2026-04-16T12:00:00Z",
        "category": "breach",
    },
    {
        "title": "SAMA Issues Enhanced Cybersecurity Framework Requirements for Financial Institutions",
        "source": "GCC Compliance Monitor",
        "description": "The Saudi Arabian Monetary Authority has released updated cybersecurity framework requirements mandating stronger access controls and incident response for all licensed financial entities.",
        "url": "https://example.com/sama-update",
        "published_at": "2026-04-16T09:00:00Z",
        "category": "compliance",
    },
    {
        "title": "Enterprise GRC Platform Market Projected to Grow 18% in 2026",
        "source": "Risk Management Weekly",
        "description": "Analyst reports show governance, risk management, and compliance platform adoption accelerating as organizations centralize oversight and automate policy enforcement.",
        "url": "https://example.com/grc-growth",
        "published_at": "2026-04-15T15:00:00Z",
        "category": "governance",
    },
    {
        "title": "ISO 27001:2025 Amendment Introduces AI Risk Management Controls",
        "source": "Standards Weekly",
        "description": "The latest amendment to ISO 27001 adds dedicated controls for artificial intelligence risk management, reflecting the growing intersection of AI and information security.",
        "url": "https://example.com/iso-27001-ai",
        "published_at": "2026-04-15T09:30:00Z",
        "category": "compliance",
    },
    {
        "title": "HIPAA Enforcement Actions Surge Following Telehealth Expansion",
        "source": "Healthcare Compliance Today",
        "description": "The HHS Office for Civil Rights has increased HIPAA enforcement activity, focusing on telehealth platforms that rapidly expanded without adequate security controls.",
        "url": "https://example.com/hipaa-telehealth",
        "published_at": "2026-04-15T07:00:00Z",
        "category": "compliance",
    },
    {
        "title": "Global Cybersecurity Spending Expected to Reach $290B by 2027",
        "source": "Industry Analyst",
        "description": "New market research forecasts worldwide cybersecurity spending will grow at 14% CAGR, driven by regulatory pressure, AI-powered threats, and zero-trust adoption.",
        "url": "https://example.com/cyber-spending",
        "published_at": "2026-04-14T18:00:00Z",
        "category": "general",
    },
]



def fetch_news() -> dict:
    """
    Primary entry point for the news endpoint.
    Uses live GNews API when a key is configured, otherwise returns demo data.
    """
    if GNEWS_API_KEY:
        result = fetch_cybersecurity_news()
        # Fallback to demo if live fetch returned nothing
        if not result.get("articles"):
            return {"articles": DEMO_ARTICLES, "is_live": False}
        result["is_live"] = True
        return result
    return {"articles": DEMO_ARTICLES, "is_live": False}


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    result = fetch_news()
    print(json.dumps(result, indent=2))
    print(f"\nTotal articles: {len(result['articles'])}")
    categories = set(a["category"] for a in result["articles"])
    print(f"Categories: {categories}")
