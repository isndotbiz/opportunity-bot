# FICO-Based Personalization - Quick Start

## What's New

Your Opportunity Research Bot now has **intelligent personalization** based on your business credit profile!

### Key Features
- ✅ **FICO Credit Integration** - Uses your actual business credit data
- ✅ **Nav Business Credit** - Incorporates payment history and tradelines
- ✅ **Smart Matching** - Recommends opportunities you can actually afford
- ✅ **Risk Alignment** - Matches your risk tolerance
- ✅ **Business Type Filtering** - Respects C-Corp vs Non-Profit rules

---

## Quick Start (3 Steps)

### 1. Run Setup
```bash
./setup_personalization.sh
```

### 2. Populate Database
```bash
python3 demo_opportunity_pipeline.py
```

### 3. Search with Personalization
```bash
python3 query_personalized.py "AI automation opportunities"
```

That's it! You'll see opportunities ranked by how well they match your credit profile.

---

## Your Current Profile

### ISNBIZ, Inc (C-Corp)
```
Credit Score: 372 (Building history)
Payment Index: 100/100 (Excellent!)
Available Credit: $0
Max Recommended Investment: $100

Risk Profile: CONSERVATIVE
Strategy: Focus on proven, low-cost opportunities
```

**What this means:**
- ✅ Perfect payment history gives you credibility
- ⚠️ Limited credit means focus on <$100 opportunities
- 🎯 Best fit: Digital products, automation tools, templates

---

## Usage Examples

### Basic Search
```bash
python3 query_personalized.py "passive income"
```

**Output:**
```
#1. Digital Course Template
🟢 MATCH SCORE: 94/100 - HIGHLY RECOMMENDED

Investment: $50
Revenue: $1500/month
Automation: 95/100

Why it's a good fit:
• Only 50% of your recommended maximum
• Low risk matches your conservative profile
• Fast time to revenue (1 week)
```

### Interactive Mode
```bash
python3 personalized_opportunity_bot.py

Commands:
  search <query>  - Search opportunities
  advice          - Get portfolio strategy
  compare         - Compare categories
  quit            - Exit
```

### Portfolio Strategy
```bash
python3 personalized_opportunity_bot.py
# Type 'advice' when prompted
```

**Output:**
```
PERSONALIZED PORTFOLIO STRATEGY

Strategy: Low-risk, proven business models
Investment Range: $100 - $100
Focus: Automation and passive income
Timeline: Quick wins (0-3 months)

Recommended Focus:
• Proven digital products
• High-automation (80+ score)
• Under $500 investment
• Fast revenue (<2 months)
```

---

## Understanding Match Scores

### 🟢 Highly Recommended (80-100)
- Strong fit across all dimensions
- You can afford it
- Risk level matches your profile
- Timeline is appropriate

### 🟡 Recommended (60-79)
- Good fit with minor considerations
- May require careful planning
- Some risk factors to evaluate

### 🟠 Consider (40-59)
- Moderate fit
- Significant considerations
- Requires thorough due diligence

### 🔴 Not Recommended (0-39)
- Poor fit for your profile
- Usually exceeds capacity
- Risk mismatch
- Wrong timeline

---

## Scoring Breakdown

Every opportunity gets scored on 4 dimensions:

### 1. Affordability (40% weight)
Can you actually afford this?
- Compares investment to your max capacity
- Considers available credit
- Ensures financial buffer

### 2. Risk Match (25% weight)
Does the risk level fit your tolerance?
- Conservative profile → Low risk opportunities
- Aggressive profile → High growth potential
- Factors in legitimacy score

### 3. Business Type (20% weight)
Is it right for your entity?
- C-Corp: Maximum flexibility
- Non-Profit: Mission alignment required
- LLC/S-Corp: Balanced approach

### 4. Timeline (15% weight)
Can you wait for returns?
- Conservative: Prefer quick wins
- Moderate: 6-12 months acceptable
- Aggressive: Willing to wait for bigger returns

---

## Common Queries

### For Your Profile (Conservative, $100 max)

**Best Searches:**
```bash
python3 query_personalized.py "digital products under $100"
python3 query_personalized.py "automated passive income"
python3 query_personalized.py "Gumroad template business"
python3 query_personalized.py "Notion templates marketplace"
python3 query_personalized.py "low cost high automation"
```

**Avoid:**
```bash
# These will likely be "Not Recommended" for your profile
python3 query_personalized.py "SaaS startup $5000"
python3 query_personalized.py "high risk ventures"
python3 query_personalized.py "equity crowdfunding"
```

---

## Improving Your Profile

### Current State → 6 Month Goal

**Now:**
- Score: 372
- Available Credit: $0
- Max Investment: $100
- Risk: Conservative

**Goal (6 months):**
- Score: 500+
- Available Credit: $5,000
- Max Investment: $1,000
- Risk: Moderate

### Action Plan

1. **Build Credit History (Months 1-3)**
   - Add 3 vendor accounts (net-30 terms)
   - Get business credit card, use 10-30%
   - Pay everything early or on time

2. **Increase Limits (Months 3-6)**
   - Request credit increases
   - Add another tradeline
   - Maintain 100 payment index

3. **Track Progress**
   - Update profile quarterly
   - Re-run searches to see new opportunities
   - Graduate to higher investment opportunities

---

## Files & Structure

```
opportunity-research-bot/
├── credit_integration/
│   ├── fico_parser.py              # FICO data parser
│   ├── credit_scorer.py            # Opportunity scoring
│   ├── personalization_engine.py   # Main engine
│   └── profiles/
│       ├── isnbiz_profile.json     # Your C-Corp profile
│       └── hroc_profile.json       # Your non-profit profile
│
├── personalized_opportunity_bot.py # Main bot
├── query_personalized.py           # Quick search
├── test_personalization.py         # Test suite
└── setup_personalization.sh        # Setup script
```

---

## FAQ

**Q: Do I need to enter my credit data manually?**
A: No! The ISNBIZ profile is already created from your Equifax report.

**Q: Is my credit data secure?**
A: Yes! Everything is stored locally in JSON files. No external servers.

**Q: Can I use this for multiple businesses?**
A: Yes! Switch between entities:
```bash
python3 query_personalized.py "query" isnbiz   # C-Corp
python3 query_personalized.py "query" hroc     # Non-Profit
```

**Q: What if my credit improves?**
A: Update your profile JSON or regenerate it with new data. The bot will automatically adjust recommendations.

**Q: Why are all opportunities scoring low?**
A: Your conservative profile ($100 max) filters out higher-cost opportunities. This is by design to protect you! Focus on:
- Digital products
- Templates
- Automation tools
- Under $100 opportunities

**Q: Can I override the scoring?**
A: Yes, but not recommended. Edit `credit_integration/credit_scorer.py` to adjust weights.

---

## Troubleshooting

### "No opportunities found"
```bash
# Solution: Populate database first
python3 demo_opportunity_pipeline.py
```

### "Profile not found"
```bash
# Solution: Regenerate profiles
python3 credit_integration/fico_parser.py
```

### "All scores are low"
This is actually working correctly! Your conservative profile ($100 max investment) is protecting you from opportunities you can't afford. Focus on:
```bash
python3 query_personalized.py "digital products under $100"
python3 query_personalized.py "templates and tools"
```

---

## Next Steps

### Immediate (Today)
1. ✅ Run setup script
2. ✅ Populate database
3. ✅ Try personalized search

### This Week
1. Search for 5-10 opportunities in your range
2. Review match scores and reasoning
3. Pick top 2-3 to research further

### This Month
1. Start one $50-100 opportunity
2. Track results
3. Build credit history
4. Update profile with progress

### This Quarter
1. Complete first opportunity
2. Add new tradelines
3. Increase credit limits
4. Graduate to $500+ opportunities

---

## Support

For detailed documentation, see:
- [PERSONALIZATION_GUIDE.md](PERSONALIZATION_GUIDE.md) - Comprehensive guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

For issues:
1. Run test suite: `python3 test_personalization.py`
2. Check logs in `logs/` directory
3. Verify database populated: `ls data/chroma_db/`

---

## What Makes This Different

### Traditional Opportunity Research
- ❌ One-size-fits-all recommendations
- ❌ No consideration of your capacity
- ❌ Ignores your risk tolerance
- ❌ Doesn't factor in business type

### Personalized Approach
- ✅ Tailored to YOUR credit profile
- ✅ Matches YOUR financial capacity
- ✅ Aligns with YOUR risk tolerance
- ✅ Respects YOUR business structure
- ✅ Adapts as YOU grow

---

**Ready to find opportunities that actually fit you?**

```bash
python3 query_personalized.py "your perfect opportunity"
```

🎯 Happy hunting!
