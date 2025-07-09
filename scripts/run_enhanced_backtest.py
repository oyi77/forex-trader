#!/usr/bin/env python3
"""
Enhanced Backtest Runner
Comprehensive testing of trading strategies with real data
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from src.backtest.enhanced_backtester import EnhancedBacktester, BacktestConfig, BacktestMetrics
from src.backtest.config_validator import create_validated_config
from src.config.configuration_manager import get_config_manager, create_extreme_preset
from src.factories.strategy_factory import get_strategy_factory, get_extreme_strategy_factory
from src.core.base_classes import BaseRiskManager


class EnhancedRiskManager(BaseRiskManager):
    """Enhanced risk manager for backtesting"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.02)
        self.max_total_exposure = config.get('max_total_exposure', 0.1)
        self.max_drawdown_threshold = config.get('max_drawdown_threshold', 0.05)
        
    def validate_trade(self, signal, current_positions):
        """Validate if trade should be executed"""
        # Check maximum number of positions
        if len(current_positions) >= 5:
            return False
        
        # Check if signal confidence is sufficient
        if hasattr(signal, 'confidence') and signal.confidence < 70:
            return False
        
        return True
    
    def calculate_position_size(self, signal, account_balance):
        """Calculate position size based on risk"""
        risk_amount = account_balance * self.max_risk_per_trade
        
        if signal.stop_loss:
            price_diff = abs(signal.price - signal.stop_loss)
            if price_diff > 0:
                return risk_amount / price_diff
        
        return account_balance * 0.01  # 1% fallback
    
    def should_emergency_stop(self, current_balance, initial_balance):
        """Check if emergency stop should be triggered"""
        drawdown = (initial_balance - current_balance) / initial_balance
        return drawdown > self.max_drawdown_threshold


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('enhanced_backtest.log')
        ]
    )


def create_backtest_scenarios() -> List[Dict[str, Any]]:
    """Create different backtest scenarios"""
    scenarios = [
        {
            'name': 'Conservative_1M_IDR',
            'initial_balance': 1000000.0,  # 1M IDR
            'leverage': 50,
            'risk_per_trade': 0.01,
            'timeframe': '1h',
            'days': 90,
            'mode': 'conservative'
        },
        {
            'name': 'Moderate_1M_IDR',
            'initial_balance': 1000000.0,
            'leverage': 100,
            'risk_per_trade': 0.02,
            'timeframe': '1h',
            'days': 90,
            'mode': 'moderate'
        },
        {
            'name': 'Aggressive_1M_IDR',
            'initial_balance': 1000000.0,
            'leverage': 200,
            'risk_per_trade': 0.05,
            'timeframe': '30m',
            'days': 90,
            'mode': 'aggressive'
        },
        {
            'name': 'Extreme_1M_IDR',
            'initial_balance': 1000000.0,
            'leverage': 2000,
            'risk_per_trade': 0.6,  # 60% risk for extreme mode
            'timeframe': '15m',
            'days': 90,
            'mode': 'extreme'
        }
    ]
    
    return scenarios


def run_scenario_backtest(scenario: Dict[str, Any]) -> BacktestMetrics:
    """Run backtest for a specific scenario"""
    logger = logging.getLogger(__name__)
    logger.info(f"Running backtest scenario: {scenario['name']}")
    
    # Create backtest configuration with validation
    config = create_validated_config(
        initial_balance=scenario['initial_balance'],
        leverage=scenario['leverage'],
        risk_per_trade=scenario['risk_per_trade'],
        timeframe=scenario['timeframe'],
        symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],  # Focus on major pairs + Gold
        start_date=datetime.now() - timedelta(days=scenario['days']),
        end_date=datetime.now()
    )
    
    # Create strategies based on mode
    if scenario['mode'] == 'extreme':
        factory = get_extreme_strategy_factory()
        strategies = []
        
        # Create extreme strategies
        extreme_configs = [
            {'type': 'EXTREME_SCALPING', 'name': 'Scalper_1', 'timeframe': '1m', 'confidence_threshold': 0.95},
            {'type': 'NEWS_EXPLOSION', 'name': 'News_Trader_1', 'news_impact_threshold': 'HIGH'},
            {'type': 'BREAKOUT_MOMENTUM', 'name': 'Momentum_1', 'momentum_threshold': 0.03},
            {'type': 'MARTINGALE_EXTREME', 'name': 'Recovery_1', 'max_levels': 8}
        ]
        
        for strategy_config in extreme_configs:
            try:
                strategy = factory.create_strategy(strategy_config['type'], strategy_config)
                strategies.append(strategy)
            except Exception as e:
                logger.warning(f"Failed to create strategy {strategy_config['type']}: {e}")
    
    else:
        factory = get_strategy_factory()
        strategies = []
        
        # Create regular strategies
        regular_configs = [
            {'type': 'RSI', 'name': 'RSI_Strategy', 'period': 14},
            {'type': 'MA_CROSSOVER', 'name': 'MA_Strategy', 'fast_period': 10, 'slow_period': 20},
            {'type': 'BREAKOUT', 'name': 'Breakout_Strategy', 'lookback_period': 20},
            {'type': 'SCALPING', 'name': 'Scalp_Strategy', 'timeframe': '5m'}
        ]
        
        for strategy_config in regular_configs:
            try:
                strategy = factory.create_strategy(strategy_config['type'], strategy_config)
                strategies.append(strategy)
            except Exception as e:
                logger.warning(f"Failed to create strategy {strategy_config['type']}: {e}")
    
    if not strategies:
        logger.error("No strategies created, cannot run backtest")
        return BacktestMetrics()
    
    # Create risk manager
    risk_manager = EnhancedRiskManager({
        'max_risk_per_trade': scenario['risk_per_trade'],
        'max_total_exposure': 0.1,
        'max_drawdown_threshold': 0.5 if scenario['mode'] == 'extreme' else 0.1
    })
    
    # Run backtest
    backtester = EnhancedBacktester(config)
    metrics = backtester.run_backtest(strategies, risk_manager)
    
    logger.info(f"Scenario {scenario['name']} completed:")
    logger.info(f"  Total Return: {metrics.total_return_pct:.2f}%")
    logger.info(f"  Win Rate: {metrics.win_rate:.2f}%")
    logger.info(f"  Max Drawdown: {metrics.max_drawdown:.2f}%")
    logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    
    return metrics


def calculate_required_performance() -> Dict[str, float]:
    """Calculate required performance to reach 2B IDR goal"""
    initial_balance = 1000000.0  # 1M IDR
    target_balance = 2000000000.0  # 2B IDR
    days_remaining = (datetime(2025, 7, 24) - datetime.now()).days
    
    required_return = (target_balance / initial_balance - 1) * 100
    required_daily_return = ((target_balance / initial_balance) ** (1 / days_remaining) - 1) * 100
    
    return {
        'total_required_return': required_return,
        'daily_required_return': required_daily_return,
        'days_remaining': days_remaining
    }


def analyze_results(scenario_results: List[Dict[str, Any]]) -> None:
    """Analyze backtest results and provide recommendations"""
    logger = logging.getLogger(__name__)
    
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST RESULTS ANALYSIS")
    logger.info("=" * 80)
    
    # Calculate required performance
    required_perf = calculate_required_performance()
    logger.info(f"GOAL ANALYSIS:")
    logger.info(f"  Target: 2,000,000,000 IDR (from 1,000,000 IDR)")
    logger.info(f"  Required Total Return: {required_perf['total_required_return']:,.0f}%")
    logger.info(f"  Required Daily Return: {required_perf['daily_required_return']:.4f}%")
    logger.info(f"  Days Remaining: {required_perf['days_remaining']}")
    
    logger.info(f"\nSCENARIO COMPARISON:")
    
    best_scenario = None
    best_return = -float('inf')
    
    for result in scenario_results:
        scenario = result['scenario']
        metrics = result['metrics']
        
        logger.info(f"\n{scenario['name']}:")
        logger.info(f"  Total Return: {metrics.total_return_pct:.2f}%")
        logger.info(f"  Annualized Return: {metrics.annualized_return:.2f}%")
        logger.info(f"  Win Rate: {metrics.win_rate:.2f}%")
        logger.info(f"  Profit Factor: {metrics.profit_factor:.2f}")
        logger.info(f"  Max Drawdown: {metrics.max_drawdown:.2f}%")
        logger.info(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        logger.info(f"  Total Trades: {metrics.total_trades}")
        
        # Check if this scenario can achieve the goal
        if metrics.annualized_return > 0:
            projected_days = required_perf['days_remaining']
            projected_return = ((1 + metrics.annualized_return / 100) ** (projected_days / 365) - 1) * 100
            logger.info(f"  Projected Return ({projected_days} days): {projected_return:.2f}%")
            
            if projected_return >= required_perf['total_required_return']:
                logger.info(f"  ✅ CAN ACHIEVE GOAL!")
            else:
                logger.info(f"  ❌ Cannot achieve goal")
        
        if metrics.total_return_pct > best_return:
            best_return = metrics.total_return_pct
            best_scenario = result
    
    # Recommendations
    logger.info(f"\nRECOMMENDATIONS:")
    
    if best_scenario:
        logger.info(f"Best performing scenario: {best_scenario['scenario']['name']}")
        logger.info(f"Best return: {best_scenario['metrics'].total_return_pct:.2f}%")
        
        # Check if any scenario can achieve the goal
        achievable_scenarios = []
        for result in scenario_results:
            metrics = result['metrics']
            if metrics.annualized_return > 0:
                projected_days = required_perf['days_remaining']
                projected_return = ((1 + metrics.annualized_return / 100) ** (projected_days / 365) - 1) * 100
                if projected_return >= required_perf['total_required_return']:
                    achievable_scenarios.append(result)
        
        if achievable_scenarios:
            logger.info(f"\n✅ GOAL IS ACHIEVABLE!")
            logger.info(f"Recommended scenarios:")
            for result in achievable_scenarios:
                scenario = result['scenario']
                metrics = result['metrics']
                logger.info(f"  - {scenario['name']}: {metrics.annualized_return:.2f}% annual return")
        else:
            logger.info(f"\n⚠️  GOAL MAY BE CHALLENGING")
            logger.info(f"Consider:")
            logger.info(f"  - Increasing leverage (current max: {max(r['scenario']['leverage'] for r in scenario_results)})")
            logger.info(f"  - Optimizing strategy parameters")
            logger.info(f"  - Adding more aggressive strategies")
            logger.info(f"  - Using shorter timeframes for more trading opportunities")
    
    logger.info("\n" + "=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Enhanced Forex Trading Backtest')
    parser.add_argument('--scenario', type=str, help='Run specific scenario')
    parser.add_argument('--all', action='store_true', help='Run all scenarios')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--days', type=int, default=90, help='Backtest days')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    print("🚀 Enhanced Forex Trading Backtest")
    print("=" * 60)
    
    # Create scenarios
    scenarios = create_backtest_scenarios()
    
    # Override days if specified
    if args.days != 90:
        for scenario in scenarios:
            scenario['days'] = args.days
    
    scenario_results = []
    
    if args.scenario:
        # Run specific scenario
        scenario = next((s for s in scenarios if s['name'] == args.scenario), None)
        if scenario:
            metrics = run_scenario_backtest(scenario)
            scenario_results.append({'scenario': scenario, 'metrics': metrics})
        else:
            logger.error(f"Scenario '{args.scenario}' not found")
            return 1
    
    elif args.all:
        # Run all scenarios
        for scenario in scenarios:
            try:
                metrics = run_scenario_backtest(scenario)
                scenario_results.append({'scenario': scenario, 'metrics': metrics})
            except Exception as e:
                logger.error(f"Scenario {scenario['name']} failed: {e}")
    
    else:
        # Run extreme scenario by default (for goal achievement)
        extreme_scenario = next(s for s in scenarios if s['name'] == 'Extreme_1M_IDR')
        metrics = run_scenario_backtest(extreme_scenario)
        scenario_results.append({'scenario': extreme_scenario, 'metrics': metrics})
    
    # Analyze results
    if scenario_results:
        analyze_results(scenario_results)
    
    print("\n✅ Backtest completed! Check reports/ directory for detailed results.")
    return 0


if __name__ == "__main__":
    exit(main())

