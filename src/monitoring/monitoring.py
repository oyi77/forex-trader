import pandas as pd
import requests
import time
import json
from datetime import datetime, timedelta

class Monitoring:
    def __init__(self, config=None):
        self.config = config if config else {}
        self.news_api_key = self.config.get("FMP_API_KEY")  # <-- NEW: FMP API key
        self.news_api_url = self.config.get("NEWS_API_URL", "https://financialmodelingprep.com/api/v3/economic_calendar")
        self.telegram_bot_token = self.config.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = self.config.get("TELEGRAM_CHAT_ID")
        self.trading_paused = False
        self.max_drawdown_percent = self.config.get("MAX_DRAWDOWN_PERCENT", 0.05)
        self.initial_equity = 10000  # Placeholder, should be dynamic
        self.current_equity = self.initial_equity
        self.peak_equity = self.initial_equity
        self.max_drawdown = 0
        self.trade_log = []
        self.daily_pnl = {}
        self.risk_metrics = {
            'max_consecutive_losses': 0,
            'current_consecutive_losses': 0,
            'largest_win': 0,
            'largest_loss': 0,
            'avg_win': 0,
            'avg_loss': 0
        }

    def fetch_news_calendar(self):
        """
        Fetch high-impact economic events using Financial Modeling Prep's free API.
        Requires FMP_API_KEY in config.yaml. See: https://financialmodelingprep.com/developer/docs/economic-calendar-api
        Returns a list of high-impact events in the next 24 hours.
        """
        if not self.news_api_key:
            print("FMP_API_KEY not set in config. Skipping news check.")
            return []
        try:
            now = datetime.utcnow()
            from_date = now.strftime('%Y-%m-%d')
            to_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
            url = f"{self.news_api_url}?from={from_date}&to={to_date}&apikey={self.news_api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            events = response.json()
            # FMP returns a list of events, each with 'event', 'date', 'country', 'impact', etc.
            # Filter for high-impact events in the next 24 hours
            high_impact = []
            for event in events:
                # Impact can be 'High', 'Medium', 'Low' (case-insensitive)
                if str(event.get('impact', '')).lower() == 'high':
                    # Parse event time
                    event_time = pd.to_datetime(event.get('date'))
                    if now <= event_time <= now + timedelta(days=1):
                        high_impact.append(event)
            return high_impact
        except Exception as e:
            print(f"Error fetching news calendar: {e}")
            return []

    def volatility_guard(self):
        """Monitor for high-impact news and pause trading if necessary"""
        news_events = self.fetch_news_calendar()
        current_time = pd.Timestamp.now()
        
        for event in news_events:
            event_time = pd.to_datetime(event.get("time"))  # Assuming "time" field exists
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
        """Monitor drawdown and pause trading if threshold exceeded"""
        self.current_equity += current_pnl  # Update equity with latest PnL
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
        """Track and display open positions"""
        if open_positions:
            print("\n--- Open Positions ---")
            total_exposure = 0
            
            for pos in open_positions:
                symbol = pos.get("symbol")
                side = pos.get("side")
                amount = pos.get("amount")
                entry_price = pos.get("entry_price")
                current_price = pos.get("current_price", entry_price)
                
                # Calculate unrealized PnL
                if side == "buy":
                    unrealized_pnl = (current_price - entry_price) * amount
                else:
                    unrealized_pnl = (entry_price - current_price) * amount
                
                total_exposure += abs(amount * entry_price)
                
                print(f"Symbol: {symbol}, Type: {side}, Amount: {amount}, Entry: {entry_price}, Current: {current_price}, PnL: {unrealized_pnl:.2f}")
            
            print(f"Total Exposure: {total_exposure:.2f}")
            print("----------------------")
        else:
            print("No open positions.")

    def send_telegram_alert(self, message):
        """Send alert via Telegram"""
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("Telegram bot token or chat ID not configured. Skipping Telegram alert.")
            return
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {"chat_id": self.telegram_chat_id, "text": message}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")

    def log_trade(self, trade_details):
        """Log trade details and update metrics"""
        trade_details['timestamp'] = datetime.now().isoformat()
        self.trade_log.append(trade_details)
        
        # Update daily PnL
        date_key = datetime.now().strftime('%Y-%m-%d')
        if date_key not in self.daily_pnl:
            self.daily_pnl[date_key] = 0
        self.daily_pnl[date_key] += trade_details.get('pnl', 0)
        
        # Update risk metrics
        pnl = trade_details.get('pnl', 0)
        if pnl > 0:
            self.risk_metrics['largest_win'] = max(self.risk_metrics['largest_win'], pnl)
            self.risk_metrics['current_consecutive_losses'] = 0
        else:
            self.risk_metrics['largest_loss'] = min(self.risk_metrics['largest_loss'], pnl)
            self.risk_metrics['current_consecutive_losses'] += 1
            self.risk_metrics['max_consecutive_losses'] = max(
                self.risk_metrics['max_consecutive_losses'], 
                self.risk_metrics['current_consecutive_losses']
            )

    def performance_logger(self):
        """Calculate and return performance metrics"""
        total_trades = len(self.trade_log)
        if total_trades == 0:
            return {
                "win_rate": 0, 
                "total_pnl": 0, 
                "max_drawdown": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "profit_factor": 0,
                "sharpe_ratio": 0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0
            }

        winning_trades = [t for t in self.trade_log if t.get("pnl", 0) > 0]
        losing_trades = [t for t in self.trade_log if t.get("pnl", 0) < 0]
        
        total_pnl = sum(t.get("pnl", 0) for t in self.trade_log)
        win_rate = len(winning_trades) / total_trades
        
        # Calculate average win and loss
        avg_win = sum(t.get("pnl", 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.get("pnl", 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Calculate profit factor
        gross_profit = sum(t.get("pnl", 0) for t in winning_trades)
        gross_loss = abs(sum(t.get("pnl", 0) for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate Sharpe ratio (simplified)
        returns = [t.get("pnl", 0) for t in self.trade_log]
        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0

        return {
            "win_rate": win_rate, 
            "total_pnl": total_pnl, 
            "max_drawdown": self.max_drawdown,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades)
        }

    def get_performance_summary(self):
        """Alias for performance_logger for compatibility"""
        return self.performance_logger()

    def save_trade_log(self, filename="trade_log.json"):
        """Save trade log to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.trade_log, f, indent=2, default=str)
            print(f"Trade log saved to {filename}")
        except Exception as e:
            print(f"Error saving trade log: {e}")

    def load_trade_log(self, filename="trade_log.json"):
        """Load trade log from file"""
        try:
            with open(filename, 'r') as f:
                self.trade_log = json.load(f)
            print(f"Trade log loaded from {filename}")
        except Exception as e:
            print(f"Error loading trade log: {e}")

    def get_daily_summary(self, date=None):
        """Get daily trading summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        daily_trades = [t for t in self.trade_log if t.get('timestamp', '').startswith(date)]
        daily_pnl = sum(t.get('pnl', 0) for t in daily_trades)
        
        return {
            'date': date,
            'trades': len(daily_trades),
            'pnl': daily_pnl,
            'trades_list': daily_trades
        }

    def check_risk_limits(self):
        """Check if any risk limits are exceeded"""
        performance = self.performance_logger()
        
        # Check consecutive losses
        if self.risk_metrics['current_consecutive_losses'] >= 5:
            self.trading_paused = True
            self.send_telegram_alert("🛑 Risk Alert: 5 consecutive losses reached. Trading paused.")
            return True
        
        # Check win rate (only if we have enough trades)
        total_trades = performance.get('total_trades', 0)
        if total_trades >= 10 and performance.get('win_rate', 0) < 0.3:
            self.trading_paused = True
            self.send_telegram_alert("🛑 Risk Alert: Win rate below 30%. Trading paused.")
            return True
        
        return False

# Example Usage (for testing purposes)
if __name__ == "__main__":
    mock_config = {
        "FMP_API_KEY": "YOUR_FMP_API_KEY", # <-- NEW: FMP API key
        "NEWS_API_URL": "https://api.example.com/news",  # Replace with a real news API endpoint
        "TELEGRAM_BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID": "YOUR_TELEGRAM_CHAT_ID",
        "MAX_DRAWDOWN_PERCENT": 0.02
    }
    monitor = Monitoring(config=mock_config)

    # Simulate drawdown
    print("\n--- Drawdown Monitor Test ---")
    monitor.drawdown_monitor(-500)  # Simulate a loss
    monitor.drawdown_monitor(-100)  # Another loss
    monitor.drawdown_monitor(700)   # A win

    # Simulate trade logging
    print("\n--- Performance Logger Test ---")
    monitor.log_trade({"symbol": "EURUSD", "pnl": 100, "side": "buy"})
    monitor.log_trade({"symbol": "GBPUSD", "pnl": -50, "side": "sell"})
    monitor.log_trade({"symbol": "XAUUSD", "pnl": 200, "side": "buy"})

    performance = monitor.performance_logger()
    print(f"Win Rate: {performance['win_rate']:.2%}")
    print(f"Total PnL: {performance['total_pnl']:.2f}")
    print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
    print(f"Profit Factor: {performance['profit_factor']:.2f}")
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")

    # Simulate open positions
    print("\n--- Position Tracker Test ---")
    mock_open_positions = [
        {"symbol": "EURUSD", "side": "buy", "amount": 0.01, "entry_price": 1.0850, "current_price": 1.0870},
        {"symbol": "GBPUSD", "side": "sell", "amount": 0.02, "entry_price": 1.2700, "current_price": 1.2680}
    ]
    monitor.position_tracker(mock_open_positions)


