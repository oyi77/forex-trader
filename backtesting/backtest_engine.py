"""
Comprehensive Backtesting Engine for Forex Trading Bot
Validates trading strategies using historical data with detailed performance metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
import logging
from dataclasses import dataclass, field
from enum import Enum
import json
import warnings
warnings.filterwarnings('ignore')

class BacktestMode(Enum):
    VECTORIZED = "vectorized"
    EVENT_DRIVEN = "event_driven"
    WALK_FORWARD = "walk_forward"

@dataclass
class Trade:
    """Individual trade record"""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # 'buy' or 'sell'
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    commission: float
    swap: float
    duration_hours: float
    strategy: str
    confidence: float
    max_favorable_excursion: float = 0.0
    max_adverse_excursion: float = 0.0

@dataclass
class BacktestResults:
    """Comprehensive backtest results"""
    # Basic metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # P&L metrics
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    profit_factor: float = 0.0
    
    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration: int = 0
    var_95: float = 0.0
    cvar_95: float = 0.0
    
    # Performance ratios
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Trading metrics
    avg_trade_duration: float = 0.0
    trades_per_month: float = 0.0
    expectancy: float = 0.0
    
    # Equity curve data
    equity_curve: pd.Series = field(default_factory=pd.Series)
    drawdown_curve: pd.Series = field(default_factory=pd.Series)
    
    # Trade details
    trades: List[Trade] = field(default_factory=list)
    
    # Monthly/yearly breakdown
    monthly_returns: pd.Series = field(default_factory=pd.Series)
    yearly_returns: pd.Series = field(default_factory=pd.Series)

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.0001, 
                 swap_rate: float = 0.0, slippage: float = 0.0001):
        self.initial_capital = initial_capital
        self.commission = commission  # Commission per trade (as percentage)
        self.swap_rate = swap_rate    # Daily swap rate
        self.slippage = slippage      # Slippage per trade
        
        self.logger = logging.getLogger('BacktestEngine')
        
        # Backtest state
        self.current_capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_history = []
        self.timestamp_history = []
        
        self.logger.info("Backtest Engine initialized")
    
    def run_backtest(self, data: pd.DataFrame, strategy_func: Callable,
                    mode: BacktestMode = BacktestMode.VECTORIZED,
                    **strategy_params) -> BacktestResults:
        """Run comprehensive backtest"""
        try:
            self.logger.info(f"Starting backtest with {len(data)} data points")
            
            # Reset state
            self._reset_state()
            
            # Run backtest based on mode
            if mode == BacktestMode.VECTORIZED:
                results = self._run_vectorized_backtest(data, strategy_func, **strategy_params)
            elif mode == BacktestMode.EVENT_DRIVEN:
                results = self._run_event_driven_backtest(data, strategy_func, **strategy_params)
            elif mode == BacktestMode.WALK_FORWARD:
                results = self._run_walk_forward_backtest(data, strategy_func, **strategy_params)
            else:
                raise ValueError(f"Unknown backtest mode: {mode}")
            
            self.logger.info(f"Backtest completed: {results.total_trades} trades, "
                           f"{results.win_rate:.1%} win rate, {results.total_pnl:.2f} total P&L")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Backtest error: {e}")
            raise
    
    def _reset_state(self):
        """Reset backtest state"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_history = [self.initial_capital]
        self.timestamp_history = []
    
    def _run_vectorized_backtest(self, data: pd.DataFrame, strategy_func: Callable,
                                **strategy_params) -> BacktestResults:
        """Run vectorized backtest (fastest method)"""
        try:
            # Generate signals using strategy function
            signals = strategy_func(data, **strategy_params)
            
            if signals is None or signals.empty:
                self.logger.warning("No signals generated by strategy")
                return BacktestResults()
            
            # Ensure signals align with data
            signals = signals.reindex(data.index, fill_value=0)
            
            # Calculate returns
            returns = data['close'].pct_change().fillna(0)
            
            # Apply signals to returns (assuming 1 = buy, -1 = sell, 0 = hold)
            strategy_returns = signals.shift(1) * returns
            
            # Calculate cumulative returns
            cumulative_returns = (1 + strategy_returns).cumprod()
            equity_curve = self.initial_capital * cumulative_returns
            
            # Generate trades from signals
            trades = self._generate_trades_from_signals(data, signals)
            
            # Calculate comprehensive metrics
            results = self._calculate_backtest_metrics(equity_curve, trades, data.index)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Vectorized backtest error: {e}")
            raise
    
    def _run_event_driven_backtest(self, data: pd.DataFrame, strategy_func: Callable,
                                  **strategy_params) -> BacktestResults:
        """Run event-driven backtest (more realistic)"""
        try:
            # Initialize strategy
            strategy_state = {}
            
            for i, (timestamp, row) in enumerate(data.iterrows()):
                # Update strategy state with current data
                current_data = data.iloc[:i+1]
                
                # Get signal from strategy
                signal = strategy_func(current_data, strategy_state, **strategy_params)
                
                if signal:
                    # Process signal
                    self._process_signal(signal, row, timestamp)
                
                # Update equity
                current_equity = self._calculate_current_equity(row)
                self.equity_history.append(current_equity)
                self.timestamp_history.append(timestamp)
                
                # Check for position exits
                self._check_position_exits(row, timestamp)
            
            # Close any remaining positions
            self._close_all_positions(data.iloc[-1], data.index[-1])
            
            # Calculate results
            equity_curve = pd.Series(self.equity_history, index=self.timestamp_history)
            results = self._calculate_backtest_metrics(equity_curve, self.trades, data.index)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Event-driven backtest error: {e}")
            raise
    
    def _run_walk_forward_backtest(self, data: pd.DataFrame, strategy_func: Callable,
                                  training_period: int = 252, testing_period: int = 63,
                                  **strategy_params) -> BacktestResults:
        """Run walk-forward backtest (most robust)"""
        try:
            all_trades = []
            all_equity = []
            all_timestamps = []
            
            start_idx = training_period
            
            while start_idx + testing_period <= len(data):
                # Training data
                train_data = data.iloc[start_idx - training_period:start_idx]
                
                # Testing data
                test_data = data.iloc[start_idx:start_idx + testing_period]
                
                # Optimize strategy on training data (simplified)
                optimized_params = self._optimize_strategy_parameters(
                    train_data, strategy_func, **strategy_params
                )
                
                # Test on out-of-sample data
                test_results = self._run_vectorized_backtest(
                    test_data, strategy_func, **optimized_params
                )
                
                # Accumulate results
                all_trades.extend(test_results.trades)
                
                if not test_results.equity_curve.empty:
                    all_equity.extend(test_results.equity_curve.values)
                    all_timestamps.extend(test_results.equity_curve.index)
                
                start_idx += testing_period
            
            # Combine all results
            if all_equity and all_timestamps:
                equity_curve = pd.Series(all_equity, index=all_timestamps)
                results = self._calculate_backtest_metrics(equity_curve, all_trades, data.index)
            else:
                results = BacktestResults()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Walk-forward backtest error: {e}")
            raise
    
    def _generate_trades_from_signals(self, data: pd.DataFrame, signals: pd.Series) -> List[Trade]:
        """Generate trade records from signals"""
        trades = []
        position = None
        
        try:
            for i, (timestamp, signal) in enumerate(signals.items()):
                if i >= len(data):
                    break
                
                current_price = data.loc[timestamp, 'close']
                
                # Entry signal
                if signal != 0 and position is None:
                    position = {
                        'entry_time': timestamp,
                        'entry_price': current_price,
                        'side': 'buy' if signal > 0 else 'sell',
                        'quantity': abs(signal) * 1000,  # Position size
                        'max_favorable': 0.0,
                        'max_adverse': 0.0
                    }
                
                # Update position tracking
                elif position is not None:
                    # Calculate unrealized P&L
                    if position['side'] == 'buy':
                        unrealized_pnl = current_price - position['entry_price']
                    else:
                        unrealized_pnl = position['entry_price'] - current_price
                    
                    # Track excursions
                    if unrealized_pnl > position['max_favorable']:
                        position['max_favorable'] = unrealized_pnl
                    if unrealized_pnl < position['max_adverse']:
                        position['max_adverse'] = unrealized_pnl
                    
                    # Exit signal (signal changes or becomes 0)
                    if signal == 0 or (signal > 0 and position['side'] == 'sell') or \
                       (signal < 0 and position['side'] == 'buy'):
                        
                        # Close position
                        exit_price = current_price
                        duration = (timestamp - position['entry_time']).total_seconds() / 3600
                        
                        if position['side'] == 'buy':
                            pnl = (exit_price - position['entry_price']) * position['quantity']
                        else:
                            pnl = (position['entry_price'] - exit_price) * position['quantity']
                        
                        pnl_pct = pnl / (position['entry_price'] * position['quantity'])
                        
                        # Apply costs
                        commission_cost = position['entry_price'] * position['quantity'] * self.commission * 2
                        slippage_cost = position['quantity'] * self.slippage * 2
                        swap_cost = position['quantity'] * self.swap_rate * (duration / 24)
                        
                        net_pnl = pnl - commission_cost - slippage_cost - swap_cost
                        
                        trade = Trade(
                            entry_time=position['entry_time'],
                            exit_time=timestamp,
                            symbol='EURUSD',  # Default symbol
                            side=position['side'],
                            entry_price=position['entry_price'],
                            exit_price=exit_price,
                            quantity=position['quantity'],
                            pnl=net_pnl,
                            pnl_pct=net_pnl / (position['entry_price'] * position['quantity']),
                            commission=commission_cost,
                            swap=swap_cost,
                            duration_hours=duration,
                            strategy='backtest_strategy',
                            confidence=75.0,  # Default confidence
                            max_favorable_excursion=position['max_favorable'],
                            max_adverse_excursion=position['max_adverse']
                        )
                        
                        trades.append(trade)
                        position = None
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error generating trades from signals: {e}")
            return []
    
    def _calculate_backtest_metrics(self, equity_curve: pd.Series, trades: List[Trade],
                                  data_index: pd.Index) -> BacktestResults:
        """Calculate comprehensive backtest metrics"""
        try:
            results = BacktestResults()
            
            if equity_curve.empty or not trades:
                return results
            
            # Basic trade metrics
            results.total_trades = len(trades)
            results.winning_trades = sum(1 for trade in trades if trade.pnl > 0)
            results.losing_trades = sum(1 for trade in trades if trade.pnl < 0)
            results.win_rate = results.winning_trades / results.total_trades if results.total_trades > 0 else 0
            
            # P&L metrics
            results.total_pnl = sum(trade.pnl for trade in trades)
            results.total_pnl_pct = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
            
            winning_trades_pnl = [trade.pnl for trade in trades if trade.pnl > 0]
            losing_trades_pnl = [trade.pnl for trade in trades if trade.pnl < 0]
            
            results.avg_win = np.mean(winning_trades_pnl) if winning_trades_pnl else 0
            results.avg_loss = np.mean(losing_trades_pnl) if losing_trades_pnl else 0
            results.largest_win = max(winning_trades_pnl) if winning_trades_pnl else 0
            results.largest_loss = min(losing_trades_pnl) if losing_trades_pnl else 0
            
            gross_profit = sum(winning_trades_pnl) if winning_trades_pnl else 0
            gross_loss = abs(sum(losing_trades_pnl)) if losing_trades_pnl else 0
            results.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Drawdown calculation
            peak = equity_curve.expanding().max()
            drawdown = (equity_curve - peak) / peak
            results.max_drawdown_pct = drawdown.min()
            results.max_drawdown = (peak - equity_curve).max()
            
            # Find drawdown duration
            in_drawdown = drawdown < 0
            drawdown_periods = []
            current_period = 0
            
            for is_dd in in_drawdown:
                if is_dd:
                    current_period += 1
                else:
                    if current_period > 0:
                        drawdown_periods.append(current_period)
                    current_period = 0
            
            results.max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
            
            # Risk metrics
            returns = equity_curve.pct_change().dropna()
            
            if len(returns) > 1:
                # VaR and CVaR
                results.var_95 = np.percentile(returns, 5)
                results.cvar_95 = returns[returns <= results.var_95].mean()
                
                # Performance ratios
                risk_free_rate = 0.02 / 252  # Assume 2% annual risk-free rate
                excess_returns = returns - risk_free_rate
                
                if returns.std() > 0:
                    results.sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(252)
                
                downside_returns = returns[returns < 0]
                if len(downside_returns) > 0 and downside_returns.std() > 0:
                    results.sortino_ratio = excess_returns.mean() / downside_returns.std() * np.sqrt(252)
                
                annual_return = results.total_pnl_pct
                if abs(results.max_drawdown_pct) > 0:
                    results.calmar_ratio = annual_return / abs(results.max_drawdown_pct)
            
            # Trading metrics
            if trades:
                durations = [trade.duration_hours for trade in trades]
                results.avg_trade_duration = np.mean(durations)
                
                # Calculate trades per month
                if data_index is not None and len(data_index) > 0:
                    total_days = (data_index[-1] - data_index[0]).days
                    results.trades_per_month = results.total_trades / (total_days / 30.44) if total_days > 0 else 0
                
                # Expectancy
                results.expectancy = results.win_rate * results.avg_win + (1 - results.win_rate) * results.avg_loss
            
            # Store curves and trades
            results.equity_curve = equity_curve
            results.drawdown_curve = drawdown
            results.trades = trades
            
            # Monthly and yearly returns
            if not equity_curve.empty:
                monthly_equity = equity_curve.resample('M').last()
                results.monthly_returns = monthly_equity.pct_change().dropna()
                
                yearly_equity = equity_curve.resample('Y').last()
                results.yearly_returns = yearly_equity.pct_change().dropna()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating backtest metrics: {e}")
            return BacktestResults()
    
    def _optimize_strategy_parameters(self, data: pd.DataFrame, strategy_func: Callable,
                                    **base_params) -> Dict:
        """Optimize strategy parameters (simplified grid search)"""
        try:
            # Define parameter ranges for optimization
            param_ranges = {
                'fast_ma': [5, 10, 15, 20],
                'slow_ma': [20, 30, 50, 100],
                'rsi_period': [14, 21, 28],
                'rsi_oversold': [20, 25, 30],
                'rsi_overbought': [70, 75, 80]
            }
            
            best_params = base_params.copy()
            best_sharpe = -float('inf')
            
            # Simple grid search (limited to prevent long execution)
            for fast_ma in param_ranges.get('fast_ma', [base_params.get('fast_ma', 10)]):
                for slow_ma in param_ranges.get('slow_ma', [base_params.get('slow_ma', 30)]):
                    if fast_ma >= slow_ma:
                        continue
                    
                    test_params = base_params.copy()
                    test_params.update({'fast_ma': fast_ma, 'slow_ma': slow_ma})
                    
                    try:
                        # Quick test
                        test_results = self._run_vectorized_backtest(data, strategy_func, **test_params)
                        
                        if test_results.sharpe_ratio > best_sharpe:
                            best_sharpe = test_results.sharpe_ratio
                            best_params = test_params.copy()
                    
                    except Exception:
                        continue
            
            return best_params
            
        except Exception as e:
            self.logger.error(f"Parameter optimization error: {e}")
            return base_params
    
    def generate_report(self, results: BacktestResults, save_path: Optional[str] = None) -> str:
        """Generate comprehensive backtest report"""
        try:
            report = []
            report.append("=" * 80)
            report.append("FOREX TRADING BOT - BACKTEST REPORT")
            report.append("=" * 80)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")
            
            # Summary
            report.append("SUMMARY")
            report.append("-" * 40)
            report.append(f"Total Trades: {results.total_trades}")
            report.append(f"Win Rate: {results.win_rate:.2%}")
            report.append(f"Total P&L: ${results.total_pnl:.2f}")
            report.append(f"Total Return: {results.total_pnl_pct:.2%}")
            report.append(f"Sharpe Ratio: {results.sharpe_ratio:.3f}")
            report.append(f"Max Drawdown: {results.max_drawdown_pct:.2%}")
            report.append("")
            
            # Trade Analysis
            report.append("TRADE ANALYSIS")
            report.append("-" * 40)
            report.append(f"Winning Trades: {results.winning_trades}")
            report.append(f"Losing Trades: {results.losing_trades}")
            report.append(f"Average Win: ${results.avg_win:.2f}")
            report.append(f"Average Loss: ${results.avg_loss:.2f}")
            report.append(f"Largest Win: ${results.largest_win:.2f}")
            report.append(f"Largest Loss: ${results.largest_loss:.2f}")
            report.append(f"Profit Factor: {results.profit_factor:.3f}")
            report.append(f"Expectancy: ${results.expectancy:.2f}")
            report.append("")
            
            # Risk Metrics
            report.append("RISK METRICS")
            report.append("-" * 40)
            report.append(f"Maximum Drawdown: {results.max_drawdown_pct:.2%}")
            report.append(f"Max Drawdown Duration: {results.max_drawdown_duration} periods")
            report.append(f"VaR (95%): {results.var_95:.4f}")
            report.append(f"CVaR (95%): {results.cvar_95:.4f}")
            report.append(f"Sortino Ratio: {results.sortino_ratio:.3f}")
            report.append(f"Calmar Ratio: {results.calmar_ratio:.3f}")
            report.append("")
            
            # Trading Metrics
            report.append("TRADING METRICS")
            report.append("-" * 40)
            report.append(f"Average Trade Duration: {results.avg_trade_duration:.1f} hours")
            report.append(f"Trades per Month: {results.trades_per_month:.1f}")
            report.append("")
            
            # Monthly Performance
            if not results.monthly_returns.empty:
                report.append("MONTHLY RETURNS")
                report.append("-" * 40)
                for date, ret in results.monthly_returns.tail(12).items():
                    report.append(f"{date.strftime('%Y-%m')}: {ret:.2%}")
                report.append("")
            
            # Recent Trades
            if results.trades:
                report.append("RECENT TRADES (Last 10)")
                report.append("-" * 40)
                for trade in results.trades[-10:]:
                    report.append(f"{trade.entry_time.strftime('%Y-%m-%d %H:%M')} | "
                                f"{trade.side.upper()} | ${trade.pnl:.2f} | "
                                f"{trade.duration_hours:.1f}h")
                report.append("")
            
            report_text = "\n".join(report)
            
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(report_text)
                self.logger.info(f"Report saved to {save_path}")
            
            return report_text
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return "Error generating report"
    
    def plot_results(self, results: BacktestResults, save_path: Optional[str] = None):
        """Generate comprehensive backtest plots"""
        try:
            if results.equity_curve.empty:
                self.logger.warning("No equity curve data to plot")
                return
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=('Equity Curve', 'Drawdown', 'Monthly Returns', 
                              'Trade P&L Distribution', 'Rolling Sharpe Ratio', 'Trade Duration'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Equity curve
            fig.add_trace(
                go.Scatter(x=results.equity_curve.index, y=results.equity_curve.values,
                          mode='lines', name='Equity', line=dict(color='blue')),
                row=1, col=1
            )
            
            # Drawdown
            fig.add_trace(
                go.Scatter(x=results.drawdown_curve.index, y=results.drawdown_curve.values * 100,
                          mode='lines', name='Drawdown %', fill='tonexty', 
                          line=dict(color='red')),
                row=1, col=2
            )
            
            # Monthly returns
            if not results.monthly_returns.empty:
                fig.add_trace(
                    go.Bar(x=results.monthly_returns.index, y=results.monthly_returns.values * 100,
                          name='Monthly Returns %'),
                    row=2, col=1
                )
            
            # Trade P&L distribution
            if results.trades:
                trade_pnls = [trade.pnl for trade in results.trades]
                fig.add_trace(
                    go.Histogram(x=trade_pnls, name='Trade P&L Distribution', nbinsx=30),
                    row=2, col=2
                )
            
            # Rolling Sharpe ratio
            if len(results.equity_curve) > 30:
                returns = results.equity_curve.pct_change().dropna()
                rolling_sharpe = returns.rolling(30).mean() / returns.rolling(30).std() * np.sqrt(252)
                
                fig.add_trace(
                    go.Scatter(x=rolling_sharpe.index, y=rolling_sharpe.values,
                              mode='lines', name='30-Day Rolling Sharpe'),
                    row=3, col=1
                )
            
            # Trade duration distribution
            if results.trades:
                durations = [trade.duration_hours for trade in results.trades]
                fig.add_trace(
                    go.Histogram(x=durations, name='Trade Duration (hours)', nbinsx=20),
                    row=3, col=2
                )
            
            # Update layout
            fig.update_layout(
                height=1200,
                title_text="Forex Trading Bot - Backtest Results",
                showlegend=False
            )
            
            # Update y-axis labels
            fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
            fig.update_yaxes(title_text="Drawdown (%)", row=1, col=2)
            fig.update_yaxes(title_text="Return (%)", row=2, col=1)
            fig.update_yaxes(title_text="Frequency", row=2, col=2)
            fig.update_yaxes(title_text="Sharpe Ratio", row=3, col=1)
            fig.update_yaxes(title_text="Frequency", row=3, col=2)
            
            if save_path:
                fig.write_html(save_path)
                self.logger.info(f"Plots saved to {save_path}")
            else:
                fig.show()
                
        except Exception as e:
            self.logger.error(f"Error plotting results: {e}")

# Example strategy functions for testing
def simple_ma_crossover_strategy(data: pd.DataFrame, fast_ma: int = 10, slow_ma: int = 30, **kwargs) -> pd.Series:
    """Simple moving average crossover strategy"""
    try:
        if len(data) < slow_ma:
            return pd.Series(index=data.index, dtype=float).fillna(0)
        
        fast_ma_series = data['close'].rolling(fast_ma).mean()
        slow_ma_series = data['close'].rolling(slow_ma).mean()
        
        signals = pd.Series(index=data.index, dtype=float).fillna(0)
        
        # Buy signal when fast MA crosses above slow MA
        signals[fast_ma_series > slow_ma_series] = 1
        
        # Sell signal when fast MA crosses below slow MA
        signals[fast_ma_series < slow_ma_series] = -1
        
        return signals
        
    except Exception as e:
        logging.error(f"Strategy error: {e}")
        return pd.Series(index=data.index, dtype=float).fillna(0)

def rsi_mean_reversion_strategy(data: pd.DataFrame, rsi_period: int = 14, 
                               oversold: int = 30, overbought: int = 70, **kwargs) -> pd.Series:
    """RSI mean reversion strategy"""
    try:
        if len(data) < rsi_period + 1:
            return pd.Series(index=data.index, dtype=float).fillna(0)
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = pd.Series(index=data.index, dtype=float).fillna(0)
        
        # Buy when oversold
        signals[rsi < oversold] = 1
        
        # Sell when overbought
        signals[rsi > overbought] = -1
        
        return signals
        
    except Exception as e:
        logging.error(f"RSI strategy error: {e}")
        return pd.Series(index=data.index, dtype=float).fillna(0)

# Example usage and testing
def test_backtest_engine():
    """Test the backtest engine"""
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    
    # Generate realistic forex price data
    returns = np.random.normal(0, 0.001, len(dates))
    prices = 1.1000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices + np.random.normal(0, 0.0001, len(dates)),
        'high': prices + np.abs(np.random.normal(0, 0.0002, len(dates))),
        'low': prices - np.abs(np.random.normal(0, 0.0002, len(dates))),
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    # Ensure OHLC consistency
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    # Initialize backtest engine
    engine = BacktestEngine(initial_capital=10000, commission=0.0001)
    
    # Test simple MA crossover strategy
    print("Testing MA Crossover Strategy...")
    results = engine.run_backtest(
        data, 
        simple_ma_crossover_strategy,
        mode=BacktestMode.VECTORIZED,
        fast_ma=10,
        slow_ma=30
    )
    
    print(f"Total Trades: {results.total_trades}")
    print(f"Win Rate: {results.win_rate:.2%}")
    print(f"Total P&L: ${results.total_pnl:.2f}")
    print(f"Sharpe Ratio: {results.sharpe_ratio:.3f}")
    print(f"Max Drawdown: {results.max_drawdown_pct:.2%}")
    
    # Generate report
    report = engine.generate_report(results)
    print("\n" + "="*50)
    print("SAMPLE REPORT:")
    print("="*50)
    print(report[:1000] + "..." if len(report) > 1000 else report)
    
    # Test RSI strategy
    print("\n" + "="*50)
    print("Testing RSI Mean Reversion Strategy...")
    results_rsi = engine.run_backtest(
        data,
        rsi_mean_reversion_strategy,
        mode=BacktestMode.VECTORIZED,
        rsi_period=14,
        oversold=30,
        overbought=70
    )
    
    print(f"RSI Strategy - Total Trades: {results_rsi.total_trades}")
    print(f"RSI Strategy - Win Rate: {results_rsi.win_rate:.2%}")
    print(f"RSI Strategy - Total P&L: ${results_rsi.total_pnl:.2f}")
    print(f"RSI Strategy - Sharpe Ratio: {results_rsi.sharpe_ratio:.3f}")

if __name__ == "__main__":
    test_backtest_engine()

