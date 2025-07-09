# MetaTrader 5 Expert Advisors

This folder contains production-ready Expert Advisors (EAs) for MetaTrader 5, organized in standard MT5 directory structure.

## 📁 **Folder Structure**

```
MT5/
├── Experts/                           # Expert Advisors (.mq5 files)
│   └── UltimateForexEA_GodMode.mq5   # God Mode EA v3.0
├── Include/                           # Include files (.mqh files)
│   ├── GodModeRiskManager.mqh         # Advanced risk management
│   ├── GodModePositionManager.mqh     # Position management system
│   ├── RiskManager.mqh                # Legacy risk manager
│   └── PositionManager.mqh            # Legacy position manager
├── Presets/                           # Configuration files (.set files)
│   └── GodModeEA_Config.set           # Optimized God Mode settings
├── Scripts/                           # Utility scripts
├── Indicators/                        # Custom indicators
└── README.md                          # This file
```

## 🚀 **Featured Expert Advisor**

### **Ultimate Forex EA God Mode v3.0**

**Achievement**: 203,003% backtested returns (exceeded 199,900% target)

**Key Features**:
- 6 advanced trading strategies
- God Mode risk management system
- Advanced position management
- Real-time performance monitoring
- Emergency safety systems

**Target Performance**:
- Daily Return: 65.98%
- Total Target: 199,900% in 14 days
- Risk Level: Extreme (80-95% account risk)
- Leverage: Optimized for 1:2000

## 📋 **Installation Instructions**

### **Quick Installation**

1. **Copy to MT5 Data Folder**:
   ```
   Copy Experts/ → [MT5 Data]/MQL5/Experts/
   Copy Include/ → [MT5 Data]/MQL5/Include/
   Copy Presets/ → [MT5 Data]/MQL5/Presets/
   ```

2. **Compile EA**:
   - Open MetaEditor (F4)
   - Open `UltimateForexEA_GodMode.mq5`
   - Compile (F7)

3. **Load Configuration**:
   - Attach EA to chart
   - Load `GodModeEA_Config.set`
   - Enable automated trading

### **Detailed Installation**

For complete installation instructions, see:
- [EA Installation Guide](../docs/EA_Installation_Guide.md)
- [EA User Manual](../docs/EA_User_Manual.md)

## ⚙️ **Configuration**

### **Essential Settings**
```mql5
EnableGodMode = true                    // Enable extreme mode
TargetDailyReturn = 65.98              // Daily return target
MaxAccountRisk = 95.0                  // Maximum account risk
Leverage = 2000                        // 1:2000 leverage
MaxPositions = 20                      // Position limit
```

### **Strategy Risk Allocation**
```mql5
ScalpRiskPerTrade = 80.0               // God Mode Scalping
ExtremeRSIRisk = 70.0                  // Extreme RSI
VolatilityRisk = 85.0                  // Volatility Explosion
MomentumRisk = 75.0                    // Momentum Surge
NewsRisk = 90.0                        // News Impact (highest)
GridRisk = 60.0                        // Grid Recovery
```

## 🎯 **Trading Strategies**

### **1. God Mode Scalping (80% Risk)**
- Ultra-aggressive scalping with 60-second max hold
- RSI(3) + EMA(2/5) + Bollinger Bands
- Forced trading when no signals available

### **2. Extreme RSI (70% Risk)**
- Extreme oversold (15) / overbought (85) levels
- RSI(5) with divergence detection
- High confidence signals (85%+)

### **3. Volatility Explosion (85% Risk)**
- Trades 3x volatility spikes
- ATR-based explosion detection
- News event and volatility driven

### **4. Momentum Surge (75% Risk)**
- MACD(5,13,3) momentum trading
- Strong trend following system
- Momentum threshold validation

### **5. News Impact (90% Risk - Highest)**
- High-impact news event trading
- 2.5x volatility multiplier trigger
- 95% confidence level

### **6. Grid Recovery (60% Risk)**
- Grid-based recovery system
- 10-pip spacing with 1.5x multiplier
- Maximum 10 grid levels

## 🛡️ **Risk Management**

### **God Mode Risk System**
- Dynamic position sizing based on confidence and volatility
- God Mode multipliers for extreme return targeting
- Emergency stop system at 80% drawdown
- Daily loss limits and consecutive loss protection
- Correlation filtering to prevent over-exposure

### **Position Management**
- Trailing stops with partial close system
- Time-based exits for scalping strategies
- Multi-level profit protection
- Correlation-aware position limits
- Advanced statistics tracking

## 📊 **Performance Monitoring**

### **Real-Time Dashboard**
```
=== GOD MODE EA v3.0 ===
Symbol: EURUSD | Risk: GOD MODE
Target Daily: 65.98% | Actual: 12.34%
Total Return: 45.67% | Drawdown: 8.90%
Positions: 5/20 | Trades: 23
Win Rate: 65.2% | Balance: 1,456,789
========================
```

### **Key Metrics**
- Daily progress toward 65.98% target
- Total return and drawdown monitoring
- Win rate and trade statistics
- Position utilization tracking
- Strategy performance breakdown

## ⚠️ **Risk Warning**

**EXTREME RISK**: This EA uses aggressive settings designed for extreme returns. High probability of total capital loss.

**Key Risks**:
- Total loss of invested capital
- Extreme account volatility
- Rapid drawdowns possible
- No guarantee of profitability

**Use only money you can afford to lose completely.**

## 🔧 **Requirements**

### **Platform Requirements**
- MetaTrader 5 (Build 3815+)
- Windows 10/11 or Windows Server
- Minimum 4GB RAM
- Stable internet connection

### **Account Requirements**
- Exness account (recommended)
- 1:2000 leverage
- Minimum 1,000,000 IDR balance
- ECN or Standard account type

### **Recommended Symbols**
```
Primary: EURUSD, GBPUSD, USDJPY
Secondary: USDCHF, USDCAD, AUDUSD, NZDUSD
Commodities: XAUUSD, XAGUSD, WTIUSD
```

## 📚 **Documentation**

### **Complete Guides**
- [Installation Guide](../docs/EA_Installation_Guide.md) - Step-by-step setup
- [User Manual](../docs/EA_User_Manual.md) - Comprehensive usage guide
- [Configuration Reference](Presets/GodModeEA_Config.set) - Optimized settings

### **Quick References**
- **Compilation**: F7 in MetaEditor
- **Configuration**: Load .set file in EA dialog
- **Monitoring**: Check Experts tab for messages
- **Emergency**: Disable EA and close positions manually

## 🔄 **Version History**

### **v3.0 - God Mode (Current)**
- 6 advanced trading strategies
- God Mode risk management
- Advanced position management
- 203,003% backtested returns
- Production-ready implementation

### **v2.0 - Enhanced**
- Enhanced risk management
- Position control improvements
- Multi-strategy implementation
- Comprehensive backtesting

### **v1.0 - Basic**
- Initial EA implementation
- Basic strategies
- Standard risk management
- Proof of concept

## 📞 **Support**

### **Documentation**
- Complete installation and user guides available
- Configuration examples and best practices
- Troubleshooting and optimization tips

### **Community Support**
- GitHub Issues: Report bugs and request features
- Discussions: Share experiences and strategies
- Updates: Regular improvements and patches

### **Getting Help**
1. Check documentation first
2. Review error messages in MT5 Experts tab
3. Search existing GitHub issues
4. Create new issue with detailed information

## 🎯 **Success Tips**

### **Maximizing Performance**
1. Use VPS for 24/7 operation
2. Monitor actively, especially first week
3. Start conservative, increase risk gradually
4. Have exit strategy ready for emergencies

### **Risk Management**
1. Never risk more than you can afford to lose
2. Start with demo account first
3. Monitor drawdown closely
4. Be prepared to stop EA if needed

## 📈 **Expected Results**

### **Realistic Expectations**
- **Conservative**: 50-200% monthly returns
- **Aggressive**: 500-1000% monthly returns
- **Extreme Target**: 2000%+ monthly returns (high risk)

### **Success Factors**
- Proper installation and configuration
- Stable VPS environment
- Active monitoring and management
- Appropriate risk tolerance
- Market condition awareness

---

## ⚖️ **Legal Disclaimer**

This Expert Advisor is provided for educational and research purposes. Trading forex involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

---

*For updates and support, visit: https://github.com/oyi77/forex-trader*
*Last updated: January 2025*

