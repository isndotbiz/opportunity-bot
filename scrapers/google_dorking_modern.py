#!/usr/bin/env python3
"""
Modern Google dorking scraper with Crawl4AI
Uses Google Custom Search API + Crawl4AI for content extraction
"""

import asyncio
import requests
from datetime import datetime
from typing import List, Optional

from models import (
    Opportunity,
    OpportunityMetadata,
    OpportunitySource,
    ScraperConfig
)
from scrapers.crawl4ai_base import Crawl4AIBase
from scrapers.config import (
    GOOGLE_API_KEY,
    GOOGLE_CSE_ID,
    GOOGLE_DORK_QUERIES,
    MAX_OPPORTUNITIES_PER_SOURCE
)

import logging

logger = logging.getLogger(__name__)


class GoogleDorkingScraperModern(Crawl4AIBase):
    """Modern Google dorking scraper with API and Crawl4AI"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize Google dorking scraper"""
        super().__init__(config)

        self.api_key = GOOGLE_API_KEY
        self.cse_id = GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        if not self.api_key or not self.cse_id:
            logger.warning("⚠️  Google Custom Search API credentials missing!")
            logger.warning("   Get API key: https://developers.google.com/custom-search/v1/overview")
            logger.warning("   Get CSE ID: https://cse.google.com/cse/all")
            logger.warning("   Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables")
            self.use_api = False
        else:
            self.use_api = True
            logger.info("✅ Google Custom Search API initialized")

    async def search_with_api(self, query: str, num_results: int = 10) -> List[Opportunity]:
        """
        Search using Google Custom Search API

        Args:
            query: Search query
            num_results: Number of results to fetch

        Returns:
            List of Opportunities from search results
        """
        if not self.use_api:
            return []

        opportunities = []

        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': min(num_results, 10)  # API limit per request
            }

            logger.info(f"  🔎 Searching: {query[:60]}...")

            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                for item in data.get('items', []):
                    title = item.get('title', '')
                    description = item.get('snippet', '')
                    url = item.get('link', '')

                    if not url or not title:
                        continue

                    # Extract revenue from title and description
                    text = title + " " + description
                    revenue_info = self.extract_revenue(text)

                    if revenue_info:
                        revenue_claim, revenue_amount, revenue_period = revenue_info
                    else:
                        revenue_claim = None
                        revenue_amount = None
                        revenue_period = None

                    # Extract tech stack
                    tech_stack = self.extract_tech_stack(text)

                    # Determine source from URL
                    if 'reddit.com' in url:
                        source = OpportunitySource.REDDIT
                    elif 'indiehackers.com' in url:
                        source = OpportunitySource.INDIE_HACKERS
                    elif 'twitter.com' in url or 'x.com' in url:
                        source = OpportunitySource.TWITTER
                    elif 'news.ycombinator.com' in url:
                        source = OpportunitySource.HACKER_NEWS
                    else:
                        source = OpportunitySource.GOOGLE_DORK

                    # Determine tags
                    tags = ['google-dork']
                    if revenue_amount:
                        tags.append('revenue-mentioned')

                    # Build metadata
                    metadata = OpportunityMetadata(
                        title=title,
                        description=description,
                        source=source,
                        source_url=url,
                        revenue_claim=revenue_claim,
                        revenue_amount=revenue_amount,
                        revenue_period=revenue_period,
                        tech_stack=tech_stack,
                        created_at=datetime.now(),
                        discovered_at=datetime.now(),
                        tags=tags
                    )

                    opportunity = Opportunity(
                        id=f"google_{hash(url)}",
                        metadata=metadata
                    )

                    opportunities.append(opportunity)

                logger.info(f"  ✅ Found {len(opportunities)} results")

            elif response.status_code == 429:
                logger.warning("  ⚠️  Rate limit exceeded, waiting...")
                await asyncio.sleep(60)
            else:
                logger.error(f"  ❌ API error: {response.status_code}")

        except Exception as e:
            logger.error(f"  ❌ Search error: {e}")

        return opportunities

    async def enrich_with_content(
        self,
        opportunities: List[Opportunity],
        max_concurrent: int = 3
    ) -> List[Opportunity]:
        """
        Enrich opportunities by crawling full content with Crawl4AI

        Args:
            opportunities: Opportunities to enrich
            max_concurrent: Max concurrent crawls

        Returns:
            Enriched opportunities
        """
        if not self._crawl4ai_available:
            logger.warning("⚠️  Crawl4AI not available, skipping enrichment")
            return opportunities

        logger.info(f"\n🌐 Enriching {len(opportunities)} opportunities with full content...")

        # Select opportunities to enrich (prioritize those without tech stack)
        to_enrich = [
            opp for opp in opportunities[:max_concurrent]
            if not opp.metadata.tech_stack or not opp.metadata.revenue_claim
        ]

        if not to_enrich:
            to_enrich = opportunities[:max_concurrent]

        # Batch crawl
        urls = [str(opp.metadata.source_url) for opp in to_enrich]
        crawl_results = await self.batch_crawl(urls)

        # Enrich with crawled content
        for opp, result in zip(to_enrich, crawl_results):
            if result.success and result.markdown:
                # Update description with more complete content
                if len(result.markdown) > len(opp.metadata.description):
                    opp.metadata.description = result.markdown[:2000]

                # Extract additional tech stack
                additional_tech = self.extract_tech_stack(result.markdown)
                for tech in additional_tech:
                    if tech not in opp.metadata.tech_stack:
                        opp.metadata.tech_stack.append(tech)

                # Try to extract revenue if not found
                if not opp.metadata.revenue_claim:
                    revenue_info = self.extract_revenue(result.markdown)
                    if revenue_info:
                        revenue_claim, revenue_amount, revenue_period = revenue_info
                        opp.metadata.revenue_claim = revenue_claim
                        opp.metadata.revenue_amount = revenue_amount
                        opp.metadata.revenue_period = revenue_period

                logger.info(f"  ✅ Enriched: {opp.metadata.title[:50]}...")

        return opportunities

    async def scrape_all(self, enrich_content: bool = False) -> List[Opportunity]:
        """
        Execute all Google dork queries

        Args:
            enrich_content: Whether to enrich with full page content

        Returns:
            List of unique, validated Opportunities
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔍 GOOGLE DORKING (Modern with API + Crawl4AI)")
        logger.info("=" * 70)

        if not self.use_api:
            logger.error("❌ Google Custom Search API not configured, skipping")
            return []

        all_opportunities = []

        for query in GOOGLE_DORK_QUERIES:
            results = await self.search_with_api(query, num_results=10)
            all_opportunities.extend(results)

            await asyncio.sleep(1)  # Rate limiting

            if len(all_opportunities) >= MAX_OPPORTUNITIES_PER_SOURCE:
                logger.info(f"📊 Reached limit of {MAX_OPPORTUNITIES_PER_SOURCE} opportunities")
                break

        # Remove duplicates by URL
        seen_urls = set()
        unique_opportunities = []

        for opp in all_opportunities:
            url = str(opp.metadata.source_url)
            if url not in seen_urls:
                seen_urls.add(url)
                unique_opportunities.append(opp)

        logger.info(f"\n✅ Total Google dork opportunities: {len(unique_opportunities)}")
        logger.info(f"   Removed {len(all_opportunities) - len(unique_opportunities)} duplicates")

        # Optionally enrich with full content
        if enrich_content:
            unique_opportunities = await self.enrich_with_content(unique_opportunities, max_concurrent=5)

        return unique_opportunities


async def main():
    """Test the modern Google dorking scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    scraper = GoogleDorkingScraperModern()
    opportunities = await scraper.scrape_all(enrich_content=True)

    # Print samples
    print("\n" + "=" * 70)
    print("📊 SAMPLE OPPORTUNITIES")
    print("=" * 70)

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp.metadata.title}")
        print(f"   Source: {opp.metadata.source}")
        print(f"   Revenue: {opp.metadata.revenue_claim or 'Not specified'}")
        print(f"   Tech: {', '.join(opp.metadata.tech_stack[:5]) if opp.metadata.tech_stack else 'Not specified'}")
        print(f"   URL: {opp.metadata.source_url}")


if __name__ == "__main__":
    asyncio.run(main())
