import ccxt
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta
import requests

class DataIngestion:
    def __init__(self, config=None, demo_mode=True):
        self.config = config or {}
        self.demo_mode = demo_mode
        self.exchange = None
        
        # Initialize exchange if not in demo mode
        if not demo_mode and config:
            exchange_name = config.get('EXCHANGE', 'binance').lower()
            if exchange_name == 'binance':
                self.exchange = getattr(ccxt, exchange_name)()
                if config.get('BINANCE_API_KEY'):
                    self.exchange.apiKey = config['BINANCE_API_KEY']
                    self.exchange.secret = config['BINANCE_API_SECRET']
            elif exchange_name == 'oanda':
                self.exchange = getattr(ccxt, exchange_name)()
                if config.get('OANDA_API_KEY'):
                    self.exchange.apiKey = config['OANDA_API_KEY']
                    self.exchange.headers = {'OANDA-Account-ID': config.get('OANDA_ACCOUNT_ID', '')}

    def get_historical_data(self, symbol, timeframe='1h', limit=100):
        """Get historical OHLCV data for a symbol"""
        try:
            if self.demo_mode:
                return self._get_demo_data(symbol, timeframe, limit)
            else:
                return self._get_live_data(symbol, timeframe, limit)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def _get_demo_data(self, symbol, timeframe, limit):
        """Generate demo data for testing"""
        # Create realistic demo data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=limit * self._timeframe_to_hours(timeframe))
        
        # Generate timestamps
        timestamps = pd.date_range(start=start_time, end=end_time, periods=limit)
        
        # Base prices for different asset types
        base_prices = self._get_base_price(symbol)
        
        # Generate OHLCV data
        data = []
        current_price = base_prices
        
        for i, timestamp in enumerate(timestamps):
            # Add some randomness to price movement
            change = (hash(f"{symbol}{i}") % 100 - 50) / 10000  # Small random change
            current_price += change
            
            # Generate OHLC from current price
            high = current_price * (1 + abs(hash(f"{symbol}{i}high") % 50) / 10000)
            low = current_price * (1 - abs(hash(f"{symbol}{i}low") % 50) / 10000)
            open_price = current_price * (1 + (hash(f"{symbol}{i}open") % 20 - 10) / 10000)
            close_price = current_price
            
            volume = 1000 + (hash(f"{symbol}{i}vol") % 5000)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(close_price, 5),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    def _get_live_data(self, symbol, timeframe, limit):
        """Get live data from exchange"""
        try:
            if self.exchange:
                # Use CCXT for crypto exchanges
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                return df
            else:
                # Fallback to yfinance for forex
                return self._get_yfinance_data(symbol, timeframe, limit)
        except Exception as e:
            print(f"Error fetching live data: {e}")
            return self._get_demo_data(symbol, timeframe, limit)

    def _get_yfinance_data(self, symbol, timeframe, limit):
        """Get data using yfinance (fallback for forex)"""
        try:
            # Convert timeframe to yfinance format
            tf_map = {
                '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
                '1h': '1h', '4h': '4h', '1d': '1d'
            }
            yf_tf = tf_map.get(timeframe, '1h')
            
            # For forex, we need to add currency suffix
            if not symbol.endswith('=X'):
                symbol = f"{symbol}=X"
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{limit * self._timeframe_to_hours(timeframe)}h", interval=yf_tf)
            
            if df.empty:
                return self._get_demo_data(symbol, timeframe, limit)
            
            return df
        except Exception as e:
            print(f"Error fetching yfinance data: {e}")
            return self._get_demo_data(symbol, timeframe, limit)

    def _get_base_price(self, symbol):
        """Get base price for demo data generation"""
        # Forex base prices
        forex_prices = {
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 148.50,
            'USDCHF': 0.8650, 'AUDUSD': 0.6650, 'USDCAD': 1.3550,
            'NZDUSD': 0.6150, 'EURGBP': 0.8580, 'EURJPY': 161.20,
            'GBPJPY': 187.80, 'EURCHF': 0.9380, 'AUDCAD': 0.9010
        }
        
        # Crypto base prices
        crypto_prices = {
            'BTC/USDT': 45000, 'ETH/USDT': 3000, 'XRP/USDT': 0.5,
            'LTC/USDT': 150, 'BCH/USDT': 250, 'ADA/USDT': 0.4,
            'DOT/USDT': 7, 'LINK/USDT': 15, 'SOL/USDT': 100, 'BNB/USDT': 300
        }
        
        # Check forex first
        if symbol in forex_prices:
            return forex_prices[symbol]
        elif symbol in crypto_prices:
            return crypto_prices[symbol]
        else:
            # Try to extract base currency for forex
            if len(symbol) == 6 and symbol.isalpha():
                return 1.0000  # Default forex price
            else:
                return 100.0  # Default crypto price

    def _timeframe_to_hours(self, timeframe):
        """Convert timeframe string to hours"""
        tf_map = {
            '1m': 1/60, '5m': 5/60, '15m': 15/60, '30m': 30/60,
            '1h': 1, '4h': 4, '1d': 24
        }
        return tf_map.get(timeframe, 1)

    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            if self.demo_mode:
                return self._get_base_price(symbol)
            else:
                if self.exchange:
                    ticker = self.exchange.fetch_ticker(symbol)
                    return ticker['last']
                else:
                    # Fallback to yfinance
                    if not symbol.endswith('=X'):
                        symbol = f"{symbol}=X"
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    return info.get('regularMarketPrice', self._get_base_price(symbol))
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return self._get_base_price(symbol)

    def get_market_data(self, symbols, timeframes):
        """Get market data for multiple symbols and timeframes"""
        market_data = {}
        
        for symbol in symbols:
            market_data[symbol] = {}
            for timeframe in timeframes:
                data = self.get_historical_data(symbol, timeframe)
                if data is not None and not data.empty:
                    market_data[symbol][timeframe] = data
        
        return market_data

    def get_forex_data(self, symbol, timeframe='1h', limit=100):
        """Get forex-specific data"""
        # For forex, we might need special handling
        return self.get_historical_data(symbol, timeframe, limit)

    def get_crypto_data(self, symbol, timeframe='1h', limit=100):
        """Get crypto-specific data"""
        # For crypto, we might need special handling
        return self.get_historical_data(symbol, timeframe, limit)

    def validate_symbol(self, symbol):
        """Validate if a symbol is supported"""
        # Forex symbols (6 characters, all letters)
        if len(symbol) == 6 and symbol.isalpha():
            return True
        
        # Crypto symbols (contain /)
        if '/' in symbol:
            return True
        
        return False

    def get_supported_symbols(self):
        """Get list of supported symbols based on exchange"""
        exchange = self.config.get('EXCHANGE', 'binance').lower()
        
        if exchange == 'exness':
            return [
                'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD',
                'NZDUSD', 'EURGBP', 'EURJPY', 'GBPJPY', 'EURCHF', 'AUDCAD',
                'GBPCHF', 'AUDJPY', 'CADJPY', 'NZDJPY', 'CHFJPY'
            ]
        elif exchange == 'binance':
            return [
                'BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT', 'BCH/USDT',
                'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'SOL/USDT', 'BNB/USDT'
            ]
        elif exchange == 'oanda':
            return [
                'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD',
                'USD_CAD', 'NZD_USD', 'EUR_GBP', 'EUR_JPY', 'GBP_JPY'
            ]
        else:
            return ['EURUSD', 'GBPUSD', 'BTC/USDT', 'ETH/USDT']


