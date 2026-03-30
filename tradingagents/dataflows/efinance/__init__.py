"""
efinance - Alternative A-share data provider for Chinese stock market.

This module provides functions to retrieve Chinese A-share stock data using the efinance library.
It serves as a fallback when akshare is unavailable or has rate limits.

Functions:
- get_efinance_stock_online: Historical OHLCV data
- get_efinance_fundamentals: Company fundamentals overview
- get_efinance_balance_sheet: Balance sheet data
- get_efinance_cashflow: Cash flow data
- get_efinance_income_statement: Income statement data

Note: efinance does not provide news data - use akshare for news.
"""

from .stock import get_efinance_stock_online
from .fundamentals import (
    get_efinance_fundamentals,
    get_efinance_balance_sheet,
    get_efinance_cashflow,
    get_efinance_income_statement,
)

__all__ = [
    "get_efinance_stock_online",
    "get_efinance_fundamentals",
    "get_efinance_balance_sheet",
    "get_efinance_cashflow",
    "get_efinance_income_statement",
]
