"""
Data Providers Integration Module for Forex Trading Bot
Integrates multiple data sources for real-time and historical forex data
"""

import requests
import pandas as pd
import numpy as np
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class DataProvider(Enum):
    TWELVE_DATA = "twelve_data"
    FCS_API = "fcs_api"
    FREE_FOREX_API = "free_forex_api"
    OANDA = "oanda"
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None

@dataclass
class ProviderConfig:
    """Configuration for data provider"""
    name: str
    api_key: Optional[str]
    base_url: str
    rate_limit: int  # requests per minute
    free_tier_limit: int  # daily limit for free tier
    supports_realtime: bool
    supports_historical: bool
    supported_symbols: List[str]

class DataProviderManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger('DataProviderManager')
        
        # Initialize providers
        self.providers = self._initialize_providers()
        self.active_provider = None
        self.fallback_providers = []
        
        # Rate limiting
        self.request_counts = {}
        self.last_request_time = {}
        
        # Data cache
        self.data_cache = {}
        self.cache_expiry = {}
        
        # Connection pools for async requests
        self.session = None
        
        self.logger.info("Data Provider Manager initialized")
    
    def _initialize_providers(self) -> Dict[str, ProviderConfig]:
        """Initialize available data providers"""
        providers = {
            DataProvider.TWELVE_DATA.value: ProviderConfig(
                name="Twelve Data",
                api_key=self.config.get('TWELVE_DATA_API_KEY'),
                base_url="https://api.twelvedata.com",
                rate_limit=8,  # 8 requests per minute for free tier
                free_tier_limit=800,  # 800 requests per day
                supports_realtime=True,
                supports_historical=True,
                supported_symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'NZDUSD', 'USDCAD']
            ),
            
            DataProvider.FCS_API.value: ProviderConfig(
                name="FCS API",
                api_key=self.config.get('FCS_API_KEY'),
                base_url="https://fcsapi.com/api-v3",
                rate_limit=60,  # 60 requests per minute
                free_tier_limit=500,  # 500 requests per day
                supports_realtime=True,
                supports_historical=True,
                supported_symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'NZDUSD', 'USDCAD']
            ),
            
            DataProvider.FREE_FOREX_API.value: ProviderConfig(
                name="Free Forex API",
                api_key=None,
                base_url="https://www.freeforexapi.com/api",
                rate_limit=60,  # 60 requests per minute
                free_tier_limit=1000,  # 1000 requests per day
                supports_realtime=True,
                supports_historical=False,
                supported_symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'NZDUSD', 'USDCAD']
            ),
            
            DataProvider.ALPHA_VANTAGE.value: ProviderConfig(
                name="Alpha Vantage",
                api_key=self.config.get('ALPHA_VANTAGE_API_KEY'),
                base_url="https://www.alphavantage.co/query",
                rate_limit=5,  # 5 requests per minute for free tier
                free_tier_limit=100,  # 100 requests per day
                supports_realtime=True,
                supports_historical=True,
                supported_symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'NZDUSD', 'USDCAD']
            )
        }
        
        return providers
    
    async def initialize_session(self):
        """Initialize async HTTP session"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Close async HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def set_primary_provider(self, provider: DataProvider):
        """Set primary data provider"""
        if provider.value in self.providers:
            self.active_provider = provider
            self.logger.info(f"Primary provider set to: {provider.value}")
        else:
            self.logger.error(f"Provider {provider.value} not available")
    
    def add_fallback_provider(self, provider: DataProvider):
        """Add fallback data provider"""
        if provider.value in self.providers and provider not in self.fallback_providers:
            self.fallback_providers.append(provider)
            self.logger.info(f"Added fallback provider: {provider.value}")
    
    async def get_real_time_data(self, symbol: str) -> Optional[MarketData]:
        """Get real-time market data for a symbol"""
        try:
            # Try primary provider first
            if self.active_provider:
                data = await self._fetch_real_time_data(symbol, self.active_provider)
                if data:
                    return data
            
            # Try fallback providers
            for provider in self.fallback_providers:
                try:
                    data = await self._fetch_real_time_data(symbol, provider)
                    if data:
                        self.logger.info(f"Used fallback provider: {provider.value}")
                        return data
                except Exception as e:
                    self.logger.warning(f"Fallback provider {provider.value} failed: {e}")
                    continue
            
            # If all providers fail, return cached data if available
            cached_data = self._get_cached_data(symbol)
            if cached_data:
                self.logger.warning(f"Using cached data for {symbol}")
                return cached_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting real-time data for {symbol}: {e}")
            return None
    
    async def _fetch_real_time_data(self, symbol: str, provider: DataProvider) -> Optional[MarketData]:
        """Fetch real-time data from specific provider"""
        provider_config = self.providers[provider.value]
        
        # Check rate limits
        if not self._check_rate_limit(provider.value):
            raise Exception(f"Rate limit exceeded for {provider.value}")
        
        # Fetch data based on provider
        if provider == DataProvider.TWELVE_DATA:
            return await self._fetch_twelve_data_realtime(symbol, provider_config)
        elif provider == DataProvider.FCS_API:
            return await self._fetch_fcs_api_realtime(symbol, provider_config)
        elif provider == DataProvider.FREE_FOREX_API:
            return await self._fetch_free_forex_api_realtime(symbol, provider_config)
        elif provider == DataProvider.ALPHA_VANTAGE:
            return await self._fetch_alpha_vantage_realtime(symbol, provider_config)
        else:
            return None
    
    async def _fetch_twelve_data_realtime(self, symbol: str, config: ProviderConfig) -> Optional[MarketData]:
        """Fetch real-time data from Twelve Data API"""
        try:
            await self.initialize_session()
            
            # Convert symbol format (e.g., EURUSD -> EUR/USD)
            formatted_symbol = f"{symbol[:3]}/{symbol[3:]}"
            
            params = {
                'symbol': formatted_symbol,
                'interval': '1min',
                'outputsize': 1
            }
            
            if config.api_key:
                params['apikey'] = config.api_key
            
            url = f"{config.base_url}/time_series"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'values' in data and data['values']:
                        latest = data['values'][0]
                        
                        market_data = MarketData(
                            symbol=symbol,
                            timestamp=datetime.strptime(latest['datetime'], '%Y-%m-%d %H:%M:%S'),
                            open=float(latest['open']),
                            high=float(latest['high']),
                            low=float(latest['low']),
                            close=float(latest['close']),
                            volume=int(latest.get('volume', 0))
                        )
                        
                        self._cache_data(symbol, market_data)
                        self._update_request_count(config.name)
                        
                        return market_data
                else:
                    self.logger.error(f"Twelve Data API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching from Twelve Data: {e}")
        
        return None
    
    async def _fetch_fcs_api_realtime(self, symbol: str, config: ProviderConfig) -> Optional[MarketData]:
        """Fetch real-time data from FCS API"""
        try:
            await self.initialize_session()
            
            params = {
                'symbol': symbol,
                'access_key': config.api_key
            } if config.api_key else {'symbol': symbol}
            
            url = f"{config.base_url}/forex/latest"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') and 'response' in data:
                        forex_data = data['response'][0] if data['response'] else None
                        
                        if forex_data:
                            market_data = MarketData(
                                symbol=symbol,
                                timestamp=datetime.now(),
                                open=float(forex_data.get('o', 0)),
                                high=float(forex_data.get('h', 0)),
                                low=float(forex_data.get('l', 0)),
                                close=float(forex_data.get('c', 0)),
                                volume=0,  # FCS API doesn't provide volume for forex
                                bid=float(forex_data.get('b', 0)),
                                ask=float(forex_data.get('a', 0))
                            )
                            
                            if market_data.bid and market_data.ask:
                                market_data.spread = market_data.ask - market_data.bid
                            
                            self._cache_data(symbol, market_data)
                            self._update_request_count(config.name)
                            
                            return market_data
                else:
                    self.logger.error(f"FCS API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching from FCS API: {e}")
        
        return None
    
    async def _fetch_free_forex_api_realtime(self, symbol: str, config: ProviderConfig) -> Optional[MarketData]:
        """Fetch real-time data from Free Forex API"""
        try:
            await self.initialize_session()
            
            # Free Forex API uses different symbol format
            formatted_symbol = f"{symbol[:3]}{symbol[3:]}"
            
            url = f"{config.base_url}/live"
            params = {'pairs': formatted_symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'rates' in data and formatted_symbol in data['rates']:
                        rate_data = data['rates'][formatted_symbol]
                        
                        market_data = MarketData(
                            symbol=symbol,
                            timestamp=datetime.fromtimestamp(data.get('timestamp', time.time())),
                            open=float(rate_data.get('rate', 0)),
                            high=float(rate_data.get('rate', 0)),
                            low=float(rate_data.get('rate', 0)),
                            close=float(rate_data.get('rate', 0)),
                            volume=0
                        )
                        
                        self._cache_data(symbol, market_data)
                        self._update_request_count(config.name)
                        
                        return market_data
                else:
                    self.logger.error(f"Free Forex API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching from Free Forex API: {e}")
        
        return None
    
    async def _fetch_alpha_vantage_realtime(self, symbol: str, config: ProviderConfig) -> Optional[MarketData]:
        """Fetch real-time data from Alpha Vantage API"""
        try:
            await self.initialize_session()
            
            # Alpha Vantage uses different symbol format
            formatted_symbol = f"{symbol[:3]}/{symbol[3:]}"
            
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol[:3],
                'to_currency': symbol[3:],
                'apikey': config.api_key
            } if config.api_key else {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol[:3],
                'to_currency': symbol[3:]
            }
            
            async with self.session.get(config.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'Realtime Currency Exchange Rate' in data:
                        rate_data = data['Realtime Currency Exchange Rate']
                        
                        rate = float(rate_data.get('5. Exchange Rate', 0))
                        
                        market_data = MarketData(
                            symbol=symbol,
                            timestamp=datetime.strptime(
                                rate_data.get('6. Last Refreshed', ''),
                                '%Y-%m-%d %H:%M:%S'
                            ),
                            open=rate,
                            high=rate,
                            low=rate,
                            close=rate,
                            volume=0,
                            bid=float(rate_data.get('8. Bid Price', rate)),
                            ask=float(rate_data.get('9. Ask Price', rate))
                        )
                        
                        self._cache_data(symbol, market_data)
                        self._update_request_count(config.name)
                        
                        return market_data
                else:
                    self.logger.error(f"Alpha Vantage API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching from Alpha Vantage: {e}")
        
        return None
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1H', 
                                periods: int = 100) -> Optional[pd.DataFrame]:
        """Get historical market data"""
        try:
            # Try primary provider first
            if self.active_provider:
                data = await self._fetch_historical_data(symbol, timeframe, periods, self.active_provider)
                if data is not None and not data.empty:
                    return data
            
            # Try fallback providers
            for provider in self.fallback_providers:
                try:
                    data = await self._fetch_historical_data(symbol, timeframe, periods, provider)
                    if data is not None and not data.empty:
                        self.logger.info(f"Used fallback provider for historical data: {provider.value}")
                        return data
                except Exception as e:
                    self.logger.warning(f"Fallback provider {provider.value} failed for historical data: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None
    
    async def _fetch_historical_data(self, symbol: str, timeframe: str, periods: int,
                                   provider: DataProvider) -> Optional[pd.DataFrame]:
        """Fetch historical data from specific provider"""
        provider_config = self.providers[provider.value]
        
        # Check if provider supports historical data
        if not provider_config.supports_historical:
            return None
        
        # Check rate limits
        if not self._check_rate_limit(provider.value):
            raise Exception(f"Rate limit exceeded for {provider.value}")
        
        # Fetch data based on provider
        if provider == DataProvider.TWELVE_DATA:
            return await self._fetch_twelve_data_historical(symbol, timeframe, periods, provider_config)
        elif provider == DataProvider.FCS_API:
            return await self._fetch_fcs_api_historical(symbol, timeframe, periods, provider_config)
        elif provider == DataProvider.ALPHA_VANTAGE:
            return await self._fetch_alpha_vantage_historical(symbol, timeframe, periods, provider_config)
        else:
            return None
    
    async def _fetch_twelve_data_historical(self, symbol: str, timeframe: str, periods: int,
                                          config: ProviderConfig) -> Optional[pd.DataFrame]:
        """Fetch historical data from Twelve Data"""
        try:
            await self.initialize_session()
            
            # Convert symbol and timeframe format
            formatted_symbol = f"{symbol[:3]}/{symbol[3:]}"
            interval_map = {'1M': '1min', '5M': '5min', '15M': '15min', '1H': '1h', '4H': '4h', '1D': '1day'}
            interval = interval_map.get(timeframe, '1h')
            
            params = {
                'symbol': formatted_symbol,
                'interval': interval,
                'outputsize': periods
            }
            
            if config.api_key:
                params['apikey'] = config.api_key
            
            url = f"{config.base_url}/time_series"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'values' in data and data['values']:
                        df = pd.DataFrame(data['values'])
                        
                        # Convert data types
                        df['datetime'] = pd.to_datetime(df['datetime'])
                        df['open'] = df['open'].astype(float)
                        df['high'] = df['high'].astype(float)
                        df['low'] = df['low'].astype(float)
                        df['close'] = df['close'].astype(float)
                        df['volume'] = df['volume'].astype(int)
                        
                        # Rename columns to standard format
                        df = df.rename(columns={'datetime': 'timestamp'})
                        df = df.set_index('timestamp').sort_index()
                        
                        self._update_request_count(config.name)
                        
                        return df
                else:
                    self.logger.error(f"Twelve Data historical API error: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error fetching historical data from Twelve Data: {e}")
        
        return None
    
    def _check_rate_limit(self, provider_name: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Initialize tracking for new provider
        if provider_name not in self.request_counts:
            self.request_counts[provider_name] = []
            self.last_request_time[provider_name] = 0
        
        # Remove old requests (older than 1 minute)
        minute_ago = current_time - 60
        self.request_counts[provider_name] = [
            req_time for req_time in self.request_counts[provider_name] 
            if req_time > minute_ago
        ]
        
        # Check rate limit
        provider_config = self.providers[provider_name]
        if len(self.request_counts[provider_name]) >= provider_config.rate_limit:
            return False
        
        # Check minimum time between requests
        min_interval = 60 / provider_config.rate_limit
        if current_time - self.last_request_time[provider_name] < min_interval:
            return False
        
        return True
    
    def _update_request_count(self, provider_name: str):
        """Update request count for rate limiting"""
        current_time = time.time()
        
        if provider_name not in self.request_counts:
            self.request_counts[provider_name] = []
        
        self.request_counts[provider_name].append(current_time)
        self.last_request_time[provider_name] = current_time
    
    def _cache_data(self, symbol: str, data: MarketData):
        """Cache market data"""
        self.data_cache[symbol] = data
        self.cache_expiry[symbol] = datetime.now() + timedelta(minutes=5)  # 5-minute cache
    
    def _get_cached_data(self, symbol: str) -> Optional[MarketData]:
        """Get cached market data if not expired"""
        if symbol in self.data_cache and symbol in self.cache_expiry:
            if datetime.now() < self.cache_expiry[symbol]:
                return self.data_cache[symbol]
            else:
                # Remove expired cache
                del self.data_cache[symbol]
                del self.cache_expiry[symbol]
        
        return None
    
    def get_provider_status(self) -> Dict:
        """Get status of all providers"""
        status = {}
        
        for provider_name, config in self.providers.items():
            request_count = len(self.request_counts.get(provider_name, []))
            
            status[provider_name] = {
                'name': config.name,
                'active': provider_name == (self.active_provider.value if self.active_provider else None),
                'requests_last_minute': request_count,
                'rate_limit': config.rate_limit,
                'supports_realtime': config.supports_realtime,
                'supports_historical': config.supports_historical,
                'has_api_key': config.api_key is not None
            }
        
        return status
    
    def generate_synthetic_data(self, symbol: str, periods: int = 100) -> pd.DataFrame:
        """Generate synthetic market data as fallback"""
        self.logger.warning(f"Generating synthetic data for {symbol}")
        
        # Generate realistic forex price movements
        np.random.seed(hash(symbol) % 2**32)
        
        # Starting price based on symbol
        base_prices = {
            'EURUSD': 1.1000, 'GBPUSD': 1.3000, 'USDJPY': 110.0,
            'AUDUSD': 0.7500, 'USDCHF': 0.9200, 'NZDUSD': 0.7000,
            'USDCAD': 1.2500
        }
        
        base_price = base_prices.get(symbol, 1.0000)
        
        # Generate price series
        returns = np.random.normal(0, 0.001, periods)  # 0.1% volatility
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Create OHLC data
        timestamps = pd.date_range(end=datetime.now(), periods=periods, freq='H')
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices + np.random.normal(0, 0.0001, periods),
            'high': prices + np.abs(np.random.normal(0, 0.0002, periods)),
            'low': prices - np.abs(np.random.normal(0, 0.0002, periods)),
            'close': prices,
            'volume': np.random.randint(1000, 10000, periods)
        })
        
        # Ensure OHLC consistency
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        df = df.set_index('timestamp')
        
        return df

# Example usage and testing
async def test_data_providers():
    """Test data provider functionality"""
    # Initialize manager
    manager = DataProviderManager()
    
    # Set up providers (in order of preference)
    manager.set_primary_provider(DataProvider.FREE_FOREX_API)
    manager.add_fallback_provider(DataProvider.TWELVE_DATA)
    
    try:
        # Test real-time data
        print("Testing real-time data...")
        real_time_data = await manager.get_real_time_data('EURUSD')
        
        if real_time_data:
            print(f"Real-time data for EURUSD:")
            print(f"  Price: {real_time_data.close}")
            print(f"  Timestamp: {real_time_data.timestamp}")
            print(f"  Spread: {real_time_data.spread}")
        else:
            print("Failed to get real-time data")
        
        # Test historical data
        print("\nTesting historical data...")
        historical_data = await manager.get_historical_data('EURUSD', '1H', 50)
        
        if historical_data is not None and not historical_data.empty:
            print(f"Historical data shape: {historical_data.shape}")
            print(f"Latest price: {historical_data['close'].iloc[-1]}")
        else:
            print("Failed to get historical data")
        
        # Test synthetic data fallback
        print("\nTesting synthetic data...")
        synthetic_data = manager.generate_synthetic_data('EURUSD', 100)
        print(f"Synthetic data shape: {synthetic_data.shape}")
        print(f"Latest synthetic price: {synthetic_data['close'].iloc[-1]}")
        
        # Get provider status
        print("\nProvider status:")
        status = manager.get_provider_status()
        for provider, info in status.items():
            print(f"  {info['name']}: Active={info['active']}, Requests={info['requests_last_minute']}")
        
    finally:
        await manager.close_session()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_data_providers())

