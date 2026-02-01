#!/usr/bin/env python3
"""
Live Demo of FICO-Based Personalization
Shows real-world usage with actual credit profiles
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from credit_integration import (
    FICOParser,
    CreditScorer,
    OpportunityRequirements
)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)


def print_subheader(text):
    """Print formatted subheader"""
    print(f"\n{text}")
    print("-" * 70)


def demo_credit_profiles():
    """Demo: Show credit profiles"""
    print_header("DEMO 1: Business Credit Profiles")

    # ISNBIZ
    print_subheader("ISNBIZ, Inc (C-Corporation)")
    isnbiz = FICOParser.create_isnbiz_profile()

    print(f"\n📊 Credit Metrics:")
    print(f"   • Business Delinquency Score: {isnbiz.credit_score}")
    print(f"   • Payment Index: {isnbiz.payment_index}/100 {'🟢 EXCELLENT' if isnbiz.payment_index == 100 else ''}")
    print(f"   • Years in Business: {isnbiz.years_in_business}")
    print(f"   • Active Tradelines: {isnbiz.total_tradelines}")

    print(f"\n💰 Financial Capacity:")
    print(f"   • Total Credit Limit: ${isnbiz.total_credit_limit:,.2f}")
    print(f"   • Available Credit: ${isnbiz.available_credit:,.2f}")
    print(f"   • Max Recommended Investment: ${isnbiz.max_investment_recommendation:,.2f}")

    print(f"\n⚖️  Risk Assessment:")
    print(f"   • Risk Profile: {isnbiz.risk_profile.value.upper()}")
    print(f"   • Strategy: Low-risk, proven models")
    print(f"   • Focus: Quick wins, high automation")

    # HROC
    print_subheader("HROC (Non-Profit)")
    hroc = FICOParser.create_hroc_profile()

    print(f"\n📊 Organization Profile:")
    print(f"   • Business Type: {hroc.business_type.value}")
    print(f"   • Max Recommended Investment: ${hroc.max_investment_recommendation:,.2f}")
    print(f"   • Risk Profile: {hroc.risk_profile.value.upper()}")

    print(f"\n💡 Special Considerations:")
    print(f"   • Must align with 501(c)(3) mission")
    print(f"   • Revenue limits may apply")
    print(f"   • Conservative investment approach")

    return isnbiz, hroc


def demo_opportunity_matching():
    """Demo: Match opportunities to credit profile"""
    print_header("DEMO 2: Intelligent Opportunity Matching")

    isnbiz = FICOParser.create_isnbiz_profile()

    opportunities = [
        {
            'title': '💰 Digital Template Bundle',
            'investment': 50,
            'revenue': 1500,
            'months': 1,
            'risk': 'low',
            'automation': 95,
            'legitimacy': 90,
            'description': 'Create Notion templates, sell on Gumroad'
        },
        {
            'title': '🤖 AI-Powered Chrome Extension',
            'investment': 200,
            'revenue': 3000,
            'months': 2,
            'risk': 'low',
            'automation': 85,
            'legitimacy': 80,
            'description': 'Browser automation tool with AI features'
        },
        {
            'title': '🚀 SaaS Platform Startup',
            'investment': 5000,
            'revenue': 15000,
            'months': 6,
            'risk': 'high',
            'automation': 70,
            'legitimacy': 75,
            'description': 'B2B SaaS with subscription model'
        }
    ]

    print(f"\nYour Profile: {isnbiz.business_name}")
    print(f"Max Investment Capacity: ${isnbiz.max_investment_recommendation:,.2f}")
    print(f"Risk Tolerance: {isnbiz.risk_profile.value.upper()}")

    print_subheader("Scoring Each Opportunity")

    for i, opp in enumerate(opportunities, 1):
        req = OpportunityRequirements(
            min_investment=opp['investment'],
            max_investment=opp['investment'] * 1.5,
            expected_revenue=opp['revenue'],
            time_to_revenue_months=opp['months'],
            risk_level=opp['risk'],
            automation_score=opp['automation'],
            legitimacy_score=opp['legitimacy']
        )

        score = CreditScorer.score_opportunity(isnbiz, req)

        # Determine emoji
        if score.total_score >= 80:
            emoji = "🟢"
        elif score.total_score >= 60:
            emoji = "🟡"
        elif score.total_score >= 40:
            emoji = "🟠"
        else:
            emoji = "🔴"

        print(f"\n{i}. {opp['title']}")
        print(f"   {opp['description']}")
        print(f"\n   💵 Investment: ${opp['investment']:,}")
        print(f"   💰 Expected Revenue: ${opp['revenue']:,}/month")
        print(f"   ⏱️  Time to Revenue: {opp['months']} months")
        print(f"   🤖 Automation: {opp['automation']}/100")
        print(f"\n   {emoji} MATCH SCORE: {score.total_score}/100")
        print(f"   📊 Recommendation: {score.recommendation.upper().replace('_', ' ')}")

        print(f"\n   Score Breakdown:")
        print(f"      • Affordability: {score.affordability_score:.0f}/100")
        print(f"      • Risk Match: {score.risk_match_score:.0f}/100")
        print(f"      • Business Fit: {score.business_type_score:.0f}/100")
        print(f"      • Timeline: {score.timeline_score:.0f}/100")

        print(f"\n   💡 Why this score?")
        for reason in score.reasoning[:2]:
            print(f"      • {reason}")

        if score.total_score >= 80:
            print(f"\n   ✅ Action: START RESEARCHING - Strong fit for your profile")
        elif score.total_score >= 60:
            print(f"\n   ⚠️  Action: EVALUATE CAREFULLY - Good potential with some considerations")
        elif score.total_score >= 40:
            print(f"\n   🤔 Action: CONSIDER ALTERNATIVES - Better options likely available")
        else:
            print(f"\n   ❌ Action: SKIP - Poor fit for current profile")


def demo_portfolio_strategy():
    """Demo: Portfolio strategy recommendations"""
    print_header("DEMO 3: Personalized Portfolio Strategy")

    isnbiz = FICOParser.create_isnbiz_profile()

    print(f"\nBased on your credit profile:")
    print(f"   • Credit Score: {isnbiz.credit_score} (Building History)")
    print(f"   • Payment Index: {isnbiz.payment_index}/100 (Excellent)")
    print(f"   • Max Investment: ${isnbiz.max_investment_recommendation:,.2f}")
    print(f"   • Risk Profile: {isnbiz.risk_profile.value.upper()}")

    print_subheader("Recommended Strategy")

    print(f"\n🎯 APPROACH: Low-Risk, Proven Business Models")
    print(f"\n   Focus on opportunities that:")
    print(f"   ✓ Require <$100 investment")
    print(f"   ✓ Have proven track records")
    print(f"   ✓ Offer quick wins (0-3 months)")
    print(f"   ✓ Are highly automated (80+ score)")
    print(f"   ✓ Generate passive income")

    print_subheader("Recommended Opportunity Types")

    recommendations = [
        {
            'type': '📝 Digital Templates',
            'examples': ['Notion templates', 'Figma design templates', 'Canva templates'],
            'investment': '$20-50',
            'time': '1-2 weeks',
            'why': 'Low cost, high automation, proven marketplace'
        },
        {
            'type': '🤖 Automation Tools',
            'examples': ['Zapier workflows', 'Make scenarios', 'Browser extensions'],
            'investment': '$50-100',
            'time': '2-4 weeks',
            'why': 'One-time build, recurring revenue potential'
        },
        {
            'type': '📚 Educational Content',
            'examples': ['Gumroad guides', 'Video courses', 'Code templates'],
            'investment': '$0-75',
            'time': '1-3 weeks',
            'why': 'Leverage existing knowledge, passive income'
        }
    ]

    for rec in recommendations:
        print(f"\n{rec['type']}")
        print(f"   Examples:")
        for example in rec['examples']:
            print(f"      • {example}")
        print(f"   Investment Range: {rec['investment']}")
        print(f"   Time to Market: {rec['time']}")
        print(f"   Why It Fits: {rec['why']}")

    print_subheader("Growth Path")

    milestones = [
        {
            'phase': 'Phase 1: Now (Conservative)',
            'duration': 'Next 3 months',
            'goal': 'Build foundation',
            'actions': [
                'Launch 1-2 digital products under $100',
                'Establish revenue stream ($500-1000/month)',
                'Build credit history with on-time payments',
                'Add 2-3 business tradelines'
            ]
        },
        {
            'phase': 'Phase 2: Growth (Moderate)',
            'duration': '3-6 months',
            'goal': 'Scale and expand',
            'actions': [
                'Increase credit limits to $5,000',
                'Raise max investment to $1,000',
                'Launch SaaS or subscription model',
                'Target $2,000-3,000/month revenue'
            ]
        },
        {
            'phase': 'Phase 3: Expansion (Aggressive)',
            'duration': '6-12 months',
            'goal': 'High-growth opportunities',
            'actions': [
                'Secure $10,000+ credit capacity',
                'Invest in platform businesses',
                'Build API-based services',
                'Target $5,000-10,000/month revenue'
            ]
        }
    ]

    for milestone in milestones:
        print(f"\n{milestone['phase']}")
        print(f"   Timeline: {milestone['duration']}")
        print(f"   Goal: {milestone['goal']}")
        print(f"   Actions:")
        for action in milestone['actions']:
            print(f"      • {action}")


def demo_comparison():
    """Demo: Compare same opportunity for different entities"""
    print_header("DEMO 4: Multi-Entity Comparison")

    isnbiz = FICOParser.create_isnbiz_profile()
    hroc = FICOParser.create_hroc_profile()

    # Sample opportunity
    opportunity = {
        'title': 'Community Education Platform',
        'investment': 300,
        'revenue': 2000,
        'months': 2,
        'risk': 'medium',
        'automation': 75,
        'legitimacy': 80,
        'description': 'Online courses for local community'
    }

    print(f"\nOpportunity: {opportunity['title']}")
    print(f"Description: {opportunity['description']}")
    print(f"Investment: ${opportunity['investment']}")
    print(f"Expected Revenue: ${opportunity['revenue']}/month")

    req = OpportunityRequirements(
        min_investment=opportunity['investment'],
        max_investment=opportunity['investment'] * 1.5,
        expected_revenue=opportunity['revenue'],
        time_to_revenue_months=opportunity['months'],
        risk_level=opportunity['risk'],
        automation_score=opportunity['automation'],
        legitimacy_score=opportunity['legitimacy']
    )

    # Score for ISNBIZ
    print_subheader("Scoring for ISNBIZ (C-Corp)")
    isnbiz_score = CreditScorer.score_opportunity(isnbiz, req)

    print(f"\n🏢 Business Type: C-Corporation")
    print(f"💰 Max Investment: ${isnbiz.max_investment_recommendation:,.2f}")
    print(f"⚖️  Risk Profile: {isnbiz.risk_profile.value.upper()}")
    print(f"\n{'🟢' if isnbiz_score.total_score >= 60 else '🔴'} Match Score: {isnbiz_score.total_score}/100")
    print(f"📊 Recommendation: {isnbiz_score.recommendation.upper().replace('_', ' ')}")
    print(f"\nKey Insight: {isnbiz_score.reasoning[0] if isnbiz_score.reasoning else 'N/A'}")

    # Score for HROC
    print_subheader("Scoring for HROC (Non-Profit)")
    hroc_score = CreditScorer.score_opportunity(hroc, req)

    print(f"\n🏛️  Business Type: Non-Profit")
    print(f"💰 Max Investment: ${hroc.max_investment_recommendation:,.2f}")
    print(f"⚖️  Risk Profile: {hroc.risk_profile.value.upper()}")
    print(f"\n{'🟢' if hroc_score.total_score >= 60 else '🔴'} Match Score: {hroc_score.total_score}/100")
    print(f"📊 Recommendation: {hroc_score.recommendation.upper().replace('_', ' ')}")
    print(f"\nKey Insight: {hroc_score.reasoning[0] if hroc_score.reasoning else 'N/A'}")

    # Comparison
    print_subheader("Side-by-Side Comparison")

    print(f"\n                      ISNBIZ (C-Corp)    HROC (Non-Profit)")
    print(f"   Match Score:       {isnbiz_score.total_score:>6}/100        {hroc_score.total_score:>6}/100")
    print(f"   Affordability:     {isnbiz_score.affordability_score:>6}/100        {hroc_score.affordability_score:>6}/100")
    print(f"   Risk Match:        {isnbiz_score.risk_match_score:>6}/100        {hroc_score.risk_match_score:>6}/100")
    print(f"   Business Fit:      {isnbiz_score.business_type_score:>6}/100        {hroc_score.business_type_score:>6}/100")
    print(f"   Timeline:          {isnbiz_score.timeline_score:>6}/100        {hroc_score.timeline_score:>6}/100")

    print(f"\n💡 Conclusion:")
    if hroc_score.total_score > isnbiz_score.total_score:
        print(f"   This opportunity is a BETTER fit for HROC")
        print(f"   Reason: Community focus aligns with non-profit mission")
    elif isnbiz_score.total_score > hroc_score.total_score:
        print(f"   This opportunity is a BETTER fit for ISNBIZ")
        print(f"   Reason: Commercial flexibility and higher capacity")
    else:
        print(f"   This opportunity is EQUALLY suitable for both entities")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "FICO-BASED PERSONALIZATION LIVE DEMO" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        # Demo 1: Credit Profiles
        demo_credit_profiles()

        # Demo 2: Opportunity Matching
        demo_opportunity_matching()

        # Demo 3: Portfolio Strategy
        demo_portfolio_strategy()

        # Demo 4: Entity Comparison
        demo_comparison()

        # Summary
        print_header("🎉 DEMO COMPLETE")

        print(f"\n✅ You've seen:")
        print(f"   • How credit profiles are structured")
        print(f"   • How opportunities are scored and matched")
        print(f"   • Personalized portfolio strategies")
        print(f"   • Multi-entity comparisons")

        print(f"\n🚀 Next Steps:")
        print(f"   1. Run setup: ./setup_personalization.sh")
        print(f"   2. Populate database: python3 demo_opportunity_pipeline.py")
        print(f"   3. Try search: python3 query_personalized.py 'AI automation'")
        print(f"   4. Interactive mode: python3 personalized_opportunity_bot.py")

        print(f"\n📚 Documentation:")
        print(f"   • Quick Start: README_PERSONALIZATION.md")
        print(f"   • Full Guide: PERSONALIZATION_GUIDE.md")
        print(f"   • Summary: CREDIT_INTEGRATION_SUMMARY.md")

        print("\n" + "=" * 70)
        print("\n")

    except Exception as e:
        print(f"\n\n❌ DEMO ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
