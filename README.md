# AI-Driven Trading Engine

A comprehensive, AI-powered trading engine that supports multiple exchanges including **Exness for forex trading**, Binance for cryptocurrency trading, and OANDA for forex trading. The engine features advanced technical analysis, risk management, and real-time monitoring capabilities.

## 🚀 Features

### Multi-Exchange Support
- **Exness MT5 Integration** - Full forex trading support with MetaTrader 5
- **Binance** - Cryptocurrency trading
- **OANDA** - Forex trading
- **Demo Mode** - Safe testing environment for all exchanges

### Advanced Trading Capabilities
- **Real-time Market Data** - Live price feeds and historical data
- **Technical Analysis** - Multiple indicators (RSI, MACD, Bollinger Bands, etc.)
- **AI Signal Generation** - Machine learning-based trading signals
- **Risk Management** - Position sizing, stop-loss, take-profit
- **Performance Monitoring** - Real-time P&L tracking and analytics

### Forex Trading Features (Exness)
- **Major Currency Pairs** - EURUSD, GBPUSD, USDJPY, etc.
- **Lot Size Management** - Configurable position sizes
- **Leverage Support** - Up to 100:1 leverage
- **Spread Monitoring** - Real-time spread analysis
- **Economic Calendar** - News-based trading decisions

### Risk Management
- **Position Sizing** - Risk-based position calculation
- **Stop Loss/Take Profit** - Automatic order management
- **Drawdown Protection** - Maximum loss limits
- **Consecutive Loss Limits** - Trading pause on losses
- **Volatility Monitoring** - Market condition analysis

## 📁 Project Structure

```
trading_engine/
├── main.py                 # Main trading engine
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── core/
│   ├── __init__.py
│   └── strategy_core.py   # Technical analysis strategies
├── data/
│   ├── __init__.py
│   └── data_ingestion.py  # Market data fetching
├── execution/
│   ├── __init__.py
│   ├── execution_engine.py # Order execution
│   └── exness_execution.py # Exness forex execution
├── monitoring/
│   ├── __init__.py
│   └── monitoring.py      # Risk management & monitoring
├── signals/
│   ├── __init__.py
│   └── signal_generator.py # Signal generation logic
├── tests/
│   ├── __init__.py
│   └── test_engine.py     # Test suite
└── demos/
    ├── __init__.py
    ├── demo.py            # General demo
    └── demo_exness.py     # Exness forex demo
```

## 📉 Trading Strategy & Example

The engine uses a multi-factor, technical analysis-based strategy, combining:

- **EMA Crossovers:** Detects trend changes using fast/slow Exponential Moving Averages (e.g., 20/50 EMA).
- **RSI (Relative Strength Index):** Identifies overbought/oversold conditions and momentum shifts.
- **ATR (Average True Range):** Measures volatility for adaptive stop-loss and take-profit levels.
- **Market Structure:** Recognizes Break of Structure (BOS) and Change of Character (CHoCH) for trend confirmation.
- **Order Blocks & Fair Value Gaps:** Finds institutional trading zones and price imbalances.
- **Candlestick Patterns:** Engulfing, pinbars, and doji for entry/exit timing.
- **Divergence:** Detects momentum divergence between price and RSI for early reversal signals.
- **Multi-Timeframe Analysis:** Confirms signals across different timeframes for higher accuracy.
- **Risk Management:** Each trade uses a fixed risk percentage (e.g., 1% of equity), with ATR-based stop-loss and multi-level take-profits.

### Example Trade Flow

1. **Signal Generation:**  
   - EURUSD 1h chart: 20 EMA crosses above 50 EMA (bullish), RSI is 45 (not overbought), bullish order block detected.
   - Signal: **BUY** at 1.1000, Stop Loss (SL) at 1.0980 (ATR-based), Take Profit (TP1) at 1.1020, TP2 at 1.1040.

2. **Position Sizing:**  
   - Account equity: $10,000  
   - Risk per trade: 1% ($100)  
   - Distance to SL: 20 pips (0.0020)  
   - Position size: $100 / 0.0020 = 50,000 units (0.5 lot, for illustration)

3. **Trade Outcome:**  
   - Price hits TP1 (1.1020): Profit = (1.1020 - 1.1000) × 50,000 = $1,000  
   - Price reverses and hits SL: Loss = (1.1000 - 1.0980) × 50,000 = $1,000  
   - With risk management, only $100 is lost (1% of equity), as the position is closed at SL.

### Example Profit/Loss Calculation

| Scenario         | Entry   | SL      | TP1     | Position Size | Result | P/L      |
|------------------|---------|---------|---------|---------------|--------|----------|
| Win (TP1 hit)    | 1.1000  | 1.0980  | 1.1020  | 50,000        | TP1    | +$1,000  |
| Loss (SL hit)    | 1.1000  | 1.0980  | 1.1020  | 50,000        | SL     | -$1,000* |

*With risk management, the actual loss is capped at the predefined risk per trade (e.g., $100).

## 📋 Prerequisites

### For Exness Forex Trading
1. **MetaTrader 5** - Download and install MT5 from [Exness](https://exness.com)
2. **Exness Account** - Create a demo or live account
3. **Python 3.8+** - Required for the trading engine

### For Other Exchanges
- **API Keys** - Required for live trading (optional for demo mode)
- **Python 3.8+** - Required for the trading engine

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading_engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install MetaTrader 5 (for Exness)**
   ```bash
   # On macOS (using Homebrew)
   brew install --cask metatrader5
   
   # On Windows
   # Download from https://exness.com and install manually
   
   # On Linux
   # Use Wine to run MT5
   ```

4. **Configure the engine**
   ```bash
   # Edit config.yaml with your settings
   nano config.yaml
   ```

## ⚙️ Configuration

### Exness Configuration
```yaml
# Exchange Settings
EXCHANGE: "exness"
DEMO_MODE: true  # Set to false for live trading

# Exness MT5 Configuration
EXNESS_LOGIN: "your_exness_login"
EXNESS_PASSWORD: "your_exness_password"
EXNESS_SERVER: "Exness-MT5"  # or "Exness-MT5-Demo" for demo account

# Forex Trading Parameters
FOREX_SYMBOLS: ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
FOREX_LOT_SIZE: 0.01  # Minimum lot size (0.01 = 1000 units)
FOREX_LEVERAGE: 100  # Leverage ratio
FOREX_SPREAD_LIMIT: 50  # Maximum spread in pips
```

### Other Exchange Configuration
```yaml
# Binance Configuration
BINANCE_API_KEY: "your_binance_api_key"
BINANCE_API_SECRET: "your_binance_api_secret"

# OANDA Configuration
OANDA_API_KEY: "your_oanda_api_key"
OANDA_ACCOUNT_ID: "your_oanda_account_id"
```

### Trading Parameters
```yaml
# Risk Management
RISK_PER_TRADE: 0.01  # 1% of equity per trade
MAX_DRAWDOWN_PERCENT: 0.05  # 5% max drawdown
MAX_POSITIONS: 3  # Maximum concurrent positions
MIN_CONFIDENCE: 70  # Minimum signal confidence

# Timeframes
DEFAULT_TIMEFRAMES: ["1h", "30m"]
```

## 🚀 Usage

### Quick Start (Demo Mode)
```bash
# Run the main trading engine
python main.py

# Or run the Exness-specific demo
python demos/demo_exness.py

# Or run the general demo
python demos/demo.py
```

### Exness Forex Trading Demo
```bash
python demos/demo_exness.py
```
Choose from:
1. Test forex data ingestion
2. Test Exness execution engine
3. Run full demo trading cycle

### Live Trading
1. **Set up your Exness account**
   - Create account at [Exness](https://exness.com)
   - Get your login credentials
   - Install MetaTrader 5

2. **Configure live trading**
   ```yaml
   DEMO_MODE: false
   EXNESS_LOGIN: "your_actual_login"
   EXNESS_PASSWORD: "your_actual_password"
   EXNESS_SERVER: "Exness-MT5"  # Use live server
   ```

3. **Run the engine**
   ```bash
   python main.py
   ```

## 📊 Monitoring and Analytics

### Performance Metrics
- **Win Rate** - Percentage of profitable trades
- **Profit Factor** - Ratio of gross profit to gross loss
- **Sharpe Ratio** - Risk-adjusted returns
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Total P&L** - Overall profit/loss

### Real-time Monitoring
- **Position Tracking** - Live position monitoring
- **Risk Alerts** - Automatic risk limit notifications
- **Performance Logging** - Detailed trade history
- **Economic Calendar** - News-based trading decisions

## 🔧 Customization

### Adding New Indicators
```python
# In core/strategy_core.py
def custom_indicator(self, data):
    # Your custom indicator logic
    return indicator_value
```

### Custom Signal Generation
```python
# In signals/signal_generator.py
def custom_signal_strategy(self, data):
    # Your custom signal logic
    return signal
```

### Risk Management Rules
```python
# In monitoring/monitoring.py
def custom_risk_check(self):
    # Your custom risk management logic
    return risk_status
```

## ⚠️ Risk Warnings

### Important Disclaimers
- **Trading involves substantial risk of loss**
- **Past performance does not guarantee future results**
- **Always test in demo mode before live trading**
- **Never risk more than you can afford to lose**

### Risk Management Best Practices
1. **Start with demo trading** - Test all strategies thoroughly
2. **Use proper position sizing** - Never risk more than 1-2% per trade
3. **Set stop losses** - Always use stop-loss orders
4. **Monitor performance** - Regularly review trading results
5. **Stay informed** - Keep up with market news and events

## 🐛 Troubleshooting

### Common Issues

**MetaTrader 5 Connection Issues**
```bash
# Check MT5 installation
# Verify login credentials
# Ensure correct server selection
```

**Data Feed Issues**
```bash
# Check internet connection
# Verify API keys (if using live data)
# Check exchange status
```

**Performance Issues**
```bash
# Reduce number of symbols
# Increase cycle intervals
# Check system resources
```

## 📈 Performance Optimization

### Recommended Settings
- **Demo Mode**: Always test new strategies
- **Risk per Trade**: 1-2% maximum
- **Position Limit**: 3-5 concurrent positions
- **Timeframes**: Use multiple timeframes for confirmation
- **Confidence Threshold**: 70% minimum

### System Requirements
- **CPU**: Multi-core processor recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Network**: Stable internet connection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the configuration examples
- Test in demo mode first
- Consult the documentation

## 🔄 Updates

### Recent Updates
- **Exness MT5 Integration** - Full forex trading support
- **Enhanced Risk Management** - Improved position sizing and monitoring
- **Economic Calendar Integration** - News-based trading decisions
- **Multi-Exchange Support** - Binance, OANDA, and Exness
- **Performance Analytics** - Comprehensive trading metrics

### Planned Features
- **Advanced AI Models** - Deep learning signal generation
- **Portfolio Management** - Multi-asset portfolio optimization
- **Backtesting Engine** - Historical strategy testing
- **Mobile App** - Trading on the go
- **Social Trading** - Copy trading features

---

**Disclaimer**: This software is for educational and research purposes. Trading involves substantial risk of loss. Always test thoroughly in demo mode before live trading. The authors are not responsible for any financial losses incurred through the use of this software.
