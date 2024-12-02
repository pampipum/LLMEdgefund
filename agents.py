from typing import Dict, Any
import os
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from market_data import MarketDataService

class TradingAgents:
    def __init__(self):
        """Initialize the trading agents with LangChain components"""
        self.llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        )
        self.market_data_service = MarketDataService()
        self.workflow = self._create_trading_workflow()

    def market_data_agent(self, state: MessagesState):
        """Agent responsible for gathering and preprocessing market data"""
        messages = state["messages"]
        params = messages[-1].additional_kwargs
        
        # Get the historical price data and signals
        df = self.market_data_service.get_price_data(
            params["ticker"], 
            params["lookback_start"], 
            params["current_date"]
        )
        signals = self.market_data_service.calculate_trading_signals(df)
        
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

    def quant_agent(self, state: MessagesState):
        """Agent that analyzes technical indicators and generates trading signals"""
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
        
        chain = summary_prompt | self.llm
        result = chain.invoke(state).content
        
        return {
            "messages": state["messages"] + [
                HumanMessage(content=result, name="quant_agent")
            ]
        }

    def risk_management_agent(self, state: MessagesState):
        """Agent that evaluates portfolio risk and sets position limits"""
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
        
        chain = risk_prompt | self.llm
        result = chain.invoke(state).content
        
        return {
            "messages": state["messages"] + [
                HumanMessage(content=result, name="risk_management")
            ]
        }

    def portfolio_management_agent(self, state: MessagesState):
        """Agent that makes final trading decisions and generates orders"""
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
        
        chain = portfolio_prompt | self.llm
        result = chain.invoke(state).content
        
        return {"messages": [HumanMessage(content=result, name="portfolio_manager")]}

    def _create_trading_workflow(self):
        """Create the trading agent workflow using StateGraph"""
        # Create the graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes for each agent
        workflow.add_node("market_data", self.market_data_agent)
        workflow.add_node("quant", self.quant_agent)
        workflow.add_node("risk", self.risk_management_agent)
        workflow.add_node("portfolio", self.portfolio_management_agent)
        
        # Define the workflow edges
        workflow.add_edge("market_data", "quant")
        workflow.add_edge("quant", "risk")
        workflow.add_edge("risk", "portfolio")
        workflow.add_edge("portfolio", END)
        
        # Set the entry point
        workflow.set_entry_point("market_data")
        
        return workflow.compile()

    def get_trading_decision(self, ticker: str, lookback_start: str, current_date: str, portfolio: Dict[str, float]) -> Dict[str, Any]:
        """
        Get a trading decision for the given ticker and portfolio state
        
        Args:
            ticker: Stock ticker symbol
            lookback_start: Start date for historical data analysis
            current_date: Current trading date
            portfolio: Current portfolio state (cash and stock holdings)
            
        Returns:
            Dict containing the trading decision
        """
        try:
            # Run the trading workflow
            final_state = self.workflow.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="Make a trading decision based on the market data.",
                            additional_kwargs={
                                "ticker": ticker,
                                "lookback_start": lookback_start,
                                "current_date": current_date,
                                "portfolio": portfolio
                            }
                        )
                    ]
                }
            )
            
            # Get the final decision
            decision = final_state["messages"][-1].content
            return self._parse_decision(decision)
            
        except Exception as e:
            print(f"Error getting trading decision: {e}")
            return {
                "action": "hold",
                "quantity": 0,
                "reasoning": "Error in decision making"
            }

    def _parse_decision(self, decision_str: str) -> Dict[str, Any]:
        """Parse the trading decision string into a structured format"""
        try:
            lines = decision_str.strip().split('\n')
            decision = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    decision[key.strip()] = value.strip()
            
            # Convert quantity to integer
            if 'quantity' in decision:
                try:
                    decision['quantity'] = int(float(decision['quantity']))
                except:
                    decision['quantity'] = 0
                    
            return decision
            
        except Exception as e:
            print(f"Error parsing decision: {e}")
            return {
                "action": "hold",
                "quantity": 0,
                "reasoning": "Error parsing decision"
            }