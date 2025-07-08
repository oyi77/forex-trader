# Forex Trading Bot - User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Trading Strategies](#trading-strategies)
4. [Risk Management](#risk-management)
5. [Performance Monitoring](#performance-monitoring)
6. [Configuration Settings](#configuration-settings)
7. [Best Practices](#best-practices)
8. [FAQ](#frequently-asked-questions)

## Getting Started

### First Time Setup

#### 1. Initial Configuration
After installation, configure your trading parameters:

1. **Open the Dashboard**: Navigate to `http://localhost:5000`
2. **Go to Settings**: Click on the "Settings" tab
3. **Configure Risk Management**:
   - Set maximum risk per trade (recommended: 1-2%)
   - Set total exposure limit (recommended: 50-80%)
   - Configure stop-loss and take-profit levels

4. **Select Trading Strategies**:
   - Start with conservative strategies
   - Enable 2-3 strategies maximum initially
   - Monitor performance before adding more

#### 2. Paper Trading First
**IMPORTANT**: Always start with paper trading to test the system:

1. Ensure `broker_type` is set to `"paper_trading"` in settings
2. Run the bot for at least 1-2 weeks
3. Monitor performance and adjust parameters
4. Only switch to live trading after consistent profitable results

### Quick Start Guide

1. **Start the Bot**:
   ```bash
   python main_enhanced.py
   ```

2. **Start the Dashboard**:
   ```bash
   cd trading_dashboard
   python src/main.py
   ```

3. **Access Dashboard**: Open `http://localhost:5000` in your browser

4. **Monitor Performance**: Check the dashboard regularly for:
   - Active positions
   - P&L performance
   - Risk metrics
   - Strategy signals

## Dashboard Overview

### Main Dashboard
The main dashboard provides an overview of your trading bot's performance:

#### Key Metrics Cards
- **Total P&L**: Current profit/loss
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted return measure
- **Max Drawdown**: Largest peak-to-trough decline

#### Charts and Visualizations
- **Equity Curve**: Shows account balance over time
- **Daily P&L**: Daily profit/loss breakdown
- **Position Distribution**: Current position allocation
- **Performance Metrics**: Detailed analytics

#### Quick Actions
- **Start/Stop Bot**: Control bot operation
- **Emergency Stop**: Immediately close all positions
- **Refresh Data**: Update all metrics

### Navigation Menu
- **Dashboard**: Main overview page
- **Trading**: Live trading interface
- **Performance**: Detailed analytics
- **Strategies**: Strategy management
- **Risk**: Risk monitoring
- **Settings**: Configuration panel

## Trading Strategies

### Available Strategies

#### 1. RSI Mean Reversion
**Description**: Trades based on RSI overbought/oversold conditions
**Best For**: Range-bound markets
**Parameters**:
- RSI Period: 14 (default)
- Overbought Level: 70
- Oversold Level: 30
- Confidence Threshold: 65%

**How it Works**:
- Buys when RSI < 30 (oversold)
- Sells when RSI > 70 (overbought)
- Uses additional filters for confirmation

#### 2. Moving Average Crossover
**Description**: Trades based on moving average crossovers
**Best For**: Trending markets
**Parameters**:
- Fast MA: 10 periods
- Slow MA: 20 periods
- Trend Filter: 50 period MA

**How it Works**:
- Buy signal when fast MA crosses above slow MA
- Sell signal when fast MA crosses below slow MA
- Trend filter prevents counter-trend trades

#### 3. Breakout Strategy
**Description**: Trades breakouts from consolidation patterns
**Best For**: Volatile markets with clear support/resistance
**Parameters**:
- Lookback Period: 20 bars
- Breakout Threshold: 1.5 ATR
- Volume Confirmation: Required

**How it Works**:
- Identifies consolidation patterns
- Trades breakouts above/below key levels
- Uses volume for confirmation

### Strategy Management

#### Enabling/Disabling Strategies
1. Go to the "Strategies" tab
2. Use the toggle switch next to each strategy
3. Monitor performance before making changes
4. Disable underperforming strategies

#### Strategy Configuration
Each strategy can be customized:
- **Confidence Threshold**: Minimum signal strength
- **Position Size**: Allocation per strategy
- **Risk Parameters**: Stop-loss and take-profit levels
- **Market Conditions**: When to activate/deactivate

#### Performance Monitoring
Track each strategy's performance:
- **Total Return**: Overall profitability
- **Sharpe Ratio**: Risk-adjusted performance
- **Win Rate**: Percentage of winning trades
- **Max Drawdown**: Worst losing streak
- **Correlation**: How strategies interact

## Risk Management

### Risk Controls

#### Position Sizing
The bot uses multiple position sizing methods:

1. **Kelly Criterion**: Optimal position size based on win rate and average win/loss
2. **Volatility Adjusted**: Adjusts size based on market volatility
3. **Risk Parity**: Equal risk allocation across positions
4. **Fixed Size**: Consistent position size

#### Risk Limits
- **Per-Trade Risk**: Maximum loss per individual trade
- **Total Exposure**: Maximum percentage of capital at risk
- **Correlation Limits**: Prevents over-concentration in correlated pairs
- **Drawdown Limits**: Stops trading if losses exceed threshold

#### Stop-Loss and Take-Profit
- **Dynamic Stops**: Adjust based on volatility
- **Trailing Stops**: Lock in profits as trades move favorably
- **Time-Based Exits**: Close positions after specified time
- **Technical Exits**: Exit based on technical indicators

### Risk Monitoring

#### Real-Time Alerts
The system provides alerts for:
- High exposure warnings
- Correlation risk alerts
- Drawdown notifications
- System errors or disconnections

#### Risk Metrics
Monitor these key risk metrics:
- **Value at Risk (VaR)**: Potential loss over specific time period
- **Expected Shortfall**: Average loss beyond VaR
- **Leverage Ratio**: Total exposure vs. capital
- **Margin Utilization**: Percentage of available margin used

## Performance Monitoring

### Key Performance Indicators

#### Profitability Metrics
- **Total Return**: Overall profit/loss percentage
- **Annualized Return**: Yearly return projection
- **Monthly Returns**: Month-by-month breakdown
- **Risk-Adjusted Return**: Return per unit of risk

#### Risk Metrics
- **Sharpe Ratio**: Return vs. volatility
- **Sortino Ratio**: Return vs. downside volatility
- **Maximum Drawdown**: Worst peak-to-trough decline
- **Calmar Ratio**: Return vs. maximum drawdown

#### Trading Statistics
- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss**: Average profit vs. average loss
- **Profit Factor**: Gross profit / gross loss

### Performance Analysis

#### Equity Curve Analysis
- **Smooth Growth**: Indicates consistent performance
- **Sharp Declines**: May indicate strategy issues
- **Flat Periods**: Normal during unfavorable market conditions
- **Volatility**: Higher volatility = higher risk

#### Drawdown Analysis
- **Duration**: How long drawdowns last
- **Frequency**: How often they occur
- **Recovery Time**: Time to reach new highs
- **Underwater Curve**: Time spent below previous highs

#### Strategy Attribution
- **Individual Performance**: How each strategy contributes
- **Correlation Effects**: How strategies interact
- **Market Regime Analysis**: Performance in different conditions
- **Time-Based Analysis**: Performance by time of day/week

## Configuration Settings

### Risk Management Settings

#### Basic Risk Controls
```yaml
risk_management:
  max_risk_per_trade: 0.02      # 2% maximum risk per trade
  max_total_exposure: 0.80      # 80% maximum total exposure
  stop_loss_pct: 0.015          # 1.5% stop loss
  take_profit_pct: 0.025        # 2.5% take profit
  max_correlation: 0.70         # Maximum correlation between positions
  max_drawdown_limit: 0.15      # 15% maximum drawdown before stopping
```

#### Advanced Risk Controls
```yaml
advanced_risk:
  var_confidence: 0.95          # VaR confidence level
  var_horizon: 1                # VaR time horizon (days)
  stress_test_scenarios: 5      # Number of stress test scenarios
  correlation_window: 30        # Days for correlation calculation
  volatility_window: 20         # Days for volatility calculation
```

### Trading Parameters

#### Strategy Settings
```yaml
trading_parameters:
  min_confidence: 0.65          # Minimum signal confidence
  max_positions: 5              # Maximum concurrent positions
  position_sizing_method: "kelly_criterion"
  rebalance_frequency: "daily"
  slippage_assumption: 0.0001   # Expected slippage per trade
  commission_per_trade: 0.0002  # Commission per trade
```

#### Market Data Settings
```yaml
data_sources:
  primary_provider: "twelve_data"
  fallback_providers: ["fcs_api", "free_forex_api"]
  update_frequency: "1min"
  data_history_days: 365
  market_hours_only: true
  weekend_trading: false
```

### Broker Settings

#### Paper Trading
```yaml
broker_settings:
  broker_type: "paper_trading"
  initial_balance: 10000
  leverage: 100
  spread_simulation: true
  slippage_simulation: true
```

#### Live Trading (Example)
```yaml
broker_settings:
  broker_type: "exness"
  account_id: "your_account_id"
  leverage: 50
  server: "ExnessEU-Real"
  timeout: 30
```

## Best Practices

### Trading Best Practices

#### 1. Start Conservative
- Begin with paper trading
- Use low leverage (1:10 to 1:50)
- Start with small position sizes
- Enable only 1-2 strategies initially

#### 2. Risk Management
- Never risk more than 2% per trade
- Keep total exposure below 80%
- Use stop-losses on every trade
- Monitor correlation between positions

#### 3. Strategy Selection
- Choose strategies suited to current market conditions
- Diversify across different strategy types
- Regularly review and adjust strategy parameters
- Disable strategies during poor performance periods

#### 4. Monitoring and Maintenance
- Check the dashboard daily
- Review performance weekly
- Adjust parameters monthly
- Backup configuration regularly

### Technical Best Practices

#### 1. System Reliability
- Use stable internet connection
- Run on dedicated server/VPS
- Implement automatic restarts
- Monitor system resources

#### 2. Data Quality
- Use multiple data providers
- Verify data accuracy
- Handle missing data gracefully
- Implement data validation

#### 3. Security
- Secure API keys properly
- Use strong passwords
- Enable two-factor authentication
- Regular security updates

#### 4. Performance Optimization
- Monitor memory usage
- Optimize database queries
- Clean up old log files
- Regular system maintenance

### Market Condition Adaptations

#### Trending Markets
- Enable trend-following strategies
- Increase position sizes gradually
- Use trailing stops
- Avoid mean-reversion strategies

#### Range-Bound Markets
- Enable mean-reversion strategies
- Reduce position sizes
- Use tight stop-losses
- Avoid breakout strategies

#### High Volatility
- Reduce leverage
- Tighten risk controls
- Increase monitoring frequency
- Consider reducing exposure

#### Low Volatility
- May increase position sizes slightly
- Look for breakout opportunities
- Be patient for clear signals
- Avoid overtrading

## Frequently Asked Questions

### General Questions

**Q: How much money do I need to start?**
A: For paper trading, any amount works. For live trading, we recommend starting with at least $1,000-$5,000 to allow for proper diversification and risk management.

**Q: What's the expected return?**
A: Returns vary greatly based on market conditions, strategy selection, and risk parameters. Focus on consistent performance rather than maximum returns.

**Q: How often should I check the bot?**
A: Daily monitoring is recommended. Check for alerts, review performance, and ensure the system is running properly.

**Q: Can I run multiple strategies simultaneously?**
A: Yes, the bot supports multiple strategies. Start with 2-3 strategies and monitor their correlation and combined performance.

### Technical Questions

**Q: What happens if my internet connection drops?**
A: The bot will attempt to reconnect automatically. For critical situations, consider using a VPS with redundant internet connections.

**Q: How do I backup my configuration?**
A: Copy the `config.yaml` file and database files regularly. The deployment guide includes backup scripts.

**Q: Can I modify the strategies?**
A: Yes, strategies can be customized. However, thorough testing is recommended before deploying changes.

**Q: What if the bot stops working?**
A: Check the logs for error messages, verify internet connectivity, and ensure all dependencies are installed. The troubleshooting section provides detailed guidance.

### Trading Questions

**Q: Why isn't the bot generating trades?**
A: Check signal confidence thresholds, ensure data feeds are working, and verify that market conditions match strategy requirements.

**Q: How do I know if a strategy is performing well?**
A: Monitor the Sharpe ratio, win rate, and maximum drawdown. Compare performance to benchmarks and other strategies.

**Q: Should I use maximum leverage?**
A: No, high leverage increases risk significantly. Start with conservative leverage (1:10 to 1:50) and increase gradually based on performance.

**Q: What currency pairs work best?**
A: Major pairs (EUR/USD, GBP/USD, USD/JPY) typically have better liquidity and lower spreads. Start with these before exploring exotic pairs.

### Risk Management Questions

**Q: What's a good risk per trade?**
A: 1-2% of account balance per trade is generally recommended. Never exceed 5% per trade.

**Q: How do I handle losing streaks?**
A: Losing streaks are normal. Stick to your risk management rules, review strategy performance, and consider reducing position sizes temporarily.

**Q: When should I stop the bot?**
A: Stop if drawdown exceeds your comfort level, if multiple strategies are failing simultaneously, or if you notice systematic issues.

**Q: How do I optimize risk-adjusted returns?**
A: Focus on the Sharpe ratio rather than absolute returns. Optimize strategy parameters, improve entry/exit timing, and maintain proper diversification.

---

**Support**: For additional help, consult the deployment guide, check the troubleshooting section, or contact support through the GitHub repository.

**Disclaimer**: This software is for educational and research purposes. Trading involves substantial risk of loss. Never trade with money you cannot afford to lose.

