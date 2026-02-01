#!/usr/bin/env python3
"""Quick script to query the business opportunities RAG"""

import sys
import chromadb
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).parent.absolute()  # opportunity-research-bot directory
RAG_BUSINESS_DB = WORKSPACE / "data" / "chroma_db"

def query_opportunities(query_text, n_results=5):
    """Query the business opportunities database"""
    try:
        client = chromadb.PersistentClient(path=str(RAG_BUSINESS_DB))
        collection = client.get_collection("business_opportunities")

        print(f"\n🔎 Searching for: '{query_text}'")
        print(f"📊 Database has {collection.count()} total opportunities\n")
        print("="* 60)

        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        if not results['documents'][0]:
            print("No results found.")
            return

        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
            print(f"\n{i}. {metadata['title']}")
            print(f"   {'─' * 50}")
            print(f"   💰 Revenue: {metadata['revenue_claim']}")
            print(f"   🤖 Automation Score: {metadata['automation_score']}/100")
            print(f"   ✅ Legitimacy: {metadata['legitimacy_score']}/100")
            print(f"   ⏱️  Time to Market: {metadata['time_to_market']}")
            print(f"   💵 Initial Investment: {metadata['initial_investment']}")
            print(f"   🔧 Tech Stack: {metadata['tech_stack']}")
            print(f"   📍 Source: {metadata['source']}")
            print(f"   🔗 URL: {metadata['url']}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've run the pipeline first:")
        print("  python3 demo_opportunity_pipeline.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 query_opportunities.py 'your search query'")
        print("\nExample queries:")
        print("  python3 query_opportunities.py 'AI automation opportunities'")
        print("  python3 query_opportunities.py 'passive income under $500 investment'")
        print("  python3 query_opportunities.py 'chrome extension business ideas'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    query_opportunities(query)
