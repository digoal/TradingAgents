"""
akshare stock data implementation for A-share market.

Provides historical OHLCV data for Chinese A-share stocks using akshare library.
"""

from datetime import datetime
from typing import Annotated
import pandas as pd

from ..cn_ticker_utils import is_china_ticker, normalize_cn_ticker


def _akshare_retry(func, max_retries: int = 3):
    """Retry wrapper for akshare functions with exponential backoff."""
    import time

    last_error = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))  # Simple backoff
            continue
    raise last_error


def get_akshare_stock_online(
    symbol: Annotated[str, "ticker symbol (supports A-share like 600000, sh600000)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get A-share historical OHLCV data using akshare.

    Uses akshare.stock_zh_a_hist_tx() to retrieve daily historical data.
    This function uses Tencent's server (proxy.finance.qq.com) instead of
    eastmoney's push2his server, which may be blocked in some networks.

    Args:
        symbol: A-share ticker in any supported format (600000, sh600000, 000001.SZ, etc.)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        CSV string with columns: Date, Open, Close, High, Low, Volume, Turnover
    """
    # Validate date formats
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        return f"Error: Invalid date format. Use YYYY-MM-DD. Details: {e}"

    # Convert A-share ticker to Tencent format (sh600089, sz000001)
    if is_china_ticker(symbol):
        market, code = normalize_cn_ticker(symbol)
        if market == "SH":
            tx_symbol = f"sh{code}"
        else:
            tx_symbol = f"sz{code}"
    else:
        tx_symbol = symbol

    try:
        import akshare as ak

        # Use stock_zh_a_hist_tx which uses Tencent's server
        # instead of eastmoney's push2his server
        data = _akshare_retry(
            lambda: ak.stock_zh_a_hist_tx(
                symbol=tx_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust="qfq"  # Forward adjusted price
            )
        )

        if data is None or data.empty:
            return f"No data found for symbol '{symbol}' between {start_date} and {end_date}"

        # Rename columns from Tencent format to standard English names
        # stock_zh_a_hist_tx returns: date, open, close, high, low, amount
        column_mapping = {
            'date': 'Date',
            'open': 'Open',
            'close': 'Close',
            'high': 'High',
            'low': 'Low',
            'amount': 'Turnover',  # amount is in terms of money
            'volume': 'Volume',    # if volume column exists
        }

        # Only rename columns that exist
        rename_dict = {k: v for k, v in column_mapping.items() if k in data.columns}
        data = data.rename(columns=rename_dict)

        # Ensure Date column is in proper format
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')

        # Add Volume column if not present (Tencent API may not include it)
        if 'Volume' not in data.columns:
            data['Volume'] = ''

        # Add metadata header
        header = f"# Stock data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Source: akshare (Tencent)\n\n"

        return header + data.to_csv(index=False)

    except ImportError:
        return "Error: akshare library not installed. Install with: pip install akshare"
    except Exception as e:
        return f"Error retrieving stock data for {symbol}: {str(e)}"
