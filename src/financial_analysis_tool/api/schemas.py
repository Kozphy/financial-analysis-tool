"""Pydantic schemas for the Financial ESG Risk Intelligence API.

These models define the public API contract separately from the internal
dataclasses, pandas frames, and pipeline artifacts used by the analysis layer.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Severity = Literal["LOW", "MEDIUM", "HIGH"]
Decision = Literal[
    "HOLD",
    "REVIEW",
    "ENGAGE",
    "REDUCE_EXPOSURE",
    "ENHANCED_DUE_DILIGENCE",
]


class HealthResponse(BaseModel):
    """Response model for service health and metadata.

    Attributes:
        service: Human-readable API product name.
        status: Constant health status used by smoke tests.
        version: API implementation version.
    """

    service: str
    status: Literal["OK"]
    version: str


class CompaniesResponse(BaseModel):
    """Response model listing companies available in the sample universe.

    Attributes:
        companies: Alphabetized company names available from financial or ESG
            sample data.
    """

    companies: list[str]


class CompanyFeaturesResponse(BaseModel):
    """Response model for financial and ESG features for one company.

    Attributes:
        company: Canonical company name.
        financial_summary: Financial summary payload when available.
        financial_periods: Period-level financial metrics when available.
        esg_history: Cleaned ESG company-year records.
        esg_latest: Latest ESG company-year record when available.
    """

    company: str
    financial_summary: dict[str, Any] | None = None
    financial_periods: list[dict[str, Any]] = Field(default_factory=list)
    esg_history: list[dict[str, Any]] = Field(default_factory=list)
    esg_latest: dict[str, Any] | None = None


class RiskSignalResponse(BaseModel):
    """Response model for one explainable company risk signal.

    Attributes:
        company: Company the signal applies to.
        year: ESG year or financial period.
        signal_type: Stable signal identifier.
        severity: Business severity used by risk and decision endpoints.
        reason: Human-readable explanation of the rule result.
        metric_value: Numeric value supporting the signal.
        recommendation: Suggested monitoring or portfolio action.
    """

    company: str
    year: int | str
    signal_type: str
    severity: Severity
    reason: str
    metric_value: float
    recommendation: str


class SignalsResponse(BaseModel):
    """Response model for all explainable signals for a company."""

    company: str
    signals: list[RiskSignalResponse]


class RiskProfileResponse(BaseModel):
    """Response model summarizing signal counts and severity for a company.

    Attributes:
        company: Canonical company name.
        highest_severity: Highest severity across returned signals.
        signal_count: Number of signals returned.
        severity_counts: Counts keyed by severity label.
        signals: Full explainable signal payloads.
    """

    company: str
    highest_severity: Severity
    signal_count: int
    severity_counts: dict[str, int]
    signals: list[RiskSignalResponse]


class DecisionResponse(BaseModel):
    """Response model for the portfolio decision recommendation.

    Attributes:
        company: Canonical company name.
        decision: Portfolio monitoring action selected by policy rules.
        highest_severity: Highest severity across input signals.
        signal_count: Number of signals considered.
        key_drivers: Top signal reasons that explain the decision.
        rationale: Human-readable decision explanation.
    """

    company: str
    decision: Decision
    highest_severity: Severity
    signal_count: int
    key_drivers: list[str]
    rationale: str


class PipelineRunRequest(BaseModel):
    """Request model for running existing sample-data pipelines.

    Attributes:
        mode: Pipeline mode. Valid values are checked in the service layer and
            include ``all``, ``financial``, and ``esg``.
    """

    mode: str = "all"


class PipelineRunResponse(BaseModel):
    """Response model describing pipeline execution outputs.

    Attributes:
        status: Constant success status when requested pipelines complete.
        mode: Pipeline mode that was executed.
        outputs: Generated artifact paths grouped by pipeline.
    """

    status: Literal["OK"]
    mode: Literal["all", "financial", "esg"]
    outputs: dict[str, Any]
