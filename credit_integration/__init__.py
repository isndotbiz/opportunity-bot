"""
Credit Integration Module
Integrates FICO/Nav business credit data with opportunity matching
"""

from .fico_parser import (
    FICOParser,
    CreditProfile,
    BusinessType,
    RiskProfile
)
from .personalization_engine import (
    PersonalizationEngine,
    PersonalizedRecommendation
)
from .credit_scorer import (
    CreditScorer,
    OpportunityRequirements,
    MatchScore
)

__all__ = [
    'FICOParser',
    'CreditProfile',
    'BusinessType',
    'RiskProfile',
    'PersonalizationEngine',
    'PersonalizedRecommendation',
    'CreditScorer',
    'OpportunityRequirements',
    'MatchScore'
]
