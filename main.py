import yaml
import time
from datetime import datetime

from data.data_ingestion import DataIngestion
from core.strategy_core import StrategyCore
from signals.signal_generator import SignalGenerator
from execution.execution_engine import ExecutionEngine
from monitoring.monitoring import Monitoring

class TradingEngine:
    def __init__(self, config_path='config.yaml', demo_mode=True):
        self.config = self._load_config(config_path)
        self.demo_mode = demo_mode

        self.data_ingestion = DataIngestion(exchange_id='binance', config=self.config, demo_mode=self.demo_mode)
        self.strategy_core = StrategyCore()
        self.signal_generator = SignalGenerator()
        self.execution_engine = ExecutionEngine(exchange_id='binance', config=self.config, demo_mode=self.demo_mode)
        self.monitoring = Monitoring(config=self.config)

        self.supported_symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'LTC/USDT', 'BCH/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'SOL/USDT', 'BNB/USDT'] # Example symbols
        self.timeframes = self.config.get('DEFAULT_TIMEFRAMES', ['1h', '30m'])

    def _load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def scan_all_pairs(self):
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scanning all pairs for setups...")
        top_setups = []
        for symbol in self.supported_symbols:
            market_data = self.data_ingestion.scan_market_data([symbol], self.timeframes)
            for tf in self.timeframes:
                df = market_data[symbol][tf]
                if not df.empty:
                    processed_df = self.strategy_core.apply_all_strategies(df.copy())
                    signal = self.signal_generator.generate_signal(processed_df, symbol, tf)
                    if signal and signal['signal_type'] != 'NONE':
                        top_setups.append(signal)
        
        # Sort by confidence score and return top 3
        top_setups.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        print("\n--- Top 3 Setups ---")
        if not top_setups:
            print("No setups found.")
        for i, setup in enumerate(top_setups[:3]):
            print(f"Setup {i+1}: {setup['emoji']} {setup['signal_type']} {setup['symbol']} ({setup['timeframe']}) - Confidence: {setup['confidence_score']}%\n  Entry: {setup['entry_price']}, SL: {setup['stop_loss']}, TP1: {setup['take_profit'][0]}\n  RR: {setup['risk_reward_ratio']}, Expiry: {setup['expiry_time_hours']}h\n  Alert: {setup['alert_message']} {setup['status_tag']}")
        print("--------------------")
        return top_setups[:3]

    def execute_trade_from_signal(self, signal):
        if self.monitoring.trading_paused:
            print(f"Trading is paused. Cannot execute {signal['signal_type']} for {signal['symbol']}.")
            return

        symbol = signal['symbol']
        side = signal['signal_type'].lower()
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        take_profit = signal['take_profit'][0] # Use TP1 for initial order

        # Calculate amount based on risk per trade and stop loss
        # This is a simplified calculation and needs proper position sizing logic
        risk_per_trade_usd = self.monitoring.current_equity * self.config.get('RISK_PER_TRADE', 0.01)
        if side == 'buy':
            price_diff = entry_price - stop_loss
        else:
            price_diff = stop_loss - entry_price
        
        if price_diff <= 0:
            print(f"Invalid SL for {symbol}. Cannot calculate position size.")
            return

        # Assuming 1 unit of base currency (e.g., BTC) is worth entry_price USDT
        # This needs to be adjusted for different symbols and exchanges
        amount = risk_per_trade_usd / price_diff / entry_price # Approximate amount
        amount = round(amount, 5) # Round to appropriate decimal places

        print(f"Attempting to place {side} order for {amount} {symbol} at {entry_price} with SL {stop_loss} and TP {take_profit}")
        order_result = self.execution_engine.place_order(symbol, 'limit', side, amount, entry_price, params={'stopLossPrice': stop_loss, 'takeProfitPrice': take_profit})
        
        if order_result and order_result.get('status') == 'closed': # Assuming market orders close immediately in demo
            pnl = (order_result['price'] - entry_price) * amount if side == 'buy' else (entry_price - order_result['price']) * amount
            self.monitoring.log_trade({
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'exit_price': order_result['price'],
                'pnl': pnl,
                'timestamp': datetime.now().isoformat()
            })
            self.monitoring.drawdown_monitor(pnl)
            print(f"Trade executed for {symbol}. PnL: {pnl:.2f}")
        elif order_result:
            print(f"Order for {symbol} placed, status: {order_result.get('status')}")
        else:
            print(f"Failed to place order for {symbol}.")

    def summarize_trades(self):
        print("\n--- Trade Performance Summary ---")
        performance = self.monitoring.performance_logger()
        print(f"Total Trades: {len(self.monitoring.trade_log)}")
        print(f"Win Rate: {performance['win_rate']:.2%}")
        print(f"Total PnL: {performance['total_pnl']:.2f}")
        print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
        print("\n--- Full Trade Log ---")
        if not self.monitoring.trade_log:
            print("No trades logged yet.")
        for trade in self.monitoring.trade_log:
            print(f"Symbol: {trade['symbol']}, Side: {trade['side']}, Entry: {trade['entry_price']}, Exit: {trade.get('exit_price', 'N/A')}, PnL: {trade['pnl']:.2f}")
        print("------------------------")

    def run(self, interval_minutes=60):
        print("Starting trading engine...")
        while True:
            self.monitoring.volatility_guard()
            if not self.monitoring.trading_paused:
                setups = self.scan_all_pairs()
                for signal in setups:
                    self.execute_trade_from_signal(signal)
            else:
                print("Trading paused by monitoring system.")
            
            self.monitoring.position_tracker(self.execution_engine.get_open_orders())
            self.summarize_trades()
            
            print(f"Waiting for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    # To run in demo mode (no real trades, just simulations):
    engine = TradingEngine(demo_mode=True)
    # To run with real trading (requires API keys in config.yaml and demo_mode=False):
    # engine = TradingEngine(demo_mode=False)
    engine.run(interval_minutes=1) # Scan every 1 minute for testing


