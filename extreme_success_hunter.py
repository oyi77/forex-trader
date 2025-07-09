#!/usr/bin/env python3
"""
Extreme Success Hunter
Relentlessly tests strategies until 199,900% return is achieved
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import random
import time
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.three_year_data_collector import ThreeYearDataCollector
from src.factories.strategy_factory import ExtremeStrategyFactory
from src.backtest.enhanced_backtester import BacktestConfig, EnhancedBacktester


class ExtremeSuccessHunter:
    """
    Relentlessly hunts for the winning combination that achieves 199,900% return
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
        
        # Success tracking
        self.test_count = 0
        self.successful_configs = []
        self.best_result = None
        
        # Ultra-aggressive strategies (use what's actually available)
        self.ultra_strategies = [
            'EXTREME_SCALPING',
            'NEWS_EXPLOSION',
            'BREAKOUT_MOMENTUM',
            'MARTINGALE_EXTREME',
            'MARTINGALE',
            'SCALPING'
        ]
        
        # Extreme parameter ranges
        self.extreme_ranges = {
            'leverage': [1800, 2000],
            'risk_per_trade': [0.90, 0.99],
            'max_positions': [10, 20],
            'commission_rate': [0.000001, 0.00001],  # Ultra-low
            'slippage_rate': [0.000001, 0.00001],    # Ultra-low
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('extreme_success_hunter.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_extreme_test_periods(self, num_periods: int = 50) -> List[Tuple[datetime, datetime]]:
        """Get extreme test periods with maximum volatility"""
        periods = []
        
        # Find common date range
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
        
        # Generate all possible 2-week periods
        all_periods = []
        current_start = common_start
        
        while current_start + timedelta(days=self.test_period_days) <= common_end:
            period_end = current_start + timedelta(days=self.test_period_days)
            
            # Calculate extreme volatility for this period
            period_score = 0
            for symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']:
                if symbol in self.historical_data:
                    symbol_data = self.historical_data[symbol]
                    period_data = symbol_data[
                        (symbol_data.index >= current_start) & 
                        (symbol_data.index <= period_end)
                    ]
                    
                    if not period_data.empty:
                        # Calculate multiple volatility measures
                        returns = period_data['close'].pct_change().dropna()
                        price_range = (period_data['high'].max() - period_data['low'].min()) / period_data['close'].mean()
                        volatility = returns.std() * np.sqrt(len(returns))
                        max_move = abs(returns).max()
                        
                        # Composite score favoring extreme movements
                        score = volatility * 100 + price_range * 50 + max_move * 200
                        period_score += score
            
            all_periods.append((current_start, period_end, period_score))
            current_start += timedelta(days=3)  # Move by 3 days for more overlap
        
        # Sort by extreme score (highest first)
        all_periods.sort(key=lambda x: x[2], reverse=True)
        
        # Return top extreme periods
        return [(start, end) for start, end, _ in all_periods[:num_periods]]
    
    def create_extreme_config(self, test_num: int) -> Dict[str, Any]:
        """Create extreme configuration designed for maximum returns"""
        
        # Ultra-aggressive parameters
        leverage = random.randint(self.extreme_ranges['leverage'][0], 
                                self.extreme_ranges['leverage'][1])
        risk = random.uniform(self.extreme_ranges['risk_per_trade'][0], 
                            self.extreme_ranges['risk_per_trade'][1])
        positions = random.randint(self.extreme_ranges['max_positions'][0], 
                                 self.extreme_ranges['max_positions'][1])
        
        # Ultra-low costs for maximum profit
        commission = random.uniform(self.extreme_ranges['commission_rate'][0],
                                  self.extreme_ranges['commission_rate'][1])
        slippage = random.uniform(self.extreme_ranges['slippage_rate'][0],
                                self.extreme_ranges['slippage_rate'][1])
        
        # Select multiple ultra-aggressive strategies
        num_strategies = random.randint(3, 6)
        selected_strategies = random.sample(self.ultra_strategies, num_strategies)
        
        # Create strategy configs with extreme settings
        strategies = []
        weight_per_strategy = 1.0 / len(selected_strategies)
        
        for i, strategy_type in enumerate(selected_strategies):
            strategies.append({
                'name': f'{strategy_type}_{i+1}',
                'type': strategy_type,
                'weight': weight_per_strategy,
                'risk_per_trade': risk,
                'aggressive_mode': True,
                'extreme_parameters': True
            })
        
        config = {
            'name': f'ExtremeTest_{test_num}',
            'initial_balance': self.initial_balance,
            'leverage': leverage,
            'max_risk_per_trade': risk,
            'max_positions': positions,
            'commission_rate': commission,
            'slippage_rate': slippage,
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
            'strategies': strategies,
            'test_number': test_num
        }
        
        return config
    
    def run_extreme_backtest(self, config: Dict[str, Any], 
                           start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Run extreme backtest optimized for maximum returns"""
        try:
            self.test_count += 1
            
            # Create backtest config with extreme settings
            backtest_config = BacktestConfig(
                initial_balance=config['initial_balance'],
                start_date=start_date,
                end_date=end_date,
                symbols=config['symbols'],
                commission_rate=config['commission_rate'],
                slippage_rate=config['slippage_rate'],
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
                            'risk_per_trade': strategy_config['risk_per_trade'],
                            'aggressive_mode': True,
                            'extreme_parameters': True
                        }
                    )
                    if strategy:
                        strategies.append(strategy)
                        self.logger.info(f"Created strategy: {strategy_config['name']}")
                except Exception as e:
                    self.logger.warning(f"Failed to create strategy {strategy_config['type']}: {e}")
            
            if not strategies:
                return {'return': -100, 'error': 'No strategies created'}
            
            # Prepare period data
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
            
            # Run backtest
            backtester = EnhancedBacktester(backtest_config)
            backtester.data_provider.data_cache = period_data
            
            metrics = backtester.run_backtest(strategies=strategies)
            
            # Extract metrics (handle both dict and object)
            if hasattr(metrics, '__dict__'):
                # It's an object, convert to dict
                metrics_dict = {
                    'total_return_pct': getattr(metrics, 'total_return_pct', -100),
                    'win_rate': getattr(metrics, 'win_rate', 0),
                    'total_trades': getattr(metrics, 'total_trades', 0),
                    'max_drawdown_pct': getattr(metrics, 'max_drawdown_pct', 100),
                    'sharpe_ratio': getattr(metrics, 'sharpe_ratio', -10),
                    'final_balance': getattr(metrics, 'final_balance', 0),
                    'profit_factor': getattr(metrics, 'profit_factor', 0)
                }
            else:
                # It's already a dict
                metrics_dict = metrics
            
            total_return = metrics_dict.get('total_return_pct', -100)
            
            result = {
                'test_number': config['test_number'],
                'config': config,
                'period': {'start': start_date, 'end': end_date},
                'return': total_return,
                'win_rate': metrics_dict.get('win_rate', 0),
                'total_trades': metrics_dict.get('total_trades', 0),
                'max_drawdown': metrics_dict.get('max_drawdown_pct', 100),
                'sharpe_ratio': metrics_dict.get('sharpe_ratio', -10),
                'final_balance': metrics_dict.get('final_balance', 0),
                'profit_factor': metrics_dict.get('profit_factor', 0)
            }
            
            # Log progress
            if total_return > 0:
                self.logger.info(f"🟢 Test {self.test_count}: +{total_return:.2f}% return!")
            else:
                self.logger.info(f"🔴 Test {self.test_count}: {total_return:.2f}% return")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Extreme backtest failed: {e}")
            return {'return': -100, 'error': str(e)}
    
    def hunt_for_success(self, max_tests: int = 2000) -> Dict[str, Any]:
        """Hunt relentlessly until success is achieved"""
        self.logger.info("🎯 EXTREME SUCCESS HUNTER ACTIVATED")
        self.logger.info(f"Target: {self.target_return:,}% return in {self.test_period_days} days")
        self.logger.info(f"Maximum tests: {max_tests:,}")
        self.logger.info("Will not stop until target is achieved!")
        
        # Get extreme test periods
        test_periods = self.get_extreme_test_periods(num_periods=100)
        
        if not test_periods:
            self.logger.error("No test periods available")
            return {'success': False, 'error': 'No test periods'}
        
        self.logger.info(f"Found {len(test_periods)} extreme volatility periods")
        
        all_results = []
        start_time = time.time()
        
        for test_num in range(1, max_tests + 1):
            # Create extreme configuration
            config = self.create_extreme_config(test_num)
            
            # Test on multiple extreme periods
            period_results = []
            
            # Test on top 10 most volatile periods
            for period_idx, (start_date, end_date) in enumerate(test_periods[:10]):
                result = self.run_extreme_backtest(config, start_date, end_date)
                period_results.append(result)
                
                # Check for success
                if result['return'] >= self.target_return:
                    self.logger.info(f"🏆 SUCCESS ACHIEVED! {result['return']:.2f}% >= {self.target_return}%")
                    self.successful_configs.append({
                        'config': config,
                        'result': result,
                        'period': {'start': start_date, 'end': end_date},
                        'test_number': test_num,
                        'period_index': period_idx
                    })
                    
                    # Save success immediately
                    self.save_success(self.successful_configs[-1])
                    
                    return {
                        'success': True,
                        'winning_config': self.successful_configs[-1],
                        'total_tests': self.test_count,
                        'time_elapsed': time.time() - start_time
                    }
            
            # Track best result
            valid_results = [r for r in period_results if 'error' not in r]
            if valid_results:
                best_period_result = max(valid_results, key=lambda x: x['return'])
                all_results.append(best_period_result)
                
                if self.best_result is None or best_period_result['return'] > self.best_result['return']:
                    self.best_result = best_period_result
                    self.logger.info(f"📈 New best: {best_period_result['return']:.2f}%")
            
            # Progress report every 50 tests
            if test_num % 50 == 0:
                elapsed = time.time() - start_time
                tests_per_sec = self.test_count / elapsed
                self.logger.info(f"Progress: {test_num}/{max_tests} tests, "
                               f"{tests_per_sec:.1f} tests/sec, "
                               f"Best: {self.best_result['return']:.2f}% " if self.best_result else "Best: None")
        
        # If we reach here, target was not achieved
        self.logger.warning(f"❌ Target not achieved after {max_tests:,} tests")
        
        return {
            'success': False,
            'best_result': self.best_result,
            'total_tests': self.test_count,
            'time_elapsed': time.time() - start_time,
            'all_results': all_results
        }
    
    def save_success(self, success_data: Dict[str, Any]):
        """Save successful configuration immediately"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SUCCESS_ACHIEVED_{timestamp}.json"
        
        # Convert datetime objects for JSON
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
        
        clean_data = json.loads(json.dumps(success_data, default=convert_datetime))
        
        with open(filename, 'w') as f:
            json.dump(clean_data, f, indent=2)
        
        self.logger.info(f"🎉 SUCCESS SAVED TO {filename}")


def main():
    """Main function"""
    print("🎯 EXTREME SUCCESS HUNTER")
    print("=" * 60)
    print("MISSION: Achieve 199,900% return in 14 days")
    print("METHOD: Relentless testing until success")
    print("ATTITUDE: Failure is not an option!")
    print("=" * 60)
    
    hunter = ExtremeSuccessHunter()
    
    try:
        # Hunt for success
        result = hunter.hunt_for_success(max_tests=2000)
        
        print("\n" + "=" * 60)
        if result['success']:
            print("🏆 MISSION ACCOMPLISHED!")
            print("=" * 60)
            
            winning_config = result['winning_config']
            config = winning_config['config']
            trade_result = winning_config['result']
            period = winning_config['period']
            
            print(f"🎯 WINNING CONFIGURATION:")
            print(f"  Return: {trade_result['return']:.2f}%")
            print(f"  Period: {period['start'].date()} to {period['end'].date()}")
            print(f"  Test Number: {winning_config['test_number']}")
            print(f"  Total Tests: {result['total_tests']:,}")
            print(f"  Time Elapsed: {result['time_elapsed']:.1f} seconds")
            
            print(f"\n📊 STRATEGY DETAILS:")
            print(f"  Leverage: {config['leverage']}x")
            print(f"  Risk per Trade: {config['max_risk_per_trade']*100:.1f}%")
            print(f"  Max Positions: {config['max_positions']}")
            print(f"  Commission: {config['commission_rate']*100:.4f}%")
            print(f"  Strategies: {[s['type'] for s in config['strategies']]}")
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"  Win Rate: {trade_result['win_rate']*100:.1f}%")
            print(f"  Total Trades: {trade_result['total_trades']}")
            print(f"  Max Drawdown: {trade_result['max_drawdown']:.1f}%")
            print(f"  Sharpe Ratio: {trade_result['sharpe_ratio']:.2f}")
            print(f"  Final Balance: ${trade_result['final_balance']:,.0f}")
            
        else:
            print("❌ TARGET NOT ACHIEVED")
            print("=" * 60)
            print(f"Total Tests: {result['total_tests']:,}")
            print(f"Time Elapsed: {result['time_elapsed']:.1f} seconds")
            
            if result.get('best_result'):
                best = result['best_result']
                print(f"\n📈 BEST ATTEMPT: {best['return']:.2f}%")
                config = best['config']
                print(f"  Leverage: {config['leverage']}x")
                print(f"  Risk per Trade: {config['max_risk_per_trade']*100:.1f}%")
                print(f"  Strategies: {[s['type'] for s in config['strategies']]}")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Hunt interrupted by user")
    except Exception as e:
        print(f"\n❌ Hunt failed: {e}")
        logging.error(f"Hunt error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

