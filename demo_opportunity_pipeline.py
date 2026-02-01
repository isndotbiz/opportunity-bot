#!/usr/bin/env python3
"""
Opportunity Research Bot Demo - Full Pipeline
Scrapes opportunities -> Analyzes with local Qwen -> Stores in business RAG
"""

import os
import json
import requests
import chromadb
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).parent.absolute()  # opportunity-research-bot directory
LLAMA_SERVER = "http://localhost:8080"
EMBEDDING_SERVER = "http://localhost:8001"
RAG_BUSINESS_DB = WORKSPACE / "data" / "chroma_db"

class OpportunityPipeline:
    def __init__(self):
        self.opportunities = []

    def scrape_opportunities(self):
        """Step 1: Scrape opportunities from multiple sources"""
        print("\n🔍 Step 1: Scraping Opportunities...")

        # Demo: Simulating scraped opportunities
        # In production, this would use Reddit API, Indie Hackers, etc.
        demo_opportunities = [
            {
                "title": "AI-Powered Content Repurposing Tool",
                "source": "Reddit r/SideProject",
                "url": "https://reddit.com/r/SideProject/example1",
                "description": "Tool that takes long-form content and automatically creates Twitter threads, LinkedIn posts, and blog summaries. Built with GPT-4 API. Revenue: $3K/month after 2 months.",
                "revenue_claim": "$3000/month",
                "tech_stack": "Python, GPT-4 API, Stripe",
                "time_mentioned": "2 months to $3K MRR"
            },
            {
                "title": "Automated Notion Template Marketplace",
                "source": "Indie Hackers",
                "url": "https://indiehackers.com/example2",
                "description": "Selling Notion templates on autopilot. Created 20 templates, listed on Gumroad, automated email sequences. Zero ongoing work. Revenue: $2K/month.",
                "revenue_claim": "$2000/month",
                "tech_stack": "Notion, Gumroad, ConvertKit",
                "time_mentioned": "1 month setup, passive income"
            },
            {
                "title": "Chrome Extension for LinkedIn Automation",
                "source": "Reddit r/Entrepreneur",
                "url": "https://reddit.com/r/Entrepreneur/example3",
                "description": "Chrome extension that auto-personalizes LinkedIn connection requests using AI. Subscription model. Built in 1 week, scaled to $5K MRR in 3 months.",
                "revenue_claim": "$5000/month",
                "tech_stack": "JavaScript, OpenAI API, Stripe",
                "time_mentioned": "1 week build, 3 months to $5K"
            }
        ]

        self.opportunities = demo_opportunities
        print(f"✅ Found {len(self.opportunities)} opportunities")
        return self.opportunities

    def analyze_with_local_qwen(self, opportunity):
        """Step 2: Analyze opportunity with local Qwen LLM"""
        print(f"\n🤖 Analyzing: {opportunity['title']}")

        # Build analysis prompt
        prompt = f"""You are an expert business analyst specializing in AI automation opportunities.

Analyze this business opportunity and provide structured scores:

OPPORTUNITY:
Title: {opportunity['title']}
Description: {opportunity['description']}
Revenue Claim: {opportunity['revenue_claim']}
Tech Stack: {opportunity['tech_stack']}
Time to Revenue: {opportunity['time_mentioned']}

Provide analysis in JSON format:
{{
    "automation_score": <0-100>,  // How automated is this?
    "technical_difficulty": <1-5>,  // 1=easy, 5=hard
    "time_to_market": "<estimate>",  // How long to build?
    "initial_investment": "$<amount>",  // Startup costs
    "scalability": <1-5>,  // 1=low, 5=high
    "legitimacy_score": <0-100>,  // Is this real/viable?
    "key_insights": ["insight1", "insight2", "insight3"],
    "automation_opportunities": ["opp1", "opp2"],
    "risks": ["risk1", "risk2"]
}}

Respond ONLY with valid JSON."""

        try:
            # Call local Qwen via llama-cpp-server
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
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']

                # Parse JSON from response
                try:
                    # Extract JSON if wrapped in markdown
                    if "```json" in analysis_text:
                        analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in analysis_text:
                        analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

                    analysis = json.loads(analysis_text)
                    print(f"   Automation Score: {analysis.get('automation_score', 'N/A')}/100")
                    print(f"   Legitimacy: {analysis.get('legitimacy_score', 'N/A')}/100")
                    return analysis
                except json.JSONDecodeError:
                    print(f"   ⚠️  Failed to parse JSON, using fallback")
                    return self._fallback_analysis(opportunity)
            else:
                print(f"   ⚠️  LLM server error: {response.status_code}")
                return self._fallback_analysis(opportunity)

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  LLM server not running: {e}")
            print("   ℹ️  Using fallback analysis (start llama-cpp-docker for real analysis)")
            return self._fallback_analysis(opportunity)

    def _fallback_analysis(self, opportunity):
        """Fallback analysis when LLM is unavailable"""
        return {
            "automation_score": 85,
            "technical_difficulty": 2,
            "time_to_market": "2-4 weeks",
            "initial_investment": "$500",
            "scalability": 4,
            "legitimacy_score": 80,
            "key_insights": ["High automation potential", "Proven revenue model", "Low initial cost"],
            "automation_opportunities": ["API integration", "Automated marketing", "Subscription billing"],
            "risks": ["Market competition", "API dependency"]
        }

    def store_in_business_rag(self, opportunity, analysis):
        """Step 3: Store in business RAG (ChromaDB)"""
        print(f"\n💾 Storing in Business RAG...")

        # Ensure RAG database directory exists
        RAG_BUSINESS_DB.mkdir(parents=True, exist_ok=True)

        try:
            # Connect to ChromaDB
            client = chromadb.PersistentClient(path=str(RAG_BUSINESS_DB))

            # Get or create collection
            try:
                collection = client.get_collection("business_opportunities")
            except:
                collection = client.create_collection(
                    name="business_opportunities",
                    metadata={"description": "Curated business opportunities with AI automation potential"}
                )

            # Build document for RAG
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

## Technical Details
- Tech Stack: {opportunity['tech_stack']}
- Difficulty: {analysis['technical_difficulty']}/5
- Scalability: {analysis['scalability']}/5

## Analysis
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

            # Generate document ID
            doc_id = f"opp_{datetime.now().timestamp()}"

            # Add to collection
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
                    "tech_stack": opportunity['tech_stack'],
                    "time_to_market": analysis['time_to_market'],
                    "initial_investment": analysis['initial_investment'],
                    "created_at": datetime.now().isoformat(),
                    "category": "ai-automation"
                }]
            )

            print(f"✅ Stored opportunity ID: {doc_id}")
            print(f"   Collection now has {collection.count()} opportunities")

        except Exception as e:
            print(f"❌ Error storing in RAG: {e}")
            print(f"   Make sure chromadb is installed: pip install chromadb")

    def query_business_rag(self, query):
        """Query the business RAG for insights"""
        print(f"\n🔎 Querying Business RAG: '{query}'")

        try:
            client = chromadb.PersistentClient(path=str(RAG_BUSINESS_DB))
            collection = client.get_collection("business_opportunities")

            results = collection.query(
                query_texts=[query],
                n_results=3
            )

            print(f"\n📊 Top {len(results['documents'][0])} Results:")
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                print(f"\n{i}. {metadata['title']}")
                print(f"   Automation: {metadata['automation_score']}/100")
                print(f"   Revenue: {metadata['revenue_claim']}")
                print(f"   Time to Market: {metadata['time_to_market']}")
                print(f"   Source: {metadata['source']}")

        except Exception as e:
            print(f"❌ Error querying RAG: {e}")

    def run_full_pipeline(self):
        """Run the complete pipeline"""
        print("=" * 60)
        print("🚀 OPPORTUNITY RESEARCH BOT - FULL PIPELINE DEMO")
        print("=" * 60)

        # Step 1: Scrape
        opportunities = self.scrape_opportunities()

        # Step 2 & 3: Analyze and Store
        for opp in opportunities:
            analysis = self.analyze_with_local_qwen(opp)
            self.store_in_business_rag(opp, analysis)

        # Step 4: Demo query
        print("\n" + "=" * 60)
        print("🎯 DEMO: Querying Business RAG")
        print("=" * 60)

        self.query_business_rag("high automation passive income opportunities under $1000 investment")

        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"\n💡 Next Steps:")
        print(f"   1. Start llama-cpp-docker for real Qwen analysis:")
        print(f"      cd llama-cpp-docker && docker-compose up -d")
        print(f"   2. View stored opportunities in: {RAG_BUSINESS_DB}")
        print(f"   3. Query anytime: pipeline.query_business_rag('your question')")
        print()


if __name__ == "__main__":
    pipeline = OpportunityPipeline()
    pipeline.run_full_pipeline()
