import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self, config=None):
        self.config = config or {}

    def calculate_adaptive_sl(self, entry_price, current_price, is_buy, atr_value=None):
        """Calculate adaptive stop loss based on ATR or percentage"""
        if atr_value and atr_value > 0:
            # Use ATR-based stop loss (more adaptive to volatility)
            if is_buy:
                sl = entry_price - (atr_value * 2)  # 2x ATR below entry for buy
            else:
                sl = entry_price + (atr_value * 2)  # 2x ATR above entry for sell
        else:
            # Fallback to percentage-based stop loss
            if is_buy:
                sl = entry_price * 0.995  # 0.5% below entry
            else:
                sl = entry_price * 1.005  # 0.5% above entry
        return round(sl, 5)

    def calculate_multi_level_tp(self, entry_price, is_buy, atr_value=None, rr_ratio_base=1.0):
        """Calculate multi-level take profit targets"""
        tps = []
        if atr_value and atr_value > 0:
            # ATR-based take profit levels
            if is_buy:
                for i in range(1, 6):
                    tp = entry_price + (atr_value * i * rr_ratio_base)
                    tps.append(round(tp, 5))
            else:
                for i in range(1, 6):
                    tp = entry_price - (atr_value * i * rr_ratio_base)
                    tps.append(round(tp, 5))
        else:
            # Percentage-based take profit levels
            if is_buy:
                for i in range(1, 6):
                    tp = entry_price * (1 + rr_ratio_base * i * 0.005)  # 0.5% increment per TP level
                    tps.append(round(tp, 5))
            else:
                for i in range(1, 6):
                    tp = entry_price * (1 - rr_ratio_base * i * 0.005)  # 0.5% decrement per TP level
                    tps.append(round(tp, 5))
        return tps

    def calculate_risk_reward_ratio(self, entry_price, sl_price, tp_price, is_buy):
        """Calculate risk-reward ratio"""
        if is_buy:
            risk = entry_price - sl_price
            reward = tp_price - entry_price
        else:
            risk = sl_price - entry_price
            reward = entry_price - tp_price

        if risk <= 0:
            return 0  # Avoid division by zero or negative risk
        return round(reward / risk, 2)

    def calculate_confidence_score(self, df, signal_type):
        """Calculate confidence score based on multiple factors"""
        last_row = df.iloc[-1]
        score = 0
        
        # Base score for signal type
        if signal_type == "BUY":
            # EMA trend alignment
            if last_row.get("Golden_Cross", False):
                score += 20
            if last_row.get("EMA_Short", 0) > last_row.get("EMA_Long", 0):
                score += 10
                
            # RSI conditions
            if 30 < last_row.get("RSI", 50) < 70:
                score += 15
            elif last_row.get("RSI_Oversold", False):
                score += 20
                
            # Market structure
            if last_row.get("BOS_Bullish", False):
                score += 15
            if last_row.get("Bullish_OB", False):
                score += 15
            if last_row.get("FVG_Bullish", False):
                score += 10
            if last_row.get("Bullish_Divergence", False):
                score += 15
                
            # Candlestick patterns
            if last_row.get("Engulfing_Bullish", False):
                score += 10
            if last_row.get("Pinbar_Bullish", False):
                score += 10
                
        elif signal_type == "SELL":
            # EMA trend alignment
            if last_row.get("Death_Cross", False):
                score += 20
            if last_row.get("EMA_Short", 0) < last_row.get("EMA_Long", 0):
                score += 10
                
            # RSI conditions
            if 30 < last_row.get("RSI", 50) < 70:
                score += 15
            elif last_row.get("RSI_Overbought", False):
                score += 20
                
            # Market structure
            if last_row.get("BOS_Bearish", False):
                score += 15
            if last_row.get("Bearish_OB", False):
                score += 15
            if last_row.get("FVG_Bearish", False):
                score += 10
            if last_row.get("Bearish_Divergence", False):
                score += 15
                
            # Candlestick patterns
            if last_row.get("Engulfing_Bearish", False):
                score += 10
            if last_row.get("Pinbar_Bearish", False):
                score += 10
        
        # Volatility consideration
        if last_row.get("ATR", 0) > 0:
            # Higher volatility might indicate better opportunities
            score += min(10, last_row["ATR"] / last_row["close"] * 1000)
        
        return min(100, max(0, score))

    def generate_signal(self, processed_df, symbol, timeframe):
        """Generate trading signal based on processed data"""
        if processed_df.empty or len(processed_df) < 50:
            return None

        last_row = processed_df.iloc[-1]
        atr_value = last_row.get("ATR", None)

        # Handle timestamp - it might be in the index or a column
        timestamp = None
        if "timestamp" in last_row:
            timestamp = last_row["timestamp"]
        elif processed_df.index.name == "timestamp":
            timestamp = processed_df.index[-1]
        else:
            timestamp = pd.Timestamp.now()

        signal = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": timestamp,
            "signal_type": "NONE",
            "entry_price": None,
            "stop_loss": None,
            "take_profit": [],
            "risk_reward_ratio": None,
            "confidence_score": 0,
            "expiry_time_hours": 4,  # Default expiry time
            "alert_message": "",
            "status_tag": "",
            "emoji": "",
            "atr_value": atr_value
        }

        # Buy signal conditions
        buy_conditions = (
            last_row.get("Golden_Cross", False) and
            last_row.get("RSI", 50) < 70 and
            (last_row.get("Bullish_OB", False) or last_row.get("BOS_Bullish", False) or last_row.get("Bullish_Divergence", False))
        )

        # Sell signal conditions
        sell_conditions = (
            last_row.get("Death_Cross", False) and
            last_row.get("RSI", 50) > 30 and
            (last_row.get("Bearish_OB", False) or last_row.get("BOS_Bearish", False) or last_row.get("Bearish_Divergence", False))
        )

        if buy_conditions:
            signal["signal_type"] = "BUY"
            signal["entry_price"] = last_row["close"]
            signal["stop_loss"] = self.calculate_adaptive_sl(signal["entry_price"], last_row["close"], True, atr_value)
            signal["take_profit"] = self.calculate_multi_level_tp(signal["entry_price"], True, atr_value)
            signal["risk_reward_ratio"] = self.calculate_risk_reward_ratio(signal["entry_price"], signal["stop_loss"], signal["take_profit"][0], True)
            signal["confidence_score"] = self.calculate_confidence_score(processed_df, "BUY")
            
            entry_p = signal["entry_price"]
            sl_p = signal["stop_loss"]
            tp1_p = signal["take_profit"][0]
            signal["alert_message"] = f"BUY Signal for {symbol} on {timeframe}! Entry: {entry_p}. SL: {sl_p}. TP1: {tp1_p}"
            signal["status_tag"] = "#TRADEALERT"
            signal["emoji"] = "📈"
            
        elif sell_conditions:
            signal["signal_type"] = "SELL"
            signal["entry_price"] = last_row["close"]
            signal["stop_loss"] = self.calculate_adaptive_sl(signal["entry_price"], last_row["close"], False, atr_value)
            signal["take_profit"] = self.calculate_multi_level_tp(signal["entry_price"], False, atr_value)
            signal["risk_reward_ratio"] = self.calculate_risk_reward_ratio(signal["entry_price"], signal["stop_loss"], signal["take_profit"][0], False)
            signal["confidence_score"] = self.calculate_confidence_score(processed_df, "SELL")
            
            entry_p = signal["entry_price"]
            sl_p = signal["stop_loss"]
            tp1_p = signal["take_profit"][0]
            signal["alert_message"] = f"SELL Signal for {symbol} on {timeframe}! Entry: {entry_p}. SL: {sl_p}. TP1: {tp1_p}"
            signal["status_tag"] = "#TRADEALERT"
            signal["emoji"] = "📉"

        # Only return signals with minimum confidence
        if signal["confidence_score"] < 50:
            signal["signal_type"] = "NONE"
            signal["confidence_score"] = 0

        return signal

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy DataFrame for testing
    data = {
        'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='H')),
        'open': np.random.rand(100) * 100 + 100,
        'high': np.random.rand(100) * 100 + 105,
        'low': np.random.rand(100) * 100 + 95,
        'close': np.random.rand(100) * 100 + 100,
        'volume': np.random.rand(100) * 1000
    }
    dummy_df = pd.DataFrame(data)
    
    # Add required indicators
    dummy_df["Golden_Cross"] = False
    dummy_df["Death_Cross"] = False
    dummy_df["RSI"] = 50
    dummy_df["ATR"] = 2.0
    dummy_df["Bullish_OB"] = False
    dummy_df["Bearish_OB"] = False
    dummy_df["BOS_Bullish"] = False
    dummy_df["BOS_Bearish"] = False
    dummy_df["Bullish_Divergence"] = False
    dummy_df["Bearish_Divergence"] = False

    # Simulate a Golden Cross and Bullish OB for a buy signal
    dummy_df.loc[99, "Golden_Cross"] = True
    dummy_df.loc[99, "Bullish_OB"] = True
    dummy_df.loc[99, "close"] = 150  # Example entry price

    signal_gen = SignalGenerator()
    signal = signal_gen.generate_signal(dummy_df, "EUR/USD", "H1")
    print("Generated signal:", signal)


