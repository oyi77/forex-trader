import pandas as pd
import numpy as np

class SignalGenerator:
    def __init__(self):
        pass

    def calculate_adaptive_sl(self, entry_price, current_price, is_buy, atr_value=None):
        # This is a placeholder for adaptive SL logic. 
        # A real adaptive SL would consider market volatility (e.g., ATR), 
        # market structure (e.g., previous swing low/high), or other indicators.
        # For now, a simple percentage-based SL is used as a starting point.
        if is_buy:
            # For a buy signal, SL is typically below entry price
            sl = entry_price * 0.995 # 0.5% below entry
        else:
            # For a sell signal, SL is typically above entry price
            sl = entry_price * 1.005 # 0.5% above entry
        return round(sl, 5)

    def calculate_multi_level_tp(self, entry_price, is_buy, rr_ratio_base=1.0):
        # Multi-level TP calculation. This is a simplified example.
        # In a real scenario, TP levels would be based on market structure, 
        # Fibonacci extensions, or other technical analysis.
        tps = []
        if is_buy:
            for i in range(1, 6):
                tp = entry_price * (1 + rr_ratio_base * i * 0.005) # 0.5% increment per TP level
                tps.append(round(tp, 5))
        else:
            for i in range(1, 6):
                tp = entry_price * (1 - rr_ratio_base * i * 0.005) # 0.5% decrement per TP level
                tps.append(round(tp, 5))
        return tps

    def calculate_risk_reward_ratio(self, entry_price, sl_price, tp_price, is_buy):
        if is_buy:
            risk = entry_price - sl_price
            reward = tp_price - entry_price
        else:
            risk = sl_price - entry_price
            reward = entry_price - tp_price

        if risk <= 0:
            return 0 # Avoid division by zero or negative risk
        return round(reward / risk, 2)

    def generate_signal(self, processed_df, symbol, timeframe):
        # This function will take the processed DataFrame and generate a signal
        # based on the combined logic from StrategyCore.
        # This is a highly simplified example and needs significant refinement.

        last_row = processed_df.iloc[-1]

        signal = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": last_row["timestamp"],
            "signal_type": "NONE",
            "entry_price": None,
            "stop_loss": None,
            "take_profit": [],
            "risk_reward_ratio": None,
            "confidence_score": 0,
            "expiry_time_hours": 4, # Default expiry time
            "alert_message": "",
            "status_tag": "",
            "emoji": ""
        }

        # Example signal generation logic (highly simplified)
        if last_row["Golden_Cross"] and last_row["RSI"] < 70 and last_row["Bullish_OB"]:
            signal["signal_type"] = "BUY"
            signal["entry_price"] = last_row["close"]
            signal["stop_loss"] = self.calculate_adaptive_sl(signal["entry_price"], last_row["close"], True)
            signal["take_profit"] = self.calculate_multi_level_tp(signal["entry_price"], True)
            signal["risk_reward_ratio"] = self.calculate_risk_reward_ratio(signal["entry_price"], signal["stop_loss"], signal["take_profit"][0], True)
            signal["confidence_score"] = 85
            entry_p = signal["entry_price"]
            sl_p = signal["stop_loss"]
            tp1_p = signal["take_profit"][0]
            signal["alert_message"] = f"BUY Signal for {symbol} on {timeframe}! Entry: {entry_p}. SL: {sl_p}. TP1: {tp1_p}"
            signal["status_tag"] = "#TRADEALERT"
            signal["emoji"] = "📈"
        elif last_row["Death_Cross"] and last_row["RSI"] > 30 and last_row["Bearish_OB"]:
            signal["signal_type"] = "SELL"
            signal["entry_price"] = last_row["close"]
            signal["stop_loss"] = self.calculate_adaptive_sl(signal["entry_price"], last_row["close"], False)
            signal["take_profit"] = self.calculate_multi_level_tp(signal["entry_price"], False)
            signal["risk_reward_ratio"] = self.calculate_risk_reward_ratio(signal["entry_price"], signal["stop_loss"], signal["take_profit"][0], False)
            signal["confidence_score"] = 80
            entry_p = signal["entry_price"]
            sl_p = signal["stop_loss"]
            tp1_p = signal["take_profit"][0]
            signal["alert_message"] = f"SELL Signal for {symbol} on {timeframe}! Entry: {entry_p}. SL: {sl_p}. TP1: {tp1_p}"
            signal["status_tag"] = "#TRADEALERT"
            signal["emoji"] = "📉"

        return signal

# Example Usage (for testing purposes)
# if __name__ == "__main__":
#     # Create a dummy DataFrame for testing
#     data = {
#         'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='H')),
#         'open': np.random.rand(100) * 100 + 100,
#         'high': np.random.rand(100) * 100 + 105,
#         'low': np.random.rand(100) * 100 + 95,
#         'close': np.random.rand(100) * 100 + 100,
#         'volume': np.random.rand(100) * 1000
#     }
#     dummy_df = pd.DataFrame(data)
#     dummy_df["Golden_Cross"] = False
#     dummy_df["Death_Cross"] = False
#     dummy_df["RSI"] = 50
#     dummy_df["Bullish_OB"] = False
#     dummy_df["Bearish_OB"] = False

#     # Simulate a Golden Cross and Bullish OB for a buy signal
#     dummy_df.loc[99, "Golden_Cross"] = True
#     dummy_df.loc[99, "Bullish_OB"] = True
#     dummy_df.loc[99, "close"] = 150 # Example entry price

#     signal_gen = SignalGenerator()
#     signal = signal_gen.generate_signal(dummy_df, "EUR/USD", "H1")
#     print(signal)

#     # Simulate a Death Cross and Bearish OB for a sell signal
#     dummy_df.loc[99, "Golden_Cross"] = False
#     dummy_df.loc[99, "Bullish_OB"] = False
#     dummy_df.loc[99, "Death_Cross"] = True
#     dummy_df.loc[99, "Bearish_OB"] = True
#     dummy_df.loc[99, "close"] = 140 # Example entry price

#     signal = signal_gen.generate_signal(dummy_df, "EUR/USD", "H1")
#     print(signal)


