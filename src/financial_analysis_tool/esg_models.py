"""Data models for ESG analysis summaries and presentation-ready insights."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True, slots=True)
class EsgInsight:
    """Represents one business-facing ESG insight."""

    title: str
    finding: str
    implication: str

    def to_dict(self) -> JsonDict:
        """Return the insight in dictionary form."""
        return {
            "title": self.title,
            "finding": self.finding,
            "implication": self.implication,
        }


@dataclass(frozen=True, slots=True)
class EsgAnalysisSummary:
    """Aggregates key ESG outputs for JSON, Markdown, and portfolio presentations."""

    audience_name: str
    cleaned_row_count: int
    company_count: int
    years: list[int]
    average_esg_score: float
    average_carbon_intensity: float
    cleaning_summary: JsonDict
    sector_summary: list[JsonDict]
    high_risk_companies: list[JsonDict]
    insights: list[EsgInsight]

    def to_dict(self) -> JsonDict:
        """Return the ESG summary in JSON-serializable dictionary form."""
        return {
            "audience_name": self.audience_name,
            "cleaned_row_count": self.cleaned_row_count,
            "company_count": self.company_count,
            "years": self.years,
            "average_esg_score": self.average_esg_score,
            "average_carbon_intensity": self.average_carbon_intensity,
            "cleaning_summary": self.cleaning_summary,
            "sector_summary": self.sector_summary,
            "high_risk_companies": self.high_risk_companies,
            "insights": [insight.to_dict() for insight in self.insights],
        }
