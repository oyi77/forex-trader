# Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.11 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space
- **Internet**: Stable broadband connection

### For Live Trading
- **MetaTrader 5**: Latest version
- **Exness Account**: With API access enabled
- **VPS**: Recommended for 24/7 trading

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/oyi77/forex-trader.git
cd forex-trader
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install TA-Lib (Technical Analysis Library)
# On Windows:
pip install TA-Lib

# On macOS:
brew install ta-lib
pip install TA-Lib

# On Ubuntu/Debian:
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

### 4. Install MetaTrader 5 (For Live Trading)
1. Download MT5 from [MetaTrader 5](https://www.metatrader5.com/en/download)
2. Install and create demo account or connect to Exness
3. Enable algorithmic trading in MT5 settings

### 5. Configure the System
```bash
# Copy configuration template
cp config/config.yaml.example config/config.yaml

# Edit configuration file
nano config/config.yaml
```

## Configuration

### Basic Configuration
Edit `config/config.yaml`:

```yaml
# Trading Configuration
trading:
  initial_balance: 1000000  # IDR
  leverage: 2000
  max_risk_per_trade: 0.20  # 20%
  max_positions: 10

# Broker Configuration
broker:
  name: "exness"
  server: "ExnessReal-MT5"
  login: "YOUR_LOGIN"
  password: "YOUR_PASSWORD"

# Risk Management
risk:
  max_drawdown: 0.30  # 30%
  daily_loss_limit: 0.20  # 20%
  stop_loss_pips: 50
  take_profit_pips: 100
```

### Exness Setup
1. Create Exness account at [exness.com](https://exness.com)
2. Verify your account
3. Download MT5 and connect to Exness servers
4. Enable API access in account settings
5. Note your login credentials for configuration

## Verification

### Test Installation
```bash
# Test basic functionality
python scripts/main.py --test

# Run simple backtest
python scripts/run_enhanced_backtest.py --scenario Conservative_1M_IDR --days 7

# Validate MT5 connection (if installed)
python scripts/live_trading_system.py --validate
```

### Expected Output
```
✅ Configuration loaded successfully
✅ Data providers initialized
✅ Strategy factory ready
✅ Risk management active
✅ MT5 connection established
✅ System ready for trading
```

## Troubleshooting

### Common Issues

#### TA-Lib Installation Error
```bash
# On Windows, download wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.4.24-cp311-cp311-win_amd64.whl
```

#### MT5 Connection Issues
1. Ensure MT5 is running
2. Check firewall settings
3. Verify account credentials
4. Enable algorithmic trading in MT5

#### Permission Errors
```bash
# On Linux/macOS, use sudo if needed
sudo pip install -r requirements.txt
```

#### Memory Issues
- Close unnecessary applications
- Increase virtual memory
- Use smaller datasets for testing

### Getting Help
- Check [Troubleshooting Guide](troubleshooting.md)
- Review [GitHub Issues](https://github.com/oyi77/forex-trader/issues)
- Join [GitHub Discussions](https://github.com/oyi77/forex-trader/discussions)

## Next Steps
1. Read [Configuration Guide](configuration.md)
2. Review [Strategy Development](strategies.md)
3. Start with paper trading
4. Gradually move to live trading

## Security Notes
- Never commit credentials to version control
- Use environment variables for sensitive data
- Enable 2FA on your Exness account
- Regularly update passwords
- Monitor account activity

