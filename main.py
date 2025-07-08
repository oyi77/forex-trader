import yaml
import time
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.data_ingestion import DataIngestion
from core.strategy_core import StrategyCore
from signals.signal_generator import SignalGenerator
from execution.execution_engine import ExecutionEngine
from execution.exness_execution import ExnessExecutionEngine
from monitoring.monitoring import Monitoring

# Import new modules
from backtest.backtester import Backtester
from backtest.reporting import BacktestReporter
from frontest.frontester import Frontester
from frontest.reporting import FrontestReporter

def load_config():
    """Load configuration from YAML file"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: config.yaml not found!")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        sys.exit(1)

def create_execution_engine(config):
    """Create appropriate execution engine based on configuration"""
    exchange = config.get('EXCHANGE', 'binance').lower()
    demo_mode = config.get('DEMO_MODE', True)
    
    if exchange == 'exness':
        print("Initializing Exness execution engine for forex trading...")
        return ExnessExecutionEngine(config=config, demo_mode=demo_mode)
    elif exchange == 'binance':
        print("Initializing Binance execution engine for crypto trading...")
        return ExecutionEngine(exchange_id='binance', config=config, demo_mode=demo_mode)
    elif exchange == 'oanda':
        print("Initializing OANDA execution engine for forex trading...")
        return ExecutionEngine(exchange_id='oanda', config=config, demo_mode=demo_mode)
    else:
        print(f"Unsupported exchange: {exchange}. Defaulting to Binance.")
        return ExecutionEngine(exchange_id='binance', config=config, demo_mode=demo_mode)

def run_live_trading():
    """Main trading engine function (original live trading)"""
    print("=== AI-Driven Trading Engine ===")
    print(f"Started at: {datetime.now()}")
    
    # Load configuration
    config = load_config()
    print(f"Configuration loaded. Exchange: {config.get('EXCHANGE', 'binance')}")
    print(f"Demo mode: {config.get('DEMO_MODE', True)}")
    
    try:
        # Initialize components
        print("\n1. Initializing data ingestion...")
        data_ingestion = DataIngestion(config)
        
        print("2. Initializing strategy core...")
        strategy_core = StrategyCore(config)
        
        print("3. Initializing signal generator...")
        signal_generator = SignalGenerator(config)
        
        print("4. Initializing execution engine...")
        execution_engine = create_execution_engine(config)
        
        print("5. Initializing monitoring...")
        monitoring = Monitoring(config)
        
        print("\n=== All components initialized successfully ===")
        
        # Main trading loop
        cycle_count = 0
        max_cycles = config.get('MAX_CYCLES', 10)  # Default to 10 cycles for safety
        
        while cycle_count < max_cycles:
            cycle_count += 1
            print(f"\n--- Trading Cycle {cycle_count} ---")
            print(f"Time: {datetime.now()}")
            
            try:
                # 1. Fetch market data
                print("Fetching market data...")
                symbols = config.get('FOREX_SYMBOLS', ['EURUSD', 'GBPUSD']) if config.get('EXCHANGE') == 'exness' else ['BTC/USDT', 'ETH/USDT']
                timeframes = config.get('DEFAULT_TIMEFRAMES', ['1h', '30m'])
                
                market_data = {}
                for symbol in symbols[:3]:  # Limit to 3 symbols for demo
                    for timeframe in timeframes:
                        data = data_ingestion.get_historical_data(symbol, timeframe, limit=100)
                        if data is not None and not data.empty:
                            market_data[f"{symbol}_{timeframe}"] = data
                
                if not market_data:
                    print("No market data available. Skipping cycle.")
                    time.sleep(60)
                    continue
                
                # 2. Generate trading signals
                print("Generating trading signals...")
                signals = []
                for key, data in market_data.items():
                    symbol, timeframe = key.split('_', 1)
                    signal = signal_generator.generate_signal(data, symbol, timeframe)
                    if signal and signal.get('confidence', 0) >= config.get('MIN_CONFIDENCE', 70):
                        signals.append(signal)
                
                print(f"Generated {len(signals)} signals with sufficient confidence")
                
                # 3. Execute trades
                if signals:
                    print("Executing trades...")
                    for signal in signals:
                        symbol = signal['symbol']
                        side = signal['side']
                        confidence = signal['confidence']
                        
                        # Calculate position size based on risk management
                        balance = execution_engine.get_account_balance()
                        if balance:
                            if config.get('EXCHANGE') == 'exness':
                                equity = balance.get('equity', 10000)
                                lot_size = config.get('FOREX_LOT_SIZE', 0.01)
                            else:
                                equity = balance.get('USDT', {}).get('total', 10000)
                                lot_size = 0.001  # Default crypto amount
                            
                            risk_amount = equity * config.get('RISK_PER_TRADE', 0.01)
                            
                            # Place order
                            order_result = execution_engine.place_order(
                                symbol=symbol,
                                order_type='market',
                                side=side,
                                amount=lot_size,
                                sl=signal.get('stop_loss'),
                                tp=signal.get('take_profit')
                            )
                            
                            if order_result:
                                print(f"Order placed: {symbol} {side} {lot_size}")
                                monitoring.log_trade(signal, order_result, 'executed')
                            else:
                                print(f"Failed to place order for {symbol}")
                
                # 4. Monitor and manage positions
                print("Monitoring positions...")
                positions = execution_engine.get_positions()
                if positions:
                    print(f"Current positions: {len(positions)}")
                    for position in positions:
                        monitoring.log_position_update(position)
                
                # 5. Check risk management
                print("Checking risk management...")
                risk_status = monitoring.check_risk_limits()
                if not risk_status['can_trade']:
                    print(f"Risk limits exceeded: {risk_status['reason']}")
                    break
                
                # 6. Log performance
                print("Logging performance...")
                performance = monitoring.get_performance_summary()
                print(f"Performance: {performance}")
                
                # Wait before next cycle
                wait_time = config.get('CYCLE_INTERVAL', 300)  # 5 minutes default
                print(f"Waiting {wait_time} seconds before next cycle...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\nTrading stopped by user.")
                break
            except Exception as e:
                print(f"Error in trading cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        print(f"\nTrading completed. Total cycles: {cycle_count}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # Cleanup
        if 'execution_engine' in locals():
            if hasattr(execution_engine, 'shutdown'):
                execution_engine.shutdown()
        print("Trading engine shutdown complete.")

def run_backtest():
    print("\n=== Backtest Mode ===")
    config = load_config()
    # Example: Use the same strategy and data loader as live trading
    strategy = StrategyCore(config)
    data_loader = DataIngestion(config)
    # You may want to implement a more advanced execution simulator for backtest
    execution_simulator = None  # Placeholder
    reporter = BacktestReporter()
    backtester = Backtester(strategy, data_loader, execution_simulator, reporter)
    results = backtester.run(config)
    # Save report (stub)
    reporter.generate_html_report(results, 'backtest_report.html')
    print("Backtest completed. Report saved as backtest_report.html")

def run_frontest():
    print("\n=== Frontest (Paper Trading) Mode ===")
    config = load_config()
    strategy = StrategyCore(config)
    data_source = DataIngestion(config)  # Or a live data source
    execution_simulator = None  # Placeholder
    reporter = FrontestReporter()
    frontester = Frontester(strategy, data_source, execution_simulator, reporter)
    results = frontester.run(config)
    # Save report (stub)
    reporter.generate_html_report(results, 'frontest_report.html')
    print("Frontest completed. Report saved as frontest_report.html")

def main_menu():
    while True:
        print("\n=== Trading Engine Menu ===")
        print("1. Run Live Trading")
        print("2. Run Backtest")
        print("3. Run Frontest (Paper Trading)")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()
        if choice == '1':
            run_live_trading()
        elif choice == '2':
            run_backtest()
        elif choice == '3':
            run_frontest()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()


