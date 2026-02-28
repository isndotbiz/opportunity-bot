#!/usr/bin/env python3
"""
Configuration for opportunity scrapers
Add your API keys and settings here
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
_config_dir = Path(__file__).parent.parent
_env_file = _config_dir / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

# API Keys (set via environment variables or .env file)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "OpportunityBot/1.0")

# Google Custom Search (for dorking)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

# Scraping settings
REDDIT_SUBREDDITS = [
    "SideProject",
    "EntrepreneurRideAlong",
    "Entrepreneur",
    "SweatyStartup",
    "SaaS",
    "IMadeThis",
    "roasting"
]

REDDIT_SEARCH_QUERIES = [
    "made $ revenue",
    "earning $ per month",
    "MRR revenue",
    "passive income",
    "automated business",
    "AI side project revenue"
]

# Google dork queries for finding opportunities
GOOGLE_DORK_QUERIES = [
    'site:reddit.com "made $" "per month" automation',
    'site:indiehackers.com "$" "MRR" "automation"',
    'site:microconf.com revenue "automated"',
    '"I built" "revenue" "automated" site:twitter.com',
    'site:reddit.com/r/Entrepreneur "passive income" "$" automated',
]

# Indie Hackers settings
INDIEHACKERS_URLS = [
    "https://www.indiehackers.com/products?revenueVerification=stripe",
    "https://www.indiehackers.com/interviews",
]

# Rate limiting (requests per minute)
RATE_LIMIT_REDDIT = 30
RATE_LIMIT_WEB = 10
RATE_LIMIT_GOOGLE = 100  # Custom Search API limit

# Output settings
MAX_OPPORTUNITIES_PER_SOURCE = 50
MIN_REVENUE_MENTION = 100  # Minimum $ amount to consider

# Paths
WORKSPACE = Path(__file__).parent.parent.absolute()  # opportunity-research-bot directory
CACHE_DIR = WORKSPACE / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
