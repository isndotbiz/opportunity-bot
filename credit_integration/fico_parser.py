#!/usr/bin/env python3
"""
FICO Credit Data Parser
Extracts and structures business credit data from Nav/Equifax reports
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from enum import Enum
from pathlib import Path


class BusinessType(Enum):
    """Business entity types"""
    C_CORP = "C-Corporation"
    S_CORP = "S-Corporation"
    LLC = "LLC"
    NON_PROFIT = "Non-Profit"
    SOLE_PROP = "Sole Proprietorship"


class RiskProfile(Enum):
    """Risk tolerance based on credit history"""
    CONSERVATIVE = "conservative"  # Low credit score or limited history
    MODERATE = "moderate"  # Average credit, some history
    AGGRESSIVE = "aggressive"  # Strong credit, substantial history


@dataclass
class CreditProfile:
    """Structured business credit profile"""

    # Business Identity
    business_name: str
    business_type: BusinessType
    equifax_id: Optional[str] = None
    years_in_business: Optional[int] = None

    # Credit Scores
    credit_score: Optional[int] = None  # Business Delinquency Score
    payment_index: Optional[int] = None  # 0-100

    # Credit Capacity
    total_credit_limit: float = 0.0
    total_balance: float = 0.0
    available_credit: float = 0.0

    # Payment History
    current_accounts: int = 0
    delinquent_accounts: int = 0
    total_tradelines: int = 0

    # Public Records
    bankruptcies: int = 0
    judgments: int = 0
    liens: int = 0

    # Calculated Fields
    risk_profile: Optional[RiskProfile] = None
    max_investment_recommendation: float = 0.0

    def calculate_risk_profile(self) -> RiskProfile:
        """Calculate risk tolerance based on credit data"""

        # Conservative if:
        # - Credit score < 500
        # - Payment index < 70
        # - Any public records
        # - Limited tradeline history

        if self.credit_score and self.credit_score < 500:
            return RiskProfile.CONSERVATIVE

        if self.payment_index and self.payment_index < 70:
            return RiskProfile.CONSERVATIVE

        if self.bankruptcies > 0 or self.judgments > 0 or self.liens > 0:
            return RiskProfile.CONSERVATIVE

        if self.total_tradelines < 3:
            return RiskProfile.CONSERVATIVE

        # Aggressive if:
        # - Credit score >= 700
        # - Payment index >= 90
        # - Multiple tradelines
        # - Significant available credit

        if (self.credit_score and self.credit_score >= 700 and
            self.payment_index and self.payment_index >= 90 and
            self.total_tradelines >= 5 and
            self.available_credit >= 10000):
            return RiskProfile.AGGRESSIVE

        # Default to moderate
        return RiskProfile.MODERATE

    def calculate_max_investment(self) -> float:
        """Calculate recommended maximum investment based on credit profile"""

        # Base calculation on available credit and risk profile
        base_amount = self.available_credit * 0.3  # 30% of available credit

        # Adjust for risk profile
        if self.risk_profile == RiskProfile.CONSERVATIVE:
            multiplier = 0.5  # Conservative: 50% of base
        elif self.risk_profile == RiskProfile.AGGRESSIVE:
            multiplier = 2.0  # Aggressive: 200% of base
        else:
            multiplier = 1.0  # Moderate: 100% of base

        # Adjust for payment history
        if self.payment_index:
            payment_multiplier = self.payment_index / 100.0
        else:
            payment_multiplier = 0.7  # Default moderate

        max_investment = base_amount * multiplier * payment_multiplier

        # Floor and ceiling
        max_investment = max(100, max_investment)  # Minimum $100
        max_investment = min(50000, max_investment)  # Maximum $50K

        return round(max_investment, 2)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['business_type'] = self.business_type.value
        if self.risk_profile:
            data['risk_profile'] = self.risk_profile.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'CreditProfile':
        """Create from dictionary"""
        data['business_type'] = BusinessType(data['business_type'])
        if data.get('risk_profile'):
            data['risk_profile'] = RiskProfile(data['risk_profile'])
        return cls(**data)


class FICOParser:
    """Parse FICO/Nav credit reports and extract structured data"""

    @staticmethod
    def parse_equifax_report(report_data: Dict) -> CreditProfile:
        """
        Parse Equifax business credit report

        Args:
            report_data: Dictionary containing parsed PDF data or manual input

        Returns:
            CreditProfile object
        """

        profile = CreditProfile(
            business_name=report_data.get('business_name', 'Unknown'),
            business_type=BusinessType.C_CORP,  # Default, override as needed
            equifax_id=report_data.get('equifax_id'),
            years_in_business=report_data.get('years_in_business'),
            credit_score=report_data.get('credit_score'),
            payment_index=report_data.get('payment_index'),
            total_tradelines=report_data.get('total_tradelines', 0),
            current_accounts=report_data.get('current_accounts', 0),
            delinquent_accounts=report_data.get('delinquent_accounts', 0),
            bankruptcies=report_data.get('bankruptcies', 0),
            judgments=report_data.get('judgments', 0),
            liens=report_data.get('liens', 0)
        )

        # Calculate credit capacity from tradelines
        tradelines = report_data.get('tradelines', [])
        total_credit = sum(t.get('credit_limit', 0) for t in tradelines)
        total_balance = sum(t.get('balance', 0) for t in tradelines)

        profile.total_credit_limit = total_credit
        profile.total_balance = total_balance
        profile.available_credit = total_credit - total_balance

        # Calculate derived fields
        profile.risk_profile = profile.calculate_risk_profile()
        profile.max_investment_recommendation = profile.calculate_max_investment()

        return profile

    @staticmethod
    def create_isnbiz_profile() -> CreditProfile:
        """Create credit profile for ISNBIZ based on Equifax report"""

        report_data = {
            'business_name': 'ISNBIZ, INCORPORATED',
            'equifax_id': '722429197',
            'years_in_business': 11,
            'credit_score': 372,  # Business Delinquency Score
            'payment_index': 100,  # Excellent payment history
            'total_tradelines': 2,
            'current_accounts': 2,
            'delinquent_accounts': 0,
            'bankruptcies': 0,
            'judgments': 0,
            'liens': 0,
            'tradelines': [
                {'credit_limit': 82, 'balance': 82},
                {'credit_limit': 55, 'balance': 55}
            ]
        }

        profile = FICOParser.parse_equifax_report(report_data)
        profile.business_type = BusinessType.C_CORP

        return profile

    @staticmethod
    def create_hroc_profile() -> CreditProfile:
        """Create credit profile for HROC (Non-Profit)"""

        # Placeholder - update with actual HROC data when available
        profile = CreditProfile(
            business_name='HROC',
            business_type=BusinessType.NON_PROFIT,
            years_in_business=5,
            credit_score=None,  # Non-profits may not have traditional scores
            payment_index=None,
            total_tradelines=0,
            current_accounts=0,
            delinquent_accounts=0,
            bankruptcies=0,
            judgments=0,
            liens=0
        )

        # Non-profits have different risk profiles
        profile.risk_profile = RiskProfile.CONSERVATIVE
        profile.max_investment_recommendation = 500.0  # Conservative for non-profits

        return profile

    @staticmethod
    def save_profile(profile: CreditProfile, filepath: Path):
        """Save credit profile to JSON"""
        with open(filepath, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)

    @staticmethod
    def load_profile(filepath: Path) -> CreditProfile:
        """Load credit profile from JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return CreditProfile.from_dict(data)


if __name__ == "__main__":
    # Demo: Create and display ISNBIZ profile
    print("Creating ISNBIZ Credit Profile...")
    print("=" * 70)

    isnbiz = FICOParser.create_isnbiz_profile()

    print(f"\nBusiness: {isnbiz.business_name}")
    print(f"Type: {isnbiz.business_type.value}")
    print(f"Years in Business: {isnbiz.years_in_business}")
    print(f"\nCredit Metrics:")
    print(f"  - Business Delinquency Score: {isnbiz.credit_score}")
    print(f"  - Payment Index: {isnbiz.payment_index}/100")
    print(f"  - Active Tradelines: {isnbiz.total_tradelines}")
    print(f"\nCredit Capacity:")
    print(f"  - Total Credit Limit: ${isnbiz.total_credit_limit:,.2f}")
    print(f"  - Current Balance: ${isnbiz.total_balance:,.2f}")
    print(f"  - Available Credit: ${isnbiz.available_credit:,.2f}")
    print(f"\nRisk Assessment:")
    print(f"  - Risk Profile: {isnbiz.risk_profile.value.upper()}")
    print(f"  - Max Recommended Investment: ${isnbiz.max_investment_recommendation:,.2f}")
    print(f"\nPublic Records: {isnbiz.bankruptcies + isnbiz.judgments + isnbiz.liens} (Clean)")

    print("\n" + "=" * 70)

    # Save profile
    output_dir = Path(__file__).parent / "profiles"
    output_dir.mkdir(exist_ok=True)

    FICOParser.save_profile(isnbiz, output_dir / "isnbiz_profile.json")
    print(f"\n✅ Profile saved to: {output_dir / 'isnbiz_profile.json'}")
