#!/usr/bin/env python3
"""
Credit-Based Scoring System
Scores opportunities based on user's financial capacity and risk profile
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from .fico_parser import CreditProfile, RiskProfile, BusinessType


@dataclass
class OpportunityRequirements:
    """Financial requirements for a business opportunity"""
    min_investment: float
    max_investment: float
    expected_revenue: float
    time_to_revenue_months: int
    risk_level: str  # 'low', 'medium', 'high'
    requires_credit: bool = False
    automation_score: int = 0
    legitimacy_score: int = 0


@dataclass
class MatchScore:
    """Scored match between credit profile and opportunity"""
    total_score: float  # 0-100
    affordability_score: float  # Can they afford it?
    risk_match_score: float  # Does risk level match tolerance?
    business_type_score: float  # Is it suitable for their entity type?
    timeline_score: float  # Can they wait for returns?
    recommendation: str  # 'highly_recommended', 'recommended', 'consider', 'not_recommended'
    reasoning: List[str]  # Why this score?


class CreditScorer:
    """Score opportunities based on credit profile"""

    @staticmethod
    def score_opportunity(
        credit_profile: CreditProfile,
        opportunity_req: OpportunityRequirements
    ) -> MatchScore:
        """
        Score how well an opportunity matches a credit profile

        Args:
            credit_profile: User's business credit profile
            opportunity_req: Opportunity's financial requirements

        Returns:
            MatchScore with detailed breakdown
        """

        reasoning = []

        # 1. Affordability Score (0-100)
        affordability_score = CreditScorer._score_affordability(
            credit_profile, opportunity_req, reasoning
        )

        # 2. Risk Match Score (0-100)
        risk_match_score = CreditScorer._score_risk_match(
            credit_profile, opportunity_req, reasoning
        )

        # 3. Business Type Score (0-100)
        business_type_score = CreditScorer._score_business_type(
            credit_profile, opportunity_req, reasoning
        )

        # 4. Timeline Score (0-100)
        timeline_score = CreditScorer._score_timeline(
            credit_profile, opportunity_req, reasoning
        )

        # Calculate weighted total score
        total_score = (
            affordability_score * 0.40 +      # 40% weight - most important
            risk_match_score * 0.25 +         # 25% weight
            business_type_score * 0.20 +      # 20% weight
            timeline_score * 0.15             # 15% weight
        )

        # Determine recommendation level
        if total_score >= 80:
            recommendation = 'highly_recommended'
        elif total_score >= 60:
            recommendation = 'recommended'
        elif total_score >= 40:
            recommendation = 'consider'
        else:
            recommendation = 'not_recommended'

        return MatchScore(
            total_score=round(total_score, 2),
            affordability_score=affordability_score,
            risk_match_score=risk_match_score,
            business_type_score=business_type_score,
            timeline_score=timeline_score,
            recommendation=recommendation,
            reasoning=reasoning
        )

    @staticmethod
    def _score_affordability(
        credit_profile: CreditProfile,
        opportunity_req: OpportunityRequirements,
        reasoning: List[str]
    ) -> float:
        """Score based on financial capacity"""

        max_investment = credit_profile.max_investment_recommendation
        opp_investment = opportunity_req.min_investment

        if opp_investment > max_investment:
            reasoning.append(
                f"Investment required (${opp_investment:,.0f}) exceeds "
                f"recommended maximum (${max_investment:,.0f})"
            )
            return 0.0

        # Score based on percentage of max investment
        percentage_used = (opp_investment / max_investment) * 100 if max_investment > 0 else 100

        if percentage_used <= 25:
            score = 100
            reasoning.append(
                f"Excellent fit: only {percentage_used:.0f}% of recommended maximum"
            )
        elif percentage_used <= 50:
            score = 85
            reasoning.append(
                f"Good fit: {percentage_used:.0f}% of recommended maximum"
            )
        elif percentage_used <= 75:
            score = 65
            reasoning.append(
                f"Moderate fit: {percentage_used:.0f}% of recommended maximum"
            )
        else:
            score = 40
            reasoning.append(
                f"Tight fit: {percentage_used:.0f}% of recommended maximum"
            )

        # Bonus for available credit
        if credit_profile.available_credit >= opp_investment * 2:
            score = min(100, score + 10)
            reasoning.append("Bonus: Significant credit buffer available")

        return score

    @staticmethod
    def _score_risk_match(
        credit_profile: CreditProfile,
        opportunity_req: OpportunityRequirements,
        reasoning: List[str]
    ) -> float:
        """Score based on risk profile alignment"""

        if not credit_profile.risk_profile:
            return 50.0  # Neutral if unknown

        opp_risk = opportunity_req.risk_level.lower()
        profile_risk = credit_profile.risk_profile

        # Conservative profile
        if profile_risk == RiskProfile.CONSERVATIVE:
            if opp_risk == 'low':
                score = 100
                reasoning.append("Perfect match: Low-risk opportunity for conservative profile")
            elif opp_risk == 'medium':
                score = 50
                reasoning.append("Moderate risk - consider carefully with conservative profile")
            else:  # high
                score = 20
                reasoning.append("Caution: High-risk opportunity not ideal for conservative profile")

        # Moderate profile
        elif profile_risk == RiskProfile.MODERATE:
            if opp_risk == 'low':
                score = 90
                reasoning.append("Good match: Low-risk opportunity")
            elif opp_risk == 'medium':
                score = 100
                reasoning.append("Perfect match: Medium-risk opportunity for moderate profile")
            else:  # high
                score = 60
                reasoning.append("Higher risk - evaluate potential returns carefully")

        # Aggressive profile
        else:  # AGGRESSIVE
            if opp_risk == 'low':
                score = 70
                reasoning.append("Safe choice, but may be below growth potential")
            elif opp_risk == 'medium':
                score = 90
                reasoning.append("Good match: Medium-risk with growth potential")
            else:  # high
                score = 100
                reasoning.append("Perfect match: High-risk/high-reward for aggressive profile")

        # Adjust for legitimacy score
        if opportunity_req.legitimacy_score < 60:
            score *= 0.5
            reasoning.append(f"Caution: Lower legitimacy score ({opportunity_req.legitimacy_score}/100)")

        return score

    @staticmethod
    def _score_business_type(
        credit_profile: CreditProfile,
        opportunity_req: OpportunityRequirements,
        reasoning: List[str]
    ) -> float:
        """Score based on business type compatibility"""

        biz_type = credit_profile.business_type

        # Non-profits have restrictions
        if biz_type == BusinessType.NON_PROFIT:
            if opportunity_req.expected_revenue < 10000:
                score = 90
                reasoning.append("Suitable for non-profit: Limited commercial activity")
            else:
                score = 40
                reasoning.append("Caution: Substantial revenue may conflict with non-profit status")

        # C-Corps are flexible
        elif biz_type == BusinessType.C_CORP:
            score = 100
            reasoning.append("Excellent fit: C-Corp structure supports all business types")

        # S-Corps and LLCs are also flexible
        elif biz_type in [BusinessType.S_CORP, BusinessType.LLC]:
            score = 95
            reasoning.append(f"Great fit: {biz_type.value} structure is flexible")

        # Sole proprietors have different considerations
        else:  # SOLE_PROP
            if opportunity_req.requires_credit:
                score = 60
                reasoning.append("Note: Personal credit may be involved as sole proprietor")
            else:
                score = 85
                reasoning.append("Good fit: No business credit required")

        return score

    @staticmethod
    def _score_timeline(
        credit_profile: CreditProfile,
        opportunity_req: OpportunityRequirements,
        reasoning: List[str]
    ) -> float:
        """Score based on time to revenue vs risk tolerance"""

        months = opportunity_req.time_to_revenue_months

        if not credit_profile.risk_profile:
            return 50.0

        profile_risk = credit_profile.risk_profile

        # Conservative profiles prefer faster returns
        if profile_risk == RiskProfile.CONSERVATIVE:
            if months <= 3:
                score = 100
                reasoning.append("Quick returns: Ideal for conservative approach")
            elif months <= 6:
                score = 70
                reasoning.append("Moderate timeline acceptable")
            else:
                score = 40
                reasoning.append("Longer timeline - ensure cash flow stability")

        # Moderate profiles are flexible
        elif profile_risk == RiskProfile.MODERATE:
            if months <= 6:
                score = 100
                reasoning.append("Timeline is reasonable")
            elif months <= 12:
                score = 75
                reasoning.append("Acceptable timeline for moderate growth")
            else:
                score = 50
                reasoning.append("Longer timeline - plan for sustained investment")

        # Aggressive profiles can wait for bigger returns
        else:  # AGGRESSIVE
            if months <= 12:
                score = 100
                reasoning.append("Timeline is acceptable for growth opportunity")
            elif months <= 24:
                score = 85
                reasoning.append("Longer timeline acceptable with strong growth potential")
            else:
                score = 60
                reasoning.append("Extended timeline - ensure alignment with business goals")

        # Bonus for high automation (passive income)
        if opportunity_req.automation_score >= 80:
            score = min(100, score + 15)
            reasoning.append("Bonus: High automation reduces ongoing time commitment")

        return score

    @staticmethod
    def batch_score_opportunities(
        credit_profile: CreditProfile,
        opportunities: List[Dict]
    ) -> List[tuple]:
        """
        Score multiple opportunities and return sorted by match score

        Args:
            credit_profile: User's credit profile
            opportunities: List of opportunity dictionaries

        Returns:
            List of (opportunity, MatchScore) tuples, sorted by total_score descending
        """

        scored_opportunities = []

        for opp in opportunities:
            # Extract or estimate requirements
            requirements = CreditScorer._extract_requirements(opp)

            # Score the match
            match_score = CreditScorer.score_opportunity(credit_profile, requirements)

            scored_opportunities.append((opp, match_score))

        # Sort by total score (highest first)
        scored_opportunities.sort(key=lambda x: x[1].total_score, reverse=True)

        return scored_opportunities

    @staticmethod
    def _extract_requirements(opportunity: Dict) -> OpportunityRequirements:
        """Extract opportunity requirements from opportunity data"""

        # Parse investment from initial_investment field
        investment_str = opportunity.get('initial_investment', '$500')
        try:
            investment = float(investment_str.replace('$', '').replace(',', ''))
        except:
            investment = 500  # Default

        # Parse time to market
        time_str = opportunity.get('time_to_market', '1 month')
        if 'week' in time_str.lower():
            months = 1
        elif 'month' in time_str.lower():
            # Extract number
            try:
                months = int(''.join(filter(str.isdigit, time_str.split('-')[0])))
            except:
                months = 2
        else:
            months = 3

        # Determine risk level from scores
        automation = opportunity.get('automation_score', 50)
        legitimacy = opportunity.get('legitimacy_score', 50)

        if legitimacy >= 80 and automation >= 70:
            risk = 'low'
        elif legitimacy >= 60 and automation >= 50:
            risk = 'medium'
        else:
            risk = 'high'

        # Estimate revenue from revenue_claim
        revenue_str = opportunity.get('revenue_claim', '$1000/month')
        try:
            revenue = float(revenue_str.replace('$', '').replace('/month', '').replace(',', ''))
        except:
            revenue = 1000

        return OpportunityRequirements(
            min_investment=investment,
            max_investment=investment * 1.5,
            expected_revenue=revenue,
            time_to_revenue_months=months,
            risk_level=risk,
            requires_credit=investment > 1000,
            automation_score=automation,
            legitimacy_score=legitimacy
        )


if __name__ == "__main__":
    # Demo
    from .fico_parser import FICOParser

    print("Credit Scorer Demo")
    print("=" * 70)

    # Create sample credit profile
    isnbiz = FICOParser.create_isnbiz_profile()

    print(f"\nCredit Profile: {isnbiz.business_name}")
    print(f"Risk Profile: {isnbiz.risk_profile.value}")
    print(f"Max Investment: ${isnbiz.max_investment_recommendation:,.2f}")

    # Sample opportunity
    opportunity = {
        'title': 'AI Content Tool',
        'initial_investment': '$500',
        'time_to_market': '2 weeks',
        'automation_score': 85,
        'legitimacy_score': 80,
        'revenue_claim': '$3000/month'
    }

    requirements = CreditScorer._extract_requirements(opportunity)
    score = CreditScorer.score_opportunity(isnbiz, requirements)

    print(f"\n\nOpportunity: {opportunity['title']}")
    print(f"Investment: {opportunity['initial_investment']}")
    print(f"\nMatch Score: {score.total_score}/100")
    print(f"Recommendation: {score.recommendation.upper()}")
    print(f"\nScore Breakdown:")
    print(f"  - Affordability: {score.affordability_score}/100")
    print(f"  - Risk Match: {score.risk_match_score}/100")
    print(f"  - Business Type: {score.business_type_score}/100")
    print(f"  - Timeline: {score.timeline_score}/100")
    print(f"\nReasoning:")
    for reason in score.reasoning:
        print(f"  • {reason}")

    print("\n" + "=" * 70)
