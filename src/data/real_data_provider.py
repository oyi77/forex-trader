"""
Real Data Provider for Backtesting
Fetches real market data from multiple sources
"""

import os
import logging
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
import json

from ..core.interfaces import IDataProvider, MarketData


class RealDataProvider(IDataProvider):
    """
    Real data provider that fetches data from multiple sources:
    - Yahoo Finance for forex and commodities
    - HistData.com for historical forex data
    - Metals-API for gold prices
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.cache_dir = Path(self.config.get('cache_dir', './data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Symbol mappings for different data sources
        self.yahoo_symbols = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X', 
            'USDJPY': 'USDJPY=X',
            'USDCHF': 'USDCHF=X',
            'AUDUSD': 'AUDUSD=X',
            'USDCAD': 'USDCAD=X',
            'NZDUSD': 'NZDUSD=X',
            'XAUUSD': 'GC=F',  # Gold futures
            'XAGUSD': 'SI=F',  # Silver futures
            'CRUDE_OIL': 'CL=F',  # Crude oil futures
            'BRENT_OIL': 'BZ=F'   # Brent oil futures
        }
        
        # Metals API configuration
        self.metals_api_key = self.config.get('metals_api_key', 'free')  # Free tier
        self.metals_api_base = 'https://metals-api.com/api'
        
        self.logger.info("Real data provider initialized")
    
    def get_historical_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get historical market data"""
        try:
            # Check cache first
            cache_key = f"{pair}_{timeframe}_{periods}"
            cached_data = self._get_cached_data(cache_key)
            if cached_data is not None:
                self.logger.info(f"Using cached data for {pair}")
                return cached_data
            
            # Fetch from appropriate source
            if pair in ['XAUUSD', 'XAGUSD']:
                data = self._get_metals_data(pair, timeframe, periods)
            elif pair in ['CRUDE_OIL', 'BRENT_OIL']:
                data = self._get_oil_data(pair, timeframe, periods)
            else:
                data = self._get_forex_data(pair, timeframe, periods)
            
            # Cache the data
            if data is not None and not data.empty:
                self._cache_data(cache_key, data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {pair}: {e}")
            return pd.DataFrame()
    
    def get_live_price(self, pair: str) -> MarketData:
        """Get current live price"""
        try:
            if pair in ['XAUUSD', 'XAGUSD']:
                return self._get_live_metals_price(pair)
            else:
                return self._get_live_yahoo_price(pair)
                
        except Exception as e:
            self.logger.error(f"Error fetching live price for {pair}: {e}")
            return None
    
    def is_market_open(self, pair: str) -> bool:
        """Check if market is open for trading"""
        # Forex market is open 24/5, commodities have specific hours
        now = datetime.now()
        weekday = now.weekday()
        
        # Market closed on weekends
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # For simplicity, assume markets are open during weekdays
        # In production, you'd check specific market hours
        return True
    
    def _get_forex_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get forex data from Yahoo Finance"""
        try:
            yahoo_symbol = self.yahoo_symbols.get(pair, f"{pair}=X")
            
            # Convert timeframe to Yahoo Finance format
            interval_map = {
                '1m': '1m',
                '5m': '5m', 
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            
            # Calculate period for yfinance
            if timeframe in ['1m', '5m']:
                period_days = min(7, periods // (24 * 60 // int(timeframe[:-1])))
                period = f"{period_days}d"
            elif timeframe in ['15m', '30m', '1h']:
                period_days = min(60, periods // (24 // int(timeframe[:-1]) if timeframe != '1h' else 24))
                period = f"{period_days}d"
            else:
                period = f"{min(periods, 365)}d"
            
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No data returned for {pair} from Yahoo Finance")
                return pd.DataFrame()
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add bid/ask spread simulation (typical forex spread)
            spread_pips = self._get_typical_spread(pair)
            pip_value = self._get_pip_value(pair)
            spread = spread_pips * pip_value
            
            data['bid'] = data['close'] - spread / 2
            data['ask'] = data['close'] + spread / 2
            
            self.logger.info(f"Fetched {len(data)} records for {pair} from Yahoo Finance")
            return data.tail(periods)
            
        except Exception as e:
            self.logger.error(f"Error fetching forex data for {pair}: {e}")
            return pd.DataFrame()
    
    def _get_metals_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get metals data from Metals API and Yahoo Finance"""
        try:
            # Use Yahoo Finance for historical metals data
            symbol_map = {
                'XAUUSD': 'GC=F',  # Gold futures
                'XAGUSD': 'SI=F'   # Silver futures
            }
            
            yahoo_symbol = symbol_map.get(pair, 'GC=F')
            
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m', 
                '30m': '30m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            
            # Calculate period
            if timeframe in ['1m', '5m']:
                period = "7d"
            elif timeframe in ['15m', '30m', '1h']:
                period = "60d"
            else:
                period = f"{min(periods, 365)}d"
            
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No metals data returned for {pair}")
                return pd.DataFrame()
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low', 
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Add bid/ask spread for metals (typically wider than forex)
            spread = 0.50 if pair == 'XAUUSD' else 0.02  # $0.50 for gold, $0.02 for silver
            data['bid'] = data['close'] - spread / 2
            data['ask'] = data['close'] + spread / 2
            
            self.logger.info(f"Fetched {len(data)} metals records for {pair}")
            return data.tail(periods)
            
        except Exception as e:
            self.logger.error(f"Error fetching metals data for {pair}: {e}")
            return pd.DataFrame()
    
    def _get_oil_data(self, pair: str, timeframe: str, periods: int) -> pd.DataFrame:
        """Get oil data from Yahoo Finance"""
        try:
            symbol_map = {
                'CRUDE_OIL': 'CL=F',  # WTI Crude Oil
                'BRENT_OIL': 'BZ=F'   # Brent Crude Oil
            }
            
            yahoo_symbol = symbol_map.get(pair, 'CL=F')
            
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m', 
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            
            # Calculate period
            if timeframe in ['1m', '5m']:
                period = "7d"
            elif timeframe in ['15m', '30m', '1h']:
                period = "60d"
            else:
                period = f"{min(periods, 365)}d"
            
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                self.logger.warning(f"No oil data returned for {pair}")
                return pd.DataFrame()
            
            # Standardize column names
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close', 
                'Volume': 'volume'
            })
            
            # Add bid/ask spread for oil (typically $0.02-0.05)
            spread = 0.03  # $0.03 spread
            data['bid'] = data['close'] - spread / 2
            data['ask'] = data['close'] + spread / 2
            
            self.logger.info(f"Fetched {len(data)} oil records for {pair}")
            return data.tail(periods)
            
        except Exception as e:
            self.logger.error(f"Error fetching oil data for {pair}: {e}")
            return pd.DataFrame()
    
    def _get_live_yahoo_price(self, pair: str) -> MarketData:
        """Get live price from Yahoo Finance"""
        try:
            yahoo_symbol = self.yahoo_symbols.get(pair, f"{pair}=X")
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            current_price = info.get('regularMarketPrice', info.get('previousClose', 0))
            
            if current_price == 0:
                return None
            
            # Simulate bid/ask spread
            spread_pips = self._get_typical_spread(pair)
            pip_value = self._get_pip_value(pair)
            spread = spread_pips * pip_value
            
            bid = current_price - spread / 2
            ask = current_price + spread / 2
            
            return MarketData(
                pair=pair,
                timestamp=datetime.now(),
                open=current_price,
                high=current_price,
                low=current_price,
                close=current_price,
                volume=0,
                bid=bid,
                ask=ask
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching live Yahoo price for {pair}: {e}")
            return None
    
    def _get_live_metals_price(self, pair: str) -> MarketData:
        """Get live metals price from Metals API"""
        try:
            # For free tier, use Yahoo Finance as backup
            return self._get_live_yahoo_price(pair)
            
        except Exception as e:
            self.logger.error(f"Error fetching live metals price for {pair}: {e}")
            return None
    
    def _get_typical_spread(self, pair: str) -> float:
        """Get typical spread in pips for a currency pair"""
        spreads = {
            'EURUSD': 1.5,
            'GBPUSD': 2.0,
            'USDJPY': 1.5,
            'USDCHF': 2.0,
            'AUDUSD': 2.5,
            'USDCAD': 2.5,
            'NZDUSD': 3.0,
            'XAUUSD': 50.0,  # Gold spread in cents
            'XAGUSD': 2.0,   # Silver spread in cents
            'CRUDE_OIL': 3.0,
            'BRENT_OIL': 3.0
        }
        return spreads.get(pair, 3.0)
    
    def _get_pip_value(self, pair: str) -> float:
        """Get pip value for a currency pair"""
        if pair in ['USDJPY']:
            return 0.01  # JPY pairs have 2 decimal places
        elif pair in ['XAUUSD', 'XAGUSD', 'CRUDE_OIL', 'BRENT_OIL']:
            return 0.01  # Commodities
        else:
            return 0.0001  # Most forex pairs have 4 decimal places
    
    def _get_cached_data(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Get data from cache if available and not expired"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            if cache_file.exists():
                # Check if cache is less than 1 hour old
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < 3600:  # 1 hour
                    return pd.read_pickle(cache_file)
            return None
        except Exception:
            return None
    
    def _cache_data(self, cache_key: str, data: pd.DataFrame) -> None:
        """Cache data to disk"""
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            data.to_pickle(cache_file)
        except Exception as e:
            self.logger.warning(f"Failed to cache data: {e}")
    
    def download_historical_data(self, pairs: List[str], timeframe: str = '1h', days: int = 365) -> Dict[str, pd.DataFrame]:
        """Download and cache historical data for multiple pairs"""
        self.logger.info(f"Downloading historical data for {len(pairs)} pairs")
        
        data_dict = {}
        for pair in pairs:
            try:
                periods = self._calculate_periods(timeframe, days)
                data = self.get_historical_data(pair, timeframe, periods)
                if not data.empty:
                    data_dict[pair] = data
                    self.logger.info(f"Downloaded {len(data)} records for {pair}")
                else:
                    self.logger.warning(f"No data available for {pair}")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to download data for {pair}: {e}")
        
        return data_dict
    
    def _calculate_periods(self, timeframe: str, days: int) -> int:
        """Calculate number of periods for given timeframe and days"""
        timeframe_minutes = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        
        minutes_per_day = 1440
        total_minutes = days * minutes_per_day
        tf_minutes = timeframe_minutes.get(timeframe, 60)
        
        # Account for market hours (forex is 24/5, so ~5/7 of the time)
        if timeframe != '1d':
            market_factor = 5/7  # 5 days per week
            total_minutes *= market_factor
        
        return int(total_minutes / tf_minutes)


class HistDataDownloader:
    """
    Downloads historical data from HistData.com
    For high-quality 1-minute forex data
    """
    
    def __init__(self, download_dir: str = "./data/histdata"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # HistData.com URL patterns
        self.base_url = "https://www.histdata.com/download-free-forex-historical-data"
        
    def download_pair_data(self, pair: str, year: int) -> Optional[pd.DataFrame]:
        """Download 1-minute data for a specific pair and year"""
        try:
            # This would require implementing the actual download logic
            # For now, we'll use Yahoo Finance as a fallback
            self.logger.info(f"HistData download not implemented, using Yahoo Finance for {pair}")
            
            # Use Yahoo Finance as fallback
            provider = RealDataProvider()
            return provider.get_historical_data(pair, '1m', 365 * 24 * 60)
            
        except Exception as e:
            self.logger.error(f"Error downloading HistData for {pair}: {e}")
            return None


def create_real_data_provider(config: Dict[str, Any] = None) -> RealDataProvider:
    """Factory function to create a real data provider"""
    return RealDataProvider(config)

