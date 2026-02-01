#!/usr/bin/env python3
"""
Base Crawl4AI scraper with modern features
- JavaScript rendering
- Smart anti-bot handling
- Concurrent crawling
- Retry logic with exponential backoff
"""

import asyncio
import logging
import time
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

from models import CrawlResult, ScraperConfig

logger = logging.getLogger(__name__)


class Crawl4AIBase:
    """Base class for Crawl4AI-powered scrapers"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize Crawl4AI scraper"""
        self.config = config or ScraperConfig()
        self._crawl4ai_available = False
        self._init_crawl4ai()

    def _init_crawl4ai(self):
        """Initialize Crawl4AI library"""
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

            self.AsyncWebCrawler = AsyncWebCrawler
            self.BrowserConfig = BrowserConfig
            self.CrawlerRunConfig = CrawlerRunConfig
            self.CacheMode = CacheMode
            self._crawl4ai_available = True

            logger.info("✅ Crawl4AI initialized successfully")
        except ImportError as e:
            logger.warning(f"⚠️  Crawl4AI not available: {e}")
            logger.warning("Install with: pip install 'crawl4ai[all]'")
            self._crawl4ai_available = False

    def _get_browser_config(self) -> Any:
        """Get browser configuration"""
        if not self._crawl4ai_available:
            raise RuntimeError("Crawl4AI is not available")

        return self.BrowserConfig(
            headless=self.config.headless,
            user_agent=self.config.user_agent,
            viewport_width=1920,
            viewport_height=1080,
            extra_args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

    def _get_crawler_config(self, session_id: Optional[str] = None) -> Any:
        """Get crawler run configuration"""
        if not self._crawl4ai_available:
            raise RuntimeError("Crawl4AI is not available")

        config_dict = {
            "cache_mode": self.CacheMode.BYPASS,
            "page_timeout": self.config.timeout * 1000,  # Convert to ms
            "wait_until": self.config.wait_for,
            "mean_delay": (self.config.min_delay + self.config.max_delay) / 2,
            "max_range": self.config.max_delay - self.config.min_delay,
        }

        if session_id:
            config_dict["session_id"] = session_id

        return self.CrawlerRunConfig(**config_dict)

    async def crawl_url(
        self,
        url: str,
        extract_links: bool = True,
        extract_metadata: bool = True
    ) -> CrawlResult:
        """
        Crawl a single URL with Crawl4AI

        Args:
            url: URL to crawl
            extract_links: Whether to extract links
            extract_metadata: Whether to extract metadata

        Returns:
            CrawlResult with crawled data
        """
        if not self._crawl4ai_available:
            return CrawlResult(
                url=url,
                success=False,
                error="Crawl4AI is not available. Install with: pip install 'crawl4ai[all]'"
            )

        start_time = time.time()

        try:
            browser_config = self._get_browser_config()
            crawler_config = self._get_crawler_config()

            async with self.AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"🌐 Crawling: {url}")

                result = await crawler.arun(url=url, config=crawler_config)

                if not result.success:
                    raise Exception(result.error_message or "Crawl failed")

                # Get markdown content
                markdown = result.markdown_v2.raw_markdown if hasattr(result, 'markdown_v2') else result.markdown

                # Extract title
                title = result.metadata.get('title', '') if hasattr(result, 'metadata') else ''

                # Extract links if requested
                links = []
                if extract_links and hasattr(result, 'links'):
                    links = [link.get('href', '') for link in result.links if link.get('href')]

                # Extract images
                images = []
                if hasattr(result, 'media') and result.media:
                    images = [img.get('src', '') for img in result.media.get('images', [])]

                crawl_time_ms = int((time.time() - start_time) * 1000)

                logger.info(f"✅ Crawled successfully: {url} ({crawl_time_ms}ms)")

                return CrawlResult(
                    url=url,
                    success=True,
                    title=title,
                    markdown=markdown,
                    html=result.html if hasattr(result, 'html') else None,
                    status_code=getattr(result, 'status_code', 200),
                    links=links,
                    images=images,
                    crawl_time_ms=crawl_time_ms,
                    timestamp=datetime.now()
                )

        except Exception as e:
            crawl_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Crawl failed for {url}: {e}")

            return CrawlResult(
                url=url,
                success=False,
                error=str(e),
                crawl_time_ms=crawl_time_ms,
                timestamp=datetime.now()
            )

    async def batch_crawl(
        self,
        urls: List[str],
        extract_links: bool = True
    ) -> List[CrawlResult]:
        """
        Crawl multiple URLs concurrently using Crawl4AI's efficient multi-URL crawling

        Args:
            urls: List of URLs to crawl
            extract_links: Whether to extract links

        Returns:
            List of CrawlResults
        """
        if not self._crawl4ai_available:
            return [
                CrawlResult(
                    url=url,
                    success=False,
                    error="Crawl4AI is not available"
                )
                for url in urls
            ]

        logger.info(f"🚀 Starting batch crawl of {len(urls)} URLs (max_concurrent={self.config.max_concurrent})")

        try:
            browser_config = self._get_browser_config()
            crawler_config = self._get_crawler_config()

            async with self.AsyncWebCrawler(config=browser_config) as crawler:
                # Use Crawl4AI's native multi-URL crawling
                start_time = time.time()
                crawl_results = await crawler.acrawl_many(
                    urls=urls,
                    config=crawler_config,
                    max_concurrent=self.config.max_concurrent
                )

                total_time = time.time() - start_time

                # Process results
                results = []
                for i, (url, result) in enumerate(zip(urls, crawl_results), 1):
                    try:
                        if result.success:
                            # Get markdown content
                            markdown = result.markdown_v2.raw_markdown if hasattr(result, 'markdown_v2') else result.markdown

                            # Extract title
                            title = result.metadata.get('title', '') if hasattr(result, 'metadata') else ''

                            # Extract links
                            links = []
                            if extract_links and hasattr(result, 'links'):
                                links = [link.get('href', '') for link in result.links if link.get('href')]

                            logger.info(f"[{i}/{len(urls)}] ✅ {url}")

                            results.append(CrawlResult(
                                url=url,
                                success=True,
                                title=title,
                                markdown=markdown,
                                html=result.html if hasattr(result, 'html') else None,
                                status_code=getattr(result, 'status_code', 200),
                                links=links,
                                timestamp=datetime.now()
                            ))
                        else:
                            logger.error(f"[{i}/{len(urls)}] ❌ {url}: {result.error_message}")
                            results.append(CrawlResult(
                                url=url,
                                success=False,
                                error=result.error_message,
                                timestamp=datetime.now()
                            ))
                    except Exception as e:
                        logger.error(f"[{i}/{len(urls)}] ❌ Error processing {url}: {e}")
                        results.append(CrawlResult(
                            url=url,
                            success=False,
                            error=str(e),
                            timestamp=datetime.now()
                        ))

                successful = len([r for r in results if r.success])
                logger.info(
                    f"✅ Batch crawl complete: {successful}/{len(urls)} successful in {total_time:.2f}s "
                    f"({len(urls)/total_time:.2f} URLs/sec)"
                )

                return results

        except Exception as e:
            logger.error(f"❌ Batch crawl failed: {e}")
            return [
                CrawlResult(
                    url=url,
                    success=False,
                    error=f"Batch crawl error: {str(e)}",
                    timestamp=datetime.now()
                )
                for url in urls
            ]

    def extract_revenue(self, text: str) -> Optional[tuple]:
        """
        Extract revenue mentions from text

        Returns:
            Tuple of (revenue_claim, revenue_amount, revenue_period) or None
        """
        # Patterns for revenue mentions
        patterns = [
            (r'\$\s*(\d+[,\d]*)\s*/?(?:per\s+)?(mo|month|mrr|monthly)', 'month'),
            (r'\$\s*(\d+[,\d]*)\s*/?k\s*/?(?:per\s+)?(mo|month|mrr|monthly)', 'month', 1000),
            (r'(\d+[,\d]*)\s*\$\s*/?(?:per\s+)?(mo|month|mrr|monthly)', 'month'),
            (r'revenue.*?\$\s*(\d+[,\d]*)', 'unknown'),
            (r'making.*?\$\s*(\d+[,\d]*)', 'unknown'),
            (r'earning.*?\$\s*(\d+[,\d]*)', 'unknown'),
            (r'(\d+[,\d]*)\s*\$\s*/?(?:per\s+)?(yr|year|arr|annual)', 'year'),
            (r'\$\s*(\d+[,\d]*)\s*/?(?:per\s+)?(yr|year|arr|annual)', 'year'),
        ]

        for pattern_info in patterns:
            pattern = pattern_info[0]
            period = pattern_info[1]
            multiplier = pattern_info[2] if len(pattern_info) > 2 else 1

            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str) * multiplier
                    revenue_claim = f"${amount:,.0f}/{period}" if period != 'unknown' else f"${amount:,.0f}"
                    return (revenue_claim, amount, period)
                except ValueError:
                    continue

        return None

    def extract_tech_stack(self, text: str) -> List[str]:
        """Extract technology mentions from text"""
        tech_keywords = {
            'Python', 'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js',
            'FastAPI', 'Django', 'Flask', 'Vue', 'Svelte', 'Tailwind',
            'PostgreSQL', 'MongoDB', 'Redis', 'Stripe', 'GPT-4', 'OpenAI',
            'Claude', 'AWS', 'Vercel', 'Supabase', 'Firebase', 'Docker',
            'Kubernetes', 'GraphQL', 'REST', 'API', 'Llama', 'Anthropic',
            'LangChain', 'Pinecone', 'Weaviate', 'ChromaDB', 'Hugging Face'
        }

        found_tech = []
        text_upper = text.upper()

        for tech in tech_keywords:
            if tech.upper() in text_upper:
                found_tech.append(tech)

        return found_tech

    def extract_time_to_build(self, text: str) -> Optional[str]:
        """Extract time-to-build mentions from text"""
        patterns = [
            r'built\s+in\s+(\d+\s+(?:day|week|month)s?)',
            r'took\s+(\d+\s+(?:day|week|month)s?)',
            r'(\d+\s+(?:day|week|month)s?)\s+to\s+build',
            r'(\d+\s+(?:day|week|month)s?)\s+to\s+launch',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def sanitize_filename(self, url: str) -> str:
        """Create safe filename from URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        domain = re.sub(r'https?://(www\.)?', '', url)
        domain = re.sub(r'[^\w\-]', '_', domain.split('/')[0])
        return f"{domain}_{url_hash}"
