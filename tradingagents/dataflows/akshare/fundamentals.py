"""
akshare fundamental data implementation for A-share market.

Provides company fundamentals, balance sheet, cash flow, and income statement data.
Uses Sina interface as primary source, eastmoney as fallback.
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


def _get_stock_code(ticker: str) -> str:
    """Extract 6-digit stock code from ticker."""
    if is_china_ticker(ticker):
        _, code = normalize_cn_ticker(ticker)
        return code
    return ticker


def _get_akshare_fundamentals_sina(ticker: str) -> str:
    """Get company fundamentals via Sina interface."""
    code = _get_stock_code(ticker)
    import akshare as ak

    # Get company name from the all-stocks table
    try:
        all_stocks = ak.stock_info_a_code_name()
        if all_stocks is not None and not all_stocks.empty:
            row = all_stocks[all_stocks.iloc[:, 0].astype(str) == code]
            if not row.empty:
                company_name = row.iloc[0, 1]
                name_line = f"公司名称: {company_name}"
            else:
                name_line = f"公司代码: {code}"
        else:
            name_line = f"公司代码: {code}"
    except Exception:
        name_line = f"公司代码: {code}"

    # Try to get brief info from income statement
    try:
        income = ak.stock_financial_report_sina(stock=code, symbol='利润表')
        if income is not None and not income.empty:
            latest = income.iloc[0]
            lines = [name_line]
            key_metrics = [
                ('报告日', '报告期'),
                ('营业总收入', '营业总收入'),
                ('营业收入', '营业收入'),
                ('净利润', '净利润'),
            ]
            for col_key, label in key_metrics:
                if col_key in latest.index:
                    val = latest[col_key]
                    if pd.notna(val):
                        if col_key == '报告日':
                            lines.append(f"{label}: {val}")
                        else:
                            lines.append(f"{label}: {val:,.2f}" if isinstance(val, (int, float)) else f"{label}: {val}")
            return "# Company Fundamentals for " + code + "\n" + "\n".join(lines)
    except Exception:
        pass

    return f"# Company Fundamentals for {code}\n{name_line}\n(No detailed fundamental data available)"


def _get_balance_sheet_sina(ticker: str) -> pd.DataFrame | None:
    """Get balance sheet via Sina interface."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        df = ak.stock_financial_report_sina(stock=code, symbol='资产负债表')
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    return None


def _get_income_statement_sina(ticker: str) -> pd.DataFrame | None:
    """Get income statement via Sina interface."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        df = ak.stock_financial_report_sina(stock=code, symbol='利润表')
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    return None


def _get_cash_flow_sina(ticker: str) -> pd.DataFrame | None:
    """Get cash flow statement via Sina interface."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        df = ak.stock_financial_report_sina(stock=code, symbol='现金流量表')
        if df is not None and not df.empty:
            return df
    except Exception:
        pass
    return None


def _get_balance_sheet_em(ticker: str, freq: str) -> pd.DataFrame | None:
    """Get balance sheet via eastmoney interface (fallback)."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        if freq.lower() == 'quarterly':
            return ak.stock_balance_sheet_by_report_em(symbol=code)
        else:
            return ak.stock_balance_sheet_by_yearly_em(symbol=code)
    except Exception:
        pass
    return None


def _get_cash_flow_em(ticker: str, freq: str) -> pd.DataFrame | None:
    """Get cash flow via eastmoney interface (fallback)."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        if freq.lower() == 'quarterly':
            return ak.stock_cash_flow_sheet_by_quarterly_em(symbol=code)
        else:
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=code)
    except Exception:
        pass
    return None


def _get_income_statement_em(ticker: str, freq: str) -> pd.DataFrame | None:
    """Get income statement via eastmoney interface (fallback)."""
    code = _get_stock_code(ticker)
    import akshare as ak

    try:
        if freq.lower() == 'quarterly':
            return ak.stock_profit_sheet_by_quarterly_em(symbol=code)
        else:
            return ak.stock_profit_sheet_by_yearly_em(symbol=code)
    except Exception:
        pass
    return None


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
    if not is_china_ticker(ticker):
        return f"Error: get_akshare_fundamentals only supports A-share stocks. Got: {ticker}"

    try:
        import akshare as ak

        # Try eastmoney individual info first
        code = _get_stock_code(ticker)
        try:
            info = ak.stock_individual_info_em(symbol=code)
            if info is not None and not info.empty:
                lines = []
                for _, row in info.iterrows():
                    if len(row) >= 2:
                        lines.append(f"{row.iloc[0]}: {row.iloc[1]}")
                header = f"# Company Fundamentals for {code}\n"
                header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += f"# Source: akshare (eastmoney)\n\n"
                return header + "\n".join(lines)
        except Exception:
            pass

        # Fallback to Sina-based fundamentals
        return _get_akshare_fundamentals_sina(ticker)

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
    if not is_china_ticker(ticker):
        return f"Error: get_akshare_balance_sheet only supports A-share stocks. Got: {ticker}"

    code = _get_stock_code(ticker)

    try:
        import akshare as ak

        # Try Sina first (more reliable)
        data = _get_balance_sheet_sina(ticker)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Balance Sheet ({freq})")

        # Fallback to eastmoney
        data = _get_balance_sheet_em(ticker, freq)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Balance Sheet ({freq})")

        return f"No balance sheet data found for {code}"

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving balance sheet for {code}: {str(e)}"


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
    if not is_china_ticker(ticker):
        return f"Error: get_akshare_cashflow only supports A-share stocks. Got: {ticker}"

    code = _get_stock_code(ticker)

    try:
        import akshare as ak

        # Try Sina first (more reliable)
        data = _get_cash_flow_sina(ticker)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Cash Flow ({freq})")

        # Fallback to eastmoney
        data = _get_cash_flow_em(ticker, freq)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Cash Flow ({freq})")

        return f"No cash flow data found for {code}"

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving cash flow for {code}: {str(e)}"


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
    if not is_china_ticker(ticker):
        return f"Error: get_akshare_income_statement only supports A-share stocks. Got: {ticker}"

    code = _get_stock_code(ticker)

    try:
        import akshare as ak

        # Try Sina first (more reliable)
        data = _get_income_statement_sina(ticker)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Income Statement ({freq})")

        # Fallback to eastmoney
        data = _get_income_statement_em(ticker, freq)
        if data is not None and not data.empty:
            return _format_df_to_csv(data, code, f"Income Statement ({freq})")

        return f"No income statement data found for {code}"

    except ImportError:
        return "Error: akshare library not installed"
    except Exception as e:
        return f"Error retrieving income statement for {code}: {str(e)}"
