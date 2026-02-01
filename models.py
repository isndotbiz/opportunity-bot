#!/usr/bin/env python3
"""
Pydantic models for opportunity data validation
Modern, type-safe data models with validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator, field_validator


class OpportunitySource(str, Enum):
    """Source platforms for opportunities"""
    REDDIT = "reddit"
    INDIE_HACKERS = "indie_hackers"
    GOOGLE_DORK = "google_dork"
    TWITTER = "twitter"
    HACKER_NEWS = "hacker_news"
    OTHER = "other"


class TechnicalDifficulty(int, Enum):
    """Technical difficulty levels"""
    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    HARD = 4
    VERY_HARD = 5


class OpportunityMetadata(BaseModel):
    """Metadata extracted from opportunity"""
    title: str = Field(..., min_length=5, max_length=500, description="Opportunity title")
    description: str = Field(..., min_length=10, description="Full description")
    source: OpportunitySource = Field(..., description="Platform where found")
    source_url: HttpUrl = Field(..., description="Original URL")

    # Revenue information
    revenue_claim: Optional[str] = Field(None, description="Claimed revenue (e.g., $5000/month)")
    revenue_amount: Optional[float] = Field(None, ge=0, description="Parsed revenue amount in USD")
    revenue_period: Optional[str] = Field(None, description="Revenue period (month/year)")

    # Technical details
    tech_stack: List[str] = Field(default_factory=list, description="Technologies mentioned")
    time_to_build: Optional[str] = Field(None, description="Time mentioned to build")

    # Social proof
    score: Optional[int] = Field(None, ge=0, description="Platform score (upvotes, likes, etc.)")
    comments_count: Optional[int] = Field(None, ge=0, description="Number of comments/engagement")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="When opportunity was created")
    discovered_at: datetime = Field(default_factory=datetime.now, description="When we discovered it")

    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    author: Optional[str] = Field(None, description="Author/creator username")

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "title": "AI Content Repurposing Tool",
                "description": "Automated tool for repurposing long-form content into social media posts",
                "source": "reddit",
                "source_url": "https://reddit.com/r/SideProject/example",
                "revenue_claim": "$3000/month",
                "revenue_amount": 3000.0,
                "revenue_period": "month",
                "tech_stack": ["Python", "GPT-4", "FastAPI"],
                "score": 245,
                "tags": ["ai", "automation", "saas"]
            }
        }


class OpportunityAnalysis(BaseModel):
    """AI-generated analysis of opportunity"""

    # Scores (0-100)
    automation_score: int = Field(..., ge=0, le=100, description="How automated/passive is this")
    legitimacy_score: int = Field(..., ge=0, le=100, description="How legitimate/viable this appears")
    scalability_score: int = Field(..., ge=0, le=100, description="Scalability potential")

    # Difficulty & Investment
    technical_difficulty: TechnicalDifficulty = Field(..., description="Technical complexity (1-5)")
    time_to_market: str = Field(..., description="Estimated time to build")
    initial_investment: str = Field(..., description="Estimated startup costs")

    # Insights
    key_insights: List[str] = Field(..., min_length=1, description="Key takeaways")
    automation_opportunities: List[str] = Field(default_factory=list, description="What can be automated")
    risks: List[str] = Field(default_factory=list, description="Potential risks")
    competitive_advantages: List[str] = Field(default_factory=list, description="Unique selling points")

    # Market analysis
    target_market: Optional[str] = Field(None, description="Target customer segment")
    market_size_estimate: Optional[str] = Field(None, description="Estimated market size")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    analysis_model: str = Field(default="qwen-2.5-7b", description="LLM used for analysis")

    class Config:
        use_enum_values = True


class Opportunity(BaseModel):
    """Complete opportunity with metadata and analysis"""

    id: Optional[str] = Field(None, description="Unique identifier")
    metadata: OpportunityMetadata = Field(..., description="Opportunity metadata")
    analysis: Optional[OpportunityAnalysis] = Field(None, description="AI analysis")

    # RAG storage metadata
    collection_name: str = Field(default="business_opportunities", description="ChromaDB collection")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model")

    # Document representation for RAG
    def to_document(self) -> str:
        """Convert to markdown document for RAG storage"""
        doc = f"# {self.metadata.title}\n\n"
        doc += f"## Overview\n{self.metadata.description}\n\n"

        doc += f"## Source\n"
        doc += f"- Platform: {self.metadata.source}\n"
        doc += f"- URL: {self.metadata.source_url}\n"
        if self.metadata.author:
            doc += f"- Author: {self.metadata.author}\n"
        if self.metadata.score:
            doc += f"- Score: {self.metadata.score}\n"
        doc += f"- Discovered: {self.metadata.discovered_at.isoformat()}\n\n"

        if self.metadata.revenue_claim:
            doc += f"## Revenue\n"
            doc += f"- Claim: {self.metadata.revenue_claim}\n"
            if self.metadata.revenue_amount:
                doc += f"- Amount: ${self.metadata.revenue_amount:,.2f}\n"
            doc += "\n"

        if self.metadata.tech_stack:
            doc += f"## Tech Stack\n"
            doc += "\n".join(f"- {tech}" for tech in self.metadata.tech_stack)
            doc += "\n\n"

        if self.analysis:
            doc += f"## Analysis\n"
            doc += f"- Automation Score: {self.analysis.automation_score}/100\n"
            doc += f"- Legitimacy Score: {self.analysis.legitimacy_score}/100\n"
            doc += f"- Scalability: {self.analysis.scalability_score}/100\n"
            doc += f"- Technical Difficulty: {self.analysis.technical_difficulty}/5\n"
            doc += f"- Time to Market: {self.analysis.time_to_market}\n"
            doc += f"- Initial Investment: {self.analysis.initial_investment}\n\n"

            if self.analysis.key_insights:
                doc += f"### Key Insights\n"
                doc += "\n".join(f"- {insight}" for insight in self.analysis.key_insights)
                doc += "\n\n"

            if self.analysis.automation_opportunities:
                doc += f"### Automation Opportunities\n"
                doc += "\n".join(f"- {opp}" for opp in self.analysis.automation_opportunities)
                doc += "\n\n"

            if self.analysis.risks:
                doc += f"### Risks\n"
                doc += "\n".join(f"- {risk}" for risk in self.analysis.risks)
                doc += "\n\n"

            if self.analysis.competitive_advantages:
                doc += f"### Competitive Advantages\n"
                doc += "\n".join(f"- {adv}" for adv in self.analysis.competitive_advantages)
                doc += "\n\n"

        if self.metadata.tags:
            doc += f"## Tags\n"
            doc += ", ".join(self.metadata.tags)
            doc += "\n"

        return doc

    def to_metadata_dict(self) -> Dict[str, Any]:
        """Convert to metadata dictionary for ChromaDB"""
        meta = {
            "title": self.metadata.title,
            "source": self.metadata.source,
            "url": str(self.metadata.source_url),
            "created_at": self.metadata.created_at.isoformat(),
            "discovered_at": self.metadata.discovered_at.isoformat(),
        }

        # Add optional fields if present
        if self.metadata.revenue_claim:
            meta["revenue_claim"] = self.metadata.revenue_claim
        if self.metadata.revenue_amount:
            meta["revenue_amount"] = self.metadata.revenue_amount
        if self.metadata.tech_stack:
            meta["tech_stack"] = ",".join(self.metadata.tech_stack)
        if self.metadata.author:
            meta["author"] = self.metadata.author
        if self.metadata.score:
            meta["score"] = self.metadata.score
        if self.metadata.tags:
            meta["tags"] = ",".join(self.metadata.tags)

        # Add analysis if present
        if self.analysis:
            meta.update({
                "automation_score": self.analysis.automation_score,
                "legitimacy_score": self.analysis.legitimacy_score,
                "scalability_score": self.analysis.scalability_score,
                "technical_difficulty": self.analysis.technical_difficulty,
                "time_to_market": self.analysis.time_to_market,
                "initial_investment": self.analysis.initial_investment,
                "analyzed_at": self.analysis.analyzed_at.isoformat(),
            })

        return meta

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "title": "AI Content Repurposing Tool",
                    "description": "Tool that takes long-form content and creates social media posts",
                    "source": "reddit",
                    "source_url": "https://reddit.com/r/SideProject/example",
                    "revenue_claim": "$3000/month",
                    "tech_stack": ["Python", "GPT-4", "FastAPI"],
                },
                "analysis": {
                    "automation_score": 90,
                    "legitimacy_score": 85,
                    "scalability_score": 80,
                    "technical_difficulty": 2,
                    "time_to_market": "2-4 weeks",
                    "initial_investment": "$500",
                    "key_insights": ["High automation potential", "Proven revenue model"]
                }
            }
        }


class CrawlResult(BaseModel):
    """Result from web crawling operation"""

    url: str = Field(..., description="URL that was crawled")
    success: bool = Field(..., description="Whether crawl was successful")

    # Content
    title: Optional[str] = Field(None, description="Page title")
    markdown: Optional[str] = Field(None, description="Extracted markdown content")
    html: Optional[str] = Field(None, description="Raw HTML")

    # Metadata
    status_code: Optional[int] = Field(None, description="HTTP status code")
    error: Optional[str] = Field(None, description="Error message if failed")

    # Links and media
    links: List[str] = Field(default_factory=list, description="Extracted links")
    images: List[str] = Field(default_factory=list, description="Extracted images")

    # Performance
    crawl_time_ms: Optional[int] = Field(None, description="Time taken to crawl (ms)")

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now, description="When crawled")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "success": True,
                "title": "Example Page",
                "markdown": "# Example\nContent here",
                "status_code": 200,
                "links": ["https://example.com/page1"],
                "crawl_time_ms": 1234
            }
        }


class ScraperConfig(BaseModel):
    """Configuration for scrapers"""

    # Crawl4AI settings
    headless: bool = Field(default=True, description="Run browser in headless mode")
    user_agent: str = Field(
        default="OpportunityBot/2.0 (+https://github.com/yourusername/opportunity-bot)",
        description="User agent string"
    )
    timeout: int = Field(default=30, ge=5, le=120, description="Request timeout in seconds")
    max_concurrent: int = Field(default=5, ge=1, le=20, description="Max concurrent requests")

    # Rate limiting
    min_delay: float = Field(default=1.0, ge=0.1, description="Minimum delay between requests")
    max_delay: float = Field(default=3.0, ge=0.5, description="Maximum delay between requests")

    # JavaScript rendering
    render_js: bool = Field(default=True, description="Enable JavaScript rendering")
    wait_for: str = Field(default="networkidle", description="Wait condition (load, domcontentloaded, networkidle)")

    # Retry settings
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay: float = Field(default=2.0, ge=0.5, description="Delay between retries")

    class Config:
        json_schema_extra = {
            "example": {
                "headless": True,
                "timeout": 30,
                "max_concurrent": 5,
                "render_js": True
            }
        }
