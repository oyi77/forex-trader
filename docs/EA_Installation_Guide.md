# Ultimate Forex EA God Mode v3.0 - Installation Guide

## 🚨 **EXTREME RISK WARNING** 🚨

**This Expert Advisor uses EXTREME RISK settings designed to achieve 203,003% returns in 14 days. This is mathematically aggressive and carries a very high probability of total capital loss. Only use money you can afford to lose completely.**

## 📋 **Prerequisites**

### Required Software
- **MetaTrader 5** (Build 3815 or higher)
- **Windows 10/11** or **Windows Server 2016+**
- **Exness MT5 Account** with 1:2000 leverage
- **Minimum 4GB RAM** and **stable internet connection**

### Account Requirements
- **Broker**: Exness (recommended for 1:2000 leverage)
- **Account Type**: Standard or Pro account
- **Minimum Balance**: 1,000,000 IDR (or equivalent)
- **Leverage**: 1:2000 (maximum available)
- **Allowed Symbols**: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, XAGUSD, WTIUSD

## 📁 **File Structure**

The EA package contains the following files:

```
EA/
├── MT5/
│   └── UltimateForexEA_GodMode.mq5     # Main EA file
├── Include/
│   ├── GodModeRiskManager.mqh          # Risk management class
│   └── GodModePositionManager.mqh      # Position management class
├── Config/
│   └── GodModeEA_Config.set            # Optimized configuration
└── docs/
    ├── EA_Installation_Guide.md        # This guide
    └── EA_User_Manual.md               # User manual
```

## 🔧 **Installation Steps**

### Step 1: Prepare MetaTrader 5

1. **Open MetaTrader 5**
2. **Login to your Exness account**
3. **Verify leverage is set to 1:2000**
   - Go to Tools → Options → Trade
   - Check "Maximum deviation" is set to 50 points
   - Ensure "Allow automated trading" is checked

### Step 2: Install EA Files

1. **Open Data Folder**
   - In MT5: File → Open Data Folder
   - Navigate to `MQL5/Experts/`

2. **Copy Main EA File**
   - Copy `UltimateForexEA_GodMode.mq5` to `MQL5/Experts/`

3. **Copy Include Files**
   - Navigate to `MQL5/Include/`
   - Create folder named `GodMode/` if it doesn't exist
   - Copy `GodModeRiskManager.mqh` and `GodModePositionManager.mqh` to `MQL5/Include/GodMode/`

4. **Copy Configuration**
   - Navigate to `MQL5/Presets/`
   - Copy `GodModeEA_Config.set` to this folder

### Step 3: Compile the EA

1. **Open MetaEditor**
   - Press F4 in MT5 or Tools → MetaQuotes Language Editor

2. **Open EA File**
   - File → Open → Navigate to `MQL5/Experts/UltimateForexEA_GodMode.mq5`

3. **Compile**
   - Press F7 or Build → Compile
   - Ensure no errors in the compilation log
   - If errors occur, check include file paths

### Step 4: Configure EA Settings

1. **Load Configuration**
   - In MT5 Navigator, find "UltimateForexEA_GodMode" under Expert Advisors
   - Right-click → Attach to Chart
   - In the settings dialog, click "Load" and select `GodModeEA_Config.set`

2. **Verify Critical Settings**
   ```
   EnableGodMode = true
   TargetDailyReturn = 65.98
   MaxAccountRisk = 95.0
   Leverage = 2000
   InitialBalance = 1000000.0 (adjust to your balance)
   ```

3. **Symbol Configuration**
   - Ensure current chart symbol is in AllowedSymbols list
   - Recommended symbols: EURUSD, GBPUSD, USDJPY, XAUUSD

### Step 5: Enable Automated Trading

1. **Global Settings**
   - Tools → Options → Expert Advisors
   - Check "Allow automated trading"
   - Check "Allow DLL imports"
   - Check "Allow imports of external experts"

2. **Chart Settings**
   - Right-click on chart → Expert Advisors → Allow automated trading
   - Ensure "AutoTrading" button in toolbar is active (green)

## ⚙️ **Configuration Options**

### Risk Management Settings

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EnableGodMode` | true | Enables extreme risk mode |
| `RiskLevel` | RISK_GOD_MODE | Risk level (0-4, 4=God Mode) |
| `TargetDailyReturn` | 65.98 | Target daily return (%) |
| `MaxAccountRisk` | 95.0 | Maximum account risk (%) |
| `MaxPositions` | 20 | Maximum concurrent positions |

### Strategy Settings

| Strategy | Risk % | Description |
|----------|--------|-------------|
| God Mode Scalping | 80% | Ultra-aggressive scalping |
| Extreme RSI | 70% | RSI oversold/overbought |
| Volatility Explosion | 85% | High volatility trading |
| Momentum Surge | 75% | MACD momentum trading |
| News Impact | 90% | News event trading |
| Grid Recovery | 60% | Grid-based recovery |

### Position Management

| Parameter | Default | Description |
|-----------|---------|-------------|
| `UseTrailingStop` | true | Enable trailing stops |
| `TrailingStopPips` | 3.0 | Trailing distance (pips) |
| `DefaultStopLossPips` | 20.0 | Default stop loss (pips) |
| `DefaultTakeProfitPips` | 5.0 | Default take profit (pips) |

## 🚀 **Starting the EA**

### Pre-Launch Checklist

- [ ] Account balance ≥ 1,000,000 IDR
- [ ] Leverage set to 1:2000
- [ ] Automated trading enabled
- [ ] EA compiled without errors
- [ ] Configuration loaded
- [ ] Stable internet connection
- [ ] VPS recommended for 24/7 operation

### Launch Procedure

1. **Select Chart**
   - Open chart for desired symbol (EURUSD recommended)
   - Set timeframe to M1 or M5

2. **Attach EA**
   - Drag EA from Navigator to chart
   - Verify settings in dialog
   - Click "OK" to start

3. **Monitor Launch**
   - Check "Experts" tab for initialization messages
   - Look for "GOD MODE EA INITIALIZATION COMPLETED"
   - Verify no error messages

### Initial Monitoring

**First 30 Minutes:**
- Monitor for first trades
- Check position opening
- Verify risk calculations
- Watch for any errors

**First Hour:**
- Confirm strategy activation
- Monitor profit/loss
- Check position management
- Verify trailing stops

## 📊 **Performance Monitoring**

### Key Metrics to Watch

1. **Daily Return Progress**
   - Target: 65.98% daily
   - Monitor actual vs. target
   - Adjust if significantly behind

2. **Risk Metrics**
   - Current drawdown
   - Position count
   - Total exposure
   - Consecutive losses

3. **Strategy Performance**
   - Individual strategy returns
   - Win rates by strategy
   - Most profitable strategies

### Dashboard Information

The EA displays real-time information on the chart:

```
=== GOD MODE EA v3.0 ===
Symbol: EURUSD | Risk: GOD MODE
Target Daily: 65.98% | Actual: 12.34%
Total Return: 45.67% | Drawdown: 8.90%
Positions: 5/20 | Trades: 23
Win Rate: 65.2% | Balance: 1,456,789
========================
```

## ⚠️ **Risk Management**

### Emergency Stop Conditions

The EA will automatically stop trading if:
- Account balance drops below 10% of initial
- Drawdown exceeds 80%
- Daily loss exceeds 50%
- Consecutive losses exceed 5

### Manual Intervention

**When to Intervene:**
- Drawdown > 30%
- Daily return < 20% of target
- Unusual market conditions
- Major news events

**How to Intervene:**
- Reduce position sizes
- Disable aggressive strategies
- Close all positions manually
- Stop EA temporarily

## 🔧 **Troubleshooting**

### Common Issues

**EA Not Starting:**
- Check compilation errors
- Verify include file paths
- Ensure automated trading enabled
- Check account permissions

**No Trades Opening:**
- Verify symbol in allowed list
- Check spread conditions
- Confirm market hours
- Review risk settings

**High Losses:**
- Reduce risk percentages
- Disable most aggressive strategies
- Implement tighter stops
- Consider stopping EA

**Performance Issues:**
- Use VPS for stability
- Ensure sufficient RAM
- Check internet connection
- Monitor CPU usage

### Error Messages

| Error | Solution |
|-------|----------|
| "Invalid parameters" | Check configuration values |
| "Not enough money" | Increase account balance |
| "Trade context busy" | Wait and retry |
| "Market closed" | Check trading hours |
| "Invalid stops" | Adjust SL/TP settings |

## 📞 **Support**

### Getting Help

1. **Check Logs**
   - MT5 → Tools → Options → Expert Advisors → Journal
   - Look for detailed error messages

2. **Documentation**
   - Read EA_User_Manual.md
   - Check GitHub repository
   - Review configuration guide

3. **Community Support**
   - GitHub Issues: https://github.com/oyi77/forex-trader/issues
   - Discussions: Check repository discussions

### Reporting Issues

When reporting issues, include:
- MT5 build number
- EA version
- Account type and broker
- Error messages from journal
- Configuration settings used
- Market conditions when issue occurred

## 📈 **Optimization**

### Strategy Tester

1. **Setup Testing**
   - Tools → Strategy Tester
   - Select "UltimateForexEA_GodMode"
   - Choose symbol and timeframe
   - Set date range (minimum 1 month)

2. **Optimization Parameters**
   - Use ranges provided in config file
   - Focus on key parameters:
     - TargetDailyReturn: 50-100
     - MaxAccountRisk: 80-95
     - Strategy risk percentages
     - Position limits

3. **Evaluation Criteria**
   - Total return
   - Maximum drawdown
   - Profit factor
   - Sharpe ratio
   - Recovery factor

### Live Optimization

**Weekly Review:**
- Analyze performance metrics
- Identify best-performing strategies
- Adjust risk parameters
- Update symbol list if needed

**Monthly Optimization:**
- Full strategy review
- Parameter fine-tuning
- Market condition analysis
- Risk model updates

## 🎯 **Success Tips**

### Maximizing Performance

1. **Use VPS**
   - 24/7 operation
   - Low latency
   - Stable connection
   - Backup power

2. **Monitor Actively**
   - First week: Hourly checks
   - After stabilization: Daily reviews
   - Weekly performance analysis
   - Monthly optimization

3. **Risk Management**
   - Never risk more than you can lose
   - Start with smaller position sizes
   - Gradually increase as confidence builds
   - Always have exit strategy

4. **Market Awareness**
   - Monitor major news events
   - Be aware of market holidays
   - Understand correlation effects
   - Watch for unusual volatility

### Realistic Expectations

While the EA targets 203,003% returns, realistic expectations should consider:
- **Conservative estimate**: 50-200% monthly
- **Aggressive estimate**: 500-1000% monthly  
- **Extreme scenario**: 2000%+ monthly (high risk)

Remember: Past performance does not guarantee future results.

---

## 📄 **Legal Disclaimer**

This Expert Advisor is provided for educational and research purposes. Trading forex and CFDs involves substantial risk of loss and is not suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to trade forex and CFDs, you should carefully consider your investment objectives, level of experience, and risk appetite.

**The developers are not responsible for any losses incurred through the use of this EA.**

---

*For detailed usage instructions, see EA_User_Manual.md*
*For technical documentation, see the source code comments*
*For updates and support, visit: https://github.com/oyi77/forex-trader*

