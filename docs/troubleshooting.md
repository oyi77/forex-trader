# ❓ Troubleshooting Guide

Complete guide to resolving common issues with the Advanced Forex Trading Engine.

## 🎯 Quick Diagnosis

### System Status Check
```bash
python scripts/test_system.py
```

Expected output:
```
✅ System check passed
✅ Dependencies installed
✅ Configuration loaded
✅ MT5 connection available
✅ Risk management active
✅ Strategies loaded
```

## 🚨 Common Issues & Solutions

### 1. Installation Issues

#### Python Dependencies Not Installing
**Symptoms**: `ModuleNotFoundError` or import errors
**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Install dependencies with force
pip install -r requirements.txt --force-reinstall

# Check Python version (requires 3.11+)
python --version
```

#### MT5 Connection Issues
**Symptoms**: "Failed to connect to MT5" or connection timeouts
**Solution**:
1. **Verify MT5 is running**
2. **Check terminal path in config**:
```yaml
broker:
  terminal_path: "C:/MetaTrader5/terminal64.exe"  # Update this path
```
3. **Enable API trading in MT5**:
   - Tools → Options → Expert Advisors
   - Enable "Allow automated trading"
   - Enable "Allow DLL imports"

#### Configuration Errors
**Symptoms**: "Invalid configuration" or missing parameters
**Solution**:
```bash
# Validate configuration
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Check required fields
python scripts/validate_config.py
```

### 2. Trading Issues

#### No Trades Executing
**Symptoms**: System running but no positions opened
**Possible Causes**:
1. **Automated trading disabled**
   - Check MT5: AutoTrading button should be green
   - Check EA settings: "Allow live trading" enabled

2. **Symbol not in allowed list**
   - Check `AllowedSymbols` in configuration
   - Add your symbol to the list

3. **Risk management blocking trades**
   - Check daily loss limits
   - Check maximum positions
   - Check drawdown limits

4. **No signals generated**
   - Check strategy parameters
   - Verify market data quality
   - Check confidence thresholds

**Solution**:
```python
# Enable debug logging
logging:
  level: "DEBUG"
  console: true

# Check signal generation
python scripts/debug_signals.py
```

#### Frequent Stop Outs
**Symptoms**: Positions closing quickly at stop loss
**Possible Causes**:
1. **Stop loss too tight**
   - Increase `DefaultStopLossPips`
   - Use ATR-based stops

2. **High market volatility**
   - Reduce position sizes
   - Use volatility-adjusted stops

3. **Poor entry timing**
   - Review strategy logic
   - Check market conditions

**Solution**:
```yaml
stop_loss_take_profit:
  default_stop_loss_pips: 30.0     # Increase from 20.0
  use_dynamic_sltp: true           # Enable dynamic stops
  sl_multiplier: 1.0               # Increase multiplier
```

#### Poor Performance
**Symptoms**: Low win rate or negative returns
**Possible Causes**:
1. **Strategy overfitting**
   - Reduce strategy complexity
   - Use walk-forward analysis

2. **Market conditions changed**
   - Adapt strategy parameters
   - Check market regime

3. **Risk management too conservative**
   - Adjust position sizing
   - Review risk parameters

**Solution**:
```bash
# Run strategy optimization
python scripts/optimize_strategies.py

# Analyze performance
python scripts/analyze_performance.py
```

### 3. MT5 EA Issues

#### EA Won't Compile
**Symptoms**: Compilation errors in MetaEditor
**Solution**:
1. **Check include files**:
   - Verify all `.mqh` files are in Include folder
   - Check file paths in includes

2. **Check syntax errors**:
   - Review error messages
   - Fix syntax issues

3. **Update MT5**:
   - Download latest MT5 version
   - Restart MetaEditor

#### EA Not Attaching to Chart
**Symptoms**: EA won't attach or shows errors
**Solution**:
1. **Check chart settings**:
   - Enable "Allow DLL imports"
   - Enable "Allow external experts imports"

2. **Check EA permissions**:
   - Right-click EA → Properties
   - Enable "Allow live trading"
   - Enable "Allow DLL imports"

3. **Check symbol settings**:
   - Verify symbol is available
   - Check symbol properties

#### EA Not Trading
**Symptoms**: EA attached but no trades
**Solution**:
1. **Check EA settings**:
   - Verify "Allow live trading" is enabled
   - Check "AllowedSymbols" includes current symbol

2. **Check account settings**:
   - Verify demo/live account selection
   - Check leverage settings

3. **Check risk settings**:
   - Review risk parameters
   - Check position limits

### 4. Performance Issues

#### High CPU Usage
**Symptoms**: System running slowly or freezing
**Solution**:
```yaml
# Reduce update frequency
data_provider:
  update_interval: 5               # Increase from 1

# Optimize logging
logging:
  level: "WARNING"                 # Reduce from INFO
  console: false                   # Disable console output
```

#### Memory Issues
**Symptoms**: Out of memory errors
**Solution**:
```yaml
# Reduce data cache
data_provider:
  cache_data: false                # Disable caching
  historical_data_days: 7          # Reduce from 30

# Limit position tracking
position_management:
  max_positions: 10                # Reduce from 20
```

#### Slow Execution
**Symptoms**: Delayed trade execution
**Solution**:
1. **Use VPS for trading**
2. **Optimize network connection**
3. **Reduce strategy complexity**
4. **Use ECN execution**

### 5. Risk Management Issues

#### High Drawdown
**Symptoms**: Account losing money rapidly
**Solution**:
```yaml
# Reduce risk immediately
risk:
  max_drawdown: 10.0              # Reduce from 20.0
  daily_loss_limit: 5.0           # Reduce from 10.0
  max_account_risk: 50.0          # Reduce from 95.0

trading:
  max_positions: 5                # Reduce from 20
  risk_per_trade: 2.0            # Reduce from 5.0
```

#### Emergency Stop Activated
**Symptoms**: "EMERGENCY STOP ACTIVE" message
**Solution**:
1. **Check account balance**
2. **Review recent trades**
3. **Reset emergency stop**:
```python
# Reset emergency stop (use with caution)
risk_manager.reset_emergency_stop()
```

### 6. Data Issues

#### No Market Data
**Symptoms**: "No data available" errors
**Solution**:
1. **Check MT5 connection**
2. **Verify symbol availability**
3. **Check data provider settings**
4. **Restart MT5**

#### Historical Data Missing
**Symptoms**: Backtesting fails or incomplete
**Solution**:
```bash
# Download historical data
python scripts/download_data.py --symbols EURUSD,GBPUSD --days 365

# Verify data quality
python scripts/validate_data.py
```

## 🔧 Advanced Troubleshooting

### Debug Mode
Enable debug mode for detailed logging:
```yaml
logging:
  level: "DEBUG"
  file: "logs/debug.log"
  console: true
  enable_performance_logging: true
```

### System Diagnostics
Run comprehensive system check:
```bash
python scripts/system_diagnostics.py
```

### Performance Profiling
Profile system performance:
```bash
python scripts/profile_performance.py
```

### Network Diagnostics
Check network connectivity:
```bash
python scripts/network_test.py
```

## 📊 Monitoring & Alerts

### Real-time Monitoring
Monitor system health:
```python
# Check system status
system_status = trading_engine.get_system_status()
print(f"System Status: {system_status}")

# Check risk metrics
risk_metrics = risk_manager.get_risk_metrics()
print(f"Risk Metrics: {risk_metrics}")

# Check performance
performance = trading_engine.get_performance()
print(f"Performance: {performance}")
```

### Alert Configuration
Configure alerts for issues:
```yaml
alerts:
  enable_email_alerts: true
  enable_sms_alerts: false
  alert_thresholds:
    drawdown_warning: 15.0
    daily_loss_warning: 8.0
    consecutive_losses_warning: 3
    performance_warning: -5.0
```

## 🆘 Emergency Procedures

### Immediate Stop
If system is causing issues:
```python
# Emergency stop all trading
trading_engine.emergency_stop()

# Close all positions
position_manager.close_all_positions("EMERGENCY")

# Disable automated trading
trading_engine.disable_automated_trading()
```

### System Reset
Reset system to safe state:
```python
# Reset all components
trading_engine.reset_system()

# Clear all positions
position_manager.clear_all_positions()

# Reset risk management
risk_manager.reset_risk_limits()
```

### Data Recovery
Recover from data corruption:
```bash
# Backup current data
python scripts/backup_data.py

# Restore from backup
python scripts/restore_data.py --backup latest

# Validate data integrity
python scripts/validate_data_integrity.py
```

## 📞 Getting Help

### Before Asking for Help
1. **Check this troubleshooting guide**
2. **Run system diagnostics**
3. **Collect error logs**
4. **Document the issue**

### Information to Provide
When reporting issues, include:
- **Error messages** (complete text)
- **System logs** (relevant sections)
- **Configuration files** (sanitized)
- **Steps to reproduce**
- **Expected vs actual behavior**

### Support Channels
- **Documentation**: [Complete Guide](README.md)
- **GitHub Issues**: [Report Bug](https://github.com/oyi77/forex-trader/issues)
- **GitHub Discussions**: [Ask Question](https://github.com/oyi77/forex-trader/discussions)
- **Community**: Join our trading community

### Log Files Location
- **System logs**: `logs/system.log`
- **Trading logs**: `logs/trading.log`
- **Error logs**: `logs/errors.log`
- **Performance logs**: `logs/performance.log`

## 🎯 Prevention

### Regular Maintenance
1. **Daily**: Check system status and performance
2. **Weekly**: Review logs and optimize settings
3. **Monthly**: Update dependencies and backup data
4. **Quarterly**: Full system audit and optimization

### Best Practices
1. **Start with demo accounts**
2. **Use conservative settings initially**
3. **Monitor system continuously**
4. **Keep backups of configurations**
5. **Test changes before live use**

### Monitoring Checklist
- [ ] System running without errors
- [ ] MT5 connection stable
- [ ] Risk metrics within limits
- [ ] Performance meeting targets
- [ ] No unusual trading activity
- [ ] Logs clean and informative

---

*For additional help, see [Complete Documentation](README.md)* 