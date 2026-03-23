"""Financial analysis toolkit for structured company performance data."""

from .backtest import run_backtest
from .data_loader import load_financial_records, load_price_records
from .factors import compute_factor_snapshots
from .metrics import analyze_records, summarize_company_performance

__all__ = [
    "analyze_records",
    "compute_factor_snapshots",
    "load_financial_records",
    "load_price_records",
    "run_backtest",
    "summarize_company_performance",
]
