"""
akshare technical indicators implementation for A-share market.

Technical indicators are calculated locally using stockstats after fetching data via akshare.
"""

from datetime import datetime, timedelta
from typing import Annotated
import pandas as pd
from io import StringIO

from ..cn_ticker_utils import is_china_ticker
from ..stockstats_utils import StockstatsUtils, _clean_dataframe
from .stock import get_akshare_stock_online


# Indicator descriptions (consistent with y_finance.py)
INDICATOR_DESCRIPTIONS = {
    "close_50_sma": (
        "50 SMA: A medium-term trend indicator. "
        "Usage: Identify trend direction and serve as dynamic support/resistance. "
        "Tips: It lags price; combine with faster indicators for timely signals."
    ),
    "close_200_sma": (
        "200 SMA: A long-term trend benchmark. "
        "Usage: Confirm overall market trend and identify golden/death cross setups. "
        "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
    ),
    "close_10_ema": (
        "10 EMA: A responsive short-term average. "
        "Usage: Capture quick shifts in momentum and potential entry points. "
        "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
    ),
    "macd": (
        "MACD: Computes momentum via differences of EMAs. "
        "Usage: Look for crossovers and divergence as signals of trend changes. "
        "Tips: Confirm with other indicators in low-volatility or sideways markets."
    ),
    "macds": (
        "MACD Signal: An EMA smoothing of the MACD line. "
        "Usage: Use crossovers with the MACD line to trigger trades. "
        "Tips: Should be part of a broader strategy to avoid false positives."
    ),
    "macdh": (
        "MACD Histogram: Shows the gap between the MACD line and its signal. "
        "Usage: Visualize momentum strength and spot divergence early. "
        "Tips: Can be volatile; complement with additional filters in fast-moving markets."
    ),
    "rsi": (
        "RSI: Measures momentum to flag overbought/oversold conditions. "
        "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
        "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
    ),
    "boll": (
        "Bollinger Middle: A 20 SMA serving as a basis for Bollinger Bands. "
        "Usage: Acts as a dynamic benchmark for price movement. "
        "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
    ),
    "boll_ub": (
        "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
        "Usage: Signals potential overbought conditions and breakout zones. "
        "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
    ),
    "boll_lb": (
        "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
        "Usage: Indicates potential oversold conditions. "
        "Tips: Use additional analysis to avoid false reversal signals."
    ),
    "atr": (
        "ATR: Averages true range to measure volatility. "
        "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
        "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
    ),
    "vwma": (
        "VWMA: A moving average weighted by volume. "
        "Usage: Confirm trends by integrating price action with volume data. "
        "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
    ),
    "mfi": (
        "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
        "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
        "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
    ),
}


SUPPORTED_INDICATORS = list(INDICATOR_DESCRIPTIONS.keys())


def get_akshare_indicators_window(
    symbol: Annotated[str, "ticker symbol (supports A-share)"],
    indicator: Annotated[str, "technical indicator name"],
    curr_date: Annotated[str, "The current trading date YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """
    Get technical indicator values for A-share stock using akshare data + stockstats calculation.

    Args:
        symbol: A-share ticker
        indicator: Technical indicator name (e.g., 'rsi', 'macd', 'boll')
        curr_date: Current trading date
        look_back_days: Number of days to look back

    Returns:
        Formatted string with indicator values and description
    """
    # Validate indicator
    if indicator not in SUPPORTED_INDICATORS:
        return (
            f"Error: Indicator '{indicator}' not supported. "
            f"Available indicators: {list(SUPPORTED_INDICATORS)}"
        )

    # Calculate date range
    try:
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    except ValueError:
        return f"Error: Invalid date format '{curr_date}'. Use YYYY-MM-DD."

    # Get extra days for indicator calculation (some indicators need more history)
    start_date_dt = curr_date_dt - timedelta(days=look_back_days + 100)
    start_date = start_date_dt.strftime("%Y-%m-%d")

    # Fetch stock data using akshare
    data_str = get_akshare_stock_online(symbol, start_date, curr_date)

    if data_str.startswith("Error") or data_str.startswith("No data"):
        return data_str

    try:
        # Parse CSV data (skip header lines)
        lines = data_str.split('\n')
        data_lines = [l for l in lines if l and not l.startswith('#')]

        if not data_lines:
            return f"Error: No data available for {symbol}"

        data = pd.read_csv(StringIO('\n'.join(data_lines)))

        if data.empty:
            return f"Error: No data available for {symbol}"

        # Clean and prepare for stockstats
        data = _clean_dataframe(data)

        # Calculate the specific indicator
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol="AKSHARE",
            indicator=indicator,
            curr_date=curr_date,
            data=data  # Pass the pre-fetched data
        )

        # Build result string for the requested window
        result_lines = [f"## {indicator} values from {start_date} to {curr_date}:\n"]

        # Get values for look_back_days window
        current_dt = curr_date_dt
        values = []
        while current_dt >= start_date_dt:
            date_str = current_dt.strftime('%Y-%m-%d')

            # Get value for this date from stockstats
            val = StockstatsUtils.get_stock_stats(
                symbol="AKSHARE",
                indicator=indicator,
                curr_date=date_str,
                data=data
            )

            if val and val != "N/A":
                values.append(f"{date_str}: {val}")
            else:
                values.append(f"{date_str}: N/A")

            current_dt = current_dt - timedelta(days=1)

        result_lines.extend(values)
        result_lines.append("\n")
        result_lines.append(INDICATOR_DESCRIPTIONS.get(indicator, "No description available."))

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error calculating indicator for {symbol}: {str(e)}"
