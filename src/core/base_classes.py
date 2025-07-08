"""
Base Classes for Forex Trading System
Implementing common functionality and following SOLID principles
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from abc import ABC

from .interfaces import (
    ISignalGenerator, IRiskManager, IExecutionEngine, IDataProvider,
    TradingSignal, TradeResult, MarketData, RiskMetrics
)


class BaseComponent(ABC):
    """Base class for all trading system components"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._is_initialized = False
        
    def initialize(self) -> None:
        """Initialize the component"""
        if not self._is_initialized:
            self._setup()
            self._is_initialized = True
            self.logger.info(f"{self.name} initialized successfully")
    
    def _setup(self) -> None:
        """Override in subclasses for specific setup logic"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def is_initialized(self) -> bool:
        """Check if component is initialized"""
        return self._is_initialized


class BaseSignalGenerator(BaseComponent, ISignalGenerator):
    """Base class for all signal generators"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.required_periods = self.get_config('required_periods', 20)
        self.confidence_threshold = self.get_config('confidence_threshold', 0.6)
        
    def generate_signal(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate trading signal with validation"""
        if not self._validate_data(data):
            return None
            
        try:
            signal = self._generate_signal_impl(data, pair)
            if signal and self._validate_signal(signal):
                return signal
        except Exception as e:
            self.logger.error(f"Error generating signal for {pair}: {e}")
        
        return None
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """Validate input data"""
        if data is None or data.empty:
            return False
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        if len(data) < self.required_periods:
            return False
            
        return True
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate generated signal"""
        if signal.confidence < self.confidence_threshold:
            return False
        
        if signal.signal not in ['BUY', 'SELL', 'HOLD']:
            return False
            
        return True
    
    def _generate_signal_impl(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Override in subclasses for specific signal logic"""
        raise NotImplementedError
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return self.name
    
    def get_required_periods(self) -> int:
        """Get required periods"""
        return self.required_periods


class BaseRiskManager(BaseComponent, IRiskManager):
    """Base class for risk management"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.max_risk_per_trade = self.get_config('max_risk_per_trade', 0.02)
        self.max_total_exposure = self.get_config('max_total_exposure', 0.1)
        self.max_drawdown_threshold = self.get_config('max_drawdown_threshold', 0.2)
        
    def calculate_position_size(self, signal: TradingSignal, account_balance: float) -> float:
        """Calculate position size with risk management"""
        if not self._validate_signal_for_sizing(signal):
            return 0.0
        
        try:
            base_size = self._calculate_base_size(signal, account_balance)
            adjusted_size = self._apply_risk_adjustments(base_size, signal, account_balance)
            return max(0.0, adjusted_size)
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def validate_trade(self, signal: TradingSignal, current_positions: List[TradeResult]) -> bool:
        """Validate trade against risk rules"""
        # Check maximum positions
        max_positions = self.get_config('max_positions', 10)
        if len(current_positions) >= max_positions:
            return False
        
        # Check pair concentration
        pair_positions = [p for p in current_positions if p.signal.pair == signal.pair]
        max_pair_positions = self.get_config('max_pair_positions', 3)
        if len(pair_positions) >= max_pair_positions:
            return False
        
        # Check correlation limits
        if self._check_correlation_limits(signal, current_positions):
            return False
            
        return True
    
    def calculate_risk_metrics(self, trades: List[TradeResult], current_balance: float) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        if not trades:
            return self._empty_risk_metrics()
        
        returns = [t.profit_loss / current_balance for t in trades if t.status == 'CLOSED']
        
        if not returns:
            return self._empty_risk_metrics()
        
        return RiskMetrics(
            var_1d=self._calculate_var(returns, 0.05, 1),
            var_5d=self._calculate_var(returns, 0.05, 5),
            max_drawdown=self._calculate_max_drawdown(trades, current_balance),
            sharpe_ratio=self._calculate_sharpe_ratio(returns),
            sortino_ratio=self._calculate_sortino_ratio(returns),
            calmar_ratio=self._calculate_calmar_ratio(returns),
            current_exposure=self._calculate_current_exposure(trades, current_balance),
            position_concentration=self._calculate_position_concentration(trades)
        )
    
    def should_emergency_stop(self, current_balance: float, initial_balance: float) -> bool:
        """Check if emergency stop should be triggered"""
        drawdown = (initial_balance - current_balance) / initial_balance
        return drawdown >= self.max_drawdown_threshold
    
    def _validate_signal_for_sizing(self, signal: TradingSignal) -> bool:
        """Validate signal for position sizing"""
        return signal is not None and signal.confidence > 0
    
    def _calculate_base_size(self, signal: TradingSignal, account_balance: float) -> float:
        """Calculate base position size"""
        risk_amount = account_balance * self.max_risk_per_trade
        
        if signal.stop_loss:
            price_risk = abs(signal.price - signal.stop_loss)
            if price_risk > 0:
                return risk_amount / price_risk
        
        # Fallback to percentage of balance
        return account_balance * 0.01
    
    def _apply_risk_adjustments(self, base_size: float, signal: TradingSignal, account_balance: float) -> float:
        """Apply risk adjustments to base size"""
        # Confidence adjustment
        confidence_multiplier = signal.confidence
        adjusted_size = base_size * confidence_multiplier
        
        # Volatility adjustment
        volatility_multiplier = self.get_config('volatility_multiplier', 1.0)
        adjusted_size *= volatility_multiplier
        
        return adjusted_size
    
    def _check_correlation_limits(self, signal: TradingSignal, current_positions: List[TradeResult]) -> bool:
        """Check if adding position would violate correlation limits"""
        # Simplified correlation check - can be enhanced
        same_base_currency = [p for p in current_positions 
                            if p.signal.pair[:3] == signal.pair[:3]]
        max_same_base = self.get_config('max_same_base_currency', 5)
        return len(same_base_currency) >= max_same_base
    
    def _calculate_var(self, returns: List[float], confidence: float, days: int) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        return np.percentile(returns_array, (1 - confidence) * 100) * np.sqrt(days)
    
    def _calculate_max_drawdown(self, trades: List[TradeResult], current_balance: float) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0.0
        
        cumulative_returns = []
        running_balance = current_balance
        
        for trade in sorted(trades, key=lambda t: t.entry_time):
            if trade.status == 'CLOSED':
                running_balance += trade.profit_loss
                cumulative_returns.append(running_balance)
        
        if not cumulative_returns:
            return 0.0
        
        peak = cumulative_returns[0]
        max_dd = 0.0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array  # Assuming risk-free rate is 0
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    def _calculate_sortino_ratio(self, returns: List[float]) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0.0
        
        returns_array = np.array(returns)
        negative_returns = returns_array[returns_array < 0]
        
        if len(negative_returns) == 0:
            return float('inf')
        
        downside_deviation = np.std(negative_returns)
        if downside_deviation == 0:
            return 0.0
        
        return np.mean(returns_array) / downside_deviation * np.sqrt(252)
    
    def _calculate_calmar_ratio(self, returns: List[float]) -> float:
        """Calculate Calmar ratio"""
        if not returns:
            return 0.0
        
        annual_return = np.mean(returns) * 252
        max_dd = self._calculate_max_drawdown([], 0)  # Simplified
        
        if max_dd == 0:
            return float('inf')
        
        return annual_return / max_dd
    
    def _calculate_current_exposure(self, trades: List[TradeResult], current_balance: float) -> float:
        """Calculate current market exposure"""
        open_trades = [t for t in trades if t.status == 'OPEN']
        total_exposure = sum(abs(t.position_size * t.entry_price) for t in open_trades)
        return total_exposure / current_balance if current_balance > 0 else 0.0
    
    def _calculate_position_concentration(self, trades: List[TradeResult]) -> Dict[str, float]:
        """Calculate position concentration by pair"""
        open_trades = [t for t in trades if t.status == 'OPEN']
        if not open_trades:
            return {}
        
        pair_exposure = {}
        total_exposure = 0.0
        
        for trade in open_trades:
            exposure = abs(trade.position_size * trade.entry_price)
            pair_exposure[trade.signal.pair] = pair_exposure.get(trade.signal.pair, 0) + exposure
            total_exposure += exposure
        
        if total_exposure == 0:
            return {}
        
        return {pair: exposure / total_exposure for pair, exposure in pair_exposure.items()}
    
    def _empty_risk_metrics(self) -> RiskMetrics:
        """Return empty risk metrics"""
        return RiskMetrics(
            var_1d=0.0, var_5d=0.0, max_drawdown=0.0,
            sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
            current_exposure=0.0, position_concentration={}
        )


class BaseExecutionEngine(BaseComponent, IExecutionEngine):
    """Base class for execution engines"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.account_balance = self.get_config('initial_balance', 100000.0)
        self.open_positions: List[TradeResult] = []
        self.closed_trades: List[TradeResult] = []
        self.trade_counter = 0
        
    def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeResult:
        """Execute a trade"""
        if position_size <= 0:
            raise ValueError("Position size must be positive")
        
        try:
            trade_id = self._generate_trade_id()
            entry_price = self._get_execution_price(signal)
            
            trade = TradeResult(
                trade_id=trade_id,
                signal=signal,
                entry_price=entry_price,
                exit_price=None,
                position_size=position_size,
                profit_loss=0.0,
                status='OPEN',
                entry_time=datetime.now(),
                slippage=self._calculate_slippage(signal, position_size),
                commission=self._calculate_commission(position_size, entry_price)
            )
            
            self.open_positions.append(trade)
            self._update_account_balance(-trade.commission)
            
            self.logger.info(f"Trade executed: {trade_id} - {signal.pair} {signal.signal} @ {entry_price}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            raise
    
    def close_position(self, trade_id: str) -> TradeResult:
        """Close an open position"""
        trade = self._find_open_trade(trade_id)
        if not trade:
            raise ValueError(f"Trade {trade_id} not found or already closed")
        
        try:
            exit_price = self._get_exit_price(trade)
            exit_commission = self._calculate_commission(trade.position_size, exit_price)
            
            # Calculate profit/loss
            if trade.signal.signal == 'BUY':
                profit_loss = (exit_price - trade.entry_price) * trade.position_size
            else:  # SELL
                profit_loss = (trade.entry_price - exit_price) * trade.position_size
            
            profit_loss -= (trade.commission + exit_commission)
            
            # Update trade
            trade.exit_price = exit_price
            trade.profit_loss = profit_loss
            trade.status = 'CLOSED'
            trade.exit_time = datetime.now()
            trade.commission += exit_commission
            
            # Move to closed trades
            self.open_positions.remove(trade)
            self.closed_trades.append(trade)
            
            # Update account balance
            self._update_account_balance(profit_loss - exit_commission)
            
            self.logger.info(f"Position closed: {trade_id} - P&L: {profit_loss:.2f}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Error closing position {trade_id}: {e}")
            raise
    
    def get_open_positions(self) -> List[TradeResult]:
        """Get all open positions"""
        return self.open_positions.copy()
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        return self.account_balance
    
    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        self.trade_counter += 1
        return f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.trade_counter:04d}"
    
    def _get_execution_price(self, signal: TradingSignal) -> float:
        """Get execution price (override in subclasses)"""
        return signal.price
    
    def _get_exit_price(self, trade: TradeResult) -> float:
        """Get exit price (override in subclasses)"""
        return trade.entry_price  # Simplified
    
    def _calculate_slippage(self, signal: TradingSignal, position_size: float) -> float:
        """Calculate slippage (override in subclasses)"""
        base_slippage = self.get_config('base_slippage', 0.0001)
        size_impact = position_size * self.get_config('size_impact_factor', 0.00001)
        return base_slippage + size_impact
    
    def _calculate_commission(self, position_size: float, price: float) -> float:
        """Calculate commission"""
        commission_rate = self.get_config('commission_rate', 0.0001)
        return position_size * price * commission_rate
    
    def _find_open_trade(self, trade_id: str) -> Optional[TradeResult]:
        """Find open trade by ID"""
        for trade in self.open_positions:
            if trade.trade_id == trade_id:
                return trade
        return None
    
    def _update_account_balance(self, amount: float) -> None:
        """Update account balance"""
        self.account_balance += amount


class BaseDataProvider(BaseComponent, IDataProvider):
    """Base class for data providers"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.cache_enabled = self.get_config('cache_enabled', True)
        self.cache_ttl = self.get_config('cache_ttl', 300)  # 5 minutes
        self._cache: Dict[str, Dict] = {}
    
    def get_historical_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get historical data with caching"""
        cache_key = f"{pair}_{timeframe}_{periods}"
        
        if self.cache_enabled and self._is_cache_valid(cache_key):
            return self._cache[cache_key]['data']
        
        try:
            data = self._fetch_historical_data(pair, timeframe, periods)
            
            if self.cache_enabled:
                self._cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {pair}: {e}")
            raise
    
    def get_live_price(self, pair: str) -> MarketData:
        """Get live price (override in subclasses)"""
        raise NotImplementedError
    
    def is_market_open(self, pair: str) -> bool:
        """Check if market is open (override in subclasses)"""
        return True  # Simplified - forex is mostly 24/5
    
    def _fetch_historical_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Fetch historical data (override in subclasses)"""
        raise NotImplementedError
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl

