"""
Enhanced Strategy Core for Forex Trading Bot
Implements comprehensive technical analysis with complete indicator calculations
"""

import pandas as pd
import ta
import numpy as np
from typing import Dict, List, Optional, Tuple

class EnhancedStrategyCore:
    def __init__(self, config=None):
        self.config = config or {}
        self.lookback_periods = {
            'ema_short': 20,
            'ema_long': 50,
            'rsi': 14,
            'atr': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'stoch_k': 14,
            'stoch_d': 3,
            'adx': 14
        }
        
        # Update with config values if provided
        if 'INDICATOR_PERIODS' in self.config:
            self.lookback_periods.update(self.config['INDICATOR_PERIODS'])
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for the dataframe"""
        if df.empty or len(df) < 100:
            return df
        
        # Make a copy to avoid modifying original
        result_df = df.copy()
        
        # Basic price indicators
        result_df = self._calculate_moving_averages(result_df)
        result_df = self._calculate_momentum_indicators(result_df)
        result_df = self._calculate_volatility_indicators(result_df)
        result_df = self._calculate_trend_indicators(result_df)
        result_df = self._calculate_volume_indicators(result_df)
        
        # Advanced pattern recognition
        result_df = self._detect_candlestick_patterns(result_df)
        result_df = self._detect_market_structure(result_df)
        result_df = self._detect_divergences(result_df)
        result_df = self._identify_support_resistance(result_df)
        
        return result_df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various moving averages"""
        # Exponential Moving Averages
        df["EMA_Short"] = ta.trend.ema_indicator(
            df["close"], window=self.lookback_periods['ema_short']
        )
        df["EMA_Long"] = ta.trend.ema_indicator(
            df["close"], window=self.lookback_periods['ema_long']
        )
        
        # Simple Moving Averages
        df["SMA_20"] = ta.trend.sma_indicator(df["close"], window=20)
        df["SMA_50"] = ta.trend.sma_indicator(df["close"], window=50)
        df["SMA_200"] = ta.trend.sma_indicator(df["close"], window=200)
        
        # Weighted Moving Average
        df["WMA_20"] = ta.trend.wma_indicator(df["close"], window=20)
        
        # EMA Crossover signals
        df["Golden_Cross"] = (
            (df["EMA_Short"].shift(1) <= df["EMA_Long"].shift(1)) & 
            (df["EMA_Short"] > df["EMA_Long"])
        )
        df["Death_Cross"] = (
            (df["EMA_Short"].shift(1) >= df["EMA_Long"].shift(1)) & 
            (df["EMA_Short"] < df["EMA_Long"])
        )
        
        # Trend strength
        df["EMA_Trend_Strength"] = (df["EMA_Short"] - df["EMA_Long"]) / df["EMA_Long"] * 100
        
        return df
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum-based indicators"""
        # RSI
        df["RSI"] = ta.momentum.rsi(df["close"], window=self.lookback_periods['rsi'])
        df["RSI_Overbought"] = df["RSI"] > 70
        df["RSI_Oversold"] = df["RSI"] < 30
        
        # Stochastic Oscillator
        df["Stoch_K"] = ta.momentum.stoch(
            df["high"], df["low"], df["close"], 
            window=self.lookback_periods['stoch_k']
        )
        df["Stoch_D"] = ta.momentum.stoch_signal(
            df["high"], df["low"], df["close"],
            window=self.lookback_periods['stoch_k'],
            smooth_window=self.lookback_periods['stoch_d']
        )
        
        # MACD
        macd_line = ta.trend.macd(
            df["close"],
            window_slow=self.lookback_periods['macd_slow'],
            window_fast=self.lookback_periods['macd_fast']
        )
        macd_signal = ta.trend.macd_signal(
            df["close"],
            window_slow=self.lookback_periods['macd_slow'],
            window_fast=self.lookback_periods['macd_fast'],
            window_sign=self.lookback_periods['macd_signal']
        )
        macd_histogram = ta.trend.macd_diff(
            df["close"],
            window_slow=self.lookback_periods['macd_slow'],
            window_fast=self.lookback_periods['macd_fast'],
            window_sign=self.lookback_periods['macd_signal']
        )
        
        df["MACD"] = macd_line
        df["MACD_Signal"] = macd_signal
        df["MACD_Histogram"] = macd_histogram
        df["MACD_Bullish"] = (
            (df["MACD"].shift(1) <= df["MACD_Signal"].shift(1)) &
            (df["MACD"] > df["MACD_Signal"])
        )
        df["MACD_Bearish"] = (
            (df["MACD"].shift(1) >= df["MACD_Signal"].shift(1)) &
            (df["MACD"] < df["MACD_Signal"])
        )
        
        # Williams %R
        df["Williams_R"] = ta.momentum.williams_r(
            df["high"], df["low"], df["close"], lbp=14
        )
        
        # Rate of Change
        df["ROC"] = ta.momentum.roc(df["close"], window=12)
        
        return df
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility-based indicators"""
        # Average True Range
        df["ATR"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], 
            window=self.lookback_periods['atr']
        )
        
        # Bollinger Bands
        bb_high = ta.volatility.bollinger_hband(
            df["close"], 
            window=self.lookback_periods['bb_period'],
            window_dev=self.lookback_periods['bb_std']
        )
        bb_low = ta.volatility.bollinger_lband(
            df["close"],
            window=self.lookback_periods['bb_period'],
            window_dev=self.lookback_periods['bb_std']
        )
        bb_mid = ta.volatility.bollinger_mavg(
            df["close"],
            window=self.lookback_periods['bb_period']
        )
        
        df["BB_Upper"] = bb_high
        df["BB_Lower"] = bb_low
        df["BB_Middle"] = bb_mid
        df["BB_Width"] = (bb_high - bb_low) / bb_mid * 100
        df["BB_Position"] = (df["close"] - bb_low) / (bb_high - bb_low)
        
        # Bollinger Band signals
        df["BB_Squeeze"] = df["BB_Width"] < df["BB_Width"].rolling(20).quantile(0.2)
        df["BB_Upper_Touch"] = df["close"] >= df["BB_Upper"]
        df["BB_Lower_Touch"] = df["close"] <= df["BB_Lower"]
        
        # Keltner Channels
        df["KC_Upper"] = ta.volatility.keltner_channel_hband(
            df["high"], df["low"], df["close"], window=20
        )
        df["KC_Lower"] = ta.volatility.keltner_channel_lband(
            df["high"], df["low"], df["close"], window=20
        )
        df["KC_Middle"] = ta.volatility.keltner_channel_mband(
            df["high"], df["low"], df["close"], window=20
        )
        
        return df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend-based indicators"""
        # ADX (Average Directional Index)
        df["ADX"] = ta.trend.adx(
            df["high"], df["low"], df["close"], 
            window=self.lookback_periods['adx']
        )
        df["ADX_Strong_Trend"] = df["ADX"] > 25
        df["ADX_Weak_Trend"] = df["ADX"] < 20
        
        # Directional Movement
        df["DI_Plus"] = ta.trend.adx_pos(
            df["high"], df["low"], df["close"], window=14
        )
        df["DI_Minus"] = ta.trend.adx_neg(
            df["high"], df["low"], df["close"], window=14
        )
        
        # Parabolic SAR
        df["PSAR"] = ta.trend.psar_down(df["high"], df["low"], df["close"])
        df["PSAR_Bullish"] = df["close"] > df["PSAR"]
        df["PSAR_Bearish"] = df["close"] < df["PSAR"]
        
        # Ichimoku Cloud
        df["Ichimoku_A"] = ta.trend.ichimoku_a(df["high"], df["low"])
        df["Ichimoku_B"] = ta.trend.ichimoku_b(df["high"], df["low"])
        df["Ichimoku_Base"] = ta.trend.ichimoku_base_line(df["high"], df["low"])
        df["Ichimoku_Conversion"] = ta.trend.ichimoku_conversion_line(df["high"], df["low"])
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        if 'volume' not in df.columns:
            df['volume'] = 1  # Default volume if not available
        
        # Volume Moving Average
        df["Volume_MA"] = df["volume"].rolling(20).mean()
        df["Volume_Ratio"] = df["volume"] / df["Volume_MA"]
        df["High_Volume"] = df["Volume_Ratio"] > 1.5
        
        # On-Balance Volume
        df["OBV"] = ta.volume.on_balance_volume(df["close"], df["volume"])
        
        # Volume Price Trend
        df["VPT"] = ta.volume.volume_price_trend(df["close"], df["volume"])
        
        # Accumulation/Distribution Line
        df["ADL"] = ta.volume.acc_dist_index(
            df["high"], df["low"], df["close"], df["volume"]
        )
        
        return df
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect candlestick patterns"""
        # Basic candle properties
        df["Body_Size"] = abs(df["close"] - df["open"])
        df["Upper_Shadow"] = df["high"] - df[["open", "close"]].max(axis=1)
        df["Lower_Shadow"] = df[["open", "close"]].min(axis=1) - df["low"]
        df["Total_Range"] = df["high"] - df["low"]
        
        # Doji patterns
        df["Doji"] = df["Body_Size"] < (df["Total_Range"] * 0.1)
        
        # Hammer and Hanging Man
        df["Hammer"] = (
            (df["Lower_Shadow"] > df["Body_Size"] * 2) &
            (df["Upper_Shadow"] < df["Body_Size"] * 0.5) &
            (df["close"] > df["open"])
        )
        df["Hanging_Man"] = (
            (df["Lower_Shadow"] > df["Body_Size"] * 2) &
            (df["Upper_Shadow"] < df["Body_Size"] * 0.5) &
            (df["close"] < df["open"])
        )
        
        # Shooting Star and Inverted Hammer
        df["Shooting_Star"] = (
            (df["Upper_Shadow"] > df["Body_Size"] * 2) &
            (df["Lower_Shadow"] < df["Body_Size"] * 0.5) &
            (df["close"] < df["open"])
        )
        df["Inverted_Hammer"] = (
            (df["Upper_Shadow"] > df["Body_Size"] * 2) &
            (df["Lower_Shadow"] < df["Body_Size"] * 0.5) &
            (df["close"] > df["open"])
        )
        
        # Engulfing patterns
        df["Bullish_Engulfing"] = (
            (df["close"].shift(1) < df["open"].shift(1)) &  # Previous red candle
            (df["close"] > df["open"]) &  # Current green candle
            (df["open"] < df["close"].shift(1)) &  # Current open below previous close
            (df["close"] > df["open"].shift(1))  # Current close above previous open
        )
        df["Bearish_Engulfing"] = (
            (df["close"].shift(1) > df["open"].shift(1)) &  # Previous green candle
            (df["close"] < df["open"]) &  # Current red candle
            (df["open"] > df["close"].shift(1)) &  # Current open above previous close
            (df["close"] < df["open"].shift(1))  # Current close below previous open
        )
        
        # Pin bars
        df["Bullish_Pinbar"] = (
            (df["Lower_Shadow"] > df["Body_Size"] * 2) &
            (df["Lower_Shadow"] > df["Upper_Shadow"] * 2) &
            (df["close"] > (df["high"] + df["low"]) / 2)
        )
        df["Bearish_Pinbar"] = (
            (df["Upper_Shadow"] > df["Body_Size"] * 2) &
            (df["Upper_Shadow"] > df["Lower_Shadow"] * 2) &
            (df["close"] < (df["high"] + df["low"]) / 2)
        )
        
        return df
    
    def _detect_market_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect market structure patterns"""
        window = 5
        
        # Swing highs and lows
        df["Swing_High"] = (
            (df["high"] == df["high"].rolling(window*2+1, center=True).max()) &
            (df["high"].shift(window) < df["high"]) &
            (df["high"].shift(-window) < df["high"])
        )
        df["Swing_Low"] = (
            (df["low"] == df["low"].rolling(window*2+1, center=True).min()) &
            (df["low"].shift(window) > df["low"]) &
            (df["low"].shift(-window) > df["low"])
        )
        
        # Higher highs and lower lows
        swing_highs = df[df["Swing_High"]]["high"]
        swing_lows = df[df["Swing_Low"]]["low"]
        
        df["Higher_High"] = False
        df["Lower_Low"] = False
        df["Lower_High"] = False
        df["Higher_Low"] = False
        
        # Break of Structure (BOS)
        df["BOS_Bullish"] = (
            (df["close"] > df["high"].rolling(20).max().shift(1)) &
            (df["close"].shift(1) <= df["high"].rolling(20).max().shift(2))
        )
        df["BOS_Bearish"] = (
            (df["close"] < df["low"].rolling(20).min().shift(1)) &
            (df["close"].shift(1) >= df["low"].rolling(20).min().shift(2))
        )
        
        # Change of Character (CHoCH)
        df["CHoCH_Bullish"] = (
            df["BOS_Bullish"] & 
            (df["EMA_Short"].shift(5) < df["EMA_Long"].shift(5))
        )
        df["CHoCH_Bearish"] = (
            df["BOS_Bearish"] & 
            (df["EMA_Short"].shift(5) > df["EMA_Long"].shift(5))
        )
        
        return df
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify support and resistance levels"""
        window = 10
        
        # Local maxima and minima
        df["Local_Max"] = df["high"] == df["high"].rolling(window*2+1, center=True).max()
        df["Local_Min"] = df["low"] == df["low"].rolling(window*2+1, center=True).min()
        
        # Support and resistance levels
        resistance_levels = df[df["Local_Max"]]["high"].dropna()
        support_levels = df[df["Local_Min"]]["low"].dropna()
        
        # Current price relative to S/R levels
        current_price = df["close"].iloc[-1] if not df.empty else 0
        
        # Find nearest support and resistance
        if len(resistance_levels) > 0:
            nearest_resistance = resistance_levels[resistance_levels > current_price].min()
            df["Nearest_Resistance"] = nearest_resistance
            df["Distance_To_Resistance"] = (nearest_resistance - current_price) / current_price * 100
        else:
            df["Nearest_Resistance"] = np.nan
            df["Distance_To_Resistance"] = np.nan
        
        if len(support_levels) > 0:
            nearest_support = support_levels[support_levels < current_price].max()
            df["Nearest_Support"] = nearest_support
            df["Distance_To_Support"] = (current_price - nearest_support) / current_price * 100
        else:
            df["Nearest_Support"] = np.nan
            df["Distance_To_Support"] = np.nan
        
        return df
    
    def _detect_divergences(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect price-indicator divergences"""
        window = 10
        
        # Price peaks and troughs
        price_peaks = df["high"].rolling(window*2+1, center=True).max() == df["high"]
        price_troughs = df["low"].rolling(window*2+1, center=True).min() == df["low"]
        
        # RSI peaks and troughs
        rsi_peaks = df["RSI"].rolling(window*2+1, center=True).max() == df["RSI"]
        rsi_troughs = df["RSI"].rolling(window*2+1, center=True).min() == df["RSI"]
        
        # MACD peaks and troughs
        macd_peaks = df["MACD"].rolling(window*2+1, center=True).max() == df["MACD"]
        macd_troughs = df["MACD"].rolling(window*2+1, center=True).min() == df["MACD"]
        
        # Bullish divergence (price makes lower low, indicator makes higher low)
        df["RSI_Bullish_Divergence"] = False
        df["MACD_Bullish_Divergence"] = False
        df["RSI_Bearish_Divergence"] = False
        df["MACD_Bearish_Divergence"] = False
        
        # Simplified divergence detection
        for i in range(window*2, len(df)-window):
            # Look for recent peaks/troughs
            recent_price_peaks = df.iloc[i-window:i+window][price_peaks.iloc[i-window:i+window]]
            recent_rsi_peaks = df.iloc[i-window:i+window][rsi_peaks.iloc[i-window:i+window]]
            
            if len(recent_price_peaks) >= 2 and len(recent_rsi_peaks) >= 2:
                # Check for bearish divergence
                if (recent_price_peaks["high"].iloc[-1] > recent_price_peaks["high"].iloc[-2] and
                    recent_rsi_peaks["RSI"].iloc[-1] < recent_rsi_peaks["RSI"].iloc[-2]):
                    df.iloc[i, df.columns.get_loc("RSI_Bearish_Divergence")] = True
        
        # Combine divergences
        df["Bullish_Divergence"] = df["RSI_Bullish_Divergence"] | df["MACD_Bullish_Divergence"]
        df["Bearish_Divergence"] = df["RSI_Bearish_Divergence"] | df["MACD_Bearish_Divergence"]
        
        return df
    
    def identify_fair_value_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify Fair Value Gaps (FVG)"""
        # Bullish FVG: candle 1 high < candle 3 low
        df["FVG_Bullish"] = (
            (df["high"].shift(2) < df["low"]) & 
            (df["close"] > df["open"]) &
            (df["close"].shift(1) > df["open"].shift(1))
        )
        
        # Bearish FVG: candle 1 low > candle 3 high
        df["FVG_Bearish"] = (
            (df["low"].shift(2) > df["high"]) & 
            (df["close"] < df["open"]) &
            (df["close"].shift(1) < df["open"].shift(1))
        )
        
        return df
    
    def identify_order_blocks(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify Order Blocks"""
        # Bullish Order Block: Last bearish candle before bullish move
        df["Bullish_OB"] = (
            (df["close"].shift(1) < df["open"].shift(1)) &  # Previous bearish candle
            (df["close"] > df["open"]) &  # Current bullish candle
            (df["close"] > df["high"].shift(1)) &  # Break above previous high
            (df["BOS_Bullish"] == True)  # Confirmed by BOS
        )
        
        # Bearish Order Block: Last bullish candle before bearish move
        df["Bearish_OB"] = (
            (df["close"].shift(1) > df["open"].shift(1)) &  # Previous bullish candle
            (df["close"] < df["open"]) &  # Current bearish candle
            (df["close"] < df["low"].shift(1)) &  # Break below previous low
            (df["BOS_Bearish"] == True)  # Confirmed by BOS
        )
        
        return df
    
    def calculate_market_regime(self, df: pd.DataFrame) -> str:
        """Determine current market regime"""
        if df.empty or len(df) < 50:
            return "UNKNOWN"
        
        recent_data = df.tail(20)
        
        # Trend strength
        ema_trend = recent_data["EMA_Trend_Strength"].mean()
        adx_avg = recent_data["ADX"].mean()
        
        # Volatility
        atr_ratio = recent_data["ATR"].mean() / recent_data["close"].mean()
        bb_width_avg = recent_data["BB_Width"].mean()
        
        # Determine regime
        if adx_avg > 25 and abs(ema_trend) > 1:
            if ema_trend > 0:
                return "STRONG_UPTREND"
            else:
                return "STRONG_DOWNTREND"
        elif adx_avg > 20 and abs(ema_trend) > 0.5:
            if ema_trend > 0:
                return "WEAK_UPTREND"
            else:
                return "WEAK_DOWNTREND"
        elif bb_width_avg < 2 and atr_ratio < 0.01:
            return "LOW_VOLATILITY_RANGE"
        elif bb_width_avg > 5 and atr_ratio > 0.02:
            return "HIGH_VOLATILITY_RANGE"
        else:
            return "SIDEWAYS_RANGE"
    
    def get_strategy_signals(self, df: pd.DataFrame) -> Dict:
        """Get comprehensive strategy signals"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        regime = self.calculate_market_regime(df)
        
        signals = {
            'regime': regime,
            'trend_signals': {
                'ema_trend': 'BULLISH' if latest.get('EMA_Short', 0) > latest.get('EMA_Long', 0) else 'BEARISH',
                'golden_cross': latest.get('Golden_Cross', False),
                'death_cross': latest.get('Death_Cross', False),
                'adx_strength': latest.get('ADX', 0),
                'psar_signal': 'BULLISH' if latest.get('PSAR_Bullish', False) else 'BEARISH'
            },
            'momentum_signals': {
                'rsi_level': latest.get('RSI', 50),
                'rsi_overbought': latest.get('RSI_Overbought', False),
                'rsi_oversold': latest.get('RSI_Oversold', False),
                'macd_signal': 'BULLISH' if latest.get('MACD_Bullish', False) else 'BEARISH',
                'stoch_level': latest.get('Stoch_K', 50)
            },
            'volatility_signals': {
                'bb_position': latest.get('BB_Position', 0.5),
                'bb_squeeze': latest.get('BB_Squeeze', False),
                'atr_level': latest.get('ATR', 0),
                'volatility_regime': 'HIGH' if latest.get('BB_Width', 0) > 5 else 'LOW'
            },
            'pattern_signals': {
                'bullish_engulfing': latest.get('Bullish_Engulfing', False),
                'bearish_engulfing': latest.get('Bearish_Engulfing', False),
                'bullish_pinbar': latest.get('Bullish_Pinbar', False),
                'bearish_pinbar': latest.get('Bearish_Pinbar', False),
                'doji': latest.get('Doji', False)
            },
            'structure_signals': {
                'bos_bullish': latest.get('BOS_Bullish', False),
                'bos_bearish': latest.get('BOS_Bearish', False),
                'bullish_ob': latest.get('Bullish_OB', False),
                'bearish_ob': latest.get('Bearish_OB', False),
                'fvg_bullish': latest.get('FVG_Bullish', False),
                'fvg_bearish': latest.get('FVG_Bearish', False)
            },
            'divergence_signals': {
                'bullish_divergence': latest.get('Bullish_Divergence', False),
                'bearish_divergence': latest.get('Bearish_Divergence', False)
            }
        }
        
        return signals

# Example usage
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=500, freq='H')
    
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(500).cumsum() + 100,
        'high': np.random.randn(500).cumsum() + 102,
        'low': np.random.randn(500).cumsum() + 98,
        'close': np.random.randn(500).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 500)
    })
    
    # Test Enhanced Strategy Core
    strategy = EnhancedStrategyCore()
    processed_data = strategy.calculate_all_indicators(sample_data)
    signals = strategy.get_strategy_signals(processed_data)
    
    print("Sample processed data columns:", processed_data.columns.tolist())
    print("Strategy signals:", signals)

