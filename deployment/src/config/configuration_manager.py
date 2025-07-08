"""
Configuration Manager Implementation
Following SOLID principles for configuration management
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod

from ..core.interfaces import IConfigurationManager


@dataclass
class TradingConfig:
    """Trading configuration data class"""
    initial_balance: float = 1000000.0
    leverage: int = 100
    risk_per_trade: float = 0.01
    max_positions: int = 5
    max_drawdown_threshold: float = 0.05
    commission_rate: float = 0.00005
    slippage_rate: float = 0.0003
    take_profit_ratio: float = 2.0
    data_provider: str = "YAHOO"
    execution_engine: str = "PAPER"
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    broker_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_risk_per_trade: float = 0.02
    max_total_exposure: float = 0.1
    max_drawdown_stop: float = 0.05
    position_sizing_method: str = "FIXED_PERCENTAGE"
    stop_loss_method: str = "ATR"
    max_consecutive_losses: int = 5
    min_win_rate: float = 0.3
    min_confidence: float = 70.0


@dataclass
class DataConfig:
    """Data provider configuration"""
    primary_provider: str = "YAHOO"
    backup_providers: List[str] = field(default_factory=lambda: ["HISTDATA", "METALS_API"])
    cache_enabled: bool = True
    cache_duration_minutes: int = 60
    historical_data_path: str = "./data/historical"
    symbols: List[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "CL=F"])


class ConfigurationManager(IConfigurationManager):
    """
    Configuration Manager implementing SOLID principles
    - Single Responsibility: Manages configuration only
    - Open/Closed: Extensible for new config types
    - Liskov Substitution: Implements IConfigurationManager interface
    - Interface Segregation: Focused interface
    - Dependency Inversion: Depends on abstractions
    """
    
    def __init__(self, config_file: str = "config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.config_file = Path(config_file)
        self._config_data: Dict[str, Any] = {}
        self._trading_config: Optional[TradingConfig] = None
        self._risk_config: Optional[RiskConfig] = None
        self._data_config: Optional[DataConfig] = None
        
        # Load configuration on initialization
        self.reload_config()
    
    def reload_config(self) -> None:
        """Reload configuration from source"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self._config_data = yaml.safe_load(f) or {}
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.warning(f"Config file {self.config_file} not found, using defaults")
                self._config_data = {}
            
            # Initialize config objects
            self._initialize_configs()
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._config_data = {}
            self._initialize_configs()
    
    def _initialize_configs(self) -> None:
        """Initialize configuration objects from loaded data"""
        # Trading configuration
        trading_data = self._config_data.copy()
        self._trading_config = TradingConfig(
            initial_balance=trading_data.get('initial_balance', 1000000.0),
            leverage=trading_data.get('leverage', 100),
            risk_per_trade=trading_data.get('risk_per_trade', 0.01),
            max_positions=trading_data.get('max_positions', 5),
            max_drawdown_threshold=trading_data.get('max_drawdown_threshold', 0.05),
            commission_rate=trading_data.get('commission_rate', 0.00005),
            slippage_rate=trading_data.get('slippage_rate', 0.0003),
            take_profit_ratio=trading_data.get('take_profit_ratio', 2.0),
            data_provider=trading_data.get('data_provider', 'YAHOO'),
            execution_engine=trading_data.get('execution_engine', 'PAPER'),
            strategies=trading_data.get('strategies', []),
            broker_config=trading_data.get('broker_config', {})
        )
        
        # Risk configuration
        self._risk_config = RiskConfig(
            max_risk_per_trade=trading_data.get('risk_per_trade', 0.02),
            max_total_exposure=trading_data.get('max_total_exposure', 0.1),
            max_drawdown_stop=trading_data.get('max_drawdown_threshold', 0.05),
            position_sizing_method=trading_data.get('position_sizing_method', 'FIXED_PERCENTAGE'),
            stop_loss_method=trading_data.get('stop_loss_method', 'ATR'),
            max_consecutive_losses=trading_data.get('MAX_CONSECUTIVE_LOSSES', 5),
            min_win_rate=trading_data.get('MIN_WIN_RATE', 0.3),
            min_confidence=trading_data.get('MIN_CONFIDENCE', 70.0)
        )
        
        # Data configuration
        forex_symbols = trading_data.get('FOREX_SYMBOLS', ["EURUSD", "GBPUSD", "USDJPY"])
        additional_symbols = ["XAUUSD", "CL=F"]  # Gold and Oil
        all_symbols = forex_symbols + additional_symbols
        
        self._data_config = DataConfig(
            primary_provider=trading_data.get('data_provider', 'YAHOO'),
            symbols=all_symbols,
            historical_data_path=trading_data.get('historical_data_path', './data/historical')
        )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config_data.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config_data[key] = value
        self._initialize_configs()  # Reinitialize configs
    
    def get_trading_config(self) -> TradingConfig:
        """Get trading configuration"""
        return self._trading_config
    
    def get_risk_config(self) -> RiskConfig:
        """Get risk management configuration"""
        return self._risk_config
    
    def get_data_config(self) -> DataConfig:
        """Get data provider configuration"""
        return self._data_config
    
    def load_config_preset(self, preset_name: str) -> None:
        """Load a configuration preset"""
        presets = {
            'conservative': {
                'risk_per_trade': 0.01,
                'leverage': 50,
                'max_positions': 3,
                'max_drawdown_threshold': 0.03
            },
            'moderate': {
                'risk_per_trade': 0.02,
                'leverage': 100,
                'max_positions': 5,
                'max_drawdown_threshold': 0.05
            },
            'aggressive': {
                'risk_per_trade': 0.05,
                'leverage': 200,
                'max_positions': 10,
                'max_drawdown_threshold': 0.1
            },
            'extreme': {
                'risk_per_trade': 0.6,
                'leverage': 2000,
                'max_positions': 20,
                'max_drawdown_threshold': 0.8,
                'extreme_mode': True,
                'martingale_enabled': True,
                'scalping_enabled': True,
                'news_trading_enabled': True
            }
        }
        
        if preset_name in presets:
            preset_config = presets[preset_name]
            for key, value in preset_config.items():
                self.set_config(key, value)
            self.logger.info(f"Loaded {preset_name} configuration preset")
        else:
            self.logger.warning(f"Unknown preset: {preset_name}")
    
    def load_default_config(self) -> None:
        """Load default configuration"""
        self.load_config_preset('moderate')
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config_data, f, default_flow_style=False)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def create_extreme_preset() -> None:
    """Create extreme trading preset for maximum profit potential"""
    config_manager = get_config_manager()
    
    extreme_config = {
        'initial_balance': 1000000.0,
        'leverage': 2000,
        'risk_per_trade': 0.6,  # 60% risk per trade for extreme mode
        'max_positions': 20,
        'max_drawdown_threshold': 0.8,  # 80% drawdown threshold
        'commission_rate': 0.00005,
        'slippage_rate': 0.0003,
        'take_profit_ratio': 2.0,
        'data_provider': 'YAHOO',
        'execution_engine': 'EXTREME',
        'extreme_mode': True,
        'martingale_enabled': True,
        'scalping_enabled': True,
        'news_trading_enabled': True,
        'position_sizing_method': 'FIXED_PERCENTAGE',
        'stop_loss_method': 'ATR',
        'MAX_CONSECUTIVE_LOSSES': 5,
        'MIN_WIN_RATE': 0.3,
        'MIN_CONFIDENCE': 70,
        'strategies': [
            {
                'name': 'Scalper_1',
                'type': 'EXTREME_SCALPING',
                'timeframe': '1m',
                'confidence_threshold': 0.95,
                'max_holding_minutes': 1
            },
            {
                'name': 'News_Trader_1',
                'type': 'NEWS_EXPLOSION',
                'news_impact_threshold': 'HIGH',
                'reaction_time_seconds': 3
            },
            {
                'name': 'Momentum_1',
                'type': 'BREAKOUT_MOMENTUM',
                'momentum_threshold': 0.03,
                'volume_confirmation': True
            },
            {
                'name': 'Recovery_1',
                'type': 'MARTINGALE_EXTREME',
                'max_levels': 8,
                'recovery_target': 0.1
            }
        ],
        'strategy_weights': {
            'Scalper_1': 0.4,
            'News_Trader_1': 0.3,
            'Momentum_1': 0.2,
            'Recovery_1': 0.1
        }
    }
    
    # Update configuration
    for key, value in extreme_config.items():
        config_manager.set_config(key, value)
    
    # Save the extreme preset
    config_manager.save_config()
    
    logging.getLogger(__name__).info("Extreme trading preset created and saved")


# Configuration validation
class ConfigValidator:
    """Validates configuration settings"""
    
    @staticmethod
    def validate_trading_config(config: TradingConfig) -> List[str]:
        """Validate trading configuration and return list of errors"""
        errors = []
        
        if config.initial_balance <= 0:
            errors.append("Initial balance must be positive")
        
        if config.leverage < 1 or config.leverage > 5000:
            errors.append("Leverage must be between 1 and 5000")
        
        if config.risk_per_trade < 0 or config.risk_per_trade > 1:
            errors.append("Risk per trade must be between 0 and 1")
        
        if config.max_positions < 1:
            errors.append("Max positions must be at least 1")
        
        if config.max_drawdown_threshold < 0 or config.max_drawdown_threshold > 1:
            errors.append("Max drawdown threshold must be between 0 and 1")
        
        return errors
    
    @staticmethod
    def validate_risk_config(config: RiskConfig) -> List[str]:
        """Validate risk configuration and return list of errors"""
        errors = []
        
        if config.max_risk_per_trade < 0 or config.max_risk_per_trade > 1:
            errors.append("Max risk per trade must be between 0 and 1")
        
        if config.max_total_exposure < 0 or config.max_total_exposure > 1:
            errors.append("Max total exposure must be between 0 and 1")
        
        if config.min_confidence < 0 or config.min_confidence > 100:
            errors.append("Min confidence must be between 0 and 100")
        
        return errors

