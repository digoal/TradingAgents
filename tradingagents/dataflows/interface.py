from typing import Annotated

# Import from vendor-specific modules
from .y_finance import (
    get_YFin_data_online,
    get_stock_stats_indicators_window,
    get_fundamentals as get_yfinance_fundamentals,
    get_balance_sheet as get_yfinance_balance_sheet,
    get_cashflow as get_yfinance_cashflow,
    get_income_statement as get_yfinance_income_statement,
    get_insider_transactions as get_yfinance_insider_transactions,
)
from .yfinance_news import get_news_yfinance, get_global_news_yfinance
from .alpha_vantage import (
    get_stock as get_alpha_vantage_stock,
    get_indicator as get_alpha_vantage_indicator,
    get_fundamentals as get_alpha_vantage_fundamentals,
    get_balance_sheet as get_alpha_vantage_balance_sheet,
    get_cashflow as get_alpha_vantage_cashflow,
    get_income_statement as get_alpha_vantage_income_statement,
    get_insider_transactions as get_alpha_vantage_insider_transactions,
    get_news as get_alpha_vantage_news,
    get_global_news as get_alpha_vantage_global_news,
)
from .alpha_vantage_common import AlphaVantageRateLimitError


class DataNotFoundError(Exception):
    """Raised when data is not found for a given ticker/date range."""
    pass

# Import A-share data providers
from .akshare import (
    get_akshare_stock_online,
    get_akshare_indicators_window,
    get_akshare_fundamentals,
    get_akshare_balance_sheet,
    get_akshare_cashflow,
    get_akshare_income_statement,
    get_akshare_news,
    get_akshare_global_news,
)
from .efinance import (
    get_efinance_stock_online,
    get_efinance_fundamentals,
    get_efinance_balance_sheet,
    get_efinance_cashflow,
    get_efinance_income_statement,
)

# Import A-share ticker utilities
from .cn_ticker_utils import is_china_ticker

# Configuration and routing logic
from .config import get_config

# Tools organized by category
TOOLS_CATEGORIES = {
    "core_stock_apis": {
        "description": "OHLCV stock price data",
        "tools": [
            "get_stock_data"
        ]
    },
    "technical_indicators": {
        "description": "Technical analysis indicators",
        "tools": [
            "get_indicators"
        ]
    },
    "fundamental_data": {
        "description": "Company fundamentals",
        "tools": [
            "get_fundamentals",
            "get_balance_sheet",
            "get_cashflow",
            "get_income_statement"
        ]
    },
    "news_data": {
        "description": "News and insider data",
        "tools": [
            "get_news",
            "get_global_news",
            "get_insider_transactions",
        ]
    }
}

VENDOR_LIST = [
    "yfinance",
    "alpha_vantage",
    "akshare",
    "efinance",
]

# Mapping of methods to their vendor-specific implementations
VENDOR_METHODS = {
    # core_stock_apis
    "get_stock_data": {
        "alpha_vantage": get_alpha_vantage_stock,
        "yfinance": get_YFin_data_online,
        "akshare": get_akshare_stock_online,
        "efinance": get_efinance_stock_online,
    },
    # technical_indicators
    "get_indicators": {
        "alpha_vantage": get_alpha_vantage_indicator,
        "yfinance": get_stock_stats_indicators_window,
        "akshare": get_akshare_indicators_window,
        # efinance falls back to yfinance for indicators after getting data
    },
    # fundamental_data
    "get_fundamentals": {
        "alpha_vantage": get_alpha_vantage_fundamentals,
        "yfinance": get_yfinance_fundamentals,
        "akshare": get_akshare_fundamentals,
        "efinance": get_efinance_fundamentals,
    },
    "get_balance_sheet": {
        "alpha_vantage": get_alpha_vantage_balance_sheet,
        "yfinance": get_yfinance_balance_sheet,
        "akshare": get_akshare_balance_sheet,
        "efinance": get_efinance_balance_sheet,
    },
    "get_cashflow": {
        "alpha_vantage": get_alpha_vantage_cashflow,
        "yfinance": get_yfinance_cashflow,
        "akshare": get_akshare_cashflow,
        "efinance": get_efinance_cashflow,
    },
    "get_income_statement": {
        "alpha_vantage": get_alpha_vantage_income_statement,
        "yfinance": get_yfinance_income_statement,
        "akshare": get_akshare_income_statement,
        "efinance": get_efinance_income_statement,
    },
    # news_data
    "get_news": {
        "alpha_vantage": get_alpha_vantage_news,
        "yfinance": get_news_yfinance,
        "akshare": get_akshare_news,
        # efinance does not provide news
    },
    "get_global_news": {
        "yfinance": get_global_news_yfinance,
        "alpha_vantage": get_alpha_vantage_global_news,
        "akshare": get_akshare_global_news,
    },
    "get_insider_transactions": {
        "alpha_vantage": get_alpha_vantage_insider_transactions,
        "yfinance": get_yfinance_insider_transactions,
        # akshare/efinance: Not applicable for A-shares
    },
}

def get_category_for_method(method: str) -> str:
    """Get the category that contains the specified method."""
    for category, info in TOOLS_CATEGORIES.items():
        if method in info["tools"]:
            return category
    raise ValueError(f"Method '{method}' not found in any category")

def get_vendor(category: str, method: str = None) -> str:
    """Get the configured vendor for a data category or specific tool method.
    Tool-level configuration takes precedence over category-level.
    """
    config = get_config()

    # Check tool-level configuration first (if method provided)
    if method:
        tool_vendors = config.get("tool_vendors", {})
        if method in tool_vendors:
            return tool_vendors[method]

    # Fall back to category-level configuration
    return config.get("data_vendors", {}).get(category, "default")

def route_to_vendor(method: str, *args, **kwargs):
    """Route method calls to appropriate vendor implementation with fallback support.

    This function automatically detects A-share tickers and prioritizes
    akshare/efinance for Chinese stocks, while using yfinance/alpha_vantage
    for international stocks.
    """
    category = get_category_for_method(method)
    vendor_config = get_vendor(category, method)
    primary_vendors = [v.strip() for v in vendor_config.split(',')]

    if method not in VENDOR_METHODS:
        raise ValueError(f"Method '{method}' not supported")

    # Detect if this is an A-share ticker
    ticker = args[0] if args else kwargs.get('symbol') or kwargs.get('ticker', '')
    is_cn_stock = is_china_ticker(str(ticker)) if ticker else False

    # Build fallback chain: primary vendors first, then remaining available vendors
    all_available_vendors = list(VENDOR_METHODS[method].keys())
    fallback_vendors = primary_vendors.copy()
    for vendor in all_available_vendors:
        if vendor not in fallback_vendors:
            fallback_vendors.append(vendor)

    # For A-share stocks, CN vendors (akshare, efinance) are tried first
    # If they fail, international vendors (yfinance) will be tried as fallback
    # This is because yfinance can provide some A-share data (especially fundamentals)
    if is_cn_stock:
        cn_vendors = ['akshare', 'efinance']
        # Reorder: CN vendors first, then international vendors
        cn_first = [v for v in fallback_vendors if v in cn_vendors]
        intl_next = [v for v in fallback_vendors if v not in cn_vendors]
        fallback_vendors = cn_first + intl_next

        if not fallback_vendors:
            raise RuntimeError(
                f"No A-share data vendors configured for '{method}'. "
                f"Available CN vendors: {cn_vendors}"
            )

    last_vendor_idx = len(fallback_vendors) - 1
    last_error = None

    for idx, vendor in enumerate(fallback_vendors):
        if vendor not in VENDOR_METHODS[method]:
            continue

        vendor_impl = VENDOR_METHODS[method][vendor]
        impl_func = vendor_impl[0] if isinstance(vendor_impl, list) else vendor_impl

        try:
            result = impl_func(*args, **kwargs)
            # If result indicates no data found or error, raise to trigger fallback
            if isinstance(result, str) and (result.startswith("No data found") or result.startswith("Error")):
                last_error = result
                # If this is the last vendor, return graceful failure message
                if idx == last_vendor_idx:
                    return f"Error: Data unavailable for '{method}'. All vendors failed. Last error from {vendor}: {result}"
                raise DataNotFoundError(result)
            return result
        except (AlphaVantageRateLimitError, DataNotFoundError) as e:
            last_error = str(e)
            if idx == last_vendor_idx:
                # Last vendor failed - return graceful failure message instead of crashing
                return f"Error: Data unavailable for '{method}'. All vendors failed. Last vendor: {vendor}, Error: {last_error}"
            continue  # Rate limits and data not found trigger fallback to next vendor
        except Exception as e:
            last_error = str(e)
            # For other exceptions (like network errors), try next vendor
            if idx == last_vendor_idx:
                # Return graceful failure message instead of crashing
                return f"Error: Data unavailable for '{method}'. All vendors failed. Last vendor: {vendor}, Error: {last_error}"
            continue

    # This should not be reached, but just in case return a graceful message
    return f"Error: No available vendor for '{method}'"