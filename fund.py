import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from typing import Dict, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from market_data import MarketDataService
from backtester import Backtester

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
)

def market_data_agent(state: MessagesState):
    """Responsible for gathering and preprocessing market data"""
    messages = state["messages"]
    params = messages[-1].additional_kwargs
    
    # Get market data service instance
    market_data = MarketDataService()
    
    # Get the historical price data and signals
    df = market_data.get_price_data(
        params["ticker"], 
        params["lookback_start"], 
        params["current_date"]
    )
    signals = market_data.calculate_trading_signals(df)
    
    message = HumanMessage(
        content=f"""
        Trading signals for {params['ticker']}:
        Current Price: ${signals['current_price']:.2f}
        5-day MA: ${signals['sma_5']:.2f}
        20-day MA: ${signals['sma_20']:.2f}
        50-day MA: ${signals['sma_50']:.2f}
        RSI: {signals['rsi']:.2f}
        MACD: {signals['macd']:.2f}
        MACD Signal: {signals['macd_signal']:.2f}
        Volatility: {signals['volatility']:.2f}
        """,
        name="market_data_agent",
        additional_kwargs={"signals": signals}
    )
    
    return {"messages": messages + [message]}

def quant_agent(state: MessagesState):
    """Analyzes technical indicators and generates trading signals"""
    last_message = state["messages"][-1]
    
    summary_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a hedge fund quant / technical analyst.
            Analyze the trading signals and provide a recommendation.
            Your response should be in this exact format:
            signal: bullish | bearish | neutral
            confidence: <number between 0 and 1>
            reasoning: brief explanation of your analysis"""
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            f"Based on these trading signals, provide your assessment:\n{last_message.content}"
        ),
    ])
    
    chain = summary_prompt | llm
    result = chain.invoke(state).content
    
    return {
        "messages": state["messages"] + [
            HumanMessage(content=result, name="quant_agent")
        ]
    }

def risk_management_agent(state: MessagesState):
    """Evaluates portfolio risk and sets position limits"""
    portfolio = state["messages"][0].additional_kwargs["portfolio"]
    last_message = state["messages"][-1]
    
    risk_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a risk management specialist.
            Evaluate portfolio exposure and recommend position sizing.
            Your response should be in this exact format:
            max_position_size: <number between 0 and 1>
            risk_score: <integer between 1 and 10>
            reasoning: brief explanation of your assessment"""
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            f"""Based on this analysis, provide your risk assessment.
            
            Analysis: {last_message.content}
            
            Portfolio:
            Cash: ${portfolio['cash']:.2f}
            Current Position: {portfolio['stock']} shares"""
        ),
    ])
    
    chain = risk_prompt | llm
    result = chain.invoke(state).content
    
    return {
        "messages": state["messages"] + [
            HumanMessage(content=result, name="risk_management")
        ]
    }

def portfolio_management_agent(state: MessagesState):
    """Makes final trading decisions and generates orders"""
    portfolio = state["messages"][0].additional_kwargs["portfolio"]
    last_message = state["messages"][-1]
    signals = state["messages"][1].additional_kwargs["signals"]
    
    portfolio_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a portfolio manager making final trading decisions.
            Provide your decision in this exact format:
            action: buy | sell | hold
            quantity: <positive integer>
            reasoning: brief explanation
            
            Rules:
            - Only buy if you have available cash
            - Only sell if you have shares to sell
            - The quantity must respect the max position size
            - Consider the current price for position sizing"""
        ),
        MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            f"""Make a trading decision based on:
            
            Risk Assessment: {last_message.content}
            
            Portfolio:
            Cash: ${portfolio['cash']:.2f}
            Current Position: {portfolio['stock']} shares
            Current Price: ${signals['current_price']:.2f}"""
        ),
    ])
    
    chain = portfolio_prompt | llm
    result = chain.invoke(state).content
    
    return {"messages": [HumanMessage(content=result, name="portfolio_manager")]}

def create_trading_workflow():
    """Create the trading agent workflow"""
    # Create the graph
    workflow = StateGraph(MessagesState)
    
    # Add nodes for each agent
    workflow.add_node("market_data", market_data_agent)
    workflow.add_node("quant", quant_agent)
    workflow.add_node("risk", risk_management_agent)
    workflow.add_node("portfolio", portfolio_management_agent)
    
    # Define the workflow edges
    workflow.add_edge("market_data", "quant")
    workflow.add_edge("quant", "risk")
    workflow.add_edge("risk", "portfolio")
    workflow.add_edge("portfolio", END)
    
    # Set the entry point
    workflow.set_entry_point("market_data")
    
    return workflow.compile()

def main():
    # Load configuration from environment
    ticker = os.getenv('TICKER', 'AAPL')
    start_date = os.getenv('START_DATE')
    end_date = os.getenv('END_DATE')
    initial_capital = float(os.getenv('INITIAL_CAPITAL', '100000'))
    
    # Create the trading workflow
    trading_app = create_trading_workflow()
    
    # Create backtester
    backtester = Backtester(
        market_data_service=MarketDataService(),
        trading_workflow=trading_app,
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