"""
akshare fundamental data implementation for A-share market.

Provides company fundamentals, balance sheet, cash flow, and income statement data.
"""

from datetime import datetime
from typing import Annotated
import pandas as pd

from ..cn_ticker_utils import is_china_ticker, normalize_cn_ticker


def _format_df_to_csv(df: pd.DataFrame, ticker: str, data_type: str) -> str:
    """Convert DataFrame to CSV string with header."""
    if df is None or df.empty:
        return f"No {data_type} data found for {ticker}"

    header = f"# {data_type} for {ticker}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"# Source: akshare\n\n"

    return header + df.to_csv()


def get_akshare_fundamentals(
    ticker: Annotated[str, "ticker symbol (supports A-share)"],
    curr_date: Annotated[str, "current date (not used for akshare)"] = None,
) -> str:
    """
    Get A-share company fundamentals overview.

    Args:
        ticker: A-share ticker in any supported format
        curr_date: Not used, kept for interface compatibility

    Returns:
        Formatted string with company fundamentals
    """
    if is_china_ticker(ticker):
        # akshare uses just the 6-digit code, no suffix
        market, code = normalize_cn_ticker(ticker)
        ticker = code

    try:
        import akshare as ak

        # Get individual stock info
        info = ak.stock_individual_info_em(symbol=ticker)

        if info is None or info.empty:
            return f"No fundamentals data found for {ticker}"

        # Convert to key-value format
        lines = []
        for _, row in info.iterrows():
            if len(row) >= 2:
                lines.append(f"{row.iloc[0]}: {row.iloc[1]}")

        header = f"# Company Fundamentals for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Source: akshare\n\n"

        return header + "\n".join(lines)

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {str(e)}"


def get_akshare_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share balance sheet data.

    Args:
        ticker: A-share ticker
        freq: 'annual' or 'quarterly'
        curr_date: Not used

    Returns:
        CSV string with balance sheet data
    """
    if is_china_ticker(ticker):
        # akshare uses just the 6-digit code, no suffix
        market, code = normalize_cn_ticker(ticker)
        ticker = code

    try:
        import akshare as ak

        # Use correct function names for eastmoney financial statements
        if freq.lower() == 'quarterly':
            data = ak.stock_balance_sheet_by_report_em(symbol=ticker)
        else:
            data = ak.stock_balance_sheet_by_yearly_em(symbol=ticker)

        return _format_df_to_csv(data, ticker, f"Balance Sheet ({freq})")

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving balance sheet for {ticker}: {str(e)}"


def get_akshare_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share cash flow statement data.

    Args:
        ticker: A-share ticker
        freq: 'annual' or 'quarterly'
        curr_date: Not used

    Returns:
        CSV string with cash flow data
    """
    if is_china_ticker(ticker):
        # akshare uses just the 6-digit code, no suffix
        market, code = normalize_cn_ticker(ticker)
        ticker = code

    try:
        import akshare as ak

        # Use correct function names for eastmoney financial statements
        if freq.lower() == 'quarterly':
            data = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=ticker)
        else:
            data = ak.stock_cash_flow_sheet_by_yearly_em(symbol=ticker)

        return _format_df_to_csv(data, ticker, f"Cash Flow ({freq})")

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving cash flow for {ticker}: {str(e)}"


def get_akshare_income_statement(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share income statement data.

    Args:
        ticker: A-share ticker
        freq: 'annual' or 'quarterly'
        curr_date: Not used

    Returns:
        CSV string with income statement data
    """
    if is_china_ticker(ticker):
        # akshare uses just the 6-digit code, no suffix
        market, code = normalize_cn_ticker(ticker)
        ticker = code

    try:
        import akshare as ak

        # Use correct function names for eastmoney financial statements
        if freq.lower() == 'quarterly':
            data = ak.stock_profit_sheet_by_quarterly_em(symbol=ticker)
        else:
            data = ak.stock_profit_sheet_by_yearly_em(symbol=ticker)

        return _format_df_to_csv(data, ticker, f"Income Statement ({freq})")

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving income statement for {ticker}: {str(e)}"
