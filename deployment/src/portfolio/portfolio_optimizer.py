"""
Portfolio Optimization System for Forex Trading Bot
Implements advanced portfolio optimization techniques for maximum risk-adjusted returns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

@dataclass
class OptimizationResult:
    """Result of portfolio optimization"""
    optimal_weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    max_drawdown_estimate: float
    optimization_method: str
    confidence_score: float

class PortfolioOptimizer:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger('PortfolioOptimizer')
        
        # Optimization parameters
        self.lookback_period = self.config.get('LOOKBACK_PERIOD', 252)  # 1 year
        self.rebalance_frequency = self.config.get('REBALANCE_FREQUENCY', 7)  # Weekly
        self.risk_free_rate = self.config.get('RISK_FREE_RATE', 0.02)  # 2% annual
        self.max_position_weight = self.config.get('MAX_POSITION_WEIGHT', 0.3)  # 30% max per position
        self.min_position_weight = self.config.get('MIN_POSITION_WEIGHT', 0.05)  # 5% min per position
        
        # Historical data storage
        self.price_history = {}
        self.return_history = {}
        self.correlation_matrix = None
        self.covariance_matrix = None
        
        # Optimization results
        self.current_weights = {}
        self.last_optimization = None
        self.optimization_history = []
        
        self.logger.info("Portfolio Optimizer initialized")
    
    def update_price_data(self, symbol: str, prices: pd.Series):
        """Update price history for a symbol"""
        try:
            # Store price data
            self.price_history[symbol] = prices.tail(self.lookback_period)
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            self.return_history[symbol] = returns.tail(self.lookback_period)
            
            # Update correlation and covariance matrices
            self._update_correlation_matrices()
            
        except Exception as e:
            self.logger.error(f"Error updating price data for {symbol}: {e}")
    
    def _update_correlation_matrices(self):
        """Update correlation and covariance matrices"""
        try:
            if len(self.return_history) < 2:
                return
            
            # Create returns dataframe
            returns_df = pd.DataFrame(self.return_history)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 30:  # Need minimum data
                return
            
            # Calculate correlation and covariance matrices
            self.correlation_matrix = returns_df.corr()
            self.covariance_matrix = returns_df.cov()
            
        except Exception as e:
            self.logger.error(f"Error updating correlation matrices: {e}")
    
    def optimize_portfolio(self, available_symbols: List[str], 
                         signal_strengths: Dict[str, float],
                         current_positions: Dict[str, float],
                         optimization_method: str = 'sharpe') -> OptimizationResult:
        """Optimize portfolio allocation"""
        try:
            # Filter symbols with sufficient data
            valid_symbols = [
                symbol for symbol in available_symbols 
                if symbol in self.return_history and len(self.return_history[symbol]) >= 30
            ]
            
            if len(valid_symbols) < 2:
                self.logger.warning("Insufficient data for portfolio optimization")
                return self._create_equal_weight_portfolio(available_symbols, signal_strengths)
            
            # Prepare optimization data
            returns_data = self._prepare_optimization_data(valid_symbols)
            
            if returns_data is None:
                return self._create_equal_weight_portfolio(available_symbols, signal_strengths)
            
            # Perform optimization based on method
            if optimization_method == 'sharpe':
                result = self._optimize_sharpe_ratio(returns_data, signal_strengths)
            elif optimization_method == 'min_variance':
                result = self._optimize_minimum_variance(returns_data, signal_strengths)
            elif optimization_method == 'risk_parity':
                result = self._optimize_risk_parity(returns_data, signal_strengths)
            elif optimization_method == 'black_litterman':
                result = self._optimize_black_litterman(returns_data, signal_strengths, current_positions)
            else:
                result = self._optimize_sharpe_ratio(returns_data, signal_strengths)
            
            # Update current weights
            self.current_weights = result.optimal_weights
            self.last_optimization = datetime.now()
            self.optimization_history.append(result)
            
            # Keep only last 100 optimizations
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
            
            self.logger.info(f"Portfolio optimized using {optimization_method} method")
            return result
            
        except Exception as e:
            self.logger.error(f"Error optimizing portfolio: {e}")
            return self._create_equal_weight_portfolio(available_symbols, signal_strengths)
    
    def _prepare_optimization_data(self, symbols: List[str]) -> Optional[pd.DataFrame]:
        """Prepare data for optimization"""
        try:
            returns_data = pd.DataFrame()
            
            for symbol in symbols:
                if symbol in self.return_history:
                    returns_data[symbol] = self.return_history[symbol]
            
            # Align data and remove NaN
            returns_data = returns_data.dropna()
            
            if len(returns_data) < 30:
                return None
            
            return returns_data
            
        except Exception as e:
            self.logger.error(f"Error preparing optimization data: {e}")
            return None
    
    def _optimize_sharpe_ratio(self, returns_data: pd.DataFrame, 
                             signal_strengths: Dict[str, float]) -> OptimizationResult:
        """Optimize portfolio for maximum Sharpe ratio"""
        try:
            symbols = returns_data.columns.tolist()
            n_assets = len(symbols)
            
            # Calculate expected returns and covariance
            expected_returns = returns_data.mean() * 252  # Annualized
            cov_matrix = returns_data.cov() * 252  # Annualized
            
            # Incorporate signal strengths
            for symbol in symbols:
                if symbol in signal_strengths:
                    # Boost expected return based on signal strength
                    boost = (signal_strengths[symbol] / 100 - 0.5) * 0.1  # Max 5% boost
                    expected_returns[symbol] += boost
            
            # Objective function (negative Sharpe ratio)
            def objective(weights):
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                if portfolio_volatility == 0:
                    return -np.inf
                
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe_ratio  # Negative because we minimize
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            # Bounds
            bounds = [(self.min_position_weight, self.max_position_weight) for _ in range(n_assets)]
            
            # Initial guess (equal weights)
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, initial_weights, method='SLSQP',
                bounds=bounds, constraints=constraints,
                options={'maxiter': 1000}
            )
            
            if result.success:
                optimal_weights = dict(zip(symbols, result.x))
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(result.x * expected_returns)
                portfolio_volatility = np.sqrt(np.dot(result.x.T, np.dot(cov_matrix, result.x)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                
                # Estimate max drawdown (simplified)
                max_drawdown_estimate = portfolio_volatility * 2.5  # Rough estimate
                
                return OptimizationResult(
                    optimal_weights=optimal_weights,
                    expected_return=portfolio_return,
                    expected_volatility=portfolio_volatility,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown_estimate=max_drawdown_estimate,
                    optimization_method='sharpe',
                    confidence_score=85.0
                )
            else:
                raise Exception("Optimization failed to converge")
                
        except Exception as e:
            self.logger.error(f"Error in Sharpe ratio optimization: {e}")
            return self._create_equal_weight_portfolio(symbols, signal_strengths)
    
    def _optimize_minimum_variance(self, returns_data: pd.DataFrame,
                                 signal_strengths: Dict[str, float]) -> OptimizationResult:
        """Optimize portfolio for minimum variance"""
        try:
            symbols = returns_data.columns.tolist()
            n_assets = len(symbols)
            
            # Calculate covariance matrix
            cov_matrix = returns_data.cov() * 252  # Annualized
            
            # Objective function (portfolio variance)
            def objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            # Bounds
            bounds = [(self.min_position_weight, self.max_position_weight) for _ in range(n_assets)]
            
            # Initial guess
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, initial_weights, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if result.success:
                optimal_weights = dict(zip(symbols, result.x))
                
                # Calculate portfolio metrics
                expected_returns = returns_data.mean() * 252
                portfolio_return = np.sum(result.x * expected_returns)
                portfolio_volatility = np.sqrt(result.fun)
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                
                return OptimizationResult(
                    optimal_weights=optimal_weights,
                    expected_return=portfolio_return,
                    expected_volatility=portfolio_volatility,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown_estimate=portfolio_volatility * 2.0,
                    optimization_method='min_variance',
                    confidence_score=80.0
                )
            else:
                raise Exception("Minimum variance optimization failed")
                
        except Exception as e:
            self.logger.error(f"Error in minimum variance optimization: {e}")
            return self._create_equal_weight_portfolio(symbols, signal_strengths)
    
    def _optimize_risk_parity(self, returns_data: pd.DataFrame,
                            signal_strengths: Dict[str, float]) -> OptimizationResult:
        """Optimize portfolio using risk parity approach"""
        try:
            symbols = returns_data.columns.tolist()
            n_assets = len(symbols)
            
            # Calculate covariance matrix
            cov_matrix = returns_data.cov() * 252
            
            # Risk parity objective function
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                marginal_contrib = np.dot(cov_matrix, weights)
                contrib = weights * marginal_contrib / portfolio_variance
                
                # Minimize sum of squared deviations from equal risk contribution
                target_contrib = 1.0 / n_assets
                return np.sum((contrib - target_contrib) ** 2)
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            ]
            
            # Bounds
            bounds = [(self.min_position_weight, self.max_position_weight) for _ in range(n_assets)]
            
            # Initial guess
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, initial_weights, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if result.success:
                optimal_weights = dict(zip(symbols, result.x))
                
                # Calculate portfolio metrics
                expected_returns = returns_data.mean() * 252
                portfolio_return = np.sum(result.x * expected_returns)
                portfolio_volatility = np.sqrt(np.dot(result.x.T, np.dot(cov_matrix, result.x)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                
                return OptimizationResult(
                    optimal_weights=optimal_weights,
                    expected_return=portfolio_return,
                    expected_volatility=portfolio_volatility,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown_estimate=portfolio_volatility * 1.8,
                    optimization_method='risk_parity',
                    confidence_score=75.0
                )
            else:
                raise Exception("Risk parity optimization failed")
                
        except Exception as e:
            self.logger.error(f"Error in risk parity optimization: {e}")
            return self._create_equal_weight_portfolio(symbols, signal_strengths)
    
    def _optimize_black_litterman(self, returns_data: pd.DataFrame,
                                signal_strengths: Dict[str, float],
                                current_positions: Dict[str, float]) -> OptimizationResult:
        """Optimize using Black-Litterman model"""
        try:
            symbols = returns_data.columns.tolist()
            n_assets = len(symbols)
            
            # Market equilibrium returns (simplified)
            market_caps = {symbol: 1.0 for symbol in symbols}  # Equal market caps
            market_weights = np.array([market_caps[symbol] for symbol in symbols])
            market_weights = market_weights / np.sum(market_weights)
            
            # Calculate covariance matrix
            cov_matrix = returns_data.cov() * 252
            
            # Risk aversion parameter
            risk_aversion = 3.0
            
            # Implied equilibrium returns
            pi = risk_aversion * np.dot(cov_matrix, market_weights)
            
            # Views based on signal strengths
            views = []
            view_uncertainty = []
            
            for symbol in symbols:
                if symbol in signal_strengths and abs(signal_strengths[symbol] - 50) > 20:
                    # Strong signal - create view
                    view_return = (signal_strengths[symbol] / 100 - 0.5) * 0.2  # Max 10% view
                    views.append(view_return)
                    view_uncertainty.append(0.1)  # 10% uncertainty
                else:
                    views.append(0.0)
                    view_uncertainty.append(1.0)  # High uncertainty (no view)
            
            # View matrix (identity for absolute views)
            P = np.eye(n_assets)
            Q = np.array(views)
            Omega = np.diag(view_uncertainty)
            
            # Black-Litterman formula
            tau = 0.025  # Scaling factor
            
            M1 = np.linalg.inv(tau * cov_matrix)
            M2 = np.dot(P.T, np.dot(np.linalg.inv(Omega), P))
            M3 = np.dot(np.linalg.inv(tau * cov_matrix), pi)
            M4 = np.dot(P.T, np.dot(np.linalg.inv(Omega), Q))
            
            mu_bl = np.dot(np.linalg.inv(M1 + M2), M3 + M4)
            cov_bl = np.linalg.inv(M1 + M2)
            
            # Optimize with Black-Litterman inputs
            def objective(weights):
                portfolio_return = np.sum(weights * mu_bl)
                portfolio_variance = np.dot(weights.T, np.dot(cov_bl, weights))
                return -portfolio_return + 0.5 * risk_aversion * portfolio_variance
            
            # Constraints and bounds
            constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
            bounds = [(self.min_position_weight, self.max_position_weight) for _ in range(n_assets)]
            
            # Initial guess
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Optimize
            result = minimize(
                objective, initial_weights, method='SLSQP',
                bounds=bounds, constraints=constraints
            )
            
            if result.success:
                optimal_weights = dict(zip(symbols, result.x))
                
                # Calculate portfolio metrics
                portfolio_return = np.sum(result.x * mu_bl)
                portfolio_volatility = np.sqrt(np.dot(result.x.T, np.dot(cov_bl, result.x)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                
                return OptimizationResult(
                    optimal_weights=optimal_weights,
                    expected_return=portfolio_return,
                    expected_volatility=portfolio_volatility,
                    sharpe_ratio=sharpe_ratio,
                    max_drawdown_estimate=portfolio_volatility * 2.2,
                    optimization_method='black_litterman',
                    confidence_score=90.0
                )
            else:
                raise Exception("Black-Litterman optimization failed")
                
        except Exception as e:
            self.logger.error(f"Error in Black-Litterman optimization: {e}")
            return self._create_equal_weight_portfolio(symbols, signal_strengths)
    
    def _create_equal_weight_portfolio(self, symbols: List[str],
                                     signal_strengths: Dict[str, float]) -> OptimizationResult:
        """Create equal weight portfolio as fallback"""
        n_assets = len(symbols)
        weight = 1.0 / n_assets if n_assets > 0 else 0.0
        
        optimal_weights = {symbol: weight for symbol in symbols}
        
        return OptimizationResult(
            optimal_weights=optimal_weights,
            expected_return=0.08,  # Assumed 8% return
            expected_volatility=0.15,  # Assumed 15% volatility
            sharpe_ratio=0.4,  # Assumed Sharpe ratio
            max_drawdown_estimate=0.20,  # Assumed 20% max drawdown
            optimization_method='equal_weight',
            confidence_score=50.0
        )
    
    def calculate_rebalancing_trades(self, current_positions: Dict[str, float],
                                   target_weights: Dict[str, float],
                                   account_value: float,
                                   min_trade_size: float = 100) -> Dict[str, float]:
        """Calculate trades needed to rebalance portfolio"""
        try:
            rebalancing_trades = {}
            
            # Calculate current weights
            total_position_value = sum(current_positions.values())
            current_weights = {}
            
            if total_position_value > 0:
                for symbol, value in current_positions.items():
                    current_weights[symbol] = value / total_position_value
            
            # Calculate required trades
            for symbol, target_weight in target_weights.items():
                current_weight = current_weights.get(symbol, 0.0)
                weight_diff = target_weight - current_weight
                
                # Convert to dollar amount
                trade_amount = weight_diff * account_value
                
                # Only trade if above minimum size
                if abs(trade_amount) >= min_trade_size:
                    rebalancing_trades[symbol] = trade_amount
            
            return rebalancing_trades
            
        except Exception as e:
            self.logger.error(f"Error calculating rebalancing trades: {e}")
            return {}
    
    def should_rebalance(self, current_positions: Dict[str, float],
                        target_weights: Dict[str, float],
                        threshold: float = 0.05) -> bool:
        """Determine if portfolio should be rebalanced"""
        try:
            # Check if enough time has passed
            if self.last_optimization:
                time_since_last = datetime.now() - self.last_optimization
                if time_since_last.days < self.rebalance_frequency:
                    return False
            
            # Calculate current weights
            total_value = sum(current_positions.values())
            if total_value == 0:
                return True
            
            current_weights = {
                symbol: value / total_value 
                for symbol, value in current_positions.items()
            }
            
            # Check weight deviations
            for symbol, target_weight in target_weights.items():
                current_weight = current_weights.get(symbol, 0.0)
                deviation = abs(target_weight - current_weight)
                
                if deviation > threshold:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking rebalancing need: {e}")
            return False
    
    def get_optimization_report(self) -> Dict:
        """Generate optimization report"""
        try:
            if not self.optimization_history:
                return {'status': 'No optimization history available'}
            
            latest_optimization = self.optimization_history[-1]
            
            # Calculate performance metrics
            if len(self.optimization_history) > 1:
                returns = []
                for i in range(1, len(self.optimization_history)):
                    prev_sharpe = self.optimization_history[i-1].sharpe_ratio
                    curr_sharpe = self.optimization_history[i].sharpe_ratio
                    returns.append(curr_sharpe - prev_sharpe)
                
                avg_improvement = np.mean(returns) if returns else 0
                volatility_improvement = np.std(returns) if returns else 0
            else:
                avg_improvement = 0
                volatility_improvement = 0
            
            return {
                'timestamp': datetime.now().isoformat(),
                'latest_optimization': {
                    'method': latest_optimization.optimization_method,
                    'expected_return': latest_optimization.expected_return,
                    'expected_volatility': latest_optimization.expected_volatility,
                    'sharpe_ratio': latest_optimization.sharpe_ratio,
                    'max_drawdown_estimate': latest_optimization.max_drawdown_estimate,
                    'confidence_score': latest_optimization.confidence_score,
                    'optimal_weights': latest_optimization.optimal_weights
                },
                'optimization_history': {
                    'total_optimizations': len(self.optimization_history),
                    'avg_sharpe_improvement': avg_improvement,
                    'volatility_of_improvement': volatility_improvement
                },
                'current_weights': self.current_weights,
                'last_optimization_time': self.last_optimization.isoformat() if self.last_optimization else None
            }
            
        except Exception as e:
            self.logger.error(f"Error generating optimization report: {e}")
            return {'status': f'Error: {e}'}

# Example usage and testing
if __name__ == "__main__":
    # Test portfolio optimizer
    optimizer = PortfolioOptimizer()
    
    # Generate sample price data
    np.random.seed(42)
    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']
    
    for symbol in symbols:
        # Generate realistic price series
        returns = np.random.normal(0.0001, 0.01, 252)  # Daily returns
        prices = 100 * np.exp(np.cumsum(returns))  # Price series
        price_series = pd.Series(prices, index=pd.date_range('2023-01-01', periods=252))
        
        optimizer.update_price_data(symbol, price_series)
    
    # Test optimization
    signal_strengths = {'EURUSD': 75, 'GBPUSD': 60, 'USDJPY': 80, 'AUDUSD': 55}
    current_positions = {'EURUSD': 2500, 'GBPUSD': 2000, 'USDJPY': 3000, 'AUDUSD': 2500}
    
    result = optimizer.optimize_portfolio(symbols, signal_strengths, current_positions, 'sharpe')
    
    print("Optimization Result:")
    print(f"Method: {result.optimization_method}")
    print(f"Expected Return: {result.expected_return:.4f}")
    print(f"Expected Volatility: {result.expected_volatility:.4f}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.4f}")
    print(f"Optimal Weights: {result.optimal_weights}")
    
    # Test rebalancing
    rebalancing_trades = optimizer.calculate_rebalancing_trades(
        current_positions, result.optimal_weights, 10000
    )
    print(f"\nRebalancing Trades: {rebalancing_trades}")
    
    # Generate report
    report = optimizer.get_optimization_report()
    print(f"\nOptimization Report: {report}")

