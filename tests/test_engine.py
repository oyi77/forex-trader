#!/usr/bin/env python3
"""
Test script for the AI Trading Engine
This script tests all major components to ensure they work correctly.
"""

import sys
import os
import traceback
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from data.data_ingestion import DataIngestion
        from core.strategy_core import StrategyCore
        from signals.signal_generator import SignalGenerator
        from execution.execution_engine import ExecutionEngine
        from monitoring.monitoring import Monitoring
        from main import main
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_ingestion():
    """Test data ingestion module"""
    print("\nTesting data ingestion...")
    try:
        from data.data_ingestion import DataIngestion
        
        data_ingestion = DataIngestion(demo_mode=True)
        symbols = ["BTC/USDT", "ETH/USDT"]
        timeframes = ["1h", "30m"]
        
        market_data = data_ingestion.get_market_data(symbols, timeframes)
        
        for symbol in symbols:
            for tf in timeframes:
                df = market_data[symbol][tf]
                if not df.empty:
                    print(f"✅ {symbol} {tf} data: {len(df)} rows")
                else:
                    print(f"❌ {symbol} {tf} data is empty")
        
        return True
    except Exception as e:
        print(f"❌ Data ingestion error: {e}")
        traceback.print_exc()
        return False

def test_strategy_core():
    """Test strategy core module"""
    print("\nTesting strategy core...")
    try:
        import pandas as pd
        import numpy as np
        from core.strategy_core import StrategyCore
        
        # Create test data
        data = {
            'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='h')),
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 105,
            'low': np.random.rand(100) * 100 + 95,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.rand(100) * 1000
        }
        df = pd.DataFrame(data)
        
        strategy = StrategyCore()
        processed_df = strategy.apply_all_strategies(df.copy())
        
        # Check that indicators were added
        expected_indicators = ['EMA_Short', 'EMA_Long', 'RSI', 'ATR', 'Golden_Cross', 'Death_Cross']
        missing_indicators = [ind for ind in expected_indicators if ind not in processed_df.columns]
        
        if not missing_indicators:
            print("✅ All strategy indicators applied successfully")
            return True
        else:
            print(f"❌ Missing indicators: {missing_indicators}")
            return False
            
    except Exception as e:
        print(f"❌ Strategy core error: {e}")
        traceback.print_exc()
        return False

def test_signal_generator():
    """Test signal generator module"""
    print("\nTesting signal generator...")
    try:
        import pandas as pd
        import numpy as np
        from signals.signal_generator import SignalGenerator
        
        # Create test data with indicators
        data = {
            'timestamp': pd.to_datetime(pd.date_range(start='2023-01-01', periods=100, freq='h')),
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 105,
            'low': np.random.rand(100) * 100 + 95,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.rand(100) * 1000
        }
        df = pd.DataFrame(data)
        
        # Add required indicators
        df["Golden_Cross"] = False
        df["Death_Cross"] = False
        df["RSI"] = 50
        df["ATR"] = 2.0
        df["Bullish_OB"] = False
        df["Bearish_OB"] = False
        df["BOS_Bullish"] = False
        df["BOS_Bearish"] = False
        df["Bullish_Divergence"] = False
        df["Bearish_Divergence"] = False
        
        # Simulate a signal condition
        df.loc[99, "Golden_Cross"] = True
        df.loc[99, "Bullish_OB"] = True
        df.loc[99, "close"] = 150
        
        signal_gen = SignalGenerator()
        signal = signal_gen.generate_signal(df, "BTC/USDT", "1h")
        
        if signal and signal['signal_type'] != 'NONE':
            print(f"✅ Signal generated: {signal['signal_type']} {signal['symbol']}")
            print(f"   Confidence: {signal['confidence_score']}%")
            print(f"   Entry: {signal['entry_price']}, SL: {signal['stop_loss']}")
            return True
        else:
            print("❌ No signal generated")
            return False
            
    except Exception as e:
        print(f"❌ Signal generator error: {e}")
        traceback.print_exc()
        return False

def test_execution_engine():
    """Test execution engine module"""
    print("\nTesting execution engine...")
    try:
        from execution.execution_engine import ExecutionEngine
        
        exec_engine = ExecutionEngine(demo_mode=True)
        
        # Test order placement
        order_result = exec_engine.place_order("BTC/USDT", "market", "buy", 0.001)
        
        if order_result and order_result.get('status'):
            print(f"✅ Order placed successfully: {order_result['status']}")
            
            # Test balance
            balance = exec_engine.get_account_balance()
            if balance:
                print(f"✅ Account balance retrieved: {len(balance)} currencies")
            
            # Test positions
            positions = exec_engine.get_positions()
            print(f"✅ Positions retrieved: {len(positions)} positions")
            
            return True
        else:
            print("❌ Order placement failed")
            return False
            
    except Exception as e:
        print(f"❌ Execution engine error: {e}")
        traceback.print_exc()
        return False

def test_monitoring():
    """Test monitoring module"""
    print("\nTesting monitoring...")
    try:
        from monitoring.monitoring import Monitoring
        
        monitor = Monitoring()
        
        # Test trade logging
        monitor.log_trade({
            "symbol": "BTC/USDT",
            "side": "buy",
            "entry_price": 45000,
            "exit_price": 45100,
            "amount": 0.001,
            "pnl": 0.1
        })
        
        # Test performance calculation
        performance = monitor.performance_logger()
        
        if performance['total_trades'] > 0:
            print(f"✅ Trade logged and performance calculated")
            print(f"   Total trades: {performance['total_trades']}")
            print(f"   Win rate: {performance['win_rate']:.2%}")
            print(f"   Total PnL: {performance['total_pnl']:.2f}")
            return True
        else:
            print("❌ Performance calculation failed")
            return False
            
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
        traceback.print_exc()
        return False

def test_trading_engine():
    """Test the main trading engine"""
    print("\nTesting trading engine...")
    try:
        from main import main
        
        print(f"✅ Main function import successful")
        print(f"   Main function available for testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Trading engine error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 AI Trading Engine Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Imports", test_imports),
        ("Data Ingestion", test_data_ingestion),
        ("Strategy Core", test_strategy_core),
        ("Signal Generator", test_signal_generator),
        ("Execution Engine", test_execution_engine),
        ("Monitoring", test_monitoring),
        ("Trading Engine", test_trading_engine),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The trading engine is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 