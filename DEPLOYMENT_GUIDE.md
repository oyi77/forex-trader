# Forex Trading Bot - Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Bot](#running-the-bot)
5. [Dashboard Access](#dashboard-access)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)

## System Requirements

### Minimum Requirements
- **Operating System**: Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Stable internet connection (minimum 10 Mbps)

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 16GB
- **Storage**: SSD with 50GB free space
- **Network**: High-speed internet (100+ Mbps)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/oyi77/forex-trader.git
cd forex-trader
```

### 2. Install Python Dependencies
```bash
# Install core dependencies
pip install -r requirements_enhanced.txt

# Additional packages for full functionality
pip install ta scikit-learn joblib PyYAML scipy matplotlib plotly pandas numpy
```

### 3. Install Node.js Dependencies (for Dashboard)
```bash
cd trading_dashboard
npm install
cd ../trading-dashboard-frontend
npm install
```

## Configuration

### 1. Basic Configuration
Edit the `config.yaml` file to set your trading parameters:

```yaml
# Risk Management
risk_management:
  max_risk_per_trade: 0.02  # 2% max risk per trade
  max_total_exposure: 0.80  # 80% max portfolio exposure
  stop_loss_pct: 0.015      # 1.5% stop loss
  take_profit_pct: 0.025    # 2.5% take profit

# Trading Parameters
trading_parameters:
  min_confidence: 0.65      # Minimum signal confidence
  max_positions: 5          # Maximum concurrent positions
  position_sizing_method: "kelly_criterion"
  rebalance_frequency: "daily"

# Data Sources
data_sources:
  primary_provider: "twelve_data"
  fallback_providers: ["fcs_api", "free_forex_api"]
  update_frequency: "1min"

# Broker Settings
broker_settings:
  broker_type: "paper_trading"  # Start with paper trading
  account_id: "PAPER_ACCOUNT"
  leverage: 100
```

### 2. API Keys Configuration
Create a `.env` file in the root directory:

```bash
# Data Provider API Keys
TWELVE_DATA_API_KEY=your_twelve_data_api_key
FCS_API_KEY=your_fcs_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# Broker API Keys (when using live trading)
EXNESS_API_KEY=your_exness_api_key
EXNESS_SECRET=your_exness_secret
OANDA_API_KEY=your_oanda_api_key

# Security
SECRET_KEY=your_secret_key_for_dashboard
```

### 3. Database Setup
The bot uses SQLite by default. No additional setup required for basic usage.

For production, consider PostgreSQL:
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Update config.yaml
database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "forex_trading_bot"
  user: "your_username"
  password: "your_password"
```

## Running the Bot

### 1. Paper Trading Mode (Recommended for Testing)
```bash
# Start the main trading bot
python main_enhanced.py

# In another terminal, start the dashboard
cd trading_dashboard
source venv/bin/activate
python src/main.py
```

### 2. Live Trading Mode (Production)
⚠️ **WARNING**: Only use live trading after thorough testing with paper trading.

1. Update `config.yaml` to use your live broker
2. Add real API credentials to `.env`
3. Start with small position sizes
4. Monitor closely for the first few days

```bash
# Update broker settings in config.yaml
broker_settings:
  broker_type: "exness"  # or your preferred broker
  account_id: "your_live_account_id"
  leverage: 50  # Conservative leverage for live trading
```

### 3. Running as a Service (Linux)
Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/forex-trading-bot.service
```

Add the following content:
```ini
[Unit]
Description=Forex Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/forex-trader
ExecStart=/usr/bin/python3 main_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable forex-trading-bot
sudo systemctl start forex-trading-bot
sudo systemctl status forex-trading-bot
```

## Dashboard Access

### 1. Local Development
```bash
# Start Flask backend
cd trading_dashboard
source venv/bin/activate
python src/main.py

# Start React frontend (in another terminal)
cd trading-dashboard-frontend
npm run dev
```

Access the dashboard at: `http://localhost:3000`

### 2. Production Deployment
```bash
# Build React frontend
cd trading-dashboard-frontend
npm run build

# Copy built files to Flask static directory
cp -r dist/* ../trading_dashboard/src/static/

# Start Flask server
cd ../trading_dashboard
source venv/bin/activate
python src/main.py
```

Access the dashboard at: `http://your-server-ip:5000`

### 3. Dashboard Features
- **Real-time Monitoring**: Live P&L, positions, market data
- **Strategy Control**: Enable/disable strategies, adjust parameters
- **Risk Management**: Monitor exposure, VaR, drawdown
- **Performance Analytics**: Detailed charts and statistics
- **Alert System**: Real-time notifications for important events

## Monitoring and Maintenance

### 1. Log Files
Monitor these log files for system health:
- `logs/trading_bot.log` - Main bot activity
- `logs/strategy_performance.log` - Strategy performance
- `logs/risk_management.log` - Risk alerts and actions
- `logs/data_feeds.log` - Data provider status

### 2. Performance Monitoring
Key metrics to monitor:
- **Daily P&L**: Track daily performance
- **Drawdown**: Monitor maximum drawdown
- **Win Rate**: Ensure strategies are performing
- **Sharpe Ratio**: Risk-adjusted returns
- **System Uptime**: Bot availability

### 3. Regular Maintenance Tasks
- **Daily**: Check dashboard for alerts and performance
- **Weekly**: Review strategy performance and adjust if needed
- **Monthly**: Backup configuration and trading data
- **Quarterly**: Full system review and optimization

### 4. Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"

# Backup configuration
cp config.yaml $BACKUP_DIR/config_$DATE.yaml

# Backup database
cp trading_dashboard/src/database/app.db $BACKUP_DIR/database_$DATE.db

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

echo "Backup completed: $DATE"
```

## Troubleshooting

### Common Issues

#### 1. Bot Not Starting
**Symptoms**: Bot fails to start or crashes immediately
**Solutions**:
- Check Python version: `python --version`
- Verify all dependencies: `pip list`
- Check configuration file syntax
- Review error logs in `logs/trading_bot.log`

#### 2. No Trading Signals
**Symptoms**: Bot runs but doesn't generate trades
**Solutions**:
- Check data feed connectivity
- Verify API keys in `.env` file
- Lower minimum confidence threshold
- Check strategy parameters

#### 3. Dashboard Not Loading
**Symptoms**: Cannot access web dashboard
**Solutions**:
- Verify Flask server is running: `ps aux | grep python`
- Check port availability: `netstat -tulpn | grep 5000`
- Review Flask logs for errors
- Ensure firewall allows port 5000

#### 4. High Memory Usage
**Symptoms**: System running out of memory
**Solutions**:
- Reduce data history length
- Optimize strategy calculations
- Increase system RAM
- Monitor for memory leaks

#### 5. API Rate Limits
**Symptoms**: Data feed errors or missing data
**Solutions**:
- Reduce update frequency
- Use multiple data providers
- Upgrade to premium API plans
- Implement request throttling

### Error Codes
- **E001**: Configuration file not found
- **E002**: Invalid API credentials
- **E003**: Database connection failed
- **E004**: Broker connection failed
- **E005**: Insufficient funds for trading
- **E006**: Risk limits exceeded

## Security Considerations

### 1. API Key Security
- Store API keys in `.env` file, never in code
- Use environment variables in production
- Regularly rotate API keys
- Limit API key permissions to minimum required

### 2. Network Security
- Use HTTPS for dashboard access
- Implement firewall rules
- Consider VPN for remote access
- Monitor for unusual network activity

### 3. Access Control
- Use strong passwords for dashboard
- Implement two-factor authentication
- Limit dashboard access to trusted IPs
- Regular security audits

### 4. Data Protection
- Encrypt sensitive configuration data
- Secure backup storage
- Implement data retention policies
- Comply with financial data regulations

### 5. Production Checklist
- [ ] All API keys secured
- [ ] Firewall configured
- [ ] SSL certificates installed
- [ ] Backup system tested
- [ ] Monitoring alerts configured
- [ ] Emergency stop procedures documented
- [ ] Risk limits properly set
- [ ] Paper trading thoroughly tested

## Support and Resources

### Documentation
- [Strategy Development Guide](STRATEGY_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Risk Management Best Practices](RISK_MANAGEMENT.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discord Server: Real-time community support
- Trading Forums: Strategy discussions

### Professional Support
For professional deployment and support:
- Email: support@forex-trading-bot.com
- Consultation: Available for custom implementations
- Training: Workshops for advanced usage

---

**Disclaimer**: Trading forex involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always use proper risk management and never trade with money you cannot afford to lose.

