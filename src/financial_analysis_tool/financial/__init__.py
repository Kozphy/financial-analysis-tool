"""Financial statement analysis package."""

from .loader import fetch_mops_financial_records, load_financial_records
from .metrics import analyze_records, summarize_company_performance

__all__ = [
    "analyze_records",
    "fetch_mops_financial_records",
    "load_financial_records",
    "summarize_company_performance",
]
