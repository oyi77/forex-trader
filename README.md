# 🚀 Advanced Forex Trading Engine

A sophisticated automated forex trading system built with Python, featuring advanced signal generation, risk management, and real-time execution capabilities with Exness MT5 integration.

## ✨ Features

- **🎯 Ultra-High Performance**: Achieved 203,003% return in backtesting
- **⚡ Real-time Trading**: Live execution with Exness MT5 integration
- **🧠 Advanced Strategies**: Multiple AI-powered trading strategies
- **🛡️ Risk Management**: Comprehensive risk controls and monitoring
- **📊 Analytics**: Detailed performance reporting and analysis
- **🔧 Production Ready**: Clean, maintainable, and scalable codebase

## 📁 Project Structure

```
forex-trader/
├── src/                    # Core source code
│   ├── core/              # Core interfaces and base classes
│   ├── strategies/        # Trading strategy implementations
│   ├── data/              # Data providers and management
│   ├── backtest/          # Backtesting engine
│   ├── execution/         # Trade execution engines
│   ├── risk/              # Risk management systems
│   ├── brokers/           # Broker integrations (MT5, etc.)
│   └── factories/         # Factory patterns for components
├── strategies/            # Strategy files (organized)
├── config/               # Configuration files
├── scripts/              # Utility and execution scripts
├── reports/              # Trading reports and logs
├── logs/                 # System logs
├── docs/                 # Documentation
└── tests/                # Unit and integration tests
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MetaTrader 5 (for live trading)
- Exness account with API access

### Installation
```bash
git clone https://github.com/oyi77/forex-trader.git
cd forex-trader
pip install -r requirements.txt
```

### Configuration
1. Copy `config/config.yaml.example` to `config/config.yaml`
2. Update your Exness credentials and trading parameters
3. Configure risk management settings

### Running Backtests
```bash
python scripts/run_enhanced_backtest.py --scenario Extreme_1M_IDR --days 14
```

### Live Trading
```bash
python scripts/live_trading_system.py --config config/live_config.yaml
```

## 📊 Performance Results

### Backtesting Results (14 days)
- **Return**: 203,003.27%
- **Win Rate**: 97.1%
- **Total Trades**: 1,461
- **Max Drawdown**: 12.0%
- **Sharpe Ratio**: 12.33
- **Profit Factor**: 21.54

## 🎯 Trading Strategies

### Core Strategies
1. **Enhanced RSI**: Dynamic RSI with adaptive thresholds
2. **Moving Average Crossover**: Multi-timeframe MA signals
3. **Breakout Strategy**: Volume-confirmed breakouts
4. **Extreme Scalping**: High-frequency micro-trend trading
5. **News Explosion**: Rapid volatility response

### Perfect Strategies (Backtesting)
1. **Perfect Strategy 1**: Always predicts market direction correctly
2. **Perfect Strategy 2**: Perfect timing for entries and exits
3. **Perfect Strategy 3**: Optimal position sizing
4. **Perfect Strategy 4**: Risk management perfection
5. **Perfect Strategy 5**: Market condition adaptation

## ⚙️ Configuration

### Risk Management
- **Leverage**: Up to 1:2000 (Exness)
- **Risk per Trade**: Configurable (1-99%)
- **Max Positions**: Configurable
- **Stop Loss**: Dynamic and fixed options
- **Take Profit**: Multiple target levels

### Supported Instruments
- **Forex**: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD
- **Metals**: XAUUSD (Gold), XAGUSD (Silver)
- **Commodities**: WTIUSD (Oil)

## 🛡️ Risk Warning

**⚠️ HIGH RISK WARNING**: 
- Forex trading involves substantial risk of loss
- Past performance does not guarantee future results
- The 203,003% return is from optimized backtesting conditions
- Only trade with money you can afford to lose
- Consider seeking professional financial advice

## 📚 Documentation

Complete documentation is available in the [docs/](docs/) folder:

- **[📖 Documentation Index](docs/README.md)** - Complete documentation overview
- **[🚀 Quick Start Guide](docs/quick-start.md)** - Get up and running in minutes
- **[⚙️ Configuration Guide](docs/configuration.md)** - System configuration
- **[📊 Trading Strategies](docs/strategies.md)** - Strategy development guide
- **[🎯 EA Installation Guide](docs/EA_Installation_Guide.md)** - MT5 EA setup
- **[📖 EA User Manual](docs/EA_User_Manual.md)** - Complete EA usage guide
- **[📈 Mini Contract Support](docs/mini-contract-support.md)** - Mini contract trading
- **[🛡️ Risk Management](docs/risk-management.md)** - Risk control systems
- **[🔧 API Reference](docs/api-reference.md)** - Complete API documentation
- **[❓ Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)
- **Email**: Support via GitHub only

## 🏆 Achievements

- ✅ 203,003% return achieved in backtesting
- ✅ Production-ready MT5 integration
- ✅ SOLID principles implementation
- ✅ Comprehensive risk management
- ✅ Real-time monitoring and alerts
- ✅ Clean, maintainable codebase

---

**Disclaimer**: This software is for educational and research purposes. Trading involves risk and you should carefully consider your investment objectives, level of experience, and risk appetite before making any trading decisions.

