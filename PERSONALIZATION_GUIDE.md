# FICO-Based Personalization Guide

## Overview

The Opportunity Research Bot now includes **advanced personalization** based on your business credit profile. It integrates FICO scores, Nav business credit data, and risk tolerance to provide tailored recommendations.

---

## 🎯 Key Features

### 1. **Credit Profile Integration**
- **FICO Business Delinquency Score** - Credit scoring (0-1000 scale)
- **Nav Payment Index** - Payment history (0-100 scale)
- **Credit Capacity Analysis** - Available credit and limits
- **Business Type Recognition** - C-Corp vs Non-Profit considerations

### 2. **Smart Opportunity Matching**
- **Affordability Scoring** - Matches investment to your capacity
- **Risk Alignment** - Matches opportunity risk to your tolerance
- **Business Type Filtering** - Ensures compliance (e.g., non-profit restrictions)
- **Timeline Matching** - Aligns time-to-revenue with your profile

### 3. **Personalized Recommendations**
- **Match Scores** (0-100) - How well opportunities fit your profile
- **Personalized Insights** - Tailored analysis based on your credit
- **Action Items** - Specific next steps for your situation
- **Portfolio Strategy** - Overall investment approach

---

## 📊 Your Credit Profile

### ISNBIZ, Inc (C-Corp)
```
Business: ISNBIZ, INCORPORATED
Type: C-Corporation
Years in Business: 11

Credit Metrics:
  • Business Delinquency Score: 372
  • Payment Index: 100/100
  • Active Tradelines: 2

Financial Capacity:
  • Total Credit Limit: $137.00
  • Available Credit: $0.00
  • Max Recommended Investment: $100.00

Risk Profile: CONSERVATIVE
```

**Analysis:**
- **Excellent payment history** (100/100) - Great for vendor terms
- **Low credit score** (372) - Indicates limited credit history
- **Minimal available credit** - Focus on low-cost opportunities
- **Conservative risk profile** - Prioritize proven models

### HROC (Non-Profit)
```
Business: HROC
Type: Non-Profit
Max Recommended Investment: $500.00
Risk Profile: CONSERVATIVE
```

**Special Considerations:**
- Must align with 501(c)(3) mission
- Revenue limits may apply
- Focus on social impact opportunities

---

## 🚀 Quick Start

### 1. Setup
```bash
./setup_personalization.sh
```

### 2. Populate Database
```bash
python3 demo_opportunity_pipeline.py
```

### 3. Search with Personalization
```bash
# For ISNBIZ (C-Corp)
python3 query_personalized.py "AI automation opportunities" isnbiz

# For HROC (Non-Profit)
python3 query_personalized.py "social impact opportunities" hroc
```

### 4. Interactive Mode
```bash
python3 personalized_opportunity_bot.py isnbiz
```

---

## 💡 Usage Examples

### Example 1: Basic Search
```bash
python3 query_personalized.py "passive income under $500"
```

**Output:**
```
PERSONALIZED RECOMMENDATIONS (3 matches)

#1. AI-Powered Content Repurposing Tool
────────────────────────────────────────────────────────────
🟢 MATCH SCORE: 85/100 - HIGHLY RECOMMENDED

📊 Opportunity Metrics:
   • Initial Investment: $500
   • Revenue Claim: $3000/month
   • Time to Market: 2 weeks
   • Automation Score: 85/100

📈 Score Breakdown:
   • Affordability: 40/100
   • Risk Match: 100/100
   • Business Fit: 100/100
   • Timeline: 100/100

💡 Personalized Insights:
   • Your credit profile supports up to $100 investment. This requires $500.
   • Your conservative approach with proven models aligns well.
   • As a C-Corp, you have maximum flexibility.

✅ Action Items:
   • Consider phased investment approach
   • Request case studies
   • Review API pricing and usage limits
```

### Example 2: Portfolio Strategy
```bash
python3 personalized_opportunity_bot.py isnbiz
# Type 'advice' when prompted
```

**Output:**
```
PERSONALIZED PORTFOLIO STRATEGY

🎯 Strategy: Low-risk, proven business models

💰 Investment Range: $100 - $100.00
🎪 Focus: Automation and passive income
⏱️  Timeline: Quick wins (0-3 months to revenue)
🎲 Diversification: Multiple small bets

🔍 Recommended Focus Areas:
   • Proven digital products with existing market
   • High-automation opportunities (80+ automation score)
   • Low initial investment (<$500)
   • Fast time-to-revenue (under 2 months)

⚠️  Important Considerations:
   • Low credit score - focus on building credit
   • Limited available credit - consider opportunities under $500
   • Limited credit history - establish more accounts
```

### Example 3: Compare Entities
```bash
# ISNBIZ recommendations
python3 query_personalized.py "SaaS opportunities" isnbiz

# HROC recommendations
python3 query_personalized.py "SaaS opportunities" hroc
```

**Key Differences:**
- **ISNBIZ**: Full commercial flexibility, higher investment capacity
- **HROC**: Mission-aligned only, conservative investments

---

## 🎲 Understanding Match Scores

### Score Components

#### 1. Affordability Score (40% weight)
- **100%**: Opportunity uses <25% of max investment
- **85%**: Uses 25-50% of max investment
- **65%**: Uses 50-75% of max investment
- **40%**: Uses 75-100% of max investment
- **0%**: Exceeds max investment

#### 2. Risk Match Score (25% weight)
- **Conservative Profile**:
  - Low risk = 100 points
  - Medium risk = 50 points
  - High risk = 20 points

- **Moderate Profile**:
  - Low risk = 90 points
  - Medium risk = 100 points
  - High risk = 60 points

- **Aggressive Profile**:
  - Low risk = 70 points
  - Medium risk = 90 points
  - High risk = 100 points

#### 3. Business Type Score (20% weight)
- **C-Corp**: 100 points (maximum flexibility)
- **Non-Profit**: 90 points if low revenue, 40 if high
- **S-Corp/LLC**: 95 points
- **Sole Prop**: 60-85 points depending on credit needs

#### 4. Timeline Score (15% weight)
- **Conservative**: Prefers <3 months to revenue
- **Moderate**: Comfortable with 6-12 months
- **Aggressive**: Can wait 12-24+ months for bigger returns

### Recommendation Levels

| Score | Level | Meaning |
|-------|-------|---------|
| 80-100 | 🟢 Highly Recommended | Strong fit across all dimensions |
| 60-79 | 🟡 Recommended | Good fit, minor considerations |
| 40-59 | 🟠 Consider | Evaluate carefully, some risks |
| 0-39 | 🔴 Not Recommended | Poor fit for your profile |

---

## 🔧 Advanced Usage

### Create Custom Credit Profile

```python
from credit_integration import CreditProfile, BusinessType, FICOParser

# Create custom profile
custom_profile = CreditProfile(
    business_name="My Business",
    business_type=BusinessType.LLC,
    years_in_business=3,
    credit_score=650,
    payment_index=85,
    total_tradelines=5,
    total_credit_limit=10000,
    total_balance=3000
)

# Calculate derived metrics
custom_profile.risk_profile = custom_profile.calculate_risk_profile()
custom_profile.max_investment_recommendation = custom_profile.calculate_max_investment()

# Save for reuse
FICOParser.save_profile(custom_profile, "profiles/my_business.json")
```

### Batch Scoring

```python
from credit_integration import PersonalizationEngine, FICOParser
from pathlib import Path

# Load profile
profile = FICOParser.create_isnbiz_profile()

# Initialize engine
engine = PersonalizationEngine(profile, Path("data/chroma_db"))

# Get recommendations
recs = engine.get_personalized_recommendations(
    query="AI automation",
    n_results=10
)

# Print top 5
for i, rec in enumerate(recs[:5], 1):
    print(f"{i}. {rec.opportunity['title']}")
    print(f"   Score: {rec.match_score.total_score}/100")
```

---

## 📈 Improving Your Profile

### For ISNBIZ (Conservative → Moderate)

**Current Situation:**
- Score: 372 (Low)
- Available Credit: $0
- Max Investment: $100

**Action Plan:**
1. **Build Credit History**
   - Add 3-5 vendor accounts (net-30 terms)
   - Use business credit cards with small purchases
   - Pay everything on time (maintain 100 payment index)

2. **Increase Credit Limits**
   - Request increases every 6 months
   - Show consistent revenue growth
   - Target: $5,000-$10,000 available credit

3. **Timeline**
   - 6 months: Moderate profile (~$1,000 max investment)
   - 12 months: Aggressive profile (~$5,000 max investment)

### For HROC (Non-Profit)

**Focus Areas:**
1. **Mission-Aligned Opportunities**
   - Social enterprise models
   - Grant-funded ventures
   - Community benefit programs

2. **Conservative Growth**
   - Keep investments <$500
   - Focus on sustainable impact
   - Document mission alignment

---

## 🎯 Recommended Strategies by Profile

### Conservative Profile (ISNBIZ Current)

**Best Opportunities:**
- Digital products (<$100 investment)
- High-automation tools (80+ score)
- Proven marketplaces (Gumroad, etc.)
- Quick wins (<2 months to revenue)

**Avoid:**
- High-risk ventures
- Large upfront investments
- Unproven markets
- Long development timelines

**Sample Search:**
```bash
python3 query_personalized.py "proven passive income under $100"
python3 query_personalized.py "automated digital products"
python3 query_personalized.py "Gumroad template business"
```

### Moderate Profile (Target: 6-12 months)

**Best Opportunities:**
- SaaS with MRR potential
- Content businesses with subscriptions
- Chrome extensions (one-time dev, recurring revenue)
- Marketplace arbitrage

**Sample Search:**
```bash
python3 query_personalized.py "SaaS subscription under $2000"
python3 query_personalized.py "content automation MRR"
```

### Aggressive Profile (Target: 12+ months)

**Best Opportunities:**
- Platform businesses
- API services
- High-margin software
- Network effect products

**Sample Search:**
```bash
python3 query_personalized.py "platform marketplace scalable"
python3 query_personalized.py "API business high margin"
```

---

## 🔐 Data Privacy & Security

### What's Stored
- Credit scores and metrics
- Business type and details
- Risk profile calculations
- Opportunity match scores

### What's NOT Stored
- Personal SSN or EIN
- Bank account details
- Full credit reports
- Personal financial data

### Data Location
```
credit_integration/profiles/
  ├── isnbiz_profile.json      # ISNBIZ credit profile
  └── hroc_profile.json         # HROC credit profile
```

### Updating Credit Data
```bash
# Manually edit JSON or recreate profile
python3 -c "from credit_integration import FICOParser; \
    profile = FICOParser.create_isnbiz_profile(); \
    # Update fields as needed \
    profile.credit_score = 500; \
    FICOParser.save_profile(profile, 'credit_integration/profiles/isnbiz_profile.json')"
```

---

## 🐛 Troubleshooting

### Error: "No opportunities found"
**Solution:**
```bash
# Populate database first
python3 demo_opportunity_pipeline.py
```

### Error: "Profile not found"
**Solution:**
```bash
# Regenerate profiles
python3 credit_integration/fico_parser.py
```

### Low match scores across all opportunities
**Cause:** Your credit profile may be too conservative for current database

**Solution:**
1. Lower minimum score threshold in code
2. Add more low-investment opportunities to database
3. Update credit profile with more capacity

---

## 📚 API Reference

### Classes

#### `CreditProfile`
Represents business credit profile

**Key Fields:**
- `business_name: str`
- `business_type: BusinessType`
- `credit_score: int`
- `payment_index: int`
- `max_investment_recommendation: float`
- `risk_profile: RiskProfile`

#### `PersonalizationEngine`
Main personalization engine

**Methods:**
- `get_personalized_recommendations(query, n_results)` → List[PersonalizedRecommendation]
- `generate_portfolio_advice()` → Dict

#### `CreditScorer`
Scores opportunities against credit profile

**Methods:**
- `score_opportunity(profile, requirements)` → MatchScore
- `batch_score_opportunities(profile, opportunities)` → List[tuple]

---

## 🎓 Learning Resources

### Understanding Business Credit
- [Nav Guide to Business Credit](https://www.nav.com/business-credit-scores/)
- [Equifax Business Credit Reports](https://www.equifax.com/business/)
- [Build Business Credit Guide](https://www.sba.gov/business-guide/manage-your-business/establish-business-credit)

### Risk Management
- [Business Risk Assessment](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs)
- [Investment Strategies for Small Business](https://www.forbes.com/advisor/business/small-business-investment-strategies/)

---

## 🆘 Support

### Common Questions

**Q: Can I use this with multiple businesses?**
A: Yes! Create separate profiles for each entity:
```bash
python3 query_personalized.py "query" isnbiz
python3 query_personalized.py "query" hroc
```

**Q: How often should I update my credit profile?**
A: Update quarterly or whenever you have major credit changes (new tradelines, score changes, credit limit increases).

**Q: Can I adjust the scoring weights?**
A: Yes! Edit `credit_integration/credit_scorer.py` line ~65:
```python
total_score = (
    affordability_score * 0.40 +      # Adjust these weights
    risk_match_score * 0.25 +
    business_type_score * 0.20 +
    timeline_score * 0.15
)
```

**Q: What if my credit score improves?**
A: Update your profile JSON or regenerate it with new data.

---

## 🚀 Next Steps

1. **Run Setup**
   ```bash
   ./setup_personalization.sh
   ```

2. **Generate Test Data**
   ```bash
   python3 demo_opportunity_pipeline.py
   ```

3. **Try Personalized Search**
   ```bash
   python3 query_personalized.py "your search query"
   ```

4. **Review Portfolio Strategy**
   ```bash
   python3 personalized_opportunity_bot.py
   # Type 'advice'
   ```

5. **Monitor & Iterate**
   - Track opportunities you pursue
   - Update credit profile as you build history
   - Adjust search queries based on results

---

**Happy hunting! 🎯**
