"""
Core Interfaces for Forex Trading System
Following SOLID principles and Interface Segregation
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class TradingSignal:
    """Immutable trading signal data structure"""
    pair: str
    signal: str  # BUY, SELL, HOLD
    strategy: str
    confidence: float
    price: float
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TradeResult:
    """Immutable trade result data structure"""
    trade_id: str
    signal: TradingSignal
    entry_price: float
    exit_price: Optional[float]
    position_size: float
    profit_loss: float
    status: str  # OPEN, CLOSED, CANCELLED
    entry_time: datetime
    exit_time: Optional[datetime] = None
    slippage: float = 0.0
    commission: float = 0.0


@dataclass
class MarketData:
    """Immutable market data structure"""
    pair: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None


@dataclass
class RiskMetrics:
    """Risk assessment metrics"""
    var_1d: float
    var_5d: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    current_exposure: float
    position_concentration: Dict[str, float]


# Core Interfaces

class IDataProvider(ABC):
    """Interface for market data providers"""
    
    @abstractmethod
    def get_historical_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get historical market data"""
        pass
    
    @abstractmethod
    def get_live_price(self, pair: str) -> MarketData:
        """Get current live price"""
        pass
    
    @abstractmethod
    def is_market_open(self, pair: str) -> bool:
        """Check if market is open for trading"""
        pass


class ISignalGenerator(ABC):
    """Interface for trading signal generation"""
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, pair: str) -> Optional[TradingSignal]:
        """Generate trading signal from market data"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the strategy name"""
        pass
    
    @abstractmethod
    def get_required_periods(self) -> int:
        """Get minimum periods required for signal generation"""
        pass


class IRiskManager(ABC):
    """Interface for risk management"""
    
    @abstractmethod
    def calculate_position_size(self, signal: TradingSignal, account_balance: float) -> float:
        """Calculate appropriate position size"""
        pass
    
    @abstractmethod
    def validate_trade(self, signal: TradingSignal, current_positions: List[TradeResult]) -> bool:
        """Validate if trade should be executed"""
        pass
    
    @abstractmethod
    def calculate_risk_metrics(self, trades: List[TradeResult], current_balance: float) -> RiskMetrics:
        """Calculate current risk metrics"""
        pass
    
    @abstractmethod
    def should_emergency_stop(self, current_balance: float, initial_balance: float) -> bool:
        """Determine if emergency stop should be triggered"""
        pass


class IExecutionEngine(ABC):
    """Interface for trade execution"""
    
    @abstractmethod
    def execute_trade(self, signal: TradingSignal, position_size: float) -> TradeResult:
        """Execute a trade"""
        pass
    
    @abstractmethod
    def close_position(self, trade_id: str) -> TradeResult:
        """Close an open position"""
        pass
    
    @abstractmethod
    def get_open_positions(self) -> List[TradeResult]:
        """Get all open positions"""
        pass
    
    @abstractmethod
    def get_account_balance(self) -> float:
        """Get current account balance"""
        pass


class IPortfolioManager(ABC):
    """Interface for portfolio management"""
    
    @abstractmethod
    def optimize_allocation(self, signals: List[TradingSignal], current_balance: float) -> Dict[str, float]:
        """Optimize capital allocation across signals"""
        pass
    
    @abstractmethod
    def rebalance_portfolio(self, current_positions: List[TradeResult]) -> List[TradingSignal]:
        """Generate rebalancing signals"""
        pass


class IPerformanceAnalyzer(ABC):
    """Interface for performance analysis"""
    
    @abstractmethod
    def calculate_returns(self, trades: List[TradeResult]) -> Dict[str, float]:
        """Calculate performance metrics"""
        pass
    
    @abstractmethod
    def generate_report(self, trades: List[TradeResult], start_balance: float) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        pass


class INotificationService(ABC):
    """Interface for notifications"""
    
    @abstractmethod
    def send_trade_notification(self, trade: TradeResult) -> None:
        """Send trade execution notification"""
        pass
    
    @abstractmethod
    def send_risk_alert(self, message: str, severity: str) -> None:
        """Send risk management alert"""
        pass


class IConfigurationManager(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    def reload_config(self) -> None:
        """Reload configuration from source"""
        pass


class IStrategyFactory(ABC):
    """Interface for strategy creation"""
    
    @abstractmethod
    def create_strategy(self, strategy_type: str, config: Dict[str, Any]) -> ISignalGenerator:
        """Create a trading strategy instance"""
        pass
    
    @abstractmethod
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy types"""
        pass


class ITradingEngine(ABC):
    """Main trading engine interface"""
    
    @abstractmethod
    def start_trading(self) -> None:
        """Start the trading engine"""
        pass
    
    @abstractmethod
    def stop_trading(self) -> None:
        """Stop the trading engine"""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        pass
    
    @abstractmethod
    def add_strategy(self, strategy: ISignalGenerator, weight: float = 1.0) -> None:
        """Add a trading strategy"""
        pass
    
    @abstractmethod
    def remove_strategy(self, strategy_name: str) -> None:
        """Remove a trading strategy"""
        pass


# Strategy-specific interfaces

class IScalpingStrategy(ISignalGenerator):
    """Interface for scalping strategies"""
    
    @abstractmethod
    def get_scalping_timeframe(self) -> str:
        """Get preferred scalping timeframe"""
        pass
    
    @abstractmethod
    def get_max_holding_time(self) -> int:
        """Get maximum holding time in minutes"""
        pass


class INewsStrategy(ISignalGenerator):
    """Interface for news-based strategies"""
    
    @abstractmethod
    def get_news_impact_threshold(self) -> str:
        """Get minimum news impact level (LOW, MEDIUM, HIGH)"""
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies for news trading"""
        pass


class ITrendStrategy(ISignalGenerator):
    """Interface for trend-following strategies"""
    
    @abstractmethod
    def get_trend_timeframes(self) -> List[str]:
        """Get timeframes used for trend analysis"""
        pass
    
    @abstractmethod
    def get_trend_strength_threshold(self) -> float:
        """Get minimum trend strength for signal generation"""
        pass


# Risk management interfaces

class IPositionSizer(ABC):
    """Interface for position sizing algorithms"""
    
    @abstractmethod
    def calculate_size(self, signal: TradingSignal, account_balance: float, risk_per_trade: float) -> float:
        """Calculate position size"""
        pass


class IDrawdownManager(ABC):
    """Interface for drawdown management"""
    
    @abstractmethod
    def should_reduce_risk(self, current_drawdown: float) -> bool:
        """Determine if risk should be reduced"""
        pass
    
    @abstractmethod
    def get_risk_multiplier(self, current_drawdown: float) -> float:
        """Get risk adjustment multiplier"""
        pass


# Execution interfaces

class IOrderManager(ABC):
    """Interface for order management"""
    
    @abstractmethod
    def place_market_order(self, pair: str, side: str, size: float) -> str:
        """Place market order"""
        pass
    
    @abstractmethod
    def place_limit_order(self, pair: str, side: str, size: float, price: float) -> str:
        """Place limit order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        pass


class ISlippageModel(ABC):
    """Interface for slippage modeling"""
    
    @abstractmethod
    def estimate_slippage(self, pair: str, size: float, market_impact: float) -> float:
        """Estimate execution slippage"""
        pass


# Data interfaces

class IMarketDataCache(ABC):
    """Interface for market data caching"""
    
    @abstractmethod
    def get_cached_data(self, pair: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached market data"""
        pass
    
    @abstractmethod
    def cache_data(self, pair: str, timeframe: str, data: pd.DataFrame) -> None:
        """Cache market data"""
        pass
    
    @abstractmethod
    def invalidate_cache(self, pair: str, timeframe: str = None) -> None:
        """Invalidate cached data"""
        pass


# Event interfaces

class IEventHandler(ABC):
    """Interface for event handling"""
    
    @abstractmethod
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle system events"""
        pass


class IEventPublisher(ABC):
    """Interface for event publishing"""
    
    @abstractmethod
    def publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Publish system event"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: IEventHandler) -> None:
        """Subscribe to events"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: IEventHandler) -> None:
        """Unsubscribe from events"""
        pass

