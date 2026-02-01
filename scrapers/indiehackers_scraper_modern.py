#!/usr/bin/env python3
"""
Modern Indie Hackers scraper with Crawl4AI and Pydantic
Handles JavaScript-heavy pages with proper rendering
"""

import asyncio
import re
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from models import (
    Opportunity,
    OpportunityMetadata,
    OpportunitySource,
    ScraperConfig
)
from scrapers.crawl4ai_base import Crawl4AIBase
from scrapers.config import MAX_OPPORTUNITIES_PER_SOURCE

import logging

logger = logging.getLogger(__name__)


class IndieHackersScraperModern(Crawl4AIBase):
    """Modern Indie Hackers scraper using Crawl4AI for JavaScript rendering"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize Indie Hackers scraper"""
        super().__init__(config)
        logger.info("✅ Indie Hackers scraper initialized")

    def parse_product_card(self, card_html: str, source_url: str) -> Optional[Opportunity]:
        """
        Parse product card HTML into Opportunity

        Args:
            card_html: HTML of product card
            source_url: Page URL where found

        Returns:
            Validated Opportunity or None
        """
        try:
            soup = BeautifulSoup(card_html, 'html.parser')

            # Extract title
            title_elem = soup.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract description
            desc_elem = soup.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else title

            # Extract link
            link_elem = soup.find('a', href=True)
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if not href.startswith('http'):
                    href = f"https://www.indiehackers.com{href}"
            else:
                href = source_url

            # Extract revenue from card text
            card_text = soup.get_text()
            revenue_info = self.extract_revenue(card_text)

            if revenue_info:
                revenue_claim, revenue_amount, revenue_period = revenue_info
            else:
                revenue_claim = None
                revenue_amount = None
                revenue_period = None

            # Extract tech stack
            tech_stack = self.extract_tech_stack(card_text)

            # Determine tags
            tags = ['indie-hackers', 'validated']
            if 'stripe' in card_text.lower() or 'verified' in source_url.lower():
                tags.append('stripe-verified')
            if revenue_amount and revenue_amount >= 1000:
                tags.append('profitable')

            # Build metadata
            metadata = OpportunityMetadata(
                title=title,
                description=description,
                source=OpportunitySource.INDIE_HACKERS,
                source_url=href,
                revenue_claim=revenue_claim,
                revenue_amount=revenue_amount,
                revenue_period=revenue_period,
                tech_stack=tech_stack,
                created_at=datetime.now(),
                discovered_at=datetime.now(),
                tags=tags
            )

            opportunity = Opportunity(
                id=f"ih_{hash(href)}",
                metadata=metadata
            )

            return opportunity

        except Exception as e:
            logger.error(f"❌ Error parsing product card: {e}")
            return None

    async def scrape_products_page(self, max_products: int = 30) -> List[Opportunity]:
        """
        Scrape Indie Hackers products page (Stripe verified)

        Args:
            max_products: Maximum products to extract

        Returns:
            List of validated Opportunities
        """
        logger.info("📡 Scraping Indie Hackers products page...")

        url = "https://www.indiehackers.com/products?revenueVerification=stripe"

        # Crawl with JavaScript rendering
        result = await self.crawl_url(url, extract_links=True)

        if not result.success:
            logger.error(f"❌ Failed to crawl products page: {result.error}")
            return []

        opportunities = []

        try:
            # Parse markdown for structured content
            soup = BeautifulSoup(result.html or '', 'html.parser')

            # Find product cards (adjust selectors based on actual HTML structure)
            # Indie Hackers uses different class names, we'll try multiple selectors
            product_selectors = [
                {'class': re.compile(r'product.*card', re.I)},
                {'class': re.compile(r'item.*card', re.I)},
                {'class': re.compile(r'listing', re.I)},
                {'data-test': re.compile(r'product', re.I)},
            ]

            products = []
            for selector in product_selectors:
                products = soup.find_all('div', selector)
                if products:
                    break

            # Fallback: if no products found with specific selectors, try generic approach
            if not products:
                # Look for article or section tags that might contain products
                products = soup.find_all(['article', 'section'], limit=max_products)

            logger.info(f"  Found {len(products)} potential product elements")

            for i, product in enumerate(products[:max_products], 1):
                opportunity = self.parse_product_card(str(product), url)

                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(
                        f"  [{i}/{min(len(products), max_products)}] ✅ {opportunity.metadata.title[:50]}..."
                    )

            logger.info(f"✅ Extracted {len(opportunities)} products")

        except Exception as e:
            logger.error(f"❌ Error parsing products page: {e}")

        return opportunities

    async def scrape_interviews(self, max_interviews: int = 20) -> List[Opportunity]:
        """
        Scrape Indie Hackers interviews

        Args:
            max_interviews: Maximum interviews to extract

        Returns:
            List of validated Opportunities
        """
        logger.info("📡 Scraping Indie Hackers interviews...")

        url = "https://www.indiehackers.com/interviews"

        result = await self.crawl_url(url, extract_links=True)

        if not result.success:
            logger.error(f"❌ Failed to crawl interviews page: {result.error}")
            return []

        opportunities = []

        try:
            soup = BeautifulSoup(result.html or '', 'html.parser')

            # Find interview cards
            interview_selectors = [
                {'class': re.compile(r'interview', re.I)},
                {'class': re.compile(r'post.*card', re.I)},
                {'class': re.compile(r'story', re.I)},
            ]

            interviews = []
            for selector in interview_selectors:
                interviews = soup.find_all('div', selector)
                if interviews:
                    break

            if not interviews:
                interviews = soup.find_all(['article', 'section'], limit=max_interviews)

            logger.info(f"  Found {len(interviews)} potential interview elements")

            for i, interview in enumerate(interviews[:max_interviews], 1):
                opportunity = self.parse_interview_card(str(interview), url)

                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(
                        f"  [{i}/{min(len(interviews), max_interviews)}] ✅ {opportunity.metadata.title[:50]}..."
                    )

            logger.info(f"✅ Extracted {len(opportunities)} interviews")

        except Exception as e:
            logger.error(f"❌ Error parsing interviews page: {e}")

        return opportunities

    def parse_interview_card(self, card_html: str, source_url: str) -> Optional[Opportunity]:
        """Parse interview card into Opportunity"""
        try:
            soup = BeautifulSoup(card_html, 'html.parser')

            # Extract title
            title_elem = soup.find(['h2', 'h3', 'h4'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract description
            desc_elem = soup.find('p')
            description = desc_elem.get_text(strip=True) if desc_elem else title

            # Extract link
            link_elem = soup.find('a', href=True)
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if not href.startswith('http'):
                    href = f"https://www.indiehackers.com{href}"
            else:
                href = source_url

            # Extract revenue
            card_text = soup.get_text()
            revenue_info = self.extract_revenue(card_text)

            if revenue_info:
                revenue_claim, revenue_amount, revenue_period = revenue_info
            else:
                revenue_claim = None
                revenue_amount = None
                revenue_period = None

            # Extract tech stack
            tech_stack = self.extract_tech_stack(card_text)

            # Build metadata
            metadata = OpportunityMetadata(
                title=title,
                description=description,
                source=OpportunitySource.INDIE_HACKERS,
                source_url=href,
                revenue_claim=revenue_claim,
                revenue_amount=revenue_amount,
                revenue_period=revenue_period,
                tech_stack=tech_stack,
                created_at=datetime.now(),
                discovered_at=datetime.now(),
                tags=['indie-hackers', 'interview', 'case-study']
            )

            opportunity = Opportunity(
                id=f"ih_interview_{hash(href)}",
                metadata=metadata
            )

            return opportunity

        except Exception as e:
            logger.error(f"❌ Error parsing interview card: {e}")
            return None

    async def scrape_all(self) -> List[Opportunity]:
        """
        Scrape all Indie Hackers sources

        Returns:
            List of unique, validated Opportunities
        """
        logger.info("\n" + "=" * 70)
        logger.info("💡 INDIE HACKERS SCRAPING (Modern with Crawl4AI)")
        logger.info("=" * 70)

        # Scrape products
        products = await self.scrape_products_page(max_products=30)
        await asyncio.sleep(2)  # Rate limiting

        # Scrape interviews
        interviews = await self.scrape_interviews(max_interviews=20)

        all_opportunities = products + interviews

        # Remove duplicates by URL
        seen_urls = set()
        unique_opportunities = []

        for opp in all_opportunities:
            url = str(opp.metadata.source_url)
            if url not in seen_urls:
                seen_urls.add(url)
                unique_opportunities.append(opp)

        logger.info(f"\n✅ Total Indie Hackers opportunities: {len(unique_opportunities)}")
        logger.info(f"   Products: {len(products)}")
        logger.info(f"   Interviews: {len(interviews)}")
        logger.info(f"   Removed {len(all_opportunities) - len(unique_opportunities)} duplicates")

        return unique_opportunities


async def main():
    """Test the modern Indie Hackers scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    scraper = IndieHackersScraperModern()
    opportunities = await scraper.scrape_all()

    # Print samples
    print("\n" + "=" * 70)
    print("📊 SAMPLE OPPORTUNITIES")
    print("=" * 70)

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp.metadata.title}")
        print(f"   Revenue: {opp.metadata.revenue_claim or 'Not specified'}")
        print(f"   Tech: {', '.join(opp.metadata.tech_stack[:5]) if opp.metadata.tech_stack else 'Not specified'}")
        print(f"   Tags: {', '.join(opp.metadata.tags)}")
        print(f"   URL: {opp.metadata.source_url}")


if __name__ == "__main__":
    asyncio.run(main())
