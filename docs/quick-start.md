# 🚀 Quick Start Guide

Get the Advanced Forex Trading Engine up and running in minutes with this step-by-step guide.

## ⚡ Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **MetaTrader 5**: Latest version
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space

### Broker Account
- **Exness Account**: Recommended for best performance
- **API Access**: Enable API trading in your account
- **Leverage**: 1:2000 recommended for optimal performance
- **Minimum Balance**: $1,000 USD recommended

## 🎯 Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/oyi77/forex-trader.git
cd forex-trader
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Your Settings
1. Copy the example configuration:
```bash
cp config/config.yaml.example config/config.yaml
```

2. Edit `config/config.yaml` with your settings:
```yaml
# Broker Settings
broker:
  name: "Exness"
  account: "YOUR_ACCOUNT_NUMBER"
  password: "YOUR_PASSWORD"
  server: "Exness-Real"

# Trading Settings
trading:
  leverage: 2000
  max_positions: 20
  risk_per_trade: 5.0

# Risk Management
risk:
  max_drawdown: 20.0
  daily_loss_limit: 10.0
  max_account_risk: 95.0
```

### Step 4: Set Up MetaTrader 5 EA
1. Copy EA files to MT5:
```bash
cp -r MT5/Experts/* "C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/Common/Files/MQL5/Experts/"
cp -r MT5/Include/* "C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/Common/Files/MQL5/Include/"
cp -r MT5/Presets/* "C:/Users/YourUser/AppData/Roaming/MetaQuotes/Terminal/Common/Files/MQL5/Presets/"
```

2. Compile the EA in MetaEditor (F7)

## 🎯 First Run

### Option 1: Backtesting (Recommended for Start)
```bash
python scripts/run_enhanced_backtest.py --scenario Conservative_1M_IDR --days 7
```

### Option 2: Live Trading (Advanced Users)
```bash
python scripts/live_trading_system.py --config config/live_config.yaml
```

### Option 3: MT5 EA Only
1. Open MetaTrader 5
2. Navigate to a chart (e.g., EURUSD)
3. Drag `UltimateForexEA_GodMode.mq5` to the chart
4. Load `GodModeEA_Config.set` configuration
5. Enable automated trading

## 📊 Verify Installation

### Check Python System
```bash
python scripts/test_system.py
```

Expected output:
```
✅ System check passed
✅ Dependencies installed
✅ Configuration loaded
✅ MT5 connection available
```

### Check MT5 EA
1. Open MetaEditor (F4 in MT5)
2. Open `UltimateForexEA_GodMode.mq5`
3. Compile (F7)
4. Check for any errors

## 🎯 Quick Configuration

### Conservative Settings (Beginner)
```yaml
risk_per_trade: 2.0
max_positions: 5
leverage: 500
target_daily_return: 10.0
```

### Moderate Settings (Intermediate)
```yaml
risk_per_trade: 5.0
max_positions: 10
leverage: 1000
target_daily_return: 25.0
```

### Aggressive Settings (Advanced)
```yaml
risk_per_trade: 10.0
max_positions: 20
leverage: 2000
target_daily_return: 65.98
```

## 🎯 First Trade

### Using Python System
1. Start the system:
```bash
python scripts/live_trading_system.py
```

2. Monitor the logs:
```
=== GOD MODE EA v3.0 ===
Symbol: EURUSD | Risk: MODERATE
Target Daily: 25.0% | Actual: 0.0%
Total Return: 0.0% | Drawdown: 0.0%
Positions: 0/10 | Trades: 0
========================
```

### Using MT5 EA
1. Attach EA to chart
2. Enable automated trading
3. Monitor Experts tab for messages
4. Check positions in Terminal tab

## 🎯 Monitoring

### Real-time Dashboard
- **Python**: Check logs for real-time updates
- **MT5**: Monitor Experts tab and Terminal
- **Performance**: Track daily returns and drawdown

### Key Metrics to Watch
- **Daily Return**: Progress toward target
- **Drawdown**: Current account risk
- **Win Rate**: Trade success percentage
- **Position Count**: Active trades
- **Balance**: Account equity

## 🎯 Troubleshooting

### Common Issues

#### Python System Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check configuration
python scripts/test_system.py
```

#### MT5 EA Won't Compile
1. Check MetaEditor for errors
2. Verify all include files are present
3. Ensure MT5 is up to date
4. Restart MetaTrader 5

#### No Trades Executing
1. Check automated trading is enabled
2. Verify symbol is in allowed list
3. Check risk management settings
4. Monitor spread and market conditions

### Getting Help
- **Documentation**: [Complete Guide](README.md)
- **Issues**: [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- **Community**: [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)

## 🎯 Next Steps

### For Beginners
1. Start with backtesting to understand the system
2. Use conservative settings initially
3. Monitor performance closely
4. Read [EA User Manual](EA_User_Manual.md)

### For Intermediate Users
1. Experiment with different strategies
2. Optimize settings for your risk tolerance
3. Consider mini contracts for lower risk
4. Review [Risk Management](risk-management.md)

### For Advanced Users
1. Develop custom strategies
2. Optimize for maximum performance
3. Implement advanced risk management
4. Contribute to the project

## ⚠️ Important Notes

### Risk Management
- Start with small position sizes
- Monitor drawdown closely
- Have an exit strategy ready
- Never risk more than you can afford to lose

### Performance Expectations
- Backtesting results may not reflect live performance
- Market conditions change constantly
- Past performance doesn't guarantee future results
- Always use proper risk management

### Support
- Join our community for help and tips
- Report issues with detailed information
- Share your experiences and improvements
- Contribute to make the system better

---

**Ready to start trading?** Follow the steps above and begin your journey with the Advanced Forex Trading Engine!

*For detailed documentation, see [Complete Guide](README.md)* 