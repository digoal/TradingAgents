import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5.2",
    "quick_think_llm": "gpt-5-mini",
    "backend_url": "https://api.openai.com/v1",
    # Provider-specific thinking configuration
    "google_thinking_level": None,      # "high", "minimal", etc.
    "openai_reasoning_effort": None,    # "medium", "high", "low"
    "anthropic_effort": None,           # "high", "medium", "low"
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    # Available vendors: yfinance, alpha_vantage, akshare, efinance
    # For A-share stocks, akshare and efinance are automatically prioritized
    "data_vendors": {
        "core_stock_apis": "yfinance,akshare,efinance",       # Options: alpha_vantage, yfinance, akshare, efinance
        "technical_indicators": "yfinance,akshare",           # Options: alpha_vantage, yfinance, akshare
        "fundamental_data": "yfinance,akshare,efinance",      # Options: alpha_vantage, yfinance, akshare, efinance
        "news_data": "yfinance,akshare",                      # Options: alpha_vantage, yfinance, akshare
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
    },
}
