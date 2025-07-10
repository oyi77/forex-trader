# 📊 Trading Strategies Guide

Complete guide to understanding, developing, and optimizing trading strategies for the Advanced Forex Trading Engine.

## 🎯 Strategy Overview

The trading engine supports multiple strategy types, each designed for different market conditions and risk profiles. All strategies are built on a common framework that ensures consistency and reliability.

## 📋 Strategy Framework

### Base Strategy Class
All strategies inherit from the base strategy class:

```python
from src.core.strategy_core import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "My Custom Strategy"
        self.description = "Custom strategy description"
        self.risk_per_trade = 5.0
        self.confidence_threshold = 70.0
    
    def generate_signals(self, data):
        """Generate trading signals from market data"""
        signals = []
        # Your signal generation logic here
        return signals
    
    def calculate_position_size(self, signal, account_info):
        """Calculate position size based on signal and account"""
        # Your position sizing logic here
        return position_size
    
    def validate_signal(self, signal):
        """Validate signal before execution"""
        # Your validation logic here
        return is_valid
```

### Strategy Components
1. **Signal Generation**: Analyze market data to identify opportunities
2. **Risk Management**: Calculate position sizes and risk levels
3. **Entry Logic**: Determine optimal entry points
4. **Exit Logic**: Define exit conditions and take profit levels
5. **Position Management**: Handle ongoing position monitoring

## 🎯 Built-in Strategies

### 1. God Mode Scalping
**Purpose**: Ultra-aggressive scalping for maximum returns
**Risk Level**: Extreme (80% risk per trade)
**Best For**: High-frequency trading, volatile markets

```python
class GodModeScalpingStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "God Mode Scalping"
        self.risk_per_trade = 80.0
        self.max_hold_time = 60  # 60 seconds
        self.min_pip_movement = 0.1
        self.rsi_period = 3
        self.ema_fast = 2
        self.ema_slow = 5
        self.confidence_threshold = 50.0
    
    def generate_signals(self, data):
        signals = []
        
        # RSI analysis
        rsi = self.calculate_rsi(data, self.rsi_period)
        
        # EMA analysis
        ema_fast = self.calculate_ema(data, self.ema_fast)
        ema_slow = self.calculate_ema(data, self.ema_slow)
        
        # Signal generation
        if (rsi < 30 and ema_fast > ema_slow):
            signal = {
                'type': 'BUY',
                'confidence': 85.0,
                'stop_loss_pips': 5.0,
                'take_profit_pips': 2.0,
                'strategy': self.name
            }
            signals.append(signal)
        
        return signals
```

### 2. Extreme RSI Strategy
**Purpose**: RSI-based reversal trading with extreme levels
**Risk Level**: High (70% risk per trade)
**Best For**: Trending markets, reversal opportunities

```python
class ExtremeRSIStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Extreme RSI"
        self.risk_per_trade = 70.0
        self.rsi_period = 5
        self.oversold_level = 15.0
        self.overbought_level = 85.0
        self.confidence_boost = 25.0
    
    def generate_signals(self, data):
        signals = []
        
        # RSI calculation
        rsi = self.calculate_rsi(data, self.rsi_period)
        
        # Extreme oversold signal
        if rsi < self.oversold_level:
            signal = {
                'type': 'BUY',
                'confidence': 90.0 + self.confidence_boost,
                'stop_loss_pips': 15.0,
                'take_profit_pips': 8.0,
                'strategy': self.name
            }
            signals.append(signal)
        
        # Extreme overbought signal
        elif rsi > self.overbought_level:
            signal = {
                'type': 'SELL',
                'confidence': 90.0 + self.confidence_boost,
                'stop_loss_pips': 15.0,
                'take_profit_pips': 8.0,
                'strategy': self.name
            }
            signals.append(signal)
        
        return signals
```

### 3. Volatility Explosion Strategy
**Purpose**: Trade volatility spikes and market explosions
**Risk Level**: Very High (85% risk per trade)
**Best For**: High volatility periods, news events

```python
class VolatilityExplosionStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Volatility Explosion"
        self.risk_per_trade = 85.0
        self.volatility_threshold = 2.0
        self.lookback_period = 5
        self.explosion_multiplier = 3.0
    
    def generate_signals(self, data):
        signals = []
        
        # ATR calculation for volatility
        atr = self.calculate_atr(data, 14)
        avg_atr = self.calculate_average_atr(data, self.lookback_period)
        
        # Volatility explosion detection
        if atr > avg_atr * self.volatility_threshold:
            # Determine direction based on price action
            price_change = data['close'][-1] - data['close'][-2]
            
            if price_change > 0:
                signal = {
                    'type': 'BUY',
                    'confidence': 95.0,
                    'stop_loss_pips': 20.0,
                    'take_profit_pips': 10.0,
                    'strategy': self.name
                }
            else:
                signal = {
                    'type': 'SELL',
                    'confidence': 95.0,
                    'stop_loss_pips': 20.0,
                    'take_profit_pips': 10.0,
                    'strategy': self.name
                }
            
            signals.append(signal)
        
        return signals
```

### 4. Momentum Surge Strategy
**Purpose**: MACD-based momentum trading
**Risk Level**: High (75% risk per trade)
**Best For**: Trending markets, momentum continuation

```python
class MomentumSurgeStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Momentum Surge"
        self.risk_per_trade = 75.0
        self.macd_fast = 5
        self.macd_slow = 13
        self.macd_signal = 3
        self.momentum_threshold = 0.0001
    
    def generate_signals(self, data):
        signals = []
        
        # MACD calculation
        macd_line, signal_line, histogram = self.calculate_macd(
            data, self.macd_fast, self.macd_slow, self.macd_signal
        )
        
        # Momentum surge detection
        if (macd_line > signal_line and 
            histogram > self.momentum_threshold):
            
            signal = {
                'type': 'BUY',
                'confidence': 80.0,
                'stop_loss_pips': 12.0,
                'take_profit_pips': 6.0,
                'strategy': self.name
            }
            signals.append(signal)
        
        elif (macd_line < signal_line and 
              histogram < -self.momentum_threshold):
            
            signal = {
                'type': 'SELL',
                'confidence': 80.0,
                'stop_loss_pips': 12.0,
                'take_profit_pips': 6.0,
                'strategy': self.name
            }
            signals.append(signal)
        
        return signals
```

### 5. News Impact Strategy
**Purpose**: Trade high-impact news events
**Risk Level**: Extreme (90% risk per trade)
**Best For**: News trading, high-impact events

```python
class NewsImpactStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "News Impact"
        self.risk_per_trade = 90.0
        self.volatility_multiplier = 2.5
        self.lookback_bars = 3
        self.news_time_ranges = ["08:30-09:30", "13:30-14:30", "15:30-16:30"]
    
    def generate_signals(self, data):
        signals = []
        
        # Check if current time is in news window
        current_time = datetime.now()
        is_news_time = self.is_in_news_window(current_time)
        
        if is_news_time:
            # Enhanced volatility detection
            atr = self.calculate_atr(data, 14)
            avg_atr = self.calculate_average_atr(data, self.lookback_bars)
            
            if atr > avg_atr * self.volatility_multiplier:
                # Determine direction based on price action
                price_change = data['close'][-1] - data['close'][-2]
                
                if price_change > 0:
                    signal = {
                        'type': 'BUY',
                        'confidence': 95.0,
                        'stop_loss_pips': 25.0,
                        'take_profit_pips': 15.0,
                        'strategy': self.name
                    }
                else:
                    signal = {
                        'type': 'SELL',
                        'confidence': 95.0,
                        'stop_loss_pips': 25.0,
                        'take_profit_pips': 15.0,
                        'strategy': self.name
                    }
                
                signals.append(signal)
        
        return signals
```

### 6. Grid Recovery Strategy
**Purpose**: Grid-based recovery system
**Risk Level**: Moderate (60% risk per trade)
**Best For**: Range-bound markets, recovery trading

```python
class GridRecoveryStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Grid Recovery"
        self.risk_per_trade = 60.0
        self.grid_spacing = 10.0
        self.max_grid_levels = 10
        self.grid_multiplier = 1.5
    
    def generate_signals(self, data):
        signals = []
        
        # Grid level calculation
        current_price = data['close'][-1]
        grid_levels = self.calculate_grid_levels(current_price)
        
        # Check for grid entry opportunities
        for level in grid_levels:
            if self.should_enter_grid_level(level, data):
                signal = {
                    'type': 'GRID_BUY' if level['type'] == 'BUY' else 'GRID_SELL',
                    'confidence': 70.0,
                    'stop_loss_pips': 15.0,
                    'take_profit_pips': 8.0,
                    'strategy': self.name,
                    'grid_level': level['level']
                }
                signals.append(signal)
        
        return signals
```

## 🎯 Strategy Development

### Creating Custom Strategies

#### Step 1: Strategy Class Structure
```python
from src.core.strategy_core import BaseStrategy
import numpy as np

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "My Custom Strategy"
        self.description = "Custom strategy for specific market conditions"
        self.risk_per_trade = 5.0
        self.confidence_threshold = 70.0
        
        # Strategy-specific parameters
        self.lookback_period = 20
        self.threshold = 0.5
    
    def generate_signals(self, data):
        """Generate trading signals"""
        signals = []
        
        # Your signal generation logic here
        # Example: Simple moving average crossover
        if len(data['close']) >= self.lookback_period:
            sma_short = np.mean(data['close'][-10:])
            sma_long = np.mean(data['close'][-self.lookback_period:])
            
            if sma_short > sma_long:
                signal = {
                    'type': 'BUY',
                    'confidence': 75.0,
                    'stop_loss_pips': 10.0,
                    'take_profit_pips': 5.0,
                    'strategy': self.name
                }
                signals.append(signal)
        
        return signals
    
    def calculate_position_size(self, signal, account_info):
        """Calculate position size"""
        base_risk = account_info['balance'] * (self.risk_per_trade / 100.0)
        confidence_multiplier = signal['confidence'] / 100.0
        
        # Adjust for signal confidence
        adjusted_risk = base_risk * confidence_multiplier
        
        # Calculate position size based on stop loss
        pip_value = self.get_pip_value(signal['symbol'])
        position_size = adjusted_risk / (signal['stop_loss_pips'] * pip_value)
        
        return self.normalize_position_size(position_size)
    
    def validate_signal(self, signal):
        """Validate signal before execution"""
        # Check confidence threshold
        if signal['confidence'] < self.confidence_threshold:
            return False
        
        # Check risk limits
        if signal['stop_loss_pips'] > 50:
            return False
        
        # Check position limits
        if self.get_open_positions_count() >= self.max_positions:
            return False
        
        return True
```

#### Step 2: Strategy Registration
```python
# In src/strategies/__init__.py
from .my_custom_strategy import MyCustomStrategy

STRATEGIES = {
    'my_custom_strategy': MyCustomStrategy,
    # ... other strategies
}
```

#### Step 3: Configuration
```yaml
# In config/config.yaml
strategies:
  my_custom_strategy:
    enabled: true
    risk_per_trade: 5.0
    lookback_period: 20
    threshold: 0.5
    confidence_threshold: 70.0
```

### Strategy Optimization

#### Parameter Optimization
```python
def optimize_strategy_parameters(self, historical_data):
    """Optimize strategy parameters using historical data"""
    best_params = {}
    best_performance = 0
    
    # Parameter ranges to test
    lookback_periods = range(10, 50, 5)
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    for lookback in lookback_periods:
        for threshold in thresholds:
            # Test parameters
            self.lookback_period = lookback
            self.threshold = threshold
            
            # Run backtest
            performance = self.backtest_strategy(historical_data)
            
            if performance > best_performance:
                best_performance = performance
                best_params = {
                    'lookback_period': lookback,
                    'threshold': threshold
                }
    
    return best_params
```

#### Performance Metrics
```python
def calculate_performance_metrics(self, trades):
    """Calculate strategy performance metrics"""
    if not trades:
        return {}
    
    total_trades = len(trades)
    winning_trades = [t for t in trades if t['profit'] > 0]
    losing_trades = [t for t in trades if t['profit'] < 0]
    
    win_rate = len(winning_trades) / total_trades * 100
    total_profit = sum(t['profit'] for t in trades)
    total_loss = sum(t['profit'] for t in losing_trades)
    
    profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
    
    return {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'total_profit': total_profit,
        'profit_factor': profit_factor,
        'average_win': np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0,
        'average_loss': np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
    }
```

## 🎯 Strategy Testing

### Backtesting Framework
```python
def backtest_strategy(self, historical_data, start_date, end_date):
    """Backtest strategy on historical data"""
    trades = []
    current_positions = []
    
    for timestamp, data_point in historical_data.iterrows():
        if timestamp < start_date or timestamp > end_date:
            continue
        
        # Generate signals
        signals = self.generate_signals(data_point)
        
        # Process signals
        for signal in signals:
            if self.validate_signal(signal):
                # Open position
                position = self.open_position(signal, data_point)
                current_positions.append(position)
        
        # Update existing positions
        for position in current_positions[:]:
            if self.should_close_position(position, data_point):
                # Close position
                trade_result = self.close_position(position, data_point)
                trades.append(trade_result)
                current_positions.remove(position)
    
    return trades
```

### Walk-Forward Analysis
```python
def walk_forward_analysis(self, historical_data, window_size=30):
    """Perform walk-forward analysis"""
    results = []
    
    for i in range(window_size, len(historical_data)):
        # Training period
        training_data = historical_data.iloc[i-window_size:i]
        
        # Optimize parameters
        best_params = self.optimize_strategy_parameters(training_data)
        
        # Test period
        test_data = historical_data.iloc[i:i+1]
        
        # Apply optimized parameters
        self.apply_parameters(best_params)
        
        # Test strategy
        test_results = self.backtest_strategy(test_data)
        results.append(test_results)
    
    return results
```

## 🎯 Strategy Management

### Strategy Factory
```python
class StrategyFactory:
    """Factory for creating strategy instances"""
    
    @staticmethod
    def create_strategy(strategy_name, config):
        """Create strategy instance by name"""
        if strategy_name == 'god_mode_scalping':
            return GodModeScalpingStrategy(config)
        elif strategy_name == 'extreme_rsi':
            return ExtremeRSIStrategy(config)
        elif strategy_name == 'volatility_explosion':
            return VolatilityExplosionStrategy(config)
        elif strategy_name == 'momentum_surge':
            return MomentumSurgeStrategy(config)
        elif strategy_name == 'news_impact':
            return NewsImpactStrategy(config)
        elif strategy_name == 'grid_recovery':
            return GridRecoveryStrategy(config)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
```

### Strategy Portfolio
```python
class StrategyPortfolio:
    """Manage multiple strategies"""
    
    def __init__(self, config):
        self.strategies = {}
        self.config = config
        self.load_strategies()
    
    def load_strategies(self):
        """Load enabled strategies"""
        for strategy_name, strategy_config in self.config['strategies'].items():
            if strategy_config.get('enabled', False):
                strategy = StrategyFactory.create_strategy(strategy_name, strategy_config)
                self.strategies[strategy_name] = strategy
    
    def generate_all_signals(self, data):
        """Generate signals from all strategies"""
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            signals = strategy.generate_signals(data)
            for signal in signals:
                signal['strategy'] = strategy_name
                all_signals.append(signal)
        
        return all_signals
    
    def execute_signals(self, signals, account_info):
        """Execute signals from all strategies"""
        executed_trades = []
        
        for signal in signals:
            if self.validate_signal(signal):
                trade = self.execute_signal(signal, account_info)
                executed_trades.append(trade)
        
        return executed_trades
```

## 🎯 Best Practices

### Strategy Development
1. **Start Simple**: Begin with basic strategies and add complexity gradually
2. **Test Thoroughly**: Always backtest before live trading
3. **Risk Management**: Include proper risk controls in every strategy
4. **Documentation**: Document all strategy logic and parameters
5. **Monitoring**: Implement proper monitoring and alerting

### Performance Optimization
1. **Parameter Tuning**: Regularly optimize strategy parameters
2. **Market Adaptation**: Adjust strategies for changing market conditions
3. **Correlation Analysis**: Avoid over-correlated strategies
4. **Risk Allocation**: Properly allocate risk across strategies
5. **Continuous Improvement**: Monitor and improve strategies continuously

### Risk Management
1. **Position Sizing**: Use proper position sizing for each strategy
2. **Stop Losses**: Always include stop losses
3. **Correlation Limits**: Limit exposure to correlated strategies
4. **Drawdown Control**: Monitor and control drawdown
5. **Emergency Stops**: Implement emergency stop procedures

## 🎯 Troubleshooting

### Common Issues

#### Strategy Not Generating Signals
1. Check data quality and availability
2. Verify strategy parameters
3. Check confidence thresholds
4. Review market conditions

#### Poor Performance
1. Optimize strategy parameters
2. Check for overfitting
3. Review market conditions
4. Consider strategy adaptation

#### High Drawdown
1. Reduce position sizes
2. Tighten stop losses
3. Review risk allocation
4. Check correlation between strategies

### Getting Help
- **Documentation**: [Complete Guide](README.md)
- **Issues**: [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- **Community**: [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)

---

*For advanced strategy development, see [API Reference](api-reference.md)* 