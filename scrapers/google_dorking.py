#!/usr/bin/env python3
"""
Google Dorking scraper for finding hidden business opportunities
Uses Google Custom Search API
"""

import re
import time
import requests
from typing import List, Dict
from datetime import datetime
from scrapers.config import (
    GOOGLE_API_KEY,
    GOOGLE_CSE_ID,
    GOOGLE_DORK_QUERIES,
    RATE_LIMIT_GOOGLE
)


class GoogleDorkingScraper:
    def __init__(self):
        """Initialize Google Custom Search API client"""
        self.api_key = GOOGLE_API_KEY
        self.cse_id = GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.opportunities = []

        if not self.api_key or not self.cse_id:
            print("⚠️  Google Custom Search API credentials missing!")
            print("   Get API key: https://developers.google.com/custom-search/v1/overview")
            print("   Get CSE ID: https://cse.google.com/cse/all")
            print("   Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables")
            print("   Falling back to web scraping mode...")
            self.use_api = False
        else:
            self.use_api = True

    def extract_revenue(self, text: str) -> str:
        """Extract revenue mentions from text"""
        patterns = [
            r'\$\s*([\d,]+)\s*/?(?:mo|month|mrr|per month)',
            r'([\d,]+)\s*\$\s*/?(?:mo|month|mrr)',
            r'revenue.*?\$\s*([\d,]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/month"

        return "Not specified"

    def search_with_api(self, query: str, num_results: int = 10) -> List[Dict]:
        """Search using Google Custom Search API"""
        results = []

        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': min(num_results, 10)  # API limit per request
            }

            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                for item in data.get('items', []):
                    result = {
                        'title': item.get('title', ''),
                        'description': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': 'Google Dork',
                        'query': query,
                        'revenue_claim': self.extract_revenue(
                            item.get('title', '') + ' ' + item.get('snippet', '')
                        ),
                        'tech_stack': 'Not specified',
                        'time_mentioned': 'Not specified',
                        'created': datetime.now().isoformat()
                    }
                    results.append(result)

            elif response.status_code == 429:
                print(f"    ⚠️  Rate limit exceeded, waiting...")
                time.sleep(60)
            else:
                print(f"    ❌ API error: {response.status_code}")

        except Exception as e:
            print(f"    ❌ Search error: {e}")

        return results

    def search_with_scraping(self, query: str) -> List[Dict]:
        """Fallback: scrape Google results (less reliable, use sparingly)"""
        print(f"    ⚠️  Using web scraping for: {query[:50]}...")
        results = []

        try:
            # Basic web scraping (Note: Google blocks this easily)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            response = requests.get(search_url, headers=headers, timeout=30)

            # Very basic parsing (Google changes HTML frequently)
            # This is intentionally limited - prefer using the API
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find search result divs (very fragile)
            search_divs = soup.find_all('div', class_='g')[:5]

            for div in search_divs:
                try:
                    title_elem = div.find('h3')
                    link_elem = div.find('a', href=True)
                    snippet_elem = div.find('div', class_=re.compile('VwiC3b'))

                    if title_elem and link_elem:
                        result = {
                            'title': title_elem.text.strip(),
                            'description': snippet_elem.text.strip() if snippet_elem else '',
                            'url': link_elem['href'],
                            'source': 'Google Dork (scraped)',
                            'query': query,
                            'revenue_claim': 'Not specified',
                            'tech_stack': 'Not specified',
                            'time_mentioned': 'Not specified',
                            'created': datetime.now().isoformat()
                        }
                        results.append(result)
                except:
                    continue

            time.sleep(10)  # Longer delay to avoid blocks

        except Exception as e:
            print(f"    ❌ Scraping error: {e}")

        return results

    def scrape_all(self) -> List[Dict]:
        """Execute all Google dork queries"""
        print("\n🔍 GOOGLE DORKING:")
        print("=" * 60)

        all_opportunities = []

        for query in GOOGLE_DORK_QUERIES:
            print(f"  🔎 Searching: {query[:60]}...")

            if self.use_api:
                results = self.search_with_api(query, num_results=10)
            else:
                results = self.search_with_scraping(query)

            all_opportunities.extend(results)
            print(f"    ✅ Found {len(results)} results")

            time.sleep(2)  # Rate limiting

        # Remove duplicates
        seen_urls = set()
        unique_opportunities = []
        for opp in all_opportunities:
            if opp['url'] not in seen_urls:
                seen_urls.add(opp['url'])
                unique_opportunities.append(opp)

        print(f"\n✅ Total Google dork opportunities: {len(unique_opportunities)}")
        return unique_opportunities


if __name__ == "__main__":
    # Test the scraper
    scraper = GoogleDorkingScraper()
    opportunities = scraper.scrape_all()

    print("\n📊 Sample Opportunities:")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   URL: {opp['url']}")
        print(f"   Query: {opp['query']}")
