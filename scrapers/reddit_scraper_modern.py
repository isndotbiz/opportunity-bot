#!/usr/bin/env python3
"""
Modern Reddit scraper with Pydantic validation
Uses PRAW for API access + Crawl4AI for link content extraction
"""

import re
import time
import asyncio
from datetime import datetime
from typing import List, Optional
from praw import Reddit
from praw.models import Submission

from models import (
    Opportunity,
    OpportunityMetadata,
    OpportunitySource,
    ScraperConfig
)
from scrapers.crawl4ai_base import Crawl4AIBase
from scrapers.config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_SUBREDDITS,
    REDDIT_SEARCH_QUERIES,
    MAX_OPPORTUNITIES_PER_SOURCE,
    MIN_REVENUE_MENTION
)

import logging

logger = logging.getLogger(__name__)


class RedditScraperModern(Crawl4AIBase):
    """Modern Reddit scraper with Crawl4AI and Pydantic"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize Reddit scraper"""
        super().__init__(config)

        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            raise ValueError(
                "Reddit API credentials missing!\n"
                "Get them from: https://www.reddit.com/prefs/apps\n"
                "Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables"
            )

        self.reddit = Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            check_for_async=False
        )

        logger.info("✅ Reddit API initialized")

    def is_relevant_post(self, post: Submission) -> bool:
        """Check if post is relevant for business opportunities"""
        text = (post.title + " " + post.selftext).lower()

        # Must mention money or revenue
        money_keywords = ['$', 'revenue', 'mrr', 'arr', 'income', 'earning', 'profit', 'made']
        has_money = any(keyword in text for keyword in money_keywords)

        # Bonus if mentions automation/passive/saas
        automation_keywords = [
            'automat', 'passive', 'saas', 'ai', 'api', 'tool', 'app',
            'side project', 'launched', 'built', 'created'
        ]
        has_automation = any(keyword in text for keyword in automation_keywords)

        # High engagement posts are valuable
        high_engagement = post.score > 50 or post.num_comments > 20

        return has_money and (has_automation or high_engagement)

    def parse_reddit_post(self, post: Submission) -> Optional[Opportunity]:
        """
        Parse Reddit post into Opportunity with Pydantic validation

        Args:
            post: PRAW Submission object

        Returns:
            Validated Opportunity or None if parsing fails
        """
        try:
            text = post.title + " " + post.selftext

            # Extract revenue information
            revenue_info = self.extract_revenue(text)
            if revenue_info:
                revenue_claim, revenue_amount, revenue_period = revenue_info
            else:
                # If mentioned money but no clear claim
                if '$' in text or 'revenue' in text.lower():
                    revenue_claim = "Revenue mentioned (not specified)"
                    revenue_amount = None
                    revenue_period = None
                else:
                    revenue_claim = None
                    revenue_amount = None
                    revenue_period = None

            # Extract tech stack
            tech_stack = self.extract_tech_stack(text)

            # Extract time to build
            time_to_build = self.extract_time_to_build(text)

            # Determine tags
            tags = []
            text_lower = text.lower()
            if 'ai' in text_lower or 'gpt' in text_lower or 'llm' in text_lower:
                tags.append('ai')
            if 'automat' in text_lower:
                tags.append('automation')
            if 'saas' in text_lower:
                tags.append('saas')
            if 'side project' in text_lower or 'side hustle' in text_lower:
                tags.append('side-project')
            if 'passive' in text_lower:
                tags.append('passive-income')

            # Build metadata
            metadata = OpportunityMetadata(
                title=post.title,
                description=post.selftext[:2000] if post.selftext else post.title,
                source=OpportunitySource.REDDIT,
                source_url=f"https://reddit.com{post.permalink}",
                revenue_claim=revenue_claim,
                revenue_amount=revenue_amount,
                revenue_period=revenue_period,
                tech_stack=tech_stack,
                time_to_build=time_to_build,
                score=post.score,
                comments_count=post.num_comments,
                created_at=datetime.fromtimestamp(post.created_utc),
                discovered_at=datetime.now(),
                tags=tags,
                author=post.author.name if post.author else None
            )

            # Create Opportunity
            opportunity = Opportunity(
                id=f"reddit_{post.id}",
                metadata=metadata
            )

            return opportunity

        except Exception as e:
            logger.error(f"❌ Error parsing post {post.id}: {e}")
            return None

    def scrape_subreddit(
        self,
        subreddit_name: str,
        time_filter: str = 'month',
        limit: int = 100
    ) -> List[Opportunity]:
        """
        Scrape a specific subreddit for opportunities

        Args:
            subreddit_name: Name of subreddit (without r/)
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum posts to check per query

        Returns:
            List of validated Opportunities
        """
        logger.info(f"📡 Scraping r/{subreddit_name}...")
        opportunities = []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Search with keywords
            for query in REDDIT_SEARCH_QUERIES:
                try:
                    logger.debug(f"  Searching: '{query}'")

                    for post in subreddit.search(query, time_filter=time_filter, limit=limit):
                        if self.is_relevant_post(post):
                            opportunity = self.parse_reddit_post(post)

                            if opportunity:
                                opportunities.append(opportunity)

                                logger.info(
                                    f"  ✅ Found: {opportunity.metadata.title[:60]}... "
                                    f"(score: {opportunity.metadata.score})"
                                )

                            if len(opportunities) >= MAX_OPPORTUNITIES_PER_SOURCE:
                                logger.info(f"  📊 Reached limit of {MAX_OPPORTUNITIES_PER_SOURCE} opportunities")
                                break

                    time.sleep(1)  # Rate limiting

                    if len(opportunities) >= MAX_OPPORTUNITIES_PER_SOURCE:
                        break

                except Exception as e:
                    logger.error(f"  ⚠️  Search error for '{query}': {e}")
                    continue

            logger.info(f"✅ Found {len(opportunities)} opportunities from r/{subreddit_name}")

        except Exception as e:
            logger.error(f"❌ Error accessing r/{subreddit_name}: {e}")

        return opportunities

    def scrape_all_subreddits(self) -> List[Opportunity]:
        """
        Scrape all configured subreddits

        Returns:
            List of unique, validated Opportunities
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔴 REDDIT SCRAPING (Modern with Pydantic)")
        logger.info("=" * 70)

        all_opportunities = []

        for subreddit_name in REDDIT_SUBREDDITS:
            opportunities = self.scrape_subreddit(subreddit_name, time_filter='month', limit=50)
            all_opportunities.extend(opportunities)
            time.sleep(2)  # Rate limiting between subreddits

        # Remove duplicates by URL
        seen_urls = set()
        unique_opportunities = []

        for opp in all_opportunities:
            url = str(opp.metadata.source_url)
            if url not in seen_urls:
                seen_urls.add(url)
                unique_opportunities.append(opp)

        logger.info(f"\n✅ Total Reddit opportunities: {len(unique_opportunities)}")
        logger.info(f"   Removed {len(all_opportunities) - len(unique_opportunities)} duplicates")

        # Log statistics
        revenue_opps = [o for o in unique_opportunities if o.metadata.revenue_amount]
        logger.info(f"   With revenue data: {len(revenue_opps)}")

        return unique_opportunities

    async def enrich_with_crawl4ai(
        self,
        opportunities: List[Opportunity],
        max_concurrent: int = 3
    ) -> List[Opportunity]:
        """
        Enrich opportunities by crawling linked content with Crawl4AI

        This is useful for posts that link to external sites with more details

        Args:
            opportunities: List of opportunities to enrich
            max_concurrent: Max concurrent crawls

        Returns:
            Enriched opportunities
        """
        if not self._crawl4ai_available:
            logger.warning("⚠️  Crawl4AI not available, skipping enrichment")
            return opportunities

        logger.info(f"\n🌐 Enriching {len(opportunities)} opportunities with Crawl4AI...")

        # Find opportunities with external links in description
        url_pattern = re.compile(r'https?://[^\s]+')
        to_crawl = []

        for opp in opportunities:
            urls = url_pattern.findall(opp.metadata.description)
            # Filter out reddit URLs
            external_urls = [u for u in urls if 'reddit.com' not in u]
            if external_urls:
                to_crawl.append((opp, external_urls[0]))  # Take first external link

        if not to_crawl:
            logger.info("  No external links found to crawl")
            return opportunities

        logger.info(f"  Found {len(to_crawl)} opportunities with external links")

        # Batch crawl external links
        urls_to_crawl = [url for _, url in to_crawl]
        crawl_results = await self.batch_crawl(urls_to_crawl[:max_concurrent])

        # Enrich opportunities with crawled content
        for (opp, url), result in zip(to_crawl, crawl_results):
            if result.success and result.markdown:
                # Extract additional tech stack from crawled content
                additional_tech = self.extract_tech_stack(result.markdown)
                for tech in additional_tech:
                    if tech not in opp.metadata.tech_stack:
                        opp.metadata.tech_stack.append(tech)

                logger.info(f"  ✅ Enriched: {opp.metadata.title[:50]}... with {len(additional_tech)} tech items")

        return opportunities


async def main():
    """Test the modern Reddit scraper"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    scraper = RedditScraperModern()
    opportunities = scraper.scrape_all_subreddits()

    # Optionally enrich with Crawl4AI
    # opportunities = await scraper.enrich_with_crawl4ai(opportunities, max_concurrent=3)

    # Print sample opportunities
    print("\n" + "=" * 70)
    print("📊 SAMPLE OPPORTUNITIES")
    print("=" * 70)

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp.metadata.title}")
        print(f"   Revenue: {opp.metadata.revenue_claim or 'Not specified'}")
        print(f"   Score: {opp.metadata.score}")
        print(f"   Tech: {', '.join(opp.metadata.tech_stack[:5]) if opp.metadata.tech_stack else 'Not specified'}")
        print(f"   Tags: {', '.join(opp.metadata.tags)}")
        print(f"   URL: {opp.metadata.source_url}")

    # Demonstrate Pydantic serialization
    print("\n" + "=" * 70)
    print("📝 PYDANTIC VALIDATION DEMO")
    print("=" * 70)

    if opportunities:
        first_opp = opportunities[0]
        print("\nJSON Export:")
        print(first_opp.model_dump_json(indent=2))

        print("\nRAG Document:")
        print(first_opp.to_document()[:500] + "...")

        print("\nMetadata Dict:")
        print(first_opp.to_metadata_dict())


if __name__ == "__main__":
    asyncio.run(main())
