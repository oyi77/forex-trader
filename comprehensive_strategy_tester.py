#!/usr/bin/env python3
"""
Comprehensive Strategy Testing Framework
Tests strategies across 3 years of data to find combinations that achieve 199,900% returns
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import itertools
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.three_year_data_collector import ThreeYearDataCollector
from src.config.configuration_manager import ConfigurationManager
from src.factories.strategy_factory import ExtremeStrategyFactory
from src.backtest.enhanced_backtester import BacktestConfig, EnhancedBacktester


class ComprehensiveStrategyTester:
    """
    Tests strategies across 3 years of data to find winning combinations
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        
        # Load 3-year data
        self.data_collector = ThreeYearDataCollector()
        self.historical_data = self.data_collector.load_existing_data()
        
        if not self.historical_data:
            self.logger.error("No 3-year data found. Run data collection first.")
            sys.exit(1)
        
        self.logger.info(f"Loaded 3-year data for {len(self.historical_data)} symbols")
        
        # Target parameters
        self.target_return = 199900  # 199,900%
        self.initial_balance = 1_000_000
        self.target_balance = 2_000_000_000
        self.test_period_days = 14  # 2 weeks
        
        # Strategy combinations to test
        self.god_strategies = [
            'GOD_MODE_SCALPING',
            'MARTINGALE_GOD', 
            'VOLATILITY_GOD',
            'TREND_GOD',
            'ALL_IN_GOD'
        ]
        
        # Parameter ranges for optimization
        self.parameter_ranges = {
            'leverage': [500, 1000, 1500, 2000],
            'max_risk_per_trade': [0.30, 0.50, 0.70, 0.85, 0.95],
            'max_positions': [3, 5, 8, 10, 15],
            'max_daily_loss': [0.60, 0.70, 0.80, 0.90, 0.95],
            'max_drawdown': [0.70, 0.80, 0.90, 0.95, 0.99]
        }
        
        # Results tracking
        self.best_results = []
        self.test_count = 0
        self.successful_configs = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('comprehensive_test.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_all_2week_periods(self) -> List[Tuple[datetime, datetime]]:
        """Get all possible 2-week periods from 3-year data"""
        periods = []
        
        # Find the common date range across all symbols
        start_dates = []
        end_dates = []
        
        for symbol, data in self.historical_data.items():
            if not data.empty:
                start_dates.append(data.index.min())
                end_dates.append(data.index.max())
        
        if not start_dates:
            return periods
        
        common_start = max(start_dates)
        common_end = min(end_dates)
        
        self.logger.info(f"Common data range: {common_start.date()} to {common_end.date()}")
        
        # Generate all 2-week periods
        current_start = common_start
        
        while current_start + timedelta(days=self.test_period_days) <= common_end:
            period_end = current_start + timedelta(days=self.test_period_days)
            periods.append((current_start, period_end))
            
            # Move forward by 1 week for overlapping periods
            current_start += timedelta(days=7)
        
        self.logger.info(f"Generated {len(periods)} 2-week test periods")
        return periods
    
    def create_test_configuration(self, 
                                strategy_combo: List[str],
                                params: Tuple) -> Dict[str, Any]:
        """Create a test configuration"""
        leverage, risk, positions, daily_loss, drawdown = params
        
        # Create strategy configs
        strategies = []
        weight_per_strategy = 1.0 / len(strategy_combo)
        
        for i, strategy_type in enumerate(strategy_combo):
            strategies.append({
                'name': f'{strategy_type}_{i+1}',
                'type': strategy_type,
                'weight': weight_per_strategy,
                'risk_per_trade': risk
            })
        
        config = {
            'name': f'Test_{self.test_count}',
            'initial_balance': self.initial_balance,
            'leverage': leverage,
            'max_risk_per_trade': risk,
            'max_positions': positions,
            'max_daily_loss': daily_loss,
            'max_drawdown': drawdown,
            'symbols': list(self.historical_data.keys())[:4],  # Use top 4 pairs
            'strategies': strategies
        }
        
        return config
    
    def run_backtest_on_period(self, 
                              config: Dict[str, Any], 
                              start_date: datetime, 
                              end_date: datetime) -> Dict[str, Any]:
        """Run backtest on specific time period"""
        try:
            self.test_count += 1
            
            # Create backtest config
            backtest_config = BacktestConfig(
                initial_balance=config['initial_balance'],
                start_date=start_date,
                end_date=end_date,
                symbols=config['symbols'],
                commission_rate=0.0001,
                slippage_rate=0.00005,
                leverage=config['leverage'],
                risk_per_trade=config['max_risk_per_trade'],
                max_positions=config['max_positions']
            )
            
            # Create strategies
            strategy_factory = ExtremeStrategyFactory()
            strategies = []
            
            for strategy_config in config['strategies']:
                try:
                    strategy = strategy_factory.create_strategy(
                        strategy_config['type'],
                        {
                            'name': strategy_config['name'],
                            'leverage': config['leverage'],
                            'risk_per_trade': strategy_config['risk_per_trade']
                        }
                    )
                    if strategy:
                        strategies.append(strategy)
                except Exception as e:
                    self.logger.warning(f"Failed to create strategy {strategy_config['type']}: {e}")
            
            if not strategies:
                return {'return': -100, 'error': 'No strategies created'}
            
            # Create custom data provider for this period
            period_data = {}
            for symbol in config['symbols']:
                if symbol in self.historical_data:
                    symbol_data = self.historical_data[symbol]
                    period_symbol_data = symbol_data[
                        (symbol_data.index >= start_date) & 
                        (symbol_data.index <= end_date)
                    ].copy()
                    
                    if not period_symbol_data.empty:
                        period_data[symbol] = period_symbol_data
            
            if not period_data:
                return {'return': -100, 'error': 'No data for period'}
            
            # Run backtest with custom data
            backtester = EnhancedBacktester(backtest_config)
            
            # Override data provider with our historical data
            backtester.data_provider.data_cache = period_data
            
            metrics = backtester.run_backtest(strategies=strategies)
            
            total_return = metrics.get('total_return_pct', -100)
            
            result = {
                'test_id': self.test_count,
                'config': config,
                'period': {'start': start_date, 'end': end_date},
                'return': total_return,
                'win_rate': metrics.get('win_rate', 0),
                'total_trades': metrics.get('total_trades', 0),
                'max_drawdown': metrics.get('max_drawdown_pct', 100),
                'sharpe_ratio': metrics.get('sharpe_ratio', -10),
                'final_balance': metrics.get('final_balance', 0),
                'profit_factor': metrics.get('profit_factor', 0)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return {'return': -100, 'error': str(e)}
    
    def test_strategy_combination(self, 
                                strategy_combo: List[str], 
                                params: Tuple,
                                max_periods: int = 10) -> List[Dict[str, Any]]:
        """Test a strategy combination across multiple periods"""
        config = self.create_test_configuration(strategy_combo, params)
        
        # Get test periods
        all_periods = self.get_all_2week_periods()
        
        # Test on multiple periods (sample if too many)
        if len(all_periods) > max_periods:
            # Sample periods from different time ranges
            step = len(all_periods) // max_periods
            test_periods = all_periods[::step][:max_periods]
        else:
            test_periods = all_periods
        
        results = []
        
        for start_date, end_date in test_periods:
            result = self.run_backtest_on_period(config, start_date, end_date)
            results.append(result)
            
            # Log progress
            if result['return'] > 0:
                self.logger.info(f"✅ Positive return: {result['return']:.2f}% "
                               f"({start_date.date()} to {end_date.date()})")
            
            # Check if we hit the target
            if result['return'] >= self.target_return:
                self.logger.info(f"🎯 TARGET ACHIEVED! {result['return']:.2f}% >= {self.target_return}%")
                self.successful_configs.append({
                    'config': config,
                    'result': result,
                    'period': {'start': start_date, 'end': end_date}
                })
                return results  # Return early on success
        
        return results
    
    def run_comprehensive_optimization(self, max_tests: int = 500) -> Dict[str, Any]:
        """Run comprehensive optimization across all combinations"""
        self.logger.info("🚀 Starting comprehensive strategy optimization...")
        self.logger.info(f"Target: {self.target_return:,}% return in {self.test_period_days} days")
        self.logger.info(f"Maximum tests: {max_tests}")
        
        # Generate all parameter combinations
        param_combinations = list(itertools.product(
            self.parameter_ranges['leverage'],
            self.parameter_ranges['max_risk_per_trade'],
            self.parameter_ranges['max_positions'],
            self.parameter_ranges['max_daily_loss'],
            self.parameter_ranges['max_drawdown']
        ))
        
        self.logger.info(f"Generated {len(param_combinations)} parameter combinations")
        
        # Generate strategy combinations (1-5 strategies)
        strategy_combinations = []
        for num_strategies in range(1, 6):
            for combo in itertools.combinations(self.god_strategies, num_strategies):
                strategy_combinations.append(list(combo))
        
        self.logger.info(f"Generated {len(strategy_combinations)} strategy combinations")
        
        # Sort by aggressiveness (more strategies + higher risk first)
        strategy_combinations.sort(key=lambda x: len(x), reverse=True)
        param_combinations.sort(key=lambda x: x[0] * x[1], reverse=True)  # leverage * risk
        
        all_results = []
        tests_run = 0
        
        # Test combinations
        for strategy_combo in strategy_combinations:
            if tests_run >= max_tests:
                break
                
            for params in param_combinations:
                if tests_run >= max_tests:
                    break
                
                self.logger.info(f"Testing {strategy_combo} with leverage={params[0]}, risk={params[1]*100:.0f}%")
                
                results = self.test_strategy_combination(strategy_combo, params, max_periods=5)
                all_results.extend(results)
                tests_run += len(results)
                
                # Calculate average return for this combination
                valid_results = [r for r in results if 'error' not in r]
                if valid_results:
                    avg_return = np.mean([r['return'] for r in valid_results])
                    max_return = max([r['return'] for r in valid_results])
                    
                    self.logger.info(f"  Avg return: {avg_return:.2f}%, Max return: {max_return:.2f}%")
                    
                    # Track best results
                    for result in valid_results:
                        if result['return'] > 0:  # Only positive returns
                            self.best_results.append(result)
                    
                    # Sort and keep top 10 results
                    self.best_results.sort(key=lambda x: x['return'], reverse=True)
                    self.best_results = self.best_results[:10]
                
                # Early exit if we found successful configs
                if self.successful_configs:
                    self.logger.info(f"🏆 Found {len(self.successful_configs)} successful configurations!")
                    break
            
            if self.successful_configs:
                break
        
        # Compile summary
        summary = {
            'total_tests': tests_run,
            'successful_configs': len(self.successful_configs),
            'target_achieved': len(self.successful_configs) > 0,
            'best_results': self.best_results,
            'successful_configs': self.successful_configs,
            'all_results': all_results
        }
        
        self.logger.info(f"Optimization completed. Ran {tests_run} tests.")
        
        if self.successful_configs:
            best_config = self.successful_configs[0]
            self.logger.info(f"🎯 BEST RESULT: {best_config['result']['return']:.2f}% return")
        elif self.best_results:
            best_result = self.best_results[0]
            self.logger.info(f"📈 BEST ATTEMPT: {best_result['return']:.2f}% return")
        else:
            self.logger.warning("❌ No positive returns found")
        
        return summary
    
    def save_results(self, summary: Dict[str, Any], filename: str = None):
        """Save optimization results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_results_{timestamp}.json"
        
        # Convert datetime objects to strings for JSON serialization
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Clean the summary for JSON serialization
        clean_summary = json.loads(json.dumps(summary, default=convert_datetime))
        
        with open(filename, 'w') as f:
            json.dump(clean_summary, f, indent=2)
        
        self.logger.info(f"Results saved to {filename}")
    
    def analyze_successful_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in successful configurations"""
        if not self.successful_configs:
            return {}
        
        analysis = {
            'common_strategies': {},
            'common_parameters': {},
            'time_periods': []
        }
        
        # Analyze strategy patterns
        for config_data in self.successful_configs:
            config = config_data['config']
            
            for strategy in config['strategies']:
                strategy_type = strategy['type']
                if strategy_type not in analysis['common_strategies']:
                    analysis['common_strategies'][strategy_type] = 0
                analysis['common_strategies'][strategy_type] += 1
        
        # Analyze parameter patterns
        param_keys = ['leverage', 'max_risk_per_trade', 'max_positions', 'max_daily_loss', 'max_drawdown']
        
        for key in param_keys:
            values = [config_data['config'][key] for config_data in self.successful_configs]
            analysis['common_parameters'][key] = {
                'mean': np.mean(values),
                'median': np.median(values),
                'min': min(values),
                'max': max(values)
            }
        
        # Analyze time periods
        for config_data in self.successful_configs:
            period = config_data['period']
            analysis['time_periods'].append({
                'start': period['start'].isoformat(),
                'end': period['end'].isoformat(),
                'return': config_data['result']['return']
            })
        
        return analysis


def main():
    """Main function to run comprehensive testing"""
    print("🚀 COMPREHENSIVE STRATEGY TESTING WITH 3-YEAR DATA")
    print("=" * 70)
    print("Target: 199,900% return (1M → 2B IDR) in 2 weeks")
    print("Method: Test all strategy combinations across 3 years of data")
    print("=" * 70)
    
    # Create and run tester
    tester = ComprehensiveStrategyTester()
    
    try:
        # Run comprehensive optimization
        summary = tester.run_comprehensive_optimization(max_tests=200)
        
        # Save results
        tester.save_results(summary)
        
        # Display results
        print("\n" + "=" * 70)
        print("🏁 COMPREHENSIVE TESTING COMPLETE")
        print("=" * 70)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Target Achieved: {'✅ YES' if summary['target_achieved'] else '❌ NO'}")
        print(f"Successful Configs: {summary['successful_configs']}")
        
        if summary['successful_configs']:
            print("\n🎯 SUCCESSFUL CONFIGURATIONS:")
            for i, config_data in enumerate(summary['successful_configs'][:3]):
                config = config_data['config']
                result = config_data['result']
                period = config_data['period']
                
                print(f"\n#{i+1} - Return: {result['return']:.2f}%")
                print(f"  Period: {period['start'].date()} to {period['end'].date()}")
                print(f"  Leverage: {config['leverage']}x")
                print(f"  Risk per Trade: {config['max_risk_per_trade']*100:.0f}%")
                print(f"  Strategies: {[s['type'] for s in config['strategies']]}")
                print(f"  Win Rate: {result['win_rate']*100:.1f}%")
                print(f"  Total Trades: {result['total_trades']}")
        
        elif summary['best_results']:
            print("\n📈 BEST ATTEMPTS:")
            for i, result in enumerate(summary['best_results'][:5]):
                config = result['config']
                period = result['period']
                
                print(f"\n#{i+1} - Return: {result['return']:.2f}%")
                print(f"  Period: {period['start'].date()} to {period['end'].date()}")
                print(f"  Leverage: {config['leverage']}x")
                print(f"  Risk per Trade: {config['max_risk_per_trade']*100:.0f}%")
                print(f"  Strategies: {[s['type'] for s in config['strategies']]}")
        
        # Analyze patterns if successful
        if summary['successful_configs']:
            analysis = tester.analyze_successful_patterns()
            
            print("\n🔍 SUCCESS PATTERN ANALYSIS:")
            print("Most Common Strategies:")
            for strategy, count in sorted(analysis['common_strategies'].items(), 
                                        key=lambda x: x[1], reverse=True):
                print(f"  {strategy}: {count} times")
            
            print("\nOptimal Parameters:")
            for param, stats in analysis['common_parameters'].items():
                print(f"  {param}: {stats['mean']:.3f} (avg), {stats['median']:.3f} (median)")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        logging.error(f"Testing error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

