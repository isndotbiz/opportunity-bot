#!/usr/bin/env python3
"""
Indie Hackers scraper for verified business opportunities
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from scrapers.config import (
    INDIEHACKERS_URLS,
    MAX_OPPORTUNITIES_PER_SOURCE,
    RATE_LIMIT_WEB
)


class IndieHackersScraper:
    def __init__(self):
        """Initialize Indie Hackers scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.opportunities = []

    def extract_revenue(self, text: str) -> str:
        """Extract revenue from text"""
        patterns = [
            r'\$\s*([\d,]+)\s*/?(?:mo|month|mrr)',
            r'([\d,]+)\s*\$\s*/?(?:mo|month|mrr)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/month"

        return "Not specified"

    def scrape_products_page(self) -> List[Dict]:
        """Scrape Indie Hackers products page"""
        print("  📡 Scraping Indie Hackers products...")
        found = []

        try:
            url = "https://www.indiehackers.com/products?revenueVerification=stripe"
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}")
                return found

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find product cards (adjust selectors based on actual HTML)
            # This is a simplified version - you may need to adjust selectors
            products = soup.find_all('div', class_=re.compile('product|item|card'))[:MAX_OPPORTUNITIES_PER_SOURCE]

            for product in products:
                try:
                    # Extract product information
                    title_elem = product.find(['h2', 'h3', 'a'])
                    title = title_elem.text.strip() if title_elem else "Untitled"

                    # Get link
                    link_elem = product.find('a', href=True)
                    url = f"https://www.indiehackers.com{link_elem['href']}" if link_elem else ""

                    # Get description
                    desc_elem = product.find('p')
                    description = desc_elem.text.strip() if desc_elem else ""

                    # Get revenue if shown
                    revenue_text = product.get_text()
                    revenue = self.extract_revenue(revenue_text)

                    if title and len(title) > 5:  # Valid product
                        opportunity = {
                            'title': title,
                            'description': description[:500],
                            'source': 'Indie Hackers (Stripe Verified)',
                            'url': url,
                            'revenue_claim': revenue,
                            'tech_stack': 'Web-based SaaS',
                            'time_mentioned': 'Not specified',
                            'created': datetime.now().isoformat()
                        }
                        found.append(opportunity)

                except Exception as e:
                    continue

            print(f"    ✅ Found {len(found)} products")

        except Exception as e:
            print(f"    ❌ Error scraping products: {e}")

        return found

    def scrape_interviews(self) -> List[Dict]:
        """Scrape Indie Hackers interviews"""
        print("  📡 Scraping Indie Hackers interviews...")
        found = []

        try:
            url = "https://www.indiehackers.com/interviews"
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}")
                return found

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find interview cards
            interviews = soup.find_all('div', class_=re.compile('interview|post|article'))[:20]

            for interview in interviews:
                try:
                    title_elem = interview.find(['h2', 'h3', 'a'])
                    title = title_elem.text.strip() if title_elem else "Untitled Interview"

                    link_elem = interview.find('a', href=True)
                    url = f"https://www.indiehackers.com{link_elem['href']}" if link_elem else ""

                    desc_elem = interview.find('p')
                    description = desc_elem.text.strip() if desc_elem else ""

                    revenue_text = interview.get_text()
                    revenue = self.extract_revenue(revenue_text)

                    if title and len(title) > 10:
                        opportunity = {
                            'title': title,
                            'description': description[:500],
                            'source': 'Indie Hackers Interview',
                            'url': url,
                            'revenue_claim': revenue,
                            'tech_stack': 'Not specified',
                            'time_mentioned': 'Not specified',
                            'created': datetime.now().isoformat()
                        }
                        found.append(opportunity)

                except Exception as e:
                    continue

            print(f"    ✅ Found {len(found)} interviews")

        except Exception as e:
            print(f"    ❌ Error scraping interviews: {e}")

        return found

    def scrape_all(self) -> List[Dict]:
        """Scrape all Indie Hackers sources"""
        print("\n💡 INDIE HACKERS SCRAPING:")
        print("=" * 60)

        all_opportunities = []

        # Scrape products
        products = self.scrape_products_page()
        all_opportunities.extend(products)
        time.sleep(2)

        # Scrape interviews
        interviews = self.scrape_interviews()
        all_opportunities.extend(interviews)

        # Remove duplicates
        seen_urls = set()
        unique_opportunities = []
        for opp in all_opportunities:
            if opp['url'] and opp['url'] not in seen_urls:
                seen_urls.add(opp['url'])
                unique_opportunities.append(opp)

        print(f"\n✅ Total Indie Hackers opportunities: {len(unique_opportunities)}")
        return unique_opportunities


if __name__ == "__main__":
    # Test the scraper
    scraper = IndieHackersScraper()
    opportunities = scraper.scrape_all()

    print("\n📊 Sample Opportunities:")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   Revenue: {opp['revenue_claim']}")
        print(f"   URL: {opp['url']}")
