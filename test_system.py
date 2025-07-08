#!/usr/bin/env python3
"""
Comprehensive System Test for Forex Trading Bot
Tests all major components and generates a test report
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        import ta
        import sklearn
        import yaml
        import scipy
        import matplotlib
        import plotly
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("Testing configuration loading...")
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_signal_generation():
    """Test signal generation"""
    print("Testing signal generation...")
    try:
        from signals.enhanced_signal_generator import EnhancedSignalGenerator
        generator = EnhancedSignalGenerator()
        # Test with sample data
        import pandas as pd
        import numpy as np
        
        # Create sample OHLC data
        dates = pd.date_range('2025-01-01', periods=100, freq='H')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'open': 1.1000 + np.random.randn(100) * 0.001,
            'high': 1.1005 + np.random.randn(100) * 0.001,
            'low': 1.0995 + np.random.randn(100) * 0.001,
            'close': 1.1000 + np.random.randn(100) * 0.001,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # Test signal generation (using available method)
        signal = generator.generate_signals('EURUSD', sample_data)
        print(f"✅ Signal generation successful: {signal}")
        return True
    except Exception as e:
        print(f"❌ Signal generation failed: {e}")
        traceback.print_exc()
        return False

def test_risk_management():
    """Test risk management system"""
    print("Testing risk management...")
    try:
        from risk.advanced_risk_manager import AdvancedRiskManager
        risk_manager = AdvancedRiskManager()
        
        # Test risk calculation (using available method)
        portfolio_value = 10000
        positions = [
            {'symbol': 'EURUSD', 'size': 0.1, 'entry_price': 1.1000, 'current_price': 1.1050},
            {'symbol': 'GBPUSD', 'size': 0.05, 'entry_price': 1.2500, 'current_price': 1.2480}
        ]
        
        risk_metrics = risk_manager.calculate_risk_metrics(positions, portfolio_value)
        print(f"✅ Risk management successful: Risk Score = {risk_metrics.get('risk_score', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Risk management failed: {e}")
        traceback.print_exc()
        return False

def test_backtesting():
    """Test backtesting engine"""
    print("Testing backtesting engine...")
    try:
        from backtesting.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        print("✅ Backtesting engine initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Backtesting failed: {e}")
        traceback.print_exc()
        return False

def test_data_providers():
    """Test data provider connections"""
    print("Testing data providers...")
    try:
        from data.data_providers import DataProviderManager
        manager = DataProviderManager()
        print("✅ Data provider manager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Data provider test failed: {e}")
        traceback.print_exc()
        return False

def test_portfolio_optimization():
    """Test portfolio optimization"""
    print("Testing portfolio optimization...")
    try:
        from portfolio.portfolio_optimizer import PortfolioOptimizer
        optimizer = PortfolioOptimizer()
        print("✅ Portfolio optimizer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Portfolio optimization failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_backend():
    """Test dashboard backend"""
    print("Testing dashboard backend...")
    try:
        # Check if Flask app can be imported
        sys.path.append('trading_dashboard/src')
        from main import app
        print("✅ Dashboard backend loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Dashboard backend test failed: {e}")
        traceback.print_exc()
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    report = {
        'test_timestamp': datetime.now().isoformat(),
        'total_tests': len(results),
        'passed_tests': sum(results.values()),
        'failed_tests': len(results) - sum(results.values()),
        'success_rate': (sum(results.values()) / len(results)) * 100,
        'test_results': results
    }
    
    # Save report to file
    with open('test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("SYSTEM TEST REPORT")
    print("="*60)
    print(f"Test Timestamp: {report['test_timestamp']}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed_tests']}")
    print(f"Failed: {report['failed_tests']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print("\nDetailed Results:")
    print("-"*40)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print("\n" + "="*60)
    
    if report['success_rate'] >= 80:
        print("🎉 SYSTEM TEST PASSED - Ready for deployment!")
    else:
        print("⚠️  SYSTEM TEST FAILED - Please fix issues before deployment")
    
    return report

def main():
    """Run all system tests"""
    print("Starting Comprehensive System Test...")
    print("="*60)
    
    # Define all tests
    tests = {
        'imports': test_imports,
        'config_loading': test_config_loading,
        'signal_generation': test_signal_generation,
        'risk_management': test_risk_management,
        'backtesting': test_backtesting,
        'data_providers': test_data_providers,
        'portfolio_optimization': test_portfolio_optimization,
        'dashboard_backend': test_dashboard_backend
    }
    
    # Run all tests
    results = {}
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
        print()  # Add spacing between tests
    
    # Generate and display report
    report = generate_test_report(results)
    
    return report['success_rate'] >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
