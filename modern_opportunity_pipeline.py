#!/usr/bin/env python3
"""
Modern Opportunity Research Bot - Production Pipeline
Uses Crawl4AI + Pydantic + ChromaDB for production-ready scraping
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from models import Opportunity, OpportunityAnalysis, TechnicalDifficulty
from scrapers.reddit_scraper_modern import RedditScraperModern
from scrapers.indiehackers_scraper_modern import IndieHackersScraperModern
from scrapers.google_dorking_modern import GoogleDorkingScraperModern
from scrapers.config import ScraperConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE = Path(__file__).parent.absolute()
RAG_BUSINESS_DB = WORKSPACE / "data" / "chroma_db"
LLAMA_SERVER = "http://localhost:8080"


class ModernOpportunityPipeline:
    """Production-ready opportunity research pipeline"""

    def __init__(
        self,
        chroma_path: Optional[Path] = None,
        llama_server: Optional[str] = None
    ):
        """
        Initialize modern pipeline

        Args:
            chroma_path: Path to ChromaDB database
            llama_server: URL of local Llama server for analysis
        """
        self.chroma_path = chroma_path or RAG_BUSINESS_DB
        self.llama_server = llama_server or LLAMA_SERVER

        # Ensure database directory exists
        self.chroma_path.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection("business_opportunities")
            logger.info(f"✅ Loaded existing collection with {self.collection.count()} opportunities")
        except:
            self.collection = self.chroma_client.create_collection(
                name="business_opportunities",
                metadata={
                    "description": "Curated business opportunities with AI automation potential",
                    "created_at": datetime.now().isoformat()
                }
            )
            logger.info("✅ Created new collection: business_opportunities")

    async def scrape_all_sources(self) -> List[Opportunity]:
        """
        Scrape all sources concurrently

        Returns:
            Combined list of validated opportunities
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 MODERN OPPORTUNITY SCRAPING PIPELINE")
        logger.info("=" * 80)

        # Initialize scrapers with modern config
        config = ScraperConfig(
            headless=True,
            timeout=30,
            max_concurrent=5,
            render_js=True
        )

        reddit_scraper = RedditScraperModern(config)
        indie_scraper = IndieHackersScraperModern(config)
        google_scraper = GoogleDorkingScraperModern(config)

        # Run scrapers concurrently
        logger.info("\n📡 Starting concurrent scraping...")

        results = await asyncio.gather(
            # Reddit scraping (sync wrapped in async)
            asyncio.to_thread(reddit_scraper.scrape_all_subreddits),
            # Indie Hackers scraping (async)
            indie_scraper.scrape_all(),
            # Google dorking (async)
            google_scraper.scrape_all(enrich_content=False),
            return_exceptions=True
        )

        # Combine results
        all_opportunities = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Scraper {i} failed: {result}")
            else:
                all_opportunities.extend(result)
                logger.info(f"  ✅ Scraper {i}: {len(result)} opportunities")

        # Remove duplicates by URL
        seen_urls = set()
        unique_opportunities = []

        for opp in all_opportunities:
            url = str(opp.metadata.source_url)
            if url not in seen_urls:
                seen_urls.add(url)
                unique_opportunities.append(opp)

        logger.info(f"\n✅ Total opportunities: {len(unique_opportunities)}")
        logger.info(f"   Removed {len(all_opportunities) - len(unique_opportunities)} duplicates")

        return unique_opportunities

    async def analyze_opportunity(self, opportunity: Opportunity) -> OpportunityAnalysis:
        """
        Analyze opportunity with local LLM

        Args:
            opportunity: Opportunity to analyze

        Returns:
            OpportunityAnalysis with scores and insights
        """
        logger.info(f"🤖 Analyzing: {opportunity.metadata.title[:60]}...")

        # Build analysis prompt
        prompt = f"""You are an expert business analyst specializing in AI automation opportunities.

Analyze this business opportunity and provide structured scores:

OPPORTUNITY:
Title: {opportunity.metadata.title}
Description: {opportunity.metadata.description[:1000]}
Revenue Claim: {opportunity.metadata.revenue_claim or 'Not specified'}
Tech Stack: {', '.join(opportunity.metadata.tech_stack) if opportunity.metadata.tech_stack else 'Not specified'}
Source: {opportunity.metadata.source}
Score/Engagement: {opportunity.metadata.score or 'N/A'}

Provide analysis in JSON format:
{{
    "automation_score": <0-100>,
    "legitimacy_score": <0-100>,
    "scalability_score": <0-100>,
    "technical_difficulty": <1-5>,
    "time_to_market": "<estimate>",
    "initial_investment": "$<amount>",
    "key_insights": ["insight1", "insight2", "insight3"],
    "automation_opportunities": ["opp1", "opp2"],
    "risks": ["risk1", "risk2"],
    "competitive_advantages": ["adv1", "adv2"],
    "target_market": "<description>",
    "market_size_estimate": "<estimate>"
}}

Respond ONLY with valid JSON."""

        try:
            import requests

            # Call local LLM
            response = requests.post(
                f"{self.llama_server}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a business analysis expert. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                # Parse JSON from response
                if "```json" in analysis_text:
                    analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis_text:
                    analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

                analysis_dict = json.loads(analysis_text)

                # Validate with Pydantic
                analysis = OpportunityAnalysis(
                    automation_score=analysis_dict['automation_score'],
                    legitimacy_score=analysis_dict['legitimacy_score'],
                    scalability_score=analysis_dict['scalability_score'],
                    technical_difficulty=TechnicalDifficulty(analysis_dict['technical_difficulty']),
                    time_to_market=analysis_dict['time_to_market'],
                    initial_investment=analysis_dict['initial_investment'],
                    key_insights=analysis_dict['key_insights'],
                    automation_opportunities=analysis_dict.get('automation_opportunities', []),
                    risks=analysis_dict.get('risks', []),
                    competitive_advantages=analysis_dict.get('competitive_advantages', []),
                    target_market=analysis_dict.get('target_market'),
                    market_size_estimate=analysis_dict.get('market_size_estimate')
                )

                logger.info(
                    f"  ✅ Automation: {analysis.automation_score}/100, "
                    f"Legitimacy: {analysis.legitimacy_score}/100"
                )

                return analysis

        except Exception as e:
            logger.warning(f"  ⚠️  LLM analysis failed: {e}")
            logger.info("  ℹ️  Using fallback analysis")

        # Fallback analysis
        return self._fallback_analysis(opportunity)

    def _fallback_analysis(self, opportunity: Opportunity) -> OpportunityAnalysis:
        """Generate fallback analysis when LLM is unavailable"""
        # Calculate basic scores from metadata
        automation_score = 70

        if opportunity.metadata.revenue_amount:
            automation_score += 10

        if any(tech in opportunity.metadata.tech_stack for tech in ['API', 'GPT-4', 'AI']):
            automation_score += 10

        legitimacy_score = 60
        if opportunity.metadata.score and opportunity.metadata.score > 100:
            legitimacy_score += 20
        if opportunity.metadata.revenue_amount and opportunity.metadata.revenue_amount >= 1000:
            legitimacy_score += 10

        return OpportunityAnalysis(
            automation_score=min(automation_score, 100),
            legitimacy_score=min(legitimacy_score, 100),
            scalability_score=75,
            technical_difficulty=TechnicalDifficulty.MODERATE,
            time_to_market="2-4 weeks",
            initial_investment="$500-1000",
            key_insights=[
                "High automation potential based on tech stack",
                "Proven revenue model from source",
                "Moderate technical complexity"
            ],
            automation_opportunities=[
                "API integration",
                "Automated marketing",
                "Payment processing"
            ],
            risks=[
                "Market competition",
                "Technology dependencies"
            ],
            competitive_advantages=[
                "AI-powered features",
                "Automated workflows"
            ]
        )

    async def store_in_chromadb(self, opportunity: Opportunity):
        """
        Store opportunity in ChromaDB using Pydantic models

        Args:
            opportunity: Validated opportunity to store
        """
        logger.info(f"💾 Storing: {opportunity.metadata.title[:60]}...")

        try:
            # Convert to document and metadata using Pydantic methods
            document = opportunity.to_document()
            metadata = opportunity.to_metadata_dict()

            # Add to collection
            self.collection.add(
                ids=[opportunity.id or f"opp_{datetime.now().timestamp()}"],
                documents=[document],
                metadatas=[metadata]
            )

            logger.info(f"  ✅ Stored (total: {self.collection.count()})")

        except Exception as e:
            logger.error(f"  ❌ Error storing: {e}")

    def query_opportunities(
        self,
        query: str,
        n_results: int = 5,
        filter_criteria: Optional[dict] = None
    ) -> List[dict]:
        """
        Query stored opportunities

        Args:
            query: Search query
            n_results: Number of results to return
            filter_criteria: Optional metadata filters

        Returns:
            List of matching opportunities
        """
        logger.info(f"\n🔎 Querying: '{query}'")

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_criteria
            )

            logger.info(f"\n📊 Top {len(results['documents'][0])} Results:")

            matches = []
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                print(f"\n{i}. {metadata['title']}")
                print(f"   Source: {metadata['source']}")
                print(f"   Revenue: {metadata.get('revenue_claim', 'Not specified')}")

                if 'automation_score' in metadata:
                    print(f"   Automation: {metadata['automation_score']}/100")
                    print(f"   Legitimacy: {metadata['legitimacy_score']}/100")
                    print(f"   Time to Market: {metadata.get('time_to_market', 'Not specified')}")

                print(f"   URL: {metadata['url']}")

                matches.append(metadata)

            return matches

        except Exception as e:
            logger.error(f"❌ Query error: {e}")
            return []

    async def run_full_pipeline(
        self,
        analyze_with_llm: bool = True,
        max_opportunities: Optional[int] = None
    ):
        """
        Run complete pipeline: Scrape -> Analyze -> Store

        Args:
            analyze_with_llm: Whether to analyze with local LLM
            max_opportunities: Max opportunities to process (None = all)
        """
        logger.info("\n" + "=" * 80)
        logger.info("🚀 FULL PIPELINE EXECUTION")
        logger.info("=" * 80)

        # Step 1: Scrape
        opportunities = await self.scrape_all_sources()

        if max_opportunities:
            opportunities = opportunities[:max_opportunities]

        # Step 2: Analyze and Store
        logger.info(f"\n🤖 Analyzing and storing {len(opportunities)} opportunities...")

        for i, opp in enumerate(opportunities, 1):
            logger.info(f"\n[{i}/{len(opportunities)}] Processing: {opp.metadata.title[:60]}...")

            # Analyze
            if analyze_with_llm:
                analysis = await self.analyze_opportunity(opp)
                opp.analysis = analysis

            # Store
            await self.store_in_chromadb(opp)

        # Step 3: Demo query
        logger.info("\n" + "=" * 80)
        logger.info("🎯 DEMO QUERY")
        logger.info("=" * 80)

        self.query_opportunities(
            "high automation passive income AI opportunities under $1000 investment",
            n_results=5
        )

        logger.info("\n" + "=" * 80)
        logger.info("✅ PIPELINE COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"\n💡 Database location: {self.chroma_path}")
        logger.info(f"   Total opportunities: {self.collection.count()}")


async def main():
    """Run the modern pipeline"""
    pipeline = ModernOpportunityPipeline()

    # Run full pipeline
    await pipeline.run_full_pipeline(
        analyze_with_llm=True,  # Set to False to skip LLM analysis
        max_opportunities=10  # Limit for testing, set to None for all
    )


if __name__ == "__main__":
    asyncio.run(main())
