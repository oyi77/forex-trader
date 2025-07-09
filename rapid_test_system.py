#!/usr/bin/env python3
"""
Rapid-Fire Strategy Testing System
Automatically tests and optimizes strategies until target returns are achieved
"""

import os
import sys
import yaml
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import itertools
import time
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config.configuration_manager import ConfigurationManager
from src.factories.strategy_factory import ExtremeStrategyFactory
from src.backtest.enhanced_backtester import EnhancedBacktester
from src.core.interfaces import BacktestConfig


class RapidTestSystem:
    """
    Rapid testing system that iteratively optimizes strategies
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.target_return = 199900  # 199,900% target
        self.initial_balance = 1_000_000
        self.target_balance = 2_000_000_000
        self.days_to_test = 7
        
        # Test parameters to optimize
        self.parameter_ranges = {
            'leverage': [1000, 1500, 2000],
            'max_risk_per_trade': [0.50, 0.70, 0.85, 0.95],
            'max_positions': [5, 10, 15, 20],
            'max_daily_loss': [0.70, 0.80, 0.90, 0.95],
            'max_drawdown': [0.80, 0.90, 0.95, 0.99]
        }
        
        # God Mode strategies to test
        self.god_strategies = [
            'GOD_MODE_SCALPING',
            'MARTINGALE_GOD',
            'VOLATILITY_GOD',
            'TREND_GOD',
            'ALL_IN_GOD'
        ]
        
        self.best_result = {
            'return': -100,
            'config': None,
            'strategies': None
        }
        
        self.test_count = 0
        self.max_tests = 100  # Maximum tests before giving up
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for rapid testing"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rapid_test.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def generate_test_configurations(self) -> List[Dict[str, Any]]:
        """Generate all possible test configurations"""
        configs = []
        
        # Generate parameter combinations
        param_combinations = list(itertools.product(
            self.parameter_ranges['leverage'],
            self.parameter_ranges['max_risk_per_trade'],
            self.parameter_ranges['max_positions'],
            self.parameter_ranges['max_daily_loss'],
            self.parameter_ranges['max_drawdown']
        ))
        
        # Generate strategy combinations (1-5 strategies)
        for num_strategies in range(1, 6):
            for strategy_combo in itertools.combinations(self.god_strategies, num_strategies):
                for params in param_combinations:
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
                        'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
                        'strategies': strategies
                    }
                    
                    configs.append(config)
                    
                    if len(configs) >= self.max_tests:
                        return configs
        
        return configs
    
    def run_single_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single backtest with the given configuration"""
        try:
            self.test_count += 1
            
            # Create backtest config
            backtest_config = BacktestConfig(
                initial_balance=config['initial_balance'],
                start_date=datetime.now() - timedelta(days=self.days_to_test),
                end_date=datetime.now(),
                symbols=config['symbols'],
                commission=0.0001,
                slippage=0.00005,
                leverage=config['leverage'],
                max_risk_per_trade=config['max_risk_per_trade'],
                max_positions=config['max_positions'],
                max_daily_loss=config['max_daily_loss'],
                max_drawdown=config['max_drawdown']
            )
            
            # Create strategies
            strategy_factory = ExtremeStrategyFactory()
            strategies = []
            
            for strategy_config in config['strategies']:
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
            
            if not strategies:
                return {'return': -100, 'error': 'No strategies created'}
            
            # Run backtest
            backtester = EnhancedBacktester(backtest_config)
            metrics = backtester.run_backtest(strategies=strategies)
            
            total_return = metrics.get('total_return_pct', -100)
            
            result = {
                'test_id': self.test_count,
                'config': config,
                'return': total_return,
                'win_rate': metrics.get('win_rate', 0),
                'total_trades': metrics.get('total_trades', 0),
                'max_drawdown': metrics.get('max_drawdown_pct', 100),
                'sharpe_ratio': metrics.get('sharpe_ratio', -10),
                'final_balance': metrics.get('final_balance', 0)
            }
            
            # Log progress
            if self.test_count % 10 == 0:
                self.logger.info(f"Test {self.test_count}: Return={total_return:.2f}%, Best so far={self.best_result['return']:.2f}%")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Test {self.test_count} failed: {e}")
            return {'return': -100, 'error': str(e)}
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """Run a complete optimization cycle"""
        self.logger.info("🚀 Starting rapid-fire strategy optimization...")
        self.logger.info(f"Target: {self.target_return:,}% return in {self.days_to_test} days")
        self.logger.info(f"Maximum tests: {self.max_tests}")
        
        # Generate test configurations
        configs = self.generate_test_configurations()
        self.logger.info(f"Generated {len(configs)} test configurations")
        
        # Sort configs by aggressiveness (higher risk first)
        configs.sort(key=lambda x: (
            x['max_risk_per_trade'] * x['leverage'] * len(x['strategies'])
        ), reverse=True)
        
        start_time = time.time()
        results = []
        
        for i, config in enumerate(configs):
            if i >= self.max_tests:
                break
                
            result = self.run_single_test(config)
            results.append(result)
            
            # Update best result
            if result['return'] > self.best_result['return']:
                self.best_result = {
                    'return': result['return'],
                    'config': config,
                    'strategies': config['strategies'],
                    'full_result': result
                }
                
                self.logger.info(f"🎯 NEW BEST RESULT: {result['return']:.2f}% return!")
                
                # Check if we've achieved the target
                if result['return'] >= self.target_return:
                    self.logger.info(f"🏆 TARGET ACHIEVED! {result['return']:.2f}% >= {self.target_return}%")
                    break
            
            # Early stopping if we're getting consistently bad results
            if i > 20 and self.best_result['return'] < -50:
                self.logger.warning("Early stopping: No promising results found")
                break
        
        elapsed_time = time.time() - start_time
        
        # Generate summary
        summary = {
            'total_tests': len(results),
            'elapsed_time': elapsed_time,
            'best_result': self.best_result,
            'target_achieved': self.best_result['return'] >= self.target_return,
            'all_results': results
        }
        
        self.logger.info(f"Optimization completed in {elapsed_time:.1f} seconds")
        self.logger.info(f"Best result: {self.best_result['return']:.2f}% return")
        
        return summary
    
    def save_results(self, summary: Dict[str, Any], filename: str = None):
        """Save optimization results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimization_results_{timestamp}.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # Clean the summary for JSON serialization
        clean_summary = json.loads(json.dumps(summary, default=convert_numpy))
        
        with open(filename, 'w') as f:
            json.dump(clean_summary, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to {filename}")
    
    def create_optimized_config(self) -> Dict[str, Any]:
        """Create optimized configuration from best result"""
        if self.best_result['config'] is None:
            return None
        
        config = self.best_result['config'].copy()
        config['name'] = 'Optimized_God_Mode'
        config['description'] = f"Optimized configuration achieving {self.best_result['return']:.2f}% return"
        
        return config


def main():
    """Main function to run rapid optimization"""
    print("🚀 RAPID-FIRE STRATEGY OPTIMIZATION SYSTEM")
    print("=" * 60)
    print("Target: 199,900% return (1M → 2B IDR)")
    print("Method: Systematic testing of God Mode strategies")
    print("=" * 60)
    
    # Create and run optimization system
    optimizer = RapidTestSystem()
    
    try:
        # Run optimization
        summary = optimizer.run_optimization_cycle()
        
        # Save results
        optimizer.save_results(summary)
        
        # Display final results
        print("\n" + "=" * 60)
        print("🏁 OPTIMIZATION COMPLETE")
        print("=" * 60)
        
        best = summary['best_result']
        print(f"Best Return: {best['return']:.2f}%")
        print(f"Target Achieved: {'✅ YES' if summary['target_achieved'] else '❌ NO'}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Time Elapsed: {summary['elapsed_time']:.1f} seconds")
        
        if best['config']:
            print(f"\nBest Configuration:")
            print(f"  Leverage: {best['config']['leverage']}x")
            print(f"  Risk per Trade: {best['config']['max_risk_per_trade']*100:.0f}%")
            print(f"  Max Positions: {best['config']['max_positions']}")
            print(f"  Strategies: {len(best['config']['strategies'])}")
            
            for strategy in best['config']['strategies']:
                print(f"    - {strategy['type']} ({strategy['weight']*100:.0f}%)")
        
        # Create optimized config file
        if summary['target_achieved']:
            optimized_config = optimizer.create_optimized_config()
            if optimized_config:
                with open('god_mode_config.yaml', 'w') as f:
                    yaml.dump(optimized_config, f)
                print(f"\n✅ Optimized config saved to god_mode_config.yaml")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Optimization interrupted by user")
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        logging.error(f"Optimization error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

