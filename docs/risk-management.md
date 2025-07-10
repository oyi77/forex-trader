# 🛡️ Risk Management Guide

Complete guide to understanding and configuring the risk management systems in the Advanced Forex Trading Engine.

## 🎯 Risk Management Overview

The trading engine implements a multi-layered risk management system designed to protect your capital while maximizing returns. The system includes both automated and manual risk controls.

## 📋 Risk Management Components

### 1. Account-Level Risk Controls
- **Maximum Drawdown**: Prevents excessive account losses
- **Daily Loss Limits**: Controls daily risk exposure
- **Emergency Stop**: Automatic shutdown on catastrophic losses
- **Position Limits**: Controls maximum concurrent positions

### 2. Trade-Level Risk Controls
- **Position Sizing**: Dynamic position size calculation
- **Stop Losses**: Automatic stop loss placement
- **Take Profits**: Profit target management
- **Trailing Stops**: Dynamic stop loss adjustment

### 3. Strategy-Level Risk Controls
- **Risk Allocation**: Per-strategy risk limits
- **Correlation Limits**: Prevents over-exposure
- **Volatility Adjustment**: Dynamic risk based on market conditions
- **Time-Based Exits**: Automatic position closure

## 🎯 Risk Management Configuration

### Account Risk Settings
```yaml
risk:
  max_drawdown: 20.0               # Maximum drawdown (%)
  daily_loss_limit: 10.0           # Daily loss limit (%)
  max_account_risk: 95.0           # Maximum account risk (%)
  use_emergency_stop: true         # Enable emergency stop
  emergency_stop_threshold: 80.0   # Emergency stop at 80% loss
  max_consecutive_losses: 5        # Maximum consecutive losses
  use_dynamic_risk: true           # Use dynamic risk adjustment
  risk_reduction_factor: 0.5       # Risk reduction after losses
```

### Position Risk Settings
```yaml
position_risk:
  max_positions: 20                # Maximum concurrent positions
  max_positions_per_strategy: 5    # Max positions per strategy
  max_correlation: 0.8            # Maximum correlation between positions
  use_correlation_filter: true     # Enable correlation filtering
  position_size_multiplier: 1.0    # Position size multiplier
  use_compounding: true            # Enable compounding
  compounding_factor: 1.2          # Compounding factor
```

### Stop Loss & Take Profit Settings
```yaml
stop_loss_take_profit:
  default_stop_loss_pips: 20.0     # Default stop loss
  default_take_profit_pips: 5.0    # Default take profit
  use_dynamic_sltp: true           # Use dynamic SL/TP
  sl_multiplier: 0.5               # Stop loss multiplier
  tp_multiplier: 0.3               # Take profit multiplier
  use_trailing_stop: true          # Enable trailing stop
  trailing_stop_pips: 3.0         # Trailing stop distance
  use_partial_close: true          # Enable partial close
  partial_close_percent: 50.0      # Partial close percentage
  partial_close_profit_pips: 20.0  # Profit threshold for partial close
```

## 🎯 Risk Management Strategies

### 1. God Mode Risk Management
**Purpose**: Extreme risk management for maximum returns
**Risk Level**: 80-95% account risk
**Best For**: Aggressive traders seeking maximum returns

```python
class GodModeRiskManager:
    def __init__(self, config):
        self.max_account_risk = 95.0
        self.target_daily_return = 65.98
        self.emergency_stop_threshold = 80.0
        self.use_extreme_position_sizing = True
    
    def calculate_position_size(self, signal, account_info):
        """Calculate position size with extreme risk"""
        base_risk = account_info['balance'] * (self.max_account_risk / 100.0)
        
        # God Mode multiplier
        god_mode_multiplier = 1.0 + (self.target_daily_return / 100.0)
        
        # Confidence multiplier
        confidence_multiplier = signal['confidence'] / 100.0
        
        # Calculate adjusted risk
        adjusted_risk = base_risk * god_mode_multiplier * confidence_multiplier
        
        # Apply leverage
        leveraged_risk = adjusted_risk * (self.leverage / 100.0)
        
        return self.calculate_lot_size(leveraged_risk, signal)
    
    def check_emergency_conditions(self, account_info):
        """Check for emergency stop conditions"""
        current_drawdown = self.calculate_drawdown(account_info)
        
        if current_drawdown > self.emergency_stop_threshold:
            self.activate_emergency_stop()
            return False
        
        return True
```

### 2. Conservative Risk Management
**Purpose**: Capital preservation with moderate returns
**Risk Level**: 10-20% account risk
**Best For**: Conservative traders, beginners

```python
class ConservativeRiskManager:
    def __init__(self, config):
        self.max_account_risk = 20.0
        self.max_drawdown = 10.0
        self.daily_loss_limit = 5.0
        self.use_conservative_position_sizing = True
    
    def calculate_position_size(self, signal, account_info):
        """Calculate position size with conservative risk"""
        base_risk = account_info['balance'] * (self.max_account_risk / 100.0)
        
        # Conservative multiplier
        conservative_multiplier = 0.5
        
        # Confidence multiplier
        confidence_multiplier = signal['confidence'] / 100.0
        
        # Calculate adjusted risk
        adjusted_risk = base_risk * conservative_multiplier * confidence_multiplier
        
        return self.calculate_lot_size(adjusted_risk, signal)
    
    def validate_trade(self, signal, account_info):
        """Validate trade with conservative rules"""
        # Check daily loss limit
        if self.get_daily_loss() > self.daily_loss_limit:
            return False
        
        # Check drawdown
        if self.get_drawdown() > self.max_drawdown:
            return False
        
        # Check position limits
        if self.get_open_positions() >= 5:
            return False
        
        return True
```

### 3. Dynamic Risk Management
**Purpose**: Adaptive risk based on market conditions
**Risk Level**: Variable (10-80% account risk)
**Best For**: Experienced traders, adaptive systems

```python
class DynamicRiskManager:
    def __init__(self, config):
        self.base_risk = 20.0
        self.max_risk = 80.0
        self.volatility_multiplier = 1.0
        self.market_condition_factor = 1.0
    
    def calculate_dynamic_risk(self, market_data, account_info):
        """Calculate dynamic risk based on market conditions"""
        # Volatility adjustment
        volatility = self.calculate_volatility(market_data)
        self.volatility_multiplier = self.adjust_for_volatility(volatility)
        
        # Market condition adjustment
        market_condition = self.assess_market_condition(market_data)
        self.market_condition_factor = self.adjust_for_market_condition(market_condition)
        
        # Performance adjustment
        performance_factor = self.calculate_performance_factor(account_info)
        
        # Calculate dynamic risk
        dynamic_risk = self.base_risk * self.volatility_multiplier * self.market_condition_factor * performance_factor
        
        # Apply limits
        dynamic_risk = max(10.0, min(self.max_risk, dynamic_risk))
        
        return dynamic_risk
    
    def adjust_for_volatility(self, volatility):
        """Adjust risk based on volatility"""
        if volatility > 2.0:
            return 0.5  # Reduce risk in high volatility
        elif volatility < 0.5:
            return 1.5  # Increase risk in low volatility
        else:
            return 1.0  # Normal risk
```

## 🎯 Position Sizing Methods

### 1. Fixed Risk Method
```python
def calculate_fixed_risk_position_size(self, risk_amount, stop_loss_pips, pip_value):
    """Calculate position size using fixed risk method"""
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return self.normalize_position_size(position_size)
```

### 2. Kelly Criterion Method
```python
def calculate_kelly_position_size(self, win_rate, avg_win, avg_loss, account_balance):
    """Calculate position size using Kelly Criterion"""
    kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
    
    # Apply Kelly fraction with safety factor
    safe_kelly = kelly_fraction * 0.25  # 25% of Kelly for safety
    
    position_size = account_balance * safe_kelly
    return self.normalize_position_size(position_size)
```

### 3. Volatility-Adjusted Method
```python
def calculate_volatility_adjusted_position_size(self, base_position_size, volatility):
    """Calculate position size adjusted for volatility"""
    volatility_factor = 1.0 / volatility  # Reduce size in high volatility
    
    adjusted_position_size = base_position_size * volatility_factor
    return self.normalize_position_size(adjusted_position_size)
```

## 🎯 Stop Loss Strategies

### 1. Fixed Stop Loss
```python
def calculate_fixed_stop_loss(self, entry_price, stop_loss_pips, order_type):
    """Calculate fixed stop loss"""
    pip_size = self.get_pip_size()
    stop_distance = stop_loss_pips * pip_size
    
    if order_type == 'BUY':
        return entry_price - stop_distance
    else:
        return entry_price + stop_distance
```

### 2. ATR-Based Stop Loss
```python
def calculate_atr_stop_loss(self, entry_price, atr, atr_multiplier, order_type):
    """Calculate ATR-based stop loss"""
    stop_distance = atr * atr_multiplier
    
    if order_type == 'BUY':
        return entry_price - stop_distance
    else:
        return entry_price + stop_distance
```

### 3. Trailing Stop Loss
```python
def update_trailing_stop(self, position, current_price, trailing_pips):
    """Update trailing stop loss"""
    pip_size = self.get_pip_size()
    trailing_distance = trailing_pips * pip_size
    
    if position['type'] == 'BUY':
        new_stop_loss = current_price - trailing_distance
        if new_stop_loss > position['stop_loss']:
            return new_stop_loss
    else:
        new_stop_loss = current_price + trailing_distance
        if new_stop_loss < position['stop_loss']:
            return new_stop_loss
    
    return position['stop_loss']
```

## 🎯 Take Profit Strategies

### 1. Fixed Take Profit
```python
def calculate_fixed_take_profit(self, entry_price, take_profit_pips, order_type):
    """Calculate fixed take profit"""
    pip_size = self.get_pip_size()
    profit_distance = take_profit_pips * pip_size
    
    if order_type == 'BUY':
        return entry_price + profit_distance
    else:
        return entry_price - profit_distance
```

### 2. Risk-Reward Based Take Profit
```python
def calculate_rr_take_profit(self, entry_price, stop_loss, risk_reward_ratio, order_type):
    """Calculate take profit based on risk-reward ratio"""
    stop_distance = abs(entry_price - stop_loss)
    profit_distance = stop_distance * risk_reward_ratio
    
    if order_type == 'BUY':
        return entry_price + profit_distance
    else:
        return entry_price - profit_distance
```

### 3. Partial Close Strategy
```python
def execute_partial_close(self, position, partial_percent, profit_threshold):
    """Execute partial close of position"""
    if position['profit'] >= profit_threshold:
        close_volume = position['volume'] * (partial_percent / 100.0)
        
        # Execute partial close
        self.close_position_partial(position['ticket'], close_volume)
        
        # Update position
        position['volume'] -= close_volume
        position['partial_closed'] = True
```

## 🎯 Correlation Management

### 1. Correlation Detection
```python
def calculate_correlation(self, symbol1, symbol2, period=30):
    """Calculate correlation between two symbols"""
    prices1 = self.get_historical_prices(symbol1, period)
    prices2 = self.get_historical_prices(symbol2, period)
    
    correlation = np.corrcoef(prices1, prices2)[0, 1]
    return correlation
```

### 2. Correlation Filter
```python
def check_correlation_limit(self, new_symbol, existing_positions, max_correlation=0.8):
    """Check if new position exceeds correlation limit"""
    for position in existing_positions:
        correlation = self.calculate_correlation(new_symbol, position['symbol'])
        
        if abs(correlation) > max_correlation:
            return False
    
    return True
```

### 3. Portfolio Diversification
```python
def optimize_portfolio_diversification(self, positions, target_correlation=0.3):
    """Optimize portfolio for diversification"""
    # Calculate current portfolio correlation
    portfolio_correlation = self.calculate_portfolio_correlation(positions)
    
    if portfolio_correlation > target_correlation:
        # Suggest position adjustments
        suggestions = self.suggest_position_adjustments(positions, target_correlation)
        return suggestions
    
    return None
```

## 🎯 Risk Monitoring

### 1. Real-time Risk Dashboard
```python
class RiskDashboard:
    def __init__(self):
        self.risk_metrics = {}
    
    def update_risk_metrics(self, account_info, positions):
        """Update real-time risk metrics"""
        self.risk_metrics = {
            'current_drawdown': self.calculate_drawdown(account_info),
            'daily_loss': self.calculate_daily_loss(account_info),
            'total_exposure': self.calculate_total_exposure(positions),
            'largest_position': self.get_largest_position(positions),
            'correlation_score': self.calculate_portfolio_correlation(positions),
            'risk_score': self.calculate_overall_risk_score(account_info, positions)
        }
    
    def generate_risk_report(self):
        """Generate comprehensive risk report"""
        report = {
            'timestamp': datetime.now(),
            'metrics': self.risk_metrics,
            'alerts': self.check_risk_alerts(),
            'recommendations': self.generate_risk_recommendations()
        }
        return report
```

### 2. Risk Alerts
```python
def check_risk_alerts(self):
    """Check for risk alerts"""
    alerts = []
    
    # Drawdown alert
    if self.risk_metrics['current_drawdown'] > 15.0:
        alerts.append({
            'type': 'DRAWDOWN_WARNING',
            'message': f"Drawdown at {self.risk_metrics['current_drawdown']:.2f}%",
            'severity': 'HIGH'
        })
    
    # Daily loss alert
    if self.risk_metrics['daily_loss'] > 8.0:
        alerts.append({
            'type': 'DAILY_LOSS_WARNING',
            'message': f"Daily loss at {self.risk_metrics['daily_loss']:.2f}%",
            'severity': 'MEDIUM'
        })
    
    # Correlation alert
    if self.risk_metrics['correlation_score'] > 0.8:
        alerts.append({
            'type': 'CORRELATION_WARNING',
            'message': f"High correlation: {self.risk_metrics['correlation_score']:.2f}",
            'severity': 'MEDIUM'
        })
    
    return alerts
```

## 🎯 Emergency Procedures

### 1. Emergency Stop
```python
def activate_emergency_stop(self):
    """Activate emergency stop procedure"""
    # Close all positions
    self.close_all_positions("EMERGENCY_STOP")
    
    # Disable trading
    self.disable_trading()
    
    # Send alerts
    self.send_emergency_alerts()
    
    # Log emergency stop
    self.log_emergency_stop()
```

### 2. Risk Reduction Mode
```python
def activate_risk_reduction_mode(self):
    """Activate risk reduction mode"""
    # Reduce position sizes
    self.position_size_multiplier *= 0.5
    
    # Tighten stop losses
    self.stop_loss_multiplier *= 0.7
    
    # Reduce maximum positions
    self.max_positions = max(5, self.max_positions // 2)
    
    # Enable conservative mode
    self.enable_conservative_mode()
```

## 🎯 Best Practices

### 1. Risk Management Principles
- **Never risk more than you can afford to lose**
- **Always use stop losses**
- **Diversify your positions**
- **Monitor risk continuously**
- **Have emergency procedures ready**

### 2. Position Sizing Rules
- **Risk 1-2% per trade for conservative approach**
- **Risk 5-10% per trade for moderate approach**
- **Risk 10-20% per trade for aggressive approach**
- **Never exceed 50% total account risk**

### 3. Stop Loss Guidelines
- **Use ATR-based stops for volatility adjustment**
- **Set stops at logical support/resistance levels**
- **Avoid stops that are too tight or too wide**
- **Use trailing stops for profitable trades**

### 4. Take Profit Guidelines
- **Use risk-reward ratios of 1:2 or better**
- **Consider partial profit taking**
- **Use multiple take profit levels**
- **Let profitable trades run with trailing stops**

## 🎯 Troubleshooting

### Common Risk Management Issues

#### High Drawdown
1. **Reduce position sizes**
2. **Tighten stop losses**
3. **Review strategy performance**
4. **Check for over-correlation**

#### Frequent Stop Outs
1. **Widen stop losses**
2. **Check market volatility**
3. **Review entry timing**
4. **Adjust position sizing**

#### Poor Risk-Reward Ratios
1. **Improve entry timing**
2. **Adjust take profit levels**
3. **Review strategy logic**
4. **Check market conditions**

### Getting Help
- **Documentation**: [Complete Guide](README.md)
- **Issues**: [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- **Community**: [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)

---

*For advanced risk management techniques, see [API Reference](api-reference.md)* 