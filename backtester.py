import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from datetime import datetime, timedelta
from market_data import MarketDataService
from langchain_core.messages import HumanMessage

class Backtester:
    def __init__(
        self,
        market_data_service: MarketDataService,
        trading_workflow: Any,
        ticker: str,
        start_date: str,
        end_date: str,
        initial_capital: float
    ):
        self.market_data_service = market_data_service
        self.trading_workflow = trading_workflow
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.portfolio = {"cash": initial_capital, "stock": 0}
        self.portfolio_values: List[Dict[str, Any]] = []
        self.trades: List[Dict[str, Any]] = []
        self.benchmark_values: List[Dict[str, Any]] = []
        
    def parse_trading_decision(self, result: str) -> tuple:
        """Parse the trading decision from the agent's output"""
        try:
            lines = result.strip().split('\n')
            decision = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    decision[key.strip()] = value.strip()
            
            action = decision.get('action', 'hold')
            try:
                quantity = int(decision.get('quantity', '0'))
            except:
                quantity = 0
                
            return action, quantity
            
        except Exception as e:
            print(f"Error parsing trading decision: {e}")
            return "hold", 0
        
    def execute_trade(self, action: str, quantity: int, current_price: float) -> int:
        """Execute a trade based on the given action and quantity."""
        if action == "buy" and quantity > 0:
            cost = quantity * current_price
            if cost <= self.portfolio["cash"]:
                self.portfolio["stock"] += quantity
                self.portfolio["cash"] -= cost
                self.trades.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "action": "buy",
                    "quantity": quantity,
                    "price": current_price,
                    "total": cost
                })
                return quantity
                
            max_quantity = int(self.portfolio["cash"] // current_price)
            if max_quantity > 0:
                self.portfolio["stock"] += max_quantity
                self.portfolio["cash"] -= max_quantity * current_price
                self.trades.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "action": "buy",
                    "quantity": max_quantity,
                    "price": current_price,
                    "total": max_quantity * current_price
                })
                return max_quantity
                
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, self.portfolio["stock"])
            if quantity > 0:
                proceeds = quantity * current_price
                self.portfolio["cash"] += proceeds
                self.portfolio["stock"] -= quantity
                self.trades.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "action": "sell",
                    "quantity": quantity,
                    "price": current_price,
                    "total": proceeds
                })
                return quantity
                
        return 0
        
    def simulate_buy_and_hold(self, price_data: pd.DataFrame) -> None:
        """Simulate a buy and hold strategy for comparison"""
        initial_price = price_data['close'].iloc[0]
        shares = int(self.initial_capital / initial_price)
        remaining_cash = self.initial_capital - (shares * initial_price)
        
        for date, row in price_data.iterrows():
            current_value = shares * row['close'] + remaining_cash
            self.benchmark_values.append({
                "Date": date,
                "Portfolio Value": current_value
            })
        
    def run_backtest(self):
        """Run the backtest simulation."""
        # Get complete price data for buy & hold simulation
        complete_data = self.market_data_service.get_price_data(
            self.ticker, self.start_date, self.end_date
        )
        self.simulate_buy_and_hold(complete_data)
        
        dates = pd.date_range(self.start_date, self.end_date, freq="B")
        
        print("\nStarting backtest...")
        print(f"{'Date':<12} {'Action':<6} {'Quantity':>8} {'Price':>8} {'Cash':>12} {'Stock':>8} {'Total Value':>12}")
        print("-" * 70)
        
        for current_date in dates:
            try:
                lookback_start = (current_date - timedelta(days=30)).strftime("%Y-%m-%d")
                current_date_str = current_date.strftime("%Y-%m-%d")
                
                # Run the trading workflow
                final_state = self.trading_workflow.invoke(
                    {
                        "messages": [
                            HumanMessage(
                                content="Make a trading decision based on the market data.",
                                additional_kwargs={
                                    "ticker": self.ticker,
                                    "lookback_start": lookback_start,
                                    "current_date": current_date_str,
                                    "portfolio": self.portfolio
                                }
                            )
                        ]
                    }
                )
                
                # Get the final decision
                decision = final_state["messages"][-1].content
                action, quantity = self.parse_trading_decision(decision)
                
                # Get current price
                df = self.market_data_service.get_price_data(
                    self.ticker, current_date_str, current_date_str
                )
                current_price = df['close'].iloc[-1]
                
                # Execute the trade
                executed_quantity = self.execute_trade(action, quantity, current_price)
                
                # Calculate total value
                total_value = self.portfolio["cash"] + self.portfolio["stock"] * current_price
                
                self.portfolio_values.append({
                    "Date": current_date,
                    "Portfolio Value": total_value,
                    "Cash": self.portfolio["cash"],
                    "Stock": self.portfolio["stock"],
                    "Stock Price": current_price
                })
                
                print(
                    f"{current_date_str:<12} {action:<6} {executed_quantity:>8} "
                    f"{current_price:>8.2f} {self.portfolio['cash']:>12.2f} "
                    f"{self.portfolio['stock']:>8} {total_value:>12.2f}"
                )
                
            except Exception as e:
                print(f"Error on {current_date_str}: {str(e)}")
                continue
        
    def analyze_performance(self) -> pd.DataFrame:
        """Analyze the backtest performance."""
        if not self.portfolio_values:
            raise ValueError("No portfolio values to analyze. Run backtest first.")
            
        # Create DataFrames for both strategies
        strategy_df = pd.DataFrame(self.portfolio_values).set_index("Date")
        benchmark_df = pd.DataFrame(self.benchmark_values).set_index("Date")
        
        # Calculate returns for both strategies
        strategy_df["Daily Return"] = strategy_df["Portfolio Value"].pct_change()
        benchmark_df["Daily Return"] = benchmark_df["Portfolio Value"].pct_change()
        
        # Calculate performance metrics for strategy
        strategy_total_return = (
            strategy_df["Portfolio Value"].iloc[-1] - self.initial_capital
        ) / self.initial_capital
        
        benchmark_total_return = (
            benchmark_df["Portfolio Value"].iloc[-1] - self.initial_capital
        ) / self.initial_capital
        
        # Calculate risk metrics for both strategies
        risk_free_rate = 0.01  # 1% annual risk-free rate
        
        def calculate_sharpe(returns):
            mean_daily_return = returns.mean()
            std_daily_return = returns.std()
            return ((mean_daily_return - risk_free_rate/252) / std_daily_return) * (252 ** 0.5)
            
        strategy_sharpe = calculate_sharpe(strategy_df["Daily Return"].dropna())
        benchmark_sharpe = calculate_sharpe(benchmark_df["Daily Return"].dropna())
        
        # Calculate maximum drawdown for both strategies
        def calculate_max_drawdown(portfolio_values):
            rolling_max = portfolio_values.cummax()
            drawdowns = portfolio_values / rolling_max - 1
            return drawdowns.min()
            
        strategy_max_drawdown = calculate_max_drawdown(strategy_df["Portfolio Value"])
        benchmark_max_drawdown = calculate_max_drawdown(benchmark_df["Portfolio Value"])
        
        # Print performance comparison
        print("\nPerformance Comparison:")
        print("-" * 50)
        print("Strategy Metrics:")
        print(f"Total Return: {strategy_total_return * 100:.2f}%")
        print(f"Sharpe Ratio: {strategy_sharpe:.2f}")
        print(f"Maximum Drawdown: {strategy_max_drawdown * 100:.2f}%")
        print(f"Final Value: ${strategy_df['Portfolio Value'].iloc[-1]:,.2f}")
        print("\nBuy & Hold Metrics:")
        print(f"Total Return: {benchmark_total_return * 100:.2f}%")
        print(f"Sharpe Ratio: {benchmark_sharpe:.2f}")
        print(f"Maximum Drawdown: {benchmark_max_drawdown * 100:.2f}%")
        print(f"Final Value: ${benchmark_df['Portfolio Value'].iloc[-1]:,.2f}")
        
        # Plot performance comparison
        plt.figure(figsize=(12, 6))
        strategy_df["Portfolio Value"].plot(
            label="AI Strategy", 
            color='blue'
        )
        benchmark_df["Portfolio Value"].plot(
            label="Buy & Hold", 
            color='green',
            alpha=0.7
        )
        
        plt.title(f"Portfolio Value Over Time - {self.ticker}")
        plt.grid(True)
        plt.ylabel("Portfolio Value ($)")
        plt.xlabel("Date")
        plt.legend()
        
        # Add trade markers
        for trade in self.trades:
            date = pd.to_datetime(trade["date"])
            if date in strategy_df.index:
                color = 'g' if trade["action"] == "buy" else 'r'
                marker = '^' if trade["action"] == "buy" else 'v'
                plt.plot(
                    date, 
                    strategy_df.loc[date, "Portfolio Value"],
                    marker=marker,
                    color=color,
                    markersize=10
                )
        
        plt.show()
        
        # Print trade summary
        if self.trades:
            print("\nTrade Summary:")
            trades_df = pd.DataFrame(self.trades)
            print(trades_df.to_string(index=False))
        
        return strategy_df