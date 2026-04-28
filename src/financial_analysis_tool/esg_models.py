"""Data models for ESG analysis summaries and presentation-ready insights.

These dataclasses define business-facing ESG contracts used by reports, CLI
output, dashboards, and API responses after the pandas-based ESG pipeline has
finished cleaning and analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]


@dataclass(frozen=True, slots=True)
class EsgInsight:
    """Represents one business-facing ESG insight.

    Attributes:
        title: Short insight label for reports and dashboards.
        finding: Data-backed observation from the ESG analysis.
        implication: Business interpretation for financial stakeholders.
    """

    title: str
    finding: str
    implication: str

    def to_dict(self) -> JsonDict:
        """Convert the insight to a JSON-serializable dictionary.

        Returns:
            JsonDict: Business-facing insight payload.
        """
        return {
            "title": self.title,
            "finding": self.finding,
            "implication": self.implication,
        }


@dataclass(frozen=True, slots=True)
class EsgAnalysisSummary:
    """Aggregates key ESG outputs for JSON, Markdown, and presentations.

    Attributes:
        audience_name: Stakeholder name used in business reports.
        cleaned_row_count: Number of ESG rows after validation and cleaning.
        company_count: Number of unique companies in the cleaned dataset.
        years: Covered reporting years.
        average_esg_score: Portfolio average ESG score.
        average_carbon_intensity: Portfolio average emissions intensity.
        cleaning_summary: Data quality and imputation audit metrics.
        sector_summary: Latest-year ESG exposure summarized by sector.
        high_risk_companies: Latest-year ESG watchlist records.
        insights: Business-facing insights derived from the analysis.
    """

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
        """Convert the ESG summary to JSON-serializable dictionaries.

        Returns:
            JsonDict: ESG summary payload for reports and API responses.
        """
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
