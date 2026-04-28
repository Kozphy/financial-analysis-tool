"""FastAPI app for the Financial ESG Risk Intelligence API.

The module defines the HTTP delivery surface only. Route handlers stay thin by
delegating data access, analysis orchestration, risk signal generation, and
decision mapping to ``api.services``.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from . import services
from .schemas import (
    CompaniesResponse,
    CompanyFeaturesResponse,
    DecisionResponse,
    HealthResponse,
    PipelineRunRequest,
    PipelineRunResponse,
    RiskProfileResponse,
    SignalsResponse,
)


app = FastAPI(
    title="Financial ESG Risk Intelligence API",
    version=services.SERVICE_VERSION,
    description="Production-style API wrapper for sample financial and ESG risk analytics.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    """Return service health and metadata.

    Returns:
        dict[str, str]: Service name, OK status, and API version.
    """
    return services.get_health()


@app.get("/companies", response_model=CompaniesResponse)
def companies() -> dict[str, list[str]]:
    """Return companies available in the bundled sample data.

    Returns:
        dict[str, list[str]]: Alphabetized company names available to the API.
    """
    return {"companies": services.list_companies()}


@app.get("/features/{company}", response_model=CompanyFeaturesResponse)
def features(company: str) -> dict:
    """Return financial and ESG features for one company.

    Args:
        company: URL path company name.

    Returns:
        dict: JSON-ready financial and ESG feature payload.

    Raises:
        HTTPException: Returns 404 when the company is not covered.
    """
    try:
        return services.get_company_features(company)
    except services.CompanyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/signals/{company}", response_model=SignalsResponse)
def signals(company: str) -> dict:
    """Return explainable risk signals for one company.

    Args:
        company: URL path company name.

    Returns:
        dict: Company name and signal list containing reasons and recommendations.

    Raises:
        HTTPException: Returns 404 when the company is not covered.
    """
    try:
        canonical_company = services.get_company_features(company)["company"]
        return {
            "company": canonical_company,
            "signals": services.get_company_signals(canonical_company),
        }
    except services.CompanyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/risk/{company}", response_model=RiskProfileResponse)
def risk(company: str) -> dict:
    """Return a summarized risk profile for one company.

    Args:
        company: URL path company name.

    Returns:
        dict: Severity counts, highest severity, and supporting signals.

    Raises:
        HTTPException: Returns 404 when the company is not covered.
    """
    try:
        return services.get_company_risk_profile(company)
    except services.CompanyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/decisions/{company}", response_model=DecisionResponse)
def decisions(company: str) -> dict:
    """Return the decision-engine recommendation for one company.

    Args:
        company: URL path company name.

    Returns:
        dict: Portfolio action, key drivers, and rationale.

    Raises:
        HTTPException: Returns 404 when the company is not covered.
    """
    try:
        return services.get_company_decision(company)
    except services.CompanyNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/pipeline/run", response_model=PipelineRunResponse)
def pipeline_run(request: PipelineRunRequest) -> dict:
    """Run sample-data financial, ESG, or combined pipelines.

    Args:
        request: Requested pipeline mode: ``all``, ``financial``, or ``esg``.

    Returns:
        dict: Status, selected mode, and written artifact paths.

    Raises:
        HTTPException: Returns 400 when the requested mode is unsupported.
    """
    try:
        return services.run_pipeline(request.mode)
    except services.InvalidPipelineModeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
