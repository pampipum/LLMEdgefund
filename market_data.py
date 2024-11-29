import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime, timedelta

class MarketDataService:
    def __init__(self):
        """Initialize the MarketDataService using yfinance"""
        pass
        
    def get_price_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical price data using yfinance
        
        Args:
            ticker (str): Stock ticker symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        try:
            # Add one day to end_date to ensure we include the end date in the data
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            end_date = end.strftime("%Y-%m-%d")
            
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Get historical data
            df = stock.history(
                start=start_date,
                end=end_date,
                interval="1d"
            )
            
            # If DataFrame is empty, raise an error
            if df.empty:
                raise ValueError(f"No data found for {ticker} between {start_date} and {end_date}")
            
            # Rename columns to match our existing code
            df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            }, inplace=True)
            
            # Ensure all required columns exist
            required_cols = ["open", "close", "high", "low", "volume"]
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching data from Yahoo Finance: {str(e)}")
    
    def calculate_trading_signals(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate trading signals including technical indicators
        
        Args:
            historical_data (pd.DataFrame): DataFrame with price data
            
        Returns:
            Dict[str, float]: Dictionary containing trading signals
        """
        try:
            if historical_data.empty:
                raise ValueError("No historical data provided")
            
            # Calculate SMAs
            historical_data['sma_5'] = historical_data["close"].rolling(window=5).mean()
            historical_data['sma_20'] = historical_data["close"].rolling(window=20).mean()
            historical_data['sma_50'] = historical_data["close"].rolling(window=50).mean()

            # Calculate volume metrics
            historical_data['avg_volume'] = historical_data['volume'].rolling(window=20).mean()

            # Calculate RSI
            delta = historical_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            historical_data['rsi'] = 100 - (100 / (1 + rs))

            # Calculate MACD
            exp1 = historical_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = historical_data['close'].ewm(span=26, adjust=False).mean()
            historical_data['macd'] = exp1 - exp2
            historical_data['macd_signal'] = historical_data['macd'].ewm(span=9, adjust=False).mean()

            # Calculate Volatility (20-day standard deviation of returns)
            historical_data['returns'] = historical_data['close'].pct_change()
            historical_data['volatility'] = historical_data['returns'].rolling(window=20).std() * np.sqrt(252)

            # Fill any NaN values with 0
            historical_data = historical_data.fillna(0)

            # Get the signals
            signals = {
                "current_price": historical_data["close"].iloc[-1],
                "sma_5": historical_data["sma_5"].iloc[-1],
                "sma_20": historical_data["sma_20"].iloc[-1],
                "sma_50": historical_data["sma_50"].iloc[-1],
                "volume": historical_data["volume"].iloc[-1],
                "avg_volume": historical_data["avg_volume"].iloc[-1],
                "rsi": historical_data["rsi"].iloc[-1],
                "macd": historical_data["macd"].iloc[-1],
                "macd_signal": historical_data["macd_signal"].iloc[-1],
                "volatility": historical_data["volatility"].iloc[-1]
            }
            
            return signals
            
        except Exception as e:
            raise Exception(f"Error calculating trading signals: {str(e)}")

    def get_additional_info(self, ticker: str) -> Dict[str, any]:
        """
        Get additional company information
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, any]: Dictionary containing company information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "beta": info.get("beta", 0),
                "pe_ratio": info.get("forwardPE", 0),
            }
        except:
            # Return empty dict if additional info cannot be fetched
            return {}