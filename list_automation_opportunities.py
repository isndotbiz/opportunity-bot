#!/usr/bin/env python3
"""List all automation opportunities from ChromaDB"""
import chromadb
from pathlib import Path

db_path = Path(__file__).parent / "data" / "chroma_db"
client = chromadb.PersistentClient(path=str(db_path))

try:
    collection = client.get_collection("opportunities")
    results = collection.get()

    print("=" * 70)
    print("🤖 HIGH-AUTOMATION OPPORTUNITIES")
    print("=" * 70)
    print(f"\n📊 Total: {len(results['ids'])} opportunities\n")

    opportunities = []
    for i, doc_id in enumerate(results['ids']):
        opportunities.append({
            'metadata': results['metadatas'][i],
            'document': results['documents'][i]
        })

    opportunities.sort(key=lambda x: x['metadata'].get('automation_score', 0), reverse=True)

    for idx, opp in enumerate(opportunities[:10], 1):
        meta = opp['metadata']
        print(f"\n{idx}. {meta.get('title', 'Untitled')}")
        print("   " + "─" * 65)
        
        automation = meta.get('automation_score', 'N/A')
        if automation != 'N/A':
            bar = "█" * int(automation/10) + "░" * (10 - int(automation/10))
            print(f"   🤖 Automation: [{bar}] {automation}/100")
        
        if 'legitimacy_score' in meta:
            print(f"   ✅ Legitimacy: {meta['legitimacy_score']}/100")
        if 'revenue_potential' in meta:
            print(f"   💰 Revenue: {meta['revenue_potential']}")
        if 'investment_required' in meta:
            print(f"   💵 Investment: {meta['investment_required']}")
        if 'time_to_market' in meta:
            print(f"   ⏱️  Time: {meta['time_to_market']}")
        if 'technical_difficulty' in meta:
            print(f"   🔧 Difficulty: {meta['technical_difficulty']}/5")
        if 'source_url' in meta:
            print(f"   🔗 {meta['source_url'][:70]}")
        
        if opp['document']:
            snippet = opp['document'][:180].replace('\n', ' ')
            print(f"\n   📝 {snippet}...")

    print("\n" + "=" * 70)
except Exception as e:
    print(f"❌ Error: {e}")
