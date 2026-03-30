"""
akshare - A-share data provider for Chinese stock market.

This module provides functions to retrieve Chinese A-share stock data using the akshare library.
All functions return data in CSV format consistent with other data providers in this package.

Functions:
- get_akshare_stock_online: Historical OHLCV data
- get_akshare_indicators_window: Technical indicators
- get_akshare_fundamentals: Company fundamentals overview
- get_akshare_balance_sheet: Balance sheet data
- get_akshare_cashflow: Cash flow data
- get_akshare_income_statement: Income statement data
- get_akshare_news: Stock-specific news
- get_akshare_global_news: Market-wide news
"""

from .stock import get_akshare_stock_online
from .indicators import get_akshare_indicators_window
from .fundamentals import (
    get_akshare_fundamentals,
    get_akshare_balance_sheet,
    get_akshare_cashflow,
    get_akshare_income_statement,
)
from .news import (
    get_akshare_news,
    get_akshare_global_news,
)

__all__ = [
    "get_akshare_stock_online",
    "get_akshare_indicators_window",
    "get_akshare_fundamentals",
    "get_akshare_balance_sheet",
    "get_akshare_cashflow",
    "get_akshare_income_statement",
    "get_akshare_news",
    "get_akshare_global_news",
]
