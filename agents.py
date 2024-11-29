from typing import Dict, Any
import os
from openai import OpenAI
import json

class TradingAgents:
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo')
        
    def market_data_agent(self, signals: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Use GPT-4 to analyze market data and technical indicators."""
        try:
            system_prompt = """You are a hedge fund technical analyst.
            Your job is to analyze market data and technical indicators to determine market trends.
            You must provide your analysis in this exact format:
            price_trend: bullish | bearish | neutral
            volume_trend: high | low | neutral
            risk_level: high | medium | low
            reasoning: brief explanation of your analysis"""

            user_prompt = f"""Analyze these technical indicators for {ticker}:
            Price: ${signals['current_price']:.2f}
            5-day MA: ${signals['sma_5']:.2f}
            20-day MA: ${signals['sma_20']:.2f}
            RSI: {signals['rsi']:.2f}
            MACD: {signals['macd']:.2f}
            MACD Signal: {signals['macd_signal']:.2f}

            Provide your analysis in the specified format."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response into a structured format
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
            analysis = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip()] = value.strip()
            
            analysis['ticker'] = ticker
            return analysis
            
        except Exception as e:
            print(f"Error in market_data_agent: {e}")
            return {
                "ticker": ticker,
                "price_trend": "neutral",
                "volume_trend": "neutral",
                "risk_level": "medium",
                "reasoning": "Error in analysis"
            }
        
    def quant_agent(self, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes technical indicators and generates trading signals"""
        try:
            system_prompt = """You are a hedge fund quant / technical analyst.
            You are given trading signals for a stock.
            Analyze the signals and provide a recommendation.
            You must provide your output in this exact format:
            signal: bullish | bearish | neutral
            confidence: <float between 0 and 1>
            reasoning: brief explanation of your decision"""

            user_prompt = f"""Based on this market analysis, provide your trading signal:
            Price Trend: {market_analysis.get('price_trend')}
            Risk Level: {market_analysis.get('risk_level')}
            Analysis: {market_analysis.get('reasoning')}

            Provide your recommendation in the specified format."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response into a structured format
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
            analysis = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip()] = value.strip()
            
            return analysis
            
        except Exception as e:
            print(f"Error in quant_agent: {e}")
            return {
                "signal": "neutral",
                "confidence": "0.0",
                "reasoning": "Error in analysis"
            }
        
    def risk_management_agent(self, quant_analysis: Dict[str, Any], portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates portfolio risk and sets position limits"""
        try:
            system_prompt = """You are a risk management specialist.
            Your job is to evaluate portfolio exposure and recommend position sizing.
            You must provide your output in this exact format:
            max_position_size: <float between 0 and 1>
            risk_score: <integer between 1 and 10>
            reasoning: brief explanation of your assessment"""

            user_prompt = f"""Based on this analysis and portfolio, provide your risk assessment:
            Trading Signal: {quant_analysis.get('signal')}
            Confidence: {quant_analysis.get('confidence')}
            
            Portfolio:
            Cash: ${portfolio['cash']:.2f}
            Current Position: {portfolio['stock']} shares

            Provide your assessment in the specified format."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response into a structured format
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
            analysis = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip()] = value.strip()
            
            return analysis
            
        except Exception as e:
            print(f"Error in risk_management_agent: {e}")
            return {
                "max_position_size": "0.0",
                "risk_score": "5",
                "reasoning": "Error in risk assessment"
            }
        
    def portfolio_management_agent(self, risk_analysis: Dict[str, Any], portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Makes final trading decisions and generates orders"""
        try:
            system_prompt = """You are a portfolio manager making final trading decisions.
            Your job is to make a trading decision based on the risk management data.
            You must provide your output in this exact format:
            action: buy | sell | hold
            quantity: <positive integer>
            reasoning: brief explanation of your decision
            
            Only buy if there is available cash.
            Only sell if there are shares in the portfolio.
            The quantity must respect the max position size."""

            user_prompt = f"""Based on this risk assessment, make your trading decision:
            Max Position Size: {risk_analysis.get('max_position_size')}
            Risk Score: {risk_analysis.get('risk_score')}
            
            Portfolio:
            Cash: ${portfolio['cash']:.2f}
            Current Position: {portfolio['stock']} shares

            Provide your decision in the specified format."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            # Parse the response into a structured format
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
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
            print(f"Error in portfolio_management_agent: {e}")
            return {
                "action": "hold",
                "quantity": 0,
                "reasoning": "Error in decision making"
            }