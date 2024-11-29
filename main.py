from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from market_data import MarketDataService
from agents import TradingAgents
from backtester import Backtester
import pandas as pd
from typing import Optional, List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float

class BacktestResults(BaseModel):
    portfolio_values: List[dict]
    trades: List[dict]
    final_value: float
    total_return: float
    sharpe_ratio: float

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Backtesting API"}

@app.post("/api/backtest", response_model=BacktestResults)
async def run_backtest(request: BacktestRequest):
    try:
        # Initialize services
        market_data_service = MarketDataService()
        trading_agents = TradingAgents()
        
        # Create backtester instance
        backtester = Backtester(
            market_data_service=market_data_service,
            trading_agents=trading_agents,
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital
        )
        
        # Run backtest
        backtester.run_backtest()
        results_df = backtester.analyze_performance()
        
        # Convert results to JSON-compatible format
        portfolio_values = results_df.reset_index().to_dict('records')
        trades = backtester.trades
        
        return {
            "portfolio_values": portfolio_values,
            "trades": trades,
            "final_value": float(results_df["Portfolio Value"].iloc[-1]),
            "total_return": float((results_df["Portfolio Value"].iloc[-1] - request.initial_capital) / request.initial_capital * 100),
            "sharpe_ratio": float(results_df["Daily Return"].mean() / results_df["Daily Return"].std() * (252 ** 0.5))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/supported-tickers")
async def get_supported_tickers():
    # This is a simplified list. You might want to expand it or fetch from a database
    return {
        "tickers": [
            "AAPL",
            "GOOGL",
            "MSFT",
            "AMZN",
            "META",
            "TSLA",
            "NVDA",
            "JPM",
            "V",
            "JNJ"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)