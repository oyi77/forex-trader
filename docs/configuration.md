# ⚙️ Configuration Guide

Complete guide to configuring the Advanced Forex Trading Engine for optimal performance.

## 📋 Configuration Overview

The system uses multiple configuration files for different components:

- **`config/config.yaml`**: Main Python system configuration
- **`config/live_config.yaml`**: Live trading specific settings
- **`MT5/Presets/GodModeEA_Config.set`**: MT5 EA configuration
- **`MT5/Experts/UltimateForexEA_GodMode.mq5`**: EA input parameters

## 🎯 Main Configuration (`config/config.yaml`)

### Broker Settings
```yaml
broker:
  name: "Exness"                    # Broker name
  account: "12345678"               # Your account number
  password: "your_password"         # Your password
  server: "Exness-Real"             # Server name
  terminal_path: "C:/MetaTrader5/terminal64.exe"  # MT5 path
  enable_api: true                  # Enable API trading
```

### Trading Settings
```yaml
trading:
  leverage: 2000                    # Leverage (1:2000 recommended)
  max_positions: 20                 # Maximum concurrent positions
  risk_per_trade: 5.0              # Risk per trade (%)
  target_daily_return: 65.98        # Target daily return (%)
  use_extreme_position_sizing: true # Enable extreme sizing
  enable_forced_trading: true       # Force trades when no signals
```

### Risk Management
```yaml
risk:
  max_drawdown: 20.0               # Maximum drawdown (%)
  daily_loss_limit: 10.0           # Daily loss limit (%)
  max_account_risk: 95.0           # Maximum account risk (%)
  use_emergency_stop: true         # Enable emergency stop
  emergency_stop_threshold: 80.0   # Emergency stop at 80% loss
```

### Strategy Settings
```yaml
strategies:
  god_mode_scalping:
    enabled: true
    risk_per_trade: 80.0
    min_pip_movement: 0.1
    max_hold_time: 60
    rsi_period: 3
    ema_fast: 2
    ema_slow: 5
    confidence_threshold: 50.0

  extreme_rsi:
    enabled: true
    risk_per_trade: 70.0
    rsi_period: 5
    oversold_level: 15.0
    overbought_level: 85.0
    confidence_boost: 25.0
    use_divergence: true

  volatility_explosion:
    enabled: true
    risk_per_trade: 85.0
    volatility_threshold: 2.0
    lookback_period: 5
    explosion_multiplier: 3.0
    use_volatility_filter: true

  momentum_surge:
    enabled: true
    risk_per_trade: 75.0
    macd_fast: 5
    macd_slow: 13
    macd_signal: 3
    momentum_threshold: 0.0001
    use_momentum_filter: true

  news_impact:
    enabled: true
    risk_per_trade: 90.0
    volatility_multiplier: 2.5
    lookback_bars: 3
    trade_on_news_only: false
    news_time_ranges: "08:30-09:30,13:30-14:30,15:30-16:30"

  grid_recovery:
    enabled: true
    risk_per_trade: 60.0
    grid_spacing: 10.0
    max_grid_levels: 10
    grid_multiplier: 1.5
    use_grid_recovery: true
```

### Position Management
```yaml
position_management:
  max_positions_per_strategy: 5    # Max positions per strategy
  position_size_multiplier: 1.0    # Position size multiplier
  use_compounding: true            # Enable compounding
  compounding_factor: 1.2          # Compounding factor
  use_trailing_stop: true          # Enable trailing stop
  trailing_stop_pips: 3.0         # Trailing stop distance
  use_partial_close: true          # Enable partial close
  partial_close_percent: 50.0      # Partial close percentage
  partial_close_profit_pips: 20.0  # Profit threshold for partial close
```

### Stop Loss & Take Profit
```yaml
stop_loss_take_profit:
  default_stop_loss_pips: 20.0     # Default stop loss
  default_take_profit_pips: 5.0    # Default take profit
  use_dynamic_sltp: true           # Use dynamic SL/TP
  sl_multiplier: 0.5               # Stop loss multiplier
  tp_multiplier: 0.3               # Take profit multiplier
  use_time_based_exit: true        # Time-based exit
  max_hold_time_seconds: 3600      # Maximum hold time
  scalp_max_hold_time: 300         # Scalping hold time
```

### Time & Symbol Filters
```yaml
filters:
  use_time_filter: false           # Enable time filter
  start_hour: 0                   # Start hour (0-23)
  end_hour: 23                    # End hour (0-23)
  allowed_symbols: "EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD,XAUUSD,XAGUSD,WTIUSD,EURUSDm,GBPUSDm,USDJPYm,USDCHFm,USDCADm,AUDUSDm,NZDUSDm,XAUUSDm,XAGUSDm,WTIUSDm"
  max_spread_pips: 10.0           # Maximum spread
  use_correlation_filter: true     # Enable correlation filter
  max_correlation: 0.8            # Maximum correlation
```

### Advanced Settings
```yaml
advanced:
  magic_number: 777777             # Magic number for trades
  trade_comment: "GodMode_EA"      # Trade comment
  enable_detailed_logging: true    # Enable detailed logging
  enable_alerts: true              # Enable alerts
  send_email_alerts: false         # Send email alerts
  enable_statistics: true          # Enable statistics
  use_multi_timeframe: true        # Use multi-timeframe
  higher_timeframe: "H1"           # Higher timeframe
  enable_performance_monitoring: true  # Performance monitoring
  log_level: "INFO"                # Log level (DEBUG, INFO, WARNING, ERROR)
```

## 🎯 Live Trading Configuration (`config/live_config.yaml`)

### Live Trading Specific Settings
```yaml
live_trading:
  enabled: true                    # Enable live trading
  use_real_money: false            # Use real money (set to true for live)
  demo_account: true               # Use demo account
  max_daily_trades: 100           # Maximum daily trades
  max_concurrent_trades: 20       # Maximum concurrent trades
  emergency_stop_enabled: true     # Enable emergency stop
  emergency_stop_threshold: 80.0   # Emergency stop threshold
  
  # Performance monitoring
  performance_check_interval: 60   # Performance check interval (seconds)
  drawdown_warning_threshold: 15.0 # Drawdown warning threshold
  profit_target_threshold: 50.0    # Profit target threshold
  
  # Risk controls
  max_daily_loss: 10.0            # Maximum daily loss (%)
  max_consecutive_losses: 5       # Maximum consecutive losses
  use_dynamic_risk: true          # Use dynamic risk adjustment
  risk_reduction_factor: 0.5      # Risk reduction after losses
```

### Data Provider Settings
```yaml
data_provider:
  type: "exness_mt5"              # Data provider type
  update_interval: 1               # Update interval (seconds)
  use_historical_data: true        # Use historical data
  historical_data_days: 30         # Historical data days
  cache_data: true                 # Cache data locally
  cache_directory: "data/cache"    # Cache directory
```

### Execution Settings
```yaml
execution:
  execution_mode: "live"           # Execution mode (live/demo)
  use_slippage_control: true       # Use slippage control
  max_slippage_pips: 5.0          # Maximum slippage
  use_ecn_execution: true          # Use ECN execution
  retry_failed_orders: true        # Retry failed orders
  max_retry_attempts: 3           # Maximum retry attempts
  retry_delay_seconds: 5          # Retry delay
```

## 🎯 MT5 EA Configuration (`MT5/Presets/GodModeEA_Config.set`)

### God Mode Settings
```
EnableGodMode=1
RiskLevel=4
TargetDailyReturn=65.98
MaxAccountRisk=95.0
UseExtremePositionSizing=1
EnableForcedTrading=1
```

### Account & Broker Settings
```
InitialBalance=1000000.0
Leverage=2000
BrokerName=Exness
CommissionPerLot=0.0
MaxSlippagePips=5.0
UseECNExecution=1
```

### Strategy Selection
```
EnableGodModeScalping=1
EnableExtremeRSI=1
EnableVolatilityExplosion=1
EnableMomentumSurge=1
EnableNewsImpact=1
EnableGridRecovery=1
```

### Position Management
```
MaxPositions=20
MaxPositionsPerStrategy=5
PositionSizeMultiplier=1.0
UseCompounding=1
CompoundingFactor=1.2
```

### Stop Loss & Take Profit
```
DefaultStopLossPips=20.0
DefaultTakeProfitPips=5.0
UseDynamicSLTP=1
SLMultiplier=0.5
TPMultiplier=0.3
UseTrailingStop=1
TrailingStopPips=3.0
```

### Time & Symbol Filters
```
UseTimeFilter=0
StartHour=0
EndHour=23
AllowedSymbols=EURUSD,GBPUSD,USDJPY,USDCHF,USDCAD,AUDUSD,NZDUSD,XAUUSD,XAGUSD,WTIUSD,EURUSDm,GBPUSDm,USDJPYm,USDCHFm,USDCADm,AUDUSDm,NZDUSDm,XAUUSDm,XAGUSDm,WTIUSDm
MaxSpreadPips=10.0
```

### Advanced Settings
```
MagicNumber=777777
TradeComment=GodMode_EA
EnableDetailedLogging=1
EnableAlerts=1
SendEmailAlerts=0
EnableStatistics=1
UseMultiTimeframe=1
HigherTimeframe=16385
```

## 🎯 Configuration Profiles

### Conservative Profile (Beginner)
```yaml
trading:
  leverage: 500
  max_positions: 5
  risk_per_trade: 2.0
  target_daily_return: 10.0

risk:
  max_drawdown: 10.0
  daily_loss_limit: 5.0
  max_account_risk: 50.0

strategies:
  god_mode_scalping:
    enabled: false
  extreme_rsi:
    enabled: true
    risk_per_trade: 30.0
  volatility_explosion:
    enabled: false
  momentum_surge:
    enabled: true
    risk_per_trade: 25.0
  news_impact:
    enabled: false
  grid_recovery:
    enabled: true
    risk_per_trade: 20.0
```

### Moderate Profile (Intermediate)
```yaml
trading:
  leverage: 1000
  max_positions: 10
  risk_per_trade: 5.0
  target_daily_return: 25.0

risk:
  max_drawdown: 15.0
  daily_loss_limit: 8.0
  max_account_risk: 75.0

strategies:
  god_mode_scalping:
    enabled: true
    risk_per_trade: 40.0
  extreme_rsi:
    enabled: true
    risk_per_trade: 35.0
  volatility_explosion:
    enabled: true
    risk_per_trade: 45.0
  momentum_surge:
    enabled: true
    risk_per_trade: 30.0
  news_impact:
    enabled: true
    risk_per_trade: 50.0
  grid_recovery:
    enabled: true
    risk_per_trade: 25.0
```

### Aggressive Profile (Advanced)
```yaml
trading:
  leverage: 2000
  max_positions: 20
  risk_per_trade: 10.0
  target_daily_return: 65.98

risk:
  max_drawdown: 20.0
  daily_loss_limit: 10.0
  max_account_risk: 95.0

strategies:
  god_mode_scalping:
    enabled: true
    risk_per_trade: 80.0
  extreme_rsi:
    enabled: true
    risk_per_trade: 70.0
  volatility_explosion:
    enabled: true
    risk_per_trade: 85.0
  momentum_surge:
    enabled: true
    risk_per_trade: 75.0
  news_impact:
    enabled: true
    risk_per_trade: 90.0
  grid_recovery:
    enabled: true
    risk_per_trade: 60.0
```

## 🎯 Mini Contract Configuration

### Mini Contract Settings
```yaml
mini_contracts:
  enabled: true                    # Enable mini contract support
  multiplier: 0.1                  # Mini contract multiplier
  max_positions_multiplier: 3.0    # Position limit multiplier
  risk_threshold_multiplier: 0.5   # Risk threshold multiplier
  profit_threshold_multiplier: 0.5 # Profit threshold multiplier
  
  # Supported mini contracts
  supported_symbols:
    - "EURUSDm"
    - "GBPUSDm"
    - "USDJPYm"
    - "USDCHFm"
    - "USDCADm"
    - "AUDUSDm"
    - "NZDUSDm"
    - "XAUUSDm"
    - "XAGUSDm"
    - "WTIUSDm"
```

## 🎯 Environment-Specific Configuration

### Development Environment
```yaml
environment: "development"
logging:
  level: "DEBUG"
  file: "logs/dev.log"
  console: true

trading:
  use_demo_account: true
  max_positions: 5
  risk_per_trade: 1.0
```

### Testing Environment
```yaml
environment: "testing"
logging:
  level: "INFO"
  file: "logs/test.log"
  console: false

trading:
  use_demo_account: true
  max_positions: 10
  risk_per_trade: 2.0
```

### Production Environment
```yaml
environment: "production"
logging:
  level: "WARNING"
  file: "logs/prod.log"
  console: false

trading:
  use_demo_account: false
  max_positions: 20
  risk_per_trade: 5.0
```

## 🎯 Configuration Validation

### Python System Validation
```bash
python scripts/test_system.py --validate-config
```

### MT5 EA Validation
1. Open MetaEditor (F4 in MT5)
2. Open `UltimateForexEA_GodMode.mq5`
3. Check for compilation errors
4. Verify all parameters are valid

### Configuration Check Script
```python
# config_validator.py
import yaml
import sys

def validate_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required fields
    required_fields = ['broker', 'trading', 'risk']
    for field in required_fields:
        if field not in config:
            print(f"ERROR: Missing required field '{field}'")
            return False
    
    # Validate broker settings
    broker = config['broker']
    if not broker.get('account') or not broker.get('password'):
        print("ERROR: Missing broker credentials")
        return False
    
    # Validate trading settings
    trading = config['trading']
    if trading.get('leverage', 0) <= 0:
        print("ERROR: Invalid leverage setting")
        return False
    
    print("✅ Configuration validation passed")
    return True

if __name__ == "__main__":
    validate_config('config/config.yaml')
```

## 🎯 Configuration Best Practices

### Security
- Never commit credentials to version control
- Use environment variables for sensitive data
- Regularly rotate passwords and API keys
- Use demo accounts for testing

### Performance
- Start with conservative settings
- Gradually increase risk as you gain experience
- Monitor performance closely
- Adjust settings based on market conditions

### Risk Management
- Always set maximum drawdown limits
- Use stop losses on all trades
- Monitor daily loss limits
- Have emergency stop procedures

### Maintenance
- Regularly backup configuration files
- Document custom settings
- Version control configuration changes
- Test configuration changes before live use

## 🎯 Troubleshooting Configuration

### Common Issues

#### Invalid Configuration
```bash
# Check configuration syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

#### Missing Dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### MT5 Connection Issues
1. Verify MT5 is running
2. Check terminal path in configuration
3. Ensure API trading is enabled
4. Verify account credentials

#### Performance Issues
1. Check system resources
2. Reduce update frequency
3. Optimize logging settings
4. Use appropriate risk settings

### Getting Help
- **Documentation**: [Complete Guide](README.md)
- **Issues**: [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- **Community**: [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)

---

*For advanced configuration options, see [API Reference](api-reference.md)* 