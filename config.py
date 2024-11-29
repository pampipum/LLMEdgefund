# config.py
import os
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_variable(var_name: str, default: Any = None) -> str:
    """Get an environment variable or raise an exception if it's not set and no default is provided."""
    value = os.getenv(var_name, default)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

CONFIG: Dict[str, Any] = {
    "TICKER": get_env_variable("TICKER", "AAPL"),
    "START_DATE": get_env_variable("START_DATE", "2024-01-01"),
    "END_DATE": get_env_variable("END_DATE", datetime.now().strftime("%Y-%m-%d")),
    "INITIAL_CAPITAL": float(get_env_variable("INITIAL_CAPITAL", "100000")),
    "OPENAI_MODEL": get_env_variable("OPENAI_MODEL", "gpt-4"),
}

# Validate required API key for OpenAI
get_env_variable("OPENAI_API_KEY")