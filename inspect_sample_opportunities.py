#!/usr/bin/env python3
"""
Inspect sample opportunities from ChromaDB
"""

import sys
import os
from pathlib import Path
import chromadb

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.absolute()
LOCAL_CHROMA_PATH = WORKSPACE / "data" / "chroma_db"

def inspect_samples():
    """Inspect sample opportunities to understand data quality"""

    try:
        print(f"Connecting to local ChromaDB at {LOCAL_CHROMA_PATH}")
        client = chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))

        # List all collections
        collections = client.list_collections()
        print(f"\nFound {len(collections)} collection(s):")
        for col in collections:
            print(f"  - {col.name}: {col.count()} items")

        collection = client.get_collection("business_opportunities")

        # Get 5 sample opportunities
        results = collection.get(
            limit=5,
            include=['metadatas', 'documents']
        )

        print("\n" + "=" * 80)
        print("SAMPLE OPPORTUNITIES (First 5)")
        print("=" * 80)

        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
            print(f"\n{'=' * 80}")
            print(f"OPPORTUNITY #{i}")
            print(f"{'=' * 80}")

            print(f"\nTitle: {metadata.get('title', 'No title')}")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"URL: {metadata.get('url', 'No URL')}")

            print(f"\n--- SCORES ---")
            print(f"Automation Score: {metadata.get('automation_score', 'N/A')}/100")
            print(f"Legitimacy Score: {metadata.get('legitimacy_score', 'N/A')}/100")

            print(f"\n--- BUSINESS DETAILS ---")
            print(f"Revenue Claim: {metadata.get('revenue_claim', 'Unknown')}")
            print(f"Initial Investment: {metadata.get('initial_investment', 'Unknown')}")
            print(f"Time to Market: {metadata.get('time_to_market', 'Unknown')}")
            print(f"Tech Stack: {metadata.get('tech_stack', 'Not specified')}")

            print(f"\n--- FULL DESCRIPTION ---")
            print(doc[:500] + "..." if len(doc) > 500 else doc)

            print(f"\n--- ALL METADATA FIELDS ---")
            for key, value in metadata.items():
                if key not in ['title', 'source', 'url', 'automation_score', 'legitimacy_score',
                              'revenue_claim', 'initial_investment', 'time_to_market', 'tech_stack']:
                    print(f"{key}: {value}")

        print("\n" + "=" * 80)
        print("DATA QUALITY ASSESSMENT")
        print("=" * 80)

        # Assess data quality
        all_results = collection.get(include=['metadatas'])
        all_metadata = all_results['metadatas']

        # Check for missing fields
        missing_fields = {
            'title': 0,
            'source': 0,
            'url': 0,
            'automation_score': 0,
            'legitimacy_score': 0,
            'revenue_claim': 0,
            'initial_investment': 0,
            'time_to_market': 0,
            'tech_stack': 0
        }

        for metadata in all_metadata:
            for field in missing_fields.keys():
                if field not in metadata or metadata[field] == 'Unknown' or metadata[field] == 'Not specified':
                    missing_fields[field] += 1

        total_count = len(all_metadata)

        print("\nField Completeness:")
        for field, missing_count in sorted(missing_fields.items(), key=lambda x: x[1], reverse=True):
            complete_count = total_count - missing_count
            percentage = (complete_count / total_count) * 100 if total_count > 0 else 0
            status = "OK" if percentage > 70 else "NEEDS IMPROVEMENT"
            print(f"  {field:20s}: {complete_count:2d}/{total_count:2d} complete ({percentage:5.1f}%) - {status}")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\nError inspecting database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_samples()
