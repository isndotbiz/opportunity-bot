#!/usr/bin/env python3
"""
PRODUCTION Opportunity Research Bot
Scrapes real opportunities → Analyzes with Qwen → Stores in business RAG
"""

import os
import json
import sys
import requests
import chromadb
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add scrapers to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scrapers.reddit_scraper import RedditScraper
    from scrapers.indiehackers_scraper import IndieHackersScraper
    from scrapers.google_dorking import GoogleDorkingScraper
    from scrapers.producthunt_scraper import ProductHuntScraper
    from scrapers.hackernews_scraper import HackerNewsScraper
    from config_chromadb import get_chroma_client, get_chroma_settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure scrapers/ directory exists with all modules")
    sys.exit(1)

# Configuration
WORKSPACE = Path(__file__).parent.absolute()  # opportunity-research-bot directory
LLAMA_SERVER = "http://localhost:8080"
RAG_BUSINESS_DB = WORKSPACE / "data" / "chroma_db"  # Kept for backward compatibility


class ProductionOpportunityPipeline:
    def __init__(self, use_demo_mode: bool = False):
        """
        Initialize pipeline

        Args:
            use_demo_mode: If True, uses demo data instead of real scraping
        """
        self.use_demo_mode = use_demo_mode
        self.opportunities = []
        self.stats = {
            'scraped': 0,
            'analyzed': 0,
            'stored': 0,
            'failed': 0
        }

    def scrape_opportunities(self) -> List[Dict]:
        """Step 1: Scrape opportunities from all sources"""
        print("\n" + "=" * 70)
        print("🔍 STEP 1: SCRAPING OPPORTUNITIES FROM MULTIPLE SOURCES")
        print("=" * 70)

        if self.use_demo_mode:
            print("\n⚠️  DEMO MODE: Using sample data")
            return self._get_demo_opportunities()

        all_opportunities = []

        # Product Hunt scraping
        try:
            ph_scraper = ProductHuntScraper()
            ph_opps = ph_scraper.scrape_all()
            all_opportunities.extend(ph_opps)
            print(f"✅ Product Hunt: {len(ph_opps)} opportunities")
        except Exception as e:
            print(f"❌ Product Hunt scraping failed: {e}")

        # Hacker News scraping
        try:
            hn_scraper = HackerNewsScraper()
            hn_opps = hn_scraper.scrape_all()
            all_opportunities.extend(hn_opps)
            print(f"✅ Hacker News: {len(hn_opps)} opportunities")
        except Exception as e:
            print(f"❌ Hacker News scraping failed: {e}")

        # Indie Hackers scraping (keep as backup)
        try:
            ih_scraper = IndieHackersScraper()
            ih_opps = ih_scraper.scrape_all()
            all_opportunities.extend(ih_opps)
            print(f"✅ Indie Hackers: {len(ih_opps)} opportunities")
        except Exception as e:
            print(f"❌ Indie Hackers scraping failed: {e}")

        self.stats['scraped'] = len(all_opportunities)

        print("\n" + "=" * 70)
        print(f"📊 TOTAL OPPORTUNITIES SCRAPED: {len(all_opportunities)}")
        print("=" * 70)

        return all_opportunities

    def _get_demo_opportunities(self) -> List[Dict]:
        """Demo opportunities for testing without API keys"""
        return [
            {
                "title": "AI Email Newsletter Curator - $4K/mo in 3 months",
                "source": "Reddit r/SideProject",
                "url": "https://reddit.com/r/SideProject/demo1",
                "description": "Built an AI tool that curates personalized email newsletters. Uses GPT-4 to analyze user interests and web scraping to find relevant content. Fully automated. Revenue: $4K/month after 3 months.",
                "revenue_claim": "$4000/month",
                "tech_stack": "Python, GPT-4 API, SendGrid, Stripe",
                "time_mentioned": "3 months to $4K MRR"
            },
            {
                "title": "Twitter Thread Scheduler SaaS - $6K MRR",
                "source": "Indie Hackers",
                "url": "https://indiehackers.com/demo2",
                "description": "Chrome extension + web app for scheduling Twitter threads with AI optimization. Analyzes best posting times, suggests improvements. 200 paying users at $30/mo.",
                "revenue_claim": "$6000/month",
                "tech_stack": "Next.js, TypeScript, Supabase, OpenAI",
                "time_mentioned": "4 months to first $1K"
            }
        ]

    def analyze_with_qwen(self, opportunity: Dict) -> Dict:
        """Step 2: Analyze opportunity with local Qwen LLM"""
        print(f"\n🤖 Analyzing: {opportunity['title'][:60]}...")

        prompt = f"""You are an expert business analyst specializing in AI automation opportunities.

Analyze this business opportunity and provide structured scores:

OPPORTUNITY:
Title: {opportunity['title']}
Description: {opportunity['description']}
Revenue Claim: {opportunity['revenue_claim']}
Tech Stack: {opportunity['tech_stack']}
Source: {opportunity['source']}

Provide analysis in JSON format:
{{
    "automation_score": <0-100>,
    "technical_difficulty": <1-5>,
    "time_to_market": "<estimate>",
    "initial_investment": "$<amount>",
    "scalability": <1-5>,
    "legitimacy_score": <0-100>,
    "key_insights": ["insight1", "insight2", "insight3"],
    "automation_opportunities": ["opp1", "opp2"],
    "risks": ["risk1", "risk2"],
    "recommended_action": "<priority: high/medium/low>"
}}

Respond ONLY with valid JSON."""

        try:
            response = requests.post(
                f"{LLAMA_SERVER}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a business analysis expert. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=90
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                # Parse JSON
                if "```json" in analysis_text:
                    analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis_text:
                    analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

                analysis = json.loads(analysis_text)
                print(f"   ✅ Automation: {analysis.get('automation_score', 'N/A')}/100 | "
                      f"Legitimacy: {analysis.get('legitimacy_score', 'N/A')}/100 | "
                      f"Priority: {analysis.get('recommended_action', 'N/A')}")

                self.stats['analyzed'] += 1
                return analysis

            else:
                print(f"   ⚠️  LLM error {response.status_code}, using fallback")
                self.stats['failed'] += 1
                return self._fallback_analysis()

        except Exception as e:
            print(f"   ⚠️  Analysis failed: {e}")
            self.stats['failed'] += 1
            return self._fallback_analysis()

    def _fallback_analysis(self) -> Dict:
        """Fallback when Qwen is unavailable"""
        return {
            "automation_score": 75,
            "technical_difficulty": 3,
            "time_to_market": "3-6 weeks",
            "initial_investment": "$500-1000",
            "scalability": 4,
            "legitimacy_score": 70,
            "key_insights": ["Requires validation", "Automated analysis unavailable"],
            "automation_opportunities": ["API integration", "Payment automation"],
            "risks": ["Market validation needed"],
            "recommended_action": "medium"
        }

    def store_in_business_rag(self, opportunity: Dict, analysis: Dict):
        """Step 3: Store in business RAG"""
        try:
            # Use Xeon Gold ChromaDB (with automatic fallback to local)
            client = get_chroma_client()

            try:
                collection = client.get_collection("business_opportunities")
            except:
                collection = client.create_collection(
                    name="business_opportunities",
                    metadata={"description": "Production business opportunities with AI analysis"}
                )

            # Build document
            document = f"""
# {opportunity['title']}

## Overview
{opportunity['description']}

## Metrics
- Revenue Claim: {opportunity['revenue_claim']}
- Time to Market: {analysis['time_to_market']}
- Initial Investment: {analysis['initial_investment']}
- Automation Score: {analysis['automation_score']}/100
- Legitimacy Score: {analysis['legitimacy_score']}/100
- Recommended Priority: {analysis['recommended_action']}

## Technical Details
- Tech Stack: {opportunity['tech_stack']}
- Difficulty: {analysis['technical_difficulty']}/5
- Scalability: {analysis['scalability']}/5

## AI Analysis
### Key Insights
{chr(10).join('- ' + insight for insight in analysis['key_insights'])}

### Automation Opportunities
{chr(10).join('- ' + opp for opp in analysis['automation_opportunities'])}

### Risks
{chr(10).join('- ' + risk for risk in analysis['risks'])}

## Source
- Platform: {opportunity['source']}
- URL: {opportunity['url']}
- Discovered: {datetime.now().isoformat()}
"""

            doc_id = f"opp_{datetime.now().timestamp()}_{hash(opportunity['url']) % 10000}"

            collection.add(
                ids=[doc_id],
                documents=[document],
                metadatas=[{
                    "title": opportunity['title'],
                    "source": opportunity['source'],
                    "url": opportunity['url'],
                    "revenue_claim": opportunity['revenue_claim'],
                    "automation_score": analysis['automation_score'],
                    "legitimacy_score": analysis['legitimacy_score'],
                    "recommended_action": analysis['recommended_action'],
                    "created_at": datetime.now().isoformat()
                }]
            )

            self.stats['stored'] += 1
            print(f"   💾 Stored in RAG (Total: {collection.count()} opportunities)")

        except Exception as e:
            print(f"   ❌ Storage failed: {e}")
            self.stats['failed'] += 1

    def run_full_pipeline(self):
        """Execute complete production pipeline"""
        print("\n" + "=" * 70)
        print("PRODUCTION OPPORTUNITY RESEARCH BOT")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Scrape
        opportunities = self.scrape_opportunities()

        if not opportunities:
            print("\n❌ No opportunities found. Check API credentials or use --demo mode")
            return

        # Step 2 & 3: Analyze and Store
        print("\n" + "=" * 70)
        print("🤖 STEP 2 & 3: ANALYZING WITH QWEN & STORING IN RAG")
        print("=" * 70)

        for i, opp in enumerate(opportunities, 1):
            print(f"\n[{i}/{len(opportunities)}]", end=" ")
            analysis = self.analyze_with_qwen(opp)
            self.store_in_business_rag(opp, analysis)

        # Summary
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"📊 Statistics:")
        print(f"   • Scraped: {self.stats['scraped']}")
        print(f"   • Analyzed: {self.stats['analyzed']}")
        print(f"   • Stored: {self.stats['stored']}")
        print(f"   • Failed: {self.stats['failed']}")
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {RAG_BUSINESS_DB}")
        print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Production Opportunity Research Pipeline')
    parser.add_argument('--demo', action='store_true', help='Use demo mode (no API keys required)')
    args = parser.parse_args()

    pipeline = ProductionOpportunityPipeline(use_demo_mode=args.demo)
    pipeline.run_full_pipeline()
