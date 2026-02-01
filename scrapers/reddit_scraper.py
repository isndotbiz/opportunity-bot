#!/usr/bin/env python3
"""
Reddit scraper for business opportunities using PRAW (Python Reddit API Wrapper)
"""

import re
import time
import praw
from datetime import datetime, timedelta
from typing import List, Dict
from scrapers.config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_SUBREDDITS,
    REDDIT_SEARCH_QUERIES,
    MAX_OPPORTUNITIES_PER_SOURCE,
    MIN_REVENUE_MENTION
)


class RedditScraper:
    def __init__(self):
        """Initialize Reddit API client"""
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            raise ValueError(
                "Reddit API credentials missing!\n"
                "Get them from: https://www.reddit.com/prefs/apps\n"
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
            )

        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            check_for_async=False
        )
        self.opportunities = []

    def extract_revenue(self, text: str) -> str:
        """Extract revenue claims from text"""
        # Patterns for revenue mentions
        patterns = [
            r'\$\s*(\d+[,\d]*)\s*/?(?:mo|month|mrr)',
            r'(\d+[,\d]*)\s*\$\s*/?(?:mo|month|mrr)',
            r'revenue.*?\$\s*(\d+[,\d]*)',
            r'making.*?\$\s*(\d+[,\d]*)',
            r'earning.*?\$\s*(\d+[,\d]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                try:
                    if int(amount) >= MIN_REVENUE_MENTION:
                        return f"${amount}/month"
                except ValueError:
                    continue

        return "Not specified"

    def extract_tech_stack(self, text: str) -> str:
        """Extract technology mentions from text"""
        tech_keywords = {
            'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
            'FastAPI', 'Django', 'Flask', 'Vue', 'Svelte', 'Tailwind',
            'PostgreSQL', 'MongoDB', 'Redis', 'Stripe', 'GPT-4', 'OpenAI',
            'Claude', 'AWS', 'Vercel', 'Supabase', 'Firebase', 'Docker'
        }

        found_tech = []
        text_upper = text.upper()

        for tech in tech_keywords:
            if tech.upper() in text_upper:
                found_tech.append(tech)

        return ', '.join(found_tech[:5]) if found_tech else "Not specified"

    def is_relevant_post(self, post) -> bool:
        """Check if post is relevant (mentions revenue/automation)"""
        text = (post.title + " " + post.selftext).lower()

        # Must mention money or revenue
        money_keywords = ['$', 'revenue', 'mrr', 'arr', 'income', 'earning', 'profit']
        has_money = any(keyword in text for keyword in money_keywords)

        # Bonus if mentions automation/passive/saas
        automation_keywords = ['automat', 'passive', 'saas', 'ai', 'api', 'tool', 'app']
        has_automation = any(keyword in text for keyword in automation_keywords)

        return has_money and (has_automation or post.score > 50)

    def scrape_subreddit(self, subreddit_name: str, time_filter: str = 'month', limit: int = 100) -> List[Dict]:
        """Scrape a specific subreddit for opportunities"""
        print(f"  📡 Scraping r/{subreddit_name}...")
        found = []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Search with keywords
            for query in REDDIT_SEARCH_QUERIES:
                try:
                    for post in subreddit.search(query, time_filter=time_filter, limit=limit):
                        if self.is_relevant_post(post):
                            opportunity = {
                                'title': post.title,
                                'description': post.selftext[:500] if post.selftext else post.title,
                                'source': f'Reddit r/{subreddit_name}',
                                'url': f'https://reddit.com{post.permalink}',
                                'score': post.score,
                                'created': datetime.fromtimestamp(post.created_utc).isoformat(),
                                'revenue_claim': self.extract_revenue(post.title + " " + post.selftext),
                                'tech_stack': self.extract_tech_stack(post.title + " " + post.selftext),
                                'time_mentioned': "Not specified"
                            }

                            found.append(opportunity)

                            if len(found) >= MAX_OPPORTUNITIES_PER_SOURCE:
                                break

                    time.sleep(1)  # Rate limiting

                except Exception as e:
                    print(f"    ⚠️  Search error for '{query}': {e}")
                    continue

            print(f"    ✅ Found {len(found)} opportunities")

        except Exception as e:
            print(f"    ❌ Error accessing r/{subreddit_name}: {e}")

        return found

    def scrape_all(self) -> List[Dict]:
        """Scrape all configured subreddits"""
        print("\n🔴 REDDIT SCRAPING:")
        print("=" * 60)

        all_opportunities = []

        for subreddit_name in REDDIT_SUBREDDITS:
            opportunities = self.scrape_subreddit(subreddit_name, time_filter='month', limit=50)
            all_opportunities.extend(opportunities)
            time.sleep(2)  # Rate limiting between subreddits

        # Remove duplicates by URL
        seen_urls = set()
        unique_opportunities = []
        for opp in all_opportunities:
            if opp['url'] not in seen_urls:
                seen_urls.add(opp['url'])
                unique_opportunities.append(opp)

        print(f"\n✅ Total Reddit opportunities: {len(unique_opportunities)}")
        return unique_opportunities


if __name__ == "__main__":
    # Test the scraper
    scraper = RedditScraper()
    opportunities = scraper.scrape_all()

    # Print samples
    print("\n📊 Sample Opportunities:")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   Revenue: {opp['revenue_claim']}")
        print(f"   Score: {opp['score']}")
        print(f"   URL: {opp['url']}")
