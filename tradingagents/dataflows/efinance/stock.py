"""
efinance stock data implementation for A-share market.

Provides historical OHLCV data for Chinese A-share stocks using efinance library.
"""

from datetime import datetime
from typing import Annotated
import pandas as pd

from ..cn_ticker_utils import (
    to_efinance_ticker,
    get_efinance_market,
    is_china_ticker,
)


def get_efinance_stock_online(
    symbol: Annotated[str, "ticker symbol (supports A-share like 600000, sh600000)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Get A-share historical OHLCV data using efinance.

    Uses efinance.get_quote_history() to retrieve daily historical data.

    Args:
        symbol: A-share ticker in any supported format (600000, sh600000, etc.)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        CSV string with columns: Date, Open, Close, High, Low, Volume, Turnover, etc.
    """
    # Validate date formats
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        return f"Error: Invalid date format. Use YYYY-MM-DD. Details: {e}"

    # Validate and convert ticker
    if not is_china_ticker(symbol):
        return f"Error: efinance only supports A-share stocks. Got: {symbol}"

    try:
        code = to_efinance_ticker(symbol)
        market = get_efinance_market(symbol)
    except ValueError as e:
        return f"Error: {str(e)}"

    try:
        import efinance as ef

        # Remove dashes for efinance
        start_str = start_date.replace("-", "")
        end_str = end_date.replace("-", "")

        # efinance.stock.get_quote_history() accepts stock_codes and date range
        # Returns dict: {'600519': DataFrame}
        result = ef.stock.get_quote_history(
            stock_codes=[code],
            beg=start_str,
            end=end_str,
            fqt=1  # Forward adjusted price (前复权)
        )

        # Handle dict return type
        if isinstance(result, dict):
            if code not in result:
                # Try without zero-padding
                code_nopad = code.lstrip('0')
                if code_nopad in result:
                    data = result[code_nopad]
                else:
                    return f"No data found for {symbol} between {start_date} and {end_date}"
            else:
                data = result[code]
        else:
            data = result

        if data is None or data.empty:
            return f"No data found for {symbol} between {start_date} and {end_date}"

        # Rename columns from Chinese to English for consistency
        column_mapping = {
            '日期': 'Date',
            '股票代码': 'Code',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '成交额': 'Turnover',
            '振幅': 'Amplitude',
            '涨跌幅': 'Pct_Change',
            '涨跌额': 'Change',
            '换手率': 'Turnover_Rate',
        }

        rename_dict = {k: v for k, v in column_mapping.items() if k in data.columns}
        data = data.rename(columns=rename_dict)

        # Ensure Date column is in proper format
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date']).dt.strftime('%Y-%m-%d')

        # Add metadata header
        header = f"# Stock data for {symbol} from {start_date} to {end_date}\n"
        header += f"# Total records: {len(data)}\n"
        header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# Source: efinance\n\n"

        return header + data.to_csv(index=False)

    except ImportError:
        return "Error: efinance library not installed. Install with: pip install efinance"
    except Exception as e:
        return f"Error retrieving stock data for {symbol}: {str(e)}"
