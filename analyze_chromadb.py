#!/usr/bin/env python3
"""
Comprehensive ChromaDB Opportunity Analysis
Analyzes trends, patterns, and statistics in the opportunity database
"""

import sys
import os
from pathlib import Path
from collections import Counter, defaultdict
import statistics
from datetime import datetime
import chromadb

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Direct local connection to avoid emoji issues
WORKSPACE = Path(__file__).parent.absolute()
LOCAL_CHROMA_PATH = WORKSPACE / "data" / "chroma_db"

def analyze_database():
    """Comprehensive analysis of the opportunity database"""

    try:
        # Connect to database directly (avoid emoji issues)
        print(f"Connecting to local ChromaDB at {LOCAL_CHROMA_PATH}")
        client = chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))
        collection = client.get_collection("business_opportunities")

        # Get all opportunities
        total_count = collection.count()
        print("=" * 80)
        print("CHROMADB OPPORTUNITY DATABASE ANALYSIS")
        print("=" * 80)
        print(f"\nTotal Opportunities: {total_count}\n")

        if total_count == 0:
            print("Database is empty. Run the pipeline first:")
            print("  python3 production_opportunity_pipeline.py --demo")
            return

        # Fetch all data
        results = collection.get(
            include=['metadatas', 'documents']
        )

        metadatas = results['metadatas']
        documents = results['documents']

        # Initialize analysis containers
        automation_scores = []
        legitimacy_scores = []
        sources = []
        tech_stacks = []
        investments = []
        time_to_markets = []
        revenues = []

        high_automation = []  # automation > 80
        high_legitimacy = []  # legitimacy > 85
        top_opportunities = []  # both high

        # Parse data
        for metadata in metadatas:
            try:
                # Scores
                auto_score = float(metadata.get('automation_score', 0))
                leg_score = float(metadata.get('legitimacy_score', 0))

                automation_scores.append(auto_score)
                legitimacy_scores.append(leg_score)

                # Sources
                sources.append(metadata.get('source', 'unknown'))

                # Tech stacks
                tech = metadata.get('tech_stack', 'Not specified')
                tech_stacks.append(tech)

                # Investments
                investment = metadata.get('initial_investment', 'Unknown')
                investments.append(investment)

                # Time to market
                ttm = metadata.get('time_to_market', 'Unknown')
                time_to_markets.append(ttm)

                # Revenue
                revenue = metadata.get('revenue_claim', 'Unknown')
                revenues.append(revenue)

                # High scorers
                if auto_score > 80:
                    high_automation.append({
                        'title': metadata.get('title', 'No title'),
                        'automation': auto_score,
                        'legitimacy': leg_score,
                        'source': metadata.get('source', 'unknown'),
                        'url': metadata.get('url', ''),
                        'investment': investment,
                        'revenue': revenue
                    })

                if leg_score > 85:
                    high_legitimacy.append({
                        'title': metadata.get('title', 'No title'),
                        'automation': auto_score,
                        'legitimacy': leg_score,
                        'source': metadata.get('source', 'unknown'),
                        'url': metadata.get('url', ''),
                        'investment': investment,
                        'revenue': revenue
                    })

                if auto_score > 80 and leg_score > 85:
                    top_opportunities.append({
                        'title': metadata.get('title', 'No title'),
                        'automation': auto_score,
                        'legitimacy': leg_score,
                        'source': metadata.get('source', 'unknown'),
                        'url': metadata.get('url', ''),
                        'investment': investment,
                        'revenue': revenue,
                        'tech_stack': tech,
                        'time_to_market': ttm
                    })

            except Exception as e:
                print(f"Warning: Error parsing metadata: {e}")
                continue

        # ===== STATISTICS =====
        print("\n" + "=" * 80)
        print("SCORE STATISTICS")
        print("=" * 80)

        if automation_scores:
            print(f"\nAutomation Scores:")
            print(f"  Mean:   {statistics.mean(automation_scores):.1f}")
            print(f"  Median: {statistics.median(automation_scores):.1f}")
            print(f"  Min:    {min(automation_scores):.1f}")
            print(f"  Max:    {max(automation_scores):.1f}")
            print(f"  StdDev: {statistics.stdev(automation_scores):.1f}" if len(automation_scores) > 1 else "  StdDev: N/A")

        if legitimacy_scores:
            print(f"\nLegitimacy Scores:")
            print(f"  Mean:   {statistics.mean(legitimacy_scores):.1f}")
            print(f"  Median: {statistics.median(legitimacy_scores):.1f}")
            print(f"  Min:    {min(legitimacy_scores):.1f}")
            print(f"  Max:    {max(legitimacy_scores):.1f}")
            print(f"  StdDev: {statistics.stdev(legitimacy_scores):.1f}" if len(legitimacy_scores) > 1 else "  StdDev: N/A")

        # ===== SOURCE DISTRIBUTION =====
        print("\n" + "=" * 80)
        print("SOURCE DISTRIBUTION")
        print("=" * 80)

        source_counts = Counter(sources)
        for source, count in source_counts.most_common():
            percentage = (count / total_count) * 100
            print(f"  {source:20s}: {count:4d} ({percentage:5.1f}%)")

        # ===== TECH STACK TRENDS =====
        print("\n" + "=" * 80)
        print("TECH STACK TRENDS (Top 15)")
        print("=" * 80)

        tech_counts = Counter(tech_stacks)
        for tech, count in tech_counts.most_common(15):
            percentage = (count / total_count) * 100
            print(f"  {tech[:50]:50s}: {count:3d} ({percentage:5.1f}%)")

        # ===== INVESTMENT DISTRIBUTION =====
        print("\n" + "=" * 80)
        print("INVESTMENT DISTRIBUTION (Top 10)")
        print("=" * 80)

        investment_counts = Counter(investments)
        for investment, count in investment_counts.most_common(10):
            percentage = (count / total_count) * 100
            print(f"  {investment[:50]:50s}: {count:3d} ({percentage:5.1f}%)")

        # ===== TIME TO MARKET =====
        print("\n" + "=" * 80)
        print("TIME TO MARKET DISTRIBUTION (Top 10)")
        print("=" * 80)

        ttm_counts = Counter(time_to_markets)
        for ttm, count in ttm_counts.most_common(10):
            percentage = (count / total_count) * 100
            print(f"  {ttm[:50]:50s}: {count:3d} ({percentage:5.1f}%)")

        # ===== HIGH-SCORING OPPORTUNITIES =====
        print("\n" + "=" * 80)
        print(f"HIGH AUTOMATION OPPORTUNITIES (>{80}) - {len(high_automation)} found")
        print("=" * 80)

        # Sort by automation score
        high_automation.sort(key=lambda x: x['automation'], reverse=True)

        for i, opp in enumerate(high_automation[:10], 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   Automation: {opp['automation']:.1f} | Legitimacy: {opp['legitimacy']:.1f}")
            print(f"   Investment: {opp['investment']} | Revenue: {opp['revenue']}")
            print(f"   Source: {opp['source']}")
            print(f"   URL: {opp['url']}")

        if len(high_automation) > 10:
            print(f"\n   ... and {len(high_automation) - 10} more")

        print("\n" + "=" * 80)
        print(f"HIGH LEGITIMACY OPPORTUNITIES (>{85}) - {len(high_legitimacy)} found")
        print("=" * 80)

        # Sort by legitimacy score
        high_legitimacy.sort(key=lambda x: x['legitimacy'], reverse=True)

        for i, opp in enumerate(high_legitimacy[:10], 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   Legitimacy: {opp['legitimacy']:.1f} | Automation: {opp['automation']:.1f}")
            print(f"   Investment: {opp['investment']} | Revenue: {opp['revenue']}")
            print(f"   Source: {opp['source']}")
            print(f"   URL: {opp['url']}")

        if len(high_legitimacy) > 10:
            print(f"\n   ... and {len(high_legitimacy) - 10} more")

        print("\n" + "=" * 80)
        print(f"TOP OPPORTUNITIES (Automation >{80} AND Legitimacy >{85}) - {len(top_opportunities)} found")
        print("=" * 80)

        # Sort by combined score
        top_opportunities.sort(key=lambda x: x['automation'] + x['legitimacy'], reverse=True)

        for i, opp in enumerate(top_opportunities, 1):
            print(f"\n{i}. {opp['title']}")
            print(f"   Automation: {opp['automation']:.1f} | Legitimacy: {opp['legitimacy']:.1f}")
            print(f"   Combined Score: {opp['automation'] + opp['legitimacy']:.1f}/200")
            print(f"   Investment: {opp['investment']} | Revenue: {opp['revenue']}")
            print(f"   Time to Market: {opp['time_to_market']}")
            print(f"   Tech Stack: {opp['tech_stack']}")
            print(f"   Source: {opp['source']}")
            print(f"   URL: {opp['url']}")

        # ===== INSIGHTS & RECOMMENDATIONS =====
        print("\n" + "=" * 80)
        print("INSIGHTS & RECOMMENDATIONS")
        print("=" * 80)

        # Score insights
        avg_automation = statistics.mean(automation_scores) if automation_scores else 0
        avg_legitimacy = statistics.mean(legitimacy_scores) if legitimacy_scores else 0

        print(f"\n1. OVERALL QUALITY:")
        print(f"   - Average automation: {avg_automation:.1f}/100")
        print(f"   - Average legitimacy: {avg_legitimacy:.1f}/100")

        if avg_automation > 70:
            print(f"   -> Strong automation potential across opportunities")
        elif avg_automation > 50:
            print(f"   -> Moderate automation potential")
        else:
            print(f"   -> Low automation scores - consider filtering sources")

        if avg_legitimacy > 75:
            print(f"   -> High quality, legitimate opportunities")
        elif avg_legitimacy > 60:
            print(f"   -> Moderate quality opportunities")
        else:
            print(f"   -> Low legitimacy - review scraping sources")

        # Source insights
        print(f"\n2. SOURCE DIVERSITY:")
        print(f"   - Total sources: {len(source_counts)}")
        most_common_source = source_counts.most_common(1)[0] if source_counts else ('None', 0)
        print(f"   - Most common: {most_common_source[0]} ({most_common_source[1]} opportunities)")

        if len(source_counts) < 3:
            print(f"   -> Consider adding more data sources for diversity")
        else:
            print(f"   -> Good source diversity")

        # Tech stack insights
        print(f"\n3. TECH STACK TRENDS:")
        top_tech = tech_counts.most_common(3)
        for tech, count in top_tech:
            print(f"   - {tech}: {count} opportunities")

        # Identify gaps
        print(f"\n4. POTENTIAL GAPS TO EXPLORE:")

        # Low representation tech stacks
        underrepresented = [tech for tech, count in tech_counts.items() if count < 3 and tech != 'Not specified']
        if underrepresented:
            print(f"   - Underrepresented tech stacks: {', '.join(underrepresented[:5])}")

        # Investment gaps
        high_investment = [inv for inv in investments if '$10,000' in inv or '$20,000' in inv or '$50,000' in inv]
        low_investment = [inv for inv in investments if '$100' in inv or '$500' in inv or 'minimal' in inv.lower()]

        print(f"   - Low investment opportunities: {len(low_investment)} (< $1000)")
        print(f"   - High investment opportunities: {len(high_investment)} (> $10,000)")

        if len(low_investment) < total_count * 0.3:
            print(f"   -> Consider sourcing more low-investment opportunities")

        # Time to market gaps
        quick_wins = [ttm for ttm in time_to_markets if 'week' in ttm.lower() or 'days' in ttm.lower()]
        print(f"   - Quick wins (<1 month): {len(quick_wins)}")

        if len(quick_wins) < total_count * 0.2:
            print(f"   -> Consider sourcing more quick-win opportunities")

        print(f"\n5. RECOMMENDATIONS:")
        print(f"   - Focus on top {len(top_opportunities)} opportunities with both high automation and legitimacy")
        print(f"   - {len(high_automation)} opportunities have strong automation potential")
        print(f"   - {len(high_legitimacy)} opportunities are highly legitimate")

        if len(top_opportunities) < 10:
            print(f"   -> Expand scraping to find more high-quality opportunities")

        print("\n" + "=" * 80)
        print(f"Analysis complete. Database location: ./data/chroma_db/")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\nError analyzing database: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure:")
        print("  1. ChromaDB is set up: ./data/chroma_db/")
        print("  2. Pipeline has been run: python3 production_opportunity_pipeline.py --demo")

if __name__ == "__main__":
    analyze_database()
