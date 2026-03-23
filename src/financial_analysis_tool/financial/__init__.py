"""Financial statement analysis package."""

from .loader import load_financial_records
from .metrics import analyze_records, summarize_company_performance

__all__ = [
    "analyze_records",
    "load_financial_records",
    "summarize_company_performance",
]
