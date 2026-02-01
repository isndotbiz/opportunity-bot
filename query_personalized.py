#!/usr/bin/env python3
"""
Quick personalized query script
Search opportunities with credit-based personalization
"""

import sys
from pathlib import Path
from personalized_opportunity_bot import PersonalizedOpportunityBot


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("Personalized Opportunity Search")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 query_personalized.py <query> [business_entity]")
        print("\nExamples:")
        print("  python3 query_personalized.py 'AI automation' isnbiz")
        print("  python3 query_personalized.py 'passive income' hroc")
        print("  python3 query_personalized.py 'low investment opportunities'")
        print("\nBusiness Entities:")
        print("  isnbiz  - ISNBIZ, Inc (C-Corp) [default]")
        print("  hroc    - HROC (Non-Profit)")
        print()
        sys.exit(1)

    # Parse arguments
    query = sys.argv[1]
    entity = sys.argv[2] if len(sys.argv) > 2 else 'isnbiz'

    # Initialize bot
    bot = PersonalizedOpportunityBot(entity)

    # Search
    bot.search_opportunities(query, n_results=5)


if __name__ == "__main__":
    main()
