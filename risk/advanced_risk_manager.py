"""
Advanced Risk Management System for Forex Trading Bot
Implements comprehensive risk controls and portfolio optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class RiskMetrics:
    """Risk metrics for portfolio assessment"""
    total_exposure: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    sharpe_ratio: float
    correlation_risk: float
    leverage_ratio: float
    daily_pnl_volatility: float

@dataclass
class PositionRisk:
    """Risk assessment for individual position"""
    symbol: str
    position_size: float
    risk_amount: float
    risk_percentage: float
    correlation_score: float
    volatility_score: float
    liquidity_score: float
    overall_risk_level: RiskLevel

class AdvancedRiskManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger('AdvancedRiskManager')
        
        # Risk parameters
        self.max_daily_risk = self.config.get('MAX_DAILY_RISK', 0.03)  # 3% max daily risk
        self.max_portfolio_risk = self.config.get('MAX_PORTFOLIO_RISK', 0.10)  # 10% max portfolio risk
        self.max_single_position_risk = self.config.get('MAX_SINGLE_POSITION_RISK', 0.02)  # 2% per position
        self.max_correlation_exposure = self.config.get('MAX_CORRELATION_EXPOSURE', 0.05)  # 5% for correlated positions
        self.max_leverage = self.config.get('MAX_LEVERAGE', 10.0)  # 10:1 max leverage
        self.emergency_stop_loss = self.config.get('EMERGENCY_STOP_LOSS', 0.15)  # 15% emergency stop
        
        # Risk monitoring
        self.daily_pnl = []
        self.position_history = []
        self.risk_events = []
        self.current_drawdown = 0.0
        self.max_historical_drawdown = 0.0
        
        # Currency correlation matrix (simplified)
        self.correlation_matrix = self._initialize_correlation_matrix()
        
        # Volatility estimates for major pairs
        self.volatility_estimates = self._initialize_volatility_estimates()
        
        self.logger.info("Advanced Risk Manager initialized")
    
    def _initialize_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Initialize currency pair correlation matrix"""
        # Simplified correlation matrix for major forex pairs
        # In production, this would be updated with real-time correlations
        return {
            'EURUSD': {'EURUSD': 1.0, 'GBPUSD': 0.7, 'USDJPY': -0.3, 'AUDUSD': 0.6, 'USDCHF': -0.8},
            'GBPUSD': {'EURUSD': 0.7, 'GBPUSD': 1.0, 'USDJPY': -0.2, 'AUDUSD': 0.5, 'USDCHF': -0.6},
            'USDJPY': {'EURUSD': -0.3, 'GBPUSD': -0.2, 'USDJPY': 1.0, 'AUDUSD': -0.1, 'USDCHF': 0.4},
            'AUDUSD': {'EURUSD': 0.6, 'GBPUSD': 0.5, 'USDJPY': -0.1, 'AUDUSD': 1.0, 'USDCHF': -0.5},
            'USDCHF': {'EURUSD': -0.8, 'GBPUSD': -0.6, 'USDJPY': 0.4, 'AUDUSD': -0.5, 'USDCHF': 1.0}
        }
    
    def _initialize_volatility_estimates(self) -> Dict[str, float]:
        """Initialize volatility estimates for currency pairs"""
        # Daily volatility estimates (as percentage)
        return {
            'EURUSD': 0.007,  # 0.7% daily volatility
            'GBPUSD': 0.009,  # 0.9% daily volatility
            'USDJPY': 0.008,  # 0.8% daily volatility
            'AUDUSD': 0.010,  # 1.0% daily volatility
            'USDCHF': 0.008,  # 0.8% daily volatility
            'NZDUSD': 0.011,  # 1.1% daily volatility
            'USDCAD': 0.007,  # 0.7% daily volatility
        }
    
    def validate_new_position(self, signal: Dict, active_positions: Dict, 
                            account_balance: float) -> Tuple[bool, str, Dict]:
        """Comprehensive validation of new position"""
        try:
            # Extract signal information
            symbol = signal.get('symbol', '')
            signal_type = signal.get('signal_type', '')
            entry_price = signal.get('entry_price', 0)
            stop_loss = signal.get('stop_loss', 0)
            confidence = signal.get('confidence_score', 0)
            
            # Calculate position risk
            position_risk = self._calculate_position_risk(
                signal, account_balance, active_positions
            )
            
            # Risk checks
            checks = {
                'position_size_check': self._check_position_size(position_risk),
                'correlation_check': self._check_correlation_risk(symbol, active_positions),
                'portfolio_risk_check': self._check_portfolio_risk(position_risk, active_positions, account_balance),
                'volatility_check': self._check_volatility_risk(symbol, position_risk),
                'drawdown_check': self._check_drawdown_limits(),
                'confidence_check': self._check_confidence_threshold(confidence),
                'market_hours_check': self._check_market_hours(),
                'emergency_check': self._check_emergency_conditions()
            }
            
            # Determine if position is approved
            failed_checks = [check for check, passed in checks.items() if not passed]
            
            if failed_checks:
                reason = f"Position rejected due to: {', '.join(failed_checks)}"
                return False, reason, position_risk.__dict__
            
            # Calculate optimal position size
            optimal_size = self._calculate_optimal_position_size(
                signal, account_balance, active_positions
            )
            
            # Update signal with optimal position size
            signal['optimal_position_size'] = optimal_size
            signal['risk_assessment'] = position_risk.__dict__
            
            return True, "Position approved", position_risk.__dict__
            
        except Exception as e:
            self.logger.error(f"Error validating position: {e}")
            return False, f"Validation error: {e}", {}
    
    def _calculate_position_risk(self, signal: Dict, account_balance: float, 
                               active_positions: Dict) -> PositionRisk:
        """Calculate comprehensive risk assessment for position"""
        symbol = signal.get('symbol', '')
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        signal_type = signal.get('signal_type', '')
        
        # Calculate risk per unit
        if signal_type == 'BUY':
            risk_per_unit = abs(entry_price - stop_loss)
        else:
            risk_per_unit = abs(stop_loss - entry_price)
        
        # Calculate position size based on risk
        max_risk_amount = account_balance * self.max_single_position_risk
        position_size = max_risk_amount / risk_per_unit if risk_per_unit > 0 else 0
        
        # Calculate actual risk amount
        risk_amount = position_size * risk_per_unit
        risk_percentage = risk_amount / account_balance
        
        # Calculate correlation score
        correlation_score = self._calculate_correlation_score(symbol, active_positions)
        
        # Calculate volatility score
        volatility_score = self.volatility_estimates.get(symbol, 0.01)
        
        # Liquidity score (simplified - major pairs have high liquidity)
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD']
        liquidity_score = 1.0 if symbol in major_pairs else 0.7
        
        # Determine overall risk level
        overall_risk_level = self._determine_risk_level(
            risk_percentage, correlation_score, volatility_score, liquidity_score
        )
        
        return PositionRisk(
            symbol=symbol,
            position_size=position_size,
            risk_amount=risk_amount,
            risk_percentage=risk_percentage,
            correlation_score=correlation_score,
            volatility_score=volatility_score,
            liquidity_score=liquidity_score,
            overall_risk_level=overall_risk_level
        )
    
    def _calculate_correlation_score(self, symbol: str, active_positions: Dict) -> float:
        """Calculate correlation risk score with existing positions"""
        if not active_positions:
            return 0.0
        
        total_correlation = 0.0
        total_exposure = 0.0
        
        for position in active_positions.values():
            existing_symbol = position.get('symbol', '')
            position_size = position.get('position_size', 0)
            
            # Get correlation coefficient
            correlation = self.correlation_matrix.get(symbol, {}).get(existing_symbol, 0.0)
            
            # Weight by position size
            weighted_correlation = abs(correlation) * position_size
            total_correlation += weighted_correlation
            total_exposure += position_size
        
        return total_correlation / total_exposure if total_exposure > 0 else 0.0
    
    def _determine_risk_level(self, risk_percentage: float, correlation_score: float,
                            volatility_score: float, liquidity_score: float) -> RiskLevel:
        """Determine overall risk level for position"""
        # Calculate composite risk score
        risk_score = (
            risk_percentage * 0.4 +
            correlation_score * 0.3 +
            volatility_score * 0.2 +
            (1 - liquidity_score) * 0.1
        )
        
        if risk_score < 0.01:
            return RiskLevel.LOW
        elif risk_score < 0.02:
            return RiskLevel.MEDIUM
        elif risk_score < 0.03:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _check_position_size(self, position_risk: PositionRisk) -> bool:
        """Check if position size is within limits"""
        return position_risk.risk_percentage <= self.max_single_position_risk
    
    def _check_correlation_risk(self, symbol: str, active_positions: Dict) -> bool:
        """Check correlation risk with existing positions"""
        correlation_exposure = 0.0
        
        for position in active_positions.values():
            existing_symbol = position.get('symbol', '')
            position_size = position.get('position_size', 0)
            
            correlation = self.correlation_matrix.get(symbol, {}).get(existing_symbol, 0.0)
            
            if abs(correlation) > 0.5:  # High correlation threshold
                correlation_exposure += position_size * abs(correlation)
        
        return correlation_exposure <= self.max_correlation_exposure
    
    def _check_portfolio_risk(self, position_risk: PositionRisk, 
                            active_positions: Dict, account_balance: float) -> bool:
        """Check total portfolio risk"""
        current_portfolio_risk = sum(
            pos.get('risk_amount', 0) for pos in active_positions.values()
        )
        
        total_risk = current_portfolio_risk + position_risk.risk_amount
        portfolio_risk_percentage = total_risk / account_balance
        
        return portfolio_risk_percentage <= self.max_portfolio_risk
    
    def _check_volatility_risk(self, symbol: str, position_risk: PositionRisk) -> bool:
        """Check volatility-adjusted risk"""
        volatility = self.volatility_estimates.get(symbol, 0.01)
        volatility_adjusted_risk = position_risk.risk_percentage * (1 + volatility * 10)
        
        return volatility_adjusted_risk <= self.max_single_position_risk * 1.5
    
    def _check_drawdown_limits(self) -> bool:
        """Check if current drawdown is within limits"""
        return self.current_drawdown <= self.emergency_stop_loss
    
    def _check_confidence_threshold(self, confidence: float) -> bool:
        """Check if signal confidence meets minimum threshold"""
        min_confidence = self.config.get('MIN_CONFIDENCE', 70)
        return confidence >= min_confidence
    
    def _check_market_hours(self) -> bool:
        """Check if current time is within trading hours"""
        current_hour = datetime.now().hour
        
        # Avoid trading during low liquidity hours (simplified)
        # In production, this would consider different market sessions
        low_liquidity_hours = [22, 23, 0, 1, 2, 3, 4, 5]  # Weekend and early morning
        
        return current_hour not in low_liquidity_hours
    
    def _check_emergency_conditions(self) -> bool:
        """Check for emergency market conditions"""
        # Check for rapid drawdown
        if len(self.daily_pnl) >= 5:
            recent_pnl = self.daily_pnl[-5:]
            if all(pnl < 0 for pnl in recent_pnl):
                return False  # 5 consecutive losing days
        
        # Check for excessive volatility
        # In production, this would check market volatility indicators
        
        return True
    
    def _calculate_optimal_position_size(self, signal: Dict, account_balance: float,
                                       active_positions: Dict) -> float:
        """Calculate optimal position size using Kelly Criterion and risk parity"""
        symbol = signal.get('symbol', '')
        confidence = signal.get('confidence_score', 0) / 100
        risk_reward_ratio = signal.get('risk_reward_ratio', 1.0)
        
        # Kelly Criterion calculation
        win_probability = confidence
        kelly_fraction = (win_probability * (1 + risk_reward_ratio) - 1) / risk_reward_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Risk parity adjustment
        volatility = self.volatility_estimates.get(symbol, 0.01)
        volatility_adjustment = 0.01 / volatility  # Inverse volatility weighting
        
        # Portfolio heat adjustment
        current_heat = len(active_positions) / self.config.get('MAX_POSITIONS', 5)
        heat_adjustment = 1 - current_heat * 0.3  # Reduce size as portfolio fills
        
        # Calculate final position size
        base_risk = self.max_single_position_risk
        optimal_risk = base_risk * kelly_fraction * volatility_adjustment * heat_adjustment
        
        # Ensure within limits
        optimal_risk = min(optimal_risk, self.max_single_position_risk)
        
        return optimal_risk
    
    def update_portfolio_metrics(self, active_positions: Dict, account_balance: float,
                               current_equity: float) -> RiskMetrics:
        """Update and calculate portfolio risk metrics"""
        try:
            # Calculate total exposure
            total_exposure = sum(
                pos.get('position_size', 0) * pos.get('entry_price', 0)
                for pos in active_positions.values()
            )
            
            # Update drawdown
            peak_equity = max(current_equity, getattr(self, 'peak_equity', current_equity))
            self.peak_equity = peak_equity
            self.current_drawdown = (peak_equity - current_equity) / peak_equity
            self.max_historical_drawdown = max(self.max_historical_drawdown, self.current_drawdown)
            
            # Calculate VaR (simplified)
            portfolio_volatility = self._calculate_portfolio_volatility(active_positions)
            var_95 = current_equity * portfolio_volatility * 1.645  # 95% VaR
            
            # Calculate Sharpe ratio (simplified)
            if len(self.daily_pnl) > 30:
                returns = np.array(self.daily_pnl[-30:]) / account_balance
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calculate correlation risk
            correlation_risk = self._calculate_portfolio_correlation_risk(active_positions)
            
            # Calculate leverage ratio
            leverage_ratio = total_exposure / current_equity if current_equity > 0 else 0
            
            # Calculate daily P&L volatility
            if len(self.daily_pnl) > 10:
                daily_pnl_volatility = np.std(self.daily_pnl[-30:]) if len(self.daily_pnl) >= 30 else np.std(self.daily_pnl)
            else:
                daily_pnl_volatility = 0
            
            risk_metrics = RiskMetrics(
                total_exposure=total_exposure,
                max_drawdown=self.max_historical_drawdown,
                var_95=var_95,
                sharpe_ratio=sharpe_ratio,
                correlation_risk=correlation_risk,
                leverage_ratio=leverage_ratio,
                daily_pnl_volatility=daily_pnl_volatility
            )
            
            # Check for risk alerts
            self._check_risk_alerts(risk_metrics)
            
            return risk_metrics
            
        except Exception as e:
            self.logger.error(f"Error updating portfolio metrics: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0)
    
    def _calculate_portfolio_volatility(self, active_positions: Dict) -> float:
        """Calculate portfolio volatility considering correlations"""
        if not active_positions:
            return 0.0
        
        symbols = [pos.get('symbol', '') for pos in active_positions.values()]
        weights = [pos.get('position_size', 0) for pos in active_positions.values()]
        
        # Normalize weights
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        weights = [w / total_weight for w in weights]
        
        # Calculate portfolio variance
        portfolio_variance = 0.0
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                vol1 = self.volatility_estimates.get(symbol1, 0.01)
                vol2 = self.volatility_estimates.get(symbol2, 0.01)
                correlation = self.correlation_matrix.get(symbol1, {}).get(symbol2, 0.0)
                
                portfolio_variance += weights[i] * weights[j] * vol1 * vol2 * correlation
        
        return np.sqrt(max(0, portfolio_variance))
    
    def _calculate_portfolio_correlation_risk(self, active_positions: Dict) -> float:
        """Calculate overall portfolio correlation risk"""
        if len(active_positions) < 2:
            return 0.0
        
        symbols = [pos.get('symbol', '') for pos in active_positions.values()]
        total_correlation = 0.0
        pair_count = 0
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                correlation = abs(self.correlation_matrix.get(symbol1, {}).get(symbol2, 0.0))
                total_correlation += correlation
                pair_count += 1
        
        return total_correlation / pair_count if pair_count > 0 else 0.0
    
    def _check_risk_alerts(self, risk_metrics: RiskMetrics):
        """Check for risk alerts and log warnings"""
        alerts = []
        
        if risk_metrics.max_drawdown > 0.10:
            alerts.append(f"High drawdown: {risk_metrics.max_drawdown:.2%}")
        
        if risk_metrics.leverage_ratio > self.max_leverage:
            alerts.append(f"Excessive leverage: {risk_metrics.leverage_ratio:.1f}x")
        
        if risk_metrics.correlation_risk > 0.7:
            alerts.append(f"High correlation risk: {risk_metrics.correlation_risk:.2f}")
        
        if risk_metrics.var_95 > risk_metrics.total_exposure * 0.05:
            alerts.append(f"High VaR: ${risk_metrics.var_95:.2f}")
        
        for alert in alerts:
            self.logger.warning(f"RISK ALERT: {alert}")
            self.risk_events.append({
                'timestamp': datetime.now(),
                'type': 'RISK_ALERT',
                'message': alert
            })
    
    def should_reduce_positions(self, risk_metrics: RiskMetrics) -> bool:
        """Determine if positions should be reduced due to risk"""
        # Emergency conditions
        if risk_metrics.max_drawdown > self.emergency_stop_loss:
            return True
        
        if risk_metrics.leverage_ratio > self.max_leverage * 1.2:
            return True
        
        if risk_metrics.correlation_risk > 0.8:
            return True
        
        return False
    
    def get_position_reduction_plan(self, active_positions: Dict, 
                                  target_reduction: float) -> List[str]:
        """Get plan for reducing positions to manage risk"""
        # Sort positions by risk level (highest first)
        position_risks = []
        
        for pos_id, position in active_positions.items():
            symbol = position.get('symbol', '')
            volatility = self.volatility_estimates.get(symbol, 0.01)
            position_size = position.get('position_size', 0)
            
            risk_score = volatility * position_size
            position_risks.append((pos_id, risk_score))
        
        # Sort by risk score (highest first)
        position_risks.sort(key=lambda x: x[1], reverse=True)
        
        # Select positions to close
        positions_to_close = []
        current_reduction = 0.0
        
        for pos_id, risk_score in position_risks:
            if current_reduction >= target_reduction:
                break
            
            positions_to_close.append(pos_id)
            current_reduction += risk_score
        
        return positions_to_close
    
    def log_daily_pnl(self, pnl: float):
        """Log daily P&L for risk tracking"""
        self.daily_pnl.append(pnl)
        
        # Keep only last 252 days (1 year)
        if len(self.daily_pnl) > 252:
            self.daily_pnl = self.daily_pnl[-252:]
    
    def get_risk_report(self, active_positions: Dict, account_balance: float,
                       current_equity: float) -> Dict:
        """Generate comprehensive risk report"""
        risk_metrics = self.update_portfolio_metrics(active_positions, account_balance, current_equity)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'account_balance': account_balance,
            'current_equity': current_equity,
            'active_positions': len(active_positions),
            'risk_metrics': {
                'total_exposure': risk_metrics.total_exposure,
                'max_drawdown': risk_metrics.max_drawdown,
                'current_drawdown': self.current_drawdown,
                'var_95': risk_metrics.var_95,
                'sharpe_ratio': risk_metrics.sharpe_ratio,
                'correlation_risk': risk_metrics.correlation_risk,
                'leverage_ratio': risk_metrics.leverage_ratio,
                'daily_pnl_volatility': risk_metrics.daily_pnl_volatility
            },
            'risk_limits': {
                'max_daily_risk': self.max_daily_risk,
                'max_portfolio_risk': self.max_portfolio_risk,
                'max_single_position_risk': self.max_single_position_risk,
                'max_correlation_exposure': self.max_correlation_exposure,
                'max_leverage': self.max_leverage,
                'emergency_stop_loss': self.emergency_stop_loss
            },
            'recent_alerts': self.risk_events[-10:] if self.risk_events else [],
            'should_reduce_positions': self.should_reduce_positions(risk_metrics)
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the advanced risk manager
    config = {
        'MAX_DAILY_RISK': 0.03,
        'MAX_PORTFOLIO_RISK': 0.10,
        'MAX_SINGLE_POSITION_RISK': 0.02,
        'MIN_CONFIDENCE': 75
    }
    
    risk_manager = AdvancedRiskManager(config)
    
    # Test signal validation
    test_signal = {
        'symbol': 'EURUSD',
        'signal_type': 'BUY',
        'entry_price': 1.1000,
        'stop_loss': 1.0950,
        'take_profit': [1.1100, 1.1150, 1.1200],
        'confidence_score': 80,
        'risk_reward_ratio': 2.0
    }
    
    test_positions = {}
    test_balance = 10000.0
    
    approved, reason, risk_data = risk_manager.validate_new_position(
        test_signal, test_positions, test_balance
    )
    
    print(f"Position validation: {approved}")
    print(f"Reason: {reason}")
    print(f"Risk data: {risk_data}")
    
    # Test risk report
    risk_report = risk_manager.get_risk_report(test_positions, test_balance, test_balance)
    print(f"\nRisk Report: {risk_report}")

