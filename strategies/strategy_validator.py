"""
Strategy Validation Framework for Forex Trading Bot
Validates and compares multiple trading strategies with comprehensive metrics
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import json
import warnings
warnings.filterwarnings('ignore')

# Import our backtesting engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backtesting.backtest_engine import BacktestEngine, BacktestResults, BacktestMode

@dataclass
class StrategyMetrics:
    """Comprehensive strategy performance metrics"""
    strategy_name: str
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    calmar_ratio: float
    var_95: float
    cvar_95: float
    expectancy: float
    stability_score: float
    robustness_score: float
    overall_score: float

@dataclass
class ValidationResults:
    """Strategy validation results"""
    strategy_metrics: List[StrategyMetrics] = field(default_factory=list)
    best_strategy: Optional[str] = None
    strategy_rankings: List[Tuple[str, float]] = field(default_factory=list)
    correlation_matrix: Optional[pd.DataFrame] = None
    ensemble_weights: Optional[Dict[str, float]] = None

class StrategyValidator:
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger('StrategyValidator')
        self.backtest_engine = BacktestEngine(initial_capital=initial_capital)
        
        # Strategy registry
        self.strategies = {}
        self.validation_results = {}
        
        self.logger.info("Strategy Validator initialized")
    
    def register_strategy(self, name: str, strategy_func: Callable, 
                         default_params: Dict = None):
        """Register a trading strategy for validation"""
        self.strategies[name] = {
            'function': strategy_func,
            'params': default_params or {},
            'description': strategy_func.__doc__ or f"{name} strategy"
        }
        self.logger.info(f"Registered strategy: {name}")
    
    def validate_strategies(self, data: pd.DataFrame, 
                          validation_period: int = 252,
                          walk_forward: bool = True) -> ValidationResults:
        """Validate all registered strategies"""
        try:
            self.logger.info(f"Starting strategy validation with {len(self.strategies)} strategies")
            
            results = ValidationResults()
            strategy_returns = {}
            
            for strategy_name, strategy_info in self.strategies.items():
                self.logger.info(f"Validating strategy: {strategy_name}")
                
                try:
                    # Run backtest
                    if walk_forward:
                        backtest_results = self.backtest_engine.run_backtest(
                            data, 
                            strategy_info['function'],
                            mode=BacktestMode.WALK_FORWARD,
                            **strategy_info['params']
                        )
                    else:
                        backtest_results = self.backtest_engine.run_backtest(
                            data,
                            strategy_info['function'],
                            mode=BacktestMode.VECTORIZED,
                            **strategy_info['params']
                        )
                    
                    # Calculate comprehensive metrics
                    metrics = self._calculate_strategy_metrics(
                        strategy_name, backtest_results, data
                    )
                    
                    results.strategy_metrics.append(metrics)
                    
                    # Store returns for correlation analysis
                    if not backtest_results.equity_curve.empty:
                        returns = backtest_results.equity_curve.pct_change().dropna()
                        strategy_returns[strategy_name] = returns
                    
                    self.validation_results[strategy_name] = {
                        'metrics': metrics,
                        'backtest_results': backtest_results
                    }
                    
                except Exception as e:
                    self.logger.error(f"Error validating strategy {strategy_name}: {e}")
                    continue
            
            # Calculate strategy rankings
            results.strategy_rankings = self._rank_strategies(results.strategy_metrics)
            
            # Find best strategy
            if results.strategy_rankings:
                results.best_strategy = results.strategy_rankings[0][0]
            
            # Calculate correlation matrix
            if len(strategy_returns) > 1:
                results.correlation_matrix = self._calculate_correlation_matrix(strategy_returns)
            
            # Calculate ensemble weights
            results.ensemble_weights = self._calculate_ensemble_weights(results.strategy_metrics)
            
            self.logger.info(f"Strategy validation completed. Best strategy: {results.best_strategy}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Strategy validation error: {e}")
            return ValidationResults()
    
    def _calculate_strategy_metrics(self, strategy_name: str, 
                                  backtest_results: BacktestResults,
                                  data: pd.DataFrame) -> StrategyMetrics:
        """Calculate comprehensive strategy metrics"""
        try:
            # Basic metrics from backtest results
            total_return = backtest_results.total_pnl_pct
            annual_return = total_return  # Simplified - should be annualized
            
            # Calculate volatility
            if not backtest_results.equity_curve.empty:
                returns = backtest_results.equity_curve.pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
            else:
                volatility = 0
            
            # Stability score (consistency of returns)
            stability_score = self._calculate_stability_score(backtest_results)
            
            # Robustness score (performance across different market conditions)
            robustness_score = self._calculate_robustness_score(backtest_results, data)
            
            # Overall score (weighted combination of metrics)
            overall_score = self._calculate_overall_score(
                backtest_results.sharpe_ratio,
                backtest_results.max_drawdown_pct,
                backtest_results.win_rate,
                stability_score,
                robustness_score
            )
            
            return StrategyMetrics(
                strategy_name=strategy_name,
                total_return=total_return,
                annual_return=annual_return,
                volatility=volatility,
                sharpe_ratio=backtest_results.sharpe_ratio,
                sortino_ratio=backtest_results.sortino_ratio,
                max_drawdown=backtest_results.max_drawdown_pct,
                win_rate=backtest_results.win_rate,
                profit_factor=backtest_results.profit_factor,
                total_trades=backtest_results.total_trades,
                avg_trade_duration=backtest_results.avg_trade_duration,
                calmar_ratio=backtest_results.calmar_ratio,
                var_95=backtest_results.var_95,
                cvar_95=backtest_results.cvar_95,
                expectancy=backtest_results.expectancy,
                stability_score=stability_score,
                robustness_score=robustness_score,
                overall_score=overall_score
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics for {strategy_name}: {e}")
            return StrategyMetrics(
                strategy_name=strategy_name,
                total_return=0, annual_return=0, volatility=0,
                sharpe_ratio=0, sortino_ratio=0, max_drawdown=0,
                win_rate=0, profit_factor=0, total_trades=0,
                avg_trade_duration=0, calmar_ratio=0,
                var_95=0, cvar_95=0, expectancy=0,
                stability_score=0, robustness_score=0, overall_score=0
            )
    
    def _calculate_stability_score(self, backtest_results: BacktestResults) -> float:
        """Calculate strategy stability score"""
        try:
            if backtest_results.monthly_returns.empty:
                return 0.0
            
            # Measure consistency of monthly returns
            monthly_returns = backtest_results.monthly_returns
            
            # Coefficient of variation (lower is better)
            if monthly_returns.mean() != 0:
                cv = abs(monthly_returns.std() / monthly_returns.mean())
                stability = max(0, 1 - cv)  # Convert to 0-1 scale
            else:
                stability = 0
            
            # Adjust for number of positive months
            positive_months = (monthly_returns > 0).sum()
            total_months = len(monthly_returns)
            
            if total_months > 0:
                consistency_bonus = positive_months / total_months
                stability = (stability + consistency_bonus) / 2
            
            return min(1.0, max(0.0, stability))
            
        except Exception as e:
            self.logger.error(f"Error calculating stability score: {e}")
            return 0.0
    
    def _calculate_robustness_score(self, backtest_results: BacktestResults, 
                                  data: pd.DataFrame) -> float:
        """Calculate strategy robustness score"""
        try:
            if backtest_results.equity_curve.empty or len(data) < 100:
                return 0.0
            
            # Split data into different market regimes
            returns = data['close'].pct_change().dropna()
            
            # Identify trending vs ranging markets
            rolling_std = returns.rolling(20).std()
            high_vol_periods = rolling_std > rolling_std.quantile(0.7)
            low_vol_periods = rolling_std < rolling_std.quantile(0.3)
            
            # Calculate performance in different regimes
            equity_returns = backtest_results.equity_curve.pct_change().dropna()
            
            scores = []
            
            # Performance in high volatility periods
            if high_vol_periods.any():
                high_vol_performance = equity_returns[high_vol_periods].mean()
                scores.append(max(0, min(1, (high_vol_performance + 0.001) * 1000)))
            
            # Performance in low volatility periods
            if low_vol_periods.any():
                low_vol_performance = equity_returns[low_vol_periods].mean()
                scores.append(max(0, min(1, (low_vol_performance + 0.001) * 1000)))
            
            # Overall consistency
            if len(equity_returns) > 0:
                consistency = 1 - (equity_returns.std() / (abs(equity_returns.mean()) + 0.001))
                scores.append(max(0, min(1, consistency)))
            
            return np.mean(scores) if scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating robustness score: {e}")
            return 0.0
    
    def _calculate_overall_score(self, sharpe_ratio: float, max_drawdown: float,
                               win_rate: float, stability: float, robustness: float) -> float:
        """Calculate overall strategy score"""
        try:
            # Normalize metrics to 0-1 scale
            sharpe_score = max(0, min(1, (sharpe_ratio + 2) / 4))  # -2 to 2 range
            drawdown_score = max(0, 1 + max_drawdown)  # Drawdown is negative
            win_rate_score = win_rate
            
            # Weighted combination
            weights = {
                'sharpe': 0.25,
                'drawdown': 0.25,
                'win_rate': 0.15,
                'stability': 0.20,
                'robustness': 0.15
            }
            
            overall_score = (
                weights['sharpe'] * sharpe_score +
                weights['drawdown'] * drawdown_score +
                weights['win_rate'] * win_rate_score +
                weights['stability'] * stability +
                weights['robustness'] * robustness
            )
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    def _rank_strategies(self, strategy_metrics: List[StrategyMetrics]) -> List[Tuple[str, float]]:
        """Rank strategies by overall score"""
        try:
            rankings = [(metrics.strategy_name, metrics.overall_score) 
                       for metrics in strategy_metrics]
            rankings.sort(key=lambda x: x[1], reverse=True)
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error ranking strategies: {e}")
            return []
    
    def _calculate_correlation_matrix(self, strategy_returns: Dict[str, pd.Series]) -> pd.DataFrame:
        """Calculate correlation matrix between strategies"""
        try:
            # Align all return series
            aligned_returns = pd.DataFrame(strategy_returns)
            correlation_matrix = aligned_returns.corr()
            return correlation_matrix
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation matrix: {e}")
            return pd.DataFrame()
    
    def _calculate_ensemble_weights(self, strategy_metrics: List[StrategyMetrics]) -> Dict[str, float]:
        """Calculate optimal ensemble weights using inverse variance weighting"""
        try:
            if not strategy_metrics:
                return {}
            
            # Use inverse of volatility as weights (lower volatility = higher weight)
            weights = {}
            total_inv_vol = 0
            
            for metrics in strategy_metrics:
                if metrics.volatility > 0:
                    inv_vol = 1 / metrics.volatility
                    weights[metrics.strategy_name] = inv_vol
                    total_inv_vol += inv_vol
                else:
                    weights[metrics.strategy_name] = 0
            
            # Normalize weights
            if total_inv_vol > 0:
                for strategy_name in weights:
                    weights[strategy_name] /= total_inv_vol
            
            # Apply performance adjustment
            for metrics in strategy_metrics:
                if metrics.strategy_name in weights:
                    performance_multiplier = max(0.1, metrics.overall_score)
                    weights[metrics.strategy_name] *= performance_multiplier
            
            # Renormalize
            total_weight = sum(weights.values())
            if total_weight > 0:
                for strategy_name in weights:
                    weights[strategy_name] /= total_weight
            
            return weights
            
        except Exception as e:
            self.logger.error(f"Error calculating ensemble weights: {e}")
            return {}
    
    def generate_validation_report(self, results: ValidationResults, 
                                 save_path: Optional[str] = None) -> str:
        """Generate comprehensive validation report"""
        try:
            report = []
            report.append("=" * 80)
            report.append("FOREX TRADING BOT - STRATEGY VALIDATION REPORT")
            report.append("=" * 80)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Strategies Evaluated: {len(results.strategy_metrics)}")
            report.append("")
            
            # Strategy Rankings
            report.append("STRATEGY RANKINGS")
            report.append("-" * 50)
            for i, (strategy_name, score) in enumerate(results.strategy_rankings, 1):
                report.append(f"{i:2d}. {strategy_name:<25} Score: {score:.3f}")
            report.append("")
            
            # Best Strategy Details
            if results.best_strategy:
                best_metrics = next(
                    (m for m in results.strategy_metrics if m.strategy_name == results.best_strategy),
                    None
                )
                
                if best_metrics:
                    report.append(f"BEST STRATEGY: {results.best_strategy}")
                    report.append("-" * 50)
                    report.append(f"Total Return: {best_metrics.total_return:.2%}")
                    report.append(f"Sharpe Ratio: {best_metrics.sharpe_ratio:.3f}")
                    report.append(f"Max Drawdown: {best_metrics.max_drawdown:.2%}")
                    report.append(f"Win Rate: {best_metrics.win_rate:.2%}")
                    report.append(f"Profit Factor: {best_metrics.profit_factor:.3f}")
                    report.append(f"Total Trades: {best_metrics.total_trades}")
                    report.append(f"Stability Score: {best_metrics.stability_score:.3f}")
                    report.append(f"Robustness Score: {best_metrics.robustness_score:.3f}")
                    report.append("")
            
            # Detailed Strategy Comparison
            report.append("DETAILED STRATEGY COMPARISON")
            report.append("-" * 80)
            report.append(f"{'Strategy':<20} {'Return':<8} {'Sharpe':<8} {'Drawdown':<10} {'Win Rate':<9} {'Score':<8}")
            report.append("-" * 80)
            
            for metrics in sorted(results.strategy_metrics, 
                                key=lambda x: x.overall_score, reverse=True):
                report.append(
                    f"{metrics.strategy_name:<20} "
                    f"{metrics.total_return:>7.2%} "
                    f"{metrics.sharpe_ratio:>7.3f} "
                    f"{metrics.max_drawdown:>9.2%} "
                    f"{metrics.win_rate:>8.2%} "
                    f"{metrics.overall_score:>7.3f}"
                )
            report.append("")
            
            # Ensemble Weights
            if results.ensemble_weights:
                report.append("ENSEMBLE PORTFOLIO WEIGHTS")
                report.append("-" * 40)
                for strategy_name, weight in sorted(results.ensemble_weights.items(), 
                                                  key=lambda x: x[1], reverse=True):
                    report.append(f"{strategy_name:<25} {weight:>6.1%}")
                report.append("")
            
            # Correlation Analysis
            if results.correlation_matrix is not None and not results.correlation_matrix.empty:
                report.append("STRATEGY CORRELATION MATRIX")
                report.append("-" * 50)
                
                # Show correlation matrix
                corr_str = results.correlation_matrix.round(3).to_string()
                report.append(corr_str)
                report.append("")
                
                # Highlight highly correlated strategies
                high_corr_pairs = []
                for i in range(len(results.correlation_matrix.columns)):
                    for j in range(i+1, len(results.correlation_matrix.columns)):
                        corr_val = results.correlation_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:
                            strategy1 = results.correlation_matrix.columns[i]
                            strategy2 = results.correlation_matrix.columns[j]
                            high_corr_pairs.append((strategy1, strategy2, corr_val))
                
                if high_corr_pairs:
                    report.append("HIGH CORRELATION PAIRS (>0.7):")
                    for s1, s2, corr in high_corr_pairs:
                        report.append(f"  {s1} - {s2}: {corr:.3f}")
                    report.append("")
            
            # Recommendations
            report.append("RECOMMENDATIONS")
            report.append("-" * 40)
            
            if results.best_strategy:
                report.append(f"1. Primary Strategy: Use {results.best_strategy} as main trading strategy")
            
            if results.ensemble_weights:
                top_strategies = sorted(results.ensemble_weights.items(), 
                                      key=lambda x: x[1], reverse=True)[:3]
                strategy_names = [s[0] for s in top_strategies]
                report.append(f"2. Ensemble Approach: Combine {', '.join(strategy_names)}")
            
            # Risk warnings
            worst_drawdown = min((m.max_drawdown for m in results.strategy_metrics), default=0)
            if worst_drawdown < -0.2:
                report.append(f"3. Risk Warning: Maximum drawdown of {worst_drawdown:.1%} detected")
            
            avg_sharpe = np.mean([m.sharpe_ratio for m in results.strategy_metrics])
            if avg_sharpe < 0.5:
                report.append(f"4. Performance Warning: Average Sharpe ratio is {avg_sharpe:.2f}")
            
            report.append("")
            report.append("Note: Past performance does not guarantee future results.")
            report.append("Always use proper risk management and position sizing.")
            
            report_text = "\n".join(report)
            
            if save_path:
                with open(save_path, 'w') as f:
                    f.write(report_text)
                self.logger.info(f"Validation report saved to {save_path}")
            
            return report_text
            
        except Exception as e:
            self.logger.error(f"Error generating validation report: {e}")
            return "Error generating validation report"
    
    def get_strategy_recommendation(self, results: ValidationResults, 
                                  risk_tolerance: str = 'medium') -> Dict:
        """Get strategy recommendation based on risk tolerance"""
        try:
            if not results.strategy_metrics:
                return {'recommendation': 'No strategies available'}
            
            recommendations = {}
            
            if risk_tolerance.lower() == 'low':
                # Prioritize low drawdown and stability
                best_strategy = min(results.strategy_metrics, 
                                  key=lambda x: abs(x.max_drawdown))
                recommendations['primary'] = best_strategy.strategy_name
                recommendations['reason'] = 'Lowest maximum drawdown'
                
            elif risk_tolerance.lower() == 'high':
                # Prioritize high returns
                best_strategy = max(results.strategy_metrics, 
                                  key=lambda x: x.total_return)
                recommendations['primary'] = best_strategy.strategy_name
                recommendations['reason'] = 'Highest total return'
                
            else:  # medium risk
                # Use overall score
                best_strategy = max(results.strategy_metrics, 
                                  key=lambda x: x.overall_score)
                recommendations['primary'] = best_strategy.strategy_name
                recommendations['reason'] = 'Best overall score'
            
            # Ensemble recommendation
            if results.ensemble_weights:
                top_3_strategies = sorted(results.ensemble_weights.items(), 
                                        key=lambda x: x[1], reverse=True)[:3]
                recommendations['ensemble'] = {
                    'strategies': top_3_strategies,
                    'reason': 'Diversified portfolio approach'
                }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting strategy recommendation: {e}")
            return {'recommendation': 'Error generating recommendation'}

# Example usage and testing
def test_strategy_validator():
    """Test the strategy validator"""
    from backtesting.backtest_engine import simple_ma_crossover_strategy, rsi_mean_reversion_strategy
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    
    returns = np.random.normal(0, 0.001, len(dates))
    prices = 1.1000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices + np.random.normal(0, 0.0001, len(dates)),
        'high': prices + np.abs(np.random.normal(0, 0.0002, len(dates))),
        'low': prices - np.abs(np.random.normal(0, 0.0002, len(dates))),
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    
    # Ensure OHLC consistency
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    # Initialize validator
    validator = StrategyValidator(initial_capital=10000)
    
    # Register strategies
    validator.register_strategy(
        'MA_Crossover_Fast', 
        simple_ma_crossover_strategy,
        {'fast_ma': 5, 'slow_ma': 20}
    )
    
    validator.register_strategy(
        'MA_Crossover_Slow', 
        simple_ma_crossover_strategy,
        {'fast_ma': 10, 'slow_ma': 50}
    )
    
    validator.register_strategy(
        'RSI_Mean_Reversion', 
        rsi_mean_reversion_strategy,
        {'rsi_period': 14, 'oversold': 30, 'overbought': 70}
    )
    
    # Run validation
    print("Running strategy validation...")
    results = validator.validate_strategies(data, walk_forward=False)
    
    # Generate report
    report = validator.generate_validation_report(results)
    print(report)
    
    # Get recommendations
    recommendations = validator.get_strategy_recommendation(results, 'medium')
    print("\nRECOMMENDATIONS:")
    print(f"Primary Strategy: {recommendations.get('primary', 'None')}")
    print(f"Reason: {recommendations.get('reason', 'N/A')}")

if __name__ == "__main__":
    test_strategy_validator()

