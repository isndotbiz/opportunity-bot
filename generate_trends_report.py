#!/usr/bin/env python3
"""
Generate comprehensive trends and insights report from ChromaDB
"""

import sys
import os
from pathlib import Path
from collections import Counter
import statistics
from datetime import datetime
import chromadb
import json

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.absolute()
LOCAL_CHROMA_PATH = WORKSPACE / "data" / "chroma_db"

def generate_report():
    """Generate comprehensive trends report"""

    print(f"Connecting to ChromaDB at {LOCAL_CHROMA_PATH}\n")
    client = chromadb.PersistentClient(path=str(LOCAL_CHROMA_PATH))
    collection = client.get_collection("business_opportunities")

    total_count = collection.count()

    # Create report
    report = []
    report.append("=" * 80)
    report.append("OPPORTUNITY DATABASE TRENDS & INSIGHTS REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Database: {LOCAL_CHROMA_PATH}")
    report.append(f"Total Opportunities: {total_count}")
    report.append("=" * 80)

    if total_count == 0:
        report.append("\nDatabase is empty. No analysis available.")
        print("\n".join(report))
        return

    # Fetch all data
    results = collection.get(include=['metadatas', 'documents'])
    metadatas = results['metadatas']

    # Analysis containers
    automation_scores = []
    legitimacy_scores = []
    sources = []
    categories = []
    investments = {}
    time_to_markets = {}
    revenues = {}

    # Parse all opportunities
    for metadata in metadatas:
        auto = float(metadata.get('automation_score', 0))
        leg = float(metadata.get('legitimacy_score', 0))
        automation_scores.append(auto)
        legitimacy_scores.append(leg)
        sources.append(metadata.get('source', 'unknown'))

        if 'category' in metadata:
            categories.append(metadata['category'])

        inv = metadata.get('initial_investment', 'Unknown')
        investments[inv] = investments.get(inv, 0) + 1

        ttm = metadata.get('time_to_market', 'Unknown')
        time_to_markets[ttm] = time_to_markets.get(ttm, 0) + 1

        rev = metadata.get('revenue_claim', 'Unknown')
        revenues[rev] = revenues.get(rev, 0) + 1

    # === TREND 1: Automation vs Legitimacy ===
    report.append("\n")
    report.append("TREND #1: AUTOMATION VS LEGITIMACY BALANCE")
    report.append("-" * 80)

    avg_auto = statistics.mean(automation_scores)
    avg_leg = statistics.mean(legitimacy_scores)

    report.append(f"Average Automation Score: {avg_auto:.1f}/100")
    report.append(f"Average Legitimacy Score: {avg_leg:.1f}/100")
    report.append(f"Difference: {abs(avg_auto - avg_leg):.1f} points")

    if avg_auto > avg_leg + 10:
        report.append("\nINSIGHT: Opportunities skew toward high automation but lower legitimacy.")
        report.append("ACTION: Focus on vetting sources and filtering speculative opportunities.")
    elif avg_leg > avg_auto + 10:
        report.append("\nINSIGHT: Opportunities are legitimate but have lower automation potential.")
        report.append("ACTION: Look for more automation-focused niches (AI tools, SaaS, automation).")
    else:
        report.append("\nINSIGHT: Good balance between automation potential and legitimacy.")
        report.append("ACTION: Continue current scraping strategy.")

    # High scorers
    high_both = sum(1 for a, l in zip(automation_scores, legitimacy_scores) if a > 80 and l > 85)
    high_auto = sum(1 for a in automation_scores if a > 80)
    high_leg = sum(1 for l in legitimacy_scores if l > 85)

    report.append(f"\nHigh Automation (>80): {high_auto} ({high_auto/total_count*100:.1f}%)")
    report.append(f"High Legitimacy (>85): {high_leg} ({high_leg/total_count*100:.1f}%)")
    report.append(f"Both High: {high_both} ({high_both/total_count*100:.1f}%)")

    if high_both < 5:
        report.append("\nWARNING: Very few opportunities meet both criteria.")
        report.append("ACTION: Expand to more premium sources or adjust scoring thresholds.")

    # === TREND 2: Source Performance ===
    report.append("\n")
    report.append("TREND #2: SOURCE PERFORMANCE")
    report.append("-" * 80)

    source_counts = Counter(sources)
    report.append(f"Total Sources: {len(source_counts)}")

    # Calculate average scores per source
    source_scores = {}
    for metadata in metadatas:
        source = metadata.get('source', 'unknown')
        auto = float(metadata.get('automation_score', 0))
        leg = float(metadata.get('legitimacy_score', 0))

        if source not in source_scores:
            source_scores[source] = {'auto': [], 'leg': []}

        source_scores[source]['auto'].append(auto)
        source_scores[source]['leg'].append(leg)

    report.append("\nSource Performance (sorted by quality):")
    source_quality = []
    for source, scores in source_scores.items():
        avg_auto = statistics.mean(scores['auto'])
        avg_leg = statistics.mean(scores['leg'])
        combined = avg_auto + avg_leg
        count = source_counts[source]

        source_quality.append({
            'source': source,
            'count': count,
            'auto': avg_auto,
            'leg': avg_leg,
            'combined': combined
        })

    source_quality.sort(key=lambda x: x['combined'], reverse=True)

    for sq in source_quality:
        report.append(f"  {sq['source']:30s}: {sq['count']:3d} opps | Auto: {sq['auto']:5.1f} | Leg: {sq['leg']:5.1f} | Total: {sq['combined']:6.1f}")

    best_source = source_quality[0] if source_quality else None
    if best_source:
        report.append(f"\nBEST SOURCE: {best_source['source']} (Quality Score: {best_source['combined']:.1f})")
        report.append(f"ACTION: Prioritize scraping from {best_source['source']}")

    # === TREND 3: Investment Patterns ===
    report.append("\n")
    report.append("TREND #3: INVESTMENT PATTERNS")
    report.append("-" * 80)

    # Categorize investments
    zero_investment = sum(count for inv, count in investments.items() if '$0' in inv or 'minimal' in inv.lower())
    low_investment = sum(count for inv, count in investments.items() if any(x in inv for x in ['$100', '$200', '$300', '$400', '$500']))
    mid_investment = sum(count for inv, count in investments.items() if any(x in inv for x in ['$1000', '$2000', '$3000', '$5000']))
    high_investment = sum(count for inv, count in investments.items() if any(x in inv for x in ['$10000', '$20000', '$50000']))
    unknown_investment = investments.get('Unknown', 0)

    report.append(f"Zero Investment ($0): {zero_investment} ({zero_investment/total_count*100:.1f}%)")
    report.append(f"Low Investment (<$1K): {low_investment} ({low_investment/total_count*100:.1f}%)")
    report.append(f"Mid Investment ($1K-$10K): {mid_investment} ({mid_investment/total_count*100:.1f}%)")
    report.append(f"High Investment (>$10K): {high_investment} ({high_investment/total_count*100:.1f}%)")
    report.append(f"Unknown: {unknown_investment} ({unknown_investment/total_count*100:.1f}%)")

    if unknown_investment > total_count * 0.4:
        report.append("\nWARNING: Many opportunities lack investment data.")
        report.append("ACTION: Improve scraping to extract investment estimates.")

    accessible_count = zero_investment + low_investment
    report.append(f"\nAccessible Opportunities (<$1K): {accessible_count} ({accessible_count/total_count*100:.1f}%)")

    if accessible_count < total_count * 0.5:
        report.append("ACTION: Focus on low-barrier-to-entry opportunities for wider appeal.")

    # === TREND 4: Time to Market ===
    report.append("\n")
    report.append("TREND #4: TIME TO MARKET ANALYSIS")
    report.append("-" * 80)

    # Categorize time to market
    quick_wins = sum(count for ttm, count in time_to_markets.items()
                     if any(x in ttm.lower() for x in ['week', 'days', '1-2']))
    moderate_time = sum(count for ttm, count in time_to_markets.items()
                       if any(x in ttm.lower() for x in ['month', '2-3', '3-4']))
    long_term = sum(count for ttm, count in time_to_markets.items()
                   if any(x in ttm.lower() for x in ['6', 'year', 'quarter']))
    unknown_time = time_to_markets.get('Unknown', 0)

    report.append(f"Quick Wins (<1 month): {quick_wins} ({quick_wins/total_count*100:.1f}%)")
    report.append(f"Moderate (1-3 months): {moderate_time} ({moderate_time/total_count*100:.1f}%)")
    report.append(f"Long-term (>3 months): {long_term} ({long_term/total_count*100:.1f}%)")
    report.append(f"Unknown: {unknown_time} ({unknown_time/total_count*100:.1f}%)")

    if quick_wins < total_count * 0.3:
        report.append("\nINSIGHT: Few quick-win opportunities.")
        report.append("ACTION: Add sources focused on rapid MVPs and side projects.")

    # === TREND 5: Revenue Patterns ===
    report.append("\n")
    report.append("TREND #5: REVENUE PATTERNS")
    report.append("-" * 80)

    # Parse revenue claims
    low_revenue = sum(1 for rev in revenues.keys() if any(x in rev for x in ['$500', '$1000', '$1500', '$2000']))
    mid_revenue = sum(1 for rev in revenues.keys() if any(x in rev for x in ['$3000', '$4000', '$5000', '$8000', '$10000']))
    high_revenue = sum(1 for rev in revenues.keys() if any(x in rev for x in ['$20000', '$50000', '$100000']))

    report.append(f"Low Revenue (<$2K/mo): {low_revenue}")
    report.append(f"Mid Revenue ($2K-$10K/mo): {mid_revenue}")
    report.append(f"High Revenue (>$10K/mo): {high_revenue}")

    report.append("\nTop 5 Revenue Claims:")
    revenue_list = [(rev, count) for rev, count in revenues.items() if rev != 'Unknown']
    revenue_list.sort(key=lambda x: x[1], reverse=True)

    for rev, count in revenue_list[:5]:
        report.append(f"  {rev:30s}: {count} opportunities")

    # === TREND 6: Category Distribution ===
    if categories:
        report.append("\n")
        report.append("TREND #6: CATEGORY DISTRIBUTION")
        report.append("-" * 80)

        category_counts = Counter(categories)
        for category, count in category_counts.most_common():
            percentage = (count / total_count) * 100
            report.append(f"  {category:30s}: {count} ({percentage:.1f}%)")

    # === GAPS & RECOMMENDATIONS ===
    report.append("\n")
    report.append("GAPS & EXPANSION OPPORTUNITIES")
    report.append("-" * 80)

    gaps = []

    if high_both < total_count * 0.2:
        gaps.append("FEW HIGH-QUALITY OPPORTUNITIES: Need more premium sources")

    if unknown_investment > total_count * 0.4:
        gaps.append("MISSING INVESTMENT DATA: Improve data extraction")

    if len(source_counts) < 5:
        gaps.append("LIMITED SOURCE DIVERSITY: Add more data sources")

    if accessible_count < total_count * 0.5:
        gaps.append("HIGH BARRIERS TO ENTRY: Focus on low-investment opportunities")

    if quick_wins < total_count * 0.3:
        gaps.append("FEW QUICK WINS: Need more rapid-launch opportunities")

    # Suggest new categories
    existing_categories = set(categories) if categories else set()
    suggested_categories = {
        'e-commerce', 'content-creation', 'automation', 'saas',
        'marketplace', 'ai-tools', 'chrome-extensions', 'mobile-apps',
        'newsletters', 'courses', 'templates', 'apis'
    }

    missing_categories = suggested_categories - existing_categories
    if missing_categories:
        gaps.append(f"UNEXPLORED CATEGORIES: {', '.join(list(missing_categories)[:5])}")

    if gaps:
        report.append("Identified Gaps:")
        for i, gap in enumerate(gaps, 1):
            report.append(f"  {i}. {gap}")
    else:
        report.append("No major gaps identified. Database is well-rounded.")

    # === ACTIONABLE RECOMMENDATIONS ===
    report.append("\n")
    report.append("ACTIONABLE RECOMMENDATIONS")
    report.append("-" * 80)

    recommendations = []

    # Based on source performance
    if best_source and best_source['count'] < total_count * 0.5:
        recommendations.append(f"Increase scraping frequency from {best_source['source']} (highest quality)")

    # Based on investment
    if accessible_count < total_count * 0.5:
        recommendations.append("Target subreddits focused on bootstrapping and low-budget startups")

    # Based on scores
    if avg_auto < 75:
        recommendations.append("Filter for automation keywords: 'automated', 'passive', 'AI', 'API'")

    if avg_leg < 70:
        recommendations.append("Prioritize verified revenue sources (Indie Hackers, verified posts)")

    # Based on time to market
    if quick_wins < total_count * 0.3:
        recommendations.append("Add sources for MVP-focused communities (r/roastmystartup, r/IMadeThis)")

    # Category expansion
    if 'ai-tools' not in existing_categories:
        recommendations.append("Explore AI tool directories and marketplaces")

    if len(source_counts) < 5:
        recommendations.append("Add new sources: Product Hunt, Hacker News Show HN, Twitter #buildinpublic")

    for i, rec in enumerate(recommendations, 1):
        report.append(f"  {i}. {rec}")

    # === DATABASE HEALTH ===
    report.append("\n")
    report.append("DATABASE HEALTH")
    report.append("-" * 80)

    # Calculate completeness
    complete_opportunities = sum(
        1 for m in metadatas
        if all(k in m and m[k] not in ['Unknown', 'Not specified', '']
               for k in ['title', 'source', 'automation_score', 'legitimacy_score'])
    )

    completeness = (complete_opportunities / total_count) * 100 if total_count > 0 else 0

    report.append(f"Complete Records: {complete_opportunities}/{total_count} ({completeness:.1f}%)")
    report.append(f"Database Size: ~{total_count * 5} KB")
    report.append(f"Last Modified: Today")

    if completeness > 80:
        report.append("STATUS: HEALTHY - High data quality")
    elif completeness > 60:
        report.append("STATUS: GOOD - Acceptable data quality")
    else:
        report.append("STATUS: NEEDS IMPROVEMENT - Many incomplete records")

    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    # Print report
    full_report = "\n".join(report)
    print(full_report)

    # Save to file
    report_file = WORKSPACE / "reports" / f"trends_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(full_report)

    print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    generate_report()
