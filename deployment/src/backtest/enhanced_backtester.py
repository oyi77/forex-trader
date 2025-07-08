"""
Enhanced Backtesting Engine with Real Data
Provides accurate simulation of trading conditions
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path

from ..core.interfaces import (
    ISignalGenerator, IRiskManager, IExecutionEngine, 
    TradingSignal, TradeResult, MarketData
)
from ..data.real_data_provider import RealDataProvider


@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    initial_balance: float = 1000000.0
    leverage: int = 100
    commission_rate: float = 0.00005  # 0.005% per trade
    slippage_rate: float = 0.0003     # 0.03% slippage
    spread_multiplier: float = 1.0    # Multiply typical spreads
    risk_per_trade: float = 0.02      # 2% risk per trade
    max_positions: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timeframe: str = '1h'
    symbols: List[str] = field(default_factory=lambda: ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'])


@dataclass
class BacktestMetrics:
    """Comprehensive backtesting metrics"""
    total_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_trade_duration: float = 0.0
    avg_bars_held: float = 0.0
    recovery_factor: float = 0.0
    ulcer_index: float = 0.0
    
    # Additional metrics for extreme trading
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    
    # Risk metrics
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional Value at Risk 95%
    
    # Performance by symbol
    symbol_performance: Dict[str, float] = field(default_factory=dict)
    
    # Time-based performance
    monthly_returns: List[float] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)


class EnhancedBacktester:
    """
    Enhanced backtesting engine with realistic market simulation
    """
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_provider = RealDataProvider()
        self.current_balance = config.initial_balance
        self.initial_balance = config.initial_balance
        self.equity_curve = []
        self.trades = []
        self.open_positions = {}
        self.daily_balances = []
        
        # Performance tracking
        self.peak_balance = config.initial_balance
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Market data storage
        self.market_data = {}
        self.current_time = None
        
        self.logger.info("Enhanced backtester initialized")
    
    def run_backtest(self, strategies: List[ISignalGenerator], 
                    risk_manager: IRiskManager = None) -> BacktestMetrics:
        """Run comprehensive backtest"""
        try:
            self.logger.info("Starting enhanced backtest")
            
            # Download market data
            self._download_market_data()
            
            # Initialize time series
            self._initialize_time_series()
            
            # Run simulation
            self._run_simulation(strategies, risk_manager)
            
            # Calculate metrics
            metrics = self._calculate_metrics()
            
            # Generate reports
            self._generate_reports(metrics)
            
            self.logger.info("Backtest completed successfully")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise
    
    def _download_market_data(self) -> None:
        """Download historical market data for all symbols"""
        self.logger.info("Downloading market data...")
        
        # Calculate date range
        end_date = self.config.end_date or datetime.now()
        start_date = self.config.start_date or (end_date - timedelta(days=365))
        
        days = (end_date - start_date).days
        
        # Download data for each symbol
        for symbol in self.config.symbols:
            try:
                periods = self._calculate_periods(self.config.timeframe, days)
                data = self.data_provider.get_historical_data(symbol, self.config.timeframe, periods)
                
                if not data.empty:
                    # Ensure we have required columns
                    required_cols = ['open', 'high', 'low', 'close', 'volume']
                    if all(col in data.columns for col in required_cols):
                        self.market_data[symbol] = data
                        self.logger.info(f"Downloaded {len(data)} bars for {symbol}")
                    else:
                        self.logger.warning(f"Missing required columns for {symbol}")
                else:
                    self.logger.warning(f"No data available for {symbol}")
                    
            except Exception as e:
                self.logger.error(f"Failed to download data for {symbol}: {e}")
        
        if not self.market_data:
            raise ValueError("No market data available for backtesting")
    
    def _initialize_time_series(self) -> None:
        """Initialize time series for simulation"""
        # Find common time index across all symbols
        time_indices = []
        for symbol, data in self.market_data.items():
            time_indices.append(data.index)
        
        if time_indices:
            # Use intersection of all time indices
            common_index = time_indices[0]
            for idx in time_indices[1:]:
                common_index = common_index.intersection(idx)
            
            self.time_series = sorted(common_index)
            self.logger.info(f"Initialized time series with {len(self.time_series)} bars")
        else:
            raise ValueError("No time series data available")
    
    def _run_simulation(self, strategies: List[ISignalGenerator], 
                       risk_manager: IRiskManager = None) -> None:
        """Run the trading simulation"""
        self.logger.info("Running trading simulation...")
        
        for i, timestamp in enumerate(self.time_series):
            self.current_time = timestamp
            
            # Update equity curve
            self._update_equity_curve()
            
            # Process each symbol
            for symbol in self.config.symbols:
                if symbol not in self.market_data:
                    continue
                
                # Get current market data
                current_data = self._get_current_market_data(symbol, i)
                if current_data is None:
                    continue
                
                # Generate signals from strategies
                for strategy in strategies:
                    try:
                        signal = self._generate_signal(strategy, symbol, i)
                        if signal:
                            self._process_signal(signal, current_data, risk_manager)
                    except Exception as e:
                        self.logger.warning(f"Strategy {strategy.get_strategy_name()} failed: {e}")
            
            # Update open positions
            self._update_open_positions()
            
            # Check for margin calls or stop-outs
            self._check_risk_limits()
            
            # Log progress
            if i % 1000 == 0:
                self.logger.info(f"Processed {i}/{len(self.time_series)} bars")
        
        # Close all remaining positions
        self._close_all_positions()
    
    def _get_current_market_data(self, symbol: str, bar_index: int) -> Optional[MarketData]:
        """Get current market data for a symbol"""
        try:
            data = self.market_data[symbol]
            if bar_index >= len(data):
                return None
            
            row = data.iloc[bar_index]
            
            return MarketData(
                pair=symbol,
                timestamp=self.current_time,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume', 0),
                bid=row.get('bid', row['close'] - self._get_spread(symbol) / 2),
                ask=row.get('ask', row['close'] + self._get_spread(symbol) / 2)
            )
            
        except Exception as e:
            self.logger.warning(f"Error getting market data for {symbol}: {e}")
            return None
    
    def _generate_signal(self, strategy: ISignalGenerator, symbol: str, bar_index: int) -> Optional[TradingSignal]:
        """Generate trading signal from strategy"""
        try:
            # Get historical data for strategy
            lookback = strategy.get_required_periods() if hasattr(strategy, 'get_required_periods') else 50
            start_idx = max(0, bar_index - lookback)
            end_idx = bar_index + 1
            
            data = self.market_data[symbol].iloc[start_idx:end_idx]
            
            if len(data) < lookback:
                return None
            
            # Generate signal
            signal = strategy.generate_signal(data, symbol)
            
            if signal and signal.timestamp != self.current_time:
                # Update signal timestamp
                signal.timestamp = self.current_time
            
            return signal
            
        except Exception as e:
            self.logger.warning(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _process_signal(self, signal: TradingSignal, market_data: MarketData, 
                       risk_manager: IRiskManager = None) -> None:
        """Process a trading signal"""
        try:
            # Skip if signal is not actionable
            if signal.signal not in ['BUY', 'SELL']:
                return
            
            # Check if we already have a position in this symbol
            if signal.pair in self.open_positions:
                return  # Skip if already have position
            
            # Risk management
            if risk_manager:
                if not risk_manager.validate_trade(signal, list(self.open_positions.values())):
                    return
                
                position_size = risk_manager.calculate_position_size(signal, self.current_balance)
            else:
                position_size = self._calculate_position_size(signal)
            
            if position_size <= 0:
                return
            
            # Execute trade
            trade_result = self._execute_trade(signal, position_size, market_data)
            if trade_result:
                self.open_positions[signal.pair] = trade_result
                
        except Exception as e:
            self.logger.warning(f"Error processing signal: {e}")
    
    def _execute_trade(self, signal: TradingSignal, position_size: float, 
                      market_data: MarketData) -> Optional[TradeResult]:
        """Execute a trade with realistic slippage and commission"""
        try:
            # Determine entry price with slippage
            if signal.signal == 'BUY':
                base_price = market_data.ask
            else:
                base_price = market_data.bid
            
            # Apply slippage
            slippage = base_price * self.config.slippage_rate
            if signal.signal == 'BUY':
                entry_price = base_price + slippage
            else:
                entry_price = base_price - slippage
            
            # Calculate commission
            commission = position_size * entry_price * self.config.commission_rate
            
            # Check if we have enough balance
            required_margin = position_size * entry_price / self.config.leverage
            if required_margin + commission > self.current_balance:
                return None  # Insufficient funds
            
            # Create trade result
            trade_id = f"{signal.pair}_{self.current_time.strftime('%Y%m%d_%H%M%S')}"
            
            trade_result = TradeResult(
                trade_id=trade_id,
                signal=signal,
                entry_price=entry_price,
                exit_price=None,
                position_size=position_size,
                profit_loss=0.0,
                status='OPEN',
                entry_time=self.current_time,
                exit_time=None,
                slippage=slippage,
                commission=commission
            )
            
            # Update balance
            self.current_balance -= commission
            
            self.logger.debug(f"Opened {signal.signal} position for {signal.pair} at {entry_price}")
            return trade_result
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None
    
    def _update_open_positions(self) -> None:
        """Update open positions and check for exits"""
        positions_to_close = []
        
        for symbol, position in self.open_positions.items():
            try:
                # Get current market data
                current_data = self._get_current_market_data(symbol, 
                    self.time_series.index(self.current_time))
                
                if current_data is None:
                    continue
                
                # Check for stop loss or take profit
                should_close, exit_reason = self._should_close_position(position, current_data)
                
                if should_close:
                    positions_to_close.append((symbol, exit_reason))
                
            except Exception as e:
                self.logger.warning(f"Error updating position {symbol}: {e}")
        
        # Close positions that need to be closed
        for symbol, reason in positions_to_close:
            self._close_position(symbol, reason)
    
    def _should_close_position(self, position: TradeResult, 
                              market_data: MarketData) -> Tuple[bool, str]:
        """Check if position should be closed"""
        try:
            signal = position.signal
            
            # Determine current price
            if signal.signal == 'BUY':
                current_price = market_data.bid
            else:
                current_price = market_data.ask
            
            # Check stop loss
            if signal.stop_loss:
                if signal.signal == 'BUY' and current_price <= signal.stop_loss:
                    return True, 'STOP_LOSS'
                elif signal.signal == 'SELL' and current_price >= signal.stop_loss:
                    return True, 'STOP_LOSS'
            
            # Check take profit
            if signal.take_profit:
                if signal.signal == 'BUY' and current_price >= signal.take_profit:
                    return True, 'TAKE_PROFIT'
                elif signal.signal == 'SELL' and current_price <= signal.take_profit:
                    return True, 'TAKE_PROFIT'
            
            # Check maximum holding time (for scalping strategies)
            if hasattr(signal, 'max_holding_minutes'):
                holding_time = (self.current_time - position.entry_time).total_seconds() / 60
                if holding_time >= signal.max_holding_minutes:
                    return True, 'MAX_TIME'
            
            return False, ''
            
        except Exception as e:
            self.logger.warning(f"Error checking position exit: {e}")
            return False, ''
    
    def _close_position(self, symbol: str, reason: str = 'MANUAL') -> None:
        """Close an open position"""
        try:
            if symbol not in self.open_positions:
                return
            
            position = self.open_positions[symbol]
            
            # Get current market data
            current_data = self._get_current_market_data(symbol, 
                self.time_series.index(self.current_time))
            
            if current_data is None:
                return
            
            # Determine exit price with slippage
            if position.signal.signal == 'BUY':
                base_price = current_data.bid
            else:
                base_price = current_data.ask
            
            slippage = base_price * self.config.slippage_rate
            if position.signal.signal == 'BUY':
                exit_price = base_price - slippage
            else:
                exit_price = base_price + slippage
            
            # Calculate P&L
            if position.signal.signal == 'BUY':
                pnl = (exit_price - position.entry_price) * position.position_size
            else:
                pnl = (position.entry_price - exit_price) * position.position_size
            
            # Apply leverage
            pnl *= self.config.leverage
            
            # Calculate exit commission
            exit_commission = position.position_size * exit_price * self.config.commission_rate
            pnl -= exit_commission
            
            # Update position
            position.exit_price = exit_price
            position.exit_time = self.current_time
            position.profit_loss = pnl
            position.status = 'CLOSED'
            position.commission += exit_commission
            
            # Update balance
            self.current_balance += pnl
            
            # Add to completed trades
            self.trades.append(position)
            
            # Remove from open positions
            del self.open_positions[symbol]
            
            self.logger.debug(f"Closed {symbol} position: P&L = {pnl:.2f} ({reason})")
            
        except Exception as e:
            self.logger.error(f"Error closing position {symbol}: {e}")
    
    def _close_all_positions(self) -> None:
        """Close all remaining open positions"""
        symbols_to_close = list(self.open_positions.keys())
        for symbol in symbols_to_close:
            self._close_position(symbol, 'END_OF_BACKTEST')
    
    def _calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate position size based on risk management"""
        try:
            # Risk per trade as percentage of balance
            risk_amount = self.current_balance * self.config.risk_per_trade
            
            # Calculate position size based on stop loss
            if signal.stop_loss:
                price_diff = abs(signal.price - signal.stop_loss)
                if price_diff > 0:
                    position_size = risk_amount / price_diff
                else:
                    position_size = self.current_balance * 0.01  # 1% fallback
            else:
                # Default position size if no stop loss
                position_size = self.current_balance * 0.01
            
            # Apply leverage
            max_position_value = self.current_balance * self.config.leverage
            max_position_size = max_position_value / signal.price
            
            return min(position_size, max_position_size)
            
        except Exception as e:
            self.logger.warning(f"Error calculating position size: {e}")
            return 0.0
    
    def _get_spread(self, symbol: str) -> float:
        """Get typical spread for a symbol"""
        spreads = {
            'EURUSD': 0.0001 * 1.5,
            'GBPUSD': 0.0001 * 2.0,
            'USDJPY': 0.01 * 1.5,
            'USDCHF': 0.0001 * 2.0,
            'AUDUSD': 0.0001 * 2.5,
            'USDCAD': 0.0001 * 2.5,
            'NZDUSD': 0.0001 * 3.0,
            'XAUUSD': 0.50,
            'XAGUSD': 0.02,
            'CRUDE_OIL': 0.03,
            'BRENT_OIL': 0.03
        }
        
        base_spread = spreads.get(symbol, 0.0001 * 3.0)
        return base_spread * self.config.spread_multiplier
    
    def _update_equity_curve(self) -> None:
        """Update equity curve and drawdown tracking"""
        # Calculate current equity (balance + unrealized P&L)
        unrealized_pnl = 0.0
        
        for symbol, position in self.open_positions.items():
            try:
                current_data = self._get_current_market_data(symbol, 
                    self.time_series.index(self.current_time))
                
                if current_data:
                    if position.signal.signal == 'BUY':
                        current_price = current_data.bid
                    else:
                        current_price = current_data.ask
                    
                    if position.signal.signal == 'BUY':
                        pnl = (current_price - position.entry_price) * position.position_size
                    else:
                        pnl = (position.entry_price - current_price) * position.position_size
                    
                    pnl *= self.config.leverage
                    unrealized_pnl += pnl
                    
            except Exception:
                pass
        
        current_equity = self.current_balance + unrealized_pnl
        
        # Update peak and drawdown
        if current_equity > self.peak_balance:
            self.peak_balance = current_equity
            self.current_drawdown = 0.0
        else:
            self.current_drawdown = (self.peak_balance - current_equity) / self.peak_balance
            self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
        
        # Record equity point
        self.equity_curve.append({
            'timestamp': self.current_time,
            'balance': self.current_balance,
            'equity': current_equity,
            'drawdown': self.current_drawdown
        })
    
    def _check_risk_limits(self) -> None:
        """Check risk limits and margin requirements"""
        # Check maximum drawdown
        if self.current_drawdown > 0.5:  # 50% drawdown limit
            self.logger.warning("Maximum drawdown exceeded, closing all positions")
            self._close_all_positions()
        
        # Check minimum balance
        if self.current_balance < self.initial_balance * 0.1:  # 10% of initial
            self.logger.warning("Minimum balance reached, stopping trading")
            self._close_all_positions()
    
    def _calculate_periods(self, timeframe: str, days: int) -> int:
        """Calculate number of periods for given timeframe and days"""
        timeframe_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }
        
        minutes_per_day = 1440
        total_minutes = days * minutes_per_day
        tf_minutes = timeframe_minutes.get(timeframe, 60)
        
        # Account for market hours (forex is 24/5)
        if timeframe != '1d':
            market_factor = 5/7
            total_minutes *= market_factor
        
        return int(total_minutes / tf_minutes)
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive backtest metrics"""
        metrics = BacktestMetrics()
        
        if not self.trades:
            return metrics
        
        # Basic metrics
        final_balance = self.current_balance
        metrics.total_return = final_balance - self.initial_balance
        metrics.total_return_pct = (final_balance / self.initial_balance - 1) * 100
        
        # Trade statistics
        metrics.total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.profit_loss > 0]
        losing_trades = [t for t in self.trades if t.profit_loss < 0]
        
        metrics.winning_trades = len(winning_trades)
        metrics.losing_trades = len(losing_trades)
        metrics.win_rate = (metrics.winning_trades / metrics.total_trades) * 100 if metrics.total_trades > 0 else 0
        
        # P&L statistics
        if winning_trades:
            metrics.avg_win = sum(t.profit_loss for t in winning_trades) / len(winning_trades)
            metrics.largest_win = max(t.profit_loss for t in winning_trades)
        
        if losing_trades:
            metrics.avg_loss = sum(t.profit_loss for t in losing_trades) / len(losing_trades)
            metrics.largest_loss = min(t.profit_loss for t in losing_trades)
        
        # Profit factor
        gross_profit = sum(t.profit_loss for t in winning_trades)
        gross_loss = abs(sum(t.profit_loss for t in losing_trades))
        metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Drawdown
        metrics.max_drawdown = self.max_drawdown * 100
        metrics.max_drawdown_pct = self.max_drawdown * 100
        
        # Risk-adjusted returns
        if self.equity_curve:
            returns = self._calculate_returns()
            metrics.sharpe_ratio = self._calculate_sharpe_ratio(returns)
            metrics.sortino_ratio = self._calculate_sortino_ratio(returns)
            
            # Annualized return
            days = (self.equity_curve[-1]['timestamp'] - self.equity_curve[0]['timestamp']).days
            if days > 0:
                metrics.annualized_return = ((final_balance / self.initial_balance) ** (365 / days) - 1) * 100
        
        # Calmar ratio
        if metrics.max_drawdown > 0:
            metrics.calmar_ratio = metrics.annualized_return / metrics.max_drawdown
        
        # Trade duration
        trade_durations = []
        for trade in self.trades:
            if trade.exit_time and trade.entry_time:
                duration = (trade.exit_time - trade.entry_time).total_seconds() / 3600  # hours
                trade_durations.append(duration)
        
        if trade_durations:
            metrics.avg_trade_duration = sum(trade_durations) / len(trade_durations)
        
        # Symbol performance
        for symbol in self.config.symbols:
            symbol_trades = [t for t in self.trades if t.signal.pair == symbol]
            if symbol_trades:
                symbol_pnl = sum(t.profit_loss for t in symbol_trades)
                metrics.symbol_performance[symbol] = symbol_pnl
        
        return metrics
    
    def _calculate_returns(self) -> List[float]:
        """Calculate daily returns from equity curve"""
        if len(self.equity_curve) < 2:
            return []
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_equity = self.equity_curve[i-1]['equity']
            curr_equity = self.equity_curve[i]['equity']
            
            if prev_equity > 0:
                daily_return = (curr_equity / prev_equity - 1) * 100
                returns.append(daily_return)
        
        return returns
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Assuming risk-free rate of 2% annually (0.0055% daily)
        risk_free_rate = 0.0055
        return (mean_return - risk_free_rate) / std_return * np.sqrt(252)  # Annualized
    
    def _calculate_sortino_ratio(self, returns: List[float]) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0.0
        
        mean_return = np.mean(returns)
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return float('inf')
        
        downside_deviation = np.std(negative_returns)
        
        if downside_deviation == 0:
            return 0.0
        
        risk_free_rate = 0.0055
        return (mean_return - risk_free_rate) / downside_deviation * np.sqrt(252)
    
    def _generate_reports(self, metrics: BacktestMetrics) -> None:
        """Generate backtest reports"""
        try:
            # Create reports directory
            reports_dir = Path('./reports')
            reports_dir.mkdir(exist_ok=True)
            
            # Generate summary report
            self._generate_summary_report(metrics, reports_dir)
            
            # Generate detailed trade log
            self._generate_trade_log(reports_dir)
            
            # Generate equity curve data
            self._generate_equity_curve_data(reports_dir)
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
    
    def _generate_summary_report(self, metrics: BacktestMetrics, reports_dir: Path) -> None:
        """Generate summary report"""
        report_file = reports_dir / f"backtest_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write("ENHANCED BACKTEST SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Initial Balance: ${self.initial_balance:,.2f}\n")
            f.write(f"Final Balance: ${self.current_balance:,.2f}\n")
            f.write(f"Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_pct:.2f}%)\n")
            f.write(f"Annualized Return: {metrics.annualized_return:.2f}%\n\n")
            
            f.write(f"Total Trades: {metrics.total_trades}\n")
            f.write(f"Winning Trades: {metrics.winning_trades}\n")
            f.write(f"Losing Trades: {metrics.losing_trades}\n")
            f.write(f"Win Rate: {metrics.win_rate:.2f}%\n\n")
            
            f.write(f"Profit Factor: {metrics.profit_factor:.2f}\n")
            f.write(f"Average Win: ${metrics.avg_win:.2f}\n")
            f.write(f"Average Loss: ${metrics.avg_loss:.2f}\n")
            f.write(f"Largest Win: ${metrics.largest_win:.2f}\n")
            f.write(f"Largest Loss: ${metrics.largest_loss:.2f}\n\n")
            
            f.write(f"Maximum Drawdown: {metrics.max_drawdown:.2f}%\n")
            f.write(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}\n")
            f.write(f"Sortino Ratio: {metrics.sortino_ratio:.2f}\n")
            f.write(f"Calmar Ratio: {metrics.calmar_ratio:.2f}\n\n")
            
            f.write("SYMBOL PERFORMANCE:\n")
            for symbol, pnl in metrics.symbol_performance.items():
                f.write(f"{symbol}: ${pnl:,.2f}\n")
        
        self.logger.info(f"Summary report saved to {report_file}")
    
    def _generate_trade_log(self, reports_dir: Path) -> None:
        """Generate detailed trade log"""
        trade_log_file = reports_dir / f"trade_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        trade_data = []
        for trade in self.trades:
            trade_data.append({
                'trade_id': trade.trade_id,
                'symbol': trade.signal.pair,
                'signal': trade.signal.signal,
                'strategy': trade.signal.strategy,
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'position_size': trade.position_size,
                'profit_loss': trade.profit_loss,
                'commission': trade.commission,
                'slippage': trade.slippage,
                'confidence': trade.signal.confidence,
                'duration_hours': (trade.exit_time - trade.entry_time).total_seconds() / 3600 if trade.exit_time else None
            })
        
        if trade_data:
            df = pd.DataFrame(trade_data)
            df.to_csv(trade_log_file, index=False)
            self.logger.info(f"Trade log saved to {trade_log_file}")
    
    def _generate_equity_curve_data(self, reports_dir: Path) -> None:
        """Generate equity curve data"""
        equity_file = reports_dir / f"equity_curve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if self.equity_curve:
            df = pd.DataFrame(self.equity_curve)
            df.to_csv(equity_file, index=False)
            self.logger.info(f"Equity curve data saved to {equity_file}")


def run_enhanced_backtest(config: BacktestConfig, strategies: List[ISignalGenerator], 
                         risk_manager: IRiskManager = None) -> BacktestMetrics:
    """Run enhanced backtest with given configuration"""
    backtester = EnhancedBacktester(config)
    return backtester.run_backtest(strategies, risk_manager)

