#!/usr/bin/env python3
"""
Demo script for Exness forex trading engine
This script demonstrates the forex trading capabilities with Exness integration
"""

import yaml
import time
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_ingestion import DataIngestion
from core.strategy_core import StrategyCore
from signals.signal_generator import SignalGenerator
from execution.exness_execution import ExnessExecutionEngine
from monitoring.monitoring import Monitoring

def load_config():
    """Load configuration from YAML file"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: config.yaml not found!")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        sys.exit(1)

def demo_exness_trading():
    """Demonstrate Exness forex trading functionality"""
    print("=== Exness Forex Trading Demo ===")
    print(f"Started at: {datetime.now()}")
    
    # Load configuration
    config = load_config()
    print(f"Configuration loaded. Exchange: {config.get('EXCHANGE', 'exness')}")
    print(f"Demo mode: {config.get('DEMO_MODE', True)}")
    
    try:
        # Initialize components
        print("\n1. Initializing data ingestion...")
        data_ingestion = DataIngestion(config)
        
        print("2. Initializing strategy core...")
        strategy_core = StrategyCore(config)
        
        print("3. Initializing signal generator...")
        signal_generator = SignalGenerator(config)
        
        print("4. Initializing Exness execution engine...")
        execution_engine = ExnessExecutionEngine(config=config, demo_mode=True)
        
        print("5. Initializing monitoring...")
        monitoring = Monitoring(config)
        
        print("\n=== All components initialized successfully ===")
        
        # Get supported forex symbols
        forex_symbols = config.get('FOREX_SYMBOLS', ['EURUSD', 'GBPUSD', 'USDJPY'])
        timeframes = config.get('DEFAULT_TIMEFRAMES', ['1h', '30m'])
        
        print(f"\nSupported forex symbols: {forex_symbols}")
        print(f"Timeframes: {timeframes}")
        
        # Demo trading loop
        cycle_count = 0
        max_cycles = 3  # Run 3 cycles for demo
        
        while cycle_count < max_cycles:
            cycle_count += 1
            print(f"\n--- Demo Trading Cycle {cycle_count} ---")
            print(f"Time: {datetime.now()}")
            
            try:
                # 1. Fetch forex market data
                print("Fetching forex market data...")
                market_data = {}
                for symbol in forex_symbols[:2]:  # Test with 2 symbols
                    for timeframe in timeframes:
                        data = data_ingestion.get_forex_data(symbol, timeframe, limit=50)
                        if data is not None and not data.empty:
                            market_data[f"{symbol}_{timeframe}"] = data
                            print(f"  ✓ {symbol} {timeframe}: {len(data)} candles")
                
                if not market_data:
                    print("No market data available. Skipping cycle.")
                    time.sleep(10)
                    continue
                
                # 2. Generate forex trading signals
                print("Generating forex trading signals...")
                signals = []
                for key, data in market_data.items():
                    symbol, timeframe = key.split('_', 1)
                    # Apply strategy indicators first
                    processed_data = strategy_core.apply_all_strategies(data.copy())
                    signal = signal_generator.generate_signal(processed_data, symbol, timeframe)
                    if signal and signal.get('signal_type') != 'NONE' and signal.get('confidence_score', 0) >= config.get('MIN_CONFIDENCE', 70):
                        signals.append(signal)
                        print(f"  ✓ Signal generated for {symbol}: {signal['signal_type']} (confidence: {signal['confidence_score']}%)")
                
                print(f"Generated {len(signals)} signals with sufficient confidence")
                
                # 3. Execute forex trades
                if signals:
                    print("Executing forex trades...")
                    for signal in signals:
                        symbol = signal['symbol']
                        side = signal['signal_type'].lower()  # Convert BUY/SELL to buy/sell
                        confidence = signal['confidence_score']
                        
                        # Get account balance
                        balance = execution_engine.get_account_balance()
                        print(f"  Account balance: {balance}")
                        
                        # Calculate position size for forex
                        lot_size = config.get('FOREX_LOT_SIZE', 0.01)  # 0.01 lot = 1000 units
                        
                        # Place forex order
                        order_result = execution_engine.place_order(
                            symbol=symbol,
                            order_type='market',
                            side=side,
                            amount=lot_size,
                            sl=signal.get('stop_loss'),
                            tp=signal.get('take_profit')
                        )
                        
                        if order_result:
                            print(f"  ✓ Order placed: {symbol} {side} {lot_size} lot")
                            print(f"    Entry: {order_result.get('price_open', 'N/A')}")
                            print(f"    SL: {order_result.get('sl', 'N/A')}")
                            print(f"    TP: {order_result.get('tp', 'N/A')}")
                            # Log the trade with proper format
                            trade_details = {
                                'symbol': symbol,
                                'side': side,
                                'entry_price': order_result.get('price_open', 0),
                                'amount': lot_size,
                                'pnl': 0,  # Will be calculated when position is closed
                                'timestamp': datetime.now().isoformat()
                            }
                            monitoring.log_trade(trade_details)
                        else:
                            print(f"  ✗ Failed to place order for {symbol}")
                
                # 4. Monitor forex positions
                print("Monitoring forex positions...")
                positions = execution_engine.get_positions()
                if positions:
                    print(f"Current positions: {len(positions)}")
                    for symbol, pos_list in positions.items():
                        for pos in pos_list:
                            print(f"  {symbol}: {pos['side']} {pos['volume']} lot at {pos['price_open']}")
                            monitoring.log_position_update(pos)
                else:
                    print("  No open positions")
                
                # 5. Get current forex prices
                print("Current forex prices:")
                for symbol in forex_symbols[:3]:
                    ticker = execution_engine.get_ticker(symbol)
                    if ticker:
                        print(f"  {symbol}: Bid {ticker['bid']:.5f} | Ask {ticker['ask']:.5f}")
                
                # 6. Check risk management
                print("Checking risk management...")
                risk_status = monitoring.check_risk_limits()
                print(f"  Risk status: {risk_status}")
                
                # 7. Log performance
                print("Logging performance...")
                performance = monitoring.get_performance_summary()
                print(f"  Performance: {performance}")
                
                # Wait before next cycle
                wait_time = 30  # 30 seconds for demo
                print(f"Waiting {wait_time} seconds before next cycle...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\nDemo stopped by user.")
                break
            except Exception as e:
                print(f"Error in demo cycle: {e}")
                time.sleep(10)
        
        print(f"\nDemo completed. Total cycles: {cycle_count}")
        
        # Final summary
        print("\n=== Final Demo Summary ===")
        final_performance = monitoring.get_performance_summary()
        print(f"Total trades: {final_performance.get('total_trades', 0)}")
        print(f"Win rate: {final_performance.get('win_rate', 0):.2%}")
        print(f"Total PnL: {final_performance.get('total_pnl', 0):.2f}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # Cleanup
        if 'execution_engine' in locals():
            execution_engine.shutdown()
        print("Demo shutdown complete.")

def test_forex_data():
    """Test forex data ingestion"""
    print("\n=== Testing Forex Data Ingestion ===")
    
    config = load_config()
    data_ingestion = DataIngestion(config)
    
    forex_symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
    
    for symbol in forex_symbols:
        print(f"\nTesting {symbol}:")
        
        # Test different timeframes
        for timeframe in ['1h', '30m']:
            data = data_ingestion.get_forex_data(symbol, timeframe, limit=20)
            if data is not None and not data.empty:
                print(f"  {timeframe}: {len(data)} candles, latest close: {data['close'].iloc[-1]:.5f}")
            else:
                print(f"  {timeframe}: No data")
        
        # Test current price
        current_price = data_ingestion.get_current_price(symbol)
        print(f"  Current price: {current_price:.5f}")

def test_exness_execution():
    """Test Exness execution engine"""
    print("\n=== Testing Exness Execution Engine ===")
    
    config = load_config()
    execution_engine = ExnessExecutionEngine(config=config, demo_mode=True)
    
    # Test account balance
    balance = execution_engine.get_account_balance()
    print(f"Account balance: {balance}")
    
    # Test symbol info
    for symbol in ['EURUSD', 'GBPUSD']:
        info = execution_engine.get_symbol_info(symbol)
        print(f"{symbol} info: {info}")
    
    # Test ticker
    for symbol in ['EURUSD', 'GBPUSD']:
        ticker = execution_engine.get_ticker(symbol)
        print(f"{symbol} ticker: {ticker}")
    
    # Test order placement
    order_result = execution_engine.place_order(
        symbol='EURUSD',
        order_type='market',
        side='buy',
        amount=0.01,
        sl=1.0800,
        tp=1.0900
    )
    print(f"Demo order result: {order_result}")
    
    # Test position management
    positions = execution_engine.get_positions()
    print(f"Positions: {positions}")
    
    execution_engine.shutdown()

if __name__ == "__main__":
    print("Exness Forex Trading Demo")
    print("1. Test forex data ingestion")
    print("2. Test Exness execution engine")
    print("3. Run full demo trading cycle")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        test_forex_data()
    elif choice == '2':
        test_exness_execution()
    elif choice == '3':
        demo_exness_trading()
    else:
        print("Invalid choice. Running full demo...")
        demo_exness_trading() 