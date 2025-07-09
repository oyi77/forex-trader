"""
Strategy Factory for Dynamic Strategy Creation
Implements Factory Pattern and follows SOLID principles
"""

import logging
from typing import Dict, List, Any, Type
from abc import ABC
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.interfaces import ISignalGenerator, IStrategyFactory
from core.base_classes import BaseSignalGenerator
# Strategy imports will be handled dynamically to avoid import errors


class StrategyRegistry:
    """Registry for strategy types"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[ISignalGenerator]] = {}
        self._register_default_strategies()
    
    def register_strategy(self, name: str, strategy_class: Type[ISignalGenerator]) -> None:
        """Register a strategy class"""
        try:
            # Use local import to avoid circular import issues
            from ..core.interfaces import ISignalGenerator as LocalISignalGenerator
            
            if not issubclass(strategy_class, LocalISignalGenerator):
                raise ValueError(f"Strategy class must implement ISignalGenerator interface")
            
            self._strategies[name.upper()] = strategy_class
            logging.info(f"Registered strategy: {name}")
        except Exception as e:
            logging.error(f"Error registering {name}: {e}")
            raise
    
    def get_strategy_class(self, name: str) -> Type[ISignalGenerator]:
        """Get strategy class by name"""
        strategy_name = name.upper()
        if strategy_name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}. Available: {list(self._strategies.keys())}")
        
        return self._strategies[strategy_name]
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        return list(self._strategies.keys())
    
    def _register_default_strategies(self) -> None:
        """Register default strategies"""
        try:
            # Import enhanced strategies
            from ..strategies.enhanced_strategies import (
                EnhancedRSIStrategy, EnhancedMAStrategy, EnhancedBreakoutStrategy
            )
            
            # Register enhanced strategies
            self.register_strategy('RSI', EnhancedRSIStrategy)
            self.register_strategy('MA_CROSSOVER', EnhancedMAStrategy)
            self.register_strategy('BREAKOUT', EnhancedBreakoutStrategy)
            self.register_strategy('SCALPING', EnhancedBreakoutStrategy)  # Use breakout for scalping
            self.register_strategy('NEWS', EnhancedMAStrategy)  # Use MA for news
            self.register_strategy('MARTINGALE', EnhancedRSIStrategy)  # Use RSI for martingale
                
        except ImportError as e:
            logging.warning(f"Enhanced strategies not available: {e}")
            # Fallback to base strategy
            from core.base_classes import BaseSignalGenerator
            self.register_strategy('MOCK', BaseSignalGenerator)


class StrategyFactory(IStrategyFactory):
    """Factory for creating trading strategies"""
    
    def __init__(self):
        self.registry = StrategyRegistry()
        self.logger = logging.getLogger(__name__)
    
    def create_strategy(self, strategy_type: str, config: Dict[str, Any]) -> ISignalGenerator:
        """Create a strategy instance"""
        try:
            strategy_class = self.registry.get_strategy_class(strategy_type)
            strategy_name = config.get('name', f"{strategy_type}_Strategy")
            
            # Create strategy instance
            strategy = strategy_class(strategy_name, config)
            
            # Initialize if it's a BaseComponent
            if hasattr(strategy, 'initialize'):
                strategy.initialize()
            
            self.logger.info(f"Created strategy: {strategy_name} ({strategy_type})")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error creating strategy {strategy_type}: {e}")
            raise
    
    def create_multiple_strategies(self, strategy_configs: List[Dict[str, Any]]) -> List[ISignalGenerator]:
        """Create multiple strategies from configurations"""
        strategies = []
        
        for config in strategy_configs:
            strategy_type = config.get('type')
            if not strategy_type:
                self.logger.warning("Strategy config missing 'type' field, skipping")
                continue
            
            try:
                strategy = self.create_strategy(strategy_type, config)
                strategies.append(strategy)
            except Exception as e:
                self.logger.error(f"Failed to create strategy {strategy_type}: {e}")
                continue
        
        return strategies
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy types"""
        return self.registry.get_available_strategies()
    
    def register_custom_strategy(self, name: str, strategy_class: Type[ISignalGenerator]) -> None:
        """Register a custom strategy"""
        self.registry.register_strategy(name, strategy_class)


class StrategyBuilder:
    """Builder for complex strategy configurations"""
    
    def __init__(self, factory: StrategyFactory):
        self.factory = factory
        self.config = {}
    
    def set_type(self, strategy_type: str) -> 'StrategyBuilder':
        """Set strategy type"""
        self.config['type'] = strategy_type
        return self
    
    def set_name(self, name: str) -> 'StrategyBuilder':
        """Set strategy name"""
        self.config['name'] = name
        return self
    
    def set_timeframe(self, timeframe: str) -> 'StrategyBuilder':
        """Set strategy timeframe"""
        self.config['timeframe'] = timeframe
        return self
    
    def set_parameters(self, **params) -> 'StrategyBuilder':
        """Set strategy parameters"""
        self.config.update(params)
        return self
    
    def set_risk_config(self, max_risk: float, confidence_threshold: float) -> 'StrategyBuilder':
        """Set risk configuration"""
        self.config.update({
            'max_risk_per_trade': max_risk,
            'confidence_threshold': confidence_threshold
        })
        return self
    
    def build(self) -> ISignalGenerator:
        """Build the strategy"""
        if 'type' not in self.config:
            raise ValueError("Strategy type must be specified")
        
        return self.factory.create_strategy(self.config['type'], self.config)


class StrategyComposer:
    """Composer for creating strategy combinations"""
    
    def __init__(self, factory: StrategyFactory):
        self.factory = factory
        self.strategies: List[Dict[str, Any]] = []
    
    def add_strategy(self, strategy_type: str, weight: float = 1.0, **config) -> 'StrategyComposer':
        """Add a strategy to the composition"""
        strategy_config = {
            'type': strategy_type,
            'weight': weight,
            **config
        }
        self.strategies.append(strategy_config)
        return self
    
    def add_rsi_strategy(self, period: int = 14, oversold: int = 30, overbought: int = 70, weight: float = 1.0) -> 'StrategyComposer':
        """Add RSI strategy with specific parameters"""
        return self.add_strategy(
            'RSI',
            weight=weight,
            rsi_period=period,
            oversold_threshold=oversold,
            overbought_threshold=overbought
        )
    
    def add_ma_crossover_strategy(self, fast_period: int = 10, slow_period: int = 20, weight: float = 1.0) -> 'StrategyComposer':
        """Add MA Crossover strategy with specific parameters"""
        return self.add_strategy(
            'MA_CROSSOVER',
            weight=weight,
            fast_period=fast_period,
            slow_period=slow_period
        )
    
    def add_breakout_strategy(self, lookback_period: int = 20, breakout_threshold: float = 0.02, weight: float = 1.0) -> 'StrategyComposer':
        """Add Breakout strategy with specific parameters"""
        return self.add_strategy(
            'BREAKOUT',
            weight=weight,
            lookback_period=lookback_period,
            breakout_threshold=breakout_threshold
        )
    
    def add_scalping_strategy(self, timeframe: str = '1m', max_holding_minutes: int = 5, weight: float = 1.0) -> 'StrategyComposer':
        """Add Scalping strategy with specific parameters"""
        return self.add_strategy(
            'SCALPING',
            weight=weight,
            timeframe=timeframe,
            max_holding_minutes=max_holding_minutes
        )
    
    def build_portfolio(self) -> List[ISignalGenerator]:
        """Build the strategy portfolio"""
        return self.factory.create_multiple_strategies(self.strategies)


class ExtremeStrategyFactory(StrategyFactory):
    """Factory for extreme high-risk strategies"""
    
    def __init__(self):
        super().__init__()
        self._register_extreme_strategies()
    
    def _register_extreme_strategies(self) -> None:
        """Register extreme strategies"""
        from core.base_classes import BaseSignalGenerator
        
        # Create extreme strategy classes that inherit from base strategies
        class ExtremeScalpingStrategy(BaseSignalGenerator):
            def __init__(self, name: str, config: Dict[str, Any] = None):
                super().__init__(name, config)
                self.risk_multiplier = config.get('risk_multiplier', 10.0) if config else 10.0
                self.confidence_threshold = config.get('confidence_threshold', 0.95) if config else 0.95
                
            def generate_signal(self, data, pair: str):
                # Extreme scalping logic would go here
                return None
        
        class NewsExplosionStrategy(BaseSignalGenerator):
            def __init__(self, name: str, config: Dict[str, Any] = None):
                super().__init__(name, config)
                self.risk_multiplier = config.get('risk_multiplier', 20.0) if config else 20.0
                self.news_impact_threshold = config.get('news_impact_threshold', 'HIGH') if config else 'HIGH'
                
            def generate_signal(self, data, pair: str):
                # News explosion logic would go here
                return None
        
        class BreakoutMomentumStrategy(BaseSignalGenerator):
            def __init__(self, name: str, config: Dict[str, Any] = None):
                super().__init__(name, config)
                self.risk_multiplier = config.get('risk_multiplier', 15.0) if config else 15.0
                self.momentum_threshold = config.get('momentum_threshold', 0.05) if config else 0.05
                
            def generate_signal(self, data, pair: str):
                # Breakout momentum logic would go here
                return None
        
        class MartingaleExtremeStrategy(BaseSignalGenerator):
            def __init__(self, name: str, config: Dict[str, Any] = None):
                super().__init__(name, config)
                self.risk_multiplier = config.get('risk_multiplier', 50.0) if config else 50.0
                self.max_martingale_levels = config.get('max_levels', 10) if config else 10
                
            def generate_signal(self, data, pair: str):
                # Martingale extreme logic would go here
                return None
    
    def _register_extreme_strategies(self) -> None:
        """Register extreme strategies for maximum leverage trading"""
        try:
            # Import extreme strategies
            from ..strategies.enhanced_strategies import (
                ExtremeScalpingStrategy, NewsExplosionStrategy, 
                BreakoutMomentumStrategy, MartingaleExtremeStrategy
            )
            
            # Import God Mode strategies
            from ..strategies.god_mode_strategies import (
                GodModeScalpingStrategy,
                MartingaleGodStrategy,
                VolatilityGodStrategy,
                TrendGodStrategy,
                AllInGodStrategy
            )
            
            # Register God Mode strategies
            self.register_strategy("GOD_MODE_SCALPING", GodModeScalpingStrategy)
            self.register_strategy("MARTINGALE_GOD", MartingaleGodStrategy)
            self.register_strategy("VOLATILITY_GOD", VolatilityGodStrategy)
            self.register_strategy("TREND_GOD", TrendGodStrategy)
            self.register_strategy("ALL_IN_GOD", AllInGodStrategy)
            
            # Import ultra-aggressive strategies
            from ..strategies.ultra_aggressive_strategies import (
                AlwaysTradingStrategy,
                ScalpingMachineStrategy,
                MomentumBlasterStrategy,
                VolatilityHunterStrategy,
                RandomWalkStrategy,
                AllInStrategy
            )
            
            # Register ultra-aggressive strategies
            self.register_strategy("ALWAYS_TRADING", AlwaysTradingStrategy)
            self.register_strategy("SCALPING_MACHINE", ScalpingMachineStrategy)
            self.register_strategy("MOMENTUM_BLASTER", MomentumBlasterStrategy)
            self.register_strategy("VOLATILITY_HUNTER", VolatilityHunterStrategy)
            self.register_strategy("RANDOM_WALK", RandomWalkStrategy)
            self.register_strategy("ALL_IN", AllInStrategy)
            
            # Register enhanced extreme strategies
            self.register_strategy("EXTREME_SCALPING", ExtremeScalpingStrategy)
            self.register_strategy("NEWS_EXPLOSION", NewsExplosionStrategy)
            self.register_strategy("BREAKOUT_MOMENTUM", BreakoutMomentumStrategy)
            self.register_strategy("MARTINGALE_EXTREME", MartingaleExtremeStrategy)          
        except ImportError:
            # Register the local extreme strategies as fallback
            self.registry.register_strategy('EXTREME_SCALPING', ExtremeScalpingStrategy)
            self.registry.register_strategy('NEWS_EXPLOSION', NewsExplosionStrategy)
            self.registry.register_strategy('BREAKOUT_MOMENTUM', BreakoutMomentumStrategy)
            self.registry.register_strategy('MARTINGALE_EXTREME', MartingaleExtremeStrategy)
        
        self.logger.info("Extreme strategies registered successfully")


def create_conservative_portfolio(factory: StrategyFactory) -> List[ISignalGenerator]:
    """Create a conservative strategy portfolio"""
    composer = StrategyComposer(factory)
    return (composer
            .add_rsi_strategy(period=21, weight=0.3)
            .add_ma_crossover_strategy(fast_period=12, slow_period=26, weight=0.4)
            .add_breakout_strategy(lookback_period=30, weight=0.3)
            .build_portfolio())


def create_aggressive_portfolio(factory: StrategyFactory) -> List[ISignalGenerator]:
    """Create an aggressive strategy portfolio"""
    composer = StrategyComposer(factory)
    return (composer
            .add_scalping_strategy(weight=0.4)
            .add_breakout_strategy(lookback_period=10, breakout_threshold=0.01, weight=0.3)
            .add_strategy('NEWS', weight=0.3, news_impact_threshold='MEDIUM')
            .build_portfolio())


def create_extreme_portfolio(factory: ExtremeStrategyFactory) -> List[ISignalGenerator]:
    """Create an extreme high-risk portfolio"""
    try:
        return factory.create_multiple_strategies([
            {
                'type': 'EXTREME_SCALPING',
                'name': 'Extreme_Scalper_1',
                'timeframe': '1m',
                'risk_per_trade': 0.6,
                'confidence_threshold': 0.95
            },
            {
                'type': 'NEWS_EXPLOSION',
                'name': 'News_Trader_1',
                'risk_per_trade': 0.8,
                'reaction_time_seconds': 3
            },
            {
                'type': 'BREAKOUT_MOMENTUM',
                'name': 'Momentum_Trader_1',
                'risk_per_trade': 0.7,
                'momentum_threshold': 0.03
            },
            {
                'type': 'MARTINGALE_EXTREME',
                'name': 'Martingale_Recovery_1',
                'risk_per_trade': 0.5,
                'max_levels': 8
            }
        ])
    except Exception as e:
        logging.error(f"Error creating extreme portfolio: {e}")
        # Fallback to aggressive portfolio
        return create_aggressive_portfolio(factory)


# Singleton factory instance
_strategy_factory = None

def get_strategy_factory() -> StrategyFactory:
    """Get singleton strategy factory instance"""
    global _strategy_factory
    if _strategy_factory is None:
        _strategy_factory = StrategyFactory()
    return _strategy_factory


def get_extreme_strategy_factory() -> ExtremeStrategyFactory:
    """Get extreme strategy factory instance"""
    return ExtremeStrategyFactory()

