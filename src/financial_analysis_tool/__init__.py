"""Financial analysis toolkit for structured company performance data."""

from .financial.loader import load_financial_records
from .financial.metrics import analyze_records, summarize_company_performance
from .quant.backtest import run_backtest
from .quant.factors import compute_factor_snapshots
from .quant.loader import fetch_binance_price_records, load_price_records

__all__ = [
    "analyze_records",
    "compute_factor_snapshots",
    "fetch_binance_price_records",
    "load_financial_records",
    "load_price_records",
    "run_backtest",
    "summarize_company_performance",
]
