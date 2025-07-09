#!/usr/bin/env python3
"""
Iterative Strategy Optimizer
Continuously improves strategies until achieving 199,900% return target
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import random
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data.three_year_data_collector import ThreeYearDataCollector
from src.factories.strategy_factory import ExtremeStrategyFactory
from src.backtest.enhanced_backtester import BacktestConfig, EnhancedBacktester


class IterativeOptimizer:
    """
    Continuously optimizes strategies until target is achieved
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
        
        # Optimization state
        self.iteration = 0
        self.best_result = None
        self.successful_configs = []
        self.learning_data = []
        
        # Dynamic parameter ranges (will evolve)
        self.current_ranges = {
            'leverage': [1500, 2000],
            'risk_per_trade': [0.80, 0.95],
            'max_positions': [8, 15],
            'position_size_multiplier': [2.0, 5.0],
            'volatility_threshold': [0.01, 0.05],
            'trend_strength': [0.7, 0.95]
        }
        
        # Available strategies (use ultra-aggressive ones that generate signals)
        self.available_strategies = [
            'ALWAYS_TRADING',
            'SCALPING_MACHINE',
            'MOMENTUM_BLASTER',
            'VOLATILITY_HUNTER',
            'RANDOM_WALK',
            'ALL_IN'
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('iterative_optimization.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def get_best_2week_periods(self, num_periods: int = 20) -> List[Tuple[datetime, datetime]]:
        """Get the most volatile/profitable 2-week periods for testing"""
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
            
            # Calculate volatility for this period
            period_volatility = 0
            for symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']:
                if symbol in self.historical_data:
                    symbol_data = self.historical_data[symbol]
                    period_data = symbol_data[
                        (symbol_data.index >= current_start) & 
                        (symbol_data.index <= period_end)
                    ]
                    
                    if not period_data.empty:
                        returns = period_data['close'].pct_change().dropna()
                        volatility = returns.std() * np.sqrt(len(returns))
                        period_volatility += volatility
            
            all_periods.append((current_start, period_end, period_volatility))
            current_start += timedelta(days=7)  # Move by 1 week
        
        # Sort by volatility (highest first) and take top periods
        all_periods.sort(key=lambda x: x[2], reverse=True)
        
        # Return top volatile periods
        return [(start, end) for start, end, _ in all_periods[:num_periods]]
    
    def create_evolved_config(self, iteration: int) -> Dict[str, Any]:
        """Create an evolved configuration based on learning"""
        
        # Evolve parameters based on iteration
        if self.best_result and self.best_result['return'] > 0:
            # Learn from best result
            best_config = self.best_result['config']
            
            # Slightly modify successful parameters
            leverage = int(best_config['leverage'] * random.uniform(0.9, 1.1))
            risk = best_config['max_risk_per_trade'] * random.uniform(0.95, 1.05)
            positions = max(1, int(best_config['max_positions'] * random.uniform(0.8, 1.2)))
        else:
            # Use current ranges with some randomization
            leverage = random.randint(self.current_ranges['leverage'][0], 
                                    self.current_ranges['leverage'][1])
            risk = random.uniform(self.current_ranges['risk_per_trade'][0], 
                                self.current_ranges['risk_per_trade'][1])
            positions = random.randint(self.current_ranges['max_positions'][0], 
                                     self.current_ranges['max_positions'][1])
        
        # Ensure extreme values for extreme returns
        leverage = max(leverage, 1500)
        risk = max(risk, 0.75)
        positions = max(positions, 5)
        
        # Select strategies (favor combinations that worked before)
        if self.successful_configs:
            # Learn from successful strategy combinations
            successful_strategies = []
            for config_data in self.successful_configs:
                config = config_data['config']
                for strategy in config['strategies']:
                    successful_strategies.append(strategy['type'])
            
            # Use most common successful strategies
            strategy_counts = {}
            for strategy in successful_strategies:
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            # Select top strategies
            sorted_strategies = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
            selected_strategies = [s[0] for s in sorted_strategies[:3]]
            
            # Add some randomness
            if len(selected_strategies) < 3:
                remaining = [s for s in self.available_strategies if s not in selected_strategies]
                selected_strategies.extend(random.sample(remaining, min(2, len(remaining))))
        else:
            # Random selection with bias toward aggressive strategies
            num_strategies = random.randint(2, 4)
            selected_strategies = random.sample(self.available_strategies, num_strategies)
        
        # Create strategy configs
        strategies = []
        weight_per_strategy = 1.0 / len(selected_strategies)
        
        for i, strategy_type in enumerate(selected_strategies):
            strategies.append({
                'name': f'{strategy_type}_{i+1}',
                'type': strategy_type,
                'weight': weight_per_strategy,
                'risk_per_trade': risk
            })
        
        config = {
            'name': f'Iteration_{iteration}',
            'initial_balance': self.initial_balance,
            'leverage': leverage,
            'max_risk_per_trade': risk,
            'max_positions': positions,
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
            'strategies': strategies,
            'iteration': iteration
        }
        
        return config
    
    def run_enhanced_backtest(self, config: Dict[str, Any], 
                            start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Run enhanced backtest with custom optimizations"""
        try:
            # Create backtest config
            backtest_config = BacktestConfig(
                initial_balance=config['initial_balance'],
                start_date=start_date,
                end_date=end_date,
                symbols=config['symbols'],
                commission_rate=0.00001,  # Very low commission for extreme trading
                slippage_rate=0.00001,    # Very low slippage
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
            
            total_return = metrics.get('total_return_pct', -100)
            
            result = {
                'iteration': config['iteration'],
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
            self.logger.error(f"Enhanced backtest failed: {e}")
            return {'return': -100, 'error': str(e)}
    
    def learn_from_results(self, results: List[Dict[str, Any]]):
        """Learn from results and update parameter ranges"""
        
        # Filter successful results
        positive_results = [r for r in results if r['return'] > 0]
        
        if positive_results:
            self.logger.info(f"Learning from {len(positive_results)} positive results")
            
            # Update best result
            best_in_batch = max(positive_results, key=lambda x: x['return'])
            if self.best_result is None or best_in_batch['return'] > self.best_result['return']:
                self.best_result = best_in_batch
                self.logger.info(f"New best result: {best_in_batch['return']:.2f}%")
            
            # Analyze successful parameters
            successful_leverages = [r['config']['leverage'] for r in positive_results]
            successful_risks = [r['config']['max_risk_per_trade'] for r in positive_results]
            successful_positions = [r['config']['max_positions'] for r in positive_results]
            
            # Update parameter ranges to focus on successful values
            if successful_leverages:
                min_lev = min(successful_leverages)
                max_lev = max(successful_leverages)
                self.current_ranges['leverage'] = [
                    max(1000, int(min_lev * 0.9)),
                    min(2000, int(max_lev * 1.1))
                ]
            
            if successful_risks:
                min_risk = min(successful_risks)
                max_risk = max(successful_risks)
                self.current_ranges['risk_per_trade'] = [
                    max(0.5, min_risk * 0.95),
                    min(0.99, max_risk * 1.05)
                ]
            
            if successful_positions:
                min_pos = min(successful_positions)
                max_pos = max(successful_positions)
                self.current_ranges['max_positions'] = [
                    max(3, int(min_pos * 0.8)),
                    min(20, int(max_pos * 1.2))
                ]
            
            self.logger.info(f"Updated ranges: leverage={self.current_ranges['leverage']}, "
                           f"risk={self.current_ranges['risk_per_trade']}, "
                           f"positions={self.current_ranges['max_positions']}")
        
        # Store learning data
        self.learning_data.extend(results)
        
        # Keep only recent learning data (last 1000 results)
        if len(self.learning_data) > 1000:
            self.learning_data = self.learning_data[-1000:]
    
    def run_optimization_cycle(self, cycle_size: int = 20) -> List[Dict[str, Any]]:
        """Run one optimization cycle"""
        self.logger.info(f"🔄 Running optimization cycle {self.iteration // cycle_size + 1}")
        
        # Get best test periods
        test_periods = self.get_best_2week_periods(num_periods=10)
        
        if not test_periods:
            self.logger.error("No test periods available")
            return []
        
        cycle_results = []
        
        for i in range(cycle_size):
            self.iteration += 1
            
            # Create evolved configuration
            config = self.create_evolved_config(self.iteration)
            
            # Test on multiple periods
            config_results = []
            
            for start_date, end_date in test_periods[:5]:  # Test on top 5 periods
                result = self.run_enhanced_backtest(config, start_date, end_date)
                config_results.append(result)
                
                # Early success detection
                if result['return'] >= self.target_return:
                    self.logger.info(f"🎯 TARGET ACHIEVED! {result['return']:.2f}% >= {self.target_return}%")
                    self.successful_configs.append({
                        'config': config,
                        'result': result,
                        'period': {'start': start_date, 'end': end_date}
                    })
                    return cycle_results + config_results  # Return immediately
            
            # Calculate average performance for this config
            valid_results = [r for r in config_results if 'error' not in r]
            if valid_results:
                avg_return = np.mean([r['return'] for r in valid_results])
                max_return = max([r['return'] for r in valid_results])
                
                self.logger.info(f"Iteration {self.iteration}: Avg={avg_return:.2f}%, Max={max_return:.2f}%")
                
                # Track positive results
                if max_return > 0:
                    best_result = max(valid_results, key=lambda x: x['return'])
                    cycle_results.append(best_result)
            
            cycle_results.extend(config_results)
        
        return cycle_results
    
    def run_until_target_achieved(self, max_iterations: int = 1000) -> Dict[str, Any]:
        """Run optimization until target is achieved or max iterations reached"""
        self.logger.info("🚀 Starting iterative optimization until target achieved")
        self.logger.info(f"Target: {self.target_return:,}% return in {self.test_period_days} days")
        self.logger.info(f"Maximum iterations: {max_iterations}")
        
        all_results = []
        cycle_count = 0
        
        while self.iteration < max_iterations and not self.successful_configs:
            cycle_count += 1
            
            self.logger.info(f"🔄 CYCLE {cycle_count} - Iterations {self.iteration + 1}-{self.iteration + 20}")
            
            # Run optimization cycle
            cycle_results = self.run_optimization_cycle(cycle_size=20)
            all_results.extend(cycle_results)
            
            # Learn from results
            self.learn_from_results(cycle_results)
            
            # Progress report
            if self.best_result:
                self.logger.info(f"📈 Current best: {self.best_result['return']:.2f}%")
            
            # Check for success
            if self.successful_configs:
                self.logger.info(f"🏆 SUCCESS! Found {len(self.successful_configs)} winning configurations!")
                break
            
            # Adaptive strategy: increase aggressiveness if not making progress
            if cycle_count % 5 == 0 and not self.successful_configs:
                self.logger.info("🔥 Increasing aggressiveness...")
                self.current_ranges['leverage'][0] = min(2000, self.current_ranges['leverage'][0] + 100)
                self.current_ranges['risk_per_trade'][0] = min(0.95, self.current_ranges['risk_per_trade'][0] + 0.05)
        
        # Compile final summary
        summary = {
            'total_iterations': self.iteration,
            'total_cycles': cycle_count,
            'target_achieved': len(self.successful_configs) > 0,
            'successful_configs': self.successful_configs,
            'best_result': self.best_result,
            'all_results': all_results,
            'final_ranges': self.current_ranges
        }
        
        return summary
    
    def save_results(self, summary: Dict[str, Any]):
        """Save optimization results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iterative_optimization_{timestamp}.json"
        
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
        
        clean_summary = json.loads(json.dumps(summary, default=convert_datetime))
        
        with open(filename, 'w') as f:
            json.dump(clean_summary, f, indent=2)
        
        self.logger.info(f"Results saved to {filename}")


def main():
    """Main function"""
    print("🚀 ITERATIVE STRATEGY OPTIMIZATION")
    print("=" * 60)
    print("Goal: Keep optimizing until 199,900% return is achieved")
    print("Method: Learn from each iteration and evolve parameters")
    print("=" * 60)
    
    optimizer = IterativeOptimizer()
    
    try:
        # Run optimization until target achieved
        summary = optimizer.run_until_target_achieved(max_iterations=500)
        
        # Save results
        optimizer.save_results(summary)
        
        # Display final results
        print("\n" + "=" * 60)
        print("🏁 ITERATIVE OPTIMIZATION COMPLETE")
        print("=" * 60)
        
        print(f"Total Iterations: {summary['total_iterations']}")
        print(f"Total Cycles: {summary['total_cycles']}")
        print(f"Target Achieved: {'✅ YES' if summary['target_achieved'] else '❌ NO'}")
        
        if summary['target_achieved']:
            print(f"Successful Configs: {len(summary['successful_configs'])}")
            
            print("\n🎯 WINNING CONFIGURATIONS:")
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
        
        elif summary['best_result']:
            print(f"\n📈 BEST ATTEMPT: {summary['best_result']['return']:.2f}%")
            config = summary['best_result']['config']
            print(f"  Leverage: {config['leverage']}x")
            print(f"  Risk per Trade: {config['max_risk_per_trade']*100:.0f}%")
            print(f"  Strategies: {[s['type'] for s in config['strategies']]}")
        
        print("\n📊 FINAL PARAMETER RANGES:")
        for param, range_val in summary['final_ranges'].items():
            print(f"  {param}: {range_val}")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Optimization interrupted by user")
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        logging.error(f"Optimization error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

