import pandas as pd
import ta
import numpy as np

class StrategyCore:
    def __init__(self, config=None):
        self.config = config or {}

    def detect_ema_cross(self, df, short_period=20, long_period=50):
        """Detect EMA crossovers for trend identification"""
        df["EMA_Short"] = ta.trend.ema_indicator(df["close"], window=short_period)
        df["EMA_Long"] = ta.trend.ema_indicator(df["close"], window=long_period)
        # Golden cross: short EMA crosses above long EMA
        df["Golden_Cross"] = (df["EMA_Short"].shift(1) < df["EMA_Long"].shift(1)) & (df["EMA_Short"] > df["EMA_Long"])
        # Death cross: short EMA crosses below long EMA
        df["Death_Cross"] = (df["EMA_Short"].shift(1) > df["EMA_Long"].shift(1)) & (df["EMA_Short"] < df["EMA_Long"])
        return df

    def get_rsi(self, df, window=14):
        """Calculate RSI and overbought/oversold conditions"""
        df["RSI"] = ta.momentum.rsi(df["close"], window=window)
        df["RSI_Overbought"] = df["RSI"] > 70
        df["RSI_Oversold"] = df["RSI"] < 30
        return df

    def get_atr(self, df, window=14):
        """Calculate Average True Range for volatility measurement"""
        df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=window)
        return df

    def detect_choch_bos(self, df, window=5):
        """Detect Change of Character (CHoCH) and Break of Structure (BOS)"""
        df["High_Swing"] = df["high"].rolling(window=window).max()
        df["Low_Swing"] = df["low"].rolling(window=window).min()

        # Break of Structure (BOS) - new high after previous high
        df["BOS_Bullish"] = (df["close"] > df["High_Swing"].shift(1)) & (df["High_Swing"].shift(1) > df["High_Swing"].shift(2))
        df["BOS_Bearish"] = (df["close"] < df["Low_Swing"].shift(1)) & (df["Low_Swing"].shift(1) < df["Low_Swing"].shift(2))

        # Change of Character (CHoCH) - price breaks previous swing after trend change
        df["CHoCH_Bullish"] = (df["close"] > df["High_Swing"].shift(1)) & (df["Death_Cross"] == True).shift(1)
        df["CHoCH_Bearish"] = (df["close"] < df["Low_Swing"].shift(1)) & (df["Golden_Cross"] == True).shift(1)

        return df

    def identify_fvg(self, df):
        """Identify Fair Value Gaps (FVG)"""
        # Bullish FVG: candle 1 high < candle 3 low
        df["FVG_Bullish"] = (df["high"].shift(2) < df["low"]) & \
                            (df["close"] > df["open"]) & \
                            (df["close"].shift(1) > df["open"].shift(1)) & \
                            (df["close"].shift(2) > df["open"].shift(2))

        # Bearish FVG: candle 1 low > candle 3 high
        df["FVG_Bearish"] = (df["low"].shift(2) > df["high"]) & \
                             (df["close"] < df["open"]) & \
                             (df["close"].shift(1) < df["open"].shift(1)) & \
                             (df["close"].shift(2) < df["open"].shift(2))
        return df

    def validate_order_blocks(self, df):
        """Identify Order Blocks (OB) - institutional order zones"""
        # Bullish Order Block: last down candle before strong move up
        df["Bullish_OB"] = (df["close"] > df["open"]) & (df["close"].shift(1) < df["open"].shift(1)) & (df["close"] > df["high"].shift(1))
        
        # Bearish Order Block: last up candle before strong move down
        df["Bearish_OB"] = (df["close"] < df["open"]) & (df["close"].shift(1) > df["open"].shift(1)) & (df["close"] < df["low"].shift(1))
        return df

    def detect_liquidity_pools(self, df, window=10):
        """Detect liquidity pools above swing highs or below swing lows"""
        df["Swing_High"] = df["high"].rolling(window=window).max()
        df["Swing_Low"] = df["low"].rolling(window=window).min()
        df["Liquidity_Above_High"] = (df["high"] == df["Swing_High"]) & (df["high"] != df["high"].shift(1))
        df["Liquidity_Below_Low"] = (df["low"] == df["Swing_Low"]) & (df["low"] != df["low"].shift(1))
        return df

    def validate_fibonacci_rejection(self, df, fib_level=0.618):
        """Validate Fibonacci retracement rejections"""
        # Calculate swing high and low for Fibonacci levels
        df["Swing_High_20"] = df["high"].rolling(window=20).max()
        df["Swing_Low_20"] = df["low"].rolling(window=20).min()
        
        # Calculate Fibonacci levels
        df["Fib_618"] = df["Swing_Low_20"] + (df["Swing_High_20"] - df["Swing_Low_20"]) * fib_level
        df["Fib_382"] = df["Swing_Low_20"] + (df["Swing_High_20"] - df["Swing_Low_20"]) * 0.382
        
        # Check if price is rejecting from Fibonacci levels
        df["Fib_Rejection_Bullish"] = (df["low"] <= df["Fib_618"]) & (df["close"] > df["Fib_618"]) & (df["close"] > df["open"])
        df["Fib_Rejection_Bearish"] = (df["high"] >= df["Fib_382"]) & (df["close"] < df["Fib_382"]) & (df["close"] < df["open"])
        
        return df

    def detect_dbd_rbr(self, df):
        """Detect DBD (Drop-Base-Drop) and RBR (Rally-Base-Rally) zones"""
        # DBD: Drop-Base-Drop pattern
        df["DBD"] = (df["close"] < df["open"]) & (df["close"].shift(1) == df["open"].shift(1)) & (df["close"].shift(2) < df["open"].shift(2))
        
        # RBR: Rally-Base-Rally pattern
        df["RBR"] = (df["close"] > df["open"]) & (df["close"].shift(1) == df["open"].shift(1)) & (df["close"].shift(2) > df["open"].shift(2))
        return df

    def classify_candle_patterns(self, df):
        """Classify various candlestick patterns"""
        # Engulfing patterns
        df["Engulfing_Bullish"] = (df["close"] > df["open"]) & (df["close"] > df["open"].shift(1)) & (df["open"] < df["close"].shift(1))
        df["Engulfing_Bearish"] = (df["close"] < df["open"]) & (df["close"] < df["open"].shift(1)) & (df["open"] > df["close"].shift(1))
        
        # Pinbar patterns (hammer/shooting star)
        df["Pinbar_Bullish"] = (df["close"] > df["open"]) & (df["low"] < df["low"].shift(1)) & ((df["high"] - df["close"]) > 2 * (df["close"] - df["open"]))
        df["Pinbar_Bearish"] = (df["close"] < df["open"]) & (df["high"] > df["high"].shift(1)) & ((df["close"] - df["low"]) > 2 * (df["open"] - df["close"]))
        
        # Long wick manipulation
        df["Long_Wick_Manipulation"] = (df["high"] - df["low"]) > 3 * (df["close"] - df["open"]).abs()
        
        # Doji patterns
        df["Doji"] = abs(df["close"] - df["open"]) <= (df["high"] - df["low"]) * 0.1
        
        return df

    def detect_momentum_divergence(self, df):
        """Detect price and RSI divergence"""
        # Bullish divergence: price makes lower low, RSI makes higher low
        df["Bullish_Divergence"] = (df["close"] < df["close"].shift(1)) & (df["RSI"] > df["RSI"].shift(1))
        
        # Bearish divergence: price makes higher high, RSI makes lower high
        df["Bearish_Divergence"] = (df["close"] > df["close"].shift(1)) & (df["RSI"] < df["RSI"].shift(1))
        
        return df

    def apply_all_strategies(self, df):
        """Apply all technical analysis strategies to the dataframe"""
        df = self.detect_ema_cross(df)
        df = self.get_rsi(df)
        df = self.get_atr(df)
        df = self.detect_choch_bos(df)
        df = self.identify_fvg(df)
        df = self.validate_order_blocks(df)
        df = self.detect_liquidity_pools(df)
        df = self.validate_fibonacci_rejection(df)
        df = self.detect_dbd_rbr(df)
        df = self.classify_candle_patterns(df)
        df = self.detect_momentum_divergence(df)
        return df

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy DataFrame for testing
    data = {
        'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='H')),
        'open': [i + 100 for i in range(100)],
        'high': [i + 102 for i in range(100)],
        'low': [i + 98 for i in range(100)],
        'close': [i + 101 for i in range(100)],
        'volume': [i * 100 for i in range(100)]
    }
    dummy_df = pd.DataFrame(data)
    dummy_df["close"] = dummy_df["close"].apply(lambda x: x + (x % 10) * (-1)**(x//10))
    dummy_df["open"] = dummy_df["open"].apply(lambda x: x + (x % 5) * (-1)**(x//5))

    strategy = StrategyCore()
    processed_df = strategy.apply_all_strategies(dummy_df.copy())
    print("Strategy indicators applied successfully!")
    print(f"Columns added: {[col for col in processed_df.columns if col not in dummy_df.columns]}")


