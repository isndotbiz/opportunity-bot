#!/usr/bin/env python3
"""
Product Hunt scraper for automation opportunities
Scrapes products tagged with automation, productivity, AI tools, etc.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
from scrapers.config import (
    RATE_LIMIT_WEB,
    MAX_OPPORTUNITIES_PER_SOURCE,
    MIN_REVENUE_MENTION
)


class ProductHuntScraper:
    def __init__(self):
        """Initialize Product Hunt scraper"""
        self.base_url = "https://www.producthunt.com"
        self.opportunities = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape_topic(self, topic: str, pages: int = 2) -> List[Dict]:
        """Scrape products from a specific topic"""
        products = []

        for page in range(1, pages + 1):
            try:
                url = f"{self.base_url}/topics/{topic}"
                print(f"    Scraping {topic} (page {page})...")

                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code != 200:
                    print(f"    ⚠️  Failed to fetch {topic}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find product cards (structure may vary, this is approximate)
                # Product Hunt's HTML structure changes, so we look for common patterns
                product_links = soup.find_all('a', href=re.compile(r'/posts/'))

                for link in product_links[:20]:  # Top 20 per page
                    try:
                        product_url = self.base_url + link['href']
                        if product_url not in [p.get('url') for p in products]:
                            product_data = self.scrape_product_page(product_url)
                            if product_data:
                                products.append(product_data)

                                if len(products) >= MAX_OPPORTUNITIES_PER_SOURCE:
                                    return products
                    except Exception as e:
                        continue

                time.sleep(60 / RATE_LIMIT_WEB)

            except Exception as e:
                print(f"    ⚠️  Error scraping {topic}: {e}")
                continue

        return products

    def scrape_product_page(self, url: str) -> Dict:
        """Scrape individual product page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_elem = soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Untitled Product"

            # Extract description
            desc_elem = soup.find('meta', attrs={'name': 'description'})
            description = desc_elem['content'] if desc_elem else ""

            # Extract tagline/description from page
            tagline = soup.find('div', class_=re.compile('tagline|description', re.I))
            if tagline:
                description = tagline.text.strip()

            # Look for automation/revenue keywords
            full_text = soup.get_text()

            revenue = self.extract_revenue(full_text)
            tech_stack = self.extract_tech_stack(full_text)

            # Check if it's automation-related
            automation_keywords = ['automat', 'passive', 'no-code', 'workflow', 'ai', 'schedule']
            is_automation = any(keyword in full_text.lower() for keyword in automation_keywords)

            if not is_automation:
                return None

            return {
                'title': title,
                'description': description,
                'url': url,
                'source': 'Product Hunt',
                'revenue_claim': revenue,
                'revenue_potential': revenue,
                'tech_stack': tech_stack,
                'scraped_date': datetime.now().isoformat(),
                'tags': ['automation', 'product-hunt']
            }

        except Exception as e:
            print(f"    ⚠️  Error scraping product {url}: {e}")
            return None

    def extract_revenue(self, text: str) -> str:
        """Extract revenue mentions from text"""
        patterns = [
            r'\$\s*(\d+[,\d]*)\s*/?(?:mo|month|mrr|revenue)',
            r'(\d+[,\d]*)\s*\$\s*/?(?:mo|month|mrr)',
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
        """Extract technology mentions"""
        tech_keywords = {
            'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
            'FastAPI', 'Django', 'Flask', 'Vue', 'Svelte', 'Tailwind',
            'PostgreSQL', 'MongoDB', 'Redis', 'Stripe', 'GPT-4', 'OpenAI',
            'Claude', 'AWS', 'Vercel', 'Supabase', 'Firebase', 'No-code',
            'Zapier', 'Make', 'Airtable', 'Notion'
        }

        found_tech = []
        text_upper = text.upper()

        for tech in tech_keywords:
            if tech.upper() in text_upper:
                found_tech.append(tech)

        return ', '.join(found_tech[:5]) if found_tech else "Not specified"

    def scrape_all(self) -> List[Dict]:
        """Main scraping method"""
        print("\n💡 PRODUCT HUNT SCRAPING:")
        print("=" * 60)

        topics = [
            'productivity',
            'automation',
            'artificial-intelligence',
            'no-code',
            'developer-tools',
            'saas'
        ]

        all_products = []

        for topic in topics:
            products = self.scrape_topic(topic, pages=1)
            all_products.extend(products)
            print(f"    ✅ Found {len(products)} products in {topic}")

            if len(all_products) >= MAX_OPPORTUNITIES_PER_SOURCE:
                break

        print(f"\n✅ Total Product Hunt opportunities: {len(all_products)}")
        return all_products[:MAX_OPPORTUNITIES_PER_SOURCE]


if __name__ == "__main__":
    scraper = ProductHuntScraper()
    products = scraper.scrape_all()
    print(f"\nScraped {len(products)} products from Product Hunt")
    for p in products[:3]:
        print(f"  - {p['title']}")
