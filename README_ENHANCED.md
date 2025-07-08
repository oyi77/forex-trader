# 🚀 Advanced AI Forex Trading Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

An advanced, AI-powered forex trading bot with comprehensive risk management, multiple trading strategies, and a professional web dashboard for monitoring and control.

## 🎯 Key Features

### 🤖 AI-Enhanced Trading Engine
- **Machine Learning Integration**: Ensemble models for signal validation
- **Multiple Strategy Support**: RSI Mean Reversion, MA Crossover, Breakout strategies
- **Adaptive Position Sizing**: Kelly Criterion, Volatility-adjusted, Risk Parity
- **Real-time Signal Generation**: Advanced technical analysis with confidence scoring

### 🛡️ Advanced Risk Management
- **Multi-level Risk Controls**: Per-trade, portfolio, and correlation limits
- **Dynamic Position Sizing**: Automatically adjusts based on market conditions
- **Value at Risk (VaR)**: Real-time risk monitoring and alerts
- **Emergency Stop System**: Automatic position closure on excessive drawdown

### 📊 Professional Dashboard
- **Real-time Monitoring**: Live P&L, positions, and market data
- **Interactive Charts**: Equity curves, performance analytics, risk visualization
- **Strategy Control**: Enable/disable strategies, adjust parameters
- **Alert System**: Real-time notifications for important events

### 🔄 Comprehensive Backtesting
- **Historical Performance Analysis**: Test strategies on historical data
- **Walk-forward Optimization**: Robust parameter optimization
- **Strategy Comparison**: Side-by-side performance evaluation
- **Risk-adjusted Metrics**: Sharpe ratio, Sortino ratio, Calmar ratio

### 🌐 Multi-broker Support
- **Paper Trading**: Risk-free testing environment
- **Live Trading**: Support for major forex brokers
- **API Integration**: Seamless broker connectivity
- **Execution Management**: Slippage control and order optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 14+ (for dashboard)
- Stable internet connection
- Forex broker account (for live trading)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/oyi77/forex-trader.git
   cd forex-trader
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements_enhanced.txt
   
   # Additional packages
   pip install ta scikit-learn joblib PyYAML scipy matplotlib plotly
   ```

3. **Configure the Bot**
   ```bash
   # Copy example configuration
   cp config.example.yaml config.yaml
   
   # Edit configuration (see Configuration section)
   nano config.yaml
   ```

4. **Start Paper Trading**
   ```bash
   # Start the trading bot
   python main_enhanced.py
   
   # In another terminal, start the dashboard
   cd trading_dashboard
   python src/main.py
   ```

5. **Access Dashboard**
   Open your browser and navigate to `http://localhost:5000`

## 📋 Configuration

### Basic Configuration
Edit `config.yaml` to customize your trading parameters:

```yaml
# Risk Management
risk_management:
  max_risk_per_trade: 0.02      # 2% max risk per trade
  max_total_exposure: 0.80      # 80% max portfolio exposure
  stop_loss_pct: 0.015          # 1.5% stop loss
  take_profit_pct: 0.025        # 2.5% take profit

# Trading Parameters
trading_parameters:
  min_confidence: 0.65          # Minimum signal confidence
  max_positions: 5              # Maximum concurrent positions
  position_sizing_method: "kelly_criterion"

# Broker Settings (Start with paper trading)
broker_settings:
  broker_type: "paper_trading"
  initial_balance: 10000
  leverage: 100
```

### API Keys
Create a `.env` file for your API credentials:

```bash
# Data Provider API Keys
TWELVE_DATA_API_KEY=your_api_key
FCS_API_KEY=your_api_key

# Broker API Keys (for live trading)
EXNESS_API_KEY=your_api_key
OANDA_API_KEY=your_api_key
```

## 🎛️ Dashboard Features

### Main Dashboard
- **Portfolio Overview**: Real-time P&L, equity curve, position distribution
- **Performance Metrics**: Win rate, Sharpe ratio, maximum drawdown
- **Quick Controls**: Start/stop bot, emergency stop, refresh data

### Trading Interface
- **Live Market Data**: Real-time price feeds and technical indicators
- **Position Management**: View and manage open positions
- **Trade History**: Detailed trade log with performance analysis
- **Strategy Signals**: Real-time signal generation and confidence scores

### Risk Management
- **Risk Metrics**: VaR, exposure limits, correlation analysis
- **Alert System**: Real-time risk warnings and notifications
- **Limit Monitoring**: Visual representation of risk limit usage
- **Emergency Controls**: Quick position closure and risk reduction

### Strategy Management
- **Strategy Control**: Enable/disable individual strategies
- **Performance Comparison**: Side-by-side strategy analysis
- **Parameter Adjustment**: Real-time strategy configuration
- **Confidence Monitoring**: Track signal quality and reliability

## 📈 Trading Strategies

### 1. RSI Mean Reversion
- **Concept**: Trades overbought/oversold conditions
- **Best For**: Range-bound markets
- **Key Parameters**: RSI period (14), overbought (70), oversold (30)
- **Risk Level**: Medium

### 2. Moving Average Crossover
- **Concept**: Trades trend changes via MA crossovers
- **Best For**: Trending markets
- **Key Parameters**: Fast MA (10), Slow MA (20), Trend filter (50)
- **Risk Level**: Low-Medium

### 3. Breakout Strategy
- **Concept**: Trades breakouts from consolidation
- **Best For**: Volatile markets
- **Key Parameters**: Lookback period (20), ATR threshold (1.5)
- **Risk Level**: Medium-High

### AI Enhancement
All strategies are enhanced with:
- **Machine Learning Validation**: Ensemble models filter signals
- **Confidence Scoring**: Each signal receives a confidence score
- **Market Regime Detection**: Strategies adapt to market conditions
- **Dynamic Parameters**: Self-adjusting based on performance

## 🛡️ Risk Management

### Position Sizing Methods
1. **Kelly Criterion**: Optimal size based on win rate and risk/reward
2. **Volatility Adjusted**: Adjusts for market volatility
3. **Risk Parity**: Equal risk allocation across positions
4. **Fixed Size**: Consistent position sizing

### Risk Controls
- **Per-Trade Limits**: Maximum loss per individual trade
- **Portfolio Limits**: Total exposure and correlation controls
- **Drawdown Protection**: Automatic trading halt on excessive losses
- **Emergency Stop**: Manual override for immediate position closure

### Monitoring
- **Real-time VaR**: Value at Risk calculation and monitoring
- **Correlation Analysis**: Prevents over-concentration in correlated pairs
- **Stress Testing**: Regular portfolio stress tests
- **Alert System**: Immediate notifications for risk breaches

## 📊 Performance Analytics

### Key Metrics
- **Total Return**: Overall profitability
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss

### Visualization
- **Equity Curve**: Account balance over time
- **Drawdown Chart**: Underwater equity curve
- **Monthly Returns**: Calendar heat map
- **Strategy Attribution**: Individual strategy performance

### Backtesting
- **Historical Analysis**: Test on years of historical data
- **Walk-forward Testing**: Robust out-of-sample validation
- **Monte Carlo Simulation**: Statistical performance analysis
- **Strategy Optimization**: Parameter optimization with overfitting protection

## 🔧 Advanced Features

### Data Management
- **Multiple Providers**: Twelve Data, FCS API, Alpha Vantage
- **Failover System**: Automatic switching between providers
- **Data Validation**: Quality checks and error handling
- **Historical Storage**: Local database for backtesting

### Execution Engine
- **Smart Order Routing**: Optimal execution across brokers
- **Slippage Control**: Minimize market impact
- **Latency Optimization**: Fast signal-to-execution pipeline
- **Error Handling**: Robust error recovery and logging

### Monitoring & Alerts
- **System Health**: Monitor bot status and connectivity
- **Performance Alerts**: Notifications for significant events
- **Risk Warnings**: Immediate alerts for risk breaches
- **Custom Notifications**: Configurable alert system

## 📚 Documentation

- **[User Manual](USER_MANUAL.md)**: Comprehensive usage guide
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Production deployment instructions
- **[API Reference](API_REFERENCE.md)**: Complete API documentation
- **[Strategy Guide](STRATEGY_GUIDE.md)**: Strategy development guide

## 🚨 Important Disclaimers

### Risk Warning
- **High Risk**: Forex trading involves substantial risk of loss
- **No Guarantees**: Past performance does not guarantee future results
- **Capital Risk**: Never trade with money you cannot afford to lose
- **Professional Advice**: Consider consulting with financial professionals

### Usage Recommendations
1. **Start with Paper Trading**: Test thoroughly before live trading
2. **Conservative Approach**: Begin with low leverage and small positions
3. **Continuous Monitoring**: Regularly review performance and adjust parameters
4. **Risk Management**: Always use proper risk controls and position sizing

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/oyi77/forex-trader.git
cd forex-trader

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Start development environment
python main_enhanced.py --dev
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the comprehensive guides in the `/docs` folder
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions
- **Email**: For professional support, contact support@forex-trading-bot.com

## 🙏 Acknowledgments

- **Technical Analysis Library**: [TA-Lib](https://github.com/mrjbq7/ta-lib)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/)
- **Web Framework**: [Flask](https://flask.palletsprojects.com/)
- **Frontend**: [React](https://reactjs.org/)
- **Charting**: [Plotly](https://plotly.com/)

---

**⚠️ Trading Disclaimer**: This software is provided for educational and research purposes only. Trading forex involves substantial risk of loss and is not suitable for all investors. The developers are not responsible for any financial losses incurred through the use of this software. Always conduct thorough testing and use proper risk management techniques.

**🔒 Security Note**: Keep your API keys secure and never share them publicly. Use environment variables for sensitive configuration data.

**📈 Performance Note**: Results may vary based on market conditions, configuration settings, and execution environment. Regular monitoring and adjustment of parameters is recommended for optimal performance.

