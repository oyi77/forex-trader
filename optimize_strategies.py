#!/usr/bin/env python3
"""
Strategy Optimization Script
Optimize trading strategies to achieve 2 billion IDR goal
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import itertools

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.factories.strategy_factory import get_extreme_strategy_factory
from src.backtest.enhanced_backtester import EnhancedBacktester
from src.data.real_data_provider import RealDataProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StrategyOptimizer:
    """Optimize trading strategies for maximum performance"""
    
    def __init__(self):
        self.target_return = 199900  # 199,900% return needed
        self.days_remaining = 15
        self.required_daily_return = 65.98  # 65.98% daily return needed
        self.initial_balance = 1000000  # 1M IDR
        self.target_balance = 2000000000  # 2B IDR
        
    def optimize_extreme_strategies(self) -> Dict[str, Any]:
        """Optimize extreme strategies for the 2B IDR goal"""
        logger.info("Starting strategy optimization for 2B IDR goal")
        
        # Define parameter ranges to test
        parameter_sets = [
            # Conservative aggressive (lower risk, higher frequency)
            {
                'name': 'Conservative_Aggressive',
                'leverage': 100,
                'risk_per_trade': 0.15,  # 15% per trade
                'confidence_threshold': 80,
                'max_positions': 8,
                'stop_loss_multiplier': 1.0,
                'take_profit_multiplier': 3.0
            },
            # Moderate aggressive
            {
                'name': 'Moderate_Aggressive', 
                'leverage': 500,
                'risk_per_trade': 0.25,  # 25% per trade
                'confidence_threshold': 75,
                'max_positions': 6,
                'stop_loss_multiplier': 0.8,
                'take_profit_multiplier': 4.0
            },
            # High aggressive
            {
                'name': 'High_Aggressive',
                'leverage': 1000,
                'risk_per_trade': 0.35,  # 35% per trade
                'confidence_threshold': 70,
                'max_positions': 5,
                'stop_loss_multiplier': 0.6,
                'take_profit_multiplier': 5.0
            },
            # Ultra aggressive (but more controlled than extreme)
            {
                'name': 'Ultra_Aggressive',
                'leverage': 1500,
                'risk_per_trade': 0.45,  # 45% per trade
                'confidence_threshold': 65,
                'max_positions': 4,
                'stop_loss_multiplier': 0.5,
                'take_profit_multiplier': 6.0
            },
            # Optimized extreme (refined from previous test)
            {
                'name': 'Optimized_Extreme',
                'leverage': 800,
                'risk_per_trade': 0.20,  # 20% per trade
                'confidence_threshold': 85,
                'max_positions': 3,
                'stop_loss_multiplier': 1.2,
                'take_profit_multiplier': 8.0
            }
        ]
        
        results = []
        
        for params in parameter_sets:
            logger.info(f"Testing parameter set: {params['name']}")
            
            try:
                # Run backtest with these parameters
                metrics = self._run_optimization_backtest(params)
                
                # Calculate goal achievement probability
                goal_score = self._calculate_goal_score(metrics, params)
                
                result = {
                    'parameters': params,
                    'metrics': metrics,
                    'goal_score': goal_score,
                    'daily_return_needed': self.required_daily_return,
                    'achieved_daily_return': metrics.get('daily_return', 0),
                    'goal_achievable': goal_score > 0.7
                }
                
                results.append(result)
                
                logger.info(f"  Total Return: {metrics.get('total_return', 0):.2f}%")
                logger.info(f"  Daily Return: {metrics.get('daily_return', 0):.2f}%")
                logger.info(f"  Goal Score: {goal_score:.3f}")
                logger.info(f"  Goal Achievable: {result['goal_achievable']}")
                
            except Exception as e:
                logger.error(f"Error testing {params['name']}: {e}")
                continue
        
        # Find best performing strategy
        if results:
            best_result = max(results, key=lambda x: x['goal_score'])
            logger.info(f"\nBest performing strategy: {best_result['parameters']['name']}")
            logger.info(f"Goal Score: {best_result['goal_score']:.3f}")
            logger.info(f"Goal Achievable: {best_result['goal_achievable']}")
            
            return {
                'best_strategy': best_result,
                'all_results': results,
                'optimization_summary': self._create_optimization_summary(results)
            }
        else:
            logger.warning("No successful optimization results")
            return {'best_strategy': None, 'all_results': [], 'optimization_summary': {}}
    
    def _run_optimization_backtest(self, params: Dict[str, Any]) -> Dict[str, float]:
        """Run backtest with specific parameters"""
        
        # Create scenario configuration
        scenario = {
            'name': params['name'],
            'initial_balance': self.initial_balance,
            'leverage': params['leverage'],
            'risk_per_trade': params['risk_per_trade'],
            'confidence_threshold': params['confidence_threshold'],
            'max_positions': params['max_positions'],
            'stop_loss_multiplier': params['stop_loss_multiplier'],
            'take_profit_multiplier': params['take_profit_multiplier'],
            'pairs': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
            'strategies': [
                {'name': 'Scalping_1', 'type': 'EXTREME_SCALPING', 'weight': 0.3},
                {'name': 'News_1', 'type': 'NEWS_EXPLOSION', 'weight': 0.2},
                {'name': 'Momentum_1', 'type': 'BREAKOUT_MOMENTUM', 'weight': 0.3},
                {'name': 'Recovery_1', 'type': 'MARTINGALE_EXTREME', 'weight': 0.2}
            ]
        }
        
        # Initialize components
        factory = get_extreme_strategy_factory()
        data_provider = RealDataProvider()
        
        # Create backtest configuration
        from src.backtest.enhanced_backtester import BacktestConfig
        config = BacktestConfig(
            initial_balance=scenario['initial_balance'],
            leverage=scenario['leverage'],
            risk_per_trade=scenario['risk_per_trade'],
            max_positions=scenario['max_positions'],
            symbols=scenario['pairs']
        )
        
        backtester = EnhancedBacktester(config)
        
        # Create strategies
        strategies = []
        for strategy_config in scenario['strategies']:
            strategy = factory.create_strategy(
                strategy_config['type'],
                {
                    'name': strategy_config['name'],
                    'confidence_threshold': params['confidence_threshold'],
                    'stop_loss_multiplier': params['stop_loss_multiplier'],
                    'take_profit_multiplier': params['take_profit_multiplier']
                }
            )
            strategies.append(strategy)
        
        # Run backtest
        metrics = backtester.run_backtest(strategies=strategies)
        
        # Calculate additional metrics
        if metrics.final_balance > 0:
            total_return = ((metrics.final_balance - metrics.initial_balance) / metrics.initial_balance) * 100
            daily_return = ((metrics.final_balance / metrics.initial_balance) ** (1/30) - 1) * 100
        else:
            total_return = -100
            daily_return = -100
        
        return {
            'total_return': total_return,
            'daily_return': daily_return,
            'win_rate': metrics.win_rate,
            'profit_factor': metrics.profit_factor,
            'max_drawdown': metrics.max_drawdown,
            'sharpe_ratio': metrics.sharpe_ratio,
            'total_trades': metrics.total_trades,
            'final_balance': metrics.final_balance
        }
    
    def _calculate_goal_score(self, metrics: Dict[str, float], params: Dict[str, Any]) -> float:
        """Calculate how well this strategy could achieve the 2B IDR goal"""
        
        daily_return = metrics.get('daily_return', -100)
        win_rate = metrics.get('win_rate', 0)
        profit_factor = metrics.get('profit_factor', 0)
        max_drawdown = metrics.get('max_drawdown', 100)
        total_trades = metrics.get('total_trades', 0)
        
        # Base score from daily return achievement
        return_score = min(1.0, max(0.0, daily_return / self.required_daily_return))
        
        # Bonus for high win rate
        win_rate_bonus = min(0.3, win_rate / 100 * 0.3)
        
        # Bonus for good profit factor
        profit_factor_bonus = min(0.2, profit_factor / 5.0 * 0.2)
        
        # Penalty for high drawdown
        drawdown_penalty = min(0.4, max_drawdown / 100 * 0.4)
        
        # Bonus for sufficient trading activity
        activity_bonus = min(0.1, total_trades / 50 * 0.1)
        
        # Calculate final score
        goal_score = return_score + win_rate_bonus + profit_factor_bonus + activity_bonus - drawdown_penalty
        
        return max(0.0, min(1.0, goal_score))
    
    def _create_optimization_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Create optimization summary"""
        
        if not results:
            return {}
        
        # Sort by goal score
        sorted_results = sorted(results, key=lambda x: x['goal_score'], reverse=True)
        
        summary = {
            'total_strategies_tested': len(results),
            'achievable_strategies': len([r for r in results if r['goal_achievable']]),
            'best_daily_return': max([r['achieved_daily_return'] for r in results]),
            'required_daily_return': self.required_daily_return,
            'top_3_strategies': [
                {
                    'name': r['parameters']['name'],
                    'goal_score': r['goal_score'],
                    'daily_return': r['achieved_daily_return'],
                    'total_return': r['metrics']['total_return']
                }
                for r in sorted_results[:3]
            ]
        }
        
        return summary

def main():
    """Main optimization function"""
    print("🎯 Strategy Optimization for 2 Billion IDR Goal")
    print("=" * 60)
    
    optimizer = StrategyOptimizer()
    
    try:
        # Run optimization
        results = optimizer.optimize_extreme_strategies()
        
        if results['best_strategy']:
            best = results['best_strategy']
            
            print(f"\n🏆 BEST STRATEGY FOUND: {best['parameters']['name']}")
            print(f"Goal Score: {best['goal_score']:.3f}")
            print(f"Goal Achievable: {'✅ YES' if best['goal_achievable'] else '❌ NO'}")
            print(f"Daily Return Achieved: {best['achieved_daily_return']:.2f}%")
            print(f"Daily Return Required: {best['daily_return_needed']:.2f}%")
            print(f"Total Return: {best['metrics']['total_return']:.2f}%")
            print(f"Win Rate: {best['metrics']['win_rate']:.1f}%")
            print(f"Max Drawdown: {best['metrics']['max_drawdown']:.1f}%")
            
            # Save optimization results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"reports/optimization_results_{timestamp}.txt"
            
            os.makedirs("reports", exist_ok=True)
            with open(results_file, 'w') as f:
                f.write("STRATEGY OPTIMIZATION RESULTS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Goal: Achieve 2,000,000,000 IDR from 1,000,000 IDR\n")
                f.write(f"Required Daily Return: {optimizer.required_daily_return:.2f}%\n")
                f.write(f"Days Remaining: {optimizer.days_remaining}\n\n")
                
                f.write("OPTIMIZATION SUMMARY:\n")
                summary = results['optimization_summary']
                f.write(f"Total Strategies Tested: {summary.get('total_strategies_tested', 0)}\n")
                f.write(f"Achievable Strategies: {summary.get('achievable_strategies', 0)}\n")
                f.write(f"Best Daily Return: {summary.get('best_daily_return', 0):.2f}%\n\n")
                
                f.write("TOP 3 STRATEGIES:\n")
                for i, strategy in enumerate(summary.get('top_3_strategies', []), 1):
                    f.write(f"{i}. {strategy['name']}\n")
                    f.write(f"   Goal Score: {strategy['goal_score']:.3f}\n")
                    f.write(f"   Daily Return: {strategy['daily_return']:.2f}%\n")
                    f.write(f"   Total Return: {strategy['total_return']:.2f}%\n\n")
                
                f.write("DETAILED RESULTS:\n")
                for result in results['all_results']:
                    f.write(f"\nStrategy: {result['parameters']['name']}\n")
                    f.write(f"Parameters: {result['parameters']}\n")
                    f.write(f"Metrics: {result['metrics']}\n")
                    f.write(f"Goal Score: {result['goal_score']:.3f}\n")
                    f.write(f"Goal Achievable: {result['goal_achievable']}\n")
                    f.write("-" * 40 + "\n")
            
            print(f"\n📊 Detailed results saved to: {results_file}")
            
        else:
            print("\n❌ No viable strategies found for the 2B IDR goal")
            print("Consider:")
            print("- Extending the timeline")
            print("- Reducing the target amount")
            print("- Using additional capital")
            print("- Exploring alternative investment strategies")
        
        return 0 if results['best_strategy'] and results['best_strategy']['goal_achievable'] else 1
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

