"""
A-share ticker utilities for converting between different formats.

This module provides utilities to detect and convert A-share (Chinese stock) ticker symbols
to formats required by various data providers like akshare and efinance.

A-share ticker formats:
- Pure number: 600000, 000001
- With prefix: sh600000, sz000001, SH600000, SZ000001

Target formats:
- akshare: 600000.SH, 000001.SZ
- efinance: 600000 (with market parameter)
"""

from typing import Tuple, Optional
import re


def is_china_ticker(ticker: str) -> bool:
    """
    Fast check if ticker is in A-share format.

    Args:
        ticker: Ticker symbol to check

    Returns:
        True if ticker appears to be an A-share stock code
    """
    if not ticker:
        return False

    ticker = ticker.strip().lower()

    # Check with prefix: sh600000, sz000001
    if ticker.startswith('sh') or ticker.startswith('sz'):
        if len(ticker) == 8 and ticker[2:].isdigit():
            return True

    # Check with yfinance suffix: 600000.ss, 600000.sh, 000001.sz, 000001.she
    if '.' in ticker:
        parts = ticker.split('.')
        if len(parts) == 2:
            code, suffix = parts
            if code.isdigit() and len(code) == 6:
                if suffix.lower() in ('ss', 'sha', 'sh', 'sz', 'she'):
                    return True

    # Check pure 6-digit number
    if re.match(r'^\d{6}$', ticker):
        return True

    return False


def normalize_cn_ticker(ticker: str) -> Tuple[str, str]:
    """
    Normalize A-share ticker to (market, code) tuple.

    Args:
        ticker: A-share ticker in any format (600000, sh600000, SZ000001, 600000.SH, 000001.SZ, etc.)

    Returns:
        Tuple of (market_code, stock_code)
        - market_code: "SH" for Shanghai, "SZ" for Shenzhen
        - stock_code: 6-digit stock code

    Raises:
        ValueError: If ticker format is not recognized or cannot determine market
    """
    if not ticker:
        raise ValueError("Empty ticker")

    ticker = ticker.strip()
    ticker_upper = ticker.upper()
    ticker_lower = ticker.lower()

    # Already with exchange suffix: 600000.SS, 600000.SH, 000001.SZ, 000001.SHE
    if '.' in ticker:
        parts = ticker.split('.')
        if len(parts) == 2:
            code, suffix = parts
            code = code.zfill(6)
            if suffix.upper() in ('SS', 'SHA', 'SH'):
                return ("SH", code)
            elif suffix.upper() in ('SZ', 'SHE', 'SZSE'):
                return ("SZ", code)

    # With prefix: sh600000, SZ000001
    if ticker_lower.startswith('sh') or ticker_lower.startswith('sz'):
        prefix = ticker_lower[:2]
        code = ticker_lower[2:].zfill(6)
        if prefix == 'sh':
            return ("SH", code)
        elif prefix == 'sz':
            return ("SZ", code)

    # Pure 6-digit number
    if re.match(r'^\d{6}$', ticker):
        code = ticker.zfill(6)
        # Shanghai: starts with 6 (main board) or 9 (B-share)
        if code.startswith('6') or code.startswith('9'):
            return ("SH", code)
        # Shenzhen: starts with 0, 1, 2, 3 (includes main board, SME board, ChiNext)
        elif code.startswith(('0', '1', '2', '3')):
            return ("SZ", code)
        else:
            raise ValueError(f"Cannot determine market for A-share code: {ticker}")

    raise ValueError(f"Unrecognized A-share ticker format: {ticker}")


def to_akshare_ticker(ticker: str) -> str:
    """
    Convert A-share ticker to akshare format.

    Akshare uses format: 600000.SH, 000001.SZ

    Args:
        ticker: A-share ticker in any format

    Returns:
        Ticker in akshare format (600000.SH or 000001.SZ)

    Raises:
        ValueError: If ticker is not a valid A-share format
    """
    market, code = normalize_cn_ticker(ticker)
    return f"{code}.{market}"


def to_efinance_ticker(ticker: str) -> str:
    """
    Convert A-share ticker to efinance format.

    Efinance uses just the 6-digit code with a separate market parameter.

    Args:
        ticker: A-share ticker in any format

    Returns:
        Ticker in efinance format (6-digit code)

    Raises:
        ValueError: If ticker is not a valid A-share format
    """
    market, code = normalize_cn_ticker(ticker)
    return code


def get_efinance_market(ticker: str) -> str:
    """
    Get efinance market parameter for A-share ticker.

    Args:
        ticker: A-share ticker in any format

    Returns:
        Market string for efinance: "SH" or "SZ"

    Raises:
        ValueError: If ticker is not a valid A-share format
    """
    market, _ = normalize_cn_ticker(ticker)
    return market


def detect_and_normalize(ticker: str) -> Tuple[Optional[str], str]:
    """
    Auto-detect ticker type and return (market, code) if A-share, or (None, original) if not.

    Args:
        ticker: Ticker symbol to check

    Returns:
        Tuple of (market_or_None, normalized_code)
        - For A-share: ("SH" or "SZ", 6-digit code)
        - For non A-share: (None, original ticker uppercased)
    """
    if is_china_ticker(ticker):
        try:
            market, code = normalize_cn_ticker(ticker)
            return (market, code)
        except ValueError:
            pass

    return (None, ticker.strip().upper())
