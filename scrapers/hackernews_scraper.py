#!/usr/bin/env python3
"""
Hacker News scraper for automation opportunities
Scrapes "Show HN", "Ask HN", and posts mentioning revenue/automation
"""

import re
import time
import requests
from datetime import datetime
from typing import List, Dict
from scrapers.config import (
    RATE_LIMIT_WEB,
    MAX_OPPORTUNITIES_PER_SOURCE,
    MIN_REVENUE_MENTION
)


class HackerNewsScraper:
    def __init__(self):
        """Initialize Hacker News scraper using Algolia Search API"""
        self.api_base = "https://hacker-news.firebaseio.com/v0"
        self.algolia_api = "https://hn.algolia.com/api/v1"
        self.opportunities = []

    def get_story(self, story_id: int) -> Dict:
        """Fetch a story by ID"""
        try:
            response = requests.get(f"{self.api_base}/item/{story_id}.json", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            pass
        return None

    def search_algolia(self, query: str, tags: str = None) -> List[Dict]:
        """Search HN using Algolia API"""
        opportunities = []

        try:
            params = {
                'query': query,
                'tags': tags if tags else 'story',
                'hitsPerPage': 30
            }

            response = requests.get(f"{self.algolia_api}/search", params=params, timeout=10)
            if response.status_code != 200:
                return []

            data = response.json()
            hits = data.get('hits', [])

            print(f"    Found {len(hits)} results for '{query}'")

            for hit in hits:
                title = hit.get('title', '')
                url = hit.get('url', f"https://news.ycombinator.com/item?id={hit.get('objectID')}")
                story_text = hit.get('story_text', '')

                # Create opportunity
                full_text = f"{title} {story_text}"
                opportunity = {
                    'title': title,
                    'description': story_text[:500] if story_text else title,
                    'url': url,
                    'source': 'Hacker News',
                    'revenue_claim': self.extract_revenue(full_text),
                    'revenue_potential': self.extract_revenue(full_text),
                    'tech_stack': self.extract_tech_stack(full_text),
                    'scraped_date': datetime.now().isoformat(),
                    'tags': ['hacker-news', 'algolia-search']
                }

                opportunities.append(opportunity)

                if len(opportunities) >= 20:
                    break

        except Exception as e:
            print(f"    ⚠️  Algolia search error: {e}")

        return opportunities

    def scrape_show_hn(self, limit: int = 100) -> List[Dict]:
        """Scrape 'Show HN' posts using Algolia search"""
        opportunities = []

        try:
            # Search for Show HN posts with automation/revenue keywords
            search_queries = [
                ('Show HN automation', 'show_hn'),
                ('Show HN side project revenue', 'show_hn'),
                ('Show HN saas', 'show_hn'),
                ('Show HN passive income', 'show_hn'),
                ('Show HN built', 'show_hn'),
            ]

            for query, tags in search_queries:
                results = self.search_algolia(query, tags)
                opportunities.extend(results)

                if len(opportunities) >= limit:
                    break

                time.sleep(1)

            # Remove duplicates by URL
            seen_urls = set()
            unique_opps = []
            for opp in opportunities:
                if opp['url'] not in seen_urls:
                    seen_urls.add(opp['url'])
                    unique_opps.append(opp)

            return unique_opps[:limit]

            for idx, story_id in enumerate(story_ids):
                try:
                    story = self.get_story(story_id)
                    if not story:
                        continue

                    title = story.get('title', '')
                    url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    text = story.get('text', '')

                    # Filter for relevant posts
                    is_show_hn = title.lower().startswith('show hn')
                    is_launch = any(kw in title.lower() for kw in ['launch', 'built', 'made', 'created'])

                    combined_text = f"{title} {text}"

                    # Check for automation/revenue keywords
                    automation_keywords = ['automat', 'passive', 'saas', 'ai tool', 'side project', 'revenue', 'mrr']
                    is_relevant = any(kw in combined_text.lower() for kw in automation_keywords)

                    if (is_show_hn or is_launch) and is_relevant:
                        # Fetch comments to get more details
                        comments_text = self.fetch_comments(story.get('kids', [])[:10])

                        full_text = f"{title} {text} {comments_text}"

                        opportunity = {
                            'title': title.replace('Show HN: ', '').replace('Launch HN: ', ''),
                            'description': text[:500] if text else title,
                            'url': url,
                            'source': 'Hacker News',
                            'revenue_potential': self.extract_revenue(full_text),
                            'tech_stack': self.extract_tech_stack(full_text),
                            'scraped_date': datetime.now().isoformat(),
                            'tags': ['hacker-news', 'show-hn' if is_show_hn else 'launch']
                        }

                        opportunities.append(opportunity)
                        print(f"      ✓ Found: {opportunity['title'][:50]}...")

                        if len(opportunities) >= MAX_OPPORTUNITIES_PER_SOURCE:
                            return opportunities

                    # Rate limiting
                    if idx % 10 == 0:
                        time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"    ⚠️  Error scraping Show HN: {e}")

        return opportunities

    def fetch_comments(self, comment_ids: List[int]) -> str:
        """Fetch comment text for additional context"""
        comments_text = ""

        for comment_id in comment_ids[:5]:  # Limit to first 5 comments
            try:
                comment = self.get_story(comment_id)
                if comment and 'text' in comment:
                    comments_text += " " + comment['text']
            except Exception:
                continue

        return comments_text[:1000]  # Limit total comment text

    def scrape_ask_hn(self, limit: int = 50) -> List[Dict]:
        """Scrape 'Ask HN' posts about making money/side projects"""
        opportunities = []

        try:
            # Get Ask HN stories
            response = requests.get(f"{self.api_base}/askstories.json", timeout=10)
            if response.status_code != 200:
                print("    ⚠️  Failed to fetch Ask HN stories")
                return []

            story_ids = response.json()[:limit]
            print(f"    Checking {len(story_ids)} Ask HN stories...")

            for story_id in story_ids:
                try:
                    story = self.get_story(story_id)
                    if not story:
                        continue

                    title = story.get('title', '')
                    text = story.get('text', '')

                    # Filter for revenue/side project discussions
                    money_keywords = ['make money', 'side project', 'revenue', 'mrr', 'passive income', 'automation', 'profitable']
                    is_relevant = any(kw in title.lower() for kw in money_keywords)

                    if is_relevant:
                        # Fetch top comments for opportunities
                        comments_text = self.fetch_comments(story.get('kids', [])[:20])

                        # Extract opportunities from comments
                        comment_opportunities = self.extract_opportunities_from_text(
                            f"{title} {text} {comments_text}",
                            f"https://news.ycombinator.com/item?id={story_id}"
                        )

                        opportunities.extend(comment_opportunities)

                        if len(opportunities) >= MAX_OPPORTUNITIES_PER_SOURCE:
                            return opportunities

                    time.sleep(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"    ⚠️  Error scraping Ask HN: {e}")

        return opportunities

    def extract_opportunities_from_text(self, text: str, source_url: str) -> List[Dict]:
        """Extract opportunity mentions from text"""
        opportunities = []

        # Look for patterns like "I built X and make $Y"
        patterns = [
            r"(?:I|We)\s+(?:built|made|created|launched)\s+([^.!?]{10,100})",
            r"(?:my|our)\s+(?:side project|saas|tool|app)\s+([^.!?]{10,100})",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()

                if len(description) > 20:  # Meaningful description
                    opportunity = {
                        'title': description[:100],
                        'description': description[:500],
                        'url': source_url,
                        'source': 'Hacker News (Ask HN)',
                        'revenue_potential': self.extract_revenue(text),
                        'tech_stack': self.extract_tech_stack(description),
                        'scraped_date': datetime.now().isoformat(),
                        'tags': ['hacker-news', 'ask-hn']
                    }
                    opportunities.append(opportunity)

        return opportunities[:3]  # Max 3 per Ask HN thread

    def extract_revenue(self, text: str) -> str:
        """Extract revenue mentions from text"""
        patterns = [
            r'\$\s*(\d+[,\d]*)\s*/?(?:mo|month|mrr|arr|revenue)',
            r'(\d+[,\d]*)\s*\$\s*/?(?:mo|month|mrr)',
            r'making.*?\$\s*(\d+[,\d]*)',
            r'earning.*?\$\s*(\d+[,\d]*)',
            r'revenue.*?\$\s*(\d+[,\d]*)',
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
        """Extract technology mentions"""
        tech_keywords = {
            'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
            'Go', 'Rust', 'Ruby', 'Rails', 'Django', 'Flask', 'Vue', 'Svelte',
            'PostgreSQL', 'MongoDB', 'Redis', 'Stripe', 'GPT-4', 'OpenAI',
            'Claude', 'AWS', 'Vercel', 'Supabase', 'Firebase', 'Docker',
            'Kubernetes', 'Tailwind', 'FastAPI'
        }

        found_tech = []
        text_upper = text.upper()

        for tech in tech_keywords:
            if tech.upper() in text_upper:
                found_tech.append(tech)

        return ', '.join(found_tech[:5]) if found_tech else "Not specified"

    def scrape_all(self) -> List[Dict]:
        """Main scraping method"""
        print("\n🧡 HACKER NEWS SCRAPING:")
        print("=" * 60)

        all_opportunities = []

        # Scrape Show HN
        print("  📡 Scraping Show HN posts...")
        show_hn_opps = self.scrape_show_hn(limit=100)
        all_opportunities.extend(show_hn_opps)
        print(f"    ✅ Found {len(show_hn_opps)} Show HN opportunities")

        # Scrape Ask HN
        if len(all_opportunities) < MAX_OPPORTUNITIES_PER_SOURCE:
            print("  📡 Scraping Ask HN posts...")
            ask_hn_opps = self.scrape_ask_hn(limit=50)
            all_opportunities.extend(ask_hn_opps)
            print(f"    ✅ Found {len(ask_hn_opps)} Ask HN opportunities")

        print(f"\n✅ Total Hacker News opportunities: {len(all_opportunities)}")
        return all_opportunities[:MAX_OPPORTUNITIES_PER_SOURCE]


if __name__ == "__main__":
    scraper = HackerNewsScraper()
    opportunities = scraper.scrape_all()
    print(f"\nScraped {len(opportunities)} opportunities from Hacker News")
    for opp in opportunities[:5]:
        print(f"  - {opp['title']}")
