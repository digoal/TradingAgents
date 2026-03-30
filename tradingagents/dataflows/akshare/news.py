"""
akshare news data implementation for A-share market.

Provides news articles and market-wide news for Chinese A-share stocks.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Annotated
import pandas as pd

from ..cn_ticker_utils import is_china_ticker


def get_akshare_news(
    ticker: Annotated[str, "ticker symbol (A-share only)"],
    start_date: Annotated[str, "start date YYYY-mm-dd"],
    end_date: Annotated[str, "end date YYYY-mm-dd"],
) -> str:
    """
    Get news articles for a specific A-share stock.

    Args:
        ticker: A-share ticker (will be converted to numeric code)
        start_date: Start date for news search
        end_date: End date for news search

    Returns:
        Formatted string with news articles
    """
    if not is_china_ticker(ticker):
        return f"Error: akshare news only supports A-share stocks. Got: {ticker}"

    try:
        import akshare as ak

        # Extract numeric code from ticker (remove sh/sz prefix if present)
        ticker_clean = ticker.strip().lower()
        if ticker_clean.startswith('sh') or ticker_clean.startswith('sz'):
            ticker_code = ticker_clean[2:].zfill(6)
        else:
            ticker_code = ticker_clean.zfill(6)

        # Get news data - use stock_news_em instead of stock_news
        news_df = ak.stock_news_em(symbol=ticker_code)

        if news_df is None or news_df.empty:
            return f"No news found for {ticker} between {start_date} and {end_date}"

        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Filter by date range
        if '发布时间' in news_df.columns:
            news_df['发布时间'] = pd.to_datetime(news_df['发布时间'])
            news_df = news_df[
                (news_df['发布时间'] >= start_dt) &
                (news_df['发布时间'] <= end_dt)
            ]
        elif '发布时间' not in news_df.columns and len(news_df.columns) > 0:
            # If no date column, just return top results
            pass

        if news_df.empty:
            return f"No news found for {ticker} between {start_date} and {end_date}"

        # Format output
        result = f"## {ticker} News from {start_date} to {end_date}:\n\n"

        for idx, row in news_df.head(20).iterrows():
            # Try to extract title and content from available columns
            title = row.iloc[0] if len(row) > 0 else "No title"
            content = row.iloc[1] if len(row) > 1 else ""

            result += f"### {title}\n"
            result += f"{content}\n\n"

        return result

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


def get_akshare_global_news(
    curr_date: Annotated[str, "current date YYYY-mm-dd"],
    look_back_days: Annotated[int, "days to look back"] = 7,
    limit: Annotated[int, "max articles"] = 10,
) -> str:
    """
    Get market-wide A-share news.

    Args:
        curr_date: Current date (used as reference point)
        look_back_days: Number of days to look back
        limit: Maximum number of articles to return

    Returns:
        Formatted string with market news
    """
    try:
        import akshare as ak

        # Get A-share market news from stock_news_main_cx
        news_df = ak.stock_news_main_cx()

        if news_df is None or news_df.empty:
            return "No A-share market news found"

        result = f"## A-Share Market News (last {look_back_days} days)\n\n"

        count = 0
        for idx, row in news_df.head(limit).iterrows():
            # stock_news_main_cx has columns: tag, summary, url
            tag = row.get('tag', 'General')
            summary = row.get('summary', '')
            url = row.get('url', '')

            result += f"### {tag}\n"
            result += f"Summary: {summary}\n"
            result += f"URL: {url}\n\n"

            count += 1

        if count == 0:
            return "No A-share market news found"

        return result

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error fetching global A-share news: {str(e)}"
