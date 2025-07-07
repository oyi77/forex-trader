import pandas as pd
import requests
import time

class Monitoring:
    def __init__(self, config=None):
        self.config = config if config else {}
        self.news_api_key = self.config.get("NEWS_API_KEY")
        self.news_api_url = self.config.get("NEWS_API_URL")
        self.telegram_bot_token = self.config.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = self.config.get("TELEGRAM_CHAT_ID")
        self.trading_paused = False
        self.max_drawdown_percent = self.config.get("MAX_DRAWDOWN_PERCENT", 0.05)
        self.initial_equity = 10000 # Placeholder, should be dynamic
        self.current_equity = self.initial_equity
        self.peak_equity = self.initial_equity
        self.max_drawdown = 0
        self.trade_log = []

    def fetch_news_calendar(self):
        if not self.news_api_url or not self.news_api_key:
            print("News API URL or Key not configured. Skipping news check.")
            return []
        try:
            # This is a placeholder. A real API call would have proper parameters.
            response = requests.get(self.news_api_url, params={
                "apiKey": self.news_api_key,
                "from": pd.Timestamp.now().isoformat(),
                "to": (pd.Timestamp.now() + pd.Timedelta(days=1)).isoformat()
            })
            response.raise_for_status() # Raise an exception for HTTP errors
            news_data = response.json()
            # Filter for high-impact news. This depends on the API\"s response structure.
            high_impact_news = [event for event in news_data.get("events", []) if event.get("impact") == "high"]
            return high_impact_news
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news calendar: {e}")
            return []

    def volatility_guard(self):
        news_events = self.fetch_news_calendar()
        current_time = pd.Timestamp.now()
        for event in news_events:
            event_time = pd.to_datetime(event.get("time")) # Assuming \"time\" field exists
            time_diff_before = (event_time - current_time).total_seconds() / 60
            time_diff_after = (current_time - event_time).total_seconds() / 60

            if (-30 <= time_diff_before <= 0) or (0 <= time_diff_after <= 30):
                if not self.trading_paused:
                    self.trading_paused = True
                    self.send_telegram_alert("🚨 Volatility Guard: Trading paused due to high-impact news.")
                    print("Trading paused due to high-impact news.")
                return True
        if self.trading_paused:
            self.trading_paused = False
            self.send_telegram_alert("✅ Volatility Guard: Trading resumed.")
            print("Trading resumed.")
        return False

    def drawdown_monitor(self, current_pnl):
        self.current_equity += current_pnl # Update equity with latest PnL
        self.peak_equity = max(self.peak_equity, self.current_equity)
        drawdown = (self.peak_equity - self.current_equity) / self.peak_equity
        self.max_drawdown = max(self.max_drawdown, drawdown)

        if drawdown > self.max_drawdown_percent and not self.trading_paused:
            self.trading_paused = True
            self.send_telegram_alert(f"🛑 Drawdown Alert: Trading paused. Current drawdown: {drawdown:.2%}")
            print(f"Drawdown exceeded {self.max_drawdown_percent:.2%}. Trading paused.")
        elif drawdown <= self.max_drawdown_percent and self.trading_paused and not self.volatility_guard():
            # Only resume if not paused by volatility guard
            self.trading_paused = False
            self.send_telegram_alert(f"✅ Drawdown Alert: Trading resumed. Current drawdown: {drawdown:.2%}")
            print("Drawdown recovered. Trading resumed.")
        return drawdown

    def position_tracker(self, open_positions):
        # This function would typically interact with the execution engine
        # to get current open positions and display them.
        if open_positions:
            print("\n--- Open Positions ---")
            for pos in open_positions:
                symbol = pos.get("symbol")
                side = pos.get("side")
                amount = pos.get("amount")
                entry_price = pos.get("entry_price")
                print(f"Symbol: {symbol}, Type: {side}, Amount: {amount}, Entry: {entry_price}")
            print("----------------------")
        else:
            print("No open positions.")

    def send_telegram_alert(self, message):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("Telegram bot token or chat ID not configured. Skipping Telegram alert.")
            return
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {"chat_id": self.telegram_chat_id, "text": message}
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")

    def log_trade(self, trade_details):
        self.trade_log.append(trade_details)

    def performance_logger(self):
        total_trades = len(self.trade_log)
        if total_trades == 0:
            return {"win_rate": 0, "total_pnl": 0, "max_drawdown": 0}

        winning_trades = [t for t in self.trade_log if t.get("pnl", 0) > 0]
        total_pnl = sum(t.get("pnl", 0) for t in self.trade_log)
        win_rate = len(winning_trades) / total_trades

        return {"win_rate": win_rate, "total_pnl": total_pnl, "max_drawdown": self.max_drawdown}

# Example Usage (for testing purposes)
# if __name__ == "__main__":
#     mock_config = {
#         "NEWS_API_KEY": "YOUR_NEWS_API_KEY",
#         "NEWS_API_URL": "https://api.example.com/news", # Replace with a real news API endpoint
#         "TELEGRAM_BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN",
#         "TELEGRAM_CHAT_ID": "YOUR_TELEGRAM_CHAT_ID",
#         "MAX_DRAWDOWN_PERCENT": 0.02
#     }
#     monitor = Monitoring(config=mock_config)

#     # Simulate news event
#     # print("\n--- Volatility Guard Test ---")
#     # monitor.volatility_guard()

#     # Simulate drawdown
#     print("\n--- Drawdown Monitor Test ---")
#     monitor.drawdown_monitor(-500) # Simulate a loss
#     monitor.drawdown_monitor(-100) # Another loss
#     monitor.drawdown_monitor(700) # A win

#     # Simulate trade logging
#     print("\n--- Performance Logger Test ---")
#     monitor.log_trade({"symbol": "EURUSD", "pnl": 100, "side": "buy"})
#     monitor.log_trade({"symbol": "GBPUSD", "pnl": -50, "side": "sell"})
#     monitor.log_trade({"symbol": "XAUUSD", "pnl": 200, "side": "buy"})

#     performance = monitor.performance_logger()
#     print(f"Win Rate: {performance["win_rate"]:.2%}")
#     print(f"Total PnL: {performance["total_pnl"]:.2f}")
#     print(f"Max Drawdown: {performance["max_drawdown"]:.2%}")

#     # Simulate open positions
#     print("\n--- Position Tracker Test ---")
#     mock_open_positions = [
#         {"symbol": "EURUSD", "side": "buy", "amount": 0.01, "entry_price": 1.0850},
#         {"symbol": "GBPUSD", "side": "sell", "amount": 0.02, "entry_price": 1.2700}
#     ]
#     monitor.position_tracker(mock_open_positions)


