#!/usr/bin/env python3
"""
Personalized Opportunity Research Bot
Enhanced with FICO credit-based personalization
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add credit_integration to path
sys.path.insert(0, str(Path(__file__).parent))

from credit_integration import (
    FICOParser,
    CreditProfile,
    PersonalizationEngine,
    BusinessType,
    RiskProfile
)


class PersonalizedOpportunityBot:
    """
    Opportunity Research Bot with Credit-Based Personalization

    Features:
    - FICO/Nav business credit integration
    - Personalized recommendations based on financial capacity
    - Risk-adjusted opportunity matching
    - Business type-specific filtering
    """

    def __init__(self, business_entity: str = 'isnbiz'):
        """
        Initialize bot with user's business entity

        Args:
            business_entity: 'isnbiz' (C-Corp) or 'hroc' (Non-Profit)
        """
        self.workspace = Path(__file__).parent.absolute()
        self.rag_db_path = self.workspace / "data" / "chroma_db"

        # Load credit profile
        print(f"🔐 Loading credit profile for: {business_entity.upper()}")
        self.credit_profile = self._load_credit_profile(business_entity)

        # Initialize personalization engine
        self.engine = PersonalizationEngine(self.credit_profile, self.rag_db_path)

        # Display profile
        self._display_profile()

    def _load_credit_profile(self, business_entity: str) -> CreditProfile:
        """Load credit profile for specified business entity"""

        profiles_dir = self.workspace / "credit_integration" / "profiles"
        profiles_dir.mkdir(exist_ok=True)

        profile_file = profiles_dir / f"{business_entity}_profile.json"

        # Try to load from file
        if profile_file.exists():
            print(f"   Loading from: {profile_file}")
            return FICOParser.load_profile(profile_file)

        # Otherwise create and save
        print(f"   Creating new profile...")
        if business_entity.lower() == 'isnbiz':
            profile = FICOParser.create_isnbiz_profile()
        elif business_entity.lower() == 'hroc':
            profile = FICOParser.create_hroc_profile()
        else:
            raise ValueError(f"Unknown business entity: {business_entity}")

        # Save for next time
        FICOParser.save_profile(profile, profile_file)
        print(f"   Saved to: {profile_file}")

        return profile

    def _display_profile(self):
        """Display credit profile summary"""
        p = self.credit_profile

        print("\n" + "=" * 70)
        print("BUSINESS CREDIT PROFILE")
        print("=" * 70)
        print(f"\n🏢 Business: {p.business_name}")
        print(f"📊 Type: {p.business_type.value}")
        print(f"📅 Years in Business: {p.years_in_business}")

        print(f"\n💳 Credit Metrics:")
        if p.credit_score:
            print(f"   • Business Delinquency Score: {p.credit_score}")
        if p.payment_index:
            print(f"   • Payment Index: {p.payment_index}/100")
        print(f"   • Active Tradelines: {p.total_tradelines}")

        print(f"\n💰 Financial Capacity:")
        print(f"   • Total Credit Limit: ${p.total_credit_limit:,.2f}")
        print(f"   • Available Credit: ${p.available_credit:,.2f}")
        print(f"   • Max Recommended Investment: ${p.max_investment_recommendation:,.2f}")

        print(f"\n⚖️  Risk Profile: {p.risk_profile.value.upper()}")

        print("\n" + "=" * 70)

    def search_opportunities(self, query: str, n_results: int = 5):
        """
        Search for personalized opportunities

        Args:
            query: Search query (e.g., "AI automation opportunities")
            n_results: Number of results to return
        """

        print(f"\n🔍 Searching: '{query}'")
        print("   Personalizing based on your credit profile...")
        print()

        # Get personalized recommendations
        recommendations = self.engine.get_personalized_recommendations(query, n_results)

        if not recommendations:
            print("❌ No opportunities found matching your query and credit profile.")
            print("\n💡 Try:")
            print("   • Broader search terms")
            print("   • Running demo_opportunity_pipeline.py to populate database")
            return

        # Display results
        print("=" * 70)
        print(f"PERSONALIZED RECOMMENDATIONS ({len(recommendations)} matches)")
        print("=" * 70)

        for i, rec in enumerate(recommendations, 1):
            self._display_recommendation(i, rec)

        print("\n" + "=" * 70)
        print("💡 Next Steps:")
        print("   • Review match scores and reasoning")
        print("   • Follow action items for top matches")
        print("   • Run get_portfolio_advice() for overall strategy")
        print("=" * 70)

    def _display_recommendation(self, rank: int, rec):
        """Display a single personalized recommendation"""

        opp = rec.opportunity
        score = rec.match_score

        # Header
        print(f"\n{'─' * 70}")
        print(f"#{rank}. {opp.get('title', 'Untitled Opportunity')}")
        print(f"{'─' * 70}")

        # Match Score (color-coded)
        score_emoji = "🟢" if score.total_score >= 80 else "🟡" if score.total_score >= 60 else "🟠"
        print(f"\n{score_emoji} MATCH SCORE: {score.total_score}/100 - {score.recommendation.upper().replace('_', ' ')}")

        # Key Metrics
        print(f"\n📊 Opportunity Metrics:")
        print(f"   • Initial Investment: {opp.get('initial_investment', 'N/A')}")
        print(f"   • Revenue Claim: {opp.get('revenue_claim', 'N/A')}")
        print(f"   • Time to Market: {opp.get('time_to_market', 'N/A')}")
        print(f"   • Automation Score: {opp.get('automation_score', 'N/A')}/100")
        print(f"   • Tech Stack: {opp.get('tech_stack', 'N/A')}")

        # Match Breakdown
        print(f"\n📈 Score Breakdown:")
        print(f"   • Affordability: {score.affordability_score}/100")
        print(f"   • Risk Match: {score.risk_match_score}/100")
        print(f"   • Business Fit: {score.business_type_score}/100")
        print(f"   • Timeline: {score.timeline_score}/100")

        # Personalized Insights
        if rec.personalized_insights:
            print(f"\n💡 Personalized Insights:")
            for insight in rec.personalized_insights[:3]:  # Show top 3
                print(f"   • {insight}")

        # Action Items
        if rec.action_items:
            print(f"\n✅ Action Items:")
            for action in rec.action_items[:3]:  # Show top 3
                print(f"   • {action}")

        # Source
        print(f"\n🔗 Source: {opp.get('source', 'Unknown')} | {opp.get('url', 'N/A')}")

    def get_portfolio_advice(self):
        """Get personalized portfolio strategy advice"""

        print("\n" + "=" * 70)
        print("PERSONALIZED PORTFOLIO STRATEGY")
        print("=" * 70)

        advice = self.engine.generate_portfolio_advice()
        strategy = advice['recommended_strategy']

        print(f"\n🎯 Strategy: {strategy['approach']}")
        print(f"\n💰 Investment Range: {strategy['investment_range']}")
        print(f"🎪 Focus: {strategy['focus']}")
        print(f"⏱️  Timeline: {strategy['timeline']}")
        print(f"🎲 Diversification: {strategy['diversification']}")

        print(f"\n🔍 Recommended Focus Areas:")
        for area in advice['focus_areas']:
            print(f"   • {area}")

        if advice['warnings']:
            print(f"\n⚠️  Important Considerations:")
            for warning in advice['warnings']:
                print(f"   • {warning}")

        print("\n" + "=" * 70)

    def compare_opportunities(self, queries: list):
        """Compare opportunities across different categories"""

        print("\n" + "=" * 70)
        print("OPPORTUNITY COMPARISON")
        print("=" * 70)

        all_recommendations = []

        for query in queries:
            print(f"\n📋 Category: {query}")
            recs = self.engine.get_personalized_recommendations(query, 2)
            if recs:
                all_recommendations.extend(recs)
                print(f"   Found {len(recs)} matches")

        if not all_recommendations:
            print("\n❌ No opportunities found")
            return

        # Sort by match score
        all_recommendations.sort(key=lambda x: x.match_score.total_score, reverse=True)

        print(f"\n\n{'=' * 70}")
        print(f"TOP OPPORTUNITIES ACROSS ALL CATEGORIES")
        print(f"{'=' * 70}")

        for i, rec in enumerate(all_recommendations[:5], 1):
            print(f"\n{i}. {rec.opportunity.get('title')}")
            print(f"   Match Score: {rec.match_score.total_score}/100")
            print(f"   Investment: {rec.opportunity.get('initial_investment')}")
            print(f"   Revenue: {rec.opportunity.get('revenue_claim')}")
            print(f"   Recommendation: {rec.match_score.recommendation.upper().replace('_', ' ')}")

        print("\n" + "=" * 70)

    def interactive_mode(self):
        """Run bot in interactive mode"""

        print("\n" + "=" * 70)
        print("🤖 INTERACTIVE MODE")
        print("=" * 70)
        print("\nCommands:")
        print("  search <query>     - Search for opportunities")
        print("  advice             - Get portfolio strategy advice")
        print("  compare            - Compare opportunity categories")
        print("  profile            - Show credit profile")
        print("  quit/exit          - Exit interactive mode")
        print()

        while True:
            try:
                command = input("\n💬 > ").strip().lower()

                if command in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                elif command == 'advice':
                    self.get_portfolio_advice()

                elif command == 'profile':
                    self._display_profile()

                elif command == 'compare':
                    categories = [
                        "AI automation opportunities",
                        "passive income digital products",
                        "chrome extension business"
                    ]
                    self.compare_opportunities(categories)

                elif command.startswith('search '):
                    query = command[7:]
                    self.search_opportunities(query)

                else:
                    print("❌ Unknown command. Type 'search <query>', 'advice', 'compare', 'profile', or 'quit'")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point"""

    print("=" * 70)
    print("🚀 PERSONALIZED OPPORTUNITY RESEARCH BOT")
    print("   Enhanced with FICO Credit-Based Personalization")
    print("=" * 70)

    # Determine business entity
    if len(sys.argv) > 1:
        entity = sys.argv[1].lower()
    else:
        print("\n🏢 Select Business Entity:")
        print("   1. ISNBIZ (C-Corp)")
        print("   2. HROC (Non-Profit)")
        choice = input("\nChoice (1/2): ").strip()
        entity = 'isnbiz' if choice == '1' else 'hroc'

    # Initialize bot
    bot = PersonalizedOpportunityBot(entity)

    # Get portfolio advice
    bot.get_portfolio_advice()

    # Check if query provided
    if len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        bot.search_opportunities(query)
    else:
        # Interactive mode
        bot.interactive_mode()


if __name__ == "__main__":
    main()
