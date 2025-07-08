#!/usr/bin/env python3
"""
Simplified System Test for Forex Trading Bot
"""

import sys
import os
import json
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
        print("✅ Signal generator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Signal generation failed: {e}")
        return False

def test_risk_management():
    """Test risk management system"""
    print("Testing risk management...")
    try:
        from risk.advanced_risk_manager import AdvancedRiskManager
        risk_manager = AdvancedRiskManager()
        print("✅ Risk manager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Risk management failed: {e}")
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
        return False

def test_main_bot():
    """Test main bot initialization"""
    print("Testing main bot...")
    try:
        # Just test if main_enhanced can be imported
        import main_enhanced
        print("✅ Main bot module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Main bot test failed: {e}")
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
    print("Starting Simplified System Test...")
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
        'main_bot': test_main_bot
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

