"""
Data Provider Factory for Dynamic Data Source Creation
Implements Factory Pattern for data providers
"""

import logging
from typing import Dict, Any, Type, List
from abc import ABC
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.interfaces import IDataProvider
from core.base_classes import BaseDataProvider


class DataProviderRegistry:
    """Registry for data provider types"""
    
    def __init__(self):
        self._providers: Dict[str, Type[IDataProvider]] = {}
        self._register_default_providers()
    
    def register_provider(self, name: str, provider_class: Type[IDataProvider]) -> None:
        """Register a data provider class"""
        if not issubclass(provider_class, IDataProvider):
            raise ValueError(f"Provider class must implement IDataProvider interface")
        
        self._providers[name.upper()] = provider_class
        logging.info(f"Registered data provider: {name}")
    
    def get_provider_class(self, name: str) -> Type[IDataProvider]:
        """Get provider class by name"""
        provider_name = name.upper()
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {name}. Available: {list(self._providers.keys())}")
        
        return self._providers[provider_name]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self._providers.keys())
    
    def _register_default_providers(self) -> None:
        """Register default data providers"""
        try:
            # Register mock provider as default
            self.register_provider('MOCK', MockDataProvider)
            self.register_provider('YAHOO', MockDataProvider)  # Use mock for now
            self.register_provider('ALPHA_VANTAGE', MockDataProvider)
            self.register_provider('TWELVE_DATA', MockDataProvider)
            self.register_provider('FCS', MockDataProvider)
            
        except ImportError as e:
            logging.warning(f"Some data providers not available: {e}")
            # Register mock provider as fallback
            self.register_provider('MOCK', MockDataProvider)


class DataProviderFactory:
    """Factory for creating data providers"""
    
    def __init__(self):
        self.registry = DataProviderRegistry()
        self.logger = logging.getLogger(__name__)
    
    def create_provider(self, provider_type: str, config: Dict[str, Any]) -> IDataProvider:
        """Create a data provider instance"""
        try:
            provider_class = self.registry.get_provider_class(provider_type)
            provider_name = config.get('name', f"{provider_type}_Provider")
            
            # Create provider instance
            provider = provider_class(provider_name, config)
            
            # Initialize if it's a BaseComponent
            if hasattr(provider, 'initialize'):
                provider.initialize()
            
            self.logger.info(f"Created data provider: {provider_name} ({provider_type})")
            return provider
            
        except Exception as e:
            self.logger.error(f"Error creating data provider {provider_type}: {e}")
            raise
    
    def create_primary_provider(self, config: Dict[str, Any]) -> IDataProvider:
        """Create primary data provider with fallback"""
        primary_type = config.get('primary_provider', 'YAHOO')
        fallback_type = config.get('fallback_provider', 'MOCK')
        
        try:
            return self.create_provider(primary_type, config)
        except Exception as e:
            self.logger.warning(f"Primary provider {primary_type} failed, using fallback: {e}")
            return self.create_provider(fallback_type, config)
    
    def create_multi_provider(self, provider_configs: List[Dict[str, Any]]) -> List[IDataProvider]:
        """Create multiple data providers"""
        providers = []
        
        for config in provider_configs:
            provider_type = config.get('type')
            if not provider_type:
                self.logger.warning("Provider config missing 'type' field, skipping")
                continue
            
            try:
                provider = self.create_provider(provider_type, config)
                providers.append(provider)
            except Exception as e:
                self.logger.error(f"Failed to create provider {provider_type}: {e}")
                continue
        
        return providers
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types"""
        return self.registry.get_available_providers()


class MockDataProvider(BaseDataProvider):
    """Mock data provider for testing"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.volatility = self.get_config('volatility', 0.01)
        self.trend = self.get_config('trend', 0.0)
    
    def _fetch_historical_data(self, pair: str, timeframe: str, periods: int):
        """Generate mock historical data"""
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate mock data
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=periods),
            periods=periods,
            freq='H'
        )
        
        # Simulate price movement
        np.random.seed(42)  # For reproducible results
        returns = np.random.normal(self.trend, self.volatility, periods)
        
        # Starting price
        base_price = self.get_config('base_price', 1.1000)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Create OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            high = price * (1 + abs(np.random.normal(0, self.volatility/2)))
            low = price * (1 - abs(np.random.normal(0, self.volatility/2)))
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            volume = np.random.randint(1000, 10000)
            
            data.append({
                'timestamp': date,
                'open': open_price,
                'high': max(open_price, high, close_price),
                'low': min(open_price, low, close_price),
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def get_live_price(self, pair: str) -> 'MarketData':
        """Get mock live price"""
        from core.interfaces import MarketData
        from datetime import datetime
        import numpy as np
        
        base_price = self.get_config('base_price', 1.1000)
        current_price = base_price * (1 + np.random.normal(0, self.volatility))
        
        return MarketData(
            pair=pair,
            timestamp=datetime.now(),
            open=current_price,
            high=current_price * 1.001,
            low=current_price * 0.999,
            close=current_price,
            volume=5000,
            bid=current_price - 0.0001,
            ask=current_price + 0.0001
        )


# Singleton factory instance
_data_provider_factory = None

def get_data_provider_factory() -> DataProviderFactory:
    """Get singleton data provider factory instance"""
    global _data_provider_factory
    if _data_provider_factory is None:
        _data_provider_factory = DataProviderFactory()
    return _data_provider_factory

