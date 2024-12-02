import os
from dotenv import load_dotenv
import logging
from datetime import datetime  # Correct import for datetime
from market_data import MarketDataService
from backtester import Backtester
from agents import TradingAgents

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Disable OpenAI API request logging
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)

def validate_dates(start_date: str, end_date: str) -> tuple[str, str]:
    """Validate and format dates"""
    try:
        # Parse dates to ensure they're valid
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Ensure end date is after start date
        if end < start:
            logging.warning("End date is before start date! Using default dates.")
            return None, None
            
        return start_date, end_date
    except (ValueError, TypeError):
        logging.warning("Invalid date format in environment variables! Using default dates.")
        return None, None

def main():
    # Load configuration from environment
    ticker = os.getenv('TICKER', 'AAPL')
    start_date = os.getenv('START_DATE')
    end_date = os.getenv('END_DATE')
    initial_capital = float(os.getenv('INITIAL_CAPITAL', '100000'))
    
    # Validate dates
    start_date, end_date = validate_dates(start_date, end_date)
    
    if not start_date or not end_date:
        logging.error("Invalid or missing dates in .env file!")
        return
    
    # Create trading agents with workflow
    trading_agents = TradingAgents()
    
    # Create backtester
    backtester = Backtester(
        market_data_service=MarketDataService(),
        trading_workflow=trading_agents.workflow,
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )
    
    # Run backtest
    backtester.run_backtest()
    results_df = backtester.analyze_performance()

if __name__ == "__main__":
    main()