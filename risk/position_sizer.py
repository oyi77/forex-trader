"""
Advanced Position Sizing System for Forex Trading Bot
Implements multiple position sizing algorithms for optimal risk management
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import math

class SizingMethod(Enum):
    FIXED_PERCENTAGE = "fixed_percentage"
    KELLY_CRITERION = "kelly_criterion"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    RISK_PARITY = "risk_parity"
    OPTIMAL_F = "optimal_f"
    ADAPTIVE = "adaptive"

@dataclass
class PositionSizeResult:
    """Result of position sizing calculation"""
    position_size: float
    risk_amount: float
    risk_percentage: float
    sizing_method: str
    confidence_score: float
    max_position_value: float
    leverage_used: float
    reasoning: str

class AdvancedPositionSizer:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger('AdvancedPositionSizer')
        
        # Position sizing parameters
        self.base_risk_per_trade = self.config.get('BASE_RISK_PER_TRADE', 0.01)  # 1%
        self.max_risk_per_trade = self.config.get('MAX_RISK_PER_TRADE', 0.03)  # 3%
        self.min_risk_per_trade = self.config.get('MIN_RISK_PER_TRADE', 0.005)  # 0.5%
        self.max_leverage = self.config.get('MAX_LEVERAGE', 10.0)
        self.kelly_multiplier = self.config.get('KELLY_MULTIPLIER', 0.25)  # Conservative Kelly
        
        # Historical performance tracking
        self.trade_history = []
        self.win_rate = 0.5  # Default 50%
        self.avg_win = 0.02  # Default 2%
        self.avg_loss = 0.01  # Default 1%
        self.consecutive_losses = 0
        self.max_consecutive_losses = 0
        
        # Volatility estimates
        self.volatility_estimates = {
            'EURUSD': 0.007, 'GBPUSD': 0.009, 'USDJPY': 0.008,
            'AUDUSD': 0.010, 'USDCHF': 0.008, 'NZDUSD': 0.011,
            'USDCAD': 0.007, 'EURJPY': 0.012, 'GBPJPY': 0.015
        }
        
        self.logger.info("Advanced Position Sizer initialized")
    
    def calculate_position_size(self, signal: Dict, account_balance: float,
                              current_positions: Dict, method: SizingMethod = SizingMethod.ADAPTIVE) -> PositionSizeResult:
        """Calculate optimal position size using specified method"""
        try:
            # Extract signal information
            symbol = signal.get('symbol', '')
            entry_price = signal.get('entry_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            confidence = signal.get('confidence_score', 50)
            risk_reward_ratio = signal.get('risk_reward_ratio', 1.0)
            
            # Calculate risk per unit
            risk_per_unit = abs(entry_price - stop_loss)
            if risk_per_unit == 0:
                return self._create_zero_position_result("Zero risk per unit")
            
            # Apply sizing method
            if method == SizingMethod.FIXED_PERCENTAGE:
                result = self._fixed_percentage_sizing(
                    account_balance, risk_per_unit, confidence
                )
            elif method == SizingMethod.KELLY_CRITERION:
                result = self._kelly_criterion_sizing(
                    account_balance, risk_per_unit, confidence, risk_reward_ratio
                )
            elif method == SizingMethod.VOLATILITY_ADJUSTED:
                result = self._volatility_adjusted_sizing(
                    symbol, account_balance, risk_per_unit, confidence
                )
            elif method == SizingMethod.RISK_PARITY:
                result = self._risk_parity_sizing(
                    symbol, account_balance, risk_per_unit, current_positions
                )
            elif method == SizingMethod.OPTIMAL_F:
                result = self._optimal_f_sizing(
                    account_balance, risk_per_unit, confidence
                )
            elif method == SizingMethod.ADAPTIVE:
                result = self._adaptive_sizing(
                    signal, account_balance, risk_per_unit, current_positions
                )
            else:
                result = self._fixed_percentage_sizing(
                    account_balance, risk_per_unit, confidence
                )
            
            # Apply final validations and adjustments
            result = self._apply_final_adjustments(result, signal, account_balance, current_positions)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return self._create_zero_position_result(f"Calculation error: {e}")
    
    def _fixed_percentage_sizing(self, account_balance: float, risk_per_unit: float,
                               confidence: float) -> PositionSizeResult:
        """Fixed percentage risk sizing"""
        # Adjust base risk based on confidence
        confidence_multiplier = confidence / 100
        adjusted_risk = self.base_risk_per_trade * confidence_multiplier
        
        # Ensure within limits
        adjusted_risk = max(self.min_risk_per_trade, min(adjusted_risk, self.max_risk_per_trade))
        
        # Calculate position size
        risk_amount = account_balance * adjusted_risk
        position_size = risk_amount / risk_per_unit
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=adjusted_risk,
            sizing_method="fixed_percentage",
            confidence_score=confidence,
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Fixed {adjusted_risk:.2%} risk based on {confidence:.1f}% confidence"
        )
    
    def _kelly_criterion_sizing(self, account_balance: float, risk_per_unit: float,
                              confidence: float, risk_reward_ratio: float) -> PositionSizeResult:
        """Kelly Criterion position sizing"""
        # Estimate win probability from confidence
        win_probability = confidence / 100
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds received (risk_reward_ratio), p = win probability, q = loss probability
        b = risk_reward_ratio
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Apply conservative multiplier and ensure positive
        kelly_fraction = max(0, kelly_fraction * self.kelly_multiplier)
        
        # Ensure within risk limits
        kelly_fraction = min(kelly_fraction, self.max_risk_per_trade)
        
        # Calculate position size
        risk_amount = account_balance * kelly_fraction
        position_size = risk_amount / risk_per_unit
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=kelly_fraction,
            sizing_method="kelly_criterion",
            confidence_score=confidence,
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Kelly fraction {kelly_fraction:.2%} (conservative multiplier applied)"
        )
    
    def _volatility_adjusted_sizing(self, symbol: str, account_balance: float,
                                  risk_per_unit: float, confidence: float) -> PositionSizeResult:
        """Volatility-adjusted position sizing"""
        # Get volatility estimate
        volatility = self.volatility_estimates.get(symbol, 0.01)
        
        # Base volatility for normalization (1% daily)
        base_volatility = 0.01
        
        # Adjust risk based on volatility (inverse relationship)
        volatility_adjustment = base_volatility / volatility
        
        # Apply confidence adjustment
        confidence_adjustment = confidence / 100
        
        # Calculate adjusted risk
        adjusted_risk = self.base_risk_per_trade * volatility_adjustment * confidence_adjustment
        
        # Ensure within limits
        adjusted_risk = max(self.min_risk_per_trade, min(adjusted_risk, self.max_risk_per_trade))
        
        # Calculate position size
        risk_amount = account_balance * adjusted_risk
        position_size = risk_amount / risk_per_unit
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=adjusted_risk,
            sizing_method="volatility_adjusted",
            confidence_score=confidence,
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Volatility-adjusted risk {adjusted_risk:.2%} (vol: {volatility:.3f})"
        )
    
    def _risk_parity_sizing(self, symbol: str, account_balance: float,
                          risk_per_unit: float, current_positions: Dict) -> PositionSizeResult:
        """Risk parity position sizing"""
        # Calculate current portfolio risk
        total_current_risk = 0
        position_count = len(current_positions)
        
        for position in current_positions.values():
            pos_risk = position.get('risk_amount', 0)
            total_current_risk += pos_risk
        
        # Target equal risk contribution
        max_positions = self.config.get('MAX_POSITIONS', 5)
        target_risk_per_position = account_balance * self.base_risk_per_trade
        
        # Adjust for current portfolio heat
        if position_count > 0:
            avg_current_risk = total_current_risk / position_count
            target_risk_per_position = min(target_risk_per_position, avg_current_risk)
        
        # Calculate position size
        position_size = target_risk_per_position / risk_per_unit
        risk_percentage = target_risk_per_position / account_balance
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=target_risk_per_position,
            risk_percentage=risk_percentage,
            sizing_method="risk_parity",
            confidence_score=75.0,  # Default confidence for risk parity
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Risk parity: equal {risk_percentage:.2%} risk per position"
        )
    
    def _optimal_f_sizing(self, account_balance: float, risk_per_unit: float,
                        confidence: float) -> PositionSizeResult:
        """Optimal F position sizing (simplified)"""
        # Use historical performance if available
        if len(self.trade_history) > 10:
            returns = [trade.get('return_pct', 0) for trade in self.trade_history[-50:]]
            
            # Calculate optimal f using simplified method
            # Optimal f = average return / largest loss
            avg_return = np.mean(returns)
            largest_loss = abs(min(returns)) if returns else 0.02
            
            optimal_f = avg_return / largest_loss if largest_loss > 0 else 0.01
            
            # Apply conservative factor
            optimal_f *= 0.5
        else:
            # Use confidence-based estimate
            optimal_f = (confidence / 100) * self.base_risk_per_trade
        
        # Ensure within limits
        optimal_f = max(self.min_risk_per_trade, min(optimal_f, self.max_risk_per_trade))
        
        # Calculate position size
        risk_amount = account_balance * optimal_f
        position_size = risk_amount / risk_per_unit
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=optimal_f,
            sizing_method="optimal_f",
            confidence_score=confidence,
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Optimal F: {optimal_f:.2%} based on historical performance"
        )
    
    def _adaptive_sizing(self, signal: Dict, account_balance: float,
                       risk_per_unit: float, current_positions: Dict) -> PositionSizeResult:
        """Adaptive position sizing combining multiple methods"""
        symbol = signal.get('symbol', '')
        confidence = signal.get('confidence_score', 50)
        risk_reward_ratio = signal.get('risk_reward_ratio', 1.0)
        
        # Calculate sizes using different methods
        fixed_result = self._fixed_percentage_sizing(account_balance, risk_per_unit, confidence)
        kelly_result = self._kelly_criterion_sizing(account_balance, risk_per_unit, confidence, risk_reward_ratio)
        vol_result = self._volatility_adjusted_sizing(symbol, account_balance, risk_per_unit, confidence)
        
        # Weight the methods based on market conditions and performance
        weights = self._calculate_method_weights(signal, current_positions)
        
        # Combine position sizes
        combined_risk = (
            fixed_result.risk_percentage * weights['fixed'] +
            kelly_result.risk_percentage * weights['kelly'] +
            vol_result.risk_percentage * weights['volatility']
        )
        
        # Apply drawdown adjustment
        drawdown_adjustment = self._calculate_drawdown_adjustment()
        combined_risk *= drawdown_adjustment
        
        # Ensure within limits
        combined_risk = max(self.min_risk_per_trade, min(combined_risk, self.max_risk_per_trade))
        
        # Calculate final position size
        risk_amount = account_balance * combined_risk
        position_size = risk_amount / risk_per_unit
        
        return PositionSizeResult(
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=combined_risk,
            sizing_method="adaptive",
            confidence_score=confidence,
            max_position_value=position_size * risk_per_unit,
            leverage_used=1.0,
            reasoning=f"Adaptive sizing: {combined_risk:.2%} risk (drawdown adj: {drawdown_adjustment:.2f})"
        )
    
    def _calculate_method_weights(self, signal: Dict, current_positions: Dict) -> Dict[str, float]:
        """Calculate weights for different sizing methods"""
        confidence = signal.get('confidence_score', 50)
        risk_reward_ratio = signal.get('risk_reward_ratio', 1.0)
        
        # Base weights
        weights = {'fixed': 0.4, 'kelly': 0.3, 'volatility': 0.3}
        
        # Adjust based on confidence
        if confidence > 80:
            weights['kelly'] += 0.2
            weights['fixed'] -= 0.1
            weights['volatility'] -= 0.1
        elif confidence < 60:
            weights['fixed'] += 0.2
            weights['kelly'] -= 0.1
            weights['volatility'] -= 0.1
        
        # Adjust based on risk-reward ratio
        if risk_reward_ratio > 2.0:
            weights['kelly'] += 0.1
            weights['fixed'] -= 0.05
            weights['volatility'] -= 0.05
        
        # Adjust based on portfolio heat
        portfolio_heat = len(current_positions) / self.config.get('MAX_POSITIONS', 5)
        if portfolio_heat > 0.7:
            weights['volatility'] += 0.1
            weights['kelly'] -= 0.05
            weights['fixed'] -= 0.05
        
        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _calculate_drawdown_adjustment(self) -> float:
        """Calculate position size adjustment based on current drawdown"""
        # If no trade history, return neutral adjustment
        if len(self.trade_history) < 5:
            return 1.0
        
        # Calculate recent performance
        recent_trades = self.trade_history[-10:]
        recent_returns = [trade.get('return_pct', 0) for trade in recent_trades]
        cumulative_return = sum(recent_returns)
        
        # Adjust based on recent performance
        if cumulative_return < -0.05:  # 5% drawdown
            adjustment = 0.7  # Reduce position size by 30%
        elif cumulative_return < -0.03:  # 3% drawdown
            adjustment = 0.8  # Reduce position size by 20%
        elif cumulative_return < -0.01:  # 1% drawdown
            adjustment = 0.9  # Reduce position size by 10%
        elif cumulative_return > 0.05:  # 5% profit
            adjustment = 1.2  # Increase position size by 20%
        elif cumulative_return > 0.03:  # 3% profit
            adjustment = 1.1  # Increase position size by 10%
        else:
            adjustment = 1.0  # No adjustment
        
        # Consider consecutive losses
        if self.consecutive_losses >= 3:
            adjustment *= 0.8  # Further reduce after consecutive losses
        elif self.consecutive_losses >= 5:
            adjustment *= 0.6  # Significant reduction after many losses
        
        return max(0.3, min(1.5, adjustment))  # Cap between 30% and 150%
    
    def _apply_final_adjustments(self, result: PositionSizeResult, signal: Dict,
                               account_balance: float, current_positions: Dict) -> PositionSizeResult:
        """Apply final adjustments and validations"""
        # Check leverage limits
        entry_price = signal.get('entry_price', 1.0)
        position_value = result.position_size * entry_price
        leverage = position_value / account_balance
        
        if leverage > self.max_leverage:
            # Reduce position size to meet leverage limit
            max_position_value = account_balance * self.max_leverage
            result.position_size = max_position_value / entry_price
            result.risk_amount = result.position_size * abs(entry_price - signal.get('stop_loss', entry_price))
            result.risk_percentage = result.risk_amount / account_balance
            result.leverage_used = self.max_leverage
            result.reasoning += f" (leverage capped at {self.max_leverage}x)"
        else:
            result.leverage_used = leverage
        
        # Check minimum position size
        min_position_value = self.config.get('MIN_POSITION_VALUE', 100)
        if position_value < min_position_value:
            result.position_size = 0
            result.risk_amount = 0
            result.risk_percentage = 0
            result.reasoning = f"Position too small (min: ${min_position_value})"
        
        # Check maximum portfolio risk
        current_total_risk = sum(pos.get('risk_amount', 0) for pos in current_positions.values())
        max_portfolio_risk = account_balance * self.config.get('MAX_PORTFOLIO_RISK', 0.10)
        
        if current_total_risk + result.risk_amount > max_portfolio_risk:
            # Reduce position to fit within portfolio risk limit
            available_risk = max_portfolio_risk - current_total_risk
            if available_risk > 0:
                risk_per_unit = abs(signal.get('entry_price', 1) - signal.get('stop_loss', 1))
                result.position_size = available_risk / risk_per_unit
                result.risk_amount = available_risk
                result.risk_percentage = available_risk / account_balance
                result.reasoning += " (portfolio risk limit applied)"
            else:
                result.position_size = 0
                result.risk_amount = 0
                result.risk_percentage = 0
                result.reasoning = "Portfolio risk limit exceeded"
        
        return result
    
    def _create_zero_position_result(self, reason: str) -> PositionSizeResult:
        """Create a zero position result with reason"""
        return PositionSizeResult(
            position_size=0,
            risk_amount=0,
            risk_percentage=0,
            sizing_method="none",
            confidence_score=0,
            max_position_value=0,
            leverage_used=0,
            reasoning=reason
        )
    
    def update_trade_history(self, trade_result: Dict):
        """Update trade history for performance tracking"""
        try:
            self.trade_history.append(trade_result)
            
            # Keep only last 100 trades
            if len(self.trade_history) > 100:
                self.trade_history = self.trade_history[-100:]
            
            # Update performance metrics
            self._update_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Error updating trade history: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics from trade history"""
        if not self.trade_history:
            return
        
        # Calculate win rate
        wins = sum(1 for trade in self.trade_history if trade.get('return_pct', 0) > 0)
        self.win_rate = wins / len(self.trade_history)
        
        # Calculate average win/loss
        winning_trades = [trade.get('return_pct', 0) for trade in self.trade_history if trade.get('return_pct', 0) > 0]
        losing_trades = [trade.get('return_pct', 0) for trade in self.trade_history if trade.get('return_pct', 0) < 0]
        
        self.avg_win = np.mean(winning_trades) if winning_trades else 0.02
        self.avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0.01
        
        # Calculate consecutive losses
        consecutive = 0
        max_consecutive = 0
        
        for trade in reversed(self.trade_history):
            if trade.get('return_pct', 0) < 0:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                break
        
        self.consecutive_losses = consecutive
        self.max_consecutive_losses = max_consecutive
    
    def get_sizing_report(self) -> Dict:
        """Generate position sizing report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'base_risk_per_trade': self.base_risk_per_trade,
                'max_risk_per_trade': self.max_risk_per_trade,
                'min_risk_per_trade': self.min_risk_per_trade,
                'max_leverage': self.max_leverage,
                'kelly_multiplier': self.kelly_multiplier
            },
            'performance_metrics': {
                'win_rate': self.win_rate,
                'avg_win': self.avg_win,
                'avg_loss': self.avg_loss,
                'consecutive_losses': self.consecutive_losses,
                'max_consecutive_losses': self.max_consecutive_losses,
                'total_trades': len(self.trade_history)
            },
            'volatility_estimates': self.volatility_estimates
        }

# Example usage and testing
if __name__ == "__main__":
    # Test position sizer
    sizer = AdvancedPositionSizer()
    
    # Test signal
    test_signal = {
        'symbol': 'EURUSD',
        'entry_price': 1.1000,
        'stop_loss': 1.0950,
        'confidence_score': 75,
        'risk_reward_ratio': 2.0
    }
    
    account_balance = 10000
    current_positions = {}
    
    # Test different sizing methods
    methods = [SizingMethod.FIXED_PERCENTAGE, SizingMethod.KELLY_CRITERION, 
              SizingMethod.VOLATILITY_ADJUSTED, SizingMethod.ADAPTIVE]
    
    for method in methods:
        result = sizer.calculate_position_size(test_signal, account_balance, current_positions, method)
        print(f"\n{method.value.upper()}:")
        print(f"Position Size: {result.position_size:.2f}")
        print(f"Risk Amount: ${result.risk_amount:.2f}")
        print(f"Risk Percentage: {result.risk_percentage:.2%}")
        print(f"Reasoning: {result.reasoning}")
    
    # Generate report
    report = sizer.get_sizing_report()
    print(f"\nSizing Report: {report}")

