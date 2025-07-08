"""
Execution Engine Factory for Dynamic Execution Engine Creation
Implements Factory Pattern for execution engines
"""

import logging
from typing import Dict, Any, Type, List
from abc import ABC
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.interfaces import IExecutionEngine
from core.base_classes import BaseExecutionEngine


class ExecutionEngineRegistry:
    """Registry for execution engine types"""
    
    def __init__(self):
        self._engines: Dict[str, Type[IExecutionEngine]] = {}
        self._register_default_engines()
    
    def register_engine(self, name: str, engine_class: Type[IExecutionEngine]) -> None:
        """Register an execution engine class"""
        if not issubclass(engine_class, IExecutionEngine):
            raise ValueError(f"Engine class must implement IExecutionEngine interface")
        
        self._engines[name.upper()] = engine_class
        logging.info(f"Registered execution engine: {name}")
    
    def get_engine_class(self, name: str) -> Type[IExecutionEngine]:
        """Get engine class by name"""
        engine_name = name.upper()
        if engine_name not in self._engines:
            raise ValueError(f"Unknown engine: {name}. Available: {list(self._engines.keys())}")
        
        return self._engines[engine_name]
    
    def get_available_engines(self) -> List[str]:
        """Get list of available engine names"""
        return list(self._engines.keys())
    
    def _register_default_engines(self) -> None:
        """Register default execution engines"""
        try:
            # Register built-in engines
            self.register_engine('PAPER', PaperTradingEngine)
            self.register_engine('BACKTEST', BacktestEngine)
            self.register_engine('EXTREME', ExtremeExecutionEngine)
            self.register_engine('LIVE', PaperTradingEngine)  # Use paper trading for now
            
        except ImportError as e:
            logging.warning(f"Some execution engines not available: {e}")
            # Register paper trading as fallback
            self.register_engine('PAPER', PaperTradingEngine)


class ExecutionEngineFactory:
    """Factory for creating execution engines"""
    
    def __init__(self):
        self.registry = ExecutionEngineRegistry()
        self.logger = logging.getLogger(__name__)
    
    def create_engine(self, engine_type: str, config: Dict[str, Any]) -> IExecutionEngine:
        """Create an execution engine instance"""
        try:
            engine_class = self.registry.get_engine_class(engine_type)
            engine_name = config.get('name', f"{engine_type}_Engine")
            
            # Create engine instance
            engine = engine_class(engine_name, config)
            
            # Initialize if it's a BaseComponent
            if hasattr(engine, 'initialize'):
                engine.initialize()
            
            self.logger.info(f"Created execution engine: {engine_name} ({engine_type})")
            return engine
            
        except Exception as e:
            self.logger.error(f"Error creating execution engine {engine_type}: {e}")
            raise
    
    def create_paper_trading_engine(self, initial_balance: float = 100000.0, **config) -> IExecutionEngine:
        """Create paper trading engine with default settings"""
        paper_config = {
            'initial_balance': initial_balance,
            'commission_rate': 0.0001,
            'slippage_rate': 0.0001,
            **config
        }
        return self.create_engine('PAPER', paper_config)
    
    def create_live_trading_engine(self, broker: str, api_key: str, **config) -> IExecutionEngine:
        """Create live trading engine"""
        live_config = {
            'broker': broker,
            'api_key': api_key,
            'environment': 'live',
            **config
        }
        return self.create_engine('LIVE', live_config)
    
    def create_backtest_engine(self, initial_balance: float = 100000.0, **config) -> IExecutionEngine:
        """Create backtest engine"""
        backtest_config = {
            'initial_balance': initial_balance,
            'commission_rate': 0.0001,
            'slippage_rate': 0.0002,
            'realistic_execution': True,
            **config
        }
        return self.create_engine('BACKTEST', backtest_config)
    
    def create_extreme_engine(self, initial_balance: float = 1000000.0, leverage: int = 2000, **config) -> IExecutionEngine:
        """Create extreme execution engine for high-risk trading"""
        extreme_config = {
            'initial_balance': initial_balance,
            'leverage': leverage,
            'commission_rate': 0.00005,  # Lower commission for high volume
            'slippage_rate': 0.0003,     # Higher slippage for large positions
            'extreme_mode': True,
            'risk_per_trade': 0.6,       # 60% risk per trade
            **config
        }
        return self.create_engine('EXTREME', extreme_config)
    
    def get_available_engines(self) -> List[str]:
        """Get list of available engine types"""
        return self.registry.get_available_engines()


class PaperTradingEngine(BaseExecutionEngine):
    """Paper trading execution engine"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.commission_rate = self.get_config('commission_rate', 0.0001)
        self.slippage_rate = self.get_config('slippage_rate', 0.0001)
    
    def _get_execution_price(self, signal) -> float:
        """Get execution price with simulated slippage"""
        slippage = signal.price * self.slippage_rate
        if signal.signal == 'BUY':
            return signal.price + slippage
        else:  # SELL
            return signal.price - slippage
    
    def _get_exit_price(self, trade) -> float:
        """Get exit price with simulated slippage"""
        # Simulate some price movement
        import random
        price_change = random.uniform(-0.001, 0.001)
        base_price = trade.entry_price * (1 + price_change)
        
        slippage = base_price * self.slippage_rate
        if trade.signal.signal == 'BUY':
            return base_price - slippage  # Selling at bid
        else:  # SELL
            return base_price + slippage  # Buying at ask


class BacktestEngine(BaseExecutionEngine):
    """Backtesting execution engine"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.realistic_execution = self.get_config('realistic_execution', True)
        self.market_data = {}
    
    def set_market_data(self, pair: str, data) -> None:
        """Set market data for backtesting"""
        self.market_data[pair] = data
    
    def _get_execution_price(self, signal) -> float:
        """Get execution price from historical data"""
        if not self.realistic_execution:
            return signal.price
        
        # Use next bar's open price for more realistic execution
        pair_data = self.market_data.get(signal.pair)
        if pair_data is not None:
            # Find current timestamp and get next bar
            # This is simplified - real implementation would be more complex
            return signal.price
        
        return signal.price
    
    def _calculate_slippage(self, signal, position_size: float) -> float:
        """Calculate realistic slippage based on position size"""
        base_slippage = super()._calculate_slippage(signal, position_size)
        
        # Increase slippage for larger positions
        size_impact = min(position_size / 100000, 0.001)  # Max 0.1% impact
        return base_slippage + size_impact


class ExtremeExecutionEngine(BaseExecutionEngine):
    """Extreme execution engine for high-risk trading"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.leverage = self.get_config('leverage', 2000)
        self.extreme_mode = self.get_config('extreme_mode', True)
        self.risk_per_trade = self.get_config('risk_per_trade', 0.6)
        
        # Override account balance for extreme trading
        self.account_balance = self.get_config('initial_balance', 1000000.0)
        
        self.logger.warning(f"⚠️ EXTREME MODE ENABLED - Leverage: {self.leverage}:1, Risk per trade: {self.risk_per_trade*100}%")
    
    def execute_trade(self, signal, position_size: float):
        """Execute trade with extreme leverage"""
        # Apply leverage to position size
        leveraged_size = position_size * self.leverage
        
        # Log extreme trade
        self.logger.warning(f"🔥 EXTREME TRADE: {signal.pair} {signal.signal} - Size: {leveraged_size:.2f} (Leverage: {self.leverage}:1)")
        
        # Use base implementation with leveraged size
        return super().execute_trade(signal, leveraged_size)
    
    def _calculate_commission(self, position_size: float, price: float) -> float:
        """Calculate commission for extreme trading (lower rates for high volume)"""
        commission_rate = self.get_config('commission_rate', 0.00005)  # 0.005%
        return position_size * price * commission_rate
    
    def _calculate_slippage(self, signal, position_size: float) -> float:
        """Calculate slippage for extreme positions"""
        base_slippage = self.get_config('slippage_rate', 0.0003)
        
        # Higher slippage for extreme positions
        size_impact = min(position_size / 1000000, 0.002)  # Max 0.2% impact
        extreme_multiplier = 1.5 if self.extreme_mode else 1.0
        
        return (base_slippage + size_impact) * extreme_multiplier


# Singleton factory instance
_execution_factory = None

def get_execution_factory() -> ExecutionEngineFactory:
    """Get singleton execution factory instance"""
    global _execution_factory
    if _execution_factory is None:
        _execution_factory = ExecutionEngineFactory()
    return _execution_factory

