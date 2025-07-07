import ccxt
import pandas as pd
import time
import numpy as np

class DataIngestion:
    def __init__(self, exchange_id="binance", config=None, demo_mode=True):
        self.exchange_id = exchange_id
        self.demo_mode = demo_mode
        if not self.demo_mode:
            self.exchange = getattr(ccxt, exchange_id)()
            if config:
                self.exchange.apiKey = config.get(f"{exchange_id.upper()}_API_KEY")
                self.exchange.secret = config.get(f"{exchange_id.upper()}_API_SECRET")

    def _fetch_mock_ohlcv(self, symbol, timeframe, limit=100):
        # Generate dummy OHLCV data for testing
        freq_map = {
            "1h": "H",
            "30m": "30min",
            "1d": "D",
            "1w": "W",
            "1M": "MS",
            "H1": "H", # Adding H1 mapping
            "M30": "30min" # Adding M30 mapping
        }
        freq = freq_map.get(timeframe, None) # Use mapped frequency or None if not found

        if freq is None:
            # If timeframe is not in map, try to convert it or raise an error.
            # For simplicity, let\'s assume if it\'s not in map, it\'s an invalid timeframe for mock data.
            raise ValueError(f"Unsupported timeframe for mock data: {timeframe}")

        timestamps = pd.date_range(end=pd.Timestamp.now(), periods=limit, freq=freq)
        open_prices = np.random.uniform(100, 200, limit)
        close_prices = open_prices + np.random.uniform(-5, 5, limit)
        high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(0, 2, limit)
        low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(0, 2, limit)
        volumes = np.random.uniform(1000, 10000, limit)

        data = {
            "timestamp": timestamps,
            "open": open_prices,
            "high": high_prices,
            "low": low_prices,
            "close": close_prices,
            "volume": volumes
        }
        df = pd.DataFrame(data)
        return df

    def fetch_ohlcv(self, symbol, timeframe, limit=100):
        if self.demo_mode:
            return self._fetch_mock_ohlcv(symbol, timeframe, limit)
        else:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
            except Exception as e:
                print(f"Error fetching OHLCV for {symbol} on {self.exchange_id} ({timeframe}): {e}")
                return pd.DataFrame()

    def scan_market_data(self, symbols, timeframes, limit=100):
        all_data = {}
        for symbol in symbols:
            all_data[symbol] = {}
            for tf in timeframes:
                print(f"Fetching {symbol} {tf} data...")
                data = self.fetch_ohlcv(symbol, tf, limit)
                all_data[symbol][tf] = data
                if not self.demo_mode:
                    time.sleep(self.exchange.rateLimit / 1000) # Respect rate limits
        return all_data

# Example Usage (will be integrated into main.py later)
# if __name__ == "__main__":
#     # This would typically come from config.yaml
#     mock_config = {
#         "BINANCE_API_KEY": "YOUR_BINANCE_API_KEY",
#         "BINANCE_API_SECRET": "YOUR_BINANCE_API_SECRET",
#     }
#     data_ingestor = DataIngestion(exchange_id="binance", config=mock_config, demo_mode=True)
#     symbols = ["BTC/USDT", "ETH/USDT"]
#     timeframes = ["1h", "30m"]
#     market_data = data_ingestor.scan_market_data(symbols, timeframes)
#     for symbol, tfs_data in market_data.items():
#         for tf, df in tfs_data.items():
#             print(f"\n{symbol} {tf} Data Head:")
#             print(df.head())


