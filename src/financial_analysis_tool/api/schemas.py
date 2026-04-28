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
    """Response model for service health and metadata."""

    service: str
    status: Literal["OK"]
    version: str


class CompaniesResponse(BaseModel):
    """Response model listing companies available in the sample universe."""

    companies: list[str]


class CompanyFeaturesResponse(BaseModel):
    """Response model for financial and ESG features for one company."""

    company: str
    financial_summary: dict[str, Any] | None = None
    financial_periods: list[dict[str, Any]] = Field(default_factory=list)
    esg_history: list[dict[str, Any]] = Field(default_factory=list)
    esg_latest: dict[str, Any] | None = None


class RiskSignalResponse(BaseModel):
    """Response model for one explainable company risk signal."""

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
    """Response model summarizing signal counts and severity for a company."""

    company: str
    highest_severity: Severity
    signal_count: int
    severity_counts: dict[str, int]
    signals: list[RiskSignalResponse]


class DecisionResponse(BaseModel):
    """Response model for the portfolio decision recommendation."""

    company: str
    decision: Decision
    highest_severity: Severity
    signal_count: int
    key_drivers: list[str]
    rationale: str


class PipelineRunRequest(BaseModel):
    """Request model for running existing sample-data pipelines."""

    mode: str = "all"


class PipelineRunResponse(BaseModel):
    """Response model describing pipeline execution outputs."""

    status: Literal["OK"]
    mode: Literal["all", "financial", "esg"]
    outputs: dict[str, Any]
