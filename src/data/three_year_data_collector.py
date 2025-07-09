"""
3-Year Historical Data Collector
Downloads and manages 3 years of forex historical data for comprehensive backtesting
"""

import os
import sys
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import zipfile
import io
import time
import logging
from typing import Dict, List, Optional, Tuple
import yfinance as yf
from pathlib import Path

class ThreeYearDataCollector:
    """
    Collects 3 years of historical forex data from multiple sources
    """
    
    def __init__(self, data_dir: str = "data/3year_historical"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Currency pairs to collect
        self.forex_pairs = [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'USDCAD',
            'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'EURGBP'
        ]
        
        # Yahoo Finance symbols (add =X for forex)
        self.yf_symbols = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X', 
            'USDJPY': 'USDJPY=X',
            'USDCHF': 'USDCHF=X',
            'USDCAD': 'USDCAD=X',
            'AUDUSD': 'AUDUSD=X',
            'NZDUSD': 'NZDUSD=X',
            'EURJPY': 'EURJPY=X',
            'GBPJPY': 'GBPJPY=X',
            'EURGBP': 'EURGBP=X',
            'XAUUSD': 'GC=F',  # Gold futures
            'XAGUSD': 'SI=F',  # Silver futures
            'WTIUSD': 'CL=F'   # Oil futures
        }
        
        # Date range for 3 years
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=3*365 + 30)  # 3 years + buffer
        
        self.logger.info(f"Data collection period: {self.start_date.date()} to {self.end_date.date()}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for data collection"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def download_yahoo_finance_data(self, symbol: str, yf_symbol: str) -> Optional[pd.DataFrame]:
        """Download data from Yahoo Finance"""
        try:
            self.logger.info(f"Downloading {symbol} from Yahoo Finance...")
            
            # Download data with 1-minute intervals (max 7 days for 1m)
            # So we'll use 1-hour intervals for 3 years
            ticker = yf.Ticker(yf_symbol)
            
            # Try different intervals based on data availability
            intervals = ['1h', '1d']
            
            for interval in intervals:
                try:
                    data = ticker.history(
                        start=self.start_date,
                        end=self.end_date,
                        interval=interval,
                        auto_adjust=True,
                        prepost=True
                    )
                    
                    if not data.empty:
                        # Standardize column names
                        data.columns = [col.lower() for col in data.columns]
                        data = data.rename(columns={
                            'adj close': 'close'
                        })
                        
                        # Ensure we have required columns
                        required_cols = ['open', 'high', 'low', 'close', 'volume']
                        if all(col in data.columns for col in required_cols):
                            data['symbol'] = symbol
                            data['timeframe'] = interval
                            
                            self.logger.info(f"Downloaded {len(data)} {interval} bars for {symbol}")
                            return data
                        
                except Exception as e:
                    self.logger.warning(f"Failed to download {symbol} with {interval} interval: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading {symbol}: {e}")
            return None
    
    def download_alpha_vantage_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Download data from Alpha Vantage (free tier)"""
        try:
            # Alpha Vantage free API (no key needed for some endpoints)
            base_url = "https://www.alphavantage.co/query"
            
            # Try to get daily data
            params = {
                'function': 'FX_DAILY',
                'from_symbol': symbol[:3],
                'to_symbol': symbol[3:],
                'outputsize': 'full',
                'datatype': 'csv'
            }
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200 and 'timestamp' in response.text.lower():
                data = pd.read_csv(io.StringIO(response.text))
                
                # Standardize column names
                data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                data = data.rename(columns={
                    'timestamp': 'datetime',
                    'open': 'open',
                    'high': 'high', 
                    'low': 'low',
                    'close': 'close'
                })
                
                data['datetime'] = pd.to_datetime(data['datetime'])
                data = data.set_index('datetime')
                data['volume'] = 1000  # Dummy volume for forex
                data['symbol'] = symbol
                
                # Filter to our date range
                data = data[(data.index >= self.start_date) & (data.index <= self.end_date)]
                
                if not data.empty:
                    self.logger.info(f"Downloaded {len(data)} daily bars for {symbol} from Alpha Vantage")
                    return data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading {symbol} from Alpha Vantage: {e}")
            return None
    
    def generate_synthetic_minute_data(self, daily_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Generate synthetic minute data from daily data using realistic price movements"""
        try:
            self.logger.info(f"Generating synthetic minute data for {symbol}...")
            
            minute_data = []
            
            for date, row in daily_data.iterrows():
                # Generate 1440 minutes (24 hours) of data for each day
                daily_open = row['open']
                daily_high = row['high']
                daily_low = row['low']
                daily_close = row['close']
                daily_volume = row.get('volume', 1000)
                
                # Calculate daily range and volatility
                daily_range = daily_high - daily_low
                daily_return = (daily_close - daily_open) / daily_open
                
                # Generate minute-by-minute price path
                minutes_in_day = 1440
                minute_returns = np.random.normal(
                    daily_return / minutes_in_day,  # Mean return per minute
                    daily_range / daily_open / np.sqrt(minutes_in_day),  # Volatility per minute
                    minutes_in_day
                )
                
                # Create price path
                prices = [daily_open]
                for i in range(minutes_in_day - 1):
                    next_price = prices[-1] * (1 + minute_returns[i])
                    prices.append(next_price)
                
                # Adjust to match daily OHLC
                prices = np.array(prices)
                
                # Scale to match daily high/low
                price_min = np.min(prices)
                price_max = np.max(prices)
                
                if price_max > price_min:
                    # Scale to daily range
                    scaled_prices = daily_low + (prices - price_min) / (price_max - price_min) * daily_range
                    
                    # Adjust final price to match daily close
                    adjustment = daily_close - scaled_prices[-1]
                    scaled_prices += adjustment
                else:
                    scaled_prices = np.full(len(prices), daily_open)
                
                # Create minute bars
                for i in range(0, len(scaled_prices), 60):  # 1-hour bars from minute data
                    hour_prices = scaled_prices[i:i+60]
                    
                    if len(hour_prices) > 0:
                        minute_data.append({
                            'datetime': date + timedelta(hours=i//60),
                            'open': hour_prices[0],
                            'high': np.max(hour_prices),
                            'low': np.min(hour_prices),
                            'close': hour_prices[-1],
                            'volume': daily_volume / 24,  # Distribute volume across hours
                            'symbol': symbol
                        })
            
            df = pd.DataFrame(minute_data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            
            self.logger.info(f"Generated {len(df)} hourly bars for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generating synthetic data for {symbol}: {e}")
            return pd.DataFrame()
    
    def collect_all_data(self) -> Dict[str, pd.DataFrame]:
        """Collect 3 years of data for all currency pairs"""
        self.logger.info("Starting 3-year data collection...")
        
        all_data = {}
        
        for symbol in self.forex_pairs + ['XAUUSD', 'XAGUSD', 'WTIUSD']:
            self.logger.info(f"Collecting data for {symbol}...")
            
            # Try Yahoo Finance first
            yf_symbol = self.yf_symbols.get(symbol)
            if yf_symbol:
                data = self.download_yahoo_finance_data(symbol, yf_symbol)
                
                if data is not None and not data.empty:
                    # If we got daily data, generate synthetic minute data
                    if 'timeframe' in data.columns and data['timeframe'].iloc[0] == '1d':
                        hourly_data = self.generate_synthetic_minute_data(data, symbol)
                        if not hourly_data.empty:
                            all_data[symbol] = hourly_data
                        else:
                            all_data[symbol] = data
                    else:
                        all_data[symbol] = data
                    
                    # Save to file
                    filename = self.data_dir / f"{symbol}_3year.csv"
                    all_data[symbol].to_csv(filename)
                    self.logger.info(f"Saved {symbol} data to {filename}")
                    
                    continue
            
            # Try Alpha Vantage as backup
            if symbol in self.forex_pairs:
                data = self.download_alpha_vantage_data(symbol)
                
                if data is not None and not data.empty:
                    # Generate synthetic minute data from daily
                    hourly_data = self.generate_synthetic_minute_data(data, symbol)
                    if not hourly_data.empty:
                        all_data[symbol] = hourly_data
                    else:
                        all_data[symbol] = data
                    
                    # Save to file
                    filename = self.data_dir / f"{symbol}_3year.csv"
                    all_data[symbol].to_csv(filename)
                    self.logger.info(f"Saved {symbol} data to {filename}")
                    
                    continue
            
            self.logger.warning(f"Could not collect data for {symbol}")
            
            # Add small delay to avoid rate limiting
            time.sleep(1)
        
        self.logger.info(f"Data collection complete. Collected data for {len(all_data)} symbols")
        return all_data
    
    def load_existing_data(self) -> Dict[str, pd.DataFrame]:
        """Load existing 3-year data from files"""
        all_data = {}
        
        for symbol in self.forex_pairs + ['XAUUSD', 'XAGUSD', 'WTIUSD']:
            filename = self.data_dir / f"{symbol}_3year.csv"
            
            if filename.exists():
                try:
                    data = pd.read_csv(filename, index_col=0, parse_dates=True)
                    all_data[symbol] = data
                    self.logger.info(f"Loaded {len(data)} records for {symbol}")
                except Exception as e:
                    self.logger.error(f"Error loading {symbol}: {e}")
        
        return all_data
    
    def get_data_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Get summary statistics for collected data"""
        summary = {}
        
        for symbol, df in data.items():
            if not df.empty:
                summary[symbol] = {
                    'records': len(df),
                    'start_date': df.index.min(),
                    'end_date': df.index.max(),
                    'days': (df.index.max() - df.index.min()).days,
                    'avg_daily_volume': df['volume'].mean() if 'volume' in df.columns else 0,
                    'price_range': {
                        'min': df['low'].min(),
                        'max': df['high'].max(),
                        'avg': df['close'].mean()
                    }
                }
        
        return summary


def main():
    """Main function to collect 3-year data"""
    print("🚀 3-YEAR HISTORICAL DATA COLLECTION")
    print("=" * 50)
    
    collector = ThreeYearDataCollector()
    
    # Check if data already exists
    existing_data = collector.load_existing_data()
    
    if existing_data:
        print(f"Found existing data for {len(existing_data)} symbols")
        
        # Check data quality
        summary = collector.get_data_summary(existing_data)
        
        for symbol, stats in summary.items():
            print(f"{symbol}: {stats['records']} records, {stats['days']} days")
        
        use_existing = input("Use existing data? (y/n): ").lower().strip()
        
        if use_existing == 'y':
            print("Using existing data...")
            return existing_data
    
    # Collect new data
    print("Collecting new 3-year data...")
    all_data = collector.collect_all_data()
    
    # Display summary
    summary = collector.get_data_summary(all_data)
    
    print("\n" + "=" * 50)
    print("DATA COLLECTION SUMMARY")
    print("=" * 50)
    
    for symbol, stats in summary.items():
        print(f"{symbol}:")
        print(f"  Records: {stats['records']:,}")
        print(f"  Period: {stats['start_date'].date()} to {stats['end_date'].date()}")
        print(f"  Days: {stats['days']}")
        print(f"  Price range: {stats['price_range']['min']:.5f} - {stats['price_range']['max']:.5f}")
        print()
    
    return all_data


if __name__ == "__main__":
    main()

