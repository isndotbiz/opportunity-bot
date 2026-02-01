#!/usr/bin/env python3
"""
Personalization Engine
Personalizes opportunity recommendations based on credit profile
"""

import chromadb
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
from .fico_parser import CreditProfile, RiskProfile, BusinessType
from .credit_scorer import CreditScorer, MatchScore


@dataclass
class PersonalizedRecommendation:
    """A personalized opportunity recommendation"""
    opportunity: Dict
    match_score: MatchScore
    personalized_insights: List[str]
    action_items: List[str]
    next_steps: List[str]


class PersonalizationEngine:
    """
    Personalizes opportunity recommendations based on user's
    credit profile, business type, and risk tolerance
    """

    def __init__(self, credit_profile: CreditProfile, rag_db_path: Path):
        """
        Initialize personalization engine

        Args:
            credit_profile: User's business credit profile
            rag_db_path: Path to ChromaDB business opportunities database
        """
        self.credit_profile = credit_profile
        self.rag_db_path = rag_db_path
        self.scorer = CreditScorer()

    def get_personalized_recommendations(
        self,
        query: str,
        n_results: int = 10
    ) -> List[PersonalizedRecommendation]:
        """
        Get personalized opportunity recommendations

        Args:
            query: User's search query
            n_results: Number of results to return

        Returns:
            List of PersonalizedRecommendation objects, sorted by match score
        """

        # Step 1: Query RAG database (semantic search)
        opportunities = self._query_rag(query, n_results * 2)  # Get more, then filter

        if not opportunities:
            return []

        # Step 2: Score opportunities based on credit profile
        scored_opportunities = self.scorer.batch_score_opportunities(
            self.credit_profile,
            opportunities
        )

        # Step 3: Filter by minimum score and take top N
        min_score = 40  # Only show opportunities with 40+ match score
        filtered = [(opp, score) for opp, score in scored_opportunities if score.total_score >= min_score]
        top_opportunities = filtered[:n_results]

        # Step 4: Generate personalized insights
        recommendations = []
        for opportunity, match_score in top_opportunities:
            recommendation = self._create_recommendation(opportunity, match_score)
            recommendations.append(recommendation)

        return recommendations

    def _query_rag(self, query: str, n_results: int) -> List[Dict]:
        """Query the business opportunities RAG database"""

        try:
            client = chromadb.PersistentClient(path=str(self.rag_db_path))
            collection = client.get_collection("business_opportunities")

            # Enhance query based on credit profile
            enhanced_query = self._enhance_query(query)

            results = collection.query(
                query_texts=[enhanced_query],
                n_results=n_results
            )

            # Convert to list of opportunity dicts
            opportunities = []
            for metadata in results['metadatas'][0]:
                opportunities.append(metadata)

            return opportunities

        except Exception as e:
            print(f"Error querying RAG: {e}")
            return []

    def _enhance_query(self, query: str) -> str:
        """Enhance search query based on credit profile"""

        enhancements = []

        # Add risk level preference
        if self.credit_profile.risk_profile:
            if self.credit_profile.risk_profile == RiskProfile.CONSERVATIVE:
                enhancements.append("low risk proven stable")
            elif self.credit_profile.risk_profile == RiskProfile.AGGRESSIVE:
                enhancements.append("high growth scalable")
            else:
                enhancements.append("moderate risk balanced")

        # Add investment range
        max_inv = self.credit_profile.max_investment_recommendation
        if max_inv < 1000:
            enhancements.append("low cost under $1000")
        elif max_inv < 5000:
            enhancements.append("affordable under $5000")
        else:
            enhancements.append("scalable investment")

        # Add business type considerations
        if self.credit_profile.business_type == BusinessType.NON_PROFIT:
            enhancements.append("social impact community")
        elif self.credit_profile.business_type == BusinessType.C_CORP:
            enhancements.append("corporate scalable enterprise")

        # Combine original query with enhancements
        enhanced = f"{query} {' '.join(enhancements)}"
        return enhanced

    def _create_recommendation(
        self,
        opportunity: Dict,
        match_score: MatchScore
    ) -> PersonalizedRecommendation:
        """Create personalized recommendation with insights and action items"""

        # Generate personalized insights
        insights = self._generate_insights(opportunity, match_score)

        # Generate action items
        action_items = self._generate_action_items(opportunity, match_score)

        # Generate next steps
        next_steps = self._generate_next_steps(opportunity, match_score)

        return PersonalizedRecommendation(
            opportunity=opportunity,
            match_score=match_score,
            personalized_insights=insights,
            action_items=action_items,
            next_steps=next_steps
        )

    def _generate_insights(
        self,
        opportunity: Dict,
        match_score: MatchScore
    ) -> List[str]:
        """Generate personalized insights"""

        insights = []
        profile = self.credit_profile

        # Investment capacity insight
        investment = opportunity.get('initial_investment', '$500')
        max_invest = profile.max_investment_recommendation
        insights.append(
            f"Your credit profile supports up to ${max_invest:,.0f} investment. "
            f"This opportunity requires {investment}."
        )

        # Risk profile insight
        if profile.risk_profile:
            risk_desc = {
                RiskProfile.CONSERVATIVE: "conservative approach with proven models",
                RiskProfile.MODERATE: "balanced approach with moderate risk",
                RiskProfile.AGGRESSIVE: "growth-oriented approach with higher risk tolerance"
            }
            insights.append(
                f"Your {risk_desc[profile.risk_profile]} aligns with this opportunity."
            )

        # Business type insight
        if profile.business_type == BusinessType.C_CORP:
            insights.append(
                "As a C-Corp, you have maximum flexibility for this opportunity type."
            )
        elif profile.business_type == BusinessType.NON_PROFIT:
            insights.append(
                "As a non-profit, ensure this aligns with your mission and IRS requirements."
            )

        # Credit availability insight
        if profile.available_credit > 0:
            insights.append(
                f"You have ${profile.available_credit:,.0f} in available credit if needed."
            )

        # Payment history insight
        if profile.payment_index and profile.payment_index >= 90:
            insights.append(
                "Your excellent payment history (100/100) positions you well for vendor terms."
            )

        return insights

    def _generate_action_items(
        self,
        opportunity: Dict,
        match_score: MatchScore
    ) -> List[str]:
        """Generate actionable next steps"""

        actions = []
        profile = self.credit_profile

        # Based on match score
        if match_score.total_score >= 80:
            actions.append("Strong match - prioritize detailed evaluation")
            actions.append("Request case studies or customer testimonials")
        elif match_score.total_score >= 60:
            actions.append("Good match - conduct thorough due diligence")
            actions.append("Compare with similar opportunities")
        else:
            actions.append("Moderate match - evaluate carefully against alternatives")

        # Based on affordability
        if match_score.affordability_score < 60:
            actions.append("Consider phased investment approach to reduce risk")
            actions.append("Look for partnership opportunities to share costs")

        # Based on business type
        if profile.business_type == BusinessType.NON_PROFIT:
            actions.append("Consult with legal counsel on compliance")
            actions.append("Ensure revenue model aligns with 501(c)(3) status")

        # Based on credit needs
        investment_str = opportunity.get('initial_investment', '$0')
        try:
            investment = float(investment_str.replace('$', '').replace(',', ''))
            if investment > 1000 and profile.available_credit < investment:
                actions.append("Secure additional credit line before proceeding")
        except:
            pass

        # Technical considerations
        tech_stack = opportunity.get('tech_stack', '')
        if 'API' in tech_stack or 'GPT' in tech_stack:
            actions.append("Review API pricing and usage limits")
            actions.append("Calculate ongoing API costs vs revenue projections")

        return actions

    def _generate_next_steps(
        self,
        opportunity: Dict,
        match_score: MatchScore
    ) -> List[str]:
        """Generate concrete next steps"""

        steps = []

        # Immediate steps
        steps.append("Research the market size and competition")
        steps.append("Create detailed financial projection (12-month)")

        # Technical steps
        automation_score = opportunity.get('automation_score', 0)
        if automation_score >= 70:
            steps.append("Map automation workflow and required integrations")
        else:
            steps.append("Identify manual processes that could be automated")

        # Financial steps
        if match_score.affordability_score < 80:
            steps.append("Develop contingency budget (+20% buffer)")

        steps.append("Set up separate business account for this venture")

        # Timeline steps
        time_to_market = opportunity.get('time_to_market', '')
        if 'week' in time_to_market.lower():
            steps.append("Create detailed weekly project timeline")
        else:
            steps.append("Create phased development timeline with milestones")

        # Validation steps
        steps.append("Build MVP or prototype for market validation")
        steps.append("Conduct customer interviews (minimum 10)")

        return steps

    def generate_portfolio_advice(self) -> Dict:
        """Generate overall portfolio advice based on credit profile"""

        profile = self.credit_profile
        advice = {
            'profile_summary': {},
            'recommended_strategy': {},
            'focus_areas': [],
            'warnings': [],
            'opportunities': []
        }

        # Profile summary
        advice['profile_summary'] = {
            'business_name': profile.business_name,
            'business_type': profile.business_type.value,
            'risk_profile': profile.risk_profile.value if profile.risk_profile else 'unknown',
            'max_investment': profile.max_investment_recommendation,
            'available_credit': profile.available_credit,
            'credit_score': profile.credit_score,
            'payment_index': profile.payment_index
        }

        # Recommended strategy based on risk profile
        if profile.risk_profile == RiskProfile.CONSERVATIVE:
            advice['recommended_strategy'] = {
                'approach': 'Low-risk, proven business models',
                'investment_range': f'$100 - ${profile.max_investment_recommendation:,.0f}',
                'focus': 'Automation and passive income',
                'timeline': 'Quick wins (0-3 months to revenue)',
                'diversification': 'Multiple small bets rather than one large investment'
            }
            advice['focus_areas'] = [
                'Proven digital products with existing market',
                'High-automation opportunities (80+ automation score)',
                'Low initial investment (<$500)',
                'Fast time-to-revenue (under 2 months)'
            ]

        elif profile.risk_profile == RiskProfile.MODERATE:
            advice['recommended_strategy'] = {
                'approach': 'Balanced growth with managed risk',
                'investment_range': f'$500 - ${profile.max_investment_recommendation:,.0f}',
                'focus': 'Scalable models with proven traction',
                'timeline': 'Medium-term growth (3-6 months)',
                'diversification': 'Mix of quick wins and growth opportunities'
            }
            advice['focus_areas'] = [
                'SaaS and subscription models',
                'AI-powered automation tools',
                'Content and digital products',
                'Service businesses with automation potential'
            ]

        else:  # AGGRESSIVE
            advice['recommended_strategy'] = {
                'approach': 'High-growth, scalable opportunities',
                'investment_range': f'$1,000 - ${profile.max_investment_recommendation:,.0f}',
                'focus': 'Market leadership and rapid scaling',
                'timeline': 'Long-term growth (6-12 months)',
                'diversification': 'Concentrated bets on high-potential opportunities'
            }
            advice['focus_areas'] = [
                'Emerging markets and technologies',
                'Platform businesses with network effects',
                'High-margin SaaS products',
                'AI and automation infrastructure'
            ]

        # Warnings based on credit profile
        if profile.credit_score and profile.credit_score < 500:
            advice['warnings'].append(
                'Low credit score - focus on building credit while pursuing low-risk opportunities'
            )

        if profile.available_credit < 500:
            advice['warnings'].append(
                'Limited available credit - consider opportunities under $500 or seek funding'
            )

        if profile.total_tradelines < 3:
            advice['warnings'].append(
                'Limited credit history - establish more business credit accounts'
            )

        if profile.business_type == BusinessType.NON_PROFIT:
            advice['warnings'].append(
                'Non-profit status - ensure all opportunities align with mission and IRS rules'
            )

        return advice


if __name__ == "__main__":
    # Demo
    from .fico_parser import FICOParser

    print("Personalization Engine Demo")
    print("=" * 70)

    # Create credit profile
    isnbiz = FICOParser.create_isnbiz_profile()

    print(f"\nBusiness: {isnbiz.business_name}")
    print(f"Risk Profile: {isnbiz.risk_profile.value}")
    print(f"Max Investment: ${isnbiz.max_investment_recommendation:,.2f}")

    # Generate portfolio advice
    print("\n\n" + "=" * 70)
    print("PERSONALIZED PORTFOLIO STRATEGY")
    print("=" * 70)

    rag_path = Path(__file__).parent.parent / "data" / "chroma_db"
    engine = PersonalizationEngine(isnbiz, rag_path)
    advice = engine.generate_portfolio_advice()

    print(f"\n{advice['recommended_strategy']['approach']}")
    print(f"\nInvestment Range: {advice['recommended_strategy']['investment_range']}")
    print(f"Focus: {advice['recommended_strategy']['focus']}")
    print(f"Timeline: {advice['recommended_strategy']['timeline']}")
    print(f"\nRecommended Focus Areas:")
    for area in advice['focus_areas']:
        print(f"  • {area}")

    if advice['warnings']:
        print(f"\nImportant Considerations:")
        for warning in advice['warnings']:
            print(f"  ⚠️  {warning}")

    print("\n" + "=" * 70)
