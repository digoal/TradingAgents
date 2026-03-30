"""
efinance fundamental data implementation for A-share market.

Provides company fundamentals, balance sheet, cash flow, and income statement data.
Note: efinance fundamental data functions rely on eastmoney servers which may be blocked.
If eastmoney is blocked, these functions will return "unavailable" messages.
"""

from datetime import datetime
from typing import Annotated
import pandas as pd

from ..cn_ticker_utils import (
    to_efinance_ticker,
    get_efinance_market,
    is_china_ticker,
)


def _format_df_to_csv(df: pd.DataFrame, ticker: str, data_type: str) -> str:
    """Convert DataFrame to CSV string with header."""
    if df is None or df.empty:
        return f"No {data_type} data found for {ticker}"

    header = f"# {data_type} for {ticker}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"# Source: efinance\n\n"

    return header + df.to_csv()


def get_efinance_fundamentals(
    ticker: Annotated[str, "ticker symbol (supports A-share)"],
    curr_date: Annotated[str, "current date (not used for efinance)"] = None,
) -> str:
    """
    Get A-share company fundamentals overview.

    Args:
        ticker: A-share ticker in any supported format
        curr_date: Not used, kept for interface compatibility

    Returns:
        Formatted string with company fundamentals, or unavailable message
    """
    if not is_china_ticker(ticker):
        return f"Error: efinance only supports A-share stocks. Got: {ticker}"

    try:
        code = to_efinance_ticker(ticker)
    except ValueError as e:
        return f"Error: {str(e)}"

    try:
        import efinance as ef

        # Get stock info using correct module path
        info = ef.stock.get_base_info(code)

        if info is None or (isinstance(info, pd.DataFrame) and info.empty):
            return f"No fundamentals data found for {ticker}"

        # Convert to key-value format
        lines = []
        if isinstance(info, dict):
            for key, value in info.items():
                if pd.notna(value):
                    lines.append(f"{key}: {value}")
        elif isinstance(info, pd.DataFrame):
            for _, row in info.iterrows():
                if len(row) >= 2:
                    lines.append(f"{row.iloc[0]}: {row.iloc[1]}")

        header = f"# Company Fundamentals for {ticker}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Source: efinance\n\n"

        return header + "\n".join(lines)

    except ImportError:
        return "Error: efinance library not installed"
    except AttributeError:
        return f"Error: efinance fundamental data unavailable (API changed or eastmoney blocked)"
    except Exception as e:
        return f"Error retrieving fundamentals for {ticker}: {str(e)}"


def get_efinance_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share balance sheet data.

    Note: efinance does not provide balance sheet data directly.
    This function returns an unavailable message.

    Args:
        ticker: A-share ticker
        freq: Not used
        curr_date: Not used

    Returns:
        Unavailable message
    """
    if not is_china_ticker(ticker):
        return f"Error: efinance only supports A-share stocks. Got: {ticker}"

    return f"Error: efinance does not provide balance sheet data. Use akshare or other sources."


def get_efinance_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share cash flow statement data.

    Note: efinance does not provide cash flow data directly.
    This function returns an unavailable message.

    Args:
        ticker: A-share ticker
        freq: Not used
        curr_date: Not used

    Returns:
        Unavailable message
    """
    if not is_china_ticker(ticker):
        return f"Error: efinance only supports A-share stocks. Got: {ticker}"

    return f"Error: efinance does not provide cash flow data. Use akshare or other sources."


def get_efinance_income_statement(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[str, "frequency: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None,
) -> str:
    """
    Get A-share income statement data.

    Note: efinance does not provide income statement data directly.
    This function returns an unavailable message.

    Args:
        ticker: A-share ticker
        freq: Not used
        curr_date: Not used

    Returns:
        Unavailable message
    """
    if not is_china_ticker(ticker):
        return f"Error: efinance only supports A-share stocks. Got: {ticker}"

    return f"Error: efinance does not provide income statement data. Use akshare or other sources."
