#!/usr/bin/env python3
"""
Test Modern Setup - Verify installation and configuration
Run this after installing requirements_modern.txt
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required packages are installed"""
    logger.info("Testing imports...")

    tests = {
        "Pydantic": lambda: __import__('pydantic'),
        "ChromaDB": lambda: __import__('chromadb'),
        "PRAW (Reddit)": lambda: __import__('praw'),
        "Requests": lambda: __import__('requests'),
        "BeautifulSoup4": lambda: __import__('bs4'),
        "Asyncio": lambda: __import__('asyncio'),
    }

    # Test Crawl4AI separately (it's optional)
    try:
        import crawl4ai
        tests["Crawl4AI"] = lambda: crawl4ai
        crawl4ai_available = True
    except ImportError:
        logger.warning("⚠️  Crawl4AI not installed (optional)")
        crawl4ai_available = False

    failed = []
    for name, test_fn in tests.items():
        try:
            test_fn()
            logger.info(f"  ✅ {name}")
        except ImportError as e:
            logger.error(f"  ❌ {name}: {e}")
            failed.append(name)

    if failed:
        logger.error(f"\n❌ Missing packages: {', '.join(failed)}")
        logger.info("\nInstall with: pip install -r requirements_modern.txt")
        return False

    logger.info("\n✅ All core imports successful")

    if not crawl4ai_available:
        logger.info("\n💡 To enable Crawl4AI features:")
        logger.info("   pip install 'crawl4ai[all]'")
        logger.info("   playwright install chromium")

    return True


def test_pydantic_models():
    """Test Pydantic models"""
    logger.info("\nTesting Pydantic models...")

    try:
        from models import (
            Opportunity,
            OpportunityMetadata,
            OpportunityAnalysis,
            OpportunitySource,
            TechnicalDifficulty
        )

        # Test creating metadata
        metadata = OpportunityMetadata(
            title="Test Opportunity",
            description="This is a test opportunity for validation",
            source=OpportunitySource.REDDIT,
            source_url="https://reddit.com/r/test/example",
            revenue_claim="$1000/month",
            revenue_amount=1000.0,
            revenue_period="month",
            tech_stack=["Python", "FastAPI"],
            tags=["test", "validation"]
        )

        logger.info("  ✅ OpportunityMetadata created")

        # Test creating analysis
        analysis = OpportunityAnalysis(
            automation_score=85,
            legitimacy_score=80,
            scalability_score=75,
            technical_difficulty=TechnicalDifficulty.MODERATE,
            time_to_market="2-4 weeks",
            initial_investment="$500",
            key_insights=["Test insight 1", "Test insight 2"],
            automation_opportunities=["API integration"],
            risks=["Market competition"]
        )

        logger.info("  ✅ OpportunityAnalysis created")

        # Test creating full opportunity
        opportunity = Opportunity(
            id="test_123",
            metadata=metadata,
            analysis=analysis
        )

        logger.info("  ✅ Opportunity created")

        # Test serialization
        json_str = opportunity.model_dump_json(indent=2)
        logger.info(f"  ✅ JSON serialization ({len(json_str)} bytes)")

        # Test document conversion
        document = opportunity.to_document()
        logger.info(f"  ✅ Document conversion ({len(document)} chars)")

        # Test metadata dict
        meta_dict = opportunity.to_metadata_dict()
        logger.info(f"  ✅ Metadata dict ({len(meta_dict)} fields)")

        logger.info("\n✅ Pydantic models working correctly")
        return True

    except Exception as e:
        logger.error(f"\n❌ Pydantic model error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chromadb():
    """Test ChromaDB connection"""
    logger.info("\nTesting ChromaDB...")

    try:
        import chromadb
        from chromadb.config import Settings

        # Create test client
        test_db = Path(__file__).parent / "data" / "test_chroma"
        test_db.mkdir(parents=True, exist_ok=True)

        client = chromadb.PersistentClient(
            path=str(test_db),
            settings=Settings(anonymized_telemetry=False)
        )

        logger.info("  ✅ ChromaDB client created")

        # Create test collection
        try:
            client.delete_collection("test_collection")
        except:
            pass

        collection = client.create_collection("test_collection")
        logger.info("  ✅ Test collection created")

        # Add test document
        collection.add(
            ids=["test_1"],
            documents=["This is a test document"],
            metadatas=[{"source": "test"}]
        )

        logger.info("  ✅ Document added")

        # Query test
        results = collection.query(
            query_texts=["test"],
            n_results=1
        )

        logger.info(f"  ✅ Query successful ({len(results['documents'][0])} results)")

        # Cleanup
        client.delete_collection("test_collection")
        logger.info("  ✅ Cleanup complete")

        logger.info("\n✅ ChromaDB working correctly")
        return True

    except Exception as e:
        logger.error(f"\n❌ ChromaDB error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    logger.info("\nTesting configuration...")

    try:
        from scrapers.config import (
            REDDIT_CLIENT_ID,
            REDDIT_CLIENT_SECRET,
            REDDIT_USER_AGENT
        )

        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            logger.info("  ✅ Reddit API configured")
        else:
            logger.warning("  ⚠️  Reddit API not configured")
            logger.info("     Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")

        from scrapers.config import GOOGLE_API_KEY, GOOGLE_CSE_ID

        if GOOGLE_API_KEY and GOOGLE_CSE_ID:
            logger.info("  ✅ Google API configured")
        else:
            logger.info("  ℹ️  Google API not configured (optional)")

        logger.info("\n✅ Configuration loaded")
        return True

    except Exception as e:
        logger.error(f"\n❌ Configuration error: {e}")
        return False


def test_crawl4ai():
    """Test Crawl4AI (if available)"""
    logger.info("\nTesting Crawl4AI...")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
        logger.info("  ✅ Crawl4AI imported")

        # Test browser config
        browser_config = BrowserConfig(
            headless=True,
            user_agent="Test/1.0",
            viewport_width=1920,
            viewport_height=1080
        )
        logger.info("  ✅ BrowserConfig created")

        # Test crawler config
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            page_timeout=30000,
            wait_until="networkidle"
        )
        logger.info("  ✅ CrawlerRunConfig created")

        logger.info("\n✅ Crawl4AI available and configured")
        logger.info("   Note: Actual browser test requires 'playwright install chromium'")
        return True

    except ImportError:
        logger.warning("\n⚠️  Crawl4AI not installed")
        logger.info("\nTo install Crawl4AI:")
        logger.info("  pip install 'crawl4ai[all]'")
        logger.info("  playwright install chromium")
        return None  # None = optional feature not available

    except Exception as e:
        logger.error(f"\n❌ Crawl4AI error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("MODERN OPPORTUNITY BOT - SETUP TEST")
    logger.info("=" * 70)

    results = {
        "Imports": test_imports(),
        "Pydantic Models": test_pydantic_models(),
        "ChromaDB": test_chromadb(),
        "Configuration": test_config(),
        "Crawl4AI": test_crawl4ai()
    }

    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    for name, result in results.items():
        if result is True:
            logger.info(f"✅ {name}: PASS")
        elif result is False:
            logger.error(f"❌ {name}: FAIL")
        elif result is None:
            logger.info(f"⚠️  {name}: OPTIONAL (not installed)")

    failed = [name for name, result in results.items() if result is False]

    if failed:
        logger.error(f"\n❌ {len(failed)} test(s) failed: {', '.join(failed)}")
        logger.info("\nPlease install missing dependencies:")
        logger.info("  pip install -r requirements_modern.txt")
        return False
    else:
        logger.info("\n✅ All required tests passed!")

        optional_missing = [name for name, result in results.items() if result is None]
        if optional_missing:
            logger.info(f"\nOptional features not installed: {', '.join(optional_missing)}")
            logger.info("For full functionality:")
            logger.info("  pip install 'crawl4ai[all]'")
            logger.info("  playwright install chromium")

        logger.info("\n🚀 Ready to run:")
        logger.info("  python modern_opportunity_pipeline.py")

        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
